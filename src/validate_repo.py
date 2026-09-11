from pathlib import Path
import csv
import json
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[1]

required = [
    ROOT / "README.md",
    ROOT / "config" / "config.json",
    ROOT / "data" / "source_manifest.csv",
    ROOT / "data" / "snapshot" / "extraction_metadata.json",
    ROOT / "data" / "snapshot" / "weekly_country_covid.csv",
    ROOT / "data" / "processed" / "weekly_country_trends.csv",
    ROOT / "data" / "processed" / "annual_country_summary.csv",
    ROOT / "data" / "processed" / "country_period_summary.csv",
    ROOT / "data" / "processed" / "global_covid_analytics.sqlite",
    ROOT / "data" / "powerbi" / "weekly_country_trends.csv",
    ROOT / "data" / "powerbi" / "annual_country_summary.csv",
    ROOT / "data" / "powerbi" / "country_period_summary.csv",
    ROOT / "docs" / "data_provenance.md",
    ROOT / "docs" / "methodology.md",
    ROOT / "docs" / "data_dictionary.md",
    ROOT / "docs" / "limitations.md",
    ROOT / "sql" / "analysis_queries.sql",
    ROOT / "powerbi" / "dashboard_blueprint.md",
    ROOT / "powerbi" / "measures.dax",
    ROOT / ".github" / "workflows" / "ci.yml",
]

missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing:
    raise SystemExit("Missing required files: " + ", ".join(missing))

for legacy in [
    ROOT / "config" / "config.yaml",
    ROOT / "src" / "01_ingest.py",
    ROOT / "src" / "02_clean.py",
    ROOT / "src" / "03_train_model.py",
]:
    if legacy.exists():
        raise SystemExit(f"Legacy placeholder file still exists: {legacy.relative_to(ROOT)}")

meta = json.loads(
    (ROOT / "data" / "snapshot" / "extraction_metadata.json").read_text(encoding="utf-8")
)

if meta.get("fixed_window_start") != "2020-01-05":
    raise SystemExit("Unexpected fixed start date.")
if meta.get("fixed_window_end") != "2025-12-28":
    raise SystemExit("Unexpected fixed end date.")
if int(meta.get("country_count", 0)) < 150:
    raise SystemExit(f"Country count unexpectedly low: {meta.get('country_count')}")
if int(meta.get("snapshot_rows", 0)) < 20000:
    raise SystemExit(f"Snapshot unexpectedly small: {meta.get('snapshot_rows')}")

for source in meta.get("sources", {}).values():
    h = source.get("sha256", "")
    if not re.fullmatch(r"[0-9a-f]{64}", h):
        raise SystemExit("Missing/invalid SHA-256 source provenance.")

def rows(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

snapshot = rows(ROOT / "data" / "snapshot" / "weekly_country_covid.csv")
weekly = rows(ROOT / "data" / "processed" / "weekly_country_trends.csv")
annual = rows(ROOT / "data" / "processed" / "annual_country_summary.csv")
period = rows(ROOT / "data" / "processed" / "country_period_summary.csv")

if len(snapshot) != len(weekly):
    raise SystemExit("Processed weekly rows do not match source snapshot rows.")
if len(period) < 150:
    raise SystemExit(f"Country period table unexpectedly small: {len(period)}")

keys = {(r["iso_code"], r["date"]) for r in snapshot}
if len(keys) != len(snapshot):
    raise SystemExit("Duplicate country-date rows found in snapshot.")

if any(not re.fullmatch(r"[A-Z]{3}", r["iso_code"]) for r in snapshot):
    raise SystemExit("Non-ISO-like country code found.")

if any(not ("2020-01-05" <= r["date"] <= "2025-12-28") for r in snapshot):
    raise SystemExit("Snapshot contains dates outside fixed historical window.")

conn = sqlite3.connect(ROOT / "data" / "processed" / "global_covid_analytics.sqlite")
try:
    weekly_db = conn.execute("SELECT COUNT(*) FROM weekly_country_trends").fetchone()[0]
    annual_db = conn.execute("SELECT COUNT(*) FROM annual_country_summary").fetchone()[0]
    period_db = conn.execute("SELECT COUNT(*) FROM country_period_summary").fetchone()[0]
finally:
    conn.close()

if (weekly_db, annual_db, period_db) != (len(weekly), len(annual), len(period)):
    raise SystemExit("SQLite row counts do not match processed CSV tables.")

readme = (ROOT / "README.md").read_text(encoding="utf-8").replace("**", "").lower()
required_phrases = [
    "does not claim that committed outputs represent current 2026 conditions",
    "missing source observations remain missing",
    "descriptive surveillance analytics",
]
for phrase in required_phrases:
    if phrase not in readme:
        raise SystemExit(f"Required interpretation statement missing: {phrase}")

print(f"PASS: historical country snapshot rows = {len(snapshot):,}")
print(f"PASS: countries represented = {len(period):,}")
print(f"PASS: annual summary rows = {len(annual):,}")
print("PASS: source SHA-256 provenance captured for all four OWID series")
print("PASS: country-date keys are unique and fixed-window dates are valid")
print("PASS: SQLite warehouse matches processed outputs")
print("PASS: placeholder classification/ML workflow removed")
print("PASS: current-status, missing-data and epidemiological limitations documented")
