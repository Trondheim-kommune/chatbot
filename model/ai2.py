import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.nb import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES

nb = spacy.load('nb_dep_ud_sm')

lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)

doc = nb('Kjære Kommune-Knut, vennligst fortell meg når Husebybadet åpner!')

for token in doc:
    lemmas = lemmatizer(token.text, token.pos_)
    print(lemmas)
