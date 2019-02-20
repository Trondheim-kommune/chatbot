import json
import copy
import urllib.request


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

    def toJSON(self):
        return json.dumps(self.get_content())


class Serializer:
    """ Translate JSON output from scraper to model schema """

    __file_name = None
    __url = None
    __MODEL_SCHEMA = {
        "id": "",
        "title": "",
        "description": "",
        "url": "",
        "last_modified": "",
        "header_meta_keywords": [],
        "keywords": [],
        "content": {},
        "manually_changed": False,
    }
    __models = []
    __data = []

    def __init__(self, file_name=None, url=None):
        self.file_name = file_name
        self.url = url
        self.load_data()

    def load_data(self):
        """ Load all JSON data from a file and sets self.__data. Mostly used
        for testing-purposes: real data from scraper is a list of several JSON
        objects """

        if self.file_name:
            with open(self.file_name, "r") as f:
                data = json.load(f)
                for item in data:
                    self.__data.append(item)
        elif self.url:
            with urllib.request.urlopen(self.url) as url:
                data = json.loads(url.read().decode())
                for item in data:
                    self.__data.append(item)

    def get_data(self):
        return self.__data

    def get_models(self):
        return self.__models

    def serialize_data(self):
        """ Serialize a page object from the web scraper to the data model
        schema """

        accepted_tags = ["p", "a", "li"]

        # Iterate over all pages in the JSON data from scraper
        for data in self.__data:
            # TODO: add more metadata
            model = copy.deepcopy(self.__MODEL_SCHEMA)
            model["url"] = data["url"]

            # Actual data in the tree
            if "children" in data["tree"]:
                child_data = data["tree"]["children"]
            else:
                continue

            # Extract meta keywords if they exist
            if child_data[0]["tag"] == "meta":
                # Tokenizing the keywords on comma
                model["header_meta_keywords"] = child_data[0]["text"].split(
                    ",")
                # Remove meta element from the list before iterating
                # over the rest of the list
                child_data.pop(0)

            def iterator(idx, data, model_template, models, title):
                """ Recursively traverse the children and create new Contents
                from paragraphs """
                for child in data:
                    if "children" in child:
                        # currently just concatenates titles.. need to do
                        # something more sophisticated here in the future..
                        # with regards to keyword generation
                        iterator(idx + 1, child["children"], model_template, models,
                                 title=title + " " + child["text"])
                    elif child["tag"] in accepted_tags:
                        # Hit a leaf node in recursion tree. We extract the
                        # text here and continue

                        content = Content(title, [child["text"]])
                        new_model = copy.deepcopy(model_template)
                        new_model["id"] = child["id"]
                        new_model["content"] = content.get_content()
                        models.append(new_model)

                return models

            models = iterator(0, child_data, model, [], "")
            self.__models += models
