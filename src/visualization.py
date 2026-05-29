import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def visualize(similarity_matrix, doc_names, title = "Similarity Heatmap"):
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(similarity_matrix, xticklabels=doc_names, yticklabels=doc_names, cmap='coolwarm', annot=True, ax=ax)
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()
    return fig
    
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
    if df.empty:
        return df

    df = df.sort_values(by="Similarity Score", ascending=False).reset_index(drop=True)
    return df



def plot_clusters(reduced_vectors,cluster_labels,doc_names):

    fig, ax = plt.subplots(figsize=(10, 8))

    scatter = ax.scatter(
        reduced_vectors[:, 0],
        reduced_vectors[:, 1],
        c=cluster_labels
    )

    for i, name in enumerate(doc_names):

        ax.annotate(
            name.replace(".txt", ""),
            (
                reduced_vectors[i, 0],
                reduced_vectors[i, 1]
            ),
            fontsize=8
        )

    ax.set_title("DBSCAN Clusters")

    return fig