import snscrape.modules.twitter as sntwitter
import re

class User:
    profileImageUrl : str
    id : int
    name : str

    def from_twitter(self, user : sntwitter.User):
        if user is None: 
            return None
        self.id = user.id
        self.name = user.username
        self.profileImageUrl = user.profileImageUrl
        return self

    def from_database(self, query_result):
        if query_result is None:
            return None
        self.id = query_result[0]
        self.name = query_result[1]
        self.profileImageUrl = query_result[1]
        return self