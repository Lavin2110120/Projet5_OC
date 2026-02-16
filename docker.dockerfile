# 1. Utiliser une image Python légère (correspondant à votre .python-version)
FROM python:3.12-slim

# 2. Définir le répertoire de travail dans le conteneur
WORKDIR /app

# 3. Copier les fichiers de configuration en premier (optimisation du cache)
COPY pyproject.toml .
COPY .python-version .

# 4. Installer les dépendances
# On installe aussi uvicorn et fastapi s'ils ne sont pas dans le toml
RUN pip install --no-cache-dir . fastapi uvicorn joblib

# 5. Copier le reste du code et le modèle
COPY app.py .
COPY models/ ./models/

# 6. Exposer le port utilisé par FastAPI
EXPOSE 8000

# 7. Commande pour lancer l'API au démarrage du conteneur
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]