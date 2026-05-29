from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
from starlette.applications import Starlette
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from src.clustering import create_cluster_table, perform_dbscan
from src.preprocessing import preprocess_text
from src.similarity import tfidf_similarity
from src.visualization import rank_suspicious_pairs


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"


def _json_error(message, status_code=400):
    return JSONResponse({"error": message}, status_code=status_code)


def _safe_pca_points(tfidf_vectors):
    dense_vectors = tfidf_vectors.toarray()

    if dense_vectors.shape[0] < 2:
        return [[0.0, 0.0]]

    components = min(2, dense_vectors.shape[0], dense_vectors.shape[1])
    if components == 0:
        return [[0.0, 0.0] for _ in range(dense_vectors.shape[0])]

    reduced = PCA(n_components=components).fit_transform(dense_vectors)
    if components == 1:
        reduced = np.column_stack([reduced[:, 0], np.zeros(reduced.shape[0])])

    return reduced.round(4).tolist()


async def index(_request):
    return FileResponse(FRONTEND_DIR / "index.html")


async def analyze(request):
    form = await request.form()
    threshold = float(form.get("threshold", 0.7))
    eps = float(form.get("eps", 0.6))
    min_samples = int(form.get("min_samples", 3))
    files = form.getlist("files")

    uploaded_files = [
        file for file in files if getattr(file, "filename", "") and file.filename.endswith(".txt")
    ]

    if len(uploaded_files) < 2:
        return _json_error("Upload at least two .txt assignment files.")

    names = []
    texts = []
    for uploaded_file in uploaded_files:
        raw = await uploaded_file.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            return _json_error(f"{uploaded_file.filename} is not valid UTF-8 text.")

        names.append(uploaded_file.filename)
        texts.append(text)

    processed_texts = [preprocess_text(text) for text in texts]
    similarity_matrix, tfidf_vectors = tfidf_similarity(processed_texts)
    suspicious_pairs = rank_suspicious_pairs(similarity_matrix, names, threshold=threshold)
    pca_points = _safe_pca_points(tfidf_vectors)
    cluster_labels = perform_dbscan(tfidf_vectors, eps=eps, min_samples=min_samples)
    cluster_table = create_cluster_table(names, cluster_labels)

    response = {
        "documents": names,
        "threshold": threshold,
        "similarity_matrix": similarity_matrix.round(4).tolist(),
        "suspicious_pairs": suspicious_pairs.to_dict(orient="records"),
        "pca_points": pca_points,
        "clusters": cluster_table.to_dict(orient="records"),
    }

    return JSONResponse(response)


routes = [
    Route("/", index),
    Route("/api/analyze", analyze, methods=["POST"]),
    Mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static"),
]

app = Starlette(debug=True, routes=routes)
