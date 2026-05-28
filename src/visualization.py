import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def visualize(similarity_matrix, doc_names, title):
    sns.heatmap(similarity_matrix, xticklabels=doc_names, yticklabels=doc_names, cmap='coolwarm', annot=True)
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()
    
def rank_suspicious_pairs(similarity_matrix, doc_names, threshold=0.70):
    pairs = []
    num_docs = len(doc_names)
    
    for i in range(num_docs):
        for j in range(i + 1, num_docs):
            similarity_score = similarity_matrix[i][j]
            
            # Apply threshold
            if similarity_score >= threshold:
                pairs.append({
                    "Document 1": doc_names[i],
                    "Document 2": doc_names[j],
                    "Similarity Score": round(similarity_score,2)
                })
                
    df = pd.DataFrame(pairs)
    df = df.sort_values(by="Similarity Score", ascending=False).reset_index(drop=True)
    return df