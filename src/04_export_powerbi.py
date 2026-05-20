import pandas as pd
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
config = yaml.safe_load(open(ROOT / "config" / "config.yaml", encoding="utf-8"))

df = pd.read_csv(ROOT / config["processed_data_path"])
out = ROOT / "data" / "processed" / "powerbi_fact_main.csv"
df.to_csv(out, index=False)

# Data dictionary for Power BI
dictionary = pd.DataFrame({
    "column": df.columns,
    "dtype": [str(df[c].dtype) for c in df.columns],
    "business_description": ["Update description" for _ in df.columns]
})
dictionary.to_csv(ROOT / "powerbi" / "data_dictionary.csv", index=False)

print(f"Power BI fact table exported: {out}")
