from scrapy.http import Request, HtmlResponse
import os
import json
from chatbot.scraper.spiders import info_gathering_spider as igs

HOST = 'https://www.trondheim.kommune.no/'
URI = 'tema/kultur-og-fritid/lokaler/husebybadet/'
HB = HOST + URI


def fake_response_from_file(file_name, url=HB):
    """
    Create a Scrapy fake HTTP response from a HTML file
    @param file_name: The relative filename from the responses directory,
                      but absolute paths are also accepted.
    @param url: The URL of the response.
    returns: A scrapy HTTP response which can be used for unittesting.
    """

    request = Request(url=url)
    responses_dir = os.path.dirname(os.path.realpath(__file__))
    file_content = open(os.path.join(responses_dir, file_name), 'r').read()

    return HtmlResponse(url=url, body=file_content, request=request,
                        encoding='utf-8')


def test_scraper_snapshot():
    """
    Testing if the scraper works as intended.
    Compares sorted Json generated from HTML mockup file and snapshot mockup.
    """
    # Instansiate the spider
    spider = igs.InfoGatheringSpider()

    # The testing html uses strong tags as headers and concatenation p tags

    # Crawl the html file and returns the tree structure
    tree = spider.parse(fake_response_from_file("test.html"))
    tree_obj = next(tree)

    # Handle absolute path
    responses_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(responses_dir, 'test_html.json')

    # Retrieve snapshot
    with open(file_path, "r") as data:
        html_tree_snapshot = data.readlines()[0]

    correct = json.loads(str(html_tree_snapshot))
    result = tree_obj

    assert correct["url"] == result["url"]

    assert correct["tree"]["id"] == result["tree"]["id"]

    # Get a very specific content that contains links
    a = correct["tree"]["children"][1]["children"][3]["children"][0]["links"]
    b = result["tree"]["children"][1]["children"][3]["children"][0]["links"]
    assert a == b

    # Get a very specific content that contains a text
    a = correct["tree"]["children"][1]["children"][0]["text"]
    b = result["tree"]["children"][1]["children"][0]["text"]
    assert a == b
