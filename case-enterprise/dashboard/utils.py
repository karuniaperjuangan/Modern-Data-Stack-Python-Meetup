import os
import duckdb
import pandas as pd
import streamlit as st

def query_df(sql: str) -> pd.DataFrame:
    db_path = "/data/duckdb/pji_analytics.duckdb"
    
    with duckdb.connect(db_path) as con:
        con.execute("INSTALL iceberg; LOAD iceberg; INSTALL httpfs; LOAD httpfs;")
        con.execute("SET unsafe_enable_version_guessing = true;")
        con.execute(f"""
            CREATE OR REPLACE SECRET (
                TYPE S3,
                KEY_ID '{os.environ.get("MINIO_ROOT_USER", "minioadmin")}',
                SECRET '{os.environ.get("MINIO_ROOT_PASSWORD", "minioadmin")}',
                ENDPOINT '{os.environ.get("MINIO_ENDPOINT", "minio:9000").replace("http://", "").replace("https://", "")}',
                URL_STYLE 'path',
                USE_SSL false
            );
        """)
        
        marts_tables = [
            "mart_brand_performance",
            "mart_channel_comparison",
            "mart_distribution_network",
            "mart_executive_summary",
            "mart_inventory_optimization"
        ]
        for table in marts_tables:
            con.execute(f"CREATE OR REPLACE VIEW {table} AS SELECT * FROM iceberg_scan('s3://lakehouse/warehouse/marts/{table}');")
            
        return con.execute(sql).fetchdf()
