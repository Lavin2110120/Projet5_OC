import os
import sys
import joblib
import pandas as pd
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL
from sklearn.base import BaseEstimator, TransformerMixin

# --- 1. CONFIGURATION DU MODÈLE (PRÉ-REQUIS) ---
class PolarsPreprocessor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X): return X

# Injection dans le module main pour le dépicklage
sys.modules['__main__'].PolarsPreprocessor = PolarsPreprocessor

# --- 2. CHARGEMENT DES VARIABLES D'ENVIRONNEMENT ---
load_dotenv() 

# --- 3. CONFIGURATION ET CONNEXION BASE DE DONNÉES ---
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

def get_db_url():
    """Construit l'URL SQLAlchemy à partir des variables d'environnement."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME")
    
    if not all([user, password, host, database]):
        print("⚠️ Configuration DB incomplète dans les variables d'environnement.")
        return None

    return URL.create(
        drivername="postgresql+psycopg",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database
    )

# Tentative de connexion
db_url = get_db_url()
if db_url:
    try:
        engine = create_engine(
            db_url, 
            connect_args={"sslmode": "require"},
            pool_pre_ping=True
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Initialisation du Schéma et des Tables
        with engine.begin() as conn:
            conn.execute(text('CREATE SCHEMA IF NOT EXISTS "uml_p5";'))
        Base.metadata.create_all(bind=engine)
        print("✅ Base de données initialisée avec succès.")
    except Exception as e:
        print(f"❌ Erreur de connexion/initialisation DB : {e}")
        engine = None

# --- 4. CHARGEMENT DU MODÈLE ---
def load_model():
    try:
        model = joblib.load("full_techNova_pipeline.pkl")
        print("✅ Modèle chargé avec succès.")
        return model
    except Exception as e:
        print(f"❌ Erreur chargement modèle : {e}")
        return None

global_pipeline = load_model()

FEATURES_ORDER = [
    "age", "revenu_mensuel", "annee_experience_totale", 
    "annees_dans_l_entreprise", "distance_domicile_travail",
    "augmentation_salaire_precedente_pourcentage", "statut_marital", 
    "departement", "poste", "domaine_etude", 
    "frequence_deplacement", "heure_supplementaires"
]

# --- 5. ROUTES API (FASTAPI) ---
app = FastAPI(title="TechNova Attrition API")

@app.get("/")
def home():
    """Vérifie l'état de santé de l'API."""
    return {
        "status": "online", 
        "model_loaded": global_pipeline is not None,
        "database_connected": engine is not None
    }

@app.post("/predict")
async def predict(data: dict):
    """Effectue une prédiction et log le résultat en base de données."""
    if global_pipeline is None:
        raise HTTPException(status_code=503, detail="Modèle non disponible")
    
    try:
        # Préparation des données
        df = pd.DataFrame([data])
        df_model = df[FEATURES_ORDER]
        
        # Inférence
        prediction = global_pipeline.predict(df_model)[0]
        probability = float(global_pipeline.predict_proba(df_model)[0][1])
        risk_label = "High" if prediction == 1 else "Low"

        # Log en base de données (si disponible)
        if SessionLocal:
            try:
                with SessionLocal() as db:
                    log = PredictionLog(
                        employee_id=data.get("id_employee"),
                        prediction_text=risk_label,
                        probability=probability
                    )
                    db.add(log)
                    db.commit()
            except Exception as db_err:
                print(f"⚠️ Erreur de log DB : {db_err}")

        return {
            "employee_id": data.get("id_employee"),
            "attrition_risk": risk_label,
            "probability": f"{probability:.2%}"
        }
    except Exception as e:
        print(f"❌ Erreur lors de la prédiction : {e}")
        raise HTTPException(status_code=500, detail=str(e))