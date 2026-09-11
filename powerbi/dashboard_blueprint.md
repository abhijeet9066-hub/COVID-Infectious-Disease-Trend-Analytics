# Power BI Dashboard Blueprint

## Page 1 — Global Surveillance Overview

Cards:
- countries represented
- total reported confirmed cases in selected filter context
- total reported confirmed deaths
- peak weekly cases per million
- peak weekly deaths per million

Visible note:

> Confirmed surveillance counts do not represent all infections or all COVID-19-attributable deaths.

## Page 2 — Country Weekly Trends

Line chart:
- axis: date
- legend: country
- value: weekly_cases_per_million

Optional second visual:
- weekly_deaths_per_million

Slicer:
- country
- year

## Page 3 — Four-Week Trend Monitor

Visuals:
- cases_4w_avg_per_million
- deaths_4w_avg_per_million
- cases_4w_change_pct
- deaths_4w_change_pct

This page describes historical reporting trends; it is not a forecast.

## Page 4 — Annual Burden & Peaks

Matrix:
- country
- year
- total reported cases
- total reported deaths
- average weekly cases/deaths per million
- peak weekly cases/deaths per million

## Page 5 — Country Peak Profile

Map/table:
- ISO code
- peak case rate
- peak case date
- peak death rate
- peak death date
- max four-week averages

## Page 6 — Data Quality & Limitations

Show:
- source attribution
- fixed 2020-01-05 to 2025-12-28 window
- retrieval timestamp
- reporting coverage
- missing-data policy
- historical revision caveat
- testing/reporting comparability caveat
