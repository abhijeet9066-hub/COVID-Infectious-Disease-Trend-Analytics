import pandas as pd
from pathlib import Path
import yaml
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parents[1]
config = yaml.safe_load(open(ROOT / "config" / "config.yaml", encoding="utf-8"))

input_path = ROOT / "data" / "processed" / "stage_raw_standardized.csv"
output_path = ROOT / config["processed_data_path"]
db_path = ROOT / config["database_path"]

df = pd.read_csv(input_path)

# Basic cleaning
df = df.drop_duplicates()
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].astype(str).str.strip()

# Missing value handling
for col in df.columns:
    if df[col].dtype == "object":
        df[col] = df[col].replace({"nan": None, "": None})
    else:
        df[col] = df[col].fillna(df[col].median())

df.to_csv(output_path, index=False)

engine = create_engine(f"sqlite:///{db_path}")
df.to_sql("fact_main", engine, if_exists="replace", index=False)

print(f"Clean data saved: {output_path}")
print(f"SQLite database saved: {db_path}")
