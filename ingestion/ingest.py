import os
from datetime import date

import pandas as pd
import requests
from sqlalchemy import create_engine
from sqlalchemy import text

INGESTION_DIR = os.path.dirname(os.path.abspath(__file__))

# NOUVEAU CONCEPT : create_engine() est l'objet SQLAlchemy qui sait parler à PostgreSQL.
# Le format est : postgresql+psycopg2://user:password@host:port/nom_db
# Reprenez les identifiants EXACTS que vous avez mis dans votre docker-compose.yml
# pour le service postgres_warehouse
# ENGINE = create_engine("postgresql+psycopg2://postgres_user:postgres_password@localhost:5432/seneremit_db")

DB_HOST = os.getenv("PG_HOST", "localhost")
ENGINE = create_engine(f"postgresql+psycopg2://postgres_user:postgres_password@{DB_HOST}:5432/seneremit_db")


def load_worldbank_data():
    """Charge, harmonise et filtre les données Banque Mondiale pour le Sénégal."""
    # Reprenez ICI exactement la logique que vous avez déjà écrite et testée
    # dans explore.py (les 2 pd.read_excel, le mapping, le rename, le concat)
    # jusqu'à obtenir df_senegal_all

    # ... votre code d'harmonisation ...
    # df_recent = pd.read_excel("ingestion/rpw_dataset_2011_2025_q1.xlsx", sheet_name="Dataset (from Q2 2016)")
    # df_old = pd.read_excel("ingestion/rpw_dataset_2011_2025_q1.xlsx", sheet_name="Dataset (up to Q1 2016)")
    excel_path = os.path.join(INGESTION_DIR, "rpw_dataset_2011_2025_q1.xlsx")
    df_recent = pd.read_excel(excel_path, sheet_name="Dataset (from Q2 2016)")
    df_old = pd.read_excel(excel_path, sheet_name="Dataset (up to Q1 2016)")

    senegal = df_recent[df_recent["destination_name"] == "Senegal"]
    senegal_old = df_old[df_old["destination_name"] == "Senegal"]

    mapping = {
        "product": "payment instrument",
        "sending location": "access point",
        "coverage": "receiving network coverage",
        "note1": "Standard Note",
        "pick-up method": "pickup method",
    }

    senegal_old_renamed = senegal_old.rename(columns=mapping)
    senegal_old_renamed["pickup location"] = None

    df_senegal_all = pd.concat([senegal_old_renamed, senegal], ignore_index=True)

    colonnes_a_garder = [
        "period", "source_name", "destination_name", "firm", "firm_type",
        "payment instrument", "cc1 denomination amount", "cc1 total cost %",
        "cc1 lcu fee", "cc2 denomination amount", "cc2 total cost %",
        "cc2 lcu fee", "date", "corridor",
    ]
    df_final = df_senegal_all[colonnes_a_garder]  # comment sélectionner une liste de colonnes sur un DataFrame ?

    # df_final.to_sql("raw_worldbank_remittances", ENGINE, schema="raw", if_exists="replace", index=False)
    with ENGINE.begin() as conn:
        conn.execute(text("TRUNCATE TABLE raw.raw_worldbank_remittances"))

    df_final.to_sql("raw_worldbank_remittances", ENGINE, schema="raw", if_exists="append", index=False)
    print(f"[OK] {len(df_final)} lignes chargées dans raw.raw_worldbank_remittances")


def load_local_tariffs():
    """Charge les vrais tarifs Wave / Orange Money."""
    path = os.path.join(INGESTION_DIR, "tarifs_locaux.csv")
    df = pd.read_csv(path)  # quelle fonction pandas pour lire un CSV ?
    # df.to_sql("raw_fintech_tariffs", ENGINE, schema="raw", if_exists="replace", index=False)
    with ENGINE.begin() as conn:
            conn.execute(text("TRUNCATE TABLE raw.raw_fintech_tariffs"))
    
    df.to_sql("raw_fintech_tariffs", ENGINE, schema="raw", if_exists="append", index=False)
    print(f"[OK] {len(df)} lignes chargées dans raw.raw_fintech_tariffs")


def load_exchange_rates():
    rows = []
    for base in ["EUR", "USD"]:
        resp = requests.get(f"https://api.frankfurter.dev/v2/rate/{base}/XOF")
        data = resp.json()
        print(data)  # gardez ce print pour vérifier la structure au premier essai
        rows.append({
            "devise_origine": data['base'],
            "devise_cible": data['quote'],
            "taux": data['rate'],
            "date_taux": data['date'],
        })

    df = pd.DataFrame(rows)
    # df.to_sql("raw_exchange_rates", ENGINE, schema="raw", if_exists="replace", index=False)
    with ENGINE.begin() as conn:
        conn.execute(text("TRUNCATE TABLE raw.raw_exchange_rates"))
        
    df.to_sql("raw_exchange_rates", ENGINE, schema="raw", if_exists="append", index=False)
    print(f"[OK] {len(df)} lignes chargées dans raw.raw_exchange_rates")

# def create_schemas():
#     with ENGINE.connect() as conn:
#         conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
#         conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging"))
#         conn.execute(text("CREATE SCHEMA IF NOT EXISTS analytics"))
#         conn.commit()

def create_schemas():
    with ENGINE.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS analytics"))


# if __name__ == "__main__":
#     create_schemas()
#     load_worldbank_data()
#     load_local_tariffs()
#     load_exchange_rates()

def run():
    create_schemas()
    load_worldbank_data()
    load_local_tariffs()
    load_exchange_rates()


if __name__ == "__main__":
    run()