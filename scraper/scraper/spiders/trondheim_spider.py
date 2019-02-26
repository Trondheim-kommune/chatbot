import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.http import HtmlResponse
from bs4 import BeautifulSoup
from anytree import RenderTree, NodeMixin
from anytree.exporter import DictExporter
from hashlib import sha1
import re


class TreeElement(NodeMixin):
    # A counter used to give an unique ID to all nodes.
    counter = 0

    def __init__(self, tag, page_id, text=None, parent=None):
        ''' Tree node which stores information about an HTML tag. '''

        self.tag = tag
        self.text = text
        self.parent = parent

        # We hash the URL of all pages and add a counter for the element
        # after it. This is used to diff new and stored HTML pages.
        self.id = '%s-%s'.format(page_id, TreeElement.counter)
        TreeElement.counter += 1


class TrondheimSpider(scrapy.Spider):
    # Name of the spider. This is the name to use from the Scrapy CLI.
    name = 'trondheim'

    # The following few lines contain command line flags.
    # All flags default to false, so do not explicitly set them as so.
    # See the GitHub Wiki for information about how these are used.
    
    # Enable to display additional debugging information to output when the crawler is run.
    # In practice, this will pretty print the exported tree when a page is scraped.
    debug = None

    # If a strong tag should be seen as a sub header.
    strong_headers = None

    # Enable concatenation of paragaph tags under same header to be seen as one paragraph.
    concatenate_p = None

    # The links to start the crawling process on.
    start_urls = [
        'https://www.trondheim.kommune.no',
    ]

    # Paths on the site which are allowed. Only paths which match
    # these will ever be visited.
    allowed_paths = [
        re.compile('https://www.trondheim.kommune.no/tema'),
        re.compile('https://www.trondheim.kommune.no/aktuelt'),
        re.compile('https://www.trondheim.kommune.no/org'),
    ]

    # Pages in this list will be visited and links on them will
    # be visited, however the data will not be scrapaed.
    scrape_blacklist = [
        # Do not add data from the home page, it ranks highly but is completely useless.
        re.compile('https://www.trondheim.kommune.no/?$'),
    ]

    # These links will never be visited, even if the path is allowed above.
    visit_blacklist = [
        # News articles.
        re.compile('https://www.trondheim.kommune.no/aktuelt'),
        # Avoid misinformation about health and safety.
        re.compile('https://www.trondheim.kommune.no/tema/helse-og-omsorg'),
    ]

    # These selectors will be removed from all pages, as they contain very
    # little actual information, and are equal on all pages.
    garbage_elements = ['.footer', '.header', 'body > .container',
                        '.skip-link', '.navigation', '.nav']

    not_found_text = 'Finner ikke siden'

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

    def extract_metadata(self, root, soup, page_id):
        ''' Extract keywords metadata from the header of the page and add them
        as children of the tree root element. '''

        # Attempt finding the keywords meta tag on the page.
        keywords = soup.find('meta', attrs={'name': 'keywords'})

        if keywords and 'content' in keywords.attrs:
            # Add the keywords beneath the title in the tree, if the meta tag
            # has the content attribute correctly specified.
            TreeElement('meta', page_id, keywords.attrs['content'], parent=root)

    def locate_parent(self, elem_tag, current_parent, root):
        ''' Locate the parent element on which we should insert the next
        node in the tree, based on our hierarchy of tags. '''

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
        ''' Creates a tree structure describing the given page. This structure
        is based on headers, creating a hierarchy based on text pieces which
        are positioned in between different types of headers. '''

        # Reset id to 0 when on a new page.
        TreeElement.counter = 0

        # Hash the page URL, it will be used as an ID.
        page_id = sha1(response.url.encode()).hexdigest()

        # Parse the HTML using BeautifulSoup. Make sure we use LXML for parsing.
        soup = BeautifulSoup(response.text, 'lxml')

        # We only care about elements on the page which are defined in the hierarchy.
        elements = soup.find_all(self.hierarchy.keys())

        # We remove the header and footer tags from the page to reduce
        # bloat, as these contain little useful information.
        for garbage_selector in self.garbage_elements:
            for garbage_element in soup.select(garbage_selector):
                garbage_element.decompose()

        # Locate the title element. It might be used for the tree root.
        title = soup.find('title').text

        # Do not continue with this page if we detect it as a silent 404.
        if self.not_found_text in title: return

        # Use the title as the tree root.
        root = TreeElement('title', page_id, soup.find('title').text)

        # Attempt extracting the keywords and adding them to the tree.
        self.extract_metadata(root, soup, page_id)

        # Current position in the hierarchy.
        current_parent = root

        # Keep track of paragraph tag to be able to switch
        # position with strong tags.
        previous_paragraph = None

        for elem in elements:
            # Replace BR tags with newlines.
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
            # the flag enabling this feature is set.
            if self.strong_headers and elem_tag == 'strong' and previous_paragraph:
                current_parent = TreeElement(
                    elem_tag,
                    page_id,
                    elem_text,
                    previous_paragraph.parent,
                )

                previous_paragraph.parent = current_parent

                continue

            # Locate the parent element to use based on the hierarchy.
            parent = self.locate_parent(elem_tag, current_parent, root)

            # Concatenation of paragraph tags with same parent to collect
            # the same type of information spread among different paragraph tags.
            if elem_tag == 'p':
                if self.concatenate_p and previous_paragraph \
                        and previous_paragraph.parent == parent:
                    previous_paragraph.text += '\n\n' + elem_text
                    continue

                # Update the previous paragraph.
                previous_paragraph = current_parent

            # Create the new element.
            current_parent = TreeElement(
                elem_tag,
                page_id,
                elem_text,
                parent,
            )

        return root

    def pretty_print_tree(self, root):
        ''' Print a scraped tree for debugging. '''

        for pre, fill, node in RenderTree(root):
            # We remove newlines from the text with spaces to preserve
            # the shape of the tree when printing in the terminal.
            print('%s%s: %s' % (pre, node.tag, node.text.replace('\n', ' ')))

        # Also add a new line before the next tree.
        print()

    def parse(self, response):
        ''' Parses pages which have been requested from the server. '''

        # Only store HTML responses, not other attachments.
        if isinstance(response, HtmlResponse):
            if not any(re.match(regex, response.url) for regex in self.scrape_blacklist):
                # Generate a tree structure describing this page.
                root = self.generate_tree(response)

                # The parser might choose to ignore this page, for example when we
                # detect that the page is a 404 page. In that case, skip the page.
                if root:
                    # Pretty print the node tree if the DEBUG flag is set.
                    if self.debug: self.pretty_print_tree(root)

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
                    if re.match(allowed_path, next_page.url) and not \
                            any(re.match(regex, response.url) for regex in self.visit_blacklist):
                        yield response.follow(next_page, self.parse)
                        break
