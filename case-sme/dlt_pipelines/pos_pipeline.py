import os
import dlt
import psycopg2
from psycopg2.extras import RealDictCursor

@dlt.source
def pos_source():
    """Source: POS system data source (simulating extraction from raw Postgres tables)"""

    @dlt.resource(name="orders", write_disposition="merge", primary_key="order_id")
    def orders_resource(order_date=dlt.sources.incremental("order_date", initial_value="2010-01-01T00:00:00Z")):
        """Incremental load of orders based on order_date"""
        db_url = os.environ.get("DATABASE_URL", "postgresql://sme_user:sme_password_2024@postgres:5432/sme_db")
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        
        # Query only orders newer than the last loaded order_date
        query = "SELECT * FROM raw.orders WHERE order_date > %s ORDER BY order_date;"
        cur.execute(query, (order_date.last_value,))
        
        while True:
            rows = cur.fetchmany(1000)
            if not rows:
                break
            for row in rows:
                # convert datetime to isoformat string for compatibility
                if row.get("order_date"):
                    row["order_date"] = row["order_date"].isoformat()
                yield row
                
        cur.close()
        conn.close()

    @dlt.resource(name="order_items", write_disposition="merge", primary_key="item_id")
    def order_items_resource():
        """Full load of order items for matching orders (for demonstration)"""
        db_url = os.environ.get("DATABASE_URL", "postgresql://sme_user:sme_password_2024@postgres:5432/sme_db")
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        
        query = "SELECT * FROM raw.order_items;"
        cur.execute(query)
        
        while True:
            rows = cur.fetchmany(1000)
            if not rows:
                break
            for row in rows:
                yield row
                
        cur.close()
        conn.close()

    return orders_resource, order_items_resource

def run_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="sme_pos",
        destination="postgres",
        dataset_name="raw_dlt" # writes into a schema raw_dlt to demonstrate dlt staging
    )
    load_info = pipeline.run(pos_source())
    print(f"DLT POS Pipeline completed: {load_info}")
    return load_info

if __name__ == "__main__":
    run_pipeline()
