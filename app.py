from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np

# 1. Initialisation de l'API et chargement du modèle
app = FastAPI(title="TechNova Attrition Predictor API")

try:
    # On charge le pipeline complet (Pre-processing + Random Forest)
    model = joblib.load('final_pipeline_turnover.pkl')
except Exception as e:
    print(f"Erreur de chargement du modèle : {e}")

# 2. Modèle de données pour la requête (Input Schema)
# On définit ici les colonnes attendues après la fusion pour la prédiction directe
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
    return {"message": "Bienvenue sur l'API de prédiction de l'attrition TechNova"}

@app.post("/predict")
def predict(data: EmployeeData):
    try:
        # 1. Convertir les données reçues en DataFrame pandas
        input_df = pd.DataFrame([data.dict()])
        
        # 2. Utiliser le pipeline pour prédire
        # Le pipeline s'occupe du scaling et de l'encodage automatiquement
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]
        
        # 3. Formater la réponse
        return {
            "attrition_risk": "High" if prediction == 1 else "Low",
            "probability": f"{probability:.2%}",
            "prediction_code": int(prediction)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)