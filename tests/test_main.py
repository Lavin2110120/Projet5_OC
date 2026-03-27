from fastapi.testclient import TestClient
from app import app
import pytest

client = TestClient(app)

def test_health_check():
    """Vérifie que l'API est en ligne"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_prediction_endpoint():
    """Vérifie qu'une prédiction fonctionne et s'enregistre en base"""
    test_payload = {
        "id_employee": 1,
        "age": 41,
        "revenu_mensuel": 5993.0,
        "annee_experience_totale": 8,
        "annees_dans_l_entreprise": 6,
        "distance_domicile_travail": 1,
        "augmentation_salaire_precedente_pourcentage": 11.0,
        "statut_marital": "Célibataire",
        "departement": "Commercial",
        "poste": "Cadre Commercial",
        "domaine_etude": "Infra & Cloud",
        "frequence_deplacement": "Occasionnel",
        "heure_supplementaires": "Oui"
    }
    response = client.post("/predict", json=test_payload)
    assert response.status_code == 200
    data = response.json()
    assert "attrition_risk" in data
    assert data["database_log"] == "saved"