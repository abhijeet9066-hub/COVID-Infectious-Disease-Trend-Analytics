-- Global COVID-19 Surveillance Trend Analytics

-- 1. Highest historical peak weekly confirmed case rates
SELECT
    country,
    iso_code,
    ROUND(peak_weekly_cases_per_million, 1) AS peak_cases_per_million,
    peak_cases_date
FROM country_period_summary
WHERE peak_weekly_cases_per_million IS NOT NULL
ORDER BY peak_weekly_cases_per_million DESC
LIMIT 25;

-- 2. Highest historical peak weekly confirmed death rates
SELECT
    country,
    iso_code,
    ROUND(peak_weekly_deaths_per_million, 2) AS peak_deaths_per_million,
    peak_deaths_date
FROM country_period_summary
WHERE peak_weekly_deaths_per_million IS NOT NULL
ORDER BY peak_weekly_deaths_per_million DESC
LIMIT 25;

-- 3. Annual trend for selected countries
SELECT
    country,
    year,
    ROUND(total_reported_cases, 0) AS reported_cases,
    ROUND(total_reported_deaths, 0) AS reported_deaths,
    ROUND(avg_weekly_cases_per_million, 1) AS avg_weekly_cases_per_million,
    ROUND(avg_weekly_deaths_per_million, 2) AS avg_weekly_deaths_per_million
FROM annual_country_summary
WHERE iso_code IN ('IND', 'USA', 'GBR', 'DEU', 'FRA', 'BRA', 'JPN')
ORDER BY year, country;

-- 4. Strongest observed four-week case-reporting increases
SELECT
    country,
    date,
    ROUND(cases_4w_avg_per_million, 1) AS cases_4w_avg_per_million,
    ROUND(cases_4w_change_pct, 1) AS cases_4w_change_pct
FROM weekly_country_trends
WHERE cases_4w_change_pct IS NOT NULL
ORDER BY cases_4w_change_pct DESC
LIMIT 50;

-- 5. Reporting coverage review
SELECT
    country,
    iso_code,
    observed_week_rows,
    expected_week_rows,
    ROUND(row_coverage_pct, 1) AS row_coverage_pct,
    first_observation_date,
    last_observation_date
FROM country_period_summary
ORDER BY row_coverage_pct ASC, country;
