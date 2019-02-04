# agent-25
This is a chatbot using google dialogflow, which scrapes and indexes sites itself. The project is developen in cooperation with Trondheim Kommune, where the goal is to integrate this with their website.
## Technology
The text processing part of the project is built around google dialogflow. The scraping part is made up of a python scraper using scrapy and beautilfulsoup. The data from the scraper is then read into a MongoDB databse. Python flask is used to create a rest framework to communicate with the backend.
