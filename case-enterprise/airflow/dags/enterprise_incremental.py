from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys

sys.path.insert(0, '/opt/airflow')

default_args = {
    'owner': 'pji-data-team',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'enterprise_incremental_pipeline',
    default_args=default_args,
    description='Incremental updates: dlt (sales & ecommerce) -> register Iceberg -> dbt -> ibis',
    schedule_interval='*/30 * * * *', # Every 30 minutes
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['enterprise', 'incremental'],
) as dag:

    def run_dlt_sales():
        from dlt_pipelines.erp_sales_pipeline import run_pipeline
        run_pipeline()

    def run_dlt_ecommerce():
        from dlt_pipelines.ecommerce_pipeline import run_pipeline
        run_pipeline()

    def register_iceberg_tables():
        from dlt_pipelines.iceberg_helper import register_all
        register_all()

    def run_ibis_transforms():
        from transform_ibis.run_transforms import main as ibis_main
        ibis_main()

    dlt_sales = PythonOperator(
        task_id='dlt_sales_incremental',
        python_callable=run_dlt_sales,
    )

    dlt_ecommerce = PythonOperator(
        task_id='dlt_ecommerce_incremental',
        python_callable=run_dlt_ecommerce,
    )

    register_iceberg = PythonOperator(
        task_id='register_iceberg_tables',
        python_callable=register_iceberg_tables,
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/transform_dbt && dbt run --profiles-dir .',
    )

    ibis_transforms = PythonOperator(
        task_id='ibis_transforms',
        python_callable=run_ibis_transforms,
    )

    [dlt_sales, dlt_ecommerce] >> register_iceberg >> dbt_run >> ibis_transforms
