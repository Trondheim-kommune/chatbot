import string
import os
import pymongo
import logging

from sklearn.metrics.pairwise import cosine_similarity

from spellchecker import SpellChecker

from nltk.corpus import wordnet as wn

from chatbot.model.model_factory import ModelFactory
from chatbot.nlp.keyword import get_tfidf_model, get_stopwords, lemmatize, nb
from chatbot.nlp.synset import SynsetWrapper
from chatbot.util.config_util import Config
from chatbot.util.logger_util import set_logger


if str(os.getenv("LOG")) == "TRUE":
    set_logger()


NOT_FOUND = Config.get_value(['query_system', 'not_found'])
MULTIPLE_ANSWERS = Config.get_value(['query_system', 'multiple_answers'])
CHAR_LIMIT = Config.get_value(['query_system', 'character_limit'])
MAX_ANSWERS = Config.get_value(['query_system', 'max_answers'])
URL_FROM_TEXT = Config.get_value(['query_system', 'url_from_text'])

ANSWER_THRESHOLD = Config.get_value(['query_system', 'answer_threshold'])
SIMILARITY_THRESHOLD = Config.get_value(['query_system', 'similarity_threshold'])


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
    a corpus. '''
    content = doc['content']['text']
    return doc['content']['title'] + ' ' + content


def _get_answer(doc):
    ''' Converts a document from the model into a (text, [links])-answer tuple
    '''
    answer = [doc['content']['text'], doc['content']['links']
              if 'links' in doc['content'] else []]
    # Add the source-url to the list of urls, using the title as link text
    answer[1].append([doc['content']['title'], doc['url']])

    answer[0] = answer[0] + '\n' + doc['content']['title']
    return answer


_url_styles = {
            'plain': '{} {}',
            'html': "<a href='{1}' target='_blank'>{0}</a>"
           }


def _format_answer(answer, url_style):
    ''' Format an answer (text, links) with a specific url_style. Supports plain
    for '{} {}'-like 'text, link' format, and html for a full <a>-tag. Returns
    a plain string '''
    for link in answer[1]:
        answer[0] = answer[0].replace(link[0],
                                      _url_styles[url_style].format(*link))

    return answer[0]


def expand_query(query):
    ''' Attempts to expand the given query by using synonyms from WordNet. As
    a consequnece of this process, the query is also tokenized and lemmatized.
    '''
    spell = SpellChecker(local_dictionary='chatbot/nlp/statics/no_50k.json')

    # Tokenize, tag and filter query using Spacy
    tokens = [
        # Store both token text and POS tag
        (token.text, token.pos_) for token in nb(query)
        # Filter away punctuation.
        if token.text not in string.punctuation
    ]

    # Add possible spelling corrections, without duplicates
    # We also want to keep the original token, since the detected misspelling
    # migt be intentional - power to the user!
    tokens += [
        (spell.correction(token[0]), token[1]) for token in tokens
        if not spell.correction(token[0]) in [
            token[0] for token in tokens
        ]
    ]

    # Lemmatize tokens
    tokens = [
      # Store tuples of lemmatized tokens and their corresponding POS tags.
      (lemmatize(token[0], token[1])[0], token[0]) for token in tokens
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


def _perform_search(query_text, url_style):
    ''' Takes a query string and finds the best matching document in the
    database. '''

    logging.info('Pre expansion: {}'.format(query_text))

    # Perform simple query expansion on the original query.
    query = expand_query(query_text)

    logging.info('Post expansion: {}'.format(query))

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
        if sorted_scores[0] < ANSWER_THRESHOLD:
            return _handle_not_found(query_text)

        # Allow returning multiple answers if they rank very similarly.
        answers = []

        for score in sorted_scores:
            # Tolerance for similarity between scores.
            if sorted_scores[0] - score > SIMILARITY_THRESHOLD:
                break

            # Add this result to the list of answers.
            answers.append(_get_answer(docs[scores.index(score)]))

        if len(answers) == 1:
            # Return the answer straight away if there is only 1 result
            return _format_answer(answers[0], url_style)

        # Append answers until we reach the CHAR_LIMIT
        i, n_chars = 0, 0
        while n_chars < CHAR_LIMIT and i < len(answers):
            n_chars += len(answers[i])
            i += 1

        # If we only have 1 answer after threshold we don't want to add the
        # MULTI_ANSWERS option to the response
        if max(i, 1) == 1:
            return _format_answer(answers[0], url_style)

        # Join the results with a separator. Still setting a max number of
        # answers
        answers = answers[0:min(max(i, 1,), MAX_ANSWERS)]
        answers = [_format_answer(ans, url_style) for ans in answers]
        return '\n\n---\n\n'.join([MULTIPLE_ANSWERS] + answers)
    except KeyError:
        raise Exception('Document does not have content and texts.')
    except ValueError:
        return _handle_not_found(query_text)


class QueryHandler:
    def get_response(self, query, url_style='plain', source='dev'):
        logging.info('Source: {}'.format(source))
        response = _perform_search(query, url_style)
        logging.info('Response: {}'.format(response))
        return response
