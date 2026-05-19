from fastapi import APIRouter, Depends, HTTPException, Request

try:
    from backend.utils.auth import get_current_user
    from backend.models.predictor import predict_batch
    from backend.utils.interventions import create_plan
    from backend.utils.preprocess import load_data
    from backend.utils.public_url import get_public_api_base
    from backend.utils.shap_explainer import explain_student, generate_shap
except ModuleNotFoundError:
    from utils.auth import get_current_user
    from models.predictor import predict_batch
    from utils.interventions import create_plan
    from utils.preprocess import load_data
    from utils.public_url import get_public_api_base
    from utils.shap_explainer import explain_student, generate_shap

router = APIRouter()


@router.post("/predict")
def predict(user=Depends(get_current_user)):
    X, y, original = load_data()
    generate_shap(X)
    predictions = predict_batch(X)

    results = []

    for i, pred in enumerate(predictions):
        row = original.iloc[i]
        plan = create_plan(row)

        results.append({
            "student": i,
            "school": row["school"],
            "sex": row["sex"],
            "age": int(row["age"]),
            "subject": row["subject"],
            "risk": pred["risk"],
            "probability": pred["probability"],
            "grade": int(row["G3"]),
            "absences": int(row["absences"]),
            "failures": int(row["failures"]),
            "studytime": int(row["studytime"]),
            "actions": plan,
        })

    return results


@router.get("/students/{student_id}/explanation")
def student_explanation(student_id: int, request: Request, user=Depends(get_current_user)):
    X, _, original = load_data()
    predictions = predict_batch(X)

    try:
        explanation = explain_student(X, original, student_id)
    except IndexError as exc:
        raise HTTPException(status_code=404, detail="Student not found") from exc

    api_base = get_public_api_base(request)
    relative_image = explanation["image_url"]
    explanation["image_url"] = (
        relative_image
        if relative_image.startswith("http")
        else f"{api_base}{relative_image}"
    )
    explanation["prediction"] = predictions[student_id]
    explanation["actions"] = create_plan(original.iloc[student_id])
    return explanation
