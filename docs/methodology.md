# Methodology

## 1. Download and source validation

The extractor downloads four OWID Grapher CSVs with a descriptive User-Agent.

For each file it records a SHA-256 checksum before parsing.

The parser validates that each CSV contains:

- Entity
- Code
- Day (or Date)
- one metric value column

## 2. Country filter

Rows are retained when the source `Code` is a three-letter uppercase alphabetic value.

This removes OWID synthetic aggregate codes and leaves country-level records.

## 3. Historical and weekly sampling filter

Only rows from `2020-01-05` through `2025-12-28` are retained.

OWID defines these indicators as totals over the previous week. The extractor retains **Sunday observations only** so consecutive retained values correspond to a consistent weekly sampling grid and overlapping trailing-seven-day observations are not double-counted in annual summaries.

## 4. Metric merge

The four series are outer-joined on:

- country/entity
- ISO code
- date

Missing observations remain blank.

They are not imputed as zero because missing surveillance data and true reported zero are not necessarily equivalent.

## 5. Four-week moving averages

For each country and metric, the project calculates the mean of the latest four weekly observations only when all four source values are available.

This is a descriptive smoother.

## 6. Four-week trend change

When eight consecutive retained rows contain complete weekly values:

`current_4_week_average` is compared with the preceding four-week average.

```text
trend_change_pct =
(current_4w_avg - previous_4w_avg)
/
previous_4w_avg
× 100
```

If the comparison denominator is zero, the trend change is left blank.

## 7. Annual summaries

For each country × year the project calculates:

- sum of available weekly reported cases;
- sum of available weekly reported deaths;
- number of observed weeks;
- mean weekly cases per million;
- mean weekly deaths per million;
- peak weekly cases per million;
- peak weekly deaths per million.

Because source revisions can create negative corrections, the pipeline preserves source values rather than forcing all counts to non-negative values.

## 8. Country period summaries

For each country the project identifies:

- peak weekly case rate and date;
- peak weekly death rate and date;
- maximum four-week average rates;
- first and last observation dates;
- reporting coverage relative to the expected Sunday-week grid.

## 9. Interpretation

The pipeline analyzes confirmed surveillance reporting patterns.

It does not estimate:

- true infections;
- true attributable deaths;
- infection fatality risk;
- treatment effect;
- causal impact of public-health interventions.
