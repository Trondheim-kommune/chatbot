import json
import copy
import os

from chatbot.nlp.keyword import get_keywords, get_tfidf_model
from chatbot.util.config_util import Config


class Evaluator():
    _data = []

    _PATH = os.getcwd() + '/evaluation'
    if not os.path.exists(_PATH):
        os.mkdir(_PATH)
    else:
        raise FileExistsError("The directory evaluation/ already exists!")

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


    def _create_path(self, path_length, uri):
        ''' Build file path to the path_length-th element in uri '''
        path = self._PATH
        for i in range(path_length):
            new_path = path + '/' + uri[i]
            if not os.path.isdir(new_path):
                os.mkdir(new_path)
            path += '/{}'.format(uri[i])

        return path

    def serialize_data(self):
        for data in self._data:

            # We need to split the URL into it's respective components. 
            # TODO: The removal of the specific host part should be done throug
            # the config-file with a regex. It is a bit too specific for trd...
            # * [4:] to remove https://trondheim.kommune.no/x/
            # * strip to remove trailing /
            uri = data['url'].strip('/').split('/')[4:]
            path = self._PATH

            if 'children' not in data['tree']:
                # If the uri is not complete (leads to a content-filled page),
                # we only want to create a dir-path.
                path_len = len(uri)
                path = self._create_path(path_len, uri)
                continue
            else:
                # Whenever uri leads to a leaf-node, we want to end up with an
                # html-file at the end, not a directory. We therefore exclude
                # the last part of the uri when building the path, since this
                # is the name of the html file
                path_len = len(uri[:-1])
                path = self._create_path(path_len, uri)

                html_file = path + '/' + uri[-1] + '.html'
                if not os.path.exists(html_file):
                    # We don't actually want to make a new file here, instead
                    # we must copy a pre-defined html-template that we can then
                     # add DOM-elements to, for each content
                    os.mknod(html_file)
    
                # Serialize and build .html file in var:path

eval_ = Evaluator('chatbot/scraper/scraped.json')
eval_.serialize_data()
