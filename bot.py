import os
import classes.db_classes as classes
import nextcord
from nextcord.ext import tasks, commands
from twitterScraper import TwitterScraper

discord_token = ""
server_name = "aaa"
channel_name = "twitter-media-bot"
base_path = os.path.dirname(__file__) + "/discord/"
tw = TwitterScraper(None, download_dir=base_path + "/temp/")
last_posts = {}

intents = nextcord.Intents.default()
intents.message_content = True
intents.guild_reactions = True
client = commands.Bot(command_prefix=".", intents=intents)

def update_account_list():
    file_path = os.path.dirname(__file__) + "/AccountNames.txt"
    if not os.path.exists(file_path):
        with open(file_path, "wt") as f:
            pass
        print("AccountNames.txt was created. Add at least one account name and run the script again.")
        return []
    names = []
    with open(file_path, "rt") as f:
        names = [t.strip() for t in f.readlines()]
    if len(names) == 0:
        print("AccountNames.txt is empty. Add at least one account name.")
        return []
    return names

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name != server_name:
            raise Exception(f"Shouldn't be in {guild.name}")
    print(f'{client.user} has connected to nextcord!')
    myLoop.start()

@tasks.loop(minutes = 5)
async def myLoop():
    global tw
    global last_posts
    handles = update_account_list()
    for handle in handles:
        print(handle)
        if(handle.lower() not in last_posts):
            latest_posts = tw.fetch_all_posts(user_name=handle, use_database=False, max_count=1)
            if len(latest_posts) == 0:
                 continue
            last_posts[handle.lower()] = latest_posts[0].id-1
            print(handle, last_posts[handle.lower()])
            #continue
        posts = tw.fetch_all_posts(user_name=handle, use_database=False, newer_than=last_posts[handle.lower()])
        for post in sorted(posts, key=lambda x: x.id):
            post : classes.Post
            if post.id > last_posts[handle.lower()]:
                last_posts[handle.lower()] = post.id
            success, files = await send_post(post, handle, channel_name)
            print(success, files)
            clean_up_files(files)

async def send_post(post : classes.Post, handle, channel_name):
    global tw
    mediaList = []
    try:
        tweet = tw.get_post(post_id=post.id, use_database=False, save_database=False)
        success, mediaList = tw.download_media(tweet, download_dir=base_path, update_database=False)
        
        if success:
            url = f"https://twitter.com/{handle}/status/{tweet.id}"
            embed=nextcord.Embed(description=tweet.content, url=url)
            
            for guild in client.guilds:
                channel = nextcord.utils.get(guild.channels, name = channel_name)
                if channel is None:
                    channel = await guild.create_text_channel(channel_name)
                await channel.send(embed=embed, files=[nextcord.File(x) for x in mediaList])
                
            return True, mediaList
        else:
            return False, mediaList
    except Exception as e:
        print(e)
        return False, mediaList

def clean_up_files(mediaList):
    for media in mediaList:
        if os.path.exists(media):
            os.remove(media)

client.run(discord_token)
