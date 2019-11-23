import json
import os

from chatbot.nlp.keyword import (get_keywords, get_tfidf_model,
                                 stop_words, tokenize)


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

        corpus = self._get_corpus()
        vect, trans_corp, feat_names = self._get_tfidf_model(corpus)

        self._vectorizer = vect
        self._transformed_corpus = trans_corp
        self._feature_names = feat_names

        self._calculate_global_metrics(corpus)

    def _load_data(self):
        if self.file_name:
            with open(self.file_name, "r") as f:
                self._data.extend(json.load(f))

    def _get_corpus(self):
        ''' Return a corpus (list of strings) from self._data '''
        corpus = []
        for data in self._data:
            queue = list(data['tree'].get('children', []))
            while queue:
                node = queue.pop(0)
                if 'text' in node:
                    corpus.append(node['text'])
                if 'children' in node:
                    queue += node['children']
        return corpus

    def _get_tfidf_model(self, corpus):
        ''' Return tf-idf model for given corpus. Uses
        chatbot.keyword.get_tfidf_model() '''
        return get_tfidf_model(corpus)

    def _get_frequent_words(self):
        ''' Return a list of words that are known and used frequently in
        Norwegian '''
        with open('chatbot/nlp/statics/no_50k.json') as file_:
            return [word for word, _ in json.load(file_)]

    def _calculate_global_metrics(self, corpus):
        ''' Calculate metrics based on the global corpus '''

        # Need a list of frequent words to check how many 'rare' words each
        # text document has
        freq_words = self._get_frequent_words()

        num_rare_words = []
        for doc in corpus:
            tokens = tokenize(doc)
            unknown_words = 0
            for token in tokens:
                if token not in freq_words:
                    unknown_words += 1

            # "normalized" number of unknown words based on non-stopword tokens
            num_rare_words.append(unknown_words / len(tokens))

        n_stop_words = [sum([d.count(s) for s in stop_words] for d in corpus)]
        lens = [len(d) for d in corpus]

        # Averages to use in evaluation
        self._avg_length = sum(lens) / len(lens)
        self._avg_n_stop_words = sum(n_stop_words) / len(n_stop_words)
        self._avg_rare_words = sum(num_rare_words) / len(num_rare_words)

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
        title = None
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

                # Tread child_data as a queue for iterative traversal
                child_data = list(data['tree'].get('children', []))

                # Remove the meta-keyword element and keep going
                if len(child_data) > 0 and child_data[0]['tag'] == 'meta':
                    child_data.pop(0)

                title = child_data['text']
                while child_data:
                    node = child_data.pop(0)
                    if 'text' in node:
                        title = '{} - {}'.format(title, node['text']) \
                                if title else node['text']

                    if 'children' in node:
                        child_data += node['children']
                    else:
                        # Serialize and build .html file in var:path
                        continue


eval_ = Evaluator('chatbot/scraper/scraped.json')
eval_.serialize_data()
