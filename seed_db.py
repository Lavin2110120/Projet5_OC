import polars as pl
from sqlalchemy import create_engine, Column, Integer, Float, String, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL

# 1. PARAMÈTRES DE CONNEXION
db_config = {
    "drivername": "postgresql+psycopg",
    "username": "postgres",
    "password": "59210216sql", # Votre mot de passe
    "host": "localhost",
    "port": "5432",
    "database": "technova_db"
}

connection_url = URL.create(**db_config)
engine = create_engine(connection_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. MODÈLE DE DONNÉES (Le schéma UML P5 doit être précisé ici)
class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = {"schema": "UML P5"} 

    id_employee = Column(Integer, primary_key=True)
    age = Column(Integer)
    revenu_mensuel = Column(Float)
    annee_experience_totale = Column(Integer)
    annees_dans_l_entreprise = Column(Integer)
    distance_domicile_travail = Column(Integer)
    augmentation_salaire_precedente_pourcentage = Column(Float)
    statut_marital = Column(String)
    departement = Column(String)
    poste = Column(String)
    domaine_etude = Column(String)
    frequence_deplacement = Column(String)
    heure_supplementaires = Column(String)

# 3. LOGIQUE D'INSERTION
def seed_data():
    try:
        print(f"--- Connexion à {db_config['database']} ---")
        
        # On s'assure que SQLAlchemy crée la table dans le schéma UML P5
        Base.metadata.create_all(bind=engine)
        print("✅ Table 'employees' créée proprement dans le schéma 'UML P5' !")

        # Lecture des fichiers
        print("--- Chargement des CSV ---")
        df_sirh = pl.read_csv("extrait_sirh.csv")
        df_eval = pl.read_csv("extrait_eval.csv")
        df_sondage = pl.read_csv("extrait_sondage.csv")

        # Harmonisation des colonnes pour la jointure
        # Pour le fichier EVAL (E_101 -> 101)
        df_eval = df_eval.with_columns(
            pl.col("eval_number").str.replace("E_", "").cast(pl.Int64)
        ).rename({"eval_number": "id_employee"})

        # Pour le fichier SONDAGE (code_sondage -> id_employee)
        df_sondage = df_sondage.rename({"code_sondage": "id_employee"})

        print("--- Fusion des données (Jointure) ---")
        df_final = df_sirh.join(df_eval, on="id_employee").join(df_sondage, on="id_employee")

        print(f"--- Insertion de {len(df_final)} lignes ---")
        
        # Récupération des colonnes attendues par la classe Employee
        allowed_columns = Employee.__table__.columns.keys()

        with SessionLocal() as session:
            for row in df_final.to_dicts():
                # On filtre pour ne garder que ce qui va en base
                clean_row = {k: v for k, v in row.items() if k in allowed_columns}
                session.add(Employee(**clean_row))
            
            session.commit()
        
        print("✅ Base de données initialisée avec succès !")

    except Exception as e:
        print(f"❌ Erreur lors du peuplement : {e}")

if __name__ == "__main__":
    seed_data()