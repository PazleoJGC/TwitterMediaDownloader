import unittest
from db import Database as db
import classes.db_classes as classes

class TestScraper(unittest.TestCase):
    def test_scraper_db_users(self):
        connection = db(':memory:')
        
        for i in range(0, 20):
            t_user = classes.User()
            t_user.id = 12345 + i
            t_user.name = str(t_user.id)
            connection.add_user(t_user)

        for i in range(0, 20):
            self.assertNotEqual(connection.get_user(user_id=12345 + i), None)
            self.assertNotEqual(connection.get_user(user_name=str(12345 + i)), None)