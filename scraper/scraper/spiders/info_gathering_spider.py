import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.http import HtmlResponse
from bs4 import BeautifulSoup
from anytree import RenderTree, NodeMixin
from anytree.exporter import DictExporter
from hashlib import sha1
import re
from urllib.parse import urlparse
from urllib.parse import urljoin


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
        self.id = '{}-{}'.format(page_id, TreeElement.counter)
        TreeElement.counter += 1


class InfoGatheringSpider(scrapy.Spider):
    # Name of the spider. This is the name to use from the Scrapy CLI.
    name = 'info_gathering'

    # The following few lines contain command line flags.
    # All flags default to false, so do not explicitly set them as so.
    # See the GitHub Wiki for information about how these are used.

    # Enable to display additional debugging information to output when the crawler is run.
    # In practice, this will pretty print the exported tree when a page is scraped.
    debug = None

    # If a strong tag should be seen as a sub header.
    strong_headers = None

    # Root url for all web pages. Must not end with '/'.
    root_url = 'https://www.trondheim.kommune.no'

    # The links to start the crawling process on.
    start_urls = [
        root_url
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
        # These pages are pretty boring and contain an awful lot of maps.
        re.compile('https://www.trondheim.kommune.no/tema/bygg-kart-og-eiendom'),
        # These pages contain large blocks of text.
        re.compile('https://www.trondheim.kommune.no/tema/skatt-og-naring'),
        # These pages are quite technical in their nature.
        re.compile('https://www.trondheim.kommune.no/tema/veg-vann-og-avlop'),
        # These pages are difficult to parse and contain little information.
        re.compile('https://www.trondheim.kommune.no/aktuelt/utvalgt/om-kommunen'),
    ]

    # These selectors will be removed from all pages, as they contain very
    # little actual information, and are equal on all pages.
    garbage_elements = ['.footer', '.header', 'body > .container',
                        '.skip-link', '.navigation', '.nav', '#ssp_fantdu']

    # Elements containing text equal to one of these sentences will be
    # removed from all pages.
    garbage_text = ['Sist oppdatert:', 'Se kart', '_______________']

    # Elements containing an url in href that starts with the following
    # will be removed
    garbage_start_urls = ['#', '.', '~']

    # Elements containing an url in href that ends with the following
    # will be removed.
    garbage_resources = ['.aspx']

    # The text used for the title on 404 pages. Used to detect silent 404 error.
    not_found_text = 'Finner ikke siden'

    # Hierarchy for sorting categories.
    # Elements with level=None will follow normal html hierarchy
    hierarchy = {
        # Header elements.
        'h1': 1,
        'h2': 2,
        'h3': 3,
        'h4': 4,
        'h5': 5,
        'h6': 6,

        # Text elements
        'strong': 10,
        'p': 11,
        'a': 15,

        # Table elements
        'tr': 8,

        # List elements
        'li': 9,
    }

    # If a tag is listed here, sequences of tabs belonging to one of these types
    # will all be merged into one tag. For example, directly following paragraph
    # tags will be merged into one big paragraph, separated with newlines.
    # The value corresponding to each key is the word limit for when
    # the following tag can be merged together
    concatenation_tags_word_limit = {
        'li': 100,
        'p': 7,
    }

    # Of the elements in the hierarchy, these tags will not be created as nodes if
    # their parent is in the set of parents.
    ignored_children_tags_for_parents = {
        'strong': {'p', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'h5'},
        'p': {'li'},
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

        # Data about this elements position in the hierarchy.
        elem_level = None
        if elem_tag in self.hierarchy:
            elem_level = self.hierarchy[elem_tag]

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
            search_parent_level = None
            if search_parent.tag in self.hierarchy:
                search_parent_level = self.hierarchy[search_parent.tag]

            if search_parent_level:
                # If both tags are in the hierarchy, check their level.
                if elem_level:
                    if elem_level > search_parent_level:
                        parent = search_parent
                        break

                    if elem_level == search_parent_level:
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
        if self.not_found_text in title:
            return

        # Use the title as the tree root.
        root = TreeElement('title', page_id, soup.find('title').text)

        # Attempt extracting the keywords and adding them to the tree.
        self.extract_metadata(root, soup, page_id)

        # Current position in the hierarchy.
        current_parent = root

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

            # Set list for list point element
            if elem_tag == 'li':
                elem_text = '- ' + elem_text

            # Do not include elements with element text containing
            # blacklisted sentences.
            if any(sentence in elem_text for sentence in self.garbage_text):
                break

            if self.strong_headers:
                # If a paragraph contains a strong tag, and the correct lag is set, we
                # treat that combination as a header. This check avoids adding the strong
                # tag in addition to the custom header.
                if elem_tag == 'strong' and current_parent.tag == 'h6' and \
                        current_parent.text == elem_text:
                    continue

                if elem_tag == 'p':
                    # Find all strong tags inside this paragraph.
                    strongs = elem.find_all('strong')

                    # Check if there is only 1 strong tag, and check if it contains
                    # all of the text inside the paragraph.
                    if len(strongs) == 1 and elem_text == strongs[0].text.strip():
                        # Locate the parent in which a H6 tag would be inserted.
                        parent = self.locate_parent('h6', current_parent, root)

                        # Add a custom H6 element instead of a paragraph or strong element
                        current_parent = TreeElement(
                            'h6',
                            page_id,
                            elem_text,
                            parent,
                        )
                        continue

            # Locate the parent element to use based on the hierarchy.
            parent = self.locate_parent(elem_tag, current_parent, root)

            # Concatenate tags like paragraph tags which directly follow each other.
            if elem_tag in self.concatenation_tags_word_limit and parent.children:
                last_child = parent.children[-1]

                # Start a new paragraph if the last child already has children.
                if last_child and last_child.tag == elem_tag and not last_child.children:
                    # Concatenate the texts until limit reached
                    if len(elem_text.split()) \
                            <= self.concatenation_tags_word_limit[elem_tag]:
                        last_child.text += '\n' + elem_text
                        continue

            # Add the anchor's href url when finding an anchor
            # If anchor, don't create a new element, but add url instead to parent
            if elem_tag == 'a':
                # Create a valid url from the href url if any
                url = self.create_valid_url(elem.get('href'))

                # If the url from href is invalid, ignore anchor tag
                if url is None:
                    continue

                # If the URL is unequal to the elem text
                if url != elem_text:
                    # Add the element text to parent instead of creating a
                    # new element
                    if elem_text in parent.text:
                        parent.text += '\n' + url
                        continue

                    # Add the URL and elem_text into the end of the parent's text
                    parent.text += ' ' + elem_text + '\n' + url
            elif elem_tag in self.ignored_children_tags_for_parents \
                    and current_parent.tag \
                    in self.ignored_children_tags_for_parents[elem_tag]:
                # If the parent's text includes this element's text,
                # don't create a node for this element.
                continue
            else:
                # Create the new element.
                current_parent = TreeElement(
                    elem_tag,
                    page_id,
                    elem_text,
                    parent,
                )

        return root

    # Returns a valid url based on blacklisting and type
    def create_valid_url(self, url):
        ''' Takes in an url from an anchor tag's href.
        Returns None if the url is None, blacklisted or invalid.
        Returns an absolute url otherwise. '''

        # If the url isn't defined
        if url is None:
            return None

        # Check if the url stars with blacklisted characters
        for start_url in self.garbage_start_urls:
            if url.startswith(start_url):
                return None

        # Check if the url is a blacklisted resource or file type
        for end_url in self.garbage_resources:
            if url.endswith(end_url):
                # This url is blacklisted, ignore this element
                return None

        # If the url is relative or a valid resource link
        if not bool(urlparse(url).netloc):
            # Concatenate the root and relative url
            url = urljoin(self.root_url, url)

        return url

    def pretty_print_tree(self, root):
        ''' Print a scraped tree for debugging. '''

        for pre, fill, node in RenderTree(root):
            # We remove newlines from the text with spaces to preserve
            # the shape of the tree when printing in the terminal.
            print('{}{}: {}'.format(pre, node.tag, node.text.replace('\n', ' ')))

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
                    if self.debug:
                        self.pretty_print_tree(root)

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
                            any(re.match(regex, next_page.url) for regex in self.visit_blacklist):
                        yield response.follow(next_page, self.parse)
                        break
