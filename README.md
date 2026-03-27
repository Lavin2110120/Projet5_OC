---
title: TechNova Attrition Predictor
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
---

🚀 TechNova - Système de Prédiction d'Attrition Employés
📝 Présentation du Projet

Ce projet consiste en l'industrialisation d'un modèle de Machine Learning pour la société TechNova. L'objectif est de prédire le risque de départ des collaborateurs tout en garantissant une traçabilité totale des prédictions.
Points clés :

    API REST développée avec FastAPI.

    Traçabilité : Chaque prédiction est enregistrée dans une base de données PostgreSQL (Neon.tech) via SQLAlchemy.

    Pipeline ML : Utilisation d'un préprocesseur personnalisé (PolarsPreprocessor) intégré dans un pipeline Scikit-Learn.

    Dockerisation : Environnement reproductible via Docker.

    CI/CD : Automatisation des tests et du déploiement via GitHub Actions.

🏗 Structure du Dépôt

    app.py : Application principale FastAPI et logique de connexion DB.

    full_techNova_pipeline.pkl : Modèle de Machine Learning sérialisé.

    test_main.py : Tests unitaires pour l'API et le modèle.

    Dockerfile : Instructions de conteneurisation.

    pyproject.toml : Gestion moderne des dépendances Python.

    seed_db.py : Script pour peupler la base de données initiale.

🛠 Installation et Utilisation Locale
1. Clonage et Environnement
Bash

git clone https://github.com/Lavin2110120/Projet5_OC.git
cd Projet5_OC
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

2. Configuration

Créez un fichier .env à la racine pour les accès base de données :
Extrait de code

DB_HOST=votre_host_neon
DB_USER=neondb_owner
DB_PASSWORD=votre_mot_de_passe
DB_NAME=neondb
DB_PORT=5432

3. Installation et Lancement
Bash

pip install .
uvicorn app:app --reload

L'interface Swagger est disponible sur : http://127.0.0.1:8000/docs
🐳 Docker

Pour lancer l'application dans un conteneur :
Bash

docker build -t technova-app .
docker run -p 7860:7860 --env-file .env technova-app

⚙️ CI/CD & Déploiement

Le projet utilise GitHub Actions pour un cycle de vie automatisé :

    Tests : À chaque push, pytest vérifie l'intégrité de l'API et le chargement du modèle.

    Déploiement : Si les tests réussissent, le code est automatiquement poussé vers Hugging Face Spaces.

📊 Utilisation de l'API (Endpoint /predict)

Exemple de requête JSON :
JSON

{
  "id_employee": 1,
  "age": 41,
  "revenu_mensuel": 5993.0,
  "annee_experience_totale": 8,
  "annees_dans_l_entreprise": 6,
  "distance_domicile_travail": 1,
  "augmentation_salaire_precedente_pourcentage": 11.0,
  "statut_marital": "Married",
  "departement": "Sales",
  "poste": "Sales Executive",
  "domaine_etude": "Life Sciences",
  "frequence_deplacement": "Travel_Rarely",
  "heure_supplementaires": "No"
}

Réponse type :
JSON

{
  "employee_id": 1,
  "attrition_risk": "High",
  "probability": "87.50%"
}

Développé par Lavin2110 - Projet 5 du parcours Data Scientist (OpenClassrooms).