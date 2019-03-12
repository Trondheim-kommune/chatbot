#!/bin/bash

if ! [ -f "scraper/scraped.json" ]; then
	cd scraper
	scrapy crawl info_gathering -o scraped.json
	cd ..
fi
python model/start.py scraper/scraped.json
