import os
from classes.post import Post
from classes.user import User
import nextcord
from nextcord.ext import tasks, commands
from twitterScraper import TwitterScraper
import json

def load_settings():
    if os.path.exists("discord_settings.json"):
        with open("discord_settings.json", "rt") as f:
            return json.loads(f.read())
    else:
        settings = { 
            "discord_token": "example", 
            "server_name": "example", 
            "channel_name": "twitter-media-bot",
            "spoiler_sensitive_posts": False
        } 
        with open("discord_settings.json", "wt") as f:
            f.write(json.dumps(settings, indent = 4))
        raise Exception("Settings file created. Fill all the values and restart the bot.")

settings = load_settings()
discord_token = settings["discord_token"]
server_name = settings["server_name"]
channel_name = settings["channel_name"]
spoiler_sensitive_posts = settings["spoiler_sensitive_posts"]

if spoiler_sensitive_posts:
    import classifier
    cl = classifier.Classifier()
else:
    cl = None

downloads_path = os.path.dirname(__file__) + "/discord/downloads/"
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

def filter_images(image_path_list : list[str]):
    """
    Uses deepdanbooru to check if images from the list of files are safe (True) or unsafe (False)
    """
    global cl
    for image in image_path_list:
        if image.endswith(".mp4"):
            #can't check
            continue

        result = cl.classify(image)
        if result["rating:safe"] > result["rating:questionable"] and result["rating:safe"] > result["rating:explicit"] and result["rating:questionable"] < 0.4 and result["rating:explicit"] < 0.3:
            #image is safe
            continue
        else:
            #image is unsafe
            return False
    return True

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name != server_name:
            raise Exception(f"Shouldn't be in {guild.name}")
    print(f'{client.user} has connected to nextcord!')
    myLoop.start()

@tasks.loop(minutes = 10)
async def myLoop():
    global last_posts
    handles = update_account_list()
    for handle in handles:
        #print(handle)
        if(handle.lower() not in last_posts):
            latest_posts = TwitterScraper.fetch_posts_from_user(user_name=handle, max_count=1)
            if len(latest_posts) == 0:
                 continue
            last_posts[handle.lower()] = latest_posts[0].id
        user = TwitterScraper.get_user(user_name=handle)
        posts = TwitterScraper.fetch_posts_from_user(user_name=handle, newer_than=last_posts[handle.lower()])
        for post in sorted(posts, key=lambda x: x.id):
            post : Post
            if post.id > last_posts[handle.lower()]:
                last_posts[handle.lower()] = post.id
            success, files = await send_post(post, user, channel_name)
            clean_up_files(files)

async def send_post(post : Post, user : User, channel_name):
    global cl
    global spoiler_sensitive_posts
    mediaList = []
    try:
        success, mediaList = post.download_media(download_dir=downloads_path)
        if success:
            url = f"https://twitter.com/{user.name}/status/{post.id}"

            embed=nextcord.Embed(description=post.content)
            if user.profileImageUrl == "":
                embed.set_author(name=user.name, url=url)
            else:
                embed.set_author(name=user.name, url=url, icon_url=user.profileImageUrl)
            embed.set_footer(text=post.date)
            
            guild = nextcord.utils.get(client.guilds, name = server_name)
            channel = nextcord.utils.get(guild.channels, name = channel_name)
            if channel is None:
                channel = await guild.create_text_channel(channel_name)

            spoiler = False
            if spoiler_sensitive_posts and cl is not None:
                if filter_images(mediaList) is False:
                    spoiler = True

            await channel.send(embed=embed, files=[nextcord.File(x, spoiler=spoiler) for x in mediaList])
                
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
