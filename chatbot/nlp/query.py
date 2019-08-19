import string
import random
import os
import pymongo

from sklearn.metrics.pairwise import cosine_similarity

from nltk.corpus import wordnet as wn

from chatbot.model.model_factory import ModelFactory
from chatbot.nlp.keyword import get_tfidf_model, get_stopwords, lemmatize, nb
from chatbot.nlp.synset import SynsetWrapper
from chatbot.util.config_util import Config


NOT_FOUND = Config.get_value(['query_system', 'not_found'])
MULTIPLE_ANSWERS = Config.get_value(['query_system', 'multiple_answers'])
CHAR_LIMIT = Config.get_value(['query_system', 'character_limit'])
MAX_ANSWERS = Config.get_value(['query_system', 'max_answers'])
URL_FROM_TEXT = Config.get_value(['query_system', 'url_from_text'])


factory = ModelFactory.get_instance()
factory.set_db()


def _handle_not_found(query_text):
    '''
    Inserts this specific query text into the unknown queries collection as
    well as returning a fallback string.
    '''
    try:
        unknown_col = Config.get_mongo_collection("unknown")
        factory.get_database().get_collection(unknown_col).insert_one(
            {"query_text": query_text})
    except pymongo.errors.DuplicateKeyError:
        # If we already have this specific query in the unknown_queries
        # collection we don't need to add it again.
        pass

    return NOT_FOUND


def _get_corpus_text(doc):
    ''' Converts a document from the model into a string which will be used in
    a corpus.  All possible answers are used to generate the corpus, if
    multiple answers exist.'''
    content = ' '.join(doc['content']['texts'])
    return doc['content']['title'] + ' ' + content


def _get_answer_text(doc):
    ''' Converts a document from the model into a readable string. '''
    content = random.choice(doc['content']['texts'])
    content = content + '\n' + URL_FROM_TEXT + doc['url']

    return doc['content']['title'] + ':\n' + content


def expand_query(query):
    ''' Attempts to expand the given query by using synonyms from WordNet. As
    a consequnece of this process, the query is also tokenized and lemmatized.
    '''

    tokens = [
      # Store tuples of lemmatized tokens and their corresponding POS tags.
      (lemmatize(token.text, token.pos_)[0], token.pos_) for token in nb(query)
      # Filter away punctuation.
      if token.text not in string.punctuation
    ]

    # Filter away stopwords as we do not want to expand them.
    tokens = [token for token in tokens if token not in get_stopwords()]

    # Store synonyms in a set, so duplicates are not added multiple times.
    synonyms = set()

    # The tokens in the expanded query.
    result = []

    for token in tokens:
        # Convert POS tags from Spacy to WordNet.
        pos = getattr(wn, token[1], None)

        # Find all synsets for the word, using the Norwegian language.
        synsets = wn.synsets(token[0], lang='nob', pos=pos)

        # Get a custom synset wrapper.
        custom_synsets = SynsetWrapper.get_instance()

        # Get the synset for this token.
        custom_synset = custom_synsets.get_synset(token[0])

        if custom_synset:
            # Remove the token itself to avoid duplication.
            custom_synset.remove(token[0])
            synonyms.update(custom_synset)

        if synsets:
            for synset in synsets:
                # Find all lemmas in the synset.
                for name in synset.lemma_names(lang='nob'):
                    # Some lemmas contain underscores, which we remove.
                    synonyms.add(name.replace('_', ' '))

            # If we found synonyms, we only add the synonyms. This is because
            # the original word is already included in the synset, so this
            # avoids adding it to the result list twice.
            continue

        # Add the original token to the full query.
        result.append(token[0])

    # Add custom synset to the query
    result += synonyms

    return ' '.join(result)


def _perform_search(query_text):
    ''' Takes a query string and finds the best matching document in the
    database. '''

    # Perform simple query expansion on the original query.
    query = expand_query(query_text)

    if str(os.getenv('LOG')) == 'TRUE':
        print('Post expansion: ', query)

    # Retrieve a set of documents using MongoDB. We then attempt to filter
    # these further.
    docs = factory.get_document(query)

    # Prevent generating an empty corpus if no documents were found.
    if not docs:
        return _handle_not_found(query_text)

    # Create a corpus on the results from the MongoDB query.
    corpus = [_get_corpus_text(doc) for doc in docs]

    # Create a TF-IDF model on the corpus.
    vectorizer, corpus_matrix, feature_names = get_tfidf_model(corpus)

    try:
        # Compare the search query with all documents in our new model using
        # cosine similarity.
        scores = cosine_similarity(vectorizer.transform([query]),
                                   corpus_matrix)[0].tolist()

        sorted_scores = sorted(scores, reverse=True)

        # This could be calculated using the mean of all scores and the
        # standard deviation.
        if sorted_scores[0] < 0.1:
            return _handle_not_found(query_text)

        # Allow returning multiple answers if they rank very similarly.
        answers = []

        for score in sorted_scores:
            # Tolerance for similarity between scores.
            if sorted_scores[0] - score > 0.1:
                break

            # Add this result to the list of answers.
            answers.append(_get_answer_text(docs[scores.index(score)]))

        if len(answers) == 1:
            # Return the answer straight away if there is only 1 result/
            return answers[0]

        # Append answers until we reach the CHAR_LIMIT
        i, n_chars = 0, 0
        while n_chars < CHAR_LIMIT and i < len(answers):
            n_chars += len(answers[i])
            i += 1

        # Join the results with a separator. Still setting a max number of
        # answers
        return '\n\n---\n\n'.join([MULTIPLE_ANSWERS] + answers[0:min(max(i, 1),
                                  MAX_ANSWERS)])
    except KeyError:
        raise Exception('Document does not have content and texts.')
    except ValueError:
        return _handle_not_found(query_text)


class QueryHandler:
    def get_response(self, query):
        return _perform_search(query)
