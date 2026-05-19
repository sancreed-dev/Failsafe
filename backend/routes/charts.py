from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

try:
    from backend.utils.preprocess import CHART_DIR, load_data
    from backend.utils.shap_explainer import SHAP_IMAGE_PATH, explain_student, generate_shap
except ModuleNotFoundError:
    from utils.preprocess import CHART_DIR, load_data
    from utils.shap_explainer import SHAP_IMAGE_PATH, explain_student, generate_shap

router = APIRouter(tags=["charts"])

_NO_CACHE = {"Cache-Control": "no-cache, no-store, must-revalidate"}


@router.get("/charts/shap_summary.png")
def shap_summary_image():
    if not SHAP_IMAGE_PATH.exists():
        X, _, _ = load_data()
        generate_shap(X)

    if not SHAP_IMAGE_PATH.exists():
        raise HTTPException(status_code=404, detail="SHAP summary chart is not available")

    return FileResponse(
        SHAP_IMAGE_PATH,
        media_type="image/png",
        filename="shap_summary.png",
        headers=_NO_CACHE,
    )


@router.get("/charts/student_{student_id}_shap.png")
def student_shap_image(student_id: int):
    if student_id < 0:
        raise HTTPException(status_code=400, detail="Invalid student id")

    image_path = CHART_DIR / f"student_{student_id}_shap.png"
    if not image_path.exists():
        X, _, original = load_data()
        try:
            explain_student(X, original, student_id)
        except IndexError as exc:
            raise HTTPException(status_code=404, detail="Student not found") from exc

    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Student SHAP chart is not available")

    return FileResponse(
        image_path,
        media_type="image/png",
        filename=image_path.name,
        headers=_NO_CACHE,
    )
