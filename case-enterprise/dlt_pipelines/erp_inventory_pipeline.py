import os
import dlt
from dlt.sources.sql_database import sql_database

def run_pipeline():
    credentials = os.environ.get(
        "ERP_DATABASE_URL", 
        "postgresql://erp_user:erp_password_2024@postgres:5432/erp_db"
    )
    
    source = sql_database(
        credentials=credentials,
        schema="sap",
        table_names=["inventory_movements", "materials", "distributors"],
    )

    pipeline = dlt.pipeline(
        pipeline_name="erp_inventory",
        destination="filesystem",
        dataset_name="raw"
    )

    load_info = pipeline.run(source)
    print(f"Inventory pipeline completed: {load_info}")
    return load_info

if __name__ == "__main__":
    run_pipeline()
