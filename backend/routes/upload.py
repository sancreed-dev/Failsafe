from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

try:
    from backend.models.predictor import predict_batch
    from backend.models.predictor import load_model
    from backend.models.train_model import train_and_save_model
    from backend.utils.auth import get_current_user
    from backend.utils.database import save_prediction_snapshot
    from backend.utils.preprocess import MATH_FILENAME, POR_FILENAME, UPLOAD_DIR, load_data
    from backend.utils.shap_explainer import generate_shap
except ModuleNotFoundError:
    from models.predictor import predict_batch
    from models.predictor import load_model
    from models.train_model import train_and_save_model
    from utils.auth import get_current_user
    from utils.database import save_prediction_snapshot
    from utils.preprocess import MATH_FILENAME, POR_FILENAME, UPLOAD_DIR, load_data
    from utils.shap_explainer import generate_shap

router = APIRouter()

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def _save_upload(file: UploadFile, filename: str):
    if not file.filename or file.filename.lower() != filename:
        raise HTTPException(
            status_code=400,
            detail=f"Expected {filename}, received {file.filename or 'no file'}",
        )

    path = UPLOAD_DIR / filename
    content = await file.read()
    path.write_bytes(content)
    return path


@router.post("/upload")
async def upload_files(
    math_file: UploadFile = File(...),
    por_file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    await _save_upload(math_file, MATH_FILENAME)
    await _save_upload(por_file, POR_FILENAME)

    metrics = train_and_save_model()
    load_model(force=True)
    X, _, _ = load_data()
    generate_shap(X)
    predictions = predict_batch(X)
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for prediction in predictions:
        counts[prediction["risk"]] += 1
    save_prediction_snapshot(
        {
            "students": len(X),
            "high_risk": counts["HIGH"],
            "medium": counts["MEDIUM"],
            "safe": counts["LOW"],
        },
        metrics,
    )

    return {
        "status": "uploaded_and_trained",
        "uploaded_by": user["email"],
        "files": [MATH_FILENAME, POR_FILENAME],
        "rows": metrics["rows"],
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1": metrics["f1"],
        "shap_url": "/charts/shap_summary.png",
    }
