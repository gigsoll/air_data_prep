# Data Science Notebook Collection

An end-to-end collection of Jupyter notebooks for real-world data workflows:
- Air quality ETL and forecasting
- Public appeals exploratory analysis and outcome prediction
- Social media ad performance modeling

The repository is designed for practical experimentation in a reproducible Docker-based JupyterLab environment.

## What Is Inside

- `air_quality_ml.ipynb` and `data_prep.ipynb`: data ingestion, cleansing, feature engineering, database loading, and ML for air quality data.
- `public_reports_eda.ipynb` and `public_reports_ml.ipynb`: exploratory analysis plus predictive modeling on public appeals.
- `social_media_analysis.ipynb`: staged modeling and tuning for ad event outcomes on a social media campaign dataset.
- `Dockerfile`: ready-to-run notebook environment based on Jupyter Data Science stack.

## Notebook Guide

### `data_prep.ipynb`
- **Purpose:** Build the raw data ingestion and preparation pipeline for air monitoring records.
- **Highlights:** web scraping from the open data portal, CSV consistency checks, preprocessing, and SQLAlchemy-based schema loading.
- **Outputs:** structured, cleaned tabular data and database-ready entities for downstream analysis.

### `air_quality_ml.ipynb`
- **Purpose:** Full ETL + ML pipeline for air quality forecasting and diagnostics.
- **Highlights:** dependency-injected pipeline design, data quality normalization, Snowflake-style modeling, feature generation, and regressors (including boosted trees).
- **Outputs:** trained models, evaluation metrics, feature insights, and time-based analysis visualizations.

### `public_reports_eda.ipynb`
- **Purpose:** Explore citizen appeals data to understand structure, quality, behavior, and resolution patterns.
- **Highlights:** encoding-aware CSV loading, temporal feature extraction, correlation checks, and targeted visual EDA.
- **Outputs:** actionable trends by time/category/status and a feature-informed foundation for classification.

### `public_reports_ml.ipynb`
- **Purpose:** Predict appeal review outcomes from textual and tabular features.
- **Highlights:** TF-IDF text engineering, categorical/numeric preprocessing, class handling, model comparison, and tuning loops.
- **Outputs:** evaluated classifiers, confusion-matrix-driven performance analysis, and interpretable feature importance views.

### `social_media_analysis.ipynb`
- **Purpose:** Analyze and model social media ad effectiveness with balanced evaluation.
- **Highlights:** Kaggle dataset ingestion, DuckDB over SQLite, class balancing (downsampling/oversampling), staged hyperparameter search, optional XGBoost.
- **Outputs:** robust multi-class performance reports, model ranking, and stage-wise visual comparison.

## Quick Start (Docker-First)

### 1) Build the image

```bash
docker build -t notebook-collection .
```

### 2) Run JupyterLab in a container

```bash
docker run --rm -it \
  -p 8888:8888 \
  -v "$(pwd)":/home/jovyan/work \
  notebook-collection \
  start-notebook.py --NotebookApp.token=''
```

### 3) Open JupyterLab

Go to [http://localhost:8888/lab](http://localhost:8888/lab).

## Docker Environment Notes

The provided `Dockerfile` extends:
- `quay.io/jupyter/datascience-notebook:2026-04-02`

It additionally installs:
- system packages for MySQL Python bindings (`default-libmysqlclient-dev`, `build-essential`, `pkg-config`)
- Jupyter tooling (`jupyterlab-lsp`, `python-lsp-server[all]`, `jupyterlab-gruvbox-dark`, `jupyterthemes`)
- database/ORM dependencies (`sqlalchemy`, `mysqlclient`)

The container workspace is set to:
- `/home/jovyan/work`

## Data Notes

- Air quality notebooks use data from the Ukrainian Open Data portal (`air_monitor` dataset).
- Public reports notebooks expect a local CSV dataset under `./data` (for example `appeals_2026-04-02.csv`).
- Social media notebook pulls data via `kagglehub` and reads an SQLite database through DuckDB.
- Keep raw and intermediate files under `./data` to avoid path breakage across notebooks.

## Tech Stack

- **Core analytics:** `pandas`, `numpy`, `scipy`
- **Visualization:** `matplotlib`, `seaborn`, `plotly`
- **Machine learning:** `scikit-learn`, `xgboost`, `lightgbm`, `catboost`
- **Data access and storage:** `SQLAlchemy`, `mysqlclient`, `duckdb`, `requests`, `beautifulsoup4`
- **Notebook runtime:** JupyterLab + LSP extensions

## Suggested Execution Order

For a clean end-to-end walkthrough:

1. `data_prep.ipynb`
2. `air_quality_ml.ipynb`
3. `public_reports_eda.ipynb`
4. `public_reports_ml.ipynb`
5. `social_media_analysis.ipynb`

This order moves from data acquisition and preprocessing into EDA, then into supervised modeling and comparative evaluation.

## Optional Enhancements

- Add a `requirements.txt` or `environment.yml` for non-Docker execution.
- Add dataset schema snapshots and minimal sample files in `./data`.
- Add CI checks for notebook execution smoke-tests.
- Add badges (Docker build, notebook health, license) for repository visibility.

