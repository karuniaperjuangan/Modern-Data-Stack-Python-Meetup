from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys

sys.path.insert(0, '/opt/airflow')

default_args = {
    'owner': 'sme-data-team',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'sme_incremental_pipeline',
    default_args=default_args,
    description='Incremental pipeline: dlt -> dbt -> ibis',
    schedule_interval='0 5 * * *', # Daily at 05:00 WIB
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['sme', 'incremental'],
) as dag:

    def run_dlt_pos():
        from dlt_pipelines.pos_pipeline import run_pipeline
        run_pipeline()

    def run_dlt_inventory():
        from dlt_pipelines.inventory_pipeline import run_pipeline
        run_pipeline()

    def run_ibis_transforms():
        from transform_ibis.run_transforms import main as ibis_main
        ibis_main()

    dlt_pos = PythonOperator(
        task_id='dlt_pos_incremental',
        python_callable=run_dlt_pos,
    )

    dlt_inventory = PythonOperator(
        task_id='dlt_inventory_incremental',
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

    [dlt_pos, dlt_inventory] >> dbt_run >> ibis_transforms
