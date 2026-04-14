import os
import polars as pl
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from dotenv import load_dotenv

# 1. Chargement des variables d'environnement
load_dotenv("mdpP5.env")

# 2. Configuration de la connexion
connection_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port="5432",
    database=os.getenv("DB_NAME", "technova_db")
)

engine = create_engine(connection_url)

def seed_database():
    try: 
        print("--- Chargement et nettoyage Polars ---")
        df_sirh = pl.read_csv("extrait_sirh.csv")
        df_eval = pl.read_csv("extrait_eval.csv")
        df_sondage = pl.read_csv("extrait_sondage.csv")

        # Nettoyage et Jointure
        df_eval = df_eval.with_columns(
            pl.col("eval_number").str.replace("E_", "").cast(pl.Int64)
        ).rename({"eval_number": "id_employee"})

        df_sondage = df_sondage.rename({"code_sondage": "id_employee"})

        df_final = df_sirh.join(df_eval, on="id_employee").join(df_sondage, on="id_employee")

        print(f"--- Insertion de {len(df_final)} lignes ---")
        
        # Conversion en Pandas
        pdf = df_final.to_pandas()

        # 1. Création du schéma
        with engine.connect() as conn:
            conn.execute(text('CREATE SCHEMA IF NOT EXISTS "UML P5";'))
            conn.commit() 

        # 2. Insertion des données via String URL
        db_url_string = (
            f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST', 'localhost')}:5432/{os.getenv('DB_NAME')}"
        )

        pdf.to_sql(
            name="employees", 
            con=db_url_string, 
            schema="UML P5", 
            if_exists="replace", 
            index=False
        )
        print("✅ Base de données initialisée avec succès !")

    except Exception as e: 
        print(f"❌ Erreur lors du seeding : {e}")


if __name__ == "__main__":
    seed_database()