import os
import dlt
from dlt.sources.sql_database import sql_database

def run_pipeline():
    # Fetch PostgreSQL credentials from local config or fallback to compose env
    credentials = os.environ.get(
        "ERP_DATABASE_URL", 
        "postgresql://erp_user:erp_password_2024@postgres:5432/erp_db"
    )
    
    # Read tables from sap schema
    source = sql_database(
        credentials=credentials,
        schema="sap",
        table_names=["sales_orders", "sales_items", "customers"],
    )

    pipeline = dlt.pipeline(
        pipeline_name="erp_sales",
        destination="filesystem",
        dataset_name="raw"
    )

    load_info = pipeline.run(source)
    print(f"Sales pipeline completed: {load_info}")
    return load_info

if __name__ == "__main__":
    run_pipeline()
