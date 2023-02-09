# Twitter_to_discord
Discord bot written in python using the [nextcord](https://github.com/nextcord/nextcord) wrapper.

The bot bypasses Twitter API by using [snscrape](https://github.com/JustAnotherArchivist/snscrape). Therefore, it doesn't work with protected tweets or tweets marked as sensitive.

Loads twitter account names from a list and checks them on an interval. New posts (after initial and every subsequent check) are posted to a specified channel, on a specified server that the bot is a member of.

Configuration file has 3 fields:
```
  "discord_token" - place for your discord bot Token from https://discord.com/developers/applications
  "server_name" - target server name
  "channel_name" - target channel, the channel will be created automatically if it doesn't exist.
```

Tweets are sent as embeds with author name, url, tweet content and a timestamp. Media posts are downloaded to temporary locations and sent as files, to prevent the files from being lost when the tweet is deleted.

List of accounts is stored in a .txt file. The file can be changed while the bot is running.
```
AccountNames.txt:
twitter
elonmusk
```
will track posts on https://twitter.com/twitter and https://twitter.com/elonmusk accounts.