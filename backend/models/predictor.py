import joblib

try:
    from backend.utils.preprocess import MODEL_PATH
except ModuleNotFoundError:
    from utils.preprocess import MODEL_PATH

_model = None


def load_model(force: bool = False):
    global _model
    if force or _model is None:
        if not MODEL_PATH.exists():
            try:
                from backend.models.train_model import train_and_save_model
            except ModuleNotFoundError:
                from models.train_model import train_and_save_model

            train_and_save_model()
        _model = joblib.load(MODEL_PATH)
    return _model


def risk_label(probability: float) -> str:
    if probability >= 0.7:
        return "HIGH"
    if probability >= 0.35:
        return "MEDIUM"
    return "LOW"


def predict_student(df):
    model = load_model()
    probability = float(model.predict_proba(df)[0][1])

    return {
        "probability": round(probability, 3),
        "risk": risk_label(probability),
    }


def predict_batch(df):
    model = load_model()
    probabilities = model.predict_proba(df)[:, 1]
    return [
        {
            "probability": round(float(probability), 3),
            "risk": risk_label(float(probability)),
        }
        for probability in probabilities
    ]
