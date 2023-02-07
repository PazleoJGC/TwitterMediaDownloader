import snscrape.modules.twitter as sntwitter

class Post:
    id : int
    user_id : int
    content : str
    media : list
    downloaded : int

    def from_twitter(self, tweet):
        if tweet is None:
            return None
        self.id = tweet.id
        self.user_id = tweet.user.id
        self.content = tweet.rawContent.replace("'","''")
        
        # media is saved in db as "url|file_format" string
        media_new = []
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
        self.downloaded = 0
        return self

    def from_database(self, query_result):
        if query_result is None:
            return None
        self.id = query_result[0]
        self.user_id = query_result[1]
        self.content = query_result[2]
        self.media = query_result[3]
        self.downloaded = query_result[4]
        return self

class User:
    id : int
    name : str

    def from_twitter(self, user):
        if user is None: 
            return None
        self.id = user.id
        self.name = user.username
        return self

    def from_database(self, query_result):
        if query_result is None:
            return None
        self.id = query_result[0]
        self.name = query_result[1]
        return self