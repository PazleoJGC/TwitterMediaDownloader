from twitterScraper import TwitterScraper
from db import Database
import classes.db_schema as schema
import os

def update_account_list():
    if not os.path.exists("AccountNames.txt"):
        with open("AccountNames.txt", "wt") as f:
            pass
        print("AccountNames.txt was created. Add at least one account name and run the script again.")
        raise Exception("AccountNames.txt was created. Add at least one account name and run the script again.")
    names = []
    with open("AccountNames.txt", "rt") as f:
        names = [t.strip() for t in f.readlines()]
    if len(names) == 0:
        print("AccountNames.txt is empty. Add at least one account name.")
        raise Exception("AccountNames.txt is empty. Add at least one account name.")
    return names

db = Database()
tw = TwitterScraper(db)

for account in update_account_list():
    result = tw.download_all_posts(account, force_redownload=False, update_database=True, new_only=True)
    print(f'{account} - success: {result["success"]}, fail: {result["fail"]}, skipped: {result["skipped"]}')