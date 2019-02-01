import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.http import HtmlResponse
from bs4 import BeautifulSoup
from anytree import RenderTree, NodeMixin
from anytree.exporter import JsonExporter

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


# TODO: Create support for anchor-tag <a>
# TODO: Create tablesupport - remember to check for <thead>
# TODO: Fix unicode character
# TODO: fix support for newlines etc.
# TODO: title
# TODO: create support for multiple meta tags
# TODO: <strong><p></p></strong> needs to be child of header

class TrondheimSpider(scrapy.Spider):
    # Name of the spider. This is the name to use from the Scrapy CLI.
    name = 'trondheim'

    # The links to start the crawling process on.
    start_urls = [
        # 'https://www.trondheim.kommune.no/tema/skole/Opplaring/spesialundervisning/handbok-i-spesialpedagogikk/',
        'https://trondheim.kommune.no/tema/kultur-og-fritid/lokaler/husebybadet'
    ]

    allowed_paths = [
        # 'https://www.trondheim.kommune.no/tema/skole/Opplaring/spesialundervisning/handbok-i-spesialpedagogikk/',
        'https://trondheim.kommune.no/tema/kultur-og-fritid/lokaler/husebybadet'
    ]

    # Parses the latest response.
    def parse(self, response):
        # Constants
        TITLE_TAG_ = "title"
        HEADER_TAGS_ = ["h1", "h2", "h3", "h4", "h5", "h6"]
        META_TAG_ = "meta"
        STRONG_TAG_ = "strong"
        ANCHOR_TAG_ = "a"
        PARAGRAPH_TAG_ = "p"

        # Adding all tags
        # all_tags = [TITLE_TAG_, META_TAG_, STRONG_TAG_, ANCHOR_TAG_, PARAGRAPH_TAG_]
        all_tags = [TITLE_TAG_, META_TAG_, ANCHOR_TAG_, PARAGRAPH_TAG_]
        for h in HEADER_TAGS_:
            all_tags.append(h)

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

            tag_strings = ""
            for tag in all_tags:
                tag_strings += ", " + tag
            tag_strings = tag_strings[2:]
            print("============= TAGS INCLUDED ===============", tag_strings)
            elements = response.css(tag_strings)

            # Root element
            root = TreeElement("title", "title not existing", None)

            # Parent for meta tags
            meta_parent = TreeElement("meta_parent", "meta information", parent=root)

            # Current position, parent, in hierachy
            current_parent = root

            for elem in elements:
                soup = BeautifulSoup(elem.extract(), 'html.parser')
                elem_text = soup.text
                elem_tag = list(soup.children)[0].name

                # When found title
                if elem_tag == TITLE_TAG_:
                    root = TreeElement(elem_tag, elem_text, None)
                    # It is necessary to update the new meta_parent
                    meta_parent = TreeElement("meta_parent", "meta information", parent=root)
                    current_parent = root
                    continue

                # Find parent for element
                parent = None

                # p is always a child of current posistion
                if elem_tag == PARAGRAPH_TAG_:
                    # All paragraphs must be child of parent
                    TreeElement(elem_tag, elem_text, current_parent)
                    continue
                elif elem_tag == META_TAG_:
                    meta_content = soup.find('meta', attrs={"name": "keywords"})

                    if meta_content:
                        TreeElement(elem_tag, meta_content['content'], meta_parent)
                    continue
                else:
                    # If element has same level in hierachy
                    if elem_tag == current_parent.tag:
                        parent = current_parent.parent
                        # If the tag is a header we can go for header hierarchy
                    elif elem_tag in HEADER_TAGS_ and current_parent.tag in HEADER_TAGS_ \
                            and int((elem_tag[1])) > (int(current_parent.tag[1])):
                        # If we have found child of current parent
                        parent = current_parent
                    else:
                        # search for appropriate parent
                        temp_parent = current_parent
                        while True:
                            # if we find root
                            if temp_parent == root:
                                parent = root
                                break

                            # If we are checking two headers
                            if temp_parent.tag in HEADER_TAGS_ and elem_tag in HEADER_TAGS_:
                                # if we have found the same level in hierarchy
                                if (int(temp_parent.tag[1])) == int(elem_tag[1]):
                                    parent = temp_parent.parent
                                    break
                                    # Set parent according to header hierarchy
                                elif int(temp_parent.tag[1]) < int(elem_tag[1]):
                                    parent = temp_parent
                                    break
                            # if we have an anchor tag.
                            elif elem_tag == ANCHOR_TAG_:
                                parent = temp_parent
                                break
                            elif elem_tag == STRONG_TAG_:
                                parent = temp_parent
                                break

                            # Update current parent when searching
                            temp_parent = temp_parent.parent

                    # Remove anchors in navbar. Useless info to map.
                    if elem_tag != ANCHOR_TAG_ or parent != root:
                        # Create element
                        current_parent = TreeElement(elem_tag, elem_text, parent)

            # Printing nodetree
            for pre, fill, node in RenderTree(root):
                print("%s%s" % (pre, node.tag + " " + node.text))

            exporter = JsonExporter(indent=2, sort_keys=True)
            # print(exporter.export(root))

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
