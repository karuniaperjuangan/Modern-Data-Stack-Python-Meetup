import os
import ibis
import models

def main():
    print("Starting Ibis execution on Enterprise catalog (DuckDB S3 REST Catalog)...")
    
    # Configure S3/MinIO environment keys for DuckDB
    # Inside container, standard configuration parameters can be set via env variables
    
    # We will connect Ibis to the temporary analytics duckdb database
    # Which was generated and used by dbt in /tmp/pji_analytics.duckdb
    db_path = "/data/duckdb/pji_analytics.duckdb"
    
    con = ibis.duckdb.connect(db_path)
    
    # Configure MinIO connection
    con.raw_sql(f"""
        INSTALL iceberg; LOAD iceberg;
        INSTALL httpfs; LOAD httpfs;
        SET unsafe_enable_version_guessing = true;
        CREATE SECRET (
            TYPE S3,
            KEY_ID '{os.environ.get("MINIO_ROOT_USER", "minioadmin")}',
            SECRET '{os.environ.get("MINIO_ROOT_PASSWORD", "minioadmin")}',
            ENDPOINT '{os.environ.get("MINIO_ENDPOINT", "minio:9000").replace("http://", "")}',
            URL_STYLE 'path',
            USE_SSL false
        );
    """)
    
    # Register/map the intermediate dbt tables in duckdb to enable Ibis to query them
    # Ibis can register existing views/tables automatically once connected to duckdb
    
    print("Executing channel_sales_mix transform...")
    sales_mix = models.channel_sales_mix(con)
    # Materialize output into the local DuckDB database under analytics schema
    con.raw_sql("CREATE SCHEMA IF NOT EXISTS analytics;")
    
    # We can write these results to analytics.channel_sales_mix
    con.create_table("channel_sales_mix", sales_mix, database="analytics", overwrite=True)
    print("Materialized channel_sales_mix")
    
    print("Executing brand_margin_analysis transform...")
    brand_margin = models.brand_margin_analysis(con)
    con.create_table("brand_margin_analysis", brand_margin, database="analytics", overwrite=True)
    print("Materialized brand_margin_analysis")
    
    print("Executing regional_performance transform...")
    regional = models.regional_performance(con)
    con.create_table("regional_performance", regional, database="analytics", overwrite=True)
    print("Materialized regional_performance")
    
    print("Executing distributor_scorecard transform...")
    distributor = models.distributor_scorecard(con)
    con.create_table("distributor_scorecard", distributor, database="analytics", overwrite=True)
    print("Materialized distributor_scorecard")
    
    print("✅ Ibis transformations successfully completed!")

if __name__ == "__main__":
    main()
