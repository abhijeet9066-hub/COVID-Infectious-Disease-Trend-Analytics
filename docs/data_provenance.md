# Data Provenance

## Primary analytical source

Our World in Data (OWID) downloadable COVID-19 chart data.

Underlying confirmed cases/deaths source: World Health Organization (WHO).

The current OWID documentation identifies WHO as the source for confirmed COVID-19 cases and deaths.

## Series

The extraction uses four OWID Grapher CSV endpoints:

- weekly confirmed COVID-19 cases;
- weekly confirmed COVID-19 deaths;
- weekly confirmed cases per million people;
- weekly confirmed deaths per million people.

Exact URLs are stored in `config/config.json` and copied into extraction metadata.

## Fixed analytical window

- Start: 2020-01-05
- End: 2025-12-28

The end date is historical by design. The project does not claim to describe current 2026 conditions.

## Reproducibility metadata

Each live extraction records:

- retrieval timestamp in UTC;
- source URL;
- SHA-256 checksum of the downloaded CSV bytes;
- downloaded byte count;
- detected value column;
- final snapshot row count;
- final country count.

See `data/snapshot/extraction_metadata.json`.

## Geographic scope

The extractor keeps rows whose `Code` field is an ISO-like three-letter uppercase alphabetic code.

OWID aggregate entities such as `OWID_WRL` are therefore excluded from the country-level warehouse.

## Dynamic-source caveat

Historical WHO/OWID surveillance data can be revised after initial publication.

A later rerun may therefore produce different historical values even when the analytical date window is unchanged.

The committed snapshot is the auditable data basis for CI and portfolio review.

## Weekly sampling rule

OWID defines the selected case/death indicators as cumulative counts over the previous week.

The extractor retains Sunday-dated observations only. This prevents overlapping trailing-seven-day observations from being summed as if they were independent weekly periods.

The fixed analysis window also begins and ends on Sundays.
