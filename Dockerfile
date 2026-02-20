# 1. Image de base légère
FROM python:3.12-slim

# 2. Répertoire de travail
WORKDIR /app

# 3. Installation des dépendances système (nécessaires pour PostgreSQL et Polars)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Copie des fichiers de configuration
COPY pyproject.toml .

# 5. Installation des librairies Python (on ajoute python-multipart en plus)
RUN pip install --no-cache-dir .
RUN pip install python-multipart

# 6. Copie du code et du modèle
COPY app.py .
COPY full_techNova_pipeline.pkl .
COPY mdpP5.env .

# 7. Port utilisé par FastAPI
EXPOSE 8000

# 8. Commande de lancement
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]