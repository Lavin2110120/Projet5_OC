import os
import sys
import joblib
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sklearn.base import BaseEstimator, TransformerMixin
from pathlib import Path

# --- 1. CONFIGURATION DU MODÈLE ---
class PolarsPreprocessor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X): return X

sys.modules['__main__'].PolarsPreprocessor = PolarsPreprocessor

# --- 2. MODÈLES DE DONNÉES ---
class PredictionResponse(BaseModel):
    employee_id: int
    attrition_risk: str
    probability: str

app = FastAPI(title="TechNova Attrition API", version="1.0.0")

# --- 3. CHARGEMENT DU MODÈLE (ROBUSTE) ---
MODEL_PATH = Path(__file__).parent / "full_techNova_pipeline.pkl"

def load_model():
    if not MODEL_PATH.exists():
        print(f"❌ FICHIER MANQUANT: {MODEL_PATH}")
        return None
    try:
        model = joblib.load(MODEL_PATH)
        print("✅ Modèle chargé avec succès.")
        return model
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return None

global_pipeline = load_model()

# --- 4. ENDPOINTS ---

@app.get("/", tags=["Système"])
async def health_check():
    return {
        "status": "online",
        "model_loaded": global_pipeline is not None,
        "python_version": sys.version
    }

@app.post("/predict", response_model=PredictionResponse, tags=["Prédiction"])
async def predict(data: Dict[str, Any]):  # Changement : On accepte un dictionnaire brut
    """
    Point d'entrée de prédiction. Accepte un JSON brut pour éviter les erreurs 422 de formatage.
    """
    if global_pipeline is None:
        raise HTTPException(status_code=503, detail="Modèle non disponible sur le serveur")
    
    try:
        # On s'assure que les données numériques sont au bon format pour éviter les crashs du modèle
        input_df = pd.DataFrame([data])
        
        # Inférence
        prediction = global_pipeline.predict(input_df)[0]
        probability = float(global_pipeline.predict_proba(input_df)[0][1])
        risk_label = "High" if prediction == 1 else "Low"

        return {
            "employee_id": int(data.get("id_employee", 0)),
            "attrition_risk": risk_label,
            "probability": f"{probability:.2%}"
        }
    except Exception as e:
        # On renvoie l'erreur réelle pour débugger dans Swagger
        raise HTTPException(status_code=400, detail=f"Erreur de traitement : {str(e)}")