# -*- coding: utf-8 -*-

# Scrapy settings for nfl_data project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'nfl_data'

SPIDER_MODULES = ['nfl_data.spiders']
NEWSPIDER_MODULE = 'nfl_data.spiders'

CONCURRENT_REQUESTS = 100
LOG_LEVEL = 'INFO'
COOKIES_ENABLED = False
RETRY_ENABLED = False
DOWNLOAD_TIMEOUT = 15

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'nfl_data (+http://www.yourdomain.com)'
