#!/bin/bash
# Scrape data to /home/agent25
# Serialize the data
# Move trondheim.json file to /var/www/html

source venv/bin/activate
cd scraper/
rm trondheim.json
scrapy crawl trondheim -o trondheim.json
cp trondheim.json /var/www/html/trondheim.json 
cd ..
# serialize trondheim.json
# create new collection, delete 2 day old collection.
# or create new and hotswap the old and new collection.
# create new intents, entities.

python 