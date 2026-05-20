import pandas as pd
from pathlib import Path
import yaml, joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

ROOT = Path(__file__).resolve().parents[1]
config = yaml.safe_load(open(ROOT / "config" / "config.yaml", encoding="utf-8"))

df = pd.read_csv(ROOT / config["processed_data_path"])
target = config.get("target_column", "target")

if target not in df.columns:
    # Creates a demo target only when no target exists.
    # Replace this with the true dataset target before publishing model results.
    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) == 0:
        raise ValueError("No numeric columns available to create demo target.")
    df[target] = (df[numeric_cols[0]] > df[numeric_cols[0]].median()).astype(int)

X = df.drop(columns=[target])
y = df[target].astype(int)

numeric_features = X.select_dtypes(include="number").columns.tolist()
categorical_features = X.select_dtypes(exclude="number").columns.tolist()

preprocess = ColumnTransformer(
    transformers=[
        ("num", SimpleImputer(strategy="median"), numeric_features),
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore"))
        ]), categorical_features),
    ]
)

model = Pipeline([
    ("preprocess", preprocess),
    ("classifier", RandomForestClassifier(n_estimators=250, random_state=42, class_weight="balanced"))
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y if y.nunique() == 2 else None
)

model.fit(X_train, y_train)
pred = model.predict(X_test)

report = classification_report(y_test, pred)
(ROOT / "reports").mkdir(exist_ok=True)
(ROOT / "reports" / "model_report.txt").write_text(report, encoding="utf-8")

if hasattr(model.named_steps["classifier"], "predict_proba") and y.nunique() == 2:
    proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, proba)
    with open(ROOT / "reports" / "model_report.txt", "a", encoding="utf-8") as f:
        f.write(f"\nROC_AUC: {auc:.4f}\n")

joblib.dump(model, ROOT / "models" / "model.joblib")
print(report)
print("Model saved to models/model.joblib")
