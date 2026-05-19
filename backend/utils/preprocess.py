from pathlib import Path

import pandas as pd
from sklearn.preprocessing import LabelEncoder

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
CHART_DIR = OUTPUT_DIR / "charts"
REPORT_DIR = OUTPUT_DIR / "reports"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "model.pkl"
METRICS_PATH = MODEL_DIR / "metrics.json"
MERGED_DATA_PATH = DATA_DIR / "merged_students.csv"

MATH_FILENAME = "student-mat.csv"
POR_FILENAME = "student-por.csv"
PASSING_GRADE = 10

FEATURE_COLUMNS = [
    "school",
    "sex",
    "age",
    "address",
    "famsize",
    "Pstatus",
    "Medu",
    "Fedu",
    "Mjob",
    "Fjob",
    "reason",
    "guardian",
    "traveltime",
    "studytime",
    "failures",
    "schoolsup",
    "famsup",
    "paid",
    "activities",
    "nursery",
    "higher",
    "internet",
    "romantic",
    "famrel",
    "freetime",
    "goout",
    "Dalc",
    "Walc",
    "health",
    "absences",
    "G1",
    "G2",
    "subject",
]

FEATURE_LABELS = {
    "school": "School",
    "sex": "Student sex",
    "age": "Age",
    "address": "Home location",
    "famsize": "Family size",
    "Pstatus": "Parent cohabitation status",
    "Medu": "Mother education",
    "Fedu": "Father education",
    "Mjob": "Mother job",
    "Fjob": "Father job",
    "reason": "School choice reason",
    "guardian": "Guardian",
    "traveltime": "Travel time",
    "studytime": "Weekly study time",
    "failures": "Previous failures",
    "schoolsup": "School support",
    "famsup": "Family support",
    "paid": "Paid classes",
    "activities": "Extra activities",
    "nursery": "Nursery school",
    "higher": "Higher education ambition",
    "internet": "Internet access",
    "romantic": "Romantic relationship",
    "famrel": "Family relationship quality",
    "freetime": "Free time",
    "goout": "Going out",
    "Dalc": "Workday alcohol use",
    "Walc": "Weekend alcohol use",
    "health": "Health",
    "absences": "Absences",
    "G1": "First period grade",
    "G2": "Second period grade",
    "subject": "Subject",
}


def ensure_directories():
    for directory in (UPLOAD_DIR, CHART_DIR, REPORT_DIR, MODEL_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def _read_student_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset: {path.name}")
    return pd.read_csv(path, sep=";")


def merge_datasets(save: bool = True) -> pd.DataFrame:
    ensure_directories()

    math_df = _read_student_csv(UPLOAD_DIR / MATH_FILENAME)
    por_df = _read_student_csv(UPLOAD_DIR / POR_FILENAME)

    math_df["subject"] = "math"
    por_df["subject"] = "portuguese"

    merged = pd.concat([math_df, por_df], ignore_index=True)
    if save:
        merged.to_csv(MERGED_DATA_PATH, index=False)

    return merged


def encode_df(df: pd.DataFrame) -> pd.DataFrame:
    encoded = df.copy()
    encoded["G1"] = pd.to_numeric(encoded["G1"])
    encoded["G2"] = pd.to_numeric(encoded["G2"])
    encoded["G3"] = pd.to_numeric(encoded["G3"])
    encoded["risk"] = (encoded["G3"] < PASSING_GRADE).astype(int)
    encoded = encoded.drop(columns=["G3"])

    for col in encoded.select_dtypes(include="object").columns:
        encoder = LabelEncoder()
        encoded[col] = encoder.fit_transform(encoded[col].astype(str))

    return encoded


def load_data():
    original = merge_datasets(save=True)
    encoded = encode_df(original)

    X = encoded[FEATURE_COLUMNS]
    y = encoded["risk"]

    return X, y, original
