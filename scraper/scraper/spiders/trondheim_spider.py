import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.http import HtmlResponse
from bs4 import BeautifulSoup
from anytree import RenderTree, NodeMixin
from anytree.exporter import DictExporter

# Global ID counter for nodes.
tree_node_id = 0

class TreeElement(NodeMixin):
    def __init__(self, tag, text, parent=None):
        """Tree node which stores information about an HTML element."""
        global tree_node_id
        self.tag = tag
        self.text = text
        self.parent = parent
        self.id = tree_node_id
        tree_node_id += 1


class TrondheimSpider(scrapy.Spider):
    # Name of the spider. This is the name to use from the Scrapy CLI.
    name = 'trondheim'

    # The links to start the crawling process on.
    start_urls = [
        'https://trondheim.kommune.no/tema/kultur-og-fritid/',
    ]

    allowed_paths = [
        'https://trondheim.kommune.no/tema/kultur-og-fritid/',
    ]

    # Parses the latest response.
    def parse(self, response):
        # Only store HTML responses, not other attachments.
        if isinstance(response, HtmlResponse):
            elements = response.css('h1, h2, h3, h4, h5, h6, p')

            # Root element of the tree.
            root = TreeElement('root', 'root', None)

            # Current position in the tree.
            current_position = root

            for elem in elements:
                # Parse the element using BeautifulSoup.
                soup = BeautifulSoup(elem.extract(), 'html.parser')

                current_text = soup.text

                current_tag = list(soup.children)[0].name

                # The parent which will be used for the current element.
                parent = None

                # Paragraphs are always a children, they cannot contain any headers.
                if current_tag == 'p':
                    # Add the paragraph to the tree.
                    TreeElement(current_tag, current_text, current_position)
                else:
                    # If this header is at the same level in the hierarchy.
                    if current_tag == current_position.tag:
                        parent = current_position.parent
                    elif current_position.tag != 'root' and int((current_tag[1])) > (int(current_position.tag[1])):
                        # If we have found a child of the current position.
                        parent = current_position

                    else:
                        # Search for the appropriate parent.
                        search_position = current_position
                        
                        while True:
                            # If we reach the root element.
                            if search_position == root:
                                parent = root
                                break

                            # If we have found the same level in hierarchy.
                            if int(search_position.tag[1]) == int(current_tag[1]):
                                parent = search_position.parent
                                break

                            # Set parent according to header hierarchy.
                            elif int(search_position.tag[1]) < int(current_tag[1]):
                                parent = search_position
                                break

                            # Update current parent when searching
                            search_position = search_position.parent

                    # Create the new tree node.
                    current_position = TreeElement(current_tag, current_text, parent)

            exporter = DictExporter()

            yield {
                'url': response.url,
                'tree': exporter.export(root)
            }

            # Follow all links from allowed domains.
            for next_page in LinkExtractor().extract_links(response):
                for allowed_path in self.allowed_paths:
                    # Only follow the link if it is in the list
                    # of allowed paths.
                    if allowed_path in next_page.url:
                        yield response.follow(next_page, self.parse)
                        break
