import os

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.ensemble import RandomForestClassifier

app = FastAPI(title="Jabodetabek Campus GIS ML API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model cache
_rf_model = None

def get_model():
    global _rf_model
    if _rf_model is None:
        csv_path = os.path.join(os.path.dirname(__file__), "..", "data_ready", "kecamatan_predictions.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            feature_cols = ["dist_ind", "camp_dens", "toll_pct", "sma_grad", "area_km2"]
            X = df[feature_cols].values
            y = df["Label_Reko"].values
            rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=6)
            rf.fit(X, y)
            _rf_model = rf
    return _rf_model

class PredictRequest(BaseModel):
    dist_ind: float
    camp_dens: float
    toll_pct: float
    sma_grad: float
    area_km2: float

@app.get("/")
@app.get("/api")
@app.get("/health")
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "Jabodetabek Campus GIS & ML API",
        "documentation": "FastAPI Random Forest Model Serverless Service"
    }

@app.post("/predict")
@app.post("/api/predict")
def predict(req: PredictRequest):
    model = get_model()
    if model is None:
        return {"error": "Model could not be loaded"}
    
    features = [[req.dist_ind, req.camp_dens, req.toll_pct, req.sma_grad, req.area_km2]]
    pred = int(model.predict(features)[0])
    probs = model.predict_proba(features)[0].tolist()
    
    labels = {
        0: "Tidak Direkomendasikan",
        1: "Cukup Direkomendasikan",
        2: "Sangat Direkomendasikan"
    }
    
    return {
        "prediction": pred,
        "label": labels.get(pred, "Unknown"),
        "probabilities": {
            "tidak_direkomendasikan": probs[0] if len(probs) > 0 else 0,
            "cukup_direkomendasikan": probs[1] if len(probs) > 1 else 0,
            "sangat_direkomendasikan": probs[2] if len(probs) > 2 else 0
        }
    }
