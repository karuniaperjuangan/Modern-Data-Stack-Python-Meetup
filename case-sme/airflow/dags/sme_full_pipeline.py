from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys

# Insert dependencies path
sys.path.insert(0, '/opt/airflow')

default_args = {
    'owner': 'sme-data-team',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'sme_full_pipeline',
    default_args=default_args,
    description='Full refresh pipeline: seed -> dlt -> dbt -> ibis',
    schedule_interval=None, # Manual trigger
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['sme', 'full-refresh'],
) as dag:

    def run_seeding():
        from seed.generate_data import main as seed_main
        seed_main()

    def run_dlt_pos():
        from dlt_pipelines.pos_pipeline import run_pipeline
        run_pipeline()

    def run_dlt_inventory():
        from dlt_pipelines.inventory_pipeline import run_pipeline
        run_pipeline()

    def run_ibis_transforms():
        from transform_ibis.run_transforms import main as ibis_main
        ibis_main()

    seed_data = PythonOperator(
        task_id='seed_data',
        python_callable=run_seeding,
    )

    dlt_pos = PythonOperator(
        task_id='dlt_pos_ingest',
        python_callable=run_dlt_pos,
    )

    dlt_inventory = PythonOperator(
        task_id='dlt_inventory_ingest',
        python_callable=run_dlt_inventory,
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/transform_dbt && dbt run --profiles-dir .',
    )

    ibis_transforms = PythonOperator(
        task_id='ibis_transforms',
        python_callable=run_ibis_transforms,
    )

    # Dependencies
    seed_data >> [dlt_pos, dlt_inventory] >> dbt_run >> ibis_transforms
