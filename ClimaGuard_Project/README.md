# CLIMAGUARD — Climate Intelligence Dashboard

A Python-only Streamlit mini-project for DBMS + FODS. It explores the supplied IMD/AWS-style heatwave dataset with interactive climate charts, filters, regional comparison, project-level risk indicators, data-quality views, and CSV exports.

## Project layout

```text
ClimaGuard_Project/
├── app.py                         # Streamlit entry point and page routing
├── climaguard/                    # Reusable application modules
│   ├── __init__.py
│   ├── data.py                    # CSV loading and column type normalization
│   ├── risk.py                    # Explainable project risk scoring
│   ├── charts.py                  # Shared Plotly formatting
│   └── styles.py                  # Dashboard theme and CSS
├── data/
│   └── heatwave_imd_aws_dataset (1).csv
├── tests/
│   └── test_risk.py               # Basic scoring tests
├── requirements.txt
├── .gitignore
└── README.md
```

## Run on macOS

Python 3.10+ recommended. Open Terminal and move into this folder.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`. Open it in your browser. **Do not start this app with `python app.py`; use `streamlit run app.py`.**

## Dataset

The app expects `data/heatwave_imd_aws_dataset (1).csv`. The default path is configured relative to the project. If you replace the dataset, keep the column names used by the dashboard or update the column mapping in `app.py`.

## Current scope and limitations

- The current data source is the included CSV; this project does not yet connect to MySQL or a live IMD/NDMA feed.
- The risk score and hazard bars are illustrative student-project analytics, not official IMD thresholds, emergency alerts, or validated predictions.
- No user authentication or role-based access is implemented in this CSV-backed prototype.

## Tests

```bash
python -m unittest discover -s tests -v
```
