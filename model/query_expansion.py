import nltk
from nltk.corpus import wordnet as wn
import spacy
from nltk.stem.snowball import SnowballStemmer
import string
from model.SynsetWrapper import SynsetWrapper
from model.keyword_gen import get_stopwords


nltk.download('wordnet')
nltk.download('omw')

# Load a Norwegian language model for Spacy.
nb = spacy.load('nb_dep_ud_sm')

stemmer = SnowballStemmer('norwegian')

stopwords = get_stopwords()


def expand_query(query):
    ''' Attempts to expand the given query by using synonyms from WordNet. As
    a consequnece of this process, the query is also tokenized and stemmed. '''

    tokens = [
      # Store tuples of stemmed tokens and their corresponding POS tags.
      (stemmer.stem(token.text), token.pos_) for token in nb(query)
      # Filter away punctuation.
      if token.text not in string.punctuation
    ]

    # Filter away stopwords as we do not want to expand them.
    tokens = [token for token in tokens if token not in stopwords]

    # Store synonyms in a set, so duplicates are not added multiple times.
    synonyms = set()

    # The tokens in the expanded query.
    result = []

    for token in tokens:
        # Convert POS tags from Spacy to WordNet.
        pos = getattr(wn, token[1], None)

        # Find all synsets for the word, using the Norwegian language.
        synsets = wn.synsets(token[0], lang='nob', pos=pos)

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

        result.append(token[0])

        # Add custom synset
        custom_synset_wrapper = SynsetWrapper.get_instance()
        synonyms.update(custom_synset_wrapper.get_synset(token[0]))

    result += list(synonyms)

    return ' '.join(result)
