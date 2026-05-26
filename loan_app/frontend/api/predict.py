import json
from pathlib import Path

import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "loan_model.pkl"

# Feature order must match training exactly.
EXPECTED_FEATURES = [
    "Gender",
    "Married",
    "Dependents",
    "Education",
    "Self_Employed",
    "ApplicantIncome",
    "CoapplicantIncome",
    "LoanAmount",
    "Loan_Amount_Term",
    "Credit_History",
    "Property_Area",
]

MODEL = None


def load_model():
    global MODEL
    if MODEL is None:
        MODEL = joblib.load(MODEL_PATH)
    return MODEL


def parse_body(request):
    if hasattr(request, "json"):
        data = request.json
        if callable(data):
            return data()
        return data

    if hasattr(request, "body"):
        body = request.body
        if callable(body):
            body = body()
        if isinstance(body, bytes):
            body = body.decode("utf-8")
        return json.loads(body)

    raise ValueError("No JSON body found in request.")


def build_input(payload):
    input_data = {key: payload.get(key) for key in EXPECTED_FEATURES}
    return pd.DataFrame([input_data], columns=EXPECTED_FEATURES)


def handler(request):
    try:
        data = parse_body(request)
        if not isinstance(data, dict):
            return {"error": "Request body must be a JSON object."}

        input_df = build_input(data)
        model = load_model()
        raw_prediction = model.predict(input_df)
        probability = None
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(input_df)[0]
            probability = float(proba[1])

        decision = "Loan Approved" if int(raw_prediction[0]) == 1 else "Loan Not Approved"
        return {
            "decision": decision,
            "probability": probability,
        }
    except Exception as exc:
        return {"error": str(exc)}


application = handler
app = handler
