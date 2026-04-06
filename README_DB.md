---

## 💾 Modèle de Données & Persistance (PostgreSQL)

Pour garantir la traçabilité des décisions du modèle, chaque requête d'inférence est archivée dans une base de données PostgreSQL (hébergée sur Neon.tech).

### Schéma de la Table : `uml_p5.predictions`
Cette table permet de conserver un historique complet des interactions avec l'API.

| Colonne | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Clé primaire auto-incrémentée. |
| `employee_id` | Integer | Identifiant unique du collaborateur (ID TechNova). |
| `prediction_text` | String | Résultat de l'attrition : `High` (Risque) ou `Low` (Stable). |
| `probability` | Float | Score de confiance du modèle (0.0 à 1.0). |
| `created_at` | DateTime | Horodatage de la prédiction (UTC). |

> **Note technique** : L'accès à la base de données est géré via l'ORM **SQLAlchemy**. Un mécanisme de sécurité (`try/except`) permet à l'API de continuer à délivrer des prédictions même en cas d'indisponibilité temporaire du serveur de base de données.

---

## 📈 Exploitation Analytique

Le stockage des données en base répond à trois besoins métier majeurs identifiés pour TechNova :

1. **Audit RH** : Pouvoir justifier a posteriori pourquoi un collaborateur a été identifié comme "à risque" en retrouvant ses caractéristiques à l'instant T.
2. **Monitoring du Data Drift (Dérive)** : En analysant l'évolution des `probability` moyennes sur plusieurs mois, l'équipe Data Science peut détecter si le comportement des employés change, signalant qu'un ré-entraînement du modèle est nécessaire.
3. **Dashboarding Décisionnel** : La table est structurée pour être connectée directement à des outils de BI (PowerBI, Tableau) afin de visualiser la répartition des risques par département ou par niveau de salaire.