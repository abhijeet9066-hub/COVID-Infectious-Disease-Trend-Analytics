# Data Dictionary

## Snapshot — `weekly_country_covid.csv`

| Field | Meaning |
|---|---|
| country | OWID entity/country name |
| iso_code | Three-letter country code retained from source |
| date | Retained Sunday observation date for the trailing-seven-day indicator |
| weekly_cases | Confirmed COVID-19 cases over the reported week |
| weekly_deaths | Confirmed COVID-19 deaths over the reported week |
| weekly_cases_per_million | Weekly confirmed cases per million people |
| weekly_deaths_per_million | Weekly confirmed deaths per million people |

Blank values indicate unavailable source observations, not zero.

## Processed — `weekly_country_trends.csv`

Adds:

- `cases_4w_avg_per_million`
- `deaths_4w_avg_per_million`
- `cases_4w_change_pct`
- `deaths_4w_change_pct`

## Processed — `annual_country_summary.csv`

| Field | Meaning |
|---|---|
| total_reported_cases | Sum of available weekly confirmed case values in that country-year |
| total_reported_deaths | Sum of available weekly confirmed death values in that country-year |
| case_reporting_weeks | Weeks with a case count value |
| death_reporting_weeks | Weeks with a death count value |
| avg_weekly_cases_per_million | Mean of available weekly case-rate observations |
| avg_weekly_deaths_per_million | Mean of available weekly death-rate observations |
| peak_weekly_cases_per_million | Maximum available weekly case rate |
| peak_weekly_deaths_per_million | Maximum available weekly death rate |

## Processed — `country_period_summary.csv`

Contains fixed-window totals, peaks, peak dates, maximum smoothed rates, first/last observation dates, observed week count and reporting coverage.
