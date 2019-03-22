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


## Settings file
There is a settings file called `settings.json`, in this file there are
multiple things you could change. Every change needed to make this project work on any website should be able to be configured here. 

* mongo
    * Change things like username, password, ip(url), port, what the database is called and what the testing database is called.
* model
    * The only thing you can change here is accepted_tags. This changes which HTML element are allowed to be made into a leaf node.
* scraper
    * debug: If you want more logging to stdout whilst running the scraper.
    * strong_headers: If a strong tag should be seen as a sub header.
    * concatenation: This is a list of elements that you may want to concatenate with other siblings of the same element. Also a value for the maximum amount of words allowed after concatenation.
    * url:
        * root_url: Which url should the scraper start on.
        * allowed_paths: Which paths should the scraper be allowed to scrape. (list)
        * scrape_blacklist: Pages in this list will be visited and links on them will be visited, however the data will not be scrapaed.
    * blacklist:
        * elements: These selectors will be removed from all pages, as they contain very little actual information, and are equal on all pages.
        * visits: Sites that should never be visited by the scraper.
        * texts: Elements containing text equal to one of these sentences will be removed from all pages.
        * prefix_url: Ignore the url if it starts with this.
        * suffix_url: Ignore the url if it ends with this.
        * not_found_text: The text used for the title on 404 pages. Used to detect silent 404 error.
    * hierarchy:
        * How the different HTML elements should be sorted.
* query_system
    * not_found: Text that the bot should response with if the bot did not find what you asked for.
    * multiple_answers: Text when multiple answers are found.