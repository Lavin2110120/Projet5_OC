import os
import __main__
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import joblib
import pandas as pd
import polars as pl
from sklearn.base import BaseEstimator, TransformerMixin
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL

# --- 1. CONFIGURATION BASE DE DONNÉES ---
db_url = URL.create(
    drivername="postgresql+psycopg",
    username="postgres",
    password="59210216sql",
    host="host.docker.internal",
    port="5432",
    database="technova_db"
)

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèle pour la traçabilité des prédictions
class PredictionLog(Base):
    __tablename__ = "predictions"
    __table_args__ = {"schema": "UML P5"}

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer)
    prediction_text = Column(String)
    probability = Column(Float)
    created_at = Column(DateTime, default=func.now())

# Création de la table de logs si elle n'existe pas
Base.metadata.create_all(bind=engine)

# --- 2. PRÉPROCESSEUR POLARS (Hack Joblib) ---
class PolarsPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, skip_first_row=False):
        self.skip_first_row = skip_first_row

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        sirh_path, eval_path, sondage_path = X
        df_sirh = pl.read_csv(sirh_path)
        df_eval = pl.read_csv(eval_path)
        df_sondage = pl.read_csv(sondage_path)

        df_eval = df_eval.with_columns(pl.col("eval_number").str.replace("E_", "").cast(pl.Int64))
        
        df_final = (
            df_sirh
            .join(df_eval, left_on="id_employee", right_on="eval_number")
            .join(df_sondage, left_on="id_employee", right_on="code_sondage")
        )
        return df_final.to_pandas()

__main__.PolarsPreprocessor = PolarsPreprocessor

# --- 3. INITIALISATION API ET MODÈLE ---
app = FastAPI(title="TechNova Attrition Predictor API")

try:
    pipeline = joblib.load('full_techNova_pipeline.pkl')
    print("✅ Pipeline ML chargé !")
except Exception as e:
    print(f"❌ Erreur chargement modèle : {e}")

# --- 4. SCHÉMAS DE DONNÉES ---
class EmployeeData(BaseModel):
    id_employee: int
    age: int
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

# --- 5. ROUTES ---

@app.get("/")
def home():
    return {"status": "online", "database": "connected", "schema": "UML P5"}

@app.post("/predict")
def predict_unit(data: EmployeeData):
    db = SessionLocal()
    try:
        # 1. Prédiction
        input_df = pd.DataFrame([data.dict()])
        preprocessor = pipeline.named_steps['sklearn_preprocessor']
        classifier = pipeline.named_steps['classifier']
        
        processed_data = preprocessor.transform(input_df)
        prediction = int(classifier.predict(processed_data)[0])
        probability = float(classifier.predict_proba(processed_data)[0][1])
        
        risk_label = "High" if prediction == 1 else "Low"

        # 2. TRAÇABILITÉ : Enregistrement en BDD
        log = PredictionLog(
            employee_id=data.id_employee,
            prediction_text=risk_label,
            probability=round(probability, 4)
        )
        db.add(log)
        db.commit()

        return {
            "employee_id": data.id_employee,
            "attrition_risk": risk_label,
            "probability": f"{probability:.2%}",
            "database_log": "saved"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/predict-batch")
async def predict_batch(
    sirh: UploadFile = File(...), 
    evaluation: UploadFile = File(...), 
    sondage: UploadFile = File(...)
):
    temp_files = []
    try:
        # Sauvegarde temporaire
        for file in [sirh, evaluation, sondage]:
            path = f"temp_{file.filename}"
            with open(path, "wb") as f:
                f.write(await file.read())
            temp_files.append(path)
        
        predictions = pipeline.predict(temp_files)
        probs = pipeline.predict_proba(temp_files)[:, 1]
        
        return {
            "batch_results": [
                {"index": i, "risk": "High" if p == 1 else "Low", "prob": f"{pr:.2%}"} 
                for i, (p, pr) in enumerate(zip(predictions, probs))
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for path in temp_files:
            if os.path.exists(path):
                os.remove(path)