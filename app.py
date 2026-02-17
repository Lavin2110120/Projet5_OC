import sys
import os
import __main__ 
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import joblib
import pandas as pd
import polars as pl
from sklearn.base import BaseEstimator, TransformerMixin
from typing import List

# --- 1. DÉFINITION DE LA CLASSE ---
class PolarsPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, skip_first_row=True):
        self.skip_first_row = skip_first_row

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        # X est une liste de chemins : [sirh, eval, sondage]
        sirh_path, eval_path, sondage_path = X
        df_sirh = pl.read_csv(sirh_path)
        df_eval = pl.read_csv(eval_path)
        df_sondage = pl.read_csv(sondage_path)

        df_eval = df_eval.with_columns(
            pl.col("eval_number").str.replace("E_", "").cast(pl.Int64)
        )

        df_final = (
            df_sirh
            .join(df_eval, left_on="id_employee", right_on="eval_number", how="inner")
            .join(df_sondage, left_on="id_employee", right_on="code_sondage", how="inner")
        )

        df_final = df_final.with_columns([
            (pl.col("augementation_salaire_precedente")
             .str.replace(" %", "")
             .cast(pl.Float64) / 100).alias("augmentation_salaire_precedente_pourcentage")
        ])

        if self.skip_first_row:
            df_final = df_final.tail(-1)

        return df_final.to_pandas()

# --- 2. LE "HACK" POUR JOBLIB ---
__main__.PolarsPreprocessor = PolarsPreprocessor

# --- 3. INITIALISATION ET CHARGEMENT ---
app = FastAPI(title="TechNova Attrition Predictor API")

try:
    # On charge le fichier avec le nom exact utilisé dans ton notebook
    pipeline = joblib.load('full_techNova_pipeline.pkl')
    print("✅ Pipeline chargé avec succès !")
except Exception as e:
    print(f"❌ Erreur de chargement du modèle : {e}")

# --- 4. SCHÉMAS ET ROUTES ---

class EmployeeData(BaseModel):
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

@app.get("/")
def home():
    return {"message": "API TechNova opérationnelle"}

@app.post("/predict")
def predict_unit(data: EmployeeData):
    try:
        # Conversion pour Sklearn
        input_df = pd.DataFrame([data.dict()])
        
        # On utilise les étapes nommées du pipeline
        preprocessor = pipeline.named_steps['sklearn_preprocessor']
        classifier = pipeline.named_steps['classifier']
        
        processed_data = preprocessor.transform(input_df)
        prediction = classifier.predict(processed_data)[0]
        probability = classifier.predict_proba(processed_data)[0][1]
        
        return {
            "attrition_risk": "High" if prediction == 1 else "Low",
            "probability": f"{probability:.2%}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict-batch")
async def predict_batch(
    sirh: UploadFile = File(...), 
    evaluation: UploadFile = File(...), 
    sondage: UploadFile = File(...)
):
    temp_files = []
    try:
        # Sauvegarde temporaire locale
        for file in [sirh, evaluation, sondage]:
            path = f"temp_{file.filename}"
            with open(path, "wb") as f:
                f.write(await file.read())
            temp_files.append(path)
        
        # Le pipeline global s'occupe de la jointure Polars
        predictions = pipeline.predict(temp_files)
        probs = pipeline.predict_proba(temp_files)[:, 1]
        
        return {
            "results": [
                {"id": i, "risk": "High" if p == 1 else "Low", "prob": f"{pr:.2%}"} 
                for i, (p, pr) in enumerate(zip(predictions, probs))
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Nettoyage des fichiers temporaires
        for path in temp_files:
            if os.path.exists(path):
                os.remove(path)