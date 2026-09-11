from pathlib import Path
import csv
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DB = PROCESSED / "global_covid_analytics.sqlite"

FILES = {
    "weekly_country_trends": PROCESSED / "weekly_country_trends.csv",
    "annual_country_summary": PROCESSED / "annual_country_summary.csv",
    "country_period_summary": PROCESSED / "country_period_summary.csv",
}


def load(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def n(v):
    return None if v == "" else float(v)


def main() -> None:
    for p in FILES.values():
        if not p.exists():
            raise FileNotFoundError(f"Missing {p}. Run src/02_build_metrics.py first.")

    weekly = load(FILES["weekly_country_trends"])
    annual = load(FILES["annual_country_summary"])
    period = load(FILES["country_period_summary"])

    conn = sqlite3.connect(DB)
    try:
        conn.executescript(
            """
            DROP TABLE IF EXISTS weekly_country_trends;
            DROP TABLE IF EXISTS annual_country_summary;
            DROP TABLE IF EXISTS country_period_summary;

            CREATE TABLE weekly_country_trends (
                country TEXT,
                iso_code TEXT,
                date TEXT,
                weekly_cases REAL,
                weekly_deaths REAL,
                weekly_cases_per_million REAL,
                weekly_deaths_per_million REAL,
                cases_4w_avg_per_million REAL,
                deaths_4w_avg_per_million REAL,
                cases_4w_change_pct REAL,
                deaths_4w_change_pct REAL
            );

            CREATE TABLE annual_country_summary (
                country TEXT,
                iso_code TEXT,
                year INTEGER,
                total_reported_cases REAL,
                total_reported_deaths REAL,
                case_reporting_weeks INTEGER,
                death_reporting_weeks INTEGER,
                avg_weekly_cases_per_million REAL,
                avg_weekly_deaths_per_million REAL,
                peak_weekly_cases_per_million REAL,
                peak_weekly_deaths_per_million REAL
            );

            CREATE TABLE country_period_summary (
                country TEXT,
                iso_code TEXT,
                total_reported_cases REAL,
                total_reported_deaths REAL,
                peak_weekly_cases_per_million REAL,
                peak_cases_date TEXT,
                peak_weekly_deaths_per_million REAL,
                peak_deaths_date TEXT,
                max_cases_4w_avg_per_million REAL,
                max_deaths_4w_avg_per_million REAL,
                first_observation_date TEXT,
                last_observation_date TEXT,
                observed_week_rows INTEGER,
                expected_week_rows INTEGER,
                row_coverage_pct REAL
            );
            """
        )

        conn.executemany(
            "INSERT INTO weekly_country_trends VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            [
                (
                    r["country"], r["iso_code"], r["date"],
                    n(r["weekly_cases"]), n(r["weekly_deaths"]),
                    n(r["weekly_cases_per_million"]), n(r["weekly_deaths_per_million"]),
                    n(r["cases_4w_avg_per_million"]), n(r["deaths_4w_avg_per_million"]),
                    n(r["cases_4w_change_pct"]), n(r["deaths_4w_change_pct"]),
                )
                for r in weekly
            ],
        )

        conn.executemany(
            "INSERT INTO annual_country_summary VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            [
                (
                    r["country"], r["iso_code"], int(r["year"]),
                    n(r["total_reported_cases"]), n(r["total_reported_deaths"]),
                    int(r["case_reporting_weeks"]), int(r["death_reporting_weeks"]),
                    n(r["avg_weekly_cases_per_million"]), n(r["avg_weekly_deaths_per_million"]),
                    n(r["peak_weekly_cases_per_million"]), n(r["peak_weekly_deaths_per_million"]),
                )
                for r in annual
            ],
        )

        conn.executemany(
            "INSERT INTO country_period_summary VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            [
                (
                    r["country"], r["iso_code"],
                    n(r["total_reported_cases"]), n(r["total_reported_deaths"]),
                    n(r["peak_weekly_cases_per_million"]), r["peak_cases_date"],
                    n(r["peak_weekly_deaths_per_million"]), r["peak_deaths_date"],
                    n(r["max_cases_4w_avg_per_million"]), n(r["max_deaths_4w_avg_per_million"]),
                    r["first_observation_date"], r["last_observation_date"],
                    int(r["observed_week_rows"]), int(r["expected_week_rows"]),
                    n(r["row_coverage_pct"]),
                )
                for r in period
            ],
        )

        conn.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_weekly_iso_date
            ON weekly_country_trends (iso_code, date);

            CREATE INDEX IF NOT EXISTS idx_annual_iso_year
            ON annual_country_summary (iso_code, year);
            """
        )
        conn.commit()
    finally:
        conn.close()

    print(f"SQLite database: {DB}")
    print(f"weekly_country_trends rows: {len(weekly):,}")
    print(f"annual_country_summary rows: {len(annual):,}")
    print(f"country_period_summary rows: {len(period):,}")


if __name__ == "__main__":
    main()
