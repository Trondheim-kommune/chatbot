import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.http import HtmlResponse
from bs4 import BeautifulSoup
from anytree import RenderTree, NodeMixin

tree_node_id = 0

class TreeElement(NodeMixin):
    def __init__(self, tag, text, parent=None):
        global tree_node_id
        self.name = tag
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
            # Find all paragraphs in the response.
            paragraphs = response.css('p')

            for paragraph in paragraphs:
                # Return the paragraph contents and the link
                # the paragraph was retrieved from.
                yield {
                    'url': response.url,
                    'contents': paragraph.extract(),
                }

            elements = response.css('h1, h2, h3, h4, h5, h6, p')

            # Root element
            root = TreeElement("root", "root", None)
            # Current position, parent, in hierachy
            current_position = root

            for elem in elements:
                elem_text = BeautifulSoup(elem.extract()).text
                elem_tag = list(BeautifulSoup(elem.extract(), "html.parser").children)[0].name

                # Find parent for element
                parent = None

                # p is always a child of current posistion
                if elem_tag == "p":
                    TreeElement(elem_tag, elem_text, current_position)
                else:
                    # If element has same level in hierachy
                    if elem_tag == current_position.tag:
                        parent = current_position.parent
                    elif current_position.tag != "root" and int((elem_tag[1])) > (int(current_position.tag[1])):
                        # If we have found child of currentposition
                        parent = current_position

                    else:
                        # search for appropriate parent
                        temp_parent = current_position
                        while True:
                            # if we find root
                            if temp_parent == root:
                                parent = root
                                break

                            # if we have found the same level in hierarchy
                            if int(temp_parent.tag[1]) == int(elem_tag[1]):
                                parent = temp_parent.parent
                                break
                                # Set parent according to header hierarchy
                            elif int(temp_parent.tag[1]) < int(elem_tag[1]):
                                parent = temp_parent
                                break


                            # Update current parent when searching
                            temp_parent = temp_parent.parent

                    # Create element
                    current_position = TreeElement(elem_tag, elem_text, parent)

            # Printing nodetree
            for pre, fill, node in RenderTree(root):
                print("%s%s" % (pre, node.text))


            # Follow all links from allowed domains.
            for next_page in LinkExtractor().extract_links(response):
                for allowed_path in self.allowed_paths:
                    # Only follow the link if it is in the list
                    # of allowed paths.
                    if allowed_path in next_page.url:
                        yield response.follow(next_page, self.parse)
                        break
