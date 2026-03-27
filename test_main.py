from fastapi.testclient import TestClient
import joblib
import pytest
import app as app_module  
from app import app, PolarsPreprocessor
import sys

sys.modules['__main__'].PolarsPreprocessor = PolarsPreprocessor
client = TestClient(app)

def test_health_check():
    """Vérifie que l'API est en ligne et le modèle chargé"""
    # Si le chargement a échoué à l'import, on tente de le forcer pour le test
    """if app_module.global_pipeline is None:
        app_module.global_pipeline = joblib.load("full_techNova_pipeline.pkl") """
        
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    """ assert response.json()["model_loaded"] is True 
 """
    

def test_model():
    model = app_module.load_model()
    assert model is not None

def test_prediction_endpoint():
    """Vérifie le cycle complet : Envoi de données -> Prédiction -> Format de réponse"""
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
    
    # 1. Vérification du succès de la requête
    assert response.status_code == 200, f"Erreur: {response.text}"
    
    # 2. Vérification de la structure de la réponse
    data = response.json()
    assert "attrition_risk" in data
    assert "probability" in data
    assert data["employee_id"] == 1
    
    # 3. Vérification des valeurs cohérentes
    assert data["attrition_risk"] in ["High", "Low"]
    assert "%" in data["probability"] # Vérifie le formatage du string