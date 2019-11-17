import json
import copy
import os

from chatbot.nlp.keyword import get_keywords, get_tfidf_model
from chatbot.util.config_util import Config


class Evaluator():
    _data = []

    _MODEL_SCHEMA = {
        "id": "",
        "title": "",
        "url": "",
        "content": {}
    }

    _PATH = os.getcwd() + '/evaluation'

    def __init__(self, file_name=False):
        self.file_name = file_name
        self._load_data()

        vectorizer, transformed_corpus, feature_names = self._get_tfidf_model()

        self._vectorizer = vectorizer
        self._transformed_corpus = transformed_corpus
        self._feature_names = feature_names

    def _load_data(self):
        if self.file_name:
            with open(self.file_name, "r") as f:
                self._data.extend(json.load(f))

    def _get_tfidf_model(self):
        corpus = []
        for data in self._data:
            queue = list(data['tree'].get('children', []))
            while queue:
                node = queue.pop(0)
                if 'text' in node:
                    corpus.append(node['text'])
                if 'children' in node:
                    queue += node['children']

        return get_tfidf_model(corpus)


    def serialize_data(self):
        for data in self._data:
            model = copy.deepcopy(self._MODEL_SCHEMA)
            model['url'] = data['url']

            # * [4:] to remove https://trondheim.kommune.no/x/
            # * strip to remove trailing /
            uri = model['url'].strip('/').split('/')[4:]
            path = self._PATH

            if 'children' not in data['tree']:
                for i in range(len(uri)):
                    new_path = path + '/' + uri[i]
                    if not os.path.isdir(new_path):
                        os.mkdir(new_path)
                    path += '/{}'.format(uri[i])
            else:
                for i in range(len(uri[:-1])):
                    new_path = path + '/' + uri[i] + '.html'
                    if not os.path.exists(new_path):
                        os.mknod(new_path)
                    path += '/{}'.format(uri[i])

eval_ = Evaluator('chatbot/scraper/scraped.json')
eval_.serialize_data()
