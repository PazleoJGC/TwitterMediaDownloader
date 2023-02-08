# TwitterMediaDownloader
Python tool for scraping media posts from a list of Twitter accounts. Only images and videos (best quality) from media posts are saved, text posts are ignored. The tool bypasses the API by using [snscrape](https://github.com/JustAnotherArchivist/snscrape)

By default, files are downloaded to project directory + /downloads/, the path can be customized in TwitterScraper's constructor.

Posts and their download status are saved to a sqlite3 database.

To start downloading, add your twitter account names to AccountNames.txt, for example
```
AccountNames.txt:
twitter
elonmusk
```
will download all media posts from
```
https://twitter.com/twitter
https://twitter.com/elonmusk
```