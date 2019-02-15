import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.http import HtmlResponse
from bs4 import BeautifulSoup
from anytree import RenderTree, NodeMixin
from anytree.exporter import DictExporter


class TreeElement(NodeMixin):

    # A counter used to give an unique ID to all nodes.
    counter = 0

    def __init__(self, tag, text=None, parent=None):
        """Tree node which stores information about an HTML tag."""

        self.tag = tag
        self.text = text
        self.parent = parent

        # We use the current counter value for the ID, and then increment
        # it so that the value will always be unique.
        self.id = TreeElement.counter
        TreeElement.counter += 1


class TrondheimSpider(scrapy.Spider):
    # Name of the spider. This is the name to use from the Scrapy CLI.
    name = 'trondheim'

    # When this flag is set, we display additional debugging information
    # when the crawler is run in a terminal.
    # Add -a debug=<boolean> to the end of the command for debug mode
    # Default: False
    # Ex: scrapy crawl trondheim -o trondheim.json -a debug=True
    debug = False

    # If strong tag should be seen as a sub header
    # Add -a sh=<boolean> to the end of the command.
    # True to set strong as header
    # Default: False
    # Ex: scrapy crawl trondheim -o trondheim.json -a debug=False -a sh=True
    sh = False

    # The links to start the crawling process on.
    start_urls = [
        'https://www.trondheim.kommune.no'
    ]

    # Paths on the site which are allowed.
    allowed_paths = [
        'https://www.trondheim.kommune.no/tema',
        'https://www.trondheim.kommune.no/aktuelt',
        'https://www.trondheim.kommune.no/org'
    ]

    # These selectors will be removed from all pages, as they contain very
    # little actual information, and are equal on all pages.
    garbage_elements = ['.footer', '.header', 'body > .container',
                        '.skip-link']

    # Hierarchy for sorting categories.
    hierarchy = {
        'h1': {'level': 1},
        'h2': {'level': 2},
        'h3': {'level': 3},
        'h4': {'level': 4},
        'h5': {'level': 5},
        'h6': {'level': 6},
        'tbody': {'level': 6},
        'tr': {'level': 7},
        'th': {'level': 8},
        'strong': {'level': 8},
        'p': {'level': 8},
        'ul': {'level': 8},
        'li': {'level': 9},
        'a': {'level': 10},
    }

    def extract_metadata(self, root, soup):
        """Extract keywords metadata from the header of the page and add them
        as children of the tree root element."""

        # Attempt finding the keywords meta tag on the page.
        keywords = soup.find('meta', attrs={'name': 'keywords'})

        if keywords and 'content' in keywords.attrs:
            # Add the keywords beneath the title in the tree, if the meta tag
            # has the content attribute correctly specified.
            TreeElement('meta', keywords.attrs['content'], parent=root)

    def locate_parent(self, elem_tag, current_parent, root):
        """Locate the parent element on which we should insert the next
        node in the tree, based on our hierarchy of tags."""

        # Data about this elements positin in the hierarchy.
        elem_in_hierarchy = self.hierarchy[elem_tag]

        # This elements position in the hierarchy.
        elem_level = elem_in_hierarchy['level']

        # The parent which will be used for the next node in the tree.
        parent = None

        # Search for the appropriate parent element.
        search_parent = current_parent

        while True:
            # If we reach the root node, use it.
            if search_parent == root:
                parent = root
                break

            # We reached a tag of the same type, so use it.
            if search_parent.tag == elem_tag:
                parent = search_parent.parent
                break

            # Whether the search parent is in the hierarchy or not.
            search_parent_in_hierarchy = self.hierarchy[search_parent.tag]

            if search_parent_in_hierarchy:
                # If both tags are in the hierarchy, check their level.
                if elem_in_hierarchy:
                    if elem_level > search_parent_in_hierarchy['level']:
                        parent = search_parent
                        break

                    if elem_level == search_parent_in_hierarchy['level']:
                        # If elements are in same level in hierarchy.
                        parent = search_parent.parent
                        break
                else:
                    # Element where hierarchy is not defined.
                    parent = search_parent
                    break

            # Update the current parent while searching.
            search_parent = search_parent.parent

        # Return the parent element candidate.
        return parent

    def generate_tree(self, response):
        """Creates a tree structure describing the given page. This structure
        is based on headers, creating a hierarchy based on text pieces which
        are positioned in between different types of headers."""

        soup = BeautifulSoup(response.text, 'lxml')

        elements = soup.find_all(self.hierarchy.keys())

        # We remove the header and footer tags from the page to reduce
        # bloat, as these contain little useful information.
        for garbage_selector in self.garbage_elements:
            for garbage_element in soup.select(garbage_selector):
                garbage_element.decompose()

        # We extract the page title and use it to create the tree root.
        root = TreeElement('title', soup.find('title').text)

        # Attempt extracting the keywords and adding them to the tree.
        self.extract_metadata(root, soup)

        # Current position in the hierarchy.
        current_parent = root

        # Keep track of paragraph tag to be able to switch
        # position with strong tags.
        previous_paragraph = None

        for elem in elements:
            # Replace br tag with newline
            for br in elem.find_all('br'):
                br.replace_with('\n')

            # Remove trailing and tailing spaces from the node contents.
            elem_text = elem.text.strip()

            # Find the type of this element.
            elem_tag = elem.name

            # Do not allow tree nodes with empty text.
            if not elem_text:
                continue

            # Handle switching parent between strong and paragraph tag if
            # strong tag is considered a sub header
            if self.sh is True and elem_tag == 'strong' \
                    and previous_paragraph:
                current_parent = TreeElement(
                    elem_tag, elem_text, previous_paragraph.parent)
                previous_paragraph.parent = current_parent
                continue

            # Locate the parent element to use based on the hierarchy.
            parent = self.locate_parent(elem_tag, current_parent, root)

            # Concatenation of p tags with same parent to collect
            # the same type of information spread among different p tags
            if elem_tag == 'p':
                if previous_paragraph and previous_paragraph.parent == parent:
                    previous_paragraph.text += " " + elem_text
                    continue

                # Update the previous paragraph.
                previous_paragraph = current_parent

            # Create the new elemenet.
            current_parent = TreeElement(elem_tag, elem_text, parent)

        return root

    def parse(self, response):
        """Parses pages which have been requested from the server."""

        # Only store HTML responses, not other attachments.
        if isinstance(response, HtmlResponse):
            # Generate a tree structure describing this page.
            root = self.generate_tree(response)

            # Pretty print the node tree if the DEBUG flag is set.
            if self.debug is True:
                for pre, fill, node in RenderTree(root):
                    print('%s%s: %s' % (pre, node.tag, node.text))

            # Export the tree using the DictExporter. Scrapy will then convert
            # this dictionary to a JSON structure for us, automatically.
            exporter = DictExporter()
            tree = exporter.export(root)

            yield {
                # Export the page URL and the tree structure.
                'url': response.url,
                'tree': tree,
            }

            # Follow all links from allowed domains.
            for next_page in LinkExtractor().extract_links(response):
                for allowed_path in self.allowed_paths:
                    # Only follow links that are in the list of allowed paths.
                    if allowed_path in next_page.url:
                        yield response.follow(next_page, self.parse)
                        break
