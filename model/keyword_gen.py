from sklearn.feature_extraction.text import TfidfVectorizer


def get_stopwords():
    with open('stopwords.txt') as stopwords:
      return [line.strip() for line in stopwords.readlines() if line.strip()]

stop_words = get_stopwords()


def sort_coo(coo_matrix):
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)


def extract_top(feature_names, sorted_items, n=10):
    return [(feature_names[i], score) for i, score in sorted_items[:n]]


def get_tfidf_model(corpus):
    vectorizer = TfidfVectorizer(stop_words=stop_words)
    corpus_matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names()
    return vectorizer, corpus_matrix, feature_names


def get_keywords(vectorizer, feature_names, document, n=10):
    tfidf_vector = vectorizer.transform([document])
    sorted_items = sort_coo(tfidf_vector.tocoo())
    return extract_top(feature_names, sorted_items, n)
