from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

app = FastAPI(
    title="Limi AI - Predictive Maintenance Engine",
    description="Predicts module overheating or failure every 5 minutes",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model artifacts
model = joblib.load("xgb_model.joblib")
scaler = joblib.load("scaler.joblib")
features = joblib.load("features.joblib")

class SensorReading(BaseModel):
    module_id: str
    voltage: float
    internal_temp: float
    usage_hours: float
    external_temp: float
    humidity: float
    load_percentage: float

class PredictionResult(BaseModel):
    module_id: str
    timestamp: str
    prediction: str
    failure_probability: float
    risk_level: str
    alert: bool
    recommended_action: str

@app.get("/")
def root():
    return {"status": "Limi AI Predictive Engine is running", "version": "1.0.0"}

@app.post("/predict", response_model=PredictionResult)
def predict_failure(reading: SensorReading):
    try:
        # Feature engineering (must match training)
        temp_diff = reading.internal_temp - reading.external_temp
        voltage_deviation = abs(reading.voltage - 220)
        heat_load_index = reading.internal_temp * reading.load_percentage / 100

        input_data = pd.DataFrame([[
            reading.voltage, reading.internal_temp, reading.usage_hours,
            reading.external_temp, reading.humidity, reading.load_percentage,
            temp_diff, voltage_deviation, heat_load_index
        ]], columns=features)

        scaled = scaler.transform(input_data)
        prob = model.predict_proba(scaled)[0][1]
        prediction = "FAILURE" if prob > 0.5 else "NORMAL"

        # Risk levels
        if prob < 0.3:
            risk = "LOW"
            action = "No action needed. Monitor as scheduled."
        elif prob < 0.6:
            risk = "MEDIUM"
            action = "Schedule inspection within 24 hours."
        else:
            risk = "HIGH"
            action = "IMMEDIATE inspection required. Dispatch technician."

        return PredictionResult(
            module_id=reading.module_id,
            timestamp=datetime.now().isoformat(),
            prediction=prediction,
            failure_probability=round(float(prob), 4),
            risk_level=risk,
            alert=(prob > 0.5),
            recommended_action=action
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/batch")
def predict_batch(readings: list[SensorReading]):
    return [predict_failure(r) for r in readings]

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
