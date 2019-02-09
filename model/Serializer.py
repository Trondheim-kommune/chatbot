import json


class KeyWord:
    """ Keyword to fill keyword-list in model schema contents-list """

    __word = None
    __confidence = None

    def __init__(self, word, confidence):
        self.__word = word
        self.__confidence = confidence

    def get_keyword(self):
        return {"keyword": self.__word, "confidence": self.__confidence}


class Content:
    """ Content to fill contents-list in model schema """

    __title = ""
    __keywords = []
    __texts = []

    def __init__(self, title, texts, keywords=[]):
        self.__title = title
        self.__texts = texts
        if keywords:
            for keyword in keywords:
                if not isinstance(keyword, KeyWord):
                    raise TypeError("Must be KeyWord type")
            self.__keywords = keywords

    def get_content(self):
        return {
            "title": self.__title,
            "keywords": self.__keywords,
            "texts": self.__texts,
        }

    def __repr__(self):
        return str(self.get_content())


class Serializer:
    """ Translate JSON output from scraper to model schema """

    __file_name = None
    __MODEL_SCHEMA = {
        "title": "",
        "description": "",
        "url": "",
        "last_modified": "",
        "header_meta_keywords": [],
        "keywords": [],
        "contents": [],
        "indexed": "",
    }
    __models = []
    __data = []

    def __init__(self, file_name):
        self.file_name = file_name
        self.load_data()

    def load_data(self):
        """ Load all JSON data from a file and sets self.__data. Mostly used
        for testing-purposes: real data from scraper is a list of several JSON
        objects """
        with open(self.file_name, "r") as f:
            data = json.load(f)
            for item in data:
                self.__data.append(item)

    def get_data(self):
        return self.__data

    def get_models(self):
        return self.__models

    def serialize_data(self):
        """ Serialize a page object from the web scraper to the data model
        schema """

        # Iterate over all pages in the JSON data from scraper
        for data in self.__data:
            # TODO: add more metadata
            model = self.__MODEL_SCHEMA
            model["url"] = data["url"]

            # Actual data in the tree
            child_data = data["tree"]["children"] 

            # Extract meta keywords if they exist
            if child_data[0]["tag"] == "meta":
                # Tokenizing the keywords on comma
                model["header_meta_keywords"] = child_data[0]["text"].split(",")
                # Remove meta element from the list before iterating over the rest
                # of the list
                child_data.pop(0)

            def iterator(idx, data, model, title):
                """ Recursively traverse the children and create new Contents from
                paragraphs """
                for child in data:
                    if "children" in child.keys():
                        # currently just concatenates titles.. need to do something
                        # more sophisticated here in the future.. with regards to
                        # keyword generation
                        iterator(idx + 1, child["children"], model,
                                 title=title + " " + child["text"])
                    else:
                        # Hit a leaf node in recursion tree. We extract the text
                        # here and continue
                        content = Content(title, [child["text"]])
                        model["contents"].append(content)

                return model

            model = iterator(0, child_data, model, "")
            self.__models.append(model)
