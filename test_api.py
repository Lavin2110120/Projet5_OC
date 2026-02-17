import requests

# Configuration
BASE_URL = "http://127.0.0.1:8000"

def test_unitaire():
    print("--- Test de prédiction UNITAIRE (JSON) ---")
    url = f"{BASE_URL}/predict"
    
    # Données d'un employé fictif (doit correspondre au schéma Pydantic de app.py)
    data = {
        "age": 35,
        "revenu_mensuel": 5500.0,
        "annee_experience_totale": 10,
        "annees_dans_l_entreprise": 5,
        "distance_domicile_travail": 12,
        "augmentation_salaire_precedente_pourcentage": 0.12,
        "statut_marital": "Marié(e)",
        "departement": "Consulting",
        "poste": "Consultant",
        "domaine_etude": "Infra & Cloud",
        "frequence_deplacement": "Occasionnel",
        "heure_supplementaires": "Non"
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        print("✅ Succès (Unitaire) !")
        print("Réponse :", response.json())
    else:
        print(f"❌ Erreur {response.status_code} (Unitaire)")
        print(response.text)

def test_batch():
    print("\n--- Test de prédiction BATCH (Fichiers CSV + Polars) ---")
    url = f"{BASE_URL}/predict-batch"
    
    # On ouvre les 3 fichiers en mode binaire
    # Assure-toi que ces fichiers sont bien présents dans le même dossier
    try:
        files = {
            'sirh': open('extrait_sirh.csv', 'rb'),
            'evaluation': open('extrait_eval.csv', 'rb'),
            'sondage': open('extrait_sondage.csv', 'rb')
        }

        response = requests.post(url, files=files)

        if response.status_code == 200:
            print("✅ Succès (Batch) !")
            resultats = response.json()
            print(f"Total traités : {resultats.get('total_processed', 'N/A')}")
            print(f"Nombre de risques élevés : {resultats.get('high_risk_count', 'N/A')}")
            # Affichage des 3 premiers résultats pour vérifier
            print("Aperçu des résultats :", resultats['results'][:3])
        else:
            print(f"❌ Erreur {response.status_code} (Batch)")
            print(response.text)
            
    except FileNotFoundError as e:
        print(f"❌ Erreur : Fichier manquant pour le test batch. {e}")
    finally:
        # On ferme les fichiers proprement
        for f in files.values():
            if not f.closed:
                f.close()

if __name__ == "__main__":
    # 1. Test unitaire
    test_unitaire()
    
    # 2. Test Batch (Jointures Polars)
    test_batch()