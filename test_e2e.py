import os
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 1. Chargement des variables d'environnement
env_path = "mdpP5.env"
load_dotenv(env_path)

# 2. Import de l'application (doit se faire après load_dotenv)
import app as app_module
from app import app, PredictionLog
from fastapi.testclient import TestClient

client = TestClient(app)

# 3. Configuration de l'Engine SQL pour le test
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")
dbname = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}"
engine = create_engine(DATABASE_URL)
SessionLocalTest = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_e2e_prediction_and_db_logging():
    """Test complet : API -> ML -> DB"""
    
    # --- A. Préparation du Schéma ---
    # On s'assure que le schéma attendu par app.py existe en base
    with engine.connect() as conn:
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS "UML P5";'))
        conn.commit()

    # --- B. Payload de test ---
    payload = {
        "id_employee": 999,
        "age": 35,
        "revenu_mensuel": 5000.0,
        "annee_experience_totale": 10,
        "annees_dans_l_entreprise": 5,
        "distance_domicile_travail": 10,
        "augmentation_salaire_precedente_pourcentage": 15.0,
        "statut_marital": "Marié",
        "departement": "Ventes",
        "poste": "Responsable",
        "domaine_etude": "Commerce",
        "frequence_deplacement": "Rarement",
        "heure_supplementaires": "Non"
    }

    # --- C. Appel API ---
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    print(f"✅ API OK: {data['attrition_risk']}")

    # --- D. Vérification DB ---
    # On utilise SessionLocalTest défini plus haut
    with SessionLocalTest() as db:
        # On cherche l'entrée créée
        log = db.query(PredictionLog).filter_by(employee_id=999).first()
        
        assert log is not None, "La donnée n'a pas été insérée en DB"
        assert log.prediction_text == data["attrition_risk"]
        print(f"✅ DB OK: Log {log.id} trouvé")

        # Nettoyage
        db.delete(log)
        db.commit()
        print("✅ Nettoyage DB effectué")