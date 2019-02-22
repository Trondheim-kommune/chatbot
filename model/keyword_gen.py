from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.nb import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
import string


nb = spacy.load('nb_dep_ud_sm')


def get_stopwords():
    with open('/stopwords.txt') as stopwords:
      return [line.strip() for line in stopwords.readlines() if line.strip()]

stop_words = get_stopwords()


def sort_coo(coo_matrix):
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)


def extract_top(feature_names, sorted_items, n=10):
    return [(feature_names[i], score) for i, score in sorted_items[:n]]


class Tokenizer(object):
    def __init__(self):
        self.lemmatize = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)

    def has_digits(self, token):
        return any(char.isdigit() for char in token)

    def __call__(self, doc):
        # Tokenize the document.
        tokens = [self.lemmatize(token.text, token.pos_)[0] for token in nb(doc)]
        # Remove punctuation tokens.
        tokens = [token for token in tokens if token not in string.punctuation]
        # Remove tokens which contain any number.
        tokens = [token for token in tokens if not self.has_digits(token)]
        # Return the finished list of tokens.
        return tokens


def get_tfidf_model(corpus):
    vectorizer = TfidfVectorizer(stop_words=stop_words, tokenizer=Tokenizer())
    corpus_matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names()
    return vectorizer, corpus_matrix, feature_names


def get_keywords(vectorizer, feature_names, document, n=10):
    tfidf_vector = vectorizer.transform([document])
    sorted_items = sort_coo(tfidf_vector.tocoo())
    return extract_top(feature_names, sorted_items, n)
