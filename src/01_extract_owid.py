from __future__ import annotations

from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone
import csv
import hashlib
import io
import json
import re

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "config.json").read_text(encoding="utf-8"))
SNAPSHOT = ROOT / "data" / "snapshot"
SNAPSHOT.mkdir(parents=True, exist_ok=True)

START = CONFIG["fixed_window_start"]
END = CONFIG["fixed_window_end"]
SOURCES = CONFIG["sources"]

ISO3 = re.compile(r"^[A-Z]{3}$")


def download(url: str) -> bytes:
    req = Request(
        url,
        headers={
            "User-Agent": "global-covid-trend-analytics-portfolio/1.0",
            "Accept": "text/csv,*/*;q=0.8",
        },
    )
    with urlopen(req, timeout=120) as response:
        return response.read()


def parse_metric(raw: bytes, metric_name: str):
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    fields = reader.fieldnames or []

    entity_col = "Entity" if "Entity" in fields else None
    code_col = "Code" if "Code" in fields else None
    date_col = "Day" if "Day" in fields else ("Date" if "Date" in fields else None)

    if not entity_col or not code_col or not date_col:
        raise RuntimeError(
            f"{metric_name}: expected Entity, Code and Day/Date columns; found {fields}"
        )

    value_candidates = [c for c in fields if c not in {entity_col, code_col, date_col}]
    if len(value_candidates) != 1:
        raise RuntimeError(
            f"{metric_name}: expected one value column; found {value_candidates}"
        )
    value_col = value_candidates[0]

    out = {}
    for row in reader:
        code = (row.get(code_col) or "").strip()
        day = (row.get(date_col) or "").strip()
        entity = (row.get(entity_col) or "").strip()

        if not ISO3.fullmatch(code):
            continue
        if not (START <= day <= END):
            continue

        # OWID's indicator is a trailing 7-day total. Retain Sundays only so
        # consecutive observations represent non-overlapping weekly windows
        # rather than summing overlapping daily 7-day values.
        try:
            if datetime.fromisoformat(day).weekday() != 6:
                continue
        except ValueError:
            continue

        raw_value = (row.get(value_col) or "").strip()
        value = None
        if raw_value != "":
            try:
                value = float(raw_value)
            except ValueError:
                continue

        out[(entity, code, day)] = value

    return out, value_col


def fmt(value):
    if value is None:
        return ""
    if float(value).is_integer():
        return str(int(value))
    return f"{float(value):.6f}".rstrip("0").rstrip(".")


def main() -> None:
    print(f"Fixed historical window: {START} to {END}")
    print(f"Source series: {len(SOURCES)}")

    datasets = {}
    source_meta = {}

    for i, (metric, url) in enumerate(SOURCES.items(), start=1):
        print(f"[{i}/{len(SOURCES)}] Downloading {metric}...")
        raw = download(url)
        parsed, value_col = parse_metric(raw, metric)
        datasets[metric] = parsed
        source_meta[metric] = {
            "url": url,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "downloaded_bytes": len(raw),
            "detected_value_column": value_col,
            "retained_country_date_rows": len(parsed),
        }

    keys = sorted(set().union(*(d.keys() for d in datasets.values())), key=lambda x: (x[1], x[2], x[0]))

    if not keys:
        raise RuntimeError("No country-level records were retained.")

    out_path = SNAPSHOT / "weekly_country_covid.csv"
    fields = [
        "country",
        "iso_code",
        "date",
        "weekly_cases",
        "weekly_deaths",
        "weekly_cases_per_million",
        "weekly_deaths_per_million",
    ]

    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for entity, code, day in keys:
            w.writerow(
                {
                    "country": entity,
                    "iso_code": code,
                    "date": day,
                    "weekly_cases": fmt(datasets["weekly_cases"].get((entity, code, day))),
                    "weekly_deaths": fmt(datasets["weekly_deaths"].get((entity, code, day))),
                    "weekly_cases_per_million": fmt(
                        datasets["weekly_cases_per_million"].get((entity, code, day))
                    ),
                    "weekly_deaths_per_million": fmt(
                        datasets["weekly_deaths_per_million"].get((entity, code, day))
                    ),
                }
            )

    countries = sorted({k[1] for k in keys})
    metadata = {
        "project": CONFIG["project"],
        "source_attribution": "World Health Organization data processed/published by Our World in Data",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "fixed_window_start": START,
        "fixed_window_end": END,
        "sources": source_meta,
        "snapshot_rows": len(keys),
        "country_count": len(countries),
        "country_filter": "Code matches ^[A-Z]{3}$",
        "sampling_rule": "Retain Sunday observations only from trailing-7-day OWID indicators",
        "interpretation": (
            "Confirmed surveillance reporting data. Not all infections or all attributable deaths; "
            "not current 2026 conditions."
        ),
    }

    (SNAPSHOT / "extraction_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Country-level snapshot rows: {len(keys):,}")
    print(f"Countries retained: {len(countries):,}")
    print(f"Snapshot directory: {SNAPSHOT}")


if __name__ == "__main__":
    main()
