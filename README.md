# Agent 25

[![Build Status](https://travis-ci.com/vegarab/agent-25.svg?token=L9RN2jPDa7p43DCcYhYZ&branch=dev)](https://travis-ci.com/vegarab/agent-25)
[![codecov](https://codecov.io/gh/vegarab/agent-25/branch/dev/graph/badge.svg?token=ArL47bWQSN)](https://codecov.io/gh/vegarab/agent-25)

Agent 25 is a prototype for a chatbot which is able to teach itself. The
purpose of this project is to greatly reduce the time which must be spent
manually creating training data for chatbots, by automating the process.
This project attempts to do this by automatically scraping data from a
specific website, structuring it, and using the data to create a knowledge
base for the chatbot. When the chatbot frontend receives a query from an user,
the query is forwarded to this system, which in turn attempts to formulate
a query using the information stored in the knowledge base.

This project was carried out by a group of six students in their third year
at the Informatics study at the Norwegian Unviversity of Science and
Technology, as a part of their bachelor thesis course IT2901. Trondheim
Kommune was the project customer, and the goal of the projet was to create
a system which could easiy be introduced to their as well as other websites.
Additional project documentation is available in the project wiki. The group
also produced a report which describes the product as well as the process
behind it in great detail.

## Project structure

As requested by the customer, this project is divided into three main parts in
an MVC-inspired fashion. This is to make it easier to exchange any of the three
parts of the system.

- Google DialogFlow is used for the frontend part of the chatbot. The code in
  this project handles the response generation, which is then fed to DialogFlow.
- `api` contains a Flask API whose main task is to interface with DialogFlow.
- `model` contains a knowledge base using MongoDB. This part of the project
  attempts to structure and store information for later retrieval, and is also
  responsible for formulating answers when a query is sent to the API.

The project also contains a couple other modules, whcih do not tie directly
into the MVC-inspired structure of the project.

- `scraper` contains a web scraper using Scrapy. This system visits all pages
  on a given domain, and attempts to extract information which is then fed to
  the knowledge base.
- `website` contains a simple administration control panel which allows administrators
to fine-tune the results which are returned by the system, by overriding answers
stored in the knowledge base.

# Project requirements

This project is currently designed to be used with DialogFlow using webbooks.
In order to communicate with DialogFlow, the API needs to run on a server which
has HTTPS enabled. This is also required during development, if you want to
develop on all parts of the system

This project is currently hosted on a DigitalOcean Droplet, using NGINX as
the server and `certbot` for the required SSL certificates. The project is
not particulary resource-intensive, but some of the natural language processing
functionality can be taxing. We therefore reccoment using at least a 4 core CPU
with 4GB of RAM.

# Setup

This project currently uses virtual environments. To start the project, run
`./setup.sh`. This will create a new virtual environment with all dependencies
installed.

To run the scraper and populate the knowledge base, run `./model/start.sh`. This
command might take multiple minutes to finish. Whe

When the knowledge base is populated with data, the server can be started. To do
this, run `./api/flask/start_server_screen.sh`. This will start the server in
the background. You can see the logs by using `screen -r`.

To start the website, run `cd website`, `npm install` and `npm start`. The website
is a simple React app which uses `create-react-app`. The tests for the website are
written using Cypress, and the test suite can be run by executing `npm run cypress open`.

If you want to build the website on a server where NGINX is already installed, you
can alternatively use the command `./build_web_server.sh`. This will build the project
and copy the files to `/usr/share/nginx/html/`. Inspect the script for further information.



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
