import streamlit as st
from src.preprocessing import preprocess_text
from src.similarity import tfidf_similarity
from src.visualization import rank_suspicious_pairs, visualize, plot_clusters
from src.clustering import reduce_dimensions, plot_pca, perform_dbscan, create_cluster_table
from src.evaluation import evaluate_model
from src.utils import read_uploaded_file

st.set_page_config(
    page_title="AssignGuard",
    layout="wide"
)

st.title("AssignGuard")
st.subheader("Academic Assignment Similarity Detection System")

uploaded_files = st.file_uploader(
    "Upload assignment files",
    type=["txt"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} files uploaded")

    # Converting uploaded files to preprocessed text
    texts = read_uploaded_file(uploaded_files)
    preprocessed_text = [preprocess_text(text) for text in texts]

    if len(uploaded_files) < 2:
        st.warning("Please upload at least two assignment files.")
        st.stop()
    #Computing TF-IDF similarity
    similarity_matrix, tfidf_vectors = tfidf_similarity(preprocessed_text)
    # Ranking suspicious pairs
    st.subheader("Ranking Suspicious Pairs")
    threshold = st.slider(
        "Similarity Threshold (Recommended 0.70)",
        min_value=0.0,
        max_value=1.0,
        value=0.70,
        step=0.05
    )
    suspicious_pairs = rank_suspicious_pairs(similarity_matrix, [uploaded_file.name for uploaded_file in uploaded_files if uploaded_file is not None], threshold=threshold)
    if suspicious_pairs.empty:
        st.warning(
            "No suspicious pairs found above the selected threshold."
        )
    else:
        st.dataframe(
            suspicious_pairs,
            use_container_width=True
        )
        
    # Similarity Heatmap
    st.subheader("Similarity Heatmap")
    heatmap_fig = visualize(
        similarity_matrix,
        [file.name for file in uploaded_files]
        )

    st.pyplot(heatmap_fig)
    
    # PCA Visualization
    st.subheader("PCA Visualization")
    reduced_vectors = reduce_dimensions(tfidf_vectors)
    pca_fig = plot_pca(reduced_vectors, [file.name for file in uploaded_files])
    st.pyplot(pca_fig)
    
    # Displaying the Cluster Table
    eps = st.slider(
        "DBSCAN Epsilon (Recommended 0.6)",
        0.1,
        2.0,
        0.6,
        0.1
    )

    min_samples = st.slider(
        "DBSCAN Min Samples (Recommended 3)",
        2,
        10,
        3
    )
    cluster_labels = perform_dbscan(
        tfidf_vectors,
        eps=eps,
        min_samples=min_samples
    )
    
    st.subheader("DBSCAN Clusters")
    
    cluster_df = create_cluster_table(
        [file.name for file in uploaded_files],
        cluster_labels
    )
    st.dataframe(cluster_df)


    st.subheader("Cluster Visualization")

    cluster_fig = plot_clusters(
        reduced_vectors,
        cluster_labels,
        [file.name for file in uploaded_files]
    )

    st.pyplot(cluster_fig)
    
    # Footer
    st.divider()

    st.caption(
        "AssignGuard - Academic Assignment Similarity Detection System"
    )