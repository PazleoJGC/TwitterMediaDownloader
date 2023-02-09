import os
import sqlite3 as sl
import classes.db_schema as schema
import classes.user as user
from classes.post import Post

class Database:
    def __init__(self, db_name = None):
        if db_name is None:
            db_name = os.path.dirname(__file__) + "/database.db"
        self.db = sl.connect(db_name)
        self.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema.User.table} (
                {schema.User.id} {schema.User.id_param},
                {schema.User.name} {schema.User.name_param},
                {schema.User.image} {schema.User.image_param}
            );
        """)
        self.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema.Post.table} (
                {schema.Post.id} {schema.Post.id_param},
                {schema.Post.user_id} {schema.Post.user_id_param},
                {schema.Post.content} {schema.Post.content_param},
                {schema.Post.media} {schema.Post.media_param},
                {schema.Post.date} {schema.Post.date_param},
                {schema.Post.downloaded} {schema.Post.downloaded_param}
            );
        """)

    def execute(self, command:str, parameters : list = []):
        with self.db:
            result = self.db.execute(command, parameters).fetchall()
            return result

    def add_user(self, user : user.User, cursor : sl.Cursor = None):
        query = f"INSERT INTO {schema.User.table} VALUES({user.id}, '{user.name}', '{user.profileImageUrl}')"
        try:
            if cursor is not None:
                cursor.execute(query)
                return [True, "OK"]
            else:
                self.execute(query)
                return [True, "OK"]
        except sl.IntegrityError as e:
            return [False, str(e)]
            
    def get_user(self, user_id : int = None, user_name : str = None) -> user.User:
        if user_id is None:
            if user_name is None:
                raise Exception("user_id or user_name is required!")
            result = self.execute(f"Select * FROM {schema.User.table} WHERE {schema.User.name} = '{user_name}'")
        else:
            result = self.execute(f"Select * FROM {schema.User.table} WHERE {schema.User.id} = {user_id}")

        if len(result) == 0: return None
        return user.User().from_database(result[0])

    def get_user_all_posts(self, user_id, only_downloaded = False, only_notdownloaded = False):
        if only_notdownloaded:
            result = self.execute(f"Select * FROM {schema.Post.table} WHERE {schema.Post.user_id} = {user_id} AND {schema.Post.downloaded} = 0")
        elif only_downloaded:
            result = self.execute(f"Select * FROM {schema.Post.table} WHERE {schema.Post.user_id} = {user_id} AND {schema.Post.downloaded} = 1")
        else:
            result = self.execute(f"Select * FROM {schema.Post.table} WHERE {schema.Post.user_id} = {user_id}")
        if len(result) == 0: return []
        return [Post().from_database(f) for f in result]
    
    def update_user(self, user : user.User):
        self.execute(f"""
            UPDATE {schema.User.table}
            SET {schema.User.name} = '{user.name}', {schema.User.image} = '{user.profileImageUrl}'
            WHERE {schema.User.id}  = {user.id}
        """)

    def add_post(self, post : Post, cursor : sl.Cursor = None):
        query = f"INSERT INTO {schema.Post.table} VALUES({post.id}, {post.user_id}, ?, '{post.media}', '{post.date}', {post.downloaded})"
        try:
            if cursor is not None:
                cursor.execute(query, [post.content])
                return [True, "OK"]
            else:
                self.execute(query, [post.content])
                return [True, "OK"]
        except sl.IntegrityError as e:
            return [False, str(e)]

    def get_post(self, post_id) -> Post:
        result = self.execute(f"Select * FROM {schema.Post.table} WHERE {schema.Post.id} = {post_id}")
        if len(result) == 0: return None
        return Post().from_database(result[0])

    def update_post(self, post : Post):
        self.execute(f"""
            UPDATE {schema.Post.table}
            SET {schema.Post.media} = '{post.media}',
                {schema.Post.content} = ?,
                {schema.Post.date} = '{post.date}',
                {schema.Post.downloaded} = {post.downloaded}
            WHERE {schema.Post.id}  = {post.id}
        """, [post.content])