import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import shap

try:
    from backend.models.predictor import load_model
    from backend.utils.preprocess import CHART_DIR, FEATURE_LABELS
except ModuleNotFoundError:
    from models.predictor import load_model
    from utils.preprocess import CHART_DIR, FEATURE_LABELS

SHAP_IMAGE_PATH = CHART_DIR / "shap_summary.png"


def generate_shap(df):
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    model = load_model(force=True)
    sample = df.sample(min(len(df), 300), random_state=42)
    explainer = shap.TreeExplainer(model)
    values = explainer.shap_values(sample)

    shap.summary_plot(values, sample, show=False, plot_size=(10, 6))
    plt.tight_layout()
    plt.savefig(SHAP_IMAGE_PATH, bbox_inches="tight", dpi=160)
    plt.close()

    return str(SHAP_IMAGE_PATH)


def _student_values(df, student_index: int):
    if student_index < 0 or student_index >= len(df):
        raise IndexError("Student index out of range")

    model = load_model()
    row = df.iloc[[student_index]]
    explainer = shap.TreeExplainer(model)
    values = explainer.shap_values(row)
    values = values[0] if getattr(values, "ndim", 1) > 1 else values
    return row.iloc[0], values


def explain_student(df, original, student_index: int, top_n: int = 5):
    row, values = _student_values(df, student_index)
    original_row = original.iloc[student_index]

    ranked = sorted(
        zip(df.columns, values),
        key=lambda item: abs(float(item[1])),
        reverse=True,
    )[:top_n]

    reasons = []
    for feature, value in ranked:
        direction = "raises" if float(value) > 0 else "lowers"
        label = FEATURE_LABELS.get(feature, feature)
        raw_value = original_row[feature] if feature in original_row else row[feature]
        reasons.append(
            {
                "feature": feature,
                "label": label,
                "value": str(raw_value),
                "impact": round(float(value), 4),
                "direction": direction,
                "summary": f"{label} ({raw_value}) {direction} the predicted failure risk.",
            }
        )

    top_three = reasons[:3]
    narrative = "Main drivers: " + "; ".join(reason["summary"] for reason in top_three)
    image_path = CHART_DIR / f"student_{student_index}_shap.png"
    _save_student_chart(image_path, reasons)

    return {
        "student": student_index,
        "subject": original_row["subject"],
        "grade": int(original_row["G3"]),
        "top_reasons": reasons,
        "plain_english": narrative,
        "image_url": f"/charts/{image_path.name}",
    }


def _save_student_chart(image_path, reasons):
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    labels = [reason["label"] for reason in reasons][::-1]
    values = [reason["impact"] for reason in reasons][::-1]
    colors = ["#dc2626" if value > 0 else "#2563eb" for value in values]

    plt.figure(figsize=(8.5, 4.5))
    plt.barh(labels, values, color=colors)
    plt.axvline(0, color="#111827", linewidth=1)
    plt.title("Student-level SHAP contribution")
    plt.xlabel("Impact on failure-risk prediction")
    plt.tight_layout()
    plt.savefig(image_path, bbox_inches="tight", dpi=160)
    plt.close()
