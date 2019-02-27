#!/bin/bash

if ! [ -f "scraper/trondheim.json" ]; then
	cd scraper
	scrapy crawl trondheim -o trondheim.json
	cd ..
fi
python model/start.py scraper/trondheim.json
