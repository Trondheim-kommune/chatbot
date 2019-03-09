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

## Docker
The project has also be containerized. Below is a description of how to build and run 
the container.

To build
```bash
docker build .
```

To run, exposing port 8080
```bash
docker run -e PROJECT_ID=$PROJECT_ID -e GOOGLE_APPLICATION_CREDENTIALS="/usr/src/app/backupagent.json" -e DB_USER=$DB_USER -e DB_PWD=$DB_PWD -d -p 8080:8080 <container_id>
```

## Building the website
Run
`cd website`  
`./build_web_server.sh`  

## Running website locally
Run
`source venv/bin/activate` 
`cd website`  
`npm install`  
`npm start`
Then to run Cypress tests
`npm run cypress open`
