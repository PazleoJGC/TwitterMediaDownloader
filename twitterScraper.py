from db import Database
import classes.db_classes as classes
from downloader import Downloader as DL
import snscrape.modules.twitter as sntwitter
import os

class TwitterScraper:
    db : Database
    download_dir = ""

    def __init__(self, db:Database, download_dir = None):
        if download_dir == None:
            self.download_dir = os.path.dirname(__file__) + "/downloads"
        else:
            self.download_dir = download_dir
        self.db = db

    def get_user(self, user_name : str = None, user_id : int = None, use_database = True, save_database = True) -> classes.User:
        if (use_database or save_database) and self.db is None:
            raise Exception("Can't use database without database.")

        if user_id is not None:
            if use_database:
                user = self.db.get_user(user_id=user_id)
                if user is not None:
                    return user
            result = classes.User().from_twitter(sntwitter.TwitterUserScraper(user_id).entity)
        elif user_name is not None:
            if use_database:
                user = self.db.get_user(user_name=user_name)
                if user is not None:
                    return user
            result = classes.User().from_twitter(sntwitter.TwitterUserScraper(user_name).entity)
        else:
            raise Exception("user_name or user_id is required!")

        if result is None:
             return None
        if save_database:
            self.db.add_user(result)
        return result

    def get_post(self, post_id : int, use_database = True, save_database = True) -> classes.Post:
        if (use_database or save_database) and self.db is None:
            raise Exception("Can't use database without database.")

        if use_database:
            post = self.db.get_post(post_id)
            if post is not None:
                return post
        post = classes.Post().from_twitter(next(sntwitter.TwitterTweetScraper(post_id).get_items(), None)) # get first result
        if post is None:
            return None
        if save_database:
            self.db.add_post(post)
        return post

    def fetch_all_posts(self, user_name, new_only = False) -> int:
        """
        updates database and returns number of new posts\n
        uses Cursor to minimize database R/W
        """
        new_posts = 0

        if self.db is None:
            print("Can't fetch without a database.")
            return new_posts

        user = self.get_user(user_name=user_name)
        cached_posts = {}
        if user is None:
            print(f"user {user_name} does not exist")
            return new_posts

        user_posts = self.db.get_user_all_posts(user.id)
        for p in user_posts:
            cached_posts[p.id] = p.downloaded

        con = self.db.db.cursor()
        scraper = sntwitter.TwitterUserScraper(user_name)
        for tweet in scraper.get_items():
            if tweet.media is None:
                continue
            twt = classes.Post().from_twitter(tweet)
            if new_only and tweet.id in cached_posts:
                break
            if tweet.id not in cached_posts:
                self.db.add_post(twt, con)
                new_posts += 1
        con.close()
        self.db.db.commit()
                
        return new_posts

    def download_all_posts(self, user_name, force_redownload = False, update_database = True, new_only = False, database_only = False, reverse = False):
        """
        returns {"success", "fail", "skipped"} dictionary with numbers\n
        new_only - function will return if a post is already in database (only download new posts)\n
        database_only - do not check for new posts (only download from database)
        reverse - only works for database_only mode. Posts are downloaded starting from the oldest.
        """
        if (database_only or update_database) and self.db is None:
            raise Exception("Can't use database without database.")

        total = {"success": 0, "fail": 0, "skipped" : 0}
        user = self.get_user(user_name=user_name, save_database=update_database)
        if user is None:
            print(f"user {user_name} does not exist")
            return total

        cached_posts = {}
        if self.db is not None:
            user_posts = self.db.get_user_all_posts(user.id)
            user_posts = sorted(user_posts, key=lambda x: x.id, reverse=reverse)
            for p in user_posts:
                cached_posts[p.id] = p.downloaded
        
        if not database_only:
            scraper = sntwitter.TwitterUserScraper(user_name)
            for tweet in scraper.get_items():
                if tweet.media is None:
                    continue
                twt = classes.Post().from_twitter(tweet)
                if twt.id in cached_posts:
                    if new_only:
                        break
                    if cached_posts[tweet.id] == 1 and not force_redownload:
                        total["skipped"] += 1
                        continue
                if update_database:
                    self.db.add_post(twt)
                result = self.download_media(twt, user, update_database)
                if result[0] is True:
                    total["success"] += 1
                else:
                    total["fail"] += 1
                print(result)
        else:
            for tweet in user_posts:
                tweet : classes.Post
                if force_redownload or tweet.downloaded == 0:
                    result = self.download_media(tweet, user, update_database)
                    if result[0] is True:
                        total["success"] += 1
                    else:
                        total["fail"] += 1
                else:
                    total["skipped"] += 1
        return total

    def download_post(self, post_id : int = None, url : str = None, update_database = True) -> tuple[bool,list]:
        """
        Returns a tuple [success status, list of successfully downloaded files]
        """
        if update_database and self.db is None:
            raise Exception("Can't update database without database.")
        if post_id is None and url is None:
            raise Exception("No post_id or url provided")

        if url is not None:
            splits = url.split("/")
            for idx, split in enumerate(splits):
                if split == "status":
                    post_id = splits[idx+1]
                    break
            if post_id is None:
                raise Exception("Provided url is invalid")

        post = self.get_post(post_id, use_database=self.db is not None, save_database=update_database)
        if post is None:
            print(f"Post {post_id} does not exist")
            return [False, []]
        
        user = self.get_user(user_id=post.user_id, use_database=self.db is not None, save_database=update_database)
        if user is None:
            print(f"User {post.user_id} does not exist")
            return [False, []]

        result = self.download_media(post, user, update_database)
        return result

    
    def download_media(self, post : classes.Post, user : classes.User, update_database = True) -> tuple[bool,list]:
        """
        Returns a tuple [success status, list of successfully downloaded files]
        """
        if update_database and self.db is None:
            raise Exception("Can't update database without database.")

        downloadedFiles = []
        for idx, media in enumerate(post.media.split(',')):
            splits = media.split('|') # media is saved in db as "url|file_format" string
            file_path = os.path.join(self.download_dir, f"{user.name}/{post.id}_{idx}.{splits[1]}")
            if DL.download(splits[0], file_path)[0] == False:
                if update_database:
                    post.downloaded = 0
                    self.db.update_post(post)
                return [False, downloadedFiles]
            downloadedFiles.append(file_path)

        if update_database:
            post.downloaded = 1
            self.db.update_post(post)
        return [True, downloadedFiles]