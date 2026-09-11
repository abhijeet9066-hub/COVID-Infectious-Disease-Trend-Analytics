from __future__ import annotations

from pathlib import Path
from collections import defaultdict
from datetime import date, timedelta
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "config.json").read_text(encoding="utf-8"))
SNAPSHOT = ROOT / "data" / "snapshot"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

START = CONFIG["fixed_window_start"]
END = CONFIG["fixed_window_end"]


def parse_num(value):
    text = (value or "").strip()
    return None if text == "" else float(text)


def fmt(value, decimals=6):
    if value is None:
        return ""
    return f"{value:.{decimals}f}".rstrip("0").rstrip(".")


def avg(values):
    if len(values) != 4 or any(v is None for v in values):
        return None
    return sum(values) / 4.0


def pct_change(current, previous):
    if current is None or previous is None or previous == 0:
        return None
    return ((current - previous) / previous) * 100.0


def expected_weeks(start_s, end_s):
    start = date.fromisoformat(start_s)
    end = date.fromisoformat(end_s)
    count = 0
    d = start
    while d <= end:
        count += 1
        d += timedelta(days=7)
    return count


def main() -> None:
    src = SNAPSHOT / "weekly_country_covid.csv"
    if not src.exists():
        raise FileNotFoundError("Run src/01_extract_owid.py first.")

    groups = defaultdict(list)
    with src.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            groups[(r["country"], r["iso_code"])].append(
                {
                    "country": r["country"],
                    "iso_code": r["iso_code"],
                    "date": r["date"],
                    "weekly_cases": parse_num(r["weekly_cases"]),
                    "weekly_deaths": parse_num(r["weekly_deaths"]),
                    "weekly_cases_per_million": parse_num(r["weekly_cases_per_million"]),
                    "weekly_deaths_per_million": parse_num(r["weekly_deaths_per_million"]),
                }
            )

    trend_rows = []
    annual_acc = defaultdict(list)
    period_rows = []
    exp_weeks = expected_weeks(START, END)

    for (country, code), rows in sorted(groups.items(), key=lambda x: x[0][1]):
        rows.sort(key=lambda r: r["date"])

        case_pm_hist = []
        death_pm_hist = []
        observed_dates = []

        for r in rows:
            case_pm_hist.append(r["weekly_cases_per_million"])
            death_pm_hist.append(r["weekly_deaths_per_million"])
            observed_dates.append(r["date"])

            current_case_4 = avg(case_pm_hist[-4:])
            previous_case_4 = avg(case_pm_hist[-8:-4]) if len(case_pm_hist) >= 8 else None
            current_death_4 = avg(death_pm_hist[-4:])
            previous_death_4 = avg(death_pm_hist[-8:-4]) if len(death_pm_hist) >= 8 else None

            tr = {
                **r,
                "cases_4w_avg_per_million": current_case_4,
                "deaths_4w_avg_per_million": current_death_4,
                "cases_4w_change_pct": pct_change(current_case_4, previous_case_4),
                "deaths_4w_change_pct": pct_change(current_death_4, previous_death_4),
            }
            trend_rows.append(tr)
            annual_acc[(country, code, int(r["date"][:4]))].append(tr)

        def available(vals):
            return [v for v in vals if v is not None]

        case_vals = available([r["weekly_cases"] for r in rows])
        death_vals = available([r["weekly_deaths"] for r in rows])
        case_pm = available([r["weekly_cases_per_million"] for r in rows])
        death_pm = available([r["weekly_deaths_per_million"] for r in rows])

        case_peak_row = max(
            (r for r in rows if r["weekly_cases_per_million"] is not None),
            key=lambda x: x["weekly_cases_per_million"],
            default=None,
        )
        death_peak_row = max(
            (r for r in rows if r["weekly_deaths_per_million"] is not None),
            key=lambda x: x["weekly_deaths_per_million"],
            default=None,
        )

        country_trends = [r for r in trend_rows if r["iso_code"] == code]
        max_case_4 = max(
            (r["cases_4w_avg_per_million"] for r in country_trends if r["cases_4w_avg_per_million"] is not None),
            default=None,
        )
        max_death_4 = max(
            (r["deaths_4w_avg_per_million"] for r in country_trends if r["deaths_4w_avg_per_million"] is not None),
            default=None,
        )

        period_rows.append(
            {
                "country": country,
                "iso_code": code,
                "total_reported_cases": sum(case_vals) if case_vals else None,
                "total_reported_deaths": sum(death_vals) if death_vals else None,
                "peak_weekly_cases_per_million": None if case_peak_row is None else case_peak_row["weekly_cases_per_million"],
                "peak_cases_date": "" if case_peak_row is None else case_peak_row["date"],
                "peak_weekly_deaths_per_million": None if death_peak_row is None else death_peak_row["weekly_deaths_per_million"],
                "peak_deaths_date": "" if death_peak_row is None else death_peak_row["date"],
                "max_cases_4w_avg_per_million": max_case_4,
                "max_deaths_4w_avg_per_million": max_death_4,
                "first_observation_date": observed_dates[0],
                "last_observation_date": observed_dates[-1],
                "observed_week_rows": len(rows),
                "expected_week_rows": exp_weeks,
                "row_coverage_pct": (len(rows) / exp_weeks) * 100.0 if exp_weeks else None,
            }
        )

    trend_out = PROCESSED / "weekly_country_trends.csv"
    trend_fields = [
        "country", "iso_code", "date", "weekly_cases", "weekly_deaths",
        "weekly_cases_per_million", "weekly_deaths_per_million",
        "cases_4w_avg_per_million", "deaths_4w_avg_per_million",
        "cases_4w_change_pct", "deaths_4w_change_pct",
    ]
    with trend_out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=trend_fields)
        w.writeheader()
        for r in trend_rows:
            w.writerow({
                k: (fmt(r[k]) if isinstance(r[k], float) else r[k])
                for k in trend_fields
            })

    annual_rows = []
    for (country, code, year), rows in sorted(annual_acc.items(), key=lambda x: (x[0][1], x[0][2])):
        cases = available([r["weekly_cases"] for r in rows])
        deaths = available([r["weekly_deaths"] for r in rows])
        case_pm = available([r["weekly_cases_per_million"] for r in rows])
        death_pm = available([r["weekly_deaths_per_million"] for r in rows])

        annual_rows.append(
            {
                "country": country,
                "iso_code": code,
                "year": year,
                "total_reported_cases": sum(cases) if cases else None,
                "total_reported_deaths": sum(deaths) if deaths else None,
                "case_reporting_weeks": len(cases),
                "death_reporting_weeks": len(deaths),
                "avg_weekly_cases_per_million": (sum(case_pm) / len(case_pm)) if case_pm else None,
                "avg_weekly_deaths_per_million": (sum(death_pm) / len(death_pm)) if death_pm else None,
                "peak_weekly_cases_per_million": max(case_pm) if case_pm else None,
                "peak_weekly_deaths_per_million": max(death_pm) if death_pm else None,
            }
        )

    annual_out = PROCESSED / "annual_country_summary.csv"
    annual_fields = list(annual_rows[0].keys())
    with annual_out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=annual_fields)
        w.writeheader()
        for r in annual_rows:
            w.writerow({
                k: (fmt(r[k]) if isinstance(r[k], float) else r[k])
                for k in annual_fields
            })

    period_out = PROCESSED / "country_period_summary.csv"
    period_fields = list(period_rows[0].keys())
    with period_out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=period_fields)
        w.writeheader()
        for r in period_rows:
            w.writerow({
                k: (fmt(r[k]) if isinstance(r[k], float) else r[k])
                for k in period_fields
            })

    print(f"Weekly country trend rows: {len(trend_rows):,}")
    print(f"Annual summary rows: {len(annual_rows):,}")
    print(f"Country period summary rows: {len(period_rows):,}")


if __name__ == "__main__":
    main()
