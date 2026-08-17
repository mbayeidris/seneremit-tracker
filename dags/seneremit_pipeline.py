from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

import sys
sys.path.append("/opt/airflow/ingestion")

default_args = {
    "owner": "data-engineer",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="seneremid_dag",                          # choisissez un identifiant clair
    default_args=default_args,
    schedule_interval="0 7 * * *",                # rappelez-vous la syntaxe cron, quel rythme voulez-vous ?
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["seneremit"],
) as dag:

    def run_ingestion():
        from ingest import run
        run()

    extract_and_load = PythonOperator(
        task_id="extract_and_load_raw_data",
        python_callable=run_ingestion,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt_project && dbt run --profiles-dir /opt/airflow/dbt_project/profiles_docker",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt_project && dbt test --profiles-dir /opt/airflow/dbt_project/profiles_docker",
    )

    extract_and_load >> dbt_run >> dbt_test           # dans quel ordre doivent s'enchaîner les 3 tâches ?