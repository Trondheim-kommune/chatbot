import json
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from multi_rake import Rake

rake = Rake(language_code='no')

def sort_coo(coo_matrix):
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)
 
def extract_topn_from_vector(feature_names, sorted_items, topn=10):
    """get the feature names and tf-idf score of top n items"""
    
    #use only topn items from vector
    sorted_items = sorted_items[:topn]
 
    score_vals = []
    feature_vals = []
    
    # word index and corresponding tf-idf score
    for idx, score in sorted_items:
        
        #keep track of feature name and its corresponding score
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])
 
    #create a tuples of feature,score
    #results = zip(feature_vals,score_vals)
    results= {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]]=score_vals[idx]
    
    return results

with open('scraper/trondheim.json') as f:
    paragraphs = json.load(f)

    corpus = []

    for paragraph in paragraphs:
        # Parse the paragraph HTML using BeautifulSoup.
        soup = BeautifulSoup(paragraph['contents'], features='lxml')

        # Retrieve the raw text from the paragraph.
        paragraph_text = soup.get_text()

        # Strip extra spaces around all lines.
        lines = (line.strip() for line in paragraph_text.splitlines())

        # Remove blank lines.
        paragraph_text = '\n'.join(line for line in lines if line)

        if len(paragraph_text) > 200:
            # Append the parsed text to the corpus.
            corpus.append(paragraph_text)

    vectorizer = TfidfVectorizer(max_df=0.7)

    X = vectorizer.fit_transform(corpus)

    feature_names = vectorizer.get_feature_names()

    for doc in corpus:
        tfidf_vector = vectorizer.transform([doc])

        sorted_items=sort_coo(tfidf_vector.tocoo())
    
        #extract only the top n; n here is 10
        keywords=extract_topn_from_vector(feature_names,sorted_items,10)
        
        # now print the results
        print("\n=====Doc=====")
        print(doc)
        print("\n===Keywords===")
        for k in keywords:
            print(k,keywords[k])


        print("\n===RAKE===")
        keywords = rake.apply(doc)
        print(keywords[:10])
