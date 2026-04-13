import sys
import joblib
import pytest
import __main__
from fastapi.testclient import TestClient

# 1. On définit la classe ou on l'importe AVANT d'importer l'app
try:
    from app import PolarsPreprocessor
    __main__.PolarsPreprocessor = PolarsPreprocessor
except ImportError:
    # Si l'import direct échoue car le modèle charge déjà, on définit une classe dummy
    class PolarsPreprocessor: pass
    __main__.PolarsPreprocessor = PolarsPreprocessor

# 2. Maintenant on importe l'application
import app as app_module
from app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_model():
    model = app_module.load_model()
    assert model is not None

def test_prediction_endpoint():
    test_payload = {
        "id_employee": 1, "age": 41, "revenu_mensuel": 5993.0,
        "annee_experience_totale": 8, "annees_dans_l_entreprise": 6,
        "distance_domicile_travail": 1, "augmentation_salaire_precedente_pourcentage": 11.0,
        "statut_marital": "Célibataire", "departement": "Commercial",
        "poste": "Cadre Commercial", "domaine_etude": "Infra & Cloud",
        "frequence_deplacement": "Occasionnel", "heure_supplementaires": "Oui"
    }
    response = client.post("/predict", json=test_payload)
    assert response.status_code == 200
    data = response.json()
    assert "attrition_risk" in data
    assert data["employee_id"] == 1

def test_prediction_invalid_data():
    response = client.post("/predict", json={"id_employee": 1})
    assert response.status_code == 422