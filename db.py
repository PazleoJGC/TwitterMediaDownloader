import sqlite3 as sl
import snscrape.modules.twitter as sntwitter
import classes.db_schema as schema
import classes.db_classes as classes

class Database:
    def __init__(self, db_name = 'database.db') -> None:
        self.db = sl.connect(db_name)
        self.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema.User.table} (
                {schema.User.id} {schema.User.id_param},
                {schema.User.name} {schema.User.name_param}
            );
        """)
        self.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema.Post.table} (
                {schema.Post.id} {schema.Post.id_param},
                {schema.Post.user_id} {schema.Post.user_id_param},
                {schema.Post.content} {schema.Post.content_param},
                {schema.Post.media} {schema.Post.media_param},
                {schema.Post.downloaded} {schema.Post.downloaded_param}
            );
        """)

    def execute(self, command:str):
        with self.db:
            result = self.db.execute(command).fetchall()
            return result

    def add_user(self, user : classes.User):
        try:
            self.execute(f"INSERT INTO {schema.User.table} VALUES({user.id}, '{user.name}')")
            return [True, "OK"]
        except sl.IntegrityError as e:
            return [False, str(e)]
            
    def get_user(self, user_id : int = None, user_name : str = None) -> classes.User:
        if user_id is None:
            if user_name is None:
                raise Exception("user_id or user_name is required!")
            result = self.execute(f"Select * FROM {schema.User.table} WHERE {schema.User.name} = '{user_name}'")
        else:
            result = self.execute(f"Select * FROM {schema.User.table} WHERE {schema.User.id} = {user_id}")

        if len(result) == 0: return None
        return classes.User().from_database(result[0])

    def get_user_all_posts(self, user_id, only_downloaded = False, only_notdownloaded = False):
        if only_notdownloaded:
            result = self.execute(f"Select * FROM {schema.Post.table} WHERE {schema.Post.user_id} = {user_id} AND {schema.Post.downloaded} = 0")
        elif only_downloaded:
            result = self.execute(f"Select * FROM {schema.Post.table} WHERE {schema.Post.user_id} = {user_id} AND {schema.Post.downloaded} = 1")
        else:
            result = self.execute(f"Select * FROM {schema.Post.table} WHERE {schema.Post.user_id} = {user_id}")
        if len(result) == 0: return []
        return [classes.Post().from_database(f) for f in result]
    
    def update_user(self, user : classes.User):
        self.execute(f"""
            UPDATE {schema.User.table}
            SET {schema.User.name} = '{user.name}'
            WHERE {schema.User.id}  = {user.id}
        """)

    def add_post(self, post : classes.Post):
        try:
            self.execute(f"INSERT INTO {schema.Post.table} VALUES({post.id}, {post.user_id}, '{post.content}', '{post.media}', {post.downloaded})")
            return [True, "OK"]
        except sl.IntegrityError as e:
            return [False, str(e)]

    def get_post(self, post_id) -> classes.Post:
        result = self.execute(f"Select * FROM {schema.Post.table} WHERE {schema.Post.id} = {post_id}")
        if len(result) == 0: return None
        return classes.Post().from_database(result[0])

    def update_post(self, post : classes.Post):
        self.execute(f"""
            UPDATE {schema.Post.table}
            SET {schema.Post.media} = '{post.media}',
                {schema.Post.content} = '{post.content}',
                {schema.Post.downloaded} = {post.downloaded}
            WHERE {schema.Post.id}  = {post.id}
        """)