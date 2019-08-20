# Chatbot

[![Build Status](https://travis-ci.com/vegarab/agent-25.svg?token=L9RN2jPDa7p43DCcYhYZ&branch=dev)](https://travis-ci.com/vegarab/agent-25)
[![codecov](https://codecov.io/gh/vegarab/agent-25/branch/dev/graph/badge.svg?token=ArL47bWQSN)](https://codecov.io/gh/vegarab/agent-25)

This is a general purpose, retrieval-based chatbot, initially built as a
Bachelor's project at NTNU. The bot is self-learning, based on an XML-based
knowledge (e.g. a website). The main purpose of this project is to greatly
reduce the required resources for building a production-ready chatbot system
that can be deployed anywhere. This issue is solved by automatically scraping
data from a specific knowledge base, strcturing and indexing the data and
constructing a language model based on the knowledge base. The chatbot is then
capable of recieving queries from a user, phrased with natural human language,
while the system in turn attempts to return an answer using the information
stored in the knowledge base. 

This project was carried out by a group of six students in their third year
at the Informatics study at the Norwegian Unviversity of Science and
Technology, as a part of their bachelor thesis course IT2901. Trondheim
Kommune was the project customer, and the goal of the projet was to create
a system which could easiy be introduced to their, as well as other, websites.
The group also produced a report which describes the product as well as the
process behind it in great detail. The initial project was developed as a
prototype, while some further development has been carried out in order to make
the system production ready.

## Project structure

The project is divided into three main parts, in an MVC-inspired fashion (by
request from the product customer). This is is to make the exchange of any
module easier.

- An information gathering module `chatbot/scraper` - a highly general web
  scraper capable of indexing XML-structured data.
- A data model, representing the knowledge base of the bot `chatbot/model`.
  This is a non-SQL based system, powered by MongoDB
- A language processing and query module `chatbot/nlp` that performs similarity
  measures and matching between an input user query and knowledge in the model.

In addition, the project includes a web-interface that allows for modifcation
of the knowledge base, `chatbot/web`. This provides an administration control
panel which allows admins to fine-tune the results which are returned by the
system by overriding answers stored in the knowledge base.

Communication between the data model, language processing module, web-interface
and chat integrations is carried out through an HTTP-based API, `chatbot/api`.
This API also includes integration directly to Google's DialogFlow, allowing
for easy interaction with existing chat-view systems such as Facebook Messenger
and Slack.

# Project requirements
This system assumes a UNIX-like (pref. Linux) system, with a minimum of 2 CPU
Cores and 2GB of RAM (depending on the size of the knowledge base). Integration
to DialogFlow requires HTTPS, but this is disabled by default. 

The system is designed to run in Docker-containers, using Docker compose.

## System setup
### Environment variables
`DB_USER` and `DB_PWD` for accessing mongoDB.

`PROJECT_ID` and `GOOGLE_APPLICATION_CREDENTIALS` (filepath, JSON) if using DialogFlow
Integrations.


### Deployment
Build the system
```
make build
```
or through a clean build `make build-clean`. 

Start up the system through
```
make start
```

This will start up three containers: 
* mongoDB instance
* Python-powered HTTP API
* Web app powered by NodeJS

Entering the API container:
```
make open-bash-chatbot
```
Entering the web container
```
make open-bash-web
```

The automatic test-suite can also be executed within Docker:
```
make test-docker
```

Logs can be accessed through 
```
make docker-logs
```

### Development setup
#### Installation
Python dependencies:
```
pip install -r requirements.txt
```

Node dependencies:
```
cd chatbot/web
npm install
npm build
rm /usr/share/nginx/html/ -r
cp build /usr/share/nginx/html/ -r
```

Install the latest version of MongoDB, creating a user matching the user in
`chatbot/settings.json` to the two databases specified `dev_db` and `prod_db`. 

#### Start the API:
```
./chatbot/api/start_server.sh
```

#### Start the web application
```
cd chatbot/web
npm run
```

#### Prototype chat view
```
python chatbot/prototype.py
```


## Settings file
There is a settings file called `chatbot/settings.json`, in this file there are
multiple things you could change. Every change needed to make this project work on any website should be able to be configured here. 

* mongo
    * Change things like username, password, ip(url), port, what the database is called and what the testing database is called.
* model
    * The only thing you can change here is accepted_tags. This changes which HTML element are allowed to be made into a leaf node.
* scraper
    * debug: If you want more logging to stdout whilst running the scraper.
    * alternative_headers: If elements such as strong tags should be seen as a sub header.
    * concatenation: This is a list of elements that you may want to concatenate with other siblings of the same element. Also a value for the maximum amount of words allowed after concatenation.
    * url:
        * root_url: Which url should the scraper start on.
        * allowed_paths: Which paths should the scraper be allowed to scrape. (list)
    * blacklist:
        * elements: These selectors will be removed from all pages, as they contain very little actual information, and are equal on all pages.
        * scrape: Pages in this list will be visited and links on them will be visited, however the data will not be scraped.
        * visit: Sites that should never be visited by the scraper.
        * texts: Elements containing text equal to one of these sentences will be removed from all pages.
        * start_url: Ignore the url if it starts with this.
        * resources: Elements containing an url in href that ends with the following will be removed.
        * not_found_text: The text used for the title on 404 pages. Used to detect silent 404 errors.
    * hierarchy:
        * How the different HTML elements should be sorted.
* query_system
    * not_found: Text that the bot should response with if the bot did not find what you asked for.
    * multiple_answers: Text when multiple answers are found.


## LICENSE
Chatbot Copyright GPLv3 (C) 2019  Vegar Andreas Bergum, Tinus Flagstad, Thomas Skaaheim, Torjus Iveland, Anders Hopland

Spellchecker content CC-by-sa-3.0 license
