import json
import os

from bs4 import BeautifulSoup

from chatbot.nlp.keyword import (get_keywords, get_tfidf_model,
                                 stop_words, tokenize)
from chatbot.model.serializer import KeyWord
from chatbot.nlp.query import format_answer


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
            return [word for word in json.load(file_)]

    def _get_num_rare_words(self, doc):
        ''' Return a 'normalised' number of rare words in the document '''
        # Need a list of frequent words to check how many 'rare' words each
        # text document has
        freq_words = self._get_frequent_words()
        unknown_words = 0

        tokens = tokenize(doc)
        for token in tokens:
            if token not in freq_words:
                unknown_words += 1

        # "normalized" number of unknown words based on non-stopword tokens
        return unknown_words / len(tokens)

    def _calculate_global_metrics(self, corpus):
        ''' Calculate metrics based on the global corpus '''
        num_rare_words = [self._get_num_rare_words(doc) for doc in corpus]
        n_stop_words = [sum(d.count(s) for s in stop_words)/len(d)
                        for d in corpus]
        lens = [len(d) for d in corpus]

        # Averages to use in evaluation
        self._avg_length = sum(lens) / len(lens)
        self._max_length = max(lens)
        self._min_length = min(lens)

        self._avg_s_words = sum(n_stop_words) / len(n_stop_words)
        self._max_s_words = max(n_stop_words)
        self._min_s_words = min(n_stop_words)

        self._avg_r_words = sum(num_rare_words) / len(num_rare_words)
        self._max_r_words = max(num_rare_words)
        self._min_r_words = min(num_rare_words)

    def _create_path(self, path_length, uri):
        ''' Build file path to the path_length-th element in uri '''
        path = self._PATH
        for i in range(path_length):
            new_path = path + '/' + uri[i]
            if not os.path.isdir(new_path):
                os.mkdir(new_path)
            path += '/{}'.format(uri[i])

        return path

    def _calc_meter_values(self, min_, max_, avg_, x):
        low = (avg_-min_)/2
        high = (avg_+max_)/2

        return (max_, min_, x, high, low, avg_)

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
                # We read from the template file and save it as a bs4
                # object. This object will be extended to include the
                # contents of the page. Once the main while-loop is done, we
                # write the soup-object to the file html_file
                with open('text_evaluator/statics/template.html', 'r') as inf:
                    txt = inf.read()
                    soup = BeautifulSoup(txt, 'lxml')

                # Since the html files will be placed at unknown depths,
                # providng a relative path back to the template stylesheet is
                # not feasible. Instead, we read the contents of the style
                # document and insert it in a <style>-tag in the html document.
                with open('text_evaluator/statics/style.css', 'r') as style_f:
                    style = style_f.read()
                soup.style.insert(1, style)

                # Tread child_data as a queue for iterative traversal
                child_data = list(data['tree'].get('children', []))

                # Remove the meta-keyword element and keep going
                if len(child_data) > 0 and child_data[0]['tag'] == 'meta':
                    child_data.pop(0)

                while child_data:
                    node = child_data.pop(0)

                    if 'children' in node:
                        child_data = node['children'] + child_data

                        if 'text' in node:
                            title = node['text']

                    else:
                        # Serialize and build .html file in var:path
                        text = node['text']
                        length = len(text)
                        links = node['links']
                        # Get proper link-formatting
                        text = format_answer([text, links], 'html')

                        keywords = [KeyWord(*kw)
                                    for kw in get_keywords(self._vectorizer,
                                                           self._feature_names,
                                                           "{} {}"
                                                           .format(title,
                                                                   text))]

                        # Evaluation metrix
                        num_rare_words = self._get_num_rare_words(text)
                        num_stop_words = sum([text.count(s)
                                              for s in stop_words]) / len(text)
                        max_kw_conf = max([kw.get_keyword()['confidence']
                                           for kw in keywords])

                        page_container = soup.find(id='page-container')
                        text_content = '''
                        <div class='content-container'>
                            <div class='row'>
                                <div class='text-area'>
                                    <h3 class='title'>{}</h3>
                                    <p>{}</p>
                                </div>
                        '''.format(title, text.replace('\n', '<br>'))
                        keyword_content = '''
                        <div class='keywords'>
                            <h3>Keywords</h3>
                            <ul>
                        '''
                        for kw in keywords:
                            keyword_content += '''
                            <li><p>{}</p>
                                <progress value='{}' max='{}'></progress>
                            </li>
                            '''.format(kw.get_keyword()['keyword'],
                                       kw.get_keyword()['confidence'],
                                       max_kw_conf)
                        # Close ul, keywords and row divs
                        keyword_content += '</ul></div></div>'
                        metrics = '''
                        <div class='row'>
                            <div class='metrics'>
                                <h3> Evaluation </h3>
                            </div class='metrics'>
                        </div>
                        <div class='row'>
                            <div class='metrics'>
                                <div class='column'>
                                    <p> Length of text (50% optimal)</p>
                                    <meter max="{}", min="{}",
                                           value="{}", high="{}",
                                           low="{}", optimum="{}"></meter>
                                </div>
                                <div class='column'>
                                    <p> Number of stop words (50% optimal)</p>
                                    <meter max="{}", min="{}",
                                           value="{}", high="{}",
                                           low="{}", optimum="{}"></meter>
                                </div>
                                <div class='column'>
                                    <p> Number of rare words (low optimal)</p>
                                    <meter max="{}", min="{}",
                                           value="{}", high="{}",
                                           low="{}", optimum="{}"></meter>
                                </div>
                            </div>
                        </div>
                        '''.format(*self._calc_meter_values(self._min_length,
                                                            self._max_length,
                                                            self._avg_length,
                                                            length),
                                   *self._calc_meter_values(self._min_s_words,
                                                            self._max_s_words,
                                                            self._avg_s_words,
                                                            num_stop_words),
                                   *self._calc_meter_values(self._min_r_words,
                                                            self._max_r_words,
                                                            self._avg_r_words,
                                                            num_rare_words)
                                   )
                        # Close content-container div
                        metrics += '</div>'
                        content = text_content + keyword_content + metrics
                        content = BeautifulSoup(content, 'lxml')

                        # Insert the whole content-container div at the end of
                        # page-container div
                        page_container.append(content.div)

                # Write the whole new soup-object to the html_file now that we
                # have looped over all the contents and made the html-structure
                # for them
                with open(html_file, 'w') as outf:
                    outf.write(str(soup))


eval_ = Evaluator('chatbot/scraper/scraped.json')
eval_.serialize_data()
