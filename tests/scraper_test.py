import unittest
import os
from db import Database as db
from twitterScraper import TwitterScraper
import classes.user as user

class TestScraper(unittest.TestCase):
    def test_save_and_download(self):
        handle = "Twitter"
        posts = TwitterScraper.fetch_posts_from_user(handle, max_count=5)
        self.assertEqual(len(posts),5)
        for post in posts:
            result = post.save(download_media=True)
            for file in result[1]:
                os.remove(file)
            self.assertTrue(result[0])
