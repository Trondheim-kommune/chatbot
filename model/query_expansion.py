import nltk
from nltk.corpus import wordnet as wn
import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.nb import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
import string

nltk.download('wordnet')
nltk.download('omw')

# Load a Norwegian language model for Spacy.
nb = spacy.load('nb_dep_ud_sm')


lemmatize = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)


def expand_query(query):
    ''' Attempts to expand the given query by using synonyms from WordNet. As
    a consequnece of this process, the query is also tokenized and lemmatized. '''

    tokens = [
      # Store tuples of lemmatized tokens and their corresponding POS tags.
      (lemmatize(token.text, token.pos_)[0], token.pos_) for token in nb(query)
      # Filter away punctuation.
      if token.text not in string.punctuation
    ]

    result = []

    for token in tokens:
        # Convert POS tags from Spacy to WordNet.
        pos = getattr(wn, token[1], None)

        # Find all synsets for the word, using the Norwegian language.
        synsets = wn.synsets(token[0], lang='nob', pos=pos)

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

    return ' '.join(result)
