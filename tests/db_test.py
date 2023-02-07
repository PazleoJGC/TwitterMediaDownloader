import unittest
import sqlite3
from db import Database as db
import classes.db_classes as classes

class TestDatabase(unittest.TestCase):
    def test_user_CRUD(self):
        connection = db(':memory:')
        t_user = classes.User()
        t_user.id = 12345
        t_user.name = "Leon"

        self.assertTrue(connection.add_user(t_user)[0])
        self.assertFalse(connection.add_user(t_user)[0])

        result = connection.get_user(user_id=12345)
        self.assertTrue(result.name == "Leon" and result.id == 12345)

        t_user.name = "Noel"
        connection.update_user(t_user)

        result = connection.get_user(user_name="Noel")
        self.assertTrue(result.name == "Noel" and result.id == 12345)

        result = connection.get_user(user_name="Adam")
        self.assertTrue(result == None)

    def test_post_CRUD(self):
        connection = db(':memory:')
        t_post = classes.Post()
        t_post.id = 12345
        t_post.user_id = 6789
        t_post.content = "Hello World"
        t_post.media = "jpg1|jpg,movie1|mp4"
        t_post.downloaded = 0

        self.assertTrue(connection.add_post(t_post)[0])
        self.assertFalse(connection.add_post(t_post)[0])

        result = connection.get_post(12345)
        self.assertTrue(result.user_id == 6789 and result.downloaded == 0)

        t_post.downloaded = 1
        connection.update_post(t_post)
        result = connection.get_post(12345)
        self.assertTrue(result.user_id == 6789 and result.downloaded == 1)
        
        result = connection.get_post(123456)
        self.assertTrue(result == None)

    def test_post_get_all(self):
        connection = db(':memory:')
        t_post = classes.Post()
        t_post.id = 12345
        t_post.user_id = 6789
        t_post.content = "Hello World"
        t_post.media = "jpg1|jpg,movie1|mp4"
        t_post.downloaded = 0

        for i in range(0, 10):
            t_post.id += 1
            if i<6:
                t_post.downloaded = 1
            else:
                t_post.downloaded = 0
            connection.add_post(t_post)

        result = connection.get_user_all_posts(6789)
        self.assertEqual(len(result), 10)
        result = connection.get_user_all_posts(6789, only_downloaded=True)
        self.assertEqual(len(result), 6)
        result = connection.get_user_all_posts(6789, only_notdownloaded=True)
        self.assertEqual(len(result), 4)