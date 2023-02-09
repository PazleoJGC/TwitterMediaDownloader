from db import Database
from classes.post import Post
from classes.user import User
import snscrape.modules.twitter as sntwitter
import os

class TwitterScraper:
    def get_user(user_name : str = None, user_id : int = None, database : Database = None) -> User:
        if database:
            user = database.get_user(user_id=user_id, user_name=user_name)
            if user is not None:
                return user
                
        if user_name is None:
            if user_id is None:
                print("user_name or user_id is required!")
                return None
            result = User().from_twitter(sntwitter.TwitterUserScraper(user_id).entity)
        else:
            result = User().from_twitter(sntwitter.TwitterUserScraper(user_name).entity)

        if result is None:
            print(f"User {user_name}/{user_id} does not exist")
            return None

        if database:
            database.add_user(result)
        return result

    def get_post(post_id : int, database : Database = None) -> Post:
        if database:
            post = database.get_post(post_id)
            if post is not None:
                return post
        if post_id is None:
            print("post_id is required!")
            return None
        result = Post().from_twitter(next(sntwitter.TwitterTweetScraper(post_id).get_items(), None)) # get first result
        if result is None:
            return None
        if database:
            database.add_post(result)
        return result

    def fetch_posts_from_user(user_name, new_only = False, max_count = 0, newer_than = 0, database : Database = None) -> list[Post]:
        new_posts = []

        user = TwitterScraper.get_user(user_name=user_name, database=database)
        if user is None:
            print(f"user {user_name} does not exist")
            return new_posts

        cached_posts = {}
        if database is not None:
            user_posts = database.get_user_all_posts(user.id)
            for p in user_posts:
                cached_posts[p.id] = p.downloaded
            cursor = database.db.cursor()

        try:
            scraper = sntwitter.TwitterUserScraper(user_name)
            for item in scraper.get_items():
                tweet = Post().from_twitter(item)
                if tweet.id <= newer_than:
                    break
                if new_only and tweet.id in cached_posts:
                    break
                if tweet.id not in cached_posts:
                    if database is not None:
                        database.add_post(tweet, cursor)
                    new_posts.append(tweet)
                if(len(new_posts) == max_count):
                    break
        except Exception as e:
            print(e)
        finally:
            if database is not None:
                cursor.close()
                database.db.commit()
                
        return new_posts