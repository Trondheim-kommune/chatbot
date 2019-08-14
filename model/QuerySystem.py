from model.ModelFactory import ModelFactory
import model.db_util as util
from sklearn.metrics.pairwise import cosine_similarity
from model.keyword_gen import get_tfidf_model
from model.query_expansion import expand_query
from util.config_util import Config
import pymongo
import random

NOT_FOUND = Config.get_value(['query_system', 'not_found'])
MULTIPLE_ANSWERS = Config.get_value(['query_system', 'multiple_answers'])
CHAR_LIMIT = Config.get_value(['query_system', 'character_limit'])
MAX_ANSWERS = Config.get_value(['query_system', 'max_answers'])
URL_FROM_TEXT = Config.get_value(['query_system', 'url_from_text'])

factory = ModelFactory.get_instance()


def handle_not_found(query_text):
    '''
    Inserts this specific query text into the unknown queries collection as well as returning a
    fallback string.
    '''
    try:
        factory.get_database().get_collection("unknown_queries").insert_one(
            {"query_text": query_text})
    except pymongo.errors.DuplicateKeyError:
        # If we already have this specific query in our unknown_queries collection we don't need
        # to add it again.
        pass

    return NOT_FOUND


def get_corpus_text(doc):
    ''' Converts a document from the model into a string which will be used in a corpus.
    All possible answers are used to generate the corpus, if multiple answers exist.'''
    content = ' '.join(doc['content']['texts'])
    return doc['content']['title'] + ' ' + content


def get_answer_text(doc):
    ''' Converts a document from the model into a readable string. '''
    content = random.choice(doc['content']['texts']) + '\n' + URL_FROM_TEXT + doc['url']
    return doc['content']['title'] + ':\n' + content


def perform_search(query_text):
    ''' Takes a query string and finds the best matching document in the database. '''
    # Connect to the database to enable retrieving of documents.
    factory = ModelFactory.get_instance()
    util.set_db(factory)

    # Perform simple query expansion on the original query.
    query = expand_query(query_text)
    print('Post expansion: ', query)

    # Retrieve a set of documents using MongoDB. We then attempt to filter these further.
    docs = factory.get_document(query)

    # Prevent generating an empty corpus if no documents were found.
    if not docs:
        return handle_not_found(query_text)

    # Create a corpus on the results from the MongoDB query.
    corpus = [get_corpus_text(doc) for doc in docs]

    # Create a TF-IDF model on the corpus.
    vectorizer, corpus_matrix, feature_names = get_tfidf_model(corpus)

    try:
        # Compare the search query with all documents in our new model using cosine similarity.
        scores = cosine_similarity(vectorizer.transform([query_text]), corpus_matrix)[0].tolist()

        sorted_scores = sorted(scores, reverse=True)

        # This could be calculated using the mean of all scores and the standard deviation.
        if sorted_scores[0] < 0.1:
            return handle_not_found(query_text)

        # Allow returning multiple answers if they rank very similarly.
        answers = []

        for score in sorted_scores:
            # Tolerance for similarity between scores.
            if sorted_scores[0] - score > 0.1:
                break

            # Add this result to the list of answers.
            answers.append(get_answer_text(docs[scores.index(score)]))

        if len(answers) == 1:
            # Return the answer straight away if there is only 1 result/
            return answers[0]

        # Append answers until we reach the CHAR_LIMIT
        i, n_chars = 0, 0
        while n_chars < CHAR_LIMIT and i < len(answers):
            n_chars += len(answers[i])
            i += 1

        # Join the results with a separator. Still setting a max number of answers
        return '\n\n---\n\n'.join([MULTIPLE_ANSWERS] + answers[0:min(max(i, 1), MAX_ANSWERS)])
    except KeyError:
        raise Exception('Document does not have content and texts.')
    except ValueError:
        return handle_not_found(query_text)


class QuerySystem:
    def webhook_query(self, raw_query_text, intent, entities, default_text):
        '''
        Called when a user asks a question in DialogFLow.

        :param raw_query_text: The full query text from the user.
        :param intent: The intent that DialogFlow matched.
        :param entities: The entities that got matched.
        :param default_text: The randomly chosen static reply from the intent, if any.

        :return: A string which is the complete answer to the user query.
        '''

        print('raw_query_text:', raw_query_text)
        print('intent:', intent)
        print('entities:', entities)
        print('default_text:', default_text)

        result = perform_search(raw_query_text)

        print('result:', result)

        return result

    def get_response(self, text):
        return perform_search(text)
