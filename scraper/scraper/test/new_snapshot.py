from scraper.scraper.spiders import trondheim_spider as ts

spider = ts.TrondheimSpider()
tree  = spider.parse(fake_response_from_file("huseby.html"))
print(tree)
