# -*- coding: utf-8 -*-
# Scrapy settings for the scraper project.

# Project configuration for Python.
BOT_NAME = 'scraper'
SPIDER_MODULES = ['chatbot.scraper.spiders']
NEWSPIDER_MODULE = 'chatbot.scraper.spiders'

# Ensure data is encoded as real UTF8.
FEED_EXPORT_ENCODING = 'utf-8'

# Crawl responsibly by idenitfying our crawler.
USER_AGENT = 'chatbotbot'

# Set some more brutal concurent request numbers.
CONCURRENT_REQUESTS = 32
CONCURRENT_REQUESTS_PER_DOMAIN = 32
CONCURRENT_REQUESTS_PER_IP = 32

# Remove printing to output when in production and not needing output.
LOG_ENABLED = False
