from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from nltk.stem.snowball import SnowballStemmer
import string
import re


# Load a Norwegian language model for Spacy.
nb = spacy.load('nb_dep_ud_sm')

stemmer = SnowballStemmer('norwegian')

START_SPECIAL_CHARS = re.compile('^[{}]+'.format(re.escape(string.punctuation)))
END_SPECIAL_CHARS = re.compile('[{}]+$'.format(re.escape(string.punctuation)))


def get_stopwords():
    ''' Retrieves stopwords from the stopwords file. '''
    with open('model/stopwords.txt') as stopwords:
        return [line.strip() for line in stopwords.readlines() if line.strip()]


# Load the stopwords once when the file is loaded.
stop_words = get_stopwords()


def sort_coo(coo_matrix):
    ''' Sort scores given in a sparse matrix of coordinates. '''
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)


def extract_top(feature_names, sorted_items):
    ''' Extracts the top scoring keywords from a sorted list of scores. '''
    return [(feature_names[i], score) for i, score in sorted_items]


def stem_token(token):
    ''' Stem a token using the NLTK SnowballStemmer. '''
    return stemmer.stem(token)


class Tokenizer(object):
    def has_digits(self, token):
        ''' Returns true if the given string contains any digits. '''
        return any(char.isdigit() for char in token)

    def __call__(self, doc):
        ''' Tokenize a given document. '''
        # Tokenize the document.
        tokens = [token.text for token in nb(doc)]

        # Remove punctuation tokens.
        tokens = [token for token in tokens if token not in string.punctuation]

        # Remove tokens which contain any number.
        tokens = [token for token in tokens if not self.has_digits(token)]

        # Remove tokens without text.
        tokens = [token for token in tokens if bool(token.strip())]

        # Remove punctuation from start of tokens.
        tokens = [re.sub(START_SPECIAL_CHARS, '', token) for token in tokens]

        # Remove punctuation from end of tokens.
        tokens = [re.sub(END_SPECIAL_CHARS, '', token) for token in tokens]

        # Remove stopwords from the tokens.
        tokens = [token for token in tokens if token not in stop_words]

        # Stem all tokens.
        tokens = [stem_token(token) for token in tokens]

        # Return the finished list of tokens.
        return tokens


def get_tfidf_model(corpus):
    ''' Create a simple generic model which can be used both for search
    using cosine similarity as well as keyword generation. '''
    # Create a vectorizer which will turn documents into vectors.
    # We use a custom list of stopwords and a custom tokenizer.
    vectorizer = TfidfVectorizer(tokenizer=Tokenizer())
    # Create a simple index on the corpus.
    corpus_matrix = vectorizer.fit_transform(corpus)
    # Retrieve the names of the features. Need this to find which
    # feature a score in the matrix actually belongs to.
    feature_names = vectorizer.get_feature_names()

    return vectorizer, corpus_matrix, feature_names


def get_keywords(vectorizer, feature_names, document):
    ''' Returns the top keywords and their scores for a given document. '''
    tfidf_vector = vectorizer.transform([document])
    sorted_items = sort_coo(tfidf_vector.tocoo())

    return extract_top(feature_names, sorted_items)
