🚀 TechNova - Prédiction de l'Attrition Employés
📝 Présentation du Projet

Ce projet consiste en l'industrialisation d'un modèle de Machine Learning permettant de prédire le risque de départ (attrition) des employés de la société TechNova.

L'objectif est de fournir une solution "production-ready" comprenant une API de prédiction, une base de données de traçabilité et une conteneurisation complète.
🛠 Stack Technique

    Traitement de données : Polars (Haute performance)

    Modélisation : Scikit-Learn (Random Forest Classifier)

    API : FastAPI

    Base de données : PostgreSQL (Traçabilité des prédictions via SQLAlchemy)

    Tests : Pytest & HTTPX

    Conteneurisation : Docker

📂 Structure du Dépôt

    app.py : Point d'entrée de l'API FastAPI.

    seed_db.py : Script d'initialisation de la base de données.

    full_techNova_pipeline.pkl : Pipeline de ML entraîné et sérialisé.

    test_main.py : Tests unitaires et d'intégration.

    Dockerfile : Configuration pour le déploiement conteneurisé.

    pyproject.toml : Gestion des dépendances et métadonnées du projet.

🚀 Installation et Utilisation
1. Cloner le projet
Bash

git clone https://github.com/Lavin2110120/Projet5_OC.git
cd Projet5_OC

2. Installation via Environnement Virtuel
Bash

# Création du venv
python -m venv venv
source venv/bin/Scripts/activate  # Sur Windows: venv\Scripts\activate

# Installation des dépendances
pip install .

3. Lancer l'API
Bash

uvicorn app:app --reload

L'API sera disponible sur http://127.0.0.1:8000. Accédez à /docs pour tester les endpoints via Swagger UI.
🧪 Tests de Qualité

Pour valider le bon fonctionnement de l'API et du modèle, lancez la suite de tests :
Bash

pytest

🐳 Déploiement avec Docker

Le projet est entièrement dockerisé pour garantir la portabilité.

Construction de l'image :
Bash

docker build -t technova-app .

Lancement du conteneur :
Bash

docker run -p 8000:8000 technova-app

📊 Endpoints de l'API
Méthode	Endpoint	Description
GET	/	Vérification du statut de l'API.
POST	/predict	Prédiction unitaire (JSON) + Log en BDD.
POST	/predict-batch	Prédiction en masse via l'upload de fichiers CSV.
🔒 Sécurité et Traçabilité

    Traçabilité : Chaque prédiction effectuée via l'endpoint /predict est automatiquement enregistrée dans la table predictions du schéma UML P5 sur PostgreSQL.

    Variables d'environnement : Les informations sensibles (mots de passe BDD) doivent être configurées via des variables d'environnement en production.

Auteur : Lavin - Projet 5 - Parcours Data Scientist (OpenClassrooms)