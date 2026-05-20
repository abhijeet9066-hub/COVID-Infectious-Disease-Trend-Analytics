# COVID Infectious Disease Trend Analytics

## Business Objective
Build an end-to-end analytics and machine learning project using real-world public data to support decision making.

## Dataset Strategy
Primary source: **Our World in Data COVID dataset**

Place downloaded files in:

```text
data/raw/
```

or update:

```text
config/config.yaml
```

## Tech Stack
- Python: pandas, scikit-learn, statsmodels
- SQL: SQLite analytical warehouse
- ML: time-series forecasting
- Power BI: star schema dashboard, DAX measures, KPI cards

## Project Workflow
1. Ingest raw data
2. Clean and validate data
3. Create SQL-ready tables
4. Run EDA
5. Train ML model
6. Export dashboard tables
7. Build Power BI report using files in `data/processed/`

## Run

```bash
python src/01_ingest.py
python src/02_clean.py
python src/03_train_model.py
python src/04_export_powerbi.py
```

## Power BI Dashboard Pages
1. Executive Summary
2. Trend Analysis
3. Segment / Risk Drivers
4. ML Prediction Insights
5. Action Recommendations

## Suggested KPIs
- Total records
- Monthly trend
- High-risk cases / high-value segments
- Prediction accuracy / ROC-AUC
- Top drivers from feature importance

## Recruiter Value
This project demonstrates practical skills in data cleaning, SQL modeling, ML, healthcare/business analytics, and dashboard storytelling.
