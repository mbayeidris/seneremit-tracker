# SeneRemit-Tracker

🇬🇧 English version (this page) · 🇫🇷 [Version française](README.md)

A Modern Data Stack pipeline analyzing the real cost of sending money to Senegal — international transfers (France, Italy) and local transfers (Wave, Orange Money).

**How much does it really cost to send money to Senegal?** This project answers that question with real data: 2,000+ transactions (2011–2025, World Bank source), analyzed end-to-end, from raw ingestion to an interactive dashboard.

> 📊 [View the Power BI dashboard](https://app.powerbi.com/view?r=eyJrIjoiNTlkYzg3YzYtNDI3MC00NmJiLWE0NjQtMDc3MjNlMzc5ZDEzIiwidCI6ImYxYTRjMTkxLTNhNDEtNDAxOC05NzdmLTkyMWMzMGI0MzQ4NCJ9) · 📄 [View the LinkedIn post](#)

---

## The result at a glance

The average transfer cost ranges from **0.14%** (Moneybookers) to **9.86%** (Crédit Agricole) depending on the operator — a 70x difference to send the exact same amount, to the same destination.

![SeneRemit Pulse Dashboard](docs/dashboard.png)

---

## Architecture

```
[ World Bank Excel ]    ─┐
[ Wave/Orange CSV ]      ─┼─( Python )─> [ PostgreSQL: raw schema ]
[ Exchange rate API ]    ─┘                        │
                                          (orchestrated by Airflow)
                                                     │
                                                     ▼
                                    [ dbt: staging → marts (analytics) ]
                                                     │
                                                     ▼
                                        [ Power BI Dashboard ]
```

![dbt lineage graph](docs/lineage_graph.png)

## Tech stack

`Python` (pandas, requests, SQLAlchemy) · `PostgreSQL` · `dbt Core` · `Apache Airflow` · `Docker & Docker Compose` · `Power BI`

## Project structure

```
seneremit-tracker/
├── docker-compose.yml          # PostgreSQL (meta + warehouse) + Airflow, 5 services
├── ingestion/
│   ├── ingest.py                 # ingestion of the 3 sources into PostgreSQL (raw schema)
│   └── tarifs_locaux.csv         # real Wave / Orange Money rates (manually verified)
├── dags/
│   └── seneremit_pipeline.py     # Airflow DAG: ingestion → dbt run → dbt test
└── dbt_project/
    ├── dbt_project.yml
    ├── packages.yml               # dbt_utils
    ├── macros/
    │   └── generate_schema_name.sql   # avoids dbt's default schema concatenation
    ├── profiles_docker/
    │   └── profiles.yml.example  # copy to profiles.yml with your own credentials
    └── models/
        ├── staging/                # cleaning of the 3 raw sources, 11 tests
        └── marts/
            └── fct_remittance_costs.sql   # fact table, 1,983 rows, % and XOF
```

## Data

| Source | Content | Access |
|---|---|---|
| **World Bank — Remittance Prices Worldwide** | 2011–2025, France/Italy → Senegal corridors, 41 operators | [Official download](https://remittanceprices.worldbank.org/data-download) — place it in `ingestion/rpw_dataset_2011_2025_q1.xlsx` (not versioned, ~250k rows) |
| **Wave / Orange Money** | Real fee schedules, verified via the app and official terms | `ingestion/tarifs_locaux.csv` |
| **EUR/USD → XOF exchange rates** | Daily rate | [Frankfurter](https://frankfurter.dev) API (free, no key required) |

⚠️ The two sheets of the World Bank file (before/after Q2 2016) have different column schemas — `ingest.py` harmonizes them before loading.

## Installation

### 1. Infrastructure

```bash
docker compose up -d
```

Check `http://localhost:8080` (Airflow, credentials `airflow`/`airflow`).

### 2. Database

The `raw`, `staging`, and `analytics` schemas are created automatically on the first run of `ingest.py`.

### 3. Ingestion (manual test)

```bash
python -m venv venv
venv\Scripts\Activate.ps1          # Windows
pip install -r requirements.txt
python ingestion/ingest.py
```

### 4. dbt

```bash
cd dbt_project
cp profiles_docker/profiles.yml.example ~/.dbt/profiles.yml   # set host to "localhost" for local (non-Docker) use
dbt deps
dbt run
dbt test
dbt docs generate && dbt docs serve
```

### 5. Automated orchestration

Enable the `seneremid_dag` DAG in the Airflow UI — it chains `ingest.py` → `dbt run` → `dbt test`, scheduled daily.

## Data quality

- **15 dbt tests** on the marts models (`not_null`, `accepted_values`, `dbt_utils.accepted_range`)
- **11 tests** on the staging models
- Auto-generated documentation (`dbt docs`), full lineage graph

Some costs in the dataset are **negative** (e.g. Western Union, card payment, summer 2022) — verified against the raw data, these are legitimate temporary promotions documented by the World Bank's methodology, not a pipeline error.

## Notable technical decisions

- **`TRUNCATE` + `if_exists="append"`**, never `if_exists="replace"` when dbt views depend on the table — `replace` attempts a `DROP TABLE`, which fails if a `staging` view already depends on it.
- **`ENGINE.begin()`** instead of `connect()` + manual `commit()` — compatible with both SQLAlchemy 1.4 and 2.0 (Airflow ships a different version than the local environment).
- **`PG_HOST` as an environment variable** — the same `ingest.py` runs on the host machine (`localhost`) and inside the Airflow container (`postgres_warehouse`) without any code change.
- **Custom `generate_schema_name` macro** — avoids dbt's default schema concatenation (`analytics_staging` instead of `staging`).
- **Shared `AIRFLOW__WEBSERVER__SECRET_KEY`** across all 3 Airflow services — required for the webserver to read logs generated by the scheduler.

## Known limitations & next steps

- International corridors limited to France/Italy → Senegal (actual scope of the World Bank dataset)
- Wave/Orange Money rates are not historized — a `dbt snapshot` (SCD Type 2) would allow tracking their evolution over time
- Incremental models to consider for World Bank ingestion, which grows every quarter
- Scheduled execution depends on local Docker availability — a cloud deployment (VM or Cloud Composer) would guarantee 24/7 execution

## Author

Idrissa Mbaye — Data Analyst - Junior Data Engineer — [LinkedIn](https://www.linkedin.com/in/idrissa-mbaye) · [GitHub](https://github.com/mbayeidris)

