import json


class KeyWord:
    """ Keyword to fill keyword-list in model schema contents-list """

    __word = None
    __confidence = None

    def __init__(self, word, confidence):
        self.__word = word
        self.__confidence = confidence

    def get_keyword(self):
        return { "keyword": self.__word, "confidence": self.__confidence }


class Content:
    """ Content to fill contents-list in model schema """

    __title = None
    __keywords = []
    __texts = []

    def __init__(self, title, texts, keywords=None):
        self.__title = title
        self.__texts = texts
        if keywords: 
            for keyword in keywords:
                if not isinstance(keyword, KeyWord): raise TypeError("Must be KeyWord type")
            self.__keywords = keywords


    def get_content(self):
        return {
                    "title": self.__title,
                    "keywords": self.__keywords,
                    "texts": self.__texts
                }

    def __repr__(self):
        return str(self.get_content())


class Serializer:
    """ Translate JSON output from scraper to model schema """

    __file_name = None
    __data = None
    __model = {
                "title": None,
                "description": None,
                "url": None,
                "last_modified": None,
                "header_meta_keywords": [],
                "keywords": [],
                "contents": [],
                "indexed": None
              }

    def __init__(self, file_name):
        self.file_name = file_name
        self.load_data()

    def load_data(self):
        with open(self.file_name, 'r') as f:
            self.__data = json.load(f)
    
    def get_data(self):
        return self.__data

    def get_model(self):
        return self.__model

    def serialize_data(self):
        # TODO: add more metadata
        self.__model['url'] = self.__data['url']

        def iterator(idx, data, title):
            """ Recursively traverse the children and create new Contents from
            paragraphs """
            for child in data:
                if 'children' in child.keys():
                        # currently just concatenates titles.. need to do something
                        # more sophisticated here in the future.. with regards to
                        # keyword generation
                        iterator(idx+1, child['children'], title=title+" "+child['text'])
                else:
                    content = Content(title, child['text'])
                    self.__model['contents'].append(content)

        iterator(0, self.__data['tree']['children'], "")


if __name__ == '__main__':
    ser = Serializer('mock_data/huseby.json')
    ser.serialize_data()
    print(ser.get_model())
