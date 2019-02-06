import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.http import HtmlResponse
from bs4 import BeautifulSoup
from anytree import RenderTree, NodeMixin
from anytree.exporter import DictExporter

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
    garbage_elements = ['footer', 'header']
    # Hierarchy for sorting categories
    hierarchy = {
        'title': {'level': 0, },
        'h1': {'level': 1 },
        'h2': {'level': 2 },
        'h3': {'level': 3 },
        'h4': {'level': 4 },
        'h5': {'level': 5 },
        'h6': {'level': 6 },
        'tbody': {'level': 6 },
        'tr': {'level': 7},
        'th': {'level': 8},
        'strong': { 'level': 8 },
        'p': {'level': 8 },
        'ul': {'level': 8 },
        'li': {'level': 9 },
        'a': {'level': 10 }
    }

    # The links to start the crawling process on.
    start_urls = [
         'https://www.trondheim.kommune.no/'
    ]

    allowed_paths = [
         'https://www.trondheim.kommune.no/tema/'
    ]

    # Parses the latest response.
    def parse(self, response):
        hierarchy = self.hierarchy

        # Only store HTML responses, not other attachments.
        if isinstance(response, HtmlResponse):
            soup = BeautifulSoup(response.text)
            elements = soup.find_all(hierarchy.keys())

            # Dispose of header and footer
            for garbage in soup.find_all(self.garbage_elements):
                garbage.decompose()

            # Root element
            root = TreeElement('title', 'title not existing', None)

            # Parent for meta tagsNone
            meta_parent = TreeElement('meta_parent', 'meta information', parent=root)

            # Current position, parent, in hierarchy
            current_parent = root

            # Keep track of paragraph tag to be able to switch position with strong tags
            previous_paragraph = None

            for elem in elements:
                elem_text = elem.text.strip()
                elem_tag = elem.name

                # Do not allow tree nodes with empty text
                if not elem_text:
                    continue

                elem_in_hierarchy = hierarchy[elem_tag]
                elem_level = elem_in_hierarchy['level']

                # When found title/root element
                if elem_tag == "title":
                    root = TreeElement(elem_tag, elem_text, None)
                    # It is necessary to update the new meta_parent
                    meta_parent = TreeElement("meta_parent", "meta information", parent=root)
                    current_parent = root
                    continue

                # Save keywords from meta tags.
                if elem_tag == 'meta':
                    meta_content = soup.find('meta', attrs={"name": "keywords"})

                    if meta_content:
                        TreeElement(elem_tag, meta_content['content'], meta_parent)
                    continue

                # Parent for current element
                parent = None

                # Save keywords from meta tags.
                if elem_tag == 'meta':
                    meta_content = soup.find('meta', attrs={"name": "keywords"})

                    if meta_content:
                        TreeElement(elem_tag, meta_content['content'], meta_parent)
                    continue

                # Remove anchors in navbar.
                if elem_tag == 'a' and current_parent == root:
                    continue
                else:
                    # search for appropriate parent
                    search_parent = current_parent

                    while True:
                        # if we find root
                        if search_parent == root:
                            parent = root
                            break

                        if search_parent.tag == elem_tag:
                            parent = search_parent.parent
                            break
                        else:
                            # Whether search parent is in hierarchy
                            search_parent_in_hierarchy = hierarchy[search_parent.tag]

                            if search_parent_in_hierarchy:
                                # If both tags in hierarchy check hierarchy level
                                if elem_in_hierarchy:
                                    if elem_level > search_parent_in_hierarchy['level']:
                                        parent = search_parent
                                        break
                                    elif elem_level == search_parent_in_hierarchy['level']:
                                        # If elements are in same level in hierarchy
                                        parent = search_parent.parent
                                        break
                                else:
                                    # Element where hierarchy is not defined
                                    parent = search_parent
                                    break

                        # Update current parent when searching.
                        search_parent = search_parent.parent

                # Handle switching parent between strong and paragraph tag.
                if elem_tag == 'strong' and previous_paragraph:
                    current_parent = TreeElement(elem_tag, elem_text, previous_paragraph.parent)
                    previous_paragraph.parent = current_parent
                else:
                    # Create element
                    current_parent = TreeElement(elem_tag, elem_text, parent)

                    if elem_tag == 'p':
                        previous_paragraph = current_parent

            # Printing node tree
            for pre, fill, node in RenderTree(root):
                print("%s%s" % (pre, node.tag + " " + node.text))

            exporter = DictExporter()
            tree = exporter.export(root)

            yield {
                'url': response.url,
                'tree': tree,
            }

            # Follow all links from allowed domains.
            for next_page in LinkExtractor().extract_links(response):
                for allowed_path in self.allowed_paths:
                    # Only follow the link if it is in the list
                    # of allowed paths.
                    if allowed_path in next_page.url:
                        yield response.follow(next_page, self.parse)
                        break









"""
import json
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from multi_rake import Rake

rake = Rake(language_code='no')


def sort_coo(coo_matrix):
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)


def extract_topn_from_vector(feature_names, sorted_items, topn=10):

get
the
feature
names and tf - idf
score
of
top
n
items


    # use only topn items from vector
    sorted_items = sorted_items[:topn]

    score_vals = []
    feature_vals = []

    # word index and corresponding tf-idf score
    for idx, score in sorted_items:
        # keep track of feature name and its corresponding score
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])

    # create a tuples of feature,score
    # results = zip(feature_vals,score_vals)
    results = {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]] = score_vals[idx]

    return results


def get_corpus(element, corpus=[]):
    print('hmmm?', element, corpus)
    for child in element['children']:
        print('hmm2', child['tag'])
        if child['tag'] != 'p':
            print('hmm', child['text'])
            corpus.append(child['text'])
            print('appended text, inside if')
            if 'children' in child and len(child['children']) > 0:
                print('trying recursion', child)
                corpus += get_corpus(child, corpus)

    return corpus


with open('scraper/trondheim.json') as f:
    pages = json.load(f)

    corpus = []

    for page in pages:
        print('+++++=====YEEHAW NEW PAGE')
        corpus += get_corpus(page['tree'])
        print('page done')

print(corpus)

vectorizer = TfidfVectorizer(max_df=0.85)

X = vectorizer.fit_transform(corpus)

feature_names = vectorizer.get_feature_names()

for page in pages:
    for element in page['tree']['children']:
        if element['tag'].startswith('h'):
            doc = element['text']
            tfidf_vector = vectorizer.transform([doc])
            sorted_items = sort_coo(tfidf_vector.tocoo())
            keywords = extract_topn_from_vector(feature_names, sorted_items, 10)
            for child in element['children']:
                if child['tag'] != 'p':
                    break
                print(child['text'])
            print("\n===Keywords===")
            for k in keywords:
                print(k, keywords[k])

paragraphs = json.load(f)

corpus = []

for paragraph in paragraphs:
    # Parse the paragraph HTML using BeautifulSoup.
    soup = BeautifulSoup(paragraph['contents'], features='lxml')

    # Retrieve the raw text from the paragraph.
    paragraph_text = soup.get_text()

    # Strip extra spaces around all lines.
    lines = (line.strip() for line in paragraph_text.splitlines())

    # Remove blank lines.
    paragraph_text = '\n'.join(line for line in lines if line)

    if len(paragraph_text) > 200:
        # Append the parsed text to the corpus.
        corpus.append(paragraph_text)

vectorizer = TfidfVectorizer(max_df=0.7)

X = vectorizer.fit_transform(corpus)

feature_names = vectorizer.get_feature_names()

for doc in corpus:
    tfidf_vector = vectorizer.transform([doc])

    sorted_items = sort_coo(tfidf_vector.tocoo())

    # extract only the top n; n here is 10
    keywords = extract_topn_from_vector(feature_names, sorted_items, 10)

    # now print the results
    print("\n=====Doc=====")
    print(doc)
    print("\n===Keywords===")
    for k in keywords:
        print(k, keywords[k])

print("\n===RAKE===")
keywords = rake.apply(doc)
print(keywords[:10])
"""
