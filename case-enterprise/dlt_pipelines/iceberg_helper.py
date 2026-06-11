import os
from pyiceberg.catalog import load_catalog
import pyarrow.json as paj
import pyarrow as pa
from pyarrow.fs import S3FileSystem, FileSelector

def get_catalog():
    return load_catalog(
        "default",
        **{
            "uri": os.environ.get("PYICEBERG_CATALOG__DEFAULT__URI", "http://iceberg-rest:8181"),
            "s3.endpoint": os.environ.get("PYICEBERG_CATALOG__DEFAULT__S3__ENDPOINT", "http://minio:9000"),
            "s3.access-key-id": os.environ.get("PYICEBERG_CATALOG__DEFAULT__S3__ACCESS_KEY_ID", "minioadmin"),
            "s3.secret-access-key": os.environ.get("PYICEBERG_CATALOG__DEFAULT__S3__SECRET_ACCESS_KEY", "minioadmin"),
            "py-io-impl": "pyiceberg.io.pyarrow.PyArrowFileIO",
        }
    )

def register_jsonl_as_iceberg(catalog, s3_fs, namespace, table_name, s3_dir):
    """Scan DLT filesystem target folder in S3 for JSONL files and register as Iceberg table"""
    try:
        file_infos = s3_fs.get_file_info(FileSelector(s3_dir, recursive=True))
    except Exception as e:
        print(f"⚠️ Failed to list directory {s3_dir}: {e}")
        return

    jsonl_files = [f.path for f in file_infos if f.type == 2 and (f.path.endswith(".jsonl") or f.path.endswith(".jsonl.gz"))]
    if not jsonl_files:
        print(f"⚠️ No jsonl files found in {s3_dir} for {table_name}")
        return

    print(f"Reading schema and files from {len(jsonl_files)} JSONL files in {s3_dir}...")
    all_tables = []
    for f in jsonl_files:
        with s3_fs.open_input_stream(f) as stream:
            table = paj.read_json(stream)
            all_tables.append(table)

    combined_table = pa.concat_tables(all_tables)
    arrow_schema = combined_table.schema

    # Create namespace if not exists
    try:
        catalog.create_namespace(namespace)
    except Exception:
        pass  # already exists

    table_fullname = f"{namespace}.{table_name}"
    
    # Check if table exists, drop to re-create for the demo
    try:
        catalog.drop_table(table_fullname)
    except Exception:
        pass

    # Create and load
    iceberg_table = catalog.create_table(
        table_fullname,
        schema=arrow_schema,
    )
    
    iceberg_table.overwrite(combined_table)
    print(f"✅ Registered Iceberg table {table_fullname} containing {len(combined_table)} rows.")

def register_all():
    print("Initializing PyIceberg catalog connection...")
    catalog = get_catalog()
    
    s3_fs = S3FileSystem(
        endpoint_override=os.environ.get("PYICEBERG_CATALOG__DEFAULT__S3__ENDPOINT", "http://minio:9000"),
        access_key=os.environ.get("PYICEBERG_CATALOG__DEFAULT__S3__ACCESS_KEY_ID", "minioadmin"),
        secret_key=os.environ.get("PYICEBERG_CATALOG__DEFAULT__S3__SECRET_ACCESS_KEY", "minioadmin")
    )
    
    tables = [
        ("sales_orders", "sales_orders"),
        ("sales_items", "sales_items"),
        ("customers", "customers"),
        ("inventory_movements", "inventory_movements"),
        ("materials", "materials"),
        ("distributors", "distributors"),
        ("ecommerce_orders", "ecommerce_orders"),
        ("gl_postings", "gl_postings")
    ]
    
    for table_name, folder_name in tables:
        target_dir = f"lakehouse/raw/raw/{folder_name}"
        register_jsonl_as_iceberg(catalog, s3_fs, "sap", table_name, target_dir)

if __name__ == "__main__":
    register_all()
