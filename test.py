from src.preprocessing import preprocess_document
from src.similarity import jaccard_similarity, tfidf_similarity
from src.evaluation import evaluate_model
from src.visualization import visualize, rank_suspicious_pairs
import os

path = './data/raw'
# Store all file paths first 
file_paths = [] 
for root, _, files in os.walk(path): 
    for f in files: 
        if f.endswith('.txt'): 
            file_paths.append(os.path.join(root, f))
            
# Keep ordering consistent 
file_paths.sort()
documents = [preprocess_document(file_path) for file_path in file_paths]

tfidf_matrix = tfidf_similarity(documents)
jaccard_matrix = jaccard_similarity(documents)

doc_names = [os.path.basename(file_path) for file_path in file_paths]
print(doc_names)
results_tfidf = evaluate_model(tfidf_matrix, doc_names, 'F:/AssignGuard/data/labels/pairs.csv', threshold=0.70)
results_jaccard = evaluate_model(jaccard_matrix, doc_names, 'F:/AssignGuard/data/labels/pairs.csv', threshold=0.70)

print(rank_suspicious_pairs(tfidf_matrix, doc_names, threshold=0.70))
print(rank_suspicious_pairs(jaccard_matrix, doc_names, threshold=0.60))
