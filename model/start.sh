#!/bin/bash

if ! [ -f "scraper/scraped.json" ]; then
	cd scraper
	scrapy crawl info_gathering -o scraped.json -a strong_headers=true
	cd ..
fi
python model/start.py scraper/scraped.json
