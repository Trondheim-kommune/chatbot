import collections
import string
import re

import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.nb import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES

from sklearn.feature_extraction.text import TfidfVectorizer

import nltk


# Load a Norwegian language model for Spacy.
nb = spacy.load('nb_dep_ud_sm')

lemmatize = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)

nltk.download('wordnet')
nltk.download('omw')

START_SPEC_CHARS = re.compile('^[{}]+'.format(re.escape(string.punctuation)))
END_SPEC_CHARS = re.compile('[{}]+$'.format(re.escape(string.punctuation)))


def get_stopwords():
    ''' Retrieves stopwords from the stopwords file. '''
    with open('chatbot/nlp/statics/stopwords.txt') as stopwords:
        return [line.strip() for line in stopwords.readlines() if line.strip()]


# Load the stopwords once when the file is loaded.
stop_words = get_stopwords()


def _sort_coo(coo_matrix):
    ''' Sort scores given in a sparse matrix of coordinates. '''
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)


def _extract_top(feature_names, sorted_items, n=10):
    ''' Extracts the top scoring keywords from a sorted list of scores. '''
    return [(feature_names[i], score) for i, score in sorted_items[:n]]


def _has_digits(token):
    ''' Returns true if the given string contains any digits. '''
    return any(char.isdigit() for char in token)


def tokenize(doc):
    ''' Tokenize a given document. '''
    # Tokenize the document.
    tokens = [lemmatize(token.text, token.pos_)[0] for token in nb(doc)]

    # Remove punctuation tokens.
    tokens = [token for token in tokens if token not in string.punctuation]

    # Remove tokens which contain any number.
    tokens = [token for token in tokens if not _has_digits(token)]

    # Remove tokens without text.
    tokens = [token for token in tokens if bool(token.strip())]

    # Remove punctuation from start of tokens.
    tokens = [re.sub(START_SPEC_CHARS, '', token) for token in tokens]

    # Remove punctuation from end of tokens.
    tokens = [re.sub(END_SPEC_CHARS, '', token) for token in tokens]

    # Remove stopwords from the tokens.
    tokens = [token for token in tokens if token not in stop_words]

    # Return the finished list of tokens.
    return tokens


def lemmatize_content_keywords(content):
    ''' Go through a content in the format given to the API, and lemmatize
    all keywords again in case something changed. '''
    # Merge all texts and titles, then tokenize and POS tag them.
    tokens = nb(' '.join(([content['title']] + content['texts'])))

    # Counter for number of times each POS tag occurs for tokens.
    votes = collections.defaultdict(lambda: collections.Counter())

    for token in tokens:
        # For each word, we count how many times each POS tag occurs.
        votes[token.text][token.pos_] += 1

    for entry in content['keywords']:
        # Verify that the keyword is not empty.
        if not entry['keyword']:
            continue

        # Find the most likely POS tag for the keyword.
        # If the keyword is not in the document, use an unigram tagger.
        pos = next(iter(votes[entry['keyword']].most_common()),
                   nb(entry['keyword'])[0].pos_)

        # Store the lemmatized keyword.
        entry['keyword'] = lemmatize(entry['keyword'], pos)[0]


def get_tfidf_model(corpus):
    ''' Create a simple generic model which can be used both for search
    using cosine similarity as well as keyword generation. '''
    # Create a vectorizer which will turn documents into vectors.
    # We use a custom list of stopwords and a custom tokenizer.
    vectorizer = TfidfVectorizer(tokenizer=tokenize, sublinear_tf=True)

    # Create a simple index on the corpus.
    corpus_matrix = vectorizer.fit_transform(corpus)

    # Retrieve the names of the features. Need this to find which
    # feature a score in the matrix actually belongs to.
    feature_names = vectorizer.get_feature_names()

    return vectorizer, corpus_matrix, feature_names


def get_keywords(vectorizer, feature_names, document):
    ''' Returns the top keywords and their scores for a given document. '''
    tfidf_vector = vectorizer.transform([document])
    sorted_items = _sort_coo(tfidf_vector.tocoo())

    return _extract_top(feature_names,
                        sorted_items,
                        len(sorted_items))
