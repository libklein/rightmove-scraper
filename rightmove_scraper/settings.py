from os import environ

SEARCH_URLS = environ.get("SEARCH_URLS", "").split(",")

LOG_FILE = environ.get("LOG_FILE_PATH", "rightmove.log")

OUTPUT_JSON_PATH = environ.get("OUTPUT_JSON_PATH", False)
NO_DB = environ.get("NO_DB", False)

BOT_NAME = "rightmove_scraper"
SPIDER_MODULES = ["rightmove_scraper.spiders"]
NEWSPIDER_MODULE = "rightmove_scraper.spiders"

# Do not obey robots.txt
ROBOTSTXT_OBEY = False

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"

# Configure maximum concurrent requests performed by Scrapy (default: 16)
DOWNLOAD_DELAY = 0.1
CONCURRENT_REQUESTS = 20
CONCURRENT_REQUESTS_PER_DOMAIN = 20

# Cookies
COOKIES_ENABLED = False

# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.cookies.CookiesMiddleware": 400,
    "scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware": 300,
}

ITEM_PIPELINES = {}
# Configure item pipelines
if environ.get("NO_DB", 0) == 1:
    ITEM_PIPELINES["rightmove_scraper.pipelines.ModelPipeline"] = 300


# Enable and configure HTTP caching (disabled by default)
HTTPCACHE_ENABLED = True
# HTTPCACHE_DIR = ".cache"
# HTTPCACHE_GZIP = True
# HTTPCACHE_POLICY = "scrapy.extensions.httpcache.RFC2616Policy"
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"
