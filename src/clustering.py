from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import DBSCAN

def reduce_dimensions(tfidf_matrix):
    pca = PCA(n_components=2)
    reduced_vectors = pca.fit_transform(tfidf_matrix.toarray())
    
    return reduced_vectors

def plot_pca(reduced_vectors, doc_names):
    fig, ax = plt.subplots(figsize=(10, 8))

    x = reduced_vectors[:, 0]
    y = reduced_vectors[:, 1]

    ax.scatter(x, y)

    for i, name in enumerate(doc_names):

        ax.annotate(
            name.replace(".txt", ""),
            (x[i], y[i]),
            fontsize=8
        )

    ax.set_title("PCA of TF-IDF Vectors")
    ax.set_xlabel("Principal Component 1")
    ax.set_ylabel("Principal Component 2")

    return fig
    
def perform_dbscan(tfidf_matrix, eps=0.6, min_samples=2):
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    dense_vectors = tfidf_matrix.toarray()
    clusters = dbscan.fit_predict(dense_vectors)
    unique_labels = set(clusters)
    if 1 < len(unique_labels) < len(clusters):
        score = silhouette_score(
        dense_vectors,
        clusters
        )
        print(f"Silhouette Score: {score:.3f}")
    else:
        print("Silhouette Score cannot be computed.")
    
    return clusters

def create_cluster_table(doc_names,cluster_labels):

    return pd.DataFrame({
        "Document": doc_names,
        "Cluster": cluster_labels
    })
