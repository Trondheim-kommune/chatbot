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


class WebScraperSpider(scrapy.Spider):
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

    # The links to start the crawling process on.
    start_urls = [
<<<<<<< Updated upstream
        'https://www.trondheim.kommune.no',
=======
        #'https://www.trondheim.kommune.no'
        'https://www.trondheim.kommune.no/tema/kultur-og-fritid/lokaler/husebybadet/'
>>>>>>> Stashed changes
    ]

    # Paths on the site which are allowed. Only paths which match
    # these will ever be visited.
    allowed_paths = [
<<<<<<< Updated upstream
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
=======
        #'https://www.trondheim.kommune.no/tema',
        #'https://www.trondheim.kommune.no/aktuelt',
        #'https://www.trondheim.kommune.no/org'
>>>>>>> Stashed changes
    ]

    # These selectors will be removed from all pages, as they contain very
    # little actual information, and are equal on all pages.
    garbage_elements = ['.footer', '.header', 'body > .container',
                        '.skip-link', '.navigation', '.nav']

    # The text used for the title on 404 pages. Used to detect silent 404 error.
    not_found_text = 'Finner ikke siden'

    # Hierarchy for sorting categories.
    hierarchy = {
<<<<<<< Updated upstream
        # Header elements.
        'h1': 1,
        'h2': 2,
        'h3': 3,
        'h4': 4,
        'h5': 5,
        'h6': 6,
        # Table elements.
        'tbody': 6,
        'tr': 7,
        'th': 8,
        # Text elements and lists.
        'strong': 8,
        'p': 8,
        'ul': 8,
        'li': 9,
        'a': 10,
    }

    # If a tag is listed here, sequences of tabs belonging to one of these types
    # will all be merged into one tag. For example, directly following paragraph
    # tags will be merged into one big paragraph, separated with newlines.
    concatenation_tags = ['p']

    def extract_metadata(self, root, soup, page_id):
        ''' Extract keywords metadata from the header of the page and add them
        as children of the tree root element. '''
=======
        'h1': {'level': 1},
        'h2': {'level': 2},
        'h3': {'level': 3},
        'h4': {'level': 4},
        'h5': {'level': 5},
        'h6': {'level': 6},
        'tbody': {'level': 6},
        'strong': {'level': 8},
        'p': {'level': 8},
        'a': {'level': 10},
    }

    # Hierarchy for sorting according to html structure
    html_hierarchy = {
        'tr': {'level': 1},
        'td': {'level': 2},
        'ul': {'level': 1},
        'li': {'level': 2}
    }

    def extract_metadata(self, root, soup):
        """Extract keywords metadata from the header of the page and add them
        as children of the tree root element."""
>>>>>>> Stashed changes

        # Attempt finding the keywords meta tag on the page.
        keywords = soup.find('meta', attrs={'name': 'keywords'})

        if keywords and 'content' in keywords.attrs:
            # Add the keywords beneath the title in the tree, if the meta tag
            # has the content attribute correctly specified.
            TreeElement('meta', page_id, keywords.attrs['content'], parent=root)

    def locate_parent(self, elem_tag, current_parent, root):
<<<<<<< Updated upstream
        ''' Locate the parent element on which we should insert the next
        node in the tree, based on our hierarchy of tags. '''
=======
        """Locate the parent element on which we should insert the next
        node in the tree, based on our hierarchy of tags."""

        # Data about this elements position in the hierarchy.
        elem_in_hierarchy = None
        if elem_tag in self.hierarchy:
            elem_in_hierarchy = self.hierarchy[elem_tag]

        # Data about this elements position in the html hierarchy
        elem_in_html_hierarchy = None
        if elem_tag in self.html_hierarchy:
            elem_in_html_hierarchy = self.html_hierarchy[elem_tag]
>>>>>>> Stashed changes

        # This elements position in the hierarchy.
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
<<<<<<< Updated upstream
            search_parent_level = self.hierarchy[search_parent.tag]
=======
            search_parent_in_hierarchy = None
            if search_parent.tag in self.hierarchy:
                search_parent_in_hierarchy = self.hierarchy[search_parent.tag]

            # Whether the search parent is in the html hierarchy or not.
            search_parent_in_html_hierarchy = None
            if search_parent.tag in self.html_hierarchy:
                search_parent_in_html_hierarchy = self.html_hierarchy[search_parent.tag]
            
>>>>>>> Stashed changes

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
            elif search_parent_in_html_hierarchy:
                # If both tags are in the html hierarchy, check their level
                if elem_in_html_hierarchy:
                    if elem_level > search_parent_in_html_hierarchy['level']:
                        parent = search_parent
                        break

                    if elem_level == search_parent_in_html_hierarchy['level']:
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
            for br in elem.find_all('br'): br.replace_with('\n')

            # Remove trailing and tailing spaces from the node contents.
            elem_text = elem.text.strip()

            # Find the type of this element.
            elem_tag = elem.name

            # Do not allow tree nodes with empty text.
<<<<<<< Updated upstream
            if not elem_text: continue

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
=======
            if not elem_text:
                continue

            # Handle switching parent between strong and paragraph tag if
            # strong tag is considered a sub header flag is enabled
            if self.strong_headers and elem_tag == 'strong' \
                    and previous_paragraph:

                parent = previous_paragraph.parent
                if previous_paragraph.parent.tag == 'strong':
                    parent = previous_paragraph.parent.parent
                    
                current_parent = TreeElement(
                    elem_tag,
                    elem_text,
                    parent,
                    sha1(response.url.encode()).hexdigest(),
                )
                previous_paragraph.parent = current_parent
                continue
>>>>>>> Stashed changes

            # Locate the parent element to use based on the hierarchy.
            parent = self.locate_parent(elem_tag, current_parent, root)

            # Concatenate tags like paragraph tags which directly follow each other.
            if elem_tag in self.concatenation_tags and parent.children:
                last_child = parent.children[-1]

<<<<<<< Updated upstream
                # Start a new paragraph if the last child already has children.
                if last_child and last_child.tag == elem_tag and not last_child.children:
                    last_child.text += '\n\n' + elem_text
                    continue
=======
                # Update the previous paragraph.
                previous_paragraph = current_parent
            
            # Add the anchor's href url when finding an anchor
            if elem_tag == 'a':
                if elem.get('href') is not None:
                    elem_text += '\n' + elem.get('href')
>>>>>>> Stashed changes

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
                            any(re.match(regex, next_page.url) for regex in self.visit_blacklist):
                        yield response.follow(next_page, self.parse)
                        break
