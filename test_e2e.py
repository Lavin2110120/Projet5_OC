import os
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 1. Chargement des variables d'environnement locales
load_dotenv("mdpP5.env")

# 2. Import de l'application (l'app doit être configurée pour localhost)
import app as app_module
from app import app, PredictionLog, get_db
from fastapi.testclient import TestClient

client = TestClient(app)

# 3. Configuration de l'Engine SQL pour le test local (pgAdmin)
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "technova_db")

# On utilise psycopg2 pour correspondre à ton installation locale
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocalTest = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_e2e_local_flow():
    """
    TEST E2E : Simule le flux complet
    API (Predict) -> Modèle (ML) -> Base de données locale (PostgreSQL)
    """
    
    # ID unique pour ce test pour éviter les conflits
    TEST_EMPLOYEE_ID = 8888 

    # --- A. Payload de test (Données envoyées à l'API) ---
    payload = {
        "id_employee": TEST_EMPLOYEE_ID,
        "age": 30,
        "revenu_mensuel": 4500.0,
        "annee_experience_totale": 5,
        "annees_dans_l_entreprise": 2,
        "distance_domicile_travail": 5,
        "augmentation_salaire_precedente_pourcentage": 12.0,
        "statut_marital": "Marié",
        "departement": "Ventes",
        "poste": "Responsable",
        "domaine_etude": "Commerce",
        "frequence_deplacement": "Rarement",
        "heure_supplementaires": "Non"
    }

    # --- B. Exécution de l'appel API ---
    # Cela va déclencher la prédiction ET l'insertion en DB dans app.py
    response = client.post("/predict", json=payload)
    
    assert response.status_code == 200
    api_data = response.json()
    print(f"\n✅ [E2E] Réponse API reçue : Risque = {api_data['attrition_risk']}")

    # --- C. Vérification directe dans PostgreSQL (pgAdmin) ---
    with SessionLocalTest() as db:
        # On cherche l'entrée que l'API vient d'insérer
        db_record = db.query(PredictionLog).filter_by(employee_id=TEST_EMPLOYEE_ID).first()
        
        assert db_record is not None, "❌ Erreur E2E : La prédiction n'a pas été trouvée en base de données !"
        assert db_record.prediction_text == api_data["attrition_risk"], "❌ Erreur E2E : Incohérence des données entre API et DB"
        
        print(f"✅ [E2E] Succès : La prédiction pour l'employé {TEST_EMPLOYEE_ID} est bien loggée en DB (ID ligne: {db_record.id})")

        # --- D. Nettoyage (Optionnel) ---
        # Pour ne pas polluer ta base pgAdmin à chaque test
        db.delete(db_record)
        db.commit()
        print("✅ [E2E] Nettoyage effectué dans pgAdmin.")

if __name__ == "__main__":
    # Permet de lancer le script directement avec 'python test_e2e.py'
    test_e2e_local_flow()