import json

import joblib
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

try:
    from backend.utils.preprocess import METRICS_PATH, MODEL_PATH, load_data
except ModuleNotFoundError:
    from utils.preprocess import METRICS_PATH, MODEL_PATH, load_data


def train_and_save_model():
    X, y, original = load_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = XGBClassifier(
        n_estimators=160,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
        random_state=42,
    )

    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, pred)
    precision = precision_score(y_test, pred, zero_division=0)
    recall = recall_score(y_test, pred, zero_division=0)
    f1 = f1_score(y_test, pred, zero_division=0)
    matrix = confusion_matrix(y_test, pred).tolist()

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    metrics = {
        "model_path": str(MODEL_PATH),
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "confusion_matrix": matrix,
        "rows": len(X),
        "features": list(X.columns),
        "subjects": original["subject"].value_counts().to_dict(),
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


if __name__ == "__main__":
    metrics = train_and_save_model()
    print(f"Accuracy: {metrics['accuracy']}")
