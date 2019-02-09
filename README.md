[![codecov](https://codecov.io/gh/vegarab/agent-25/branch/feat%2F%2318-test-automation/graph/badge.svg?token=ArL47bWQSN)](https://codecov.io/gh/vegarab/agent-25)
# agent-25
This is a chatbot using google dialogflow, which scrapes and indexes sites
itself. The project is developed in cooperation with Trondheim Kommune, where
the goal is to integrate this with their website. The end goal is to have a 
fully automated chatbot which periodically searches Trondheim Kommunes 
webistes for new information, and is therefore better suited to meet the users
needs. 

## Technology
The text processing part of the project is built around google dialogflow.
The scraping part is made up of a python scraper using scrapy and beautilfulsoup. 
The data from the scraper is then read into a MongoDB databse. Python flask is 
used to create a rest framework to communicate with the backend.

## Running the program
To run the scraper, type:
```bash
cd scraper
scrapy crawl trondheim -o trondheim.json
```

