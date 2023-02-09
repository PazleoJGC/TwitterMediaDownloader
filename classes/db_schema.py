class User:
    table = "USERS"
    id = "id"
    id_param = "BIGINT NOT NULL UNIQUE PRIMARY KEY"
    name = "name"
    name_param = "TEXT NOT NULL"
    image = "image"
    image_param = "TEXT"


class Post:
    table = "POSTS"
    id = "id" 
    id_param = "BIGINT NOT NULL UNIQUE PRIMARY KEY"
    user_id = "user_id" 
    user_id_param = "BIGINT NOT NULL"
    content = "content"
    content_param = "TEXT"
    media = "media"
    media_param = "TEXT"
    date = "date"
    date_param = "TEXT NOT NULL"
    downloaded = "downloaded"
    downloaded_param = "BOOLEAN"