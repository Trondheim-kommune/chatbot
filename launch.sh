#!/bin/bash

if ! [ -f "chatbot/scraper/scraped.json" ]; then
	scrapy crawl info_gathering -o chatbot/scraper/scraped.json
fi
python launch.py chatbot/scraper/scraped.json
