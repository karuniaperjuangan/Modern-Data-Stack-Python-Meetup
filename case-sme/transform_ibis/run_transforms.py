import os
import ibis
import models

def main():
    print("Starting Ibis transformations execution...")
    
    # Read Postgres credentials from environment
    db_user = os.environ.get("POSTGRES_USER", "sme_user")
    db_pass = os.environ.get("POSTGRES_PASSWORD", "sme_password_2024")
    db_host = os.environ.get("POSTGRES_HOST", "postgres")
    db_port = int(os.environ.get("POSTGRES_PORT", 5432))
    db_name = os.environ.get("POSTGRES_DB", "sme_db")
    
    # Connect using Ibis
    con = ibis.postgres.connect(
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
        database=db_name
    )
    
    # Create the analytics schema if not exists
    with con.raw_sql("CREATE SCHEMA IF NOT EXISTS analytics;") as cursor:
        pass
        
    # Run and materialize daily_revenue
    print("Executing daily_revenue transform...")
    rev_expr = models.daily_revenue(con)
    con.create_table("daily_revenue", rev_expr, database="analytics", overwrite=True)
    print("Materialized daily_revenue into analytics.daily_revenue")
    
    # Run and materialize menu_popularity
    print("Executing menu_popularity transform...")
    pop_expr = models.menu_popularity(con)
    con.create_table("menu_popularity", pop_expr, database="analytics", overwrite=True)
    print("Materialized menu_popularity into analytics.menu_popularity")
    
    # Run and materialize peak_hours
    print("Executing peak_hours transform...")
    peak_expr = models.peak_hours(con)
    con.create_table("peak_hours", peak_expr, database="analytics", overwrite=True)
    print("Materialized peak_hours into analytics.peak_hours")
    
    # Run and materialize branch_comparison
    print("Executing branch_comparison transform...")
    comp_expr = models.branch_comparison(con)
    con.create_table("branch_comparison", comp_expr, database="analytics", overwrite=True)
    print("Materialized branch_comparison into analytics.branch_comparison")
    
    print("✅ Ibis transformations successfully materialized!")

if __name__ == "__main__":
    main()
