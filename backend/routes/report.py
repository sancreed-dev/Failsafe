from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

try:
    from backend.utils.auth import get_current_user
    from backend.models.predictor import predict_batch
    from backend.utils.preprocess import REPORT_DIR, load_data
except ModuleNotFoundError:
    from utils.auth import get_current_user
    from models.predictor import predict_batch
    from utils.preprocess import REPORT_DIR, load_data

router = APIRouter()


@router.get("/report")
def report(user=Depends(get_current_user)):
    X, y, original = load_data()
    predictions = predict_batch(X)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "failsafe_report.pdf"

    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for prediction in predictions:
        counts[prediction["risk"]] += 1

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(report_path), pagesize=letter)
    items = [
        Paragraph("FAILSAFE Student Risk Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph(
            f"Summary generated for {user['name']} from uploaded UCI student performance datasets.",
            styles["BodyText"],
        ),
        Spacer(1, 16),
    ]

    summary = [
        ["Metric", "Value"],
        ["Total students", str(len(original))],
        ["Actual failures", str(int(y.sum()))],
        ["High risk predictions", str(counts["HIGH"])],
        ["Medium risk predictions", str(counts["MEDIUM"])],
        ["Low risk predictions", str(counts["LOW"])],
        ["Average final grade", f"{float(original['G3'].mean()):.2f}"],
        ["Average absences", f"{float(original['absences'].mean()):.2f}"],
    ]

    table = Table(summary, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    items.append(table)
    items.append(Spacer(1, 16))

    top_students = sorted(
        enumerate(predictions),
        key=lambda item: item[1]["probability"],
        reverse=True,
    )[:10]
    top_table = [["Student", "Subject", "Risk", "Probability", "Grade", "Absences"]]
    for index, prediction in top_students:
        row = original.iloc[index]
        top_table.append(
            [
                str(index),
                row["subject"],
                prediction["risk"],
                f"{prediction['probability']:.3f}",
                str(int(row["G3"])),
                str(int(row["absences"])),
            ]
        )

    items.append(Paragraph("Highest Priority Students", styles["Heading2"]))
    top = Table(top_table, hAlign="LEFT")
    top.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    items.append(top)

    doc.build(items)

    return FileResponse(
        path=str(report_path),
        media_type="application/pdf",
        filename="failsafe_report.pdf",
    )
