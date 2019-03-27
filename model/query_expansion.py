import nltk
from nltk.corpus import wordnet as wn
import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.nb import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
import string
from model.SynsetWrapper import SynsetWrapper
from model.keyword_gen import get_stopwords


nltk.download('wordnet')
nltk.download('omw')

# Load a Norwegian language model for Spacy.
nb = spacy.load('nb_dep_ud_sm')

lemmatize = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)

stopwords = get_stopwords()


def expand_query(query):
    ''' Attempts to expand the given query by using synonyms from WordNet. As
    a consequnece of this process, the query is also tokenized and lemmatized. '''

    tokens = [
      # Store tuples of lemmatized tokens and their corresponding POS tags.
      (lemmatize(token.text, token.pos_)[0], token.pos_) for token in nb(query)
      # Filter away punctuation.
      if token.text not in string.punctuation
    ]

    # Filter away stopwords as we do not want to expand them.
    tokens = [token for token in tokens if token not in stopwords]

    # Custom synset tokens
    custom_synset = set()

    # The tokens in the expanded query.
    result = []

    for token in tokens:
        # Convert POS tags from Spacy to WordNet.
        pos = getattr(wn, token[1], None)

        # Find all synsets for the word, using the Norwegian language.
        synsets = wn.synsets(token[0], lang='nob', pos=pos)

        # Get a custom synset wrapper
        custom_synset_wrapper = SynsetWrapper.get_instance()
        # Get the synset for this token
        new_synset = custom_synset_wrapper.get_synset(token[0])
        if new_synset:
            # Remove the token itself to avoid duplication
            new_synset.remove(token[0])
            custom_synset.update(new_synset)

        if synsets:
            # Store synonyms in a set, as when there are multiple synsets, we
            # might end up getting the same lemma names multiple times.
            synonyms = set()

            for synset in synsets:
                # Find all lemmas in the synset.
                for name in synset.lemma_names(lang='nob'):
                    # Some lemmas contain underscores, which we remove.
                    synonyms.add(name.replace('_', ' '))

            result += list(synonyms)

            # If we found synonyms, we only add the synonyms. This is because
            # the original word is already included in the synset, so this
            # avoids adding it to the result list twice.
            continue

        result.append(token[0])

    # Add custom synset to the query
    result += custom_synset
    return ' '.join(result)
