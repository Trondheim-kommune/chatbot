from model.ModelFactory import ModelFactory
import model.db_util as util
from sklearn.metrics.pairwise import cosine_similarity
from model.keyword_gen import get_tfidf_model
from model.query_expansion import expand_query


NOT_FOUND = 'Jeg fant ikke informasjonen du spurte etter.'


def get_corpus_text(doc):
    ''' Converts a document from the model into a string which will be used in a corpus. '''
    content = ' '.join(doc['content']['texts'])
    return doc['content']['title'] + ' ' + content


def get_answer_text(doc):
    ''' Converts a document from the model into a readable string. '''
    content = ' '.join(doc['content']['texts']) + '\n' + doc['url']
    return doc['content']['title'] + ':\n' + content


def perform_search(query_text):
    ''' Takes a query string and finds the best matching document in the database. '''
    # Connect to the database to enable retrieving of documents.
    factory = ModelFactory.get_instance()
    util.set_db(factory, db='dev_db')

    # Perform simple query expansion on the original query.
    query = expand_query(query_text)

    # Retrieve a set of documents using MongoDB. We then attempt to filter these further.
    docs = factory.get_document(query)

    # Prevent generating an empty corpus if no documents were found.
    if not docs: return NOT_FOUND

    # Create a corpus on the results from the MongoDB query.
    corpus = [get_corpus_text(doc) for doc in docs]

    # Create a TF-IDF model on the corpus.
    vectorizer, corpus_matrix, feature_names = get_tfidf_model(corpus)

    try:
        # Compare the search query with all documents in our new model using cosine similarity.
        scores = cosine_similarity(vectorizer.transform([query_text]), corpus_matrix)[0]
        return get_answer_text(docs[scores.tolist().index(max(scores))])
    except KeyError:
        raise Exception('Document does not have content and texts.')
    except ValueError:
        return NOT_FOUND


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