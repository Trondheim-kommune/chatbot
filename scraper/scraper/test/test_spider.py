from scrapy.http import Request, HtmlResponse
import os
import json
from scraper.scraper.spiders import trondheim_spider as ts

HB = 'https://www.trondheim.kommune.no/tema/kultur-og-fritid/lokaler/husebybadet/'


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
    spider = ts.TrondheimSpider()

    # The testing html uses strong tags as headers and concatenation p tags
    spider.strong_headers = "true"
    spider.concatenation_p = "true"

    # Crawl the html file and returns the tree structure
    tree = spider.parse(fake_response_from_file("huseby.html"))

    # Handle absolute path
    responses_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(responses_dir, 'test_huseby_html.json')

    # Retrieve snapshot
    with open(file_path, "r") as data:
        html_tree_snapshot = data.readlines()[1]

    # Sort and compare snapshots
    t = next(tree)
    assert sorted(
        json.loads(str(html_tree_snapshot)[:-1]).items()
    ) == sorted(t.items())
