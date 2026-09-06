import os
import json
import logging
from datetime import datetime, timezone
from typing import Union

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Heart Disease Prediction API", version="1.0.0")

# Setup Logging for GCP Cloud Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("heart_disease_api")

try:
    import google.cloud.logging
    client = google.cloud.logging.Client()
    client.setup_logging()
    logger.info("GCP Cloud Logging initialized.")
except Exception as e:
    logger.info(f"Using stdout structured logging: {e}")

MODEL_PATH = os.getenv("MODEL_PATH", "model.pkl")
model = None

@app.on_event("startup")
def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        logger.info(f"Model loaded successfully from {MODEL_PATH}")
    else:
        logger.error(f"Model not found at {MODEL_PATH}")

class HeartDiseaseInput(BaseModel):
    sno: float = 0.0
    age: float
    gender: Union[int, str]
    cp: float
    trestbps: float
    chol: float
    fbs: float
    restecg: float
    thalach: float
    exang: float
    oldpeak: float
    slope: float
    ca: float
    thal: float

@app.get("/health")
def health():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy"}

@app.post("/predict")
def predict(payload: HeartDiseaseInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Model artifact unavailable")

    raw_dict = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()

    # Map categorical gender if received as string (male: 0, female: 1)
    gender_val = raw_dict["gender"]
    if isinstance(gender_val, str):
        processed_gender = 0 if gender_val.strip().lower() == "male" else 1
    else:
        processed_gender = int(gender_val)

    feature_cols = [
        "sno", "age", "gender", "cp", "trestbps", "chol", "fbs",
        "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"
    ]
    row_data = {col: raw_dict[col] for col in feature_cols if col != "gender"}
    row_data["gender"] = processed_gender
    input_df = pd.DataFrame([row_data], columns=feature_cols)

    prediction = model.predict(input_df)[0]

    # Deliverable 5: Structured log entry for GCP Cloud Logging
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_features": raw_dict,
        "predicted_output": str(prediction)
    }
    logger.info(json.dumps(log_entry))

    return {"prediction": str(prediction), "status": "success"}