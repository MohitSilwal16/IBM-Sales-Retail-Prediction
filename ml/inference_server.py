import joblib
import pandas as pd

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title="Local SageMaker Server")

MODEL_PATH = "ml/Formatted Car Sales.pkl"

# Load model at startup
bundle = joblib.load(MODEL_PATH)
model = bundle["model"]
le_encoders = bundle["encoders"]
attributes = bundle["attributes"]


# ---------- Request Schema ----------
class PredictionRequest(BaseModel):
    instances: List[Dict[str, Any]]


# ---------- Preprocessing ----------
def preprocess_input(df: pd.DataFrame) -> pd.DataFrame:
    df["date"] = pd.to_datetime(df["date"])

    df["day"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    df["day_of_week"] = df["date"].dt.day_of_week
    df["day_of_year"] = df["date"].dt.day_of_year
    df["quarter"] = df["date"].dt.quarter

    df.drop(columns=["date"], inplace=True)

    for col, encoder in le_encoders.items():
        df[col] = encoder.transform(df[col])

    return df


# ---------- Health Check ----------
@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.get("/attributes")
def get_attributes():
    return attributes


# ---------- Prediction Endpoint ----------
@app.post("/invocations")
def predict(request: PredictionRequest):
    print("Invocations Called YaML")
    df = pd.DataFrame(request.instances)
    print(df)

    # make sure date is not needed from original row
    row = df.iloc[0].copy()

    # create date range
    dates = pd.date_range("2023-12-01", "2023-12-31", freq="D")

    # repeat row for each date
    df = pd.DataFrame([row] * len(dates))

    # assign new dates
    df["date"] = dates

    try:
        df_processed = preprocess_input(df)
        preds = model.predict(df_processed)
        preds = [round(float(p)) for p in preds]
        preds = sum(preds)

        print(preds)
        return {"predictions": preds}

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}