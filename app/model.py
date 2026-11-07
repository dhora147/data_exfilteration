from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from app.features import prepare_frame, BEHAVIOUR_COLUMNS

MODEL_PATH = Path("models/insider_email_model.joblib")
METRICS_PATH = Path("models/evaluation_metrics.json")

def build_pipeline():
    text_pipe = TfidfVectorizer(ngram_range=(1,2), max_features=12000, sublinear_tf=True, min_df=1)
    behaviour_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scale", StandardScaler())
    ])
    prep = ColumnTransformer([
        ("nlp", text_pipe, "text"),
        ("behaviour", behaviour_pipe, BEHAVIOUR_COLUMNS)
    ])
    return Pipeline([
        ("features", prep),
        ("classifier", LogisticRegression(max_iter=1500, class_weight="balanced", random_state=42))
    ])

def train(df):
    data = prepare_frame(df)
    if "label" not in data:
        raise ValueError("Training data must contain a label column (0=benign, 1=suspected exfiltration).")
    y = pd.to_numeric(data["label"], errors="coerce").fillna(0).astype(int)
    if y.nunique() < 2:
        raise ValueError("Training data must contain both label classes: 0 and 1.")
    X = data[["text"] + BEHAVIOUR_COLUMNS]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    pipe = build_pipeline()
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)
    proba = pipe.predict_proba(X_test)[:, 1]
    metrics = {
        "test_rows": int(len(y_test)),
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "precision": round(float(precision_score(y_test, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, proba)), 4) if y_test.nunique() == 2 else None,
        "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
        "classification_report": classification_report(y_test, pred, output_dict=True, zero_division=0)
    }
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    METRICS_PATH.write_text(__import__("json").dumps(metrics, indent=2))
    return pipe, metrics

def load_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)

def evaluate_metrics():
    if not METRICS_PATH.exists():
        return None
    import json
    return json.loads(METRICS_PATH.read_text())

def predict(df, model):
    data = prepare_frame(df)
    X = data[["text"] + BEHAVIOUR_COLUMNS]
    probabilities = model.predict_proba(X)[:, 1]
    result = data.copy()
    result["risk_score"] = probabilities
    result["prediction"] = (probabilities >= 0.5).astype(int)
    return result
