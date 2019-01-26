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
            # Parse the raw HTML using BeautifulSoup.
            soup = BeautifulSoup(response.body)

            # Remove elements which are not rendered in the browser.
            for script in soup(['script', 'style']): script.extract()
            
            # Extract the raw text from the document/
            text = soup.get_text()

            # Strip extra spaces around all lines.
            lines = (line.strip() for line in text.splitlines())

            # Remove blank lines.
            text = '\n'.join(line for line in lines if line)

            # Yield the data we store for this page.
            yield {
                'url': response.url,
                'text': text,
            }

            # Follow all links from allowed domains.
            for next_page in LinkExtractor().extract_links(response):
                for allowed_path in self.allowed_paths:
                    if allowed_path in next_page.url:
                        yield response.follow(next_page, self.parse)
                        break
