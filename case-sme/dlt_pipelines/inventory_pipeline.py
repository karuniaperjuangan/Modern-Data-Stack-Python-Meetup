import os
import dlt
import psycopg2
from psycopg2.extras import RealDictCursor

@dlt.source
def inventory_source():
    """Source: Inventory system data source (simulating extraction from raw Postgres tables)"""

    @dlt.resource(name="branches", write_disposition="replace", primary_key="branch_id")
    def branches_resource():
        db_url = os.environ.get("DATABASE_URL", "postgresql://sme_user:sme_password_2024@postgres:5432/sme_db")
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        cur.execute("SELECT * FROM raw.branches;")
        for row in cur.fetchall():
            if row.get("opened_date"):
                row["opened_date"] = row["opened_date"].isoformat()
            yield row
        cur.close()
        conn.close()

    @dlt.resource(name="products", write_disposition="replace", primary_key="product_id")
    def products_resource():
        db_url = os.environ.get("DATABASE_URL", "postgresql://sme_user:sme_password_2024@postgres:5432/sme_db")
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        cur.execute("SELECT * FROM raw.products;")
        for row in cur.fetchall():
            yield row
        cur.close()
        conn.close()

    @dlt.resource(name="suppliers", write_disposition="replace", primary_key="supplier_id")
    def suppliers_resource():
        db_url = os.environ.get("DATABASE_URL", "postgresql://sme_user:sme_password_2024@postgres:5432/sme_db")
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        cur.execute("SELECT * FROM raw.suppliers;")
        for row in cur.fetchall():
            yield row
        cur.close()
        conn.close()

    @dlt.resource(name="ingredients", write_disposition="replace", primary_key="ingredient_id")
    def ingredients_resource():
        db_url = os.environ.get("DATABASE_URL", "postgresql://sme_user:sme_password_2024@postgres:5432/sme_db")
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        cur.execute("SELECT * FROM raw.ingredients;")
        for row in cur.fetchall():
            yield row
        cur.close()
        conn.close()

    @dlt.resource(name="inventory", write_disposition="merge", primary_key="inventory_id")
    def inventory_resource(last_updated=dlt.sources.incremental("last_updated", initial_value="2010-01-01T00:00:00Z")):
        db_url = os.environ.get("DATABASE_URL", "postgresql://sme_user:sme_password_2024@postgres:5432/sme_db")
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        query = "SELECT * FROM raw.inventory WHERE last_updated > %s ORDER BY last_updated;"
        cur.execute(query, (last_updated.last_value,))
        for row in cur.fetchall():
            if row.get("last_updated"):
                row["last_updated"] = row["last_updated"].isoformat()
            yield row
        cur.close()
        conn.close()

    return branches_resource, products_resource, suppliers_resource, ingredients_resource, inventory_resource

def run_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="sme_inventory",
        destination="postgres",
        dataset_name="raw_dlt"
    )
    load_info = pipeline.run(inventory_source())
    print(f"DLT Inventory Pipeline completed: {load_info}")
    return load_info

if __name__ == "__main__":
    run_pipeline()
