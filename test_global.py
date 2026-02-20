import requests

def test_api_online():
    # Test de la route home
    response = requests.get("http://127.0.0.1:8000/")
    print(f"Status Home: {response.status_code}")
    print(f"Response: {response.json()}")

def test_prediction():
    # Test d'une prédiction unitaire
    payload = {
        "id_employee": 1,
        "age": 30,
        "revenu_mensuel": 3500.0,
        "annee_experience_totale": 5,
        "annees_dans_l_entreprise": 3,
        "distance_domicile_travail": 10,
        "augmentation_salaire_precedente_pourcentage": 0.05,
        "statut_marital": "Célibataire",
        "departement": "R&D",
        "poste": "Ingénieur",
        "domaine_etude": "Informatique",
        "frequence_deplacement": "Rarement",
        "heure_supplementaires": "Non"
    }
    response = requests.post("http://127.0.0.1:8000/predict", json=payload)
    print(f"Status Predict: {response.status_code}")
    if response.status_code == 200:
        print(f"Résultat: {response.json()}")
    else:
        print(f"Erreur: {response.text}")

if __name__ == "__main__":
    test_api_online()
    test_prediction()