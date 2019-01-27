import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.http import HtmlResponse
from bs4 import BeautifulSoup


class TrondheimSpider(scrapy.Spider):
    # Name of the spider. This is the name to use from the Scrapy CLI.
    name = 'trondheim'

    # The links to start the crawling process on.
    start_urls = [
        'https://trondheim.kommune.no',
    ]

    allowed_paths = [
        'trondheim.kommune.no/tema',
    ]

    # Parses the latest response.
    def parse(self, response):
        # Only store HTML responses, not other attachments.
        if isinstance(response, HtmlResponse):
            # Find all paragraphs in the response.
            paragraphs = response.css('p')

            for paragraph in paragraphs:
                # Return the paragraph contents and the link
                # the paragraph was retrieved from.
                yield {
                    'url': response.url,
                    'contents': paragraph.extract(),
                }

            # Follow all links from allowed domains.
            for next_page in LinkExtractor().extract_links(response):
                for allowed_path in self.allowed_paths:
                    # Only follow the link if it is in the list
                    # of allowed paths.
                    if allowed_path in next_page.url:
                        yield response.follow(next_page, self.parse)
                        break
