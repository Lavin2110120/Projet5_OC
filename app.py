import os
import sys
import joblib
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL
from sklearn.base import BaseEstimator, TransformerMixin
from pathlib import Path

# --- 1. CONFIGURATION DU MODÈLE (PRÉ-REQUIS) ---
class PolarsPreprocessor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X): return X

sys.modules['__main__'].PolarsPreprocessor = PolarsPreprocessor

# --- 2. DOCUMENTATION DES MODÈLES DE DONNÉES (PYDANTIC) ---
class EmployeeData(BaseModel):
    """Schéma des données requises pour une prédiction d'attrition."""
    id_employee: int = Field(..., description="Identifiant unique de l'employé", example=1)
    age: int = Field(..., gt=17, lt=70, description="Âge de l'employé", example=41)
    revenu_mensuel: float = Field(..., description="Salaire mensuel brut", example=5993.0)
    annee_experience_totale: int = Field(..., description="Nombre d'années d'expérience au total", example=8)
    annees_dans_l_entreprise: int = Field(..., description="Ancienneté dans la société actuelle", example=6)
    distance_domicile_travail: int = Field(..., description="Distance en km", example=1)
    augmentation_salaire_precedente_pourcentage: float = Field(..., example=11.0)
    statut_marital: str = Field(..., description="Célibataire, Marié ou Divorcé", example="Célibataire")
    departement: str = Field(..., example="Commercial")
    poste: str = Field(..., example="Cadre Commercial")
    domaine_etude: str = Field(..., example="Infra & Cloud")
    frequence_deplacement: str = Field(..., example="Occasionnel")
    heure_supplementaires: str = Field(..., description="Oui ou Non", example="Oui")

class PredictionResponse(BaseModel):
    """Format de la réponse renvoyée par l'API."""
    employee_id: int
    attrition_risk: str = Field(..., description="Niveau de risque (High/Low)")
    probability: str = Field(..., description="Probabilité formatée en pourcentage")

# --- 3. INITIALISATION DE L'API ---
app = FastAPI(
    title="TechNova Attrition API",
    description="""
    API de prédiction du risque de départ des employés (Attrition).
    Cette API utilise un modèle Random Forest et enregistre chaque prédiction en base de données pour assurer la traçabilité.
    """,
    version="1.0.0",
    contact={
        "name": "Équipe Data TechNova",
        "url": "https://github.com/Lavin2110120/Projet5_OC",
    }
)

# --- 4. CHARGEMENT ENV ET BASE DE DONNÉES ---
load_dotenv() 
engine = None
SessionLocal = None
Base = declarative_base()

class PredictionLog(Base):
    __tablename__ = "predictions"
    __table_args__ = {"schema": "uml_p5"} 

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer)
    prediction_text = Column(String)
    probability = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# --- 5. CHARGEMENT DU MODÈLE ---
def load_model():
    #try:
        path = __file__.replace("app.py","full_techNova_pipeline.pkl")
        print(path)
        model = joblib.load(path)
        print("✅ Modèle chargé avec succès.")
        return model
    #except Exception as e:
        # print(f"❌ Erreur chargement modèle : {e}")
        # return None

global_pipeline = load_model()

FEATURES_ORDER = [
    "age", "revenu_mensuel", "annee_experience_totale", 
    "annees_dans_l_entreprise", "distance_domicile_travail",
    "augmentation_salaire_precedente_pourcentage", "statut_marital", 
    "departement", "poste", "domaine_etude", 
    "frequence_deplacement", "heure_supplementaires"
]

# --- 6. ENDPOINTS ---

@app.get("/", tags=["Système"])
async def health_check():
    """
    Vérifie l'état de santé de l'API.
    Retourne l'état de la connexion à la base de données et la disponibilité du modèle.
    """
    return {
        "status": "online",
        "model_loaded": global_pipeline is not None,
        "database_connected": engine is not None
    }

@app.post("/predict", 
          response_model=PredictionResponse, 
          tags=["Prédiction"],
          summary="Calculer le risque d'attrition")
async def predict(data: EmployeeData = Body(...)):
    """
    Effectue une prédiction d'attrition pour un employé spécifique.
    
    - **Analyse** : Le modèle traite les données socio-professionnelles.
    - **Traçabilité** : Le résultat est stocké automatiquement dans la table `predictions`.
    - **Résultat** : Retourne un label (High/Low) et une probabilité.
    """
    if global_pipeline is None:
        raise HTTPException(status_code=503, detail="Modèle non disponible")
    
    try:
        # Conversion de l'objet Pydantic en DataFrame
        input_dict = data.model_dump()
        df = pd.DataFrame([input_dict])
        
        # Inférence
        prediction = global_pipeline.predict(df)[0]
        probability = float(global_pipeline.predict_proba(df)[0][1])
        risk_label = "High" if prediction == 1 else "Low"

        # Log en base de données
        if SessionLocal:
            try:
                with SessionLocal() as db:
                    log = PredictionLog(
                        employee_id=input_dict.get("id_employee"),
                        prediction_text=risk_label,
                        probability=probability
                    )
                    db.add(log)
                    db.commit()
            except Exception as db_err:
                print(f"⚠️ Erreur de log DB : {db_err}")

        return {
            "employee_id": input_dict.get("id_employee"),
            "attrition_risk": risk_label,
            "probability": f"{probability:.2%}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))