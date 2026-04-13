import os
import sys
import joblib
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pathlib import Path

# --- 1. CONFIGURATION DU MODÈLE ---
class PolarsPreprocessor:
    def fit(self, X, y=None): return self
    def transform(self, X): return X

sys.modules['__main__'].PolarsPreprocessor = PolarsPreprocessor

# --- 2. CONFIGURATION BASE DE DONNÉES (POSTGRESQL) ---
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PredictionLog(Base):
    __tablename__ = "predictions"
    __table_args__ = {"schema": "uml_p5"} 
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer)
    prediction_text = Column(String)
    probability = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# --- 3. MODÈLES DE DONNÉES (PYDANTIC) ---
class EmployeeData(BaseModel):
    id_employee: int
    age: int = Field(..., gt=17, lt=70)
    revenu_mensuel: float
    annee_experience_totale: int
    annees_dans_l_entreprise: int
    distance_domicile_travail: int
    augmentation_salaire_precedente_pourcentage: float
    statut_marital: str
    departement: str
    poste: str
    domaine_etude: str
    frequence_deplacement: str
    heure_supplementaires: str

class PredictionResponse(BaseModel):
    employee_id: int
    attrition_risk: str
    probability: str

# --- 4. INITIALISATION ET CHARGEMENT ---
app = FastAPI(title="TechNova Attrition API")
MODEL_PATH = Path(__file__).parent / "full_techNova_pipeline.pkl"
global_pipeline = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 5. ENDPOINTS ---
@app.get("/")
async def health():
    return {"status": "online", "model_loaded": global_pipeline is not None}

@app.post("/predict", response_model=PredictionResponse)
async def predict(data: EmployeeData, db: Session = Depends(get_db)):
    if global_pipeline is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    
    try:
        input_dict = data.model_dump()
        df = pd.DataFrame([input_dict])
        
        # Inférence
        prediction = global_pipeline.predict(df)[0]
        prob = float(global_pipeline.predict_proba(df)[0][1])
        risk = "High" if prediction == 1 else "Low"

        # Sauvegarde PostgreSQL
        log = PredictionLog(
            employee_id=input_dict["id_employee"],
            prediction_text=risk,
            probability=prob
        )
        db.add(log)
        db.commit()

        return {
            "employee_id": input_dict["id_employee"],
            "attrition_risk": risk,
            "probability": f"{prob:.2%}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))