from twitterScraper import TwitterScraper
from db import Database
import os

def update_account_list():
    file_path = os.path.dirname(__file__) + "/AccountNames.txt"
    if not os.path.exists(file_path):
        with open(file_path, "wt") as f:
            pass
        print("AccountNames.txt was created. Add at least one account name and run the script again.")
        raise Exception("AccountNames.txt was created. Add at least one account name and run the script again.")
    names = []
    with open(file_path, "rt") as f:
        names = [t.strip() for t in f.readlines()]
    if len(names) == 0:
        print("AccountNames.txt is empty. Add at least one account name.")
        raise Exception("AccountNames.txt is empty. Add at least one account name.")
    return names

db = Database(db_name=os.path.dirname(__file__) + "/database.db")
tw = TwitterScraper(db, download_dir=os.path.dirname(__file__) + "/downloads")

# download single post
print(tw.download_post(url="https://twitter.com/Twitter/status/1506723004994174981"))

tw.db = None
# download single post without saving it in database
print(tw.download_post(url="https://twitter.com/Twitter/status/1577730467436138524/photo/2", update_database=False))
tw.db = db

# #cache and download posts as they come, from the most recent
# for account in update_account_list():
#     result = tw.download_all_posts(account)
#     print(f'{account} - success: {result["success"]}, fail: {result["fail"]}, skipped: {result["skipped"]}')

# #cache posts and then download them starting from the oldest
# for account in update_account_list():
#     tw.fetch_all_posts(account)
#     result = tw.download_all_posts(account, database_only=True, from_oldest=True)
#     print(f'{account} - success: {result["success"]}, fail: {result["fail"]}, skipped: {result["skipped"]}')