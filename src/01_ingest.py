import pandas as pd
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
config = yaml.safe_load(open(ROOT / "config" / "config.yaml", encoding="utf-8"))

raw_path = ROOT / config["raw_data_path"]
processed_dir = ROOT / "data" / "processed"
processed_dir.mkdir(parents=True, exist_ok=True)

if not raw_path.exists():
    raise FileNotFoundError(
        f"Raw file not found: {raw_path}. Download the public dataset and place it in data/raw/input.csv"
    )

df = pd.read_csv(raw_path)
df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]
df.to_csv(processed_dir / "stage_raw_standardized.csv", index=False)
print(f"Loaded {len(df):,} rows and {len(df.columns):,} columns")
