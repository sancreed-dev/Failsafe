import json

from fastapi import APIRouter, Depends, Request

try:
    from backend.utils.auth import get_current_user
    from backend.utils.database import latest_snapshots
    from backend.models.predictor import predict_batch
    from backend.utils.preprocess import METRICS_PATH, load_data
    from backend.utils.public_url import get_public_api_base
except ModuleNotFoundError:
    from utils.auth import get_current_user
    from utils.database import latest_snapshots
    from models.predictor import predict_batch
    from utils.preprocess import METRICS_PATH, load_data
    from utils.public_url import get_public_api_base

router = APIRouter()


def _risk_counts(predictions):
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for pred in predictions:
        counts[pred["risk"]] += 1
    return counts


@router.get("/dashboard")
def dashboard(request: Request, user=Depends(get_current_user)):
    X, y, original = load_data()
    predictions = predict_batch(X)
    counts = _risk_counts(predictions)

    subject_summary = []
    for subject, subject_df in original.groupby("subject"):
        subject_indexes = list(subject_df.index)
        subject_preds = [predictions[i] for i in subject_indexes]
        subject_counts = _risk_counts(subject_preds)
        subject_summary.append(
            {
                "subject": subject,
                "students": len(subject_df),
                "high_risk": subject_counts["HIGH"],
                "medium_risk": subject_counts["MEDIUM"],
                "low_risk": subject_counts["LOW"],
                "average_grade": round(float(subject_df["G3"].mean()), 2),
                "average_absences": round(float(subject_df["absences"].mean()), 2),
            }
        )

    return {
        "students": len(X),
        "high_risk": counts["HIGH"],
        "medium": counts["MEDIUM"],
        "safe": counts["LOW"],
        "failure_rate": round(float(y.mean() * 100), 2),
        "average_grade": round(float(original["G3"].mean()), 2),
        "average_absences": round(float(original["absences"].mean()), 2),
        "risk_distribution": [
            {"name": "HIGH", "value": counts["HIGH"]},
            {"name": "MEDIUM", "value": counts["MEDIUM"]},
            {"name": "LOW", "value": counts["LOW"]},
        ],
        "subject_summary": subject_summary,
        "model_metrics": _load_model_metrics(),
        "snapshots": latest_snapshots(),
        "shap_url": f"{get_public_api_base(request)}/charts/shap_summary.png",
    }


@router.get("/faculty/analytics")
def faculty_analytics(user=Depends(get_current_user)):
    X, y, original = load_data()
    predictions = predict_batch(X)

    all_high_risk_students = [
        {
            "student": i,
            "subject": original.iloc[i]["subject"],
            "risk": pred["risk"],
            "probability": pred["probability"],
            "grade": int(original.iloc[i]["G3"]),
            "absences": int(original.iloc[i]["absences"]),
            "failures": int(original.iloc[i]["failures"]),
        }
        for i, pred in enumerate(predictions)
        if pred["risk"] == "HIGH"
    ]

    feature_averages = original[
        ["absences", "studytime", "failures", "G1", "G2", "G3"]
    ].mean()

    return {
        "total_students": len(original),
        "actual_failures": int(y.sum()),
        "predicted_high_risk": len(all_high_risk_students),
        "interventions_required": sum(
            1 for pred in predictions if pred["risk"] in {"HIGH", "MEDIUM"}
        ),
        "feature_averages": {
            key: round(float(value), 2) for key, value in feature_averages.items()
        },
        "high_risk_students": all_high_risk_students[:20],
    }


def _load_model_metrics():
    if not METRICS_PATH.exists():
        return {}
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
