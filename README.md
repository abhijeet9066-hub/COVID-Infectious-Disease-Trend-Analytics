# Global COVID-19 Surveillance Trend Analytics

A reproducible **WHO / Our World in Data + Python + SQL + Power BI** portfolio project analyzing historical confirmed COVID-19 reporting trends across countries.

> **Interpretation warning:** Confirmed case and death counts are surveillance/reporting data. They do not represent all infections or all deaths caused by COVID-19, and cross-country comparisons are affected by testing, reporting, population structure, surveillance practice and revisions.

## Why This Repository Was Rebuilt

The previous repository was a generic analytics/ML skeleton. It named Our World in Data as the intended source but contained no COVID dataset and used a generic classification/model template unrelated to epidemic surveillance.

This rebuild replaces that placeholder workflow with a transparent historical surveillance pipeline using real public data.

## Source

The project uses Our World in Data chart CSVs whose underlying confirmed case/death source is the **World Health Organization (WHO)**.

Four public series are extracted:

- weekly confirmed COVID-19 cases;
- weekly confirmed COVID-19 deaths;
- weekly confirmed cases per million people;
- weekly confirmed deaths per million people.

The extractor keeps ISO alpha-3 country rows and excludes OWID aggregate entities.

OWID describes these indicators as totals over the **previous week**. To avoid treating overlapping daily trailing-7-day values as independent weeks, the extractor retains **Sunday observations only**, producing a consistent non-overlapping weekly series for this portfolio analysis.

## Fixed Historical Window

```text
2020-01-05 through 2025-12-28
```

The project deliberately uses a fixed historical end date. It does **not** claim that committed outputs represent current 2026 conditions.

Because historical source data may be revised, each extraction records:

- UTC retrieval time;
- exact source URLs;
- SHA-256 hash of each downloaded CSV;
- fixed analytical window;
- output row and country counts.

See:

```text
data/snapshot/extraction_metadata.json
```

## Analytics

The project builds three recruiter-friendly analytical layers.

### 1. Weekly country surveillance trends

`weekly_country_trends.csv`

Includes:

- weekly confirmed cases;
- weekly confirmed deaths;
- weekly cases per million;
- weekly deaths per million;
- 4-week moving average of cases per million;
- 4-week moving average of deaths per million;
- 4-week reporting trend change versus the preceding four weeks.

Missing source observations remain missing. They are **not silently converted to zero**.

### 2. Annual country summary

`annual_country_summary.csv`

For each country and year:

- summed reported weekly cases;
- summed reported weekly deaths;
- observed reporting weeks;
- average weekly cases per million;
- average weekly deaths per million;
- peak weekly cases per million;
- peak weekly deaths per million.

These are descriptive reporting statistics, not infection-risk estimates.

### 3. Country period summary

`country_period_summary.csv`

For each country over the fixed period:

- total reported cases in available weekly data;
- total reported deaths in available weekly data;
- peak weekly cases per million and date;
- peak weekly deaths per million and date;
- maximum 4-week average rates;
- first/last source observation dates;
- reporting-week coverage.

## Important Limitations

- Confirmed cases are lower than true infections when infections are not detected or reported.
- Confirmed deaths can differ from the true COVID-19 mortality burden.
- Reporting definitions and practices vary by country and over time.
- Historical revisions can create unusual or even negative weekly corrections.
- Weekly totals should not be treated as perfectly comparable exposure-adjusted rates.
- Per-million metrics improve population-size comparability but do not correct for testing intensity, age structure or reporting practice.
- This repository performs **descriptive surveillance analytics**, not epidemiological causal inference and not individual medical prediction.

## Pipeline

```text
WHO data processed by Our World in Data
            ↓
src/01_extract_owid.py
            ↓
data/snapshot/weekly_country_covid.csv
            ↓
src/02_build_metrics.py
            ↓
data/processed/
            ↓
src/03_build_sqlite.py
            ↓
data/processed/global_covid_analytics.sqlite
            ↓
src/04_export_powerbi.py
            ↓
data/powerbi/
```

## Repository Structure

```text
.
├── .github/workflows/ci.yml
├── config/config.json
├── data/
│   ├── source_manifest.csv
│   ├── snapshot/
│   ├── processed/
│   └── powerbi/
├── docs/
│   ├── data_provenance.md
│   ├── methodology.md
│   ├── data_dictionary.md
│   └── limitations.md
├── powerbi/
│   ├── dashboard_blueprint.md
│   └── measures.dax
├── sql/
│   └── analysis_queries.sql
├── src/
│   ├── 01_extract_owid.py
│   ├── 02_build_metrics.py
│   ├── 03_build_sqlite.py
│   ├── 04_export_powerbi.py
│   └── validate_repo.py
├── requirements.txt
└── README.md
```

## Run

The core pipeline uses the Python standard library only.

```bash
python src/01_extract_owid.py
python src/02_build_metrics.py
python src/03_build_sqlite.py
python src/04_export_powerbi.py
python src/validate_repo.py
```

GitHub Actions intentionally does **not** call the live external data source. CI rebuilds the analytical outputs from the committed source snapshot and validates them.

## SQL

The SQLite warehouse supports analysis such as:

- countries with the highest peak weekly case rate;
- countries with the highest peak weekly death rate;
- annual reporting trajectories;
- strongest four-week increases/decreases;
- reporting coverage checks;
- selected-country surveillance comparisons.

## Power BI

Recommended pages:

1. Global Surveillance Overview
2. Country Weekly Trends
3. Per-Million Comparison
4. Annual Burden & Peaks
5. Country Peak Profile
6. Data Quality & Limitations

## Interview Summary

> I rebuilt a generic COVID project into a reproducible global surveillance workflow using WHO-derived series published by Our World in Data. I extract four weekly country-level series over a fixed historical window, preserve missing observations rather than converting them to zero, calculate four-week moving averages and trend changes, create annual and country-level peak summaries, load the outputs into SQLite, and export Power BI-ready tables. I also record retrieval hashes and explicitly separate confirmed reporting trends from true infection or mortality burden.

## Skills Demonstrated

- public-health surveillance analytics
- WHO / Our World in Data integration
- reproducible HTTP data extraction
- SHA-256 provenance tracking
- time-series transformation
- moving averages and trend analysis
- population-normalized metrics
- Python ETL
- SQLite / SQL
- Power BI modeling
- data-quality interpretation
- GitHub Actions CI

## Author

**Abhijeet Vasantrao Patil**  
GitHub: https://github.com/abhijeet9066-hub
