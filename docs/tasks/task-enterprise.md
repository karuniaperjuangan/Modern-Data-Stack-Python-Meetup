# Implementation Task: Enterprise Case — PT Pesona Jelita Indonesia (PJI Group)

> **Dokumen ini adalah panduan implementasi langkah demi langkah** yang dapat dieksekusi oleh LLM atau developer. Setiap task memiliki input/output yang jelas, file yang harus dibuat, dan kode referensi.

## Overview

| Aspek | Detail |
|:------|:-------|
| **Working Directory** | `case-enterprise/` |
| **OLTP** | PostgreSQL 16 (simulated SAP ERP) |
| **OLAP** | Apache Iceberg (MinIO + REST Catalog) |
| **Port Mapping** | PG: 5433, MinIO API: 9000, MinIO Console: 9001, Iceberg REST: 8181, Airflow: 8080, Streamlit: 8502 |
| **Estimated Time** | 5-6 jam |
| **Docker RAM Required** | Minimum 6 GB |
| **Prerequisites** | Docker Desktop, Docker Compose v2.14+ |

---

## Checklist

- [ ] Task 1: Buat file `.env.example`
- [ ] Task 2: Buat `docker/postgres/init.sql` (simulated SAP tables)
- [ ] Task 3: Buat `docker/postgres/Dockerfile`
- [ ] Task 4: Buat `docker/minio/setup.sh`
- [ ] Task 5: Buat `docker/airflow/Dockerfile`
- [ ] Task 6: Buat `docker/streamlit/Dockerfile`
- [ ] Task 7: Buat `docker-compose.yml`
- [ ] Task 8: Buat `seed/generate_data.py` (enterprise-scale synthetic data)
- [ ] Task 9: Buat `dlt_pipelines/erp_sales_pipeline.py`
- [ ] Task 10: Buat `dlt_pipelines/erp_inventory_pipeline.py`
- [ ] Task 11: Buat `dlt_pipelines/erp_finance_pipeline.py`
- [ ] Task 12: Buat `dlt_pipelines/ecommerce_pipeline.py`
- [ ] Task 13: Buat dlt config files
- [ ] Task 14: Buat dbt project (`transform_dbt/`)
- [ ] Task 15: Buat Ibis transforms (`transform_ibis/`)
- [ ] Task 16: Buat Streamlit dashboard (`dashboard/`)
- [ ] Task 17: Buat Airflow DAGs (`airflow/dags/`)
- [ ] Task 18: Buat `Makefile`
- [ ] Task 19: Buat `case-enterprise/README.md`
- [ ] Task 20: Testing end-to-end

---

## Task 1: Buat `.env.example`

**File**: `case-enterprise/.env.example`

```bash
# =========================================================
# PT Pesona Jelita Indonesia (PJI Group) — Enterprise Stack
# =========================================================
# Copy file ini ke .env sebelum menjalankan docker compose
# cp .env.example .env

# === PostgreSQL (Simulated ERP Source) ===
ERP_POSTGRES_USER=erp_user
ERP_POSTGRES_PASSWORD=erp_password_2024
ERP_POSTGRES_DB=erp_db
ERP_POSTGRES_PORT=5433

# === MinIO (Object Storage) ===
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_ENDPOINT=http://minio:9000
MINIO_BUCKET=lakehouse
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001

# === Iceberg REST Catalog ===
ICEBERG_REST_PORT=8181
ICEBERG_CATALOG_NAME=pji_catalog
ICEBERG_CATALOG_WAREHOUSE=s3://lakehouse/warehouse

# === PostgreSQL (Airflow Metadata) ===
AIRFLOW_PG_USER=airflow
AIRFLOW_PG_PASSWORD=airflow_password_2024
AIRFLOW_PG_DB=airflow_db
AIRFLOW_PG_PORT=5434

# === Airflow ===
AIRFLOW_UID=50000
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__FERNET_KEY=46BKJoQYlPPOexq0OhDZnIlNepKFf87WFwLbfzqDDho=
AIRFLOW__CORE__LOAD_EXAMPLES=false
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow_password_2024@airflow-postgres:5432/airflow_db
AIRFLOW_ADMIN_USER=airflow
AIRFLOW_ADMIN_PASSWORD=airflow

# === Streamlit ===
STREAMLIT_PORT=8502

# === PyIceberg ===
PYICEBERG_CATALOG__DEFAULT__URI=http://iceberg-rest:8181
PYICEBERG_CATALOG__DEFAULT__S3__ENDPOINT=http://minio:9000
PYICEBERG_CATALOG__DEFAULT__S3__ACCESS_KEY_ID=minioadmin
PYICEBERG_CATALOG__DEFAULT__S3__SECRET_ACCESS_KEY=minioadmin
```

---

## Task 2: Buat `docker/postgres/init.sql`

**File**: `case-enterprise/docker/postgres/init.sql`

Script ini membuat tabel-tabel yang **menyerupai tabel SAP** sebagai source system.

```sql
-- =========================================================
-- Simulated SAP S/4HANA Tables
-- =========================================================

CREATE SCHEMA IF NOT EXISTS sap;

-- Customer Master (SAP: KNA1)
CREATE TABLE sap.customers (
    customer_id VARCHAR(20) PRIMARY KEY,    -- SAP: KUNNR
    customer_name VARCHAR(200) NOT NULL,     -- SAP: NAME1
    customer_type VARCHAR(20) NOT NULL,      -- distributor, retailer, modern_trade
    city VARCHAR(100),
    province VARCHAR(100),
    region VARCHAR(50),                      -- Sumatera, Jawa, Kalimantan, etc.
    channel VARCHAR(20),                     -- GT, MT, Ecommerce
    credit_limit DECIMAL(15,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_date DATE DEFAULT CURRENT_DATE
);

-- Distributor Master
CREATE TABLE sap.distributors (
    distributor_id VARCHAR(20) PRIMARY KEY,
    distributor_name VARCHAR(200) NOT NULL,
    region VARCHAR(50),
    province VARCHAR(100),
    city VARCHAR(100),
    credit_limit DECIMAL(15,2) DEFAULT 0,
    contract_start DATE,
    contract_end DATE,
    is_active BOOLEAN DEFAULT true
);

-- Material Master (SAP: MARA + MAKT)
CREATE TABLE sap.materials (
    material_id VARCHAR(20) PRIMARY KEY,     -- SAP: MATNR
    material_name VARCHAR(200) NOT NULL,      -- SAP: MAKTX
    brand VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,            -- skincare, makeup, bodycare, haircare, mensgrooming
    subcategory VARCHAR(100),
    unit_price DECIMAL(12,2) NOT NULL,
    cost_price DECIMAL(12,2) NOT NULL,
    uom VARCHAR(10) DEFAULT 'pcs',           -- SAP: MEINS
    weight_gram DECIMAL(8,2),
    is_active BOOLEAN DEFAULT true,
    launch_date DATE
);

-- Sales Order Header (SAP: VBAK)
CREATE TABLE sap.sales_orders (
    order_id VARCHAR(20) PRIMARY KEY,        -- SAP: VBELN
    customer_id VARCHAR(20) REFERENCES sap.customers(customer_id),
    distributor_id VARCHAR(20) REFERENCES sap.distributors(distributor_id),
    order_date DATE NOT NULL,                -- SAP: AUDAT
    sales_org VARCHAR(10) NOT NULL,          -- SAP: VKORG (1000, 2000, 3000)
    distribution_channel VARCHAR(10),        -- SAP: VTWEG (10=GT, 20=MT, 30=Ecom)
    net_value DECIMAL(15,2) NOT NULL,        -- SAP: NETWR
    currency VARCHAR(5) DEFAULT 'IDR',       -- SAP: WAERK
    status VARCHAR(20) DEFAULT 'created',    -- created, confirmed, delivered, invoiced
    plant VARCHAR(10)                        -- SAP: WERKS (TNG, SMG, SBY)
);

-- Sales Order Items (SAP: VBAP)
CREATE TABLE sap.sales_items (
    item_id VARCHAR(30) PRIMARY KEY,         -- SAP: VBELN + POSNR
    order_id VARCHAR(20) REFERENCES sap.sales_orders(order_id),
    material_id VARCHAR(20) REFERENCES sap.materials(material_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    net_value DECIMAL(15,2) NOT NULL,
    discount_pct DECIMAL(5,2) DEFAULT 0,
    plant VARCHAR(10)                        -- SAP: WERKS
);

-- Inventory Movements (SAP: MSEG)
CREATE TABLE sap.inventory_movements (
    movement_id VARCHAR(20) PRIMARY KEY,     -- SAP: MBLNR + ZEILE
    material_id VARCHAR(20) REFERENCES sap.materials(material_id),
    plant VARCHAR(10) NOT NULL,              -- TNG, SMG, SBY
    movement_type VARCHAR(5) NOT NULL,       -- 101, 201, 301, 601
    quantity DECIMAL(12,2) NOT NULL,
    posting_date DATE NOT NULL,              -- SAP: BUDAT
    batch VARCHAR(20),
    storage_location VARCHAR(10)
);

-- E-commerce Orders (from marketplace APIs)
CREATE TABLE sap.ecommerce_orders (
    ecom_order_id VARCHAR(30) PRIMARY KEY,
    platform VARCHAR(20) NOT NULL,           -- shopee, tokopedia, tiktokshop, lazada
    order_date DATE NOT NULL,
    product_sku VARCHAR(20) REFERENCES sap.materials(material_id),
    quantity INTEGER NOT NULL,
    revenue DECIMAL(12,2) NOT NULL,
    platform_fee DECIMAL(12,2) DEFAULT 0,
    shipping_cost DECIMAL(12,2) DEFAULT 0,
    shipping_city VARCHAR(100),
    shipping_province VARCHAR(100),
    status VARCHAR(20) DEFAULT 'paid'        -- paid, shipped, delivered, returned
);

-- GL Postings (SAP: BSEG)
CREATE TABLE sap.gl_postings (
    posting_id VARCHAR(30) PRIMARY KEY,
    document_number VARCHAR(20),             -- SAP: BELNR
    posting_date DATE NOT NULL,              -- SAP: BUDAT
    gl_account VARCHAR(10) NOT NULL,         -- SAP: HKONT
    gl_account_name VARCHAR(100),
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(5) DEFAULT 'IDR',
    cost_center VARCHAR(20),                 -- SAP: KOSTL
    profit_center VARCHAR(20),               -- SAP: PRCTR
    posting_type VARCHAR(10) NOT NULL        -- debit, credit
);

-- Create indexes
CREATE INDEX idx_sales_orders_date ON sap.sales_orders(order_date);
CREATE INDEX idx_sales_orders_customer ON sap.sales_orders(customer_id);
CREATE INDEX idx_sales_orders_distributor ON sap.sales_orders(distributor_id);
CREATE INDEX idx_sales_items_order ON sap.sales_items(order_id);
CREATE INDEX idx_sales_items_material ON sap.sales_items(material_id);
CREATE INDEX idx_inv_movements_material ON sap.inventory_movements(material_id);
CREATE INDEX idx_inv_movements_date ON sap.inventory_movements(posting_date);
CREATE INDEX idx_ecom_orders_date ON sap.ecommerce_orders(order_date);
CREATE INDEX idx_ecom_orders_platform ON sap.ecommerce_orders(platform);
CREATE INDEX idx_gl_postings_date ON sap.gl_postings(posting_date);
CREATE INDEX idx_gl_postings_account ON sap.gl_postings(gl_account);
```

---

## Task 3: Buat `docker/postgres/Dockerfile`

**File**: `case-enterprise/docker/postgres/Dockerfile`

```dockerfile
FROM postgres:16

COPY init.sql /docker-entrypoint-initdb.d/01-init.sql

ENV POSTGRES_USER=erp_user
ENV POSTGRES_PASSWORD=erp_password_2024
ENV POSTGRES_DB=erp_db
```

---

## Task 4: Buat `docker/minio/setup.sh`

**File**: `case-enterprise/docker/minio/setup.sh`

Script yang dijalankan setelah MinIO ready untuk membuat bucket.

```bash
#!/bin/bash
set -e

echo "Waiting for MinIO to be ready..."
until mc alias set local http://minio:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD} 2>/dev/null; do
    echo "MinIO not ready yet, retrying in 2 seconds..."
    sleep 2
done

echo "Creating lakehouse bucket..."
mc mb local/lakehouse --ignore-existing

echo "Setting bucket policy to public (for demo)..."
mc anonymous set public local/lakehouse

echo "✅ MinIO setup complete!"
mc ls local/
```

---

## Task 5: Buat `docker/airflow/Dockerfile`

**File**: `case-enterprise/docker/airflow/Dockerfile`

```dockerfile
FROM apache/airflow:3.0.1-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python dependencies
RUN pip install --no-cache-dir \
    "dlt[filesystem]" \
    "dbt-duckdb>=0.9" \
    "ibis-framework[duckdb]" \
    "pyiceberg[s3fs,pyarrow]" \
    "pyarrow" \
    "psycopg2-binary" \
    "faker" \
    "plotly" \
    "streamlit" \
    "duckdb" \
    "sqlalchemy" \
    "s3fs" \
    "boto3"
```

> **Catatan**: JRE diperlukan oleh beberapa komponen Iceberg. Jika image terlalu besar, bisa dihilangkan dan gunakan pure PyIceberg (Python-only).

> **Catatan untuk executor**: Gunakan Apache Airflow versi 3.x. Jika image `3.0.1` tidak tersedia, gunakan versi `2.10.x` dan sesuaikan base image tag.

---

## Task 6: Buat `docker/streamlit/Dockerfile`

**File**: `case-enterprise/docker/streamlit/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    streamlit \
    plotly \
    duckdb \
    pyiceberg[s3fs,pyarrow] \
    pyarrow \
    pandas \
    s3fs \
    boto3

COPY dashboard/ /app/

EXPOSE 8502

HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8502", "--server.address=0.0.0.0", "--server.headless=true"]
```

---

## Task 7: Buat `docker-compose.yml`

**File**: `case-enterprise/docker-compose.yml`

Services:

1. **`postgres`** — PostgreSQL 16 (simulated ERP)
   - Build: `docker/postgres/Dockerfile`
   - Port: `${ERP_POSTGRES_PORT:-5433}:5432`
   - Volume: `postgres_data:/var/lib/postgresql/data`
   - Healthcheck: `pg_isready`

2. **`minio`** — MinIO S3-compatible storage
   - Image: `minio/minio:latest`
   - Command: `server /data --console-address ":9001"`
   - Ports: `${MINIO_API_PORT:-9000}:9000`, `${MINIO_CONSOLE_PORT:-9001}:9001`
   - Volume: `minio_data:/data`
   - Environment: `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`
   - Healthcheck: `curl -f http://localhost:9000/minio/health/live`

3. **`minio-setup`** — One-shot bucket creation
   - Image: `minio/mc:latest`
   - Entrypoint: `/bin/bash /setup.sh`
   - Volume: bind mount `docker/minio/setup.sh:/setup.sh`
   - Depends on: `minio` (healthy)
   - Environment: `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`

4. **`iceberg-rest`** — Apache Iceberg REST Catalog
   - Image: `tabulario/iceberg-rest:latest`
   - Port: `${ICEBERG_REST_PORT:-8181}:8181`
   - Environment:
     ```
     CATALOG_WAREHOUSE=s3://lakehouse/warehouse
     CATALOG_IO__IMPL=org.apache.iceberg.aws.s3.S3FileIO
     CATALOG_S3_ENDPOINT=http://minio:9000
     CATALOG_S3_PATH__STYLE__ACCESS=true
     AWS_ACCESS_KEY_ID=minioadmin
     AWS_SECRET_ACCESS_KEY=minioadmin
     AWS_REGION=us-east-1
     ```
   - Depends on: `minio-setup` (completed_successfully)
   - Healthcheck: `curl -f http://localhost:8181/v1/config || exit 1`

   > **Catatan**: Jika image `tabulario/iceberg-rest` tidak tersedia, alternatif:
   > - `apache/iceberg-rest-fixture:latest`
   > - Build dari source: https://github.com/apache/iceberg-rest-image
   > - Atau gunakan `trinodb/trino` sebagai catalog (lebih berat tapi lebih reliable)

5. **`airflow-postgres`** — PostgreSQL metadata DB
   - Image: `postgres:16`
   - Port: `${AIRFLOW_PG_PORT:-5434}:5432`
   - Volume: `airflow_pg_data:/var/lib/postgresql/data`

6. **`airflow-init`** — One-shot init
   - Build: `docker/airflow/Dockerfile`
   - Command: migrate DB + create admin user
   - Depends on: `airflow-postgres` (healthy)
   - Volumes: mount semua code directories

7. **`airflow-webserver`** — Port 8080
   - Depends on: `airflow-init`, `postgres`, `minio`, `iceberg-rest`
   - Volumes: `./airflow/dags`, `./dlt_pipelines`, `./transform_dbt`, `./transform_ibis`, `./seed`
   - Environment: All from `.env` + PyIceberg config

8. **`airflow-scheduler`** — Sama seperti webserver tanpa port

9. **`streamlit`** — Dashboard
   - Build: `docker/streamlit/Dockerfile` (context: `.`)
   - Port: `${STREAMLIT_PORT:-8502}:8502`
   - Depends on: `iceberg-rest` (healthy)
   - Environment: PyIceberg connection vars, MinIO vars

**Volumes**: `postgres_data`, `minio_data`, `airflow_pg_data`, `airflow_logs`

**Network**: `enterprise_network` (bridge)

---

## Task 8: Buat `seed/generate_data.py`

**File**: `case-enterprise/seed/generate_data.py`

### Spesifikasi Data Generation

**Dependencies**: `faker`, `psycopg2`, `random`, `datetime`, `uuid`

**Connection**: Environment variable `ERP_DATABASE_URL` atau default `postgresql://erp_user:erp_password_2024@postgres:5432/erp_db`

**Random seed**: `random.seed(42)` dan `Faker('id_ID')` untuk nama Indonesia

### Data yang di-generate:

#### 1. Materials (200 records)

Generate SKU per brand per category:

```python
BRANDS = {
    "Jelita": {"category": "skincare", "segment": "premium", "sku_count": 25,
               "subcategories": ["cleanser", "toner", "serum", "moisturizer", "sunscreen", "eye cream", "mask"]},
    "Pesona": {"category": "makeup", "segment": "mass", "sku_count": 30,
               "subcategories": ["foundation", "powder", "lipstick", "lip cream", "eyeshadow", "mascara", "blush", "eyeliner"]},
    "Cahaya": {"category": "bodycare", "segment": "mid", "sku_count": 20,
               "subcategories": ["body lotion", "body wash", "hand cream", "body scrub", "deodorant"]},
    "Lestari": {"category": "skincare", "segment": "mass", "sku_count": 20,
                "subcategories": ["cleanser", "moisturizer", "mask", "toner", "lip balm"]},
    "Dewi": {"category": "haircare", "segment": "mid", "sku_count": 15,
             "subcategories": ["shampoo", "conditioner", "hair mask", "hair oil", "hair serum"]},
    "Bintang": {"category": "mensgrooming", "segment": "mass", "sku_count": 12,
                "subcategories": ["face wash", "moisturizer", "deodorant", "hair gel", "aftershave"]},
    "Nusa": {"category": "babycare", "segment": "mid", "sku_count": 10,
             "subcategories": ["baby lotion", "baby wash", "baby oil", "diaper cream", "baby powder"]},
    # 8 more smaller brands...
}
```

Material ID format: `MAT-{brand_code}-{seq:04d}` (e.g., `MAT-JLT-0001`)
Price range: Premium Rp 50K-300K, Mid Rp 25K-100K, Mass Rp 10K-50K
Cost: 30-50% of price (margin bervariasi per segment)

#### 2. Distributors (50 records)

```python
REGIONS_DISTRIBUTION = {
    "Jawa": 25,        # 50% distributors
    "Sumatera": 10,    # 20%
    "Kalimantan": 5,   # 10%
    "Sulawesi": 5,     # 10%
    "Bali & Nusa Tenggara": 3,  # 6%
    "Papua & Maluku": 2,        # 4%
}
```

Distributor ID format: `DIST-{region_code}-{seq:03d}`
Names: PT + random Indonesian business name (use Faker id_ID)
Credit limit: Rp 500 juta - Rp 10 miliar (based on region)

#### 3. Customers (1,000 records)

Mix: 60% General Trade (toko), 25% Modern Trade (chain), 15% E-commerce
Customer ID format: `CUST-{seq:06d}`
Map each customer to a province/region
Associate with nearest distributor

#### 4. Sales Orders (15,000 records) & Sales Items (50,000 records)

- Periode: 12 bulan terakhir
- Channel distribution: GT 70%, MT 15%, E-commerce 15%
- **Seasonality patterns**:
  - Normal months: base volume
  - Ramadhan (bulan ke-3 dari sekarang): +40%
  - Akhir tahun (Desember): +20%
  - Harbolnas 11.11 & 12.12: e-commerce +100%
- **Regional distribution**: Jawa 60%, Sumatera 20%, others 20%
- **Plant allocation**: Tangerang 50%, Semarang 30%, Surabaya 20%
- Order ID format: `SO-{YYYYMM}-{seq:06d}`
- Item ID format: `{order_id}-{item_seq:03d}`
- Each order: 1-8 items (avg 3.3)
- Status distribution: 5% created, 10% confirmed, 15% delivered, 70% invoiced

#### 5. Inventory Movements (30,000 records)

- Movement types: 101 (production receipt), 201 (consumption), 301 (transfer), 601 (sales delivery)
- 101 movements: ~30% volume, batch-based
- 601 movements: linked to delivered/invoiced sales
- Movement ID format: `MVMT-{YYYYMM}-{seq:06d}`

#### 6. E-commerce Orders (5,000 records)

- Platform distribution: Shopee 40%, Tokopedia 30%, TikTok Shop 20%, Lazada 10%
- Higher proportion of skincare & makeup (beauty e-com)
- Platform fee: Shopee 5-8%, Tokopedia 4-6%, TikTok Shop 3-5%, Lazada 5-7%
- Shipping distribution: follows population density
- E-com order ID format: `{PLATFORM_CODE}-{YYYYMMDD}-{seq:06d}`

#### 7. GL Postings (20,000 records)

- Revenue recognition postings (debit AR, credit Revenue)
- COGS postings (debit COGS, credit Inventory)
- Operating expense postings
- GL accounts:
  ```
  1100 - Cash & Bank
  1200 - Accounts Receivable
  1300 - Inventory
  4000 - Sales Revenue
  5000 - Cost of Goods Sold
  6000 - Operating Expenses
  6100 - Marketing Expenses
  6200 - Distribution Expenses
  ```
- Posting ID format: `GL-{YYYYMM}-{seq:06d}`

**Output**: Print summary of records generated per table.

---

## Task 9-12: Buat dlt Pipelines

### `dlt_pipelines/erp_sales_pipeline.py`

Pipeline yang membaca dari PostgreSQL (SAP simulation) dan menulis ke Iceberg lakehouse.

```python
import dlt
from dlt.sources.sql_database import sql_database

def run_pipeline():
    """Ingest sales data from ERP (PostgreSQL) to Iceberg lakehouse"""

    # Source: Read from PostgreSQL (simulated SAP)
    source = sql_database(
        credentials="postgresql://erp_user:erp_password_2024@postgres:5432/erp_db",
        schema="sap",
        table_names=["sales_orders", "sales_items", "customers"],
    )

    # Destination: Write to filesystem (Parquet files on MinIO)
    # These Parquet files will be registered as Iceberg tables
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
```

> **Catatan implementasi**: dlt ke Iceberg dapat dilakukan via:
> 1. `destination="filesystem"` → write Parquet ke MinIO → register via PyIceberg
> 2. Atau gunakan custom destination yang langsung menulis ke Iceberg via PyIceberg
>
> Untuk hands-on demo, opsi 1 lebih simple. Tambahkan fungsi helper `register_to_iceberg()` yang menggunakan PyIceberg untuk membuat/update tabel di catalog.

### `dlt_pipelines/erp_inventory_pipeline.py`
- Tables: `inventory_movements`, `materials`
- Incremental by `posting_date` for movements

### `dlt_pipelines/erp_finance_pipeline.py`
- Tables: `gl_postings`
- Incremental by `posting_date`

### `dlt_pipelines/ecommerce_pipeline.py`
- Tables: `ecommerce_orders`
- Incremental by `order_date`

### Helper: `dlt_pipelines/iceberg_helper.py`

```python
from pyiceberg.catalog import load_catalog
import pyarrow.parquet as pq

def get_catalog():
    return load_catalog(
        "default",
        **{
            "uri": "http://iceberg-rest:8181",
            "s3.endpoint": "http://minio:9000",
            "s3.access-key-id": "minioadmin",
            "s3.secret-access-key": "minioadmin",
            "py-io-impl": "pyiceberg.io.pyarrow.PyArrowFileIO",
        }
    )

def register_parquet_as_iceberg(catalog, namespace, table_name, parquet_path):
    """Register Parquet file(s) as an Iceberg table"""
    # Read parquet to get schema
    table = pq.read_table(parquet_path)

    # Create namespace if not exists
    try:
        catalog.create_namespace(namespace)
    except Exception:
        pass  # already exists

    # Create or overwrite Iceberg table
    iceberg_table = catalog.create_table(
        f"{namespace}.{table_name}",
        schema=table.schema,
    )
    iceberg_table.overwrite(table)
    print(f"✅ Registered {namespace}.{table_name} ({len(table)} rows)")
```

---

## Task 13: Buat dlt config files

**File**: `case-enterprise/dlt_pipelines/.dlt/config.toml`
```toml
[runtime]
log_level = "INFO"

[destination.filesystem]
bucket_url = "s3://lakehouse/raw"

[destination.filesystem.credentials]
aws_access_key_id = "minioadmin"
aws_secret_access_key = "minioadmin"
endpoint_url = "http://minio:9000"
```

**File**: `case-enterprise/dlt_pipelines/.dlt/secrets.toml`
```toml
[sources.sql_database.credentials]
drivername = "postgresql"
database = "erp_db"
password = "erp_password_2024"
username = "erp_user"
host = "postgres"
port = 5432
```

---

## Task 14: Buat dbt project (`transform_dbt/`)

### File Structure:
```
transform_dbt/
├── dbt_project.yml
├── profiles.yml
├── packages.yml
├── models/
│   ├── sources.yml
│   ├── staging/
│   │   ├── _staging.yml
│   │   ├── stg_sales_orders.sql
│   │   ├── stg_sales_items.sql
│   │   ├── stg_materials.sql
│   │   ├── stg_inventory_movements.sql
│   │   ├── stg_customers.sql
│   │   ├── stg_distributors.sql
│   │   └── stg_ecommerce_orders.sql
│   ├── intermediate/
│   │   ├── int_channel_sales.sql
│   │   ├── int_product_margin.sql
│   │   ├── int_distributor_performance.sql
│   │   └── int_inventory_aging.sql
│   └── marts/
│       ├── mart_executive_summary.sql
│       ├── mart_brand_performance.sql
│       ├── mart_distribution_network.sql
│       ├── mart_channel_comparison.sql
│       └── mart_inventory_optimization.sql
```

### `dbt_project.yml`:
```yaml
name: 'enterprise_pji'
version: '1.0.0'
profile: 'enterprise_pji'

model-paths: ["models"]
clean-targets: ["target", "dbt_packages"]

models:
  enterprise_pji:
    staging:
      +materialized: view
    intermediate:
      +materialized: view
    marts:
      +materialized: table
```

### `profiles.yml`:
```yaml
enterprise_pji:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: /tmp/pji_analytics.duckdb
      extensions:
        - iceberg
        - httpfs
      settings:
        s3_endpoint: "minio:9000"
        s3_access_key_id: "minioadmin"
        s3_secret_access_key: "minioadmin"
        s3_use_ssl: false
        s3_url_style: "path"
```

> **Catatan**: `dbt-duckdb` dengan Iceberg extension memungkinkan dbt membaca dan menulis Iceberg tables langsung. Sources didefinisikan sebagai external Iceberg tables.

### Model Specifications:

**staging/stg_sales_orders.sql**: Clean orders. Map distribution_channel codes ke readable names. Map plant codes ke city names. Filter cancelled orders.

**staging/stg_materials.sql**: Clean materials. Add segment (premium/mid/mass) berdasarkan price range. Calculate margin_pct.

**staging/stg_customers.sql**: Clean customers. Standardize region names.

**intermediate/int_channel_sales.sql**: Aggregate sales per channel per month. Calculate channel share %. Calculate YoY growth.

**intermediate/int_product_margin.sql**: Calculate per-product margin. Include: revenue, COGS, gross profit, margin %. Rank within brand.

**intermediate/int_distributor_performance.sql**: Distributor scorecard. Metrics: revenue, order count, unique SKUs, avg order value, credit utilization.

**intermediate/int_inventory_aging.sql**: Bucket inventory by age: 0-30d, 31-60d, 61-90d, 90+d. Calculate turnover rate.

**marts/mart_executive_summary.sql**: Monthly KPIs. Revenue, orders, gross margin, channel mix, top brands, regional performance.

**marts/mart_brand_performance.sql**: Per-brand monthly performance. Revenue, margin, growth, product count, channel breakdown.

**marts/mart_distribution_network.sql**: Per-distributor per-region metrics. Coverage %, performance rank.

**marts/mart_channel_comparison.sql**: GT vs MT vs E-commerce side-by-side. Revenue, growth, margin, volume.

**marts/mart_inventory_optimization.sql**: Stock levels, turnover, dead stock, reorder alerts.

---

## Task 15: Buat Ibis transforms

### `transform_ibis/models.py`:

4 transform functions using Ibis with DuckDB backend (reading Iceberg):

1. **`channel_sales_mix(con)`** — Revenue share per channel per month, trend
2. **`brand_margin_analysis(con)`** — Gross margin per brand, category breakdown
3. **`regional_performance(con)`** — Revenue & order volume per province/region
4. **`distributor_scorecard(con)`** — Ranking & performance metrics per distributor

### `transform_ibis/run_transforms.py`:

Connect DuckDB → load Iceberg secrets → run all transforms → write results back to Iceberg.

---

## Task 16: Buat Streamlit dashboard

### File Structure:
```
dashboard/
├── app.py
├── utils.py
└── pages/
    ├── 01_executive_summary.py
    ├── 02_brand_analytics.py
    ├── 03_distribution.py
    ├── 04_channel_comparison.py
    └── 05_inventory.py
```

### `utils.py`:

```python
import duckdb
import os
import pandas as pd
import streamlit as st

@st.cache_resource
def get_connection():
    """Get DuckDB connection configured for Iceberg on MinIO"""
    con = duckdb.connect(":memory:")
    con.execute("INSTALL iceberg; LOAD iceberg; INSTALL httpfs; LOAD httpfs;")
    con.execute(f"""
        CREATE SECRET (
            TYPE S3,
            KEY_ID '{os.environ.get("MINIO_ROOT_USER", "minioadmin")}',
            SECRET '{os.environ.get("MINIO_ROOT_PASSWORD", "minioadmin")}',
            ENDPOINT '{os.environ.get("MINIO_ENDPOINT", "minio:9000").replace("http://", "")}',
            URL_STYLE 'path',
            USE_SSL false
        );
    """)
    return con

def query_df(sql: str) -> pd.DataFrame:
    con = get_connection()
    return con.execute(sql).fetchdf()

def query_iceberg(table_path: str) -> pd.DataFrame:
    """Read an Iceberg table into a DataFrame"""
    sql = f"SELECT * FROM iceberg_scan('{table_path}')"
    return query_df(sql)
```

### Page Specifications:

**01_executive_summary.py**:
- KPI row: Revenue MTD, vs Target, Gross Margin %, YoY Growth (st.metric with delta)
- Revenue trend 12 months (plotly line + area)
- Brand revenue contribution (plotly treemap)
- Regional breakdown (plotly bar chart, horizontal)
- Top 5 & Bottom 5 distributors table

**02_brand_analytics.py**:
- Sidebar filter: Brand, Category, Period
- Brand revenue trend (plotly multi-line)
- Product mix treemap
- Margin scatter plot (revenue vs margin %)
- SKU detail table with sorting

**03_distribution.py**:
- Distributor ranking (plotly horizontal bar)
- Regional revenue map (plotly choropleth or bar by province)
- Credit utilization gauge charts
- Coverage metrics

**04_channel_comparison.py**:
- Channel revenue stacked bar (12 months)
- Channel share trend (plotly stacked area, normalized to 100%)
- E-commerce platform breakdown (Shopee/Tokopedia/TikTok Shop/Lazada)
- Channel profitability comparison table
- Growth rates comparison

**05_inventory.py**:
- Stock aging distribution (plotly stacked bar by plant)
- Inventory turnover by category (plotly bar)
- Dead stock table (>90 days, sorted by value)
- Reorder alerts (st.warning for low stock items)

### Styling:
- Color palette: `["#C72C48", "#4A90D9", "#6C5CE7", "#FF6B35", "#00C853"]`
- Enterprise feel: clean, professional
- Plotly charts with consistent theme
- Number formatting: Indonesian locale (Rp, ribuan/jutaan/miliar)

---

## Task 17: Buat Airflow DAGs

### `airflow/dags/enterprise_full_pipeline.py`:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'pji-data-team',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'enterprise_full_pipeline',
    default_args=default_args,
    description='Full refresh: seed → dlt → register Iceberg → dbt → ibis',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['enterprise', 'full-refresh'],
) as dag:

    seed = PythonOperator(
        task_id='seed_erp_data',
        python_callable=...,
    )

    dlt_sales = PythonOperator(task_id='dlt_sales_ingest', ...)
    dlt_inventory = PythonOperator(task_id='dlt_inventory_ingest', ...)
    dlt_finance = PythonOperator(task_id='dlt_finance_ingest', ...)
    dlt_ecommerce = PythonOperator(task_id='dlt_ecommerce_ingest', ...)

    register_iceberg = PythonOperator(
        task_id='register_iceberg_tables',
        python_callable=...,  # register Parquet files as Iceberg tables
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/transform_dbt && dbt run --profiles-dir .',
    )

    ibis_transforms = PythonOperator(task_id='ibis_transforms', ...)

    # Dependencies
    seed >> [dlt_sales, dlt_inventory, dlt_finance, dlt_ecommerce]
    [dlt_sales, dlt_inventory, dlt_finance, dlt_ecommerce] >> register_iceberg
    register_iceberg >> dbt_run >> ibis_transforms
```

### `airflow/dags/enterprise_incremental.py`:
Scheduled every 30 min. Skip seed. Only run sales & ecommerce incremental.

---

## Task 18: Buat `Makefile`

**File**: `case-enterprise/Makefile`

```makefile
.PHONY: setup start stop restart logs seed test clean

setup:
	cp -n .env.example .env || true
	docker compose build

start:
	docker compose up -d

stop:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

logs-airflow:
	docker compose logs -f airflow-webserver airflow-scheduler

logs-streamlit:
	docker compose logs -f streamlit

logs-minio:
	docker compose logs -f minio

seed:
	docker compose exec airflow-webserver python /opt/airflow/seed/generate_data.py

dlt-run:
	docker compose exec airflow-webserver python /opt/airflow/dlt_pipelines/erp_sales_pipeline.py
	docker compose exec airflow-webserver python /opt/airflow/dlt_pipelines/erp_inventory_pipeline.py
	docker compose exec airflow-webserver python /opt/airflow/dlt_pipelines/erp_finance_pipeline.py
	docker compose exec airflow-webserver python /opt/airflow/dlt_pipelines/ecommerce_pipeline.py

dbt-run:
	docker compose exec airflow-webserver bash -c "cd /opt/airflow/transform_dbt && dbt run --profiles-dir ."

ibis-run:
	docker compose exec airflow-webserver python /opt/airflow/transform_ibis/run_transforms.py

pipeline: seed dlt-run dbt-run ibis-run

test:
	@echo "Checking containers..."
	docker compose ps
	@echo "Checking PostgreSQL..."
	docker compose exec postgres psql -U erp_user -d erp_db -c "SELECT count(*) as sales_orders FROM sap.sales_orders;"
	@echo "Checking MinIO..."
	docker compose exec minio-setup mc ls local/lakehouse/ || true
	@echo "Checking Iceberg REST Catalog..."
	curl -s http://localhost:8181/v1/config | head -20
	@echo "Checking Streamlit..."
	curl -s http://localhost:8502/_stcore/health
	@echo ""
	@echo "✅ All checks passed"

clean:
	docker compose down -v
	@echo "✅ Cleaned all volumes"
```

---

## Task 19: Buat `case-enterprise/README.md`

Buat README khusus dengan:
- Architecture diagram (sederhana, ASCII or reference ke docs)
- Quick start instructions
- Service ports table
- Make commands
- MinIO UI instructions
- Troubleshooting (especially memory issues)

---

## Task 20: Testing end-to-end

```bash
cd case-enterprise
cp .env.example .env
docker compose up -d --build
sleep 120  # Wait for all services (Iceberg REST takes longer)

# 1. Check all containers
docker compose ps
# Expected: all services "running" or "healthy"

# 2. Check PostgreSQL (ERP simulation)
docker compose exec postgres psql -U erp_user -d erp_db -c "\dt sap.*"
# Expected: 7 tables listed

# 3. Check MinIO
curl -s http://localhost:9000/minio/health/live
# Expected: healthy

# 4. Check MinIO bucket
docker compose exec minio-setup mc ls local/lakehouse/
# Expected: lakehouse bucket exists

# 5. Check Iceberg REST Catalog
curl -s http://localhost:8181/v1/config
# Expected: JSON config response

# 6. Run seed
make seed
# Expected: ~200 materials, 50 distributors, 1000 customers,
#           15000 sales orders, 50000 items, etc.

# 7. Check seeded data
docker compose exec postgres psql -U erp_user -d erp_db -c \
    "SELECT 'materials' as tbl, count(*) FROM sap.materials
     UNION ALL SELECT 'sales_orders', count(*) FROM sap.sales_orders
     UNION ALL SELECT 'sales_items', count(*) FROM sap.sales_items
     UNION ALL SELECT 'ecommerce_orders', count(*) FROM sap.ecommerce_orders;"

# 8. Run dlt pipelines
make dlt-run

# 9. Run dbt
make dbt-run

# 10. Run Ibis transforms
make ibis-run

# 11. Check Streamlit
curl -s http://localhost:8502/_stcore/health
# Expected: "ok"

# 12. Check Airflow
curl -s http://localhost:8080/api/v1/health
# Expected: healthy

echo "✅ Enterprise case - All tests passed!"
```

---

## Dependency Graph

```mermaid
graph TD
    T1["Task 1: .env.example"] --> T7["Task 7: docker-compose.yml"]
    T2["Task 2: init.sql"] --> T3["Task 3: PG Dockerfile"]
    T3 --> T7
    T4["Task 4: minio setup.sh"] --> T7
    T5["Task 5: Airflow Dockerfile"] --> T7
    T6["Task 6: Streamlit Dockerfile"] --> T7
    T7 --> T8["Task 8: generate_data.py"]
    T8 --> T9["Task 9-12: dlt Pipelines"]
    T9 --> T13["Task 13: dlt Config"]
    T13 --> T14["Task 14: dbt Project"]
    T14 --> T15["Task 15: Ibis Transforms"]
    T15 --> T16["Task 16: Streamlit Dashboard"]
    T16 --> T17["Task 17: Airflow DAGs"]
    T17 --> T18["Task 18: Makefile"]
    T18 --> T19["Task 19: README"]
    T19 --> T20["Task 20: Testing"]
```

> **Tips untuk LLM executor**: Selesaikan task secara sequential mengikuti dependency graph. Task 1-7 bisa diparalelkan sebagian. Task 8 (data generator) sebaiknya dikerjakan teliti karena menjadi dasar semua test selanjutnya.
