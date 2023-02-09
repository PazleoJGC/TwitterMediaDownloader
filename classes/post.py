import snscrape.modules.twitter as sntwitter
from downloader import Downloader as DL
import re
import os
import json

class Post:
    id : int
    user_id : int
    content : str
    media : list
    date : str
    downloaded : int

    def from_twitter(self, tweet : sntwitter.Tweet):
        if tweet is None:
            return None
        self.id = tweet.id
        self.user_id = tweet.user.id
        self.content = re.sub(r"https://t.co\S+", "", tweet.rawContent).strip()
        
        # media is saved in db as "url|file_format" string
        media_new = []
        if tweet.media is not None:
            for medium in tweet.media:
                if isinstance(medium, sntwitter.Photo):
                    for split in medium.fullUrl.replace("?","&").split("&"):
                        if "format" in split:
                            ext = split.split('=')[-1]
                    media_new.append(medium.fullUrl + "|" + ext)
                elif isinstance(medium, sntwitter.Video) or isinstance(medium, sntwitter.Gif):
                    bestVariant = medium.variants[0]
                    for variant in medium.variants:
                        if bestVariant.bitrate is None and variant.bitrate is not None:
                            bestVariant = variant
                        elif variant.bitrate is not None and bestVariant.bitrate is not None and variant.bitrate > bestVariant.bitrate:
                            bestVariant = variant
                    media_new.append(bestVariant.url + "|" + bestVariant.contentType.split("/")[-1])
        self.media = ",".join(media_new)
        self.date = tweet.date.strftime("%d/%m/%Y, %H:%M:%S")
        self.downloaded = 0
        return self

    def from_database(self, query_result):
        if query_result is None:
            return None
        self.id = query_result[0]
        self.user_id = query_result[1]
        self.content = query_result[2]
        self.media = query_result[3]
        self.date = query_result[4]
        self.downloaded = query_result[5]
        return self

    def save(self, save_path : str = None, download_media = False) -> tuple[bool,list]:
        """
        Save path must be absolute.
        Returns a tuple [success status, file location / list of successfully downloaded files]
        """
        if save_path is None:
            save_path = os.path.join(os.getcwd(), "downloads")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        path = os.path.join(save_path, f"{self.id}.json")
        with open(path, "wt") as outfile:
            json_object = self.toJSON()
            outfile.write(json_object)

        if download_media:
            result = self.download_media(save_path)
            return [result[0], [path] + result[1]]

        return [True, [path]]

    
    def download_media(self, download_dir : str) -> tuple[bool,list]:
        """
        Returns a tuple [success status, list of successfully downloaded files]
        """
        downloadedFiles = []
        if self.media == "":
            return [True, downloadedFiles]
        for idx, media in enumerate(self.media.split(',')):
            splits = media.split('|') # media is saved in db as "url|file_format" string
            file_path = os.path.join(download_dir, f"{self.id}_{idx}.{splits[1]}")
            if DL.download(splits[0], file_path)[0] == False:
                return [False, downloadedFiles]
            downloadedFiles.append(file_path)
        return [True, downloadedFiles]

    def toJSON(self, indent = 4):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=False, indent=indent)