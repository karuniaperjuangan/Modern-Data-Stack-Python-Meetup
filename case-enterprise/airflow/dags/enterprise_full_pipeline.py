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
    'enterprise_full_pipeline',
    default_args=default_args,
    description='Full refresh: seed -> dlt -> register Iceberg -> dbt -> ibis',
    schedule_interval=None, # Manual trigger
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['enterprise', 'full-refresh'],
) as dag:

    def run_seeding():
        from seed.generate_data import main as seed_main
        seed_main()

    def run_dlt_sales():
        from dlt_pipelines.erp_sales_pipeline import run_pipeline
        run_pipeline()

    def run_dlt_inventory():
        from dlt_pipelines.erp_inventory_pipeline import run_pipeline
        run_pipeline()

    def run_dlt_finance():
        from dlt_pipelines.erp_finance_pipeline import run_pipeline
        run_pipeline()

    def run_dlt_ecommerce():
        from dlt_pipelines.ecommerce_pipeline import run_pipeline
        run_pipeline()

    def register_iceberg_tables():
        from dlt_pipelines.iceberg_helper import register_all
        register_all()

    def register_marts_iceberg_tables():
        from dlt_pipelines.iceberg_helper import register_marts
        register_marts()

    def run_ibis_transforms():
        from transform_ibis.run_transforms import main as ibis_main
        ibis_main()

    seed = PythonOperator(
        task_id='seed_erp_data',
        python_callable=run_seeding,
    )

    dlt_sales = PythonOperator(
        task_id='dlt_sales_ingest',
        python_callable=run_dlt_sales,
    )

    dlt_inventory = PythonOperator(
        task_id='dlt_inventory_ingest',
        python_callable=run_dlt_inventory,
    )

    dlt_finance = PythonOperator(
        task_id='dlt_finance_ingest',
        python_callable=run_dlt_finance,
    )

    dlt_ecommerce = PythonOperator(
        task_id='dlt_ecommerce_ingest',
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

    register_marts_iceberg = PythonOperator(
        task_id='register_marts_iceberg_tables',
        python_callable=register_marts_iceberg_tables,
    )

    ibis_transforms = PythonOperator(
        task_id='ibis_transforms',
        python_callable=run_ibis_transforms,
    )

    # Dependencies
    seed >> [dlt_sales, dlt_inventory, dlt_finance, dlt_ecommerce]
    [dlt_sales, dlt_inventory, dlt_finance, dlt_ecommerce] >> register_iceberg
    register_iceberg >> dbt_run >> register_marts_iceberg >> ibis_transforms
