from datetime import datetime
from pathlib import Path
import json
from typing import Dict, List

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, ValidationError, validator

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "loan_model.pkl"
DATA_PATH = BASE_DIR / "data" / "test.csv"
LOG_PATH = BASE_DIR / "prediction_log.txt"

# Load the test data to infer the exact training feature order.
raw_data = pd.read_csv(DATA_PATH)
EXPECTED_FEATURES = [column for column in raw_data.columns if column != "Loan_ID"]

# Dataset-based category lists for validation and form options.
CATEGORICAL_OPTIONS: Dict[str, List[str]] = {
    "Gender": ["Male", "Female"],
    "Married": ["No", "Yes"],
    "Dependents": ["0", "1", "2", "3+"],
    "Education": ["Graduate", "Not Graduate"],
    "Self_Employed": ["No", "Yes"],
    "Credit_History": ["0", "1"],
    "Property_Area": ["Rural", "Semiurban", "Urban"],
}

NUMERIC_FEATURES = [
    "ApplicantIncome",
    "CoapplicantIncome",
    "LoanAmount",
    "Loan_Amount_Term",
]

app = FastAPI(title="Loan Approval Prediction API")

# Enable CORS for local frontend development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


class LoanRequest(BaseModel):
    Gender: str = Field(...)
    Married: str = Field(...)
    Dependents: str = Field(...)
    Education: str = Field(...)
    Self_Employed: str = Field(...)
    ApplicantIncome: float = Field(..., ge=0)
    CoapplicantIncome: float = Field(..., ge=0)
    LoanAmount: float = Field(..., gt=0)
    Loan_Amount_Term: float = Field(..., gt=0)
    Credit_History: float = Field(...)
    Property_Area: str = Field(...)

    @validator("Gender")
    def validate_gender(cls, value: str) -> str:
        if value not in CATEGORICAL_OPTIONS["Gender"]:
            raise ValueError("Gender must be Male or Female.")
        return value

    @validator("Married")
    def validate_married(cls, value: str) -> str:
        if value not in CATEGORICAL_OPTIONS["Married"]:
            raise ValueError("Married must be Yes or No.")
        return value

    @validator("Dependents")
    def validate_dependents(cls, value: str) -> str:
        if value not in CATEGORICAL_OPTIONS["Dependents"]:
            raise ValueError("Dependents must be 0, 1, 2 or 3+.")
        return value

    @validator("Education")
    def validate_education(cls, value: str) -> str:
        if value not in CATEGORICAL_OPTIONS["Education"]:
            raise ValueError("Education must be Graduate or Not Graduate.")
        return value

    @validator("Self_Employed")
    def validate_self_employed(cls, value: str) -> str:
        if value not in CATEGORICAL_OPTIONS["Self_Employed"]:
            raise ValueError("Self Employed must be Yes or No.")
        return value

    @validator("Credit_History")
    def validate_credit_history(cls, value: float) -> float:
        if int(value) not in {0, 1}:
            raise ValueError("Credit History must be 0 or 1.")
        return float(int(value))

    @validator("Property_Area")
    def validate_property_area(cls, value: str) -> str:
        if value not in CATEGORICAL_OPTIONS["Property_Area"]:
            raise ValueError("Property Area must be Rural, Semiurban or Urban.")
        return value


def load_model() -> object:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


MODEL = load_model()
MODEL_SUPPORTS_PROBA = hasattr(MODEL, "predict_proba")


def build_input_dataframe(data: Dict[str, object]) -> pd.DataFrame:
    # Build a single-row dataframe in the exact feature order.
    model_input = {key: data[key] for key in EXPECTED_FEATURES}
    input_df = pd.DataFrame([model_input], columns=EXPECTED_FEATURES)
    if list(input_df.columns) != EXPECTED_FEATURES:
        raise ValueError("Input features do not match training features exactly.")
    return input_df


def make_prediction(input_df: pd.DataFrame) -> Dict[str, object]:
    # Ensure returned values are native Python types (not numpy types)
    raw_prediction = MODEL.predict(input_df)
    raw_pred_int = int(raw_prediction[0])
    approved = bool(raw_pred_int == 1)
    probability = None
    if MODEL_SUPPORTS_PROBA:
        proba = MODEL.predict_proba(input_df)[0]
        probability = float(proba[1])
    return {
        "approved": approved,
        "probability": probability,
        "raw_prediction": raw_pred_int,
    }


def log_prediction(inputs: Dict[str, object], prediction: Dict[str, object]) -> None:
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "input": inputs,
        "prediction": prediction,
    }
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(entry) + "\n")


def get_form_context(request: Request, message: str = "", error: str = "", result: Dict[str, object] | None = None):
    return {
        "request": request,
        "options": CATEGORICAL_OPTIONS,
        "result": result,
        "message": message,
        "error": error,
    }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", get_form_context(request))


@app.post("/predict", response_model=None)
async def predict(request: Request):
    content_type = request.headers.get("content-type", "")
    try:
        if "application/json" in content_type:
            payload = await request.json()
        else:
            form_data = await request.form()
            payload = {key: value for key, value in form_data.items()}
        payload = {key: payload[key] for key in EXPECTED_FEATURES}
        loan_request = LoanRequest.parse_obj(payload)
        input_df = build_input_dataframe(loan_request.model_dump())
        prediction = make_prediction(input_df)
        log_prediction(loan_request.model_dump(), prediction)
        message = "Loan Approved" if prediction["approved"] else "Loan Not Approved"
        result = {
            "decision": message,
            "probability": prediction["probability"],
        }
    except ValidationError as validation_error:
        errors = validation_error.errors()
        error_message = ", ".join([f"{err['loc'][0]}: {err['msg']}" for err in errors])
        if "application/json" in content_type:
            raise HTTPException(status_code=400, detail=error_message)
        return templates.TemplateResponse(
            "index.html",
            get_form_context(request, error=error_message),
        )
    except KeyError as missing_key:
        error_message = f"Missing feature: {missing_key.args[0]}"
        if "application/json" in content_type:
            raise HTTPException(status_code=400, detail=error_message)
        return templates.TemplateResponse("index.html", get_form_context(request, error=error_message))
    except Exception as exc:
        if "application/json" in content_type:
            raise HTTPException(status_code=500, detail=str(exc))
        return templates.TemplateResponse(
            "index.html",
            get_form_context(request, error=str(exc)),
        )

    if "application/json" in content_type:
        return JSONResponse(content=result)

    return templates.TemplateResponse(
        "index.html",
        get_form_context(request, message=result["decision"], result=result),
    )


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "model": str(MODEL_PATH.name)}
