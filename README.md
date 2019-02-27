# agent-25
[![Build Status](https://travis-ci.com/vegarab/agent-25.svg?token=L9RN2jPDa7p43DCcYhYZ&branch=dev)](https://travis-ci.com/vegarab/agent-25)
[![codecov](https://codecov.io/gh/vegarab/agent-25/branch/dev/graph/badge.svg?token=ArL47bWQSN)](https://codecov.io/gh/vegarab/agent-25)
<br>
This is a chatbot using Google DialogFlow, which scrapes and indexes sites
itself. The project is developed in cooperation with Trondheim Kommune, where
the goal is to integrate this with their website. The end goal is to have a 
fully automated chatbot which periodically searches Trondheim Kommunes 
webistes for new information, and is therefore better suited to meet the users
needs. 

## Technology
The text processing part of the project is built around Google DialogFlow.
The scraping part is made up of a python scraper using scrapy and beautilfulsoup. 
The data from the scraper is then read into a MongoDB databse. Python Flask is 
used to create a REST API to communicate with the backend.

## Running the application
Run 
`bash model/start.sh`
then start up the server
`bash api/flask/start_server_screen.sh`
