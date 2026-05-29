from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def tfidf_similarity(documents):
    # Creating the vectorizer
    vectorizer = TfidfVectorizer()

    # Converting the documents into a TF-IDF matrix
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Computing the cosine similarity matrix
    similarity_matrix = cosine_similarity(tfidf_matrix)

    return similarity_matrix, tfidf_matrix

def jaccard_similarity(documents):
    num_docs = len(documents)
    matrix = []
    
    for i in range(num_docs):
        row = []
        set1 = set(documents[i].split())
        
        for j in range(num_docs):
            set2 = set(documents[j].split())
            
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            
            similarity = intersection / union
            row.append(similarity)
            
        matrix.append(row)
    
    return matrix
        