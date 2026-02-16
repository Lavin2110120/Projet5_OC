import requests

url = "http://127.0.0.1:8000/predict"

# Exemple de données d'un employé fictif
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
    print("Succès !")
    print("Réponse de l'API :", response.json())
else:
    print("Erreur :", response.status_code)
    print(response.text)