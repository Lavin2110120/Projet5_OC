# 1. Utiliser une image Python légère
FROM python:3.11-slim

# 2. Définir le répertoire de travail
WORKDIR /app

# 3. Installer les dépendances système nécessaires (si besoin pour Polars/Arrow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Installer les librairies Python
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    joblib \
    polars \
    pyarrow \
    pandas \
    scikit-learn==1.6.1 \
    python-multipart

# 5. Copier le code de l'API
COPY app.py .

# 6. Copier le modèle

COPY full_techNova_pipeline.pkl .

# 7. Exposer le port 8000
EXPOSE 8000

# 8. Lancer l'application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]