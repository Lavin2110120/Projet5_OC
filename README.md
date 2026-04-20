---
title: TechNova Attrition Predictor
Link to my space: https://huggingface.co/spaces/Lavin2110/projet5_OC/tree/main
sdk: docker
app_port: 7860
---
 
TechNova - Système de Prédiction d'Attrition Employés

I.  Présentation du Projet

Ce projet industrialise un modèle de Machine Learning pour TechNova. L'objectif est de prédire le risque de départ des collaborateurs tout en garantissant une traçabilité totale via une base de données PostgreSQL.

Points clés :
* API REST : Développée avec FastAPI.
* Traçabilité: Chaque prédiction est enregistrée dans PostgreSQL (pgAdmin en local).
* Pipeline ML: Utilisation d'un `PolarsPreprocessor` personnalisé intégré dans un pipeline Scikit-Learn.
* Conteneurisation : Dockerisation complète pour un déploiement agnostique.
* CI/CD : Automatisation des tests et du déploiement vers Hugging Face Spaces via GitHub Actions.

II. Structure du Dépôt
* `app.py` : Logique FastAPI, chargement du modèle et persistance SQLAlchemy.
* `seed_db.py` : Script d'initialisation pour peupler la base locale depuis les extraits CSV.
* `full_techNova_pipeline.pkl` : Pipeline ML compressé (LFS).
* `test_main.py` & `test_e2e.py` : Tests unitaires et tests d'intégration bout-en-bout.
* `Dockerfile` : Configuration de l'image de production.
* `pyproject.toml` : Gestion moderne des dépendances (PEP 517/518).

III.  Installation Locale

1. Prérequis
* Python 3.12.8
* PostgreSQL / pgAdmin 4 installé localement.

2. Configuration
Crée un fichier `mdpP5.env` à la racine :
```env
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
DB_NAME=technova_db

# Installation des dépendances
pip install .

# Initialisation de la base de données
python seed_db.py

IV. API
# Lancement de l'API
python -m uvicorn app:app --reload

L'interface Swagger est disponible sur : http://127.0.0.1:8000/docs
 Docker & CI/CD

Le projet est configuré pour être déployé automatiquement.

    Build Local : docker build -t technova-app .

    CI/CD : À chaque push, GitHub Actions lance les tests. Si le succès est au rendez-vous, l'image est déployée sur Hugging Face Spaces.

L'API déployée sur Hugging Face fonctionne en mode résilient sans base de données persistante. Pour tester la persistance PostgreSQL complète, veuillez exécuter le script seed_db.py puis l'API en local comme décrit dans la section Installation.

V.  Modèle de Données & Persistance

Pour TechNova, la prédiction ne suffit pas : il faut pouvoir auditer les décisions du modèle.

1. Architecture de Stockage
Nous utilisons PostgreSQL avec le schéma suivant :
Schéma: `uml_p5`
Table: `predictions`

2. Dictionnaire des données (`predictions`)

`id` (Integer) : Clé primaire (auto-incrément)
`employee_id` (Integer) : ID unique de l'employé testé
`prediction_text` (String) : Résultat : `High` (Risque) ou `Low` (Stable)
`probability` (Float) : Score de confiance du modèle (0 à 1)
`created_at` (DateTime) : Horodatage automatique (UTC)

3.  Logique d'Insertion
La connexion est gérée par SQLAlchemy. L'application utilise une approche de "Fail-Safe" :
- L'API reçoit une demande de prédiction.
- Le modèle calcule le résultat.
- Une tentative d'insertion en base est faite.
- Si la base est indisponible : L'erreur est logguée, mais l'API renvoie quand même la prédiction à l'utilisateur pour ne pas bloquer le service RH.

4.  Cas d'Usage Métier
Le stockage de ces données dans pgAdmin permet :
1. Reporting : Connecter un outil comme PowerBI ou Tableau pour visualiser le taux d'attrition global.
2. Monitoring : Surveiller la dérive du modèle (Data Drift) en analysant l'évolution des probabilités dans le temps.
3. Audit : Vérifier a posteriori les prédictions pour un employé spécifique lors des entretiens annuels.

VI. Test&Qualité

La qualité du code est assurée par une suite de tests unitaires et E2E. Le taux de couverture actuel est de 88%, garantissant la fiabilité des prédictions et de la persistance en base de données.

Lancer les tests unitaires:
pytest test_main.py

Lancer les tests d'intégration (nécessite la DB lancée):
python test_e2e.py

Générer le rapport de couverture :
pytest --cov=app test_main.py --cov-report=html