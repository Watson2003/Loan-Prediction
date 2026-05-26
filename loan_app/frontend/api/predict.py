import json
from pathlib import Path

import joblib
import pandas as pd
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "loan_model.pkl"

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


def build_input(payload):
    input_data = {key: payload.get(key) for key in EXPECTED_FEATURES}
    return pd.DataFrame([input_data], columns=EXPECTED_FEATURES)


async def predict(request: Request) -> JSONResponse:
    try:
        data = await request.json()
        if not isinstance(data, dict):
            return JSONResponse({"error": "Request body must be a JSON object."}, status_code=400)

        input_df = build_input(data)
        model = load_model()
        raw_prediction = model.predict(input_df)
        probability = None
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(input_df)[0]
            probability = float(proba[1])

        decision = "Loan Approved" if int(raw_prediction[0]) == 1 else "Loan Not Approved"
        return JSONResponse(
            {
                "decision": decision,
                "probability": probability,
            }
        )
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


app = Starlette(
    debug=False,
    routes=[Route("/", predict, methods=["POST"])],
)
