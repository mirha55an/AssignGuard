# AssignGuard

AssignGuard is an academic assignment similarity detection tool. It accepts multiple `.txt` submissions, preprocesses the text, computes TF-IDF cosine similarity, ranks suspicious document pairs, and visualizes the results with a dark-mode dashboard.

## Tech Stack

### Frontend

- HTML
- CSS
- Vanilla JavaScript
- SVG-based charts for the heatmap and PCA projection
- Google Fonts:
  - DM Sans
  - DM Mono
  - Instrument Serif

The frontend does not use React, Vue, Tailwind, Bootstrap, or a component framework. It is a static frontend served from `app/frontend`.

### Backend

- Python
- Starlette ASGI app
- Uvicorn server
- scikit-learn for TF-IDF, cosine similarity, PCA, and DBSCAN
- spaCy and NLTK for preprocessing
- pandas for tabular report data

## Project Structure

```text
AssignGuard/
  app/
    server.py              # Starlette backend and API routes
    streamlit_app.py       # Original Streamlit app
    frontend/
      index.html           # Dashboard markup
      styles.css           # Dark-mode dashboard styling
      app.js               # Upload flow, API calls, SVG charts
  data/
    raw/                   # Sample assignment files
    labels/                # Evaluation labels
  src/
    preprocessing.py       # Text cleaning, stopword removal, lemmatization
    similarity.py          # TF-IDF and similarity functions
    clustering.py          # DBSCAN clustering utilities
    visualization.py       # Pair ranking and legacy plotting helpers
    evaluation.py          # Model evaluation helpers
    utils.py               # Shared utility functions
  test.py                  # Local experiment script
```

## How To Run

From the project root:

```powershell
cd F:\AssignGuard
```

If you already have the included virtual environment, run:

```powershell
.\venv\Scripts\python.exe -m uvicorn app.server:app --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000/
```

## If You Need To Create A Fresh Environment

```powershell
python -m venv venv
.\venv\Scripts\activate
python -m pip install streamlit scikit-learn pandas matplotlib seaborn nltk spacy uvicorn starlette python-multipart
python -m spacy download en_core_web_sm
python -m nltk.downloader stopwords
```

Then start the app:

```powershell
python -m uvicorn app.server:app --host 127.0.0.1 --port 8000
```

## How To Use

1. Open the dashboard in the browser.
2. Select two or more `.txt` assignment files from the sidebar.
3. Adjust the similarity threshold, DBSCAN epsilon, and minimum samples if needed.
4. Click `Run Analysis`.
5. Review:
   - total uploaded documents
   - flagged suspicious pairs
   - highest similarity score
   - similarity heatmap
   - PCA projection
   - DBSCAN clusters (sorted by cluster)

## API

The frontend sends uploaded files to:

```text
POST /api/analyze
```

The request uses `multipart/form-data` with:

- `files`: one or more `.txt` files
- `threshold`: similarity threshold, default `0.70`
- `eps`: DBSCAN epsilon, default `0.60`
- `min_samples`: DBSCAN minimum samples, default `3`

The response includes:

- `documents`
- `threshold`
- `similarity_matrix`
- `suspicious_pairs`
- `pca_points`
- `clusters`

## Notes

- The old Streamlit app is still available at `app/streamlit_app.py`, but the current dashboard is served by `app/server.py`.
- The frontend is intentionally framework-free so it can be edited directly through `index.html`, `styles.css`, and `app.js`.
- Input files should be UTF-8 encoded `.txt` files.
