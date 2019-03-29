#!/bin/bash

if ! [ -f "scraper/scraped.json" ]; then
	scrapy crawl info_gathering -o scraper/scraped.json
fi
python model/start.py scraper/scraped.json
