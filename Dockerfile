# 1. Image de base fixée sur la version exacte demandée
FROM python:3.12.8-slim

# 2. Répertoire de travail
WORKDIR /app

# 3. Installation des dépendances système indispensables
# build-essential et libpq-dev sont requis pour psycopg2/psycopg et sqlalchemy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Mise à jour de pip pour éviter les avertissements de version
RUN pip install --no-cache-dir --upgrade pip

# 5. Copie de l'intégralité du projet 

COPY . .

# 6. Installation du projet

RUN pip install --no-cache-dir .

# 7. Port utilisé par Hugging Face Spaces par défaut
EXPOSE 7860

# 8. Commande de lancement optimisée pour la production
# On utilise le port 7860 exigé par Hugging Face
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]