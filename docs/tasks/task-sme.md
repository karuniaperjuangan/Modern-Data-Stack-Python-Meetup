# Implementation Task: SME Case — Bebek Goreng Spesial Haji Thoriq

> **Dokumen ini adalah panduan implementasi langkah demi langkah** yang dapat dieksekusi oleh LLM atau developer. Setiap task memiliki input/output yang jelas, file yang harus dibuat, dan kode referensi.

## Overview

| Aspek | Detail |
|:------|:-------|
| **Working Directory** | `case-sme/` |
| **Database** | PostgreSQL 16 + pg_duckdb |
| **Port Mapping** | PG: 5432, Airflow: 8080, Streamlit: 8501 |
| **Estimated Time** | 3-4 jam |
| **Prerequisites** | Docker Desktop, Docker Compose v2.14+ |

---

## Checklist

- [ ] Task 1: Buat file `.env.example`
- [ ] Task 2: Buat `docker/postgres/init.sql`
- [ ] Task 3: Buat `docker/postgres/Dockerfile`
- [ ] Task 4: Buat `docker/airflow/Dockerfile`
- [ ] Task 5: Buat `docker/streamlit/Dockerfile`
- [ ] Task 6: Buat `docker-compose.yml`
- [ ] Task 7: Buat `seed/generate_data.py`
- [ ] Task 8: Buat `dlt_pipelines/pos_pipeline.py`
- [ ] Task 9: Buat `dlt_pipelines/inventory_pipeline.py`
- [ ] Task 10: Buat dlt config files (`.dlt/config.toml`, `.dlt/secrets.toml`)
- [ ] Task 11: Buat dbt project (`transform_dbt/`)
- [ ] Task 12: Buat Ibis transforms (`transform_ibis/`)
- [ ] Task 13: Buat Streamlit dashboard (`dashboard/`)
- [ ] Task 14: Buat Airflow DAGs (`airflow/dags/`)
- [ ] Task 15: Buat `Makefile`
- [ ] Task 16: Buat `case-sme/README.md`
- [ ] Task 17: Testing end-to-end

---

## Task 1: Buat `.env.example`

**File**: `case-sme/.env.example`

```bash
# ============================================
# Bebek Goreng Spesial Haji Thoriq — SME Stack
# ============================================
# Copy file ini ke .env sebelum menjalankan docker compose
# cp .env.example .env

# === PostgreSQL (Aplikasi) ===
POSTGRES_USER=sme_user
POSTGRES_PASSWORD=sme_password_2024
POSTGRES_DB=sme_db
POSTGRES_PORT=5432

# === PostgreSQL (Airflow Metadata) ===
AIRFLOW_PG_USER=airflow
AIRFLOW_PG_PASSWORD=airflow_password_2024
AIRFLOW_PG_DB=airflow_db
AIRFLOW_PG_PORT=5433

# === Airflow ===
AIRFLOW_UID=50000
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__FERNET_KEY=46BKJoQYlPPOexq0OhDZnIlNepKFf87WFwLbfzqDDho=
AIRFLOW__CORE__LOAD_EXAMPLES=false
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow_password_2024@airflow-postgres:5432/airflow_db
AIRFLOW_ADMIN_USER=airflow
AIRFLOW_ADMIN_PASSWORD=airflow

# === Streamlit ===
STREAMLIT_PORT=8501
```

---

## Task 2: Buat `docker/postgres/init.sql`

**File**: `case-sme/docker/postgres/init.sql`

Script ini dijalankan saat PostgreSQL pertama kali start. Membuat extension pg_duckdb dan schema-schema yang dibutuhkan.

```sql
-- Enable pg_duckdb extension
CREATE EXTENSION IF NOT EXISTS pg_duckdb;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS intermediate;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS analytics;

-- === RAW TABLES ===

-- Branches
CREATE TABLE raw.branches (
    branch_id SERIAL PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    address TEXT,
    city VARCHAR(50) DEFAULT 'Surabaya',
    phone VARCHAR(20),
    opened_date DATE
);

-- Products (Menu)
CREATE TABLE raw.products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL, -- makanan_utama, sambal, minuman, tambahan
    price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2),
    is_active BOOLEAN DEFAULT true
);

-- Orders
CREATE TABLE raw.orders (
    order_id SERIAL PRIMARY KEY,
    branch_id INTEGER REFERENCES raw.branches(branch_id),
    order_date TIMESTAMP NOT NULL,
    customer_count INTEGER DEFAULT 1,
    payment_type VARCHAR(20) NOT NULL, -- cash, qris, transfer
    total_amount DECIMAL(12,2) NOT NULL
);

-- Order Items
CREATE TABLE raw.order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES raw.orders(order_id),
    product_id INTEGER REFERENCES raw.products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL
);

-- Suppliers
CREATE TABLE raw.suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    category VARCHAR(50)
);

-- Ingredients
CREATE TABLE raw.ingredients (
    ingredient_id SERIAL PRIMARY KEY,
    ingredient_name VARCHAR(100) NOT NULL,
    unit VARCHAR(20) NOT NULL, -- kg, liter, pcs, ikat
    supplier_id INTEGER REFERENCES raw.suppliers(supplier_id),
    unit_cost DECIMAL(10,2)
);

-- Inventory
CREATE TABLE raw.inventory (
    inventory_id SERIAL PRIMARY KEY,
    branch_id INTEGER REFERENCES raw.branches(branch_id),
    ingredient_id INTEGER REFERENCES raw.ingredients(ingredient_id),
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_orders_branch_id ON raw.orders(branch_id);
CREATE INDEX idx_orders_date ON raw.orders(order_date);
CREATE INDEX idx_order_items_order_id ON raw.order_items(order_id);
CREATE INDEX idx_order_items_product_id ON raw.order_items(product_id);
CREATE INDEX idx_inventory_branch ON raw.inventory(branch_id);
CREATE INDEX idx_inventory_ingredient ON raw.inventory(ingredient_id);
```

---

## Task 3: Buat `docker/postgres/Dockerfile`

**File**: `case-sme/docker/postgres/Dockerfile`

```dockerfile
FROM pgduckdb/pgduckdb:16

# Copy init script
COPY init.sql /docker-entrypoint-initdb.d/01-init.sql

# Set default environment variables
ENV POSTGRES_USER=sme_user
ENV POSTGRES_PASSWORD=sme_password_2024
ENV POSTGRES_DB=sme_db
```

---

## Task 4: Buat `docker/airflow/Dockerfile`

**File**: `case-sme/docker/airflow/Dockerfile`

Custom Airflow image dengan library yang dibutuhkan (dlt, dbt, ibis).

```dockerfile
FROM apache/airflow:3.0.1-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python dependencies
RUN pip install --no-cache-dir \
    "dlt[postgres]" \
    "dbt-postgres" \
    "ibis-framework[postgres]" \
    "psycopg2-binary" \
    "faker" \
    "plotly" \
    "streamlit"
```

> **Catatan untuk executor**: Gunakan Apache Airflow versi 3.x. Jika image `3.0.1` tidak tersedia, gunakan versi `2.10.x` dan sesuaikan base image tag. Cek Docker Hub: https://hub.docker.com/r/apache/airflow/tags

---

## Task 5: Buat `docker/streamlit/Dockerfile`

**File**: `case-sme/docker/streamlit/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    streamlit \
    plotly \
    psycopg2-binary \
    sqlalchemy \
    pandas

COPY dashboard/ /app/

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

---

## Task 6: Buat `docker-compose.yml`

**File**: `case-sme/docker-compose.yml`

Buat docker compose file yang mendefinisikan:

1. **`postgres`** — pgduckdb/pgduckdb:16 (build from docker/postgres/Dockerfile)
   - Port: `${POSTGRES_PORT:-5432}:5432`
   - Volume: `postgres_data:/var/lib/postgresql/data`
   - Init script: via Dockerfile COPY
   - Healthcheck: `pg_isready`
   - Environment: from `.env`

2. **`airflow-postgres`** — postgres:16 (metadata DB)
   - Port: `${AIRFLOW_PG_PORT:-5433}:5432`
   - Volume: `airflow_pg_data:/var/lib/postgresql/data`
   - Healthcheck: `pg_isready`
   - Environment: `POSTGRES_USER=${AIRFLOW_PG_USER}`, `POSTGRES_PASSWORD=${AIRFLOW_PG_PASSWORD}`, `POSTGRES_DB=${AIRFLOW_PG_DB}`

3. **`airflow-init`** — One-shot container
   - Build from `docker/airflow/Dockerfile`
   - Command: `bash -c "airflow db migrate && airflow users create --username ${AIRFLOW_ADMIN_USER:-airflow} --password ${AIRFLOW_ADMIN_PASSWORD:-airflow} --firstname Admin --lastname User --role Admin --email admin@example.com || true"`
   - Depends on: `airflow-postgres` (healthy)
   - Environment: from `.env`
   - Volumes: mount `./airflow/dags:/opt/airflow/dags`, `./dlt_pipelines:/opt/airflow/dlt_pipelines`, `./transform_dbt:/opt/airflow/transform_dbt`, `./transform_ibis:/opt/airflow/transform_ibis`, `./seed:/opt/airflow/seed`

4. **`airflow-webserver`** — Airflow webserver
   - Build from `docker/airflow/Dockerfile`
   - Command: `airflow webserver`
   - Port: `8080:8080`
   - Depends on: `airflow-init` (completed_successfully), `postgres` (healthy)
   - Environment: from `.env`
   - Volumes: same as airflow-init + `airflow_logs:/opt/airflow/logs`

5. **`airflow-scheduler`** — Airflow scheduler
   - Build from `docker/airflow/Dockerfile`
   - Command: `airflow scheduler`
   - Depends on: `airflow-init` (completed_successfully), `postgres` (healthy)
   - Environment: from `.env`
   - Volumes: same as airflow-webserver

6. **`streamlit`** — Dashboard
   - Build from `docker/streamlit/Dockerfile` (context: `.`)
   - Port: `${STREAMLIT_PORT:-8501}:8501`
   - Depends on: `postgres` (healthy)
   - Environment: `DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}`

**Volumes**: `postgres_data`, `airflow_pg_data`, `airflow_logs`

**Network**: Semua service pada network `sme_network` (bridge driver)

---

## Task 7: Buat `seed/generate_data.py`

**File**: `case-sme/seed/generate_data.py`

Script Python yang generate synthetic data dan insert ke PostgreSQL.

### Spesifikasi:

**Dependencies**: `faker`, `psycopg2`, `random`, `datetime`

**Connection**: Baca dari environment variable `DATABASE_URL` atau gunakan default `postgresql://sme_user:sme_password_2024@postgres:5432/sme_db`

**Data yang di-generate:**

1. **Branches** (3 records):
   ```python
   branches = [
       {"branch_name": "Rungkut", "address": "Jl. Rungkut Asri No. 15, Surabaya", "phone": "031-8712345", "opened_date": "2010-03-15"},
       {"branch_name": "Wiyung", "address": "Jl. Wiyung Indah No. 8, Surabaya", "phone": "031-7523456", "opened_date": "2018-07-20"},
       {"branch_name": "Kenjeran", "address": "Jl. Kenjeran No. 120, Surabaya", "phone": "031-3814567", "opened_date": "2021-01-10"},
   ]
   ```

2. **Products** (16 records) — Sesuai tabel di docs/02-studi-kasus-sme.md

3. **Suppliers** (8 records):
   - Supplier ayam, bebek, bumbu, sayur, minyak goreng, beras, minuman, kemasan
   - Nama-nama supplier realistis Indonesia

4. **Ingredients** (20 records):
   - Bebek mentah, ayam mentah, beras, minyak goreng, bawang merah, bawang putih, cabai rawit, cabai merah, tomat, kencur, laos, kunyit, ketumbar, garam, gula, jeruk nipis, timun, kemangi, selada, es batu

5. **Orders** (~3,000 records):
   - Periode: 6 bulan terakhir dari `datetime.now()`
   - Distribusi per cabang: Rungkut 40%, Wiyung 35%, Kenjeran 25%
   - Weekend 40-60% lebih banyak order
   - Peak hours: 11:00-14:00 (40%), 17:00-21:00 (40%), sisanya (20%)
   - Payment: cash 50%, qris 35%, transfer 15%
   - Customer count: 1-6 orang (weighted random)
   - Growth trend: +5% per bulan

6. **Order Items** (~7,500 records):
   - Setiap order memiliki 1-5 items (avg 2.5)
   - Bebek Goreng Kremes paling populer (~30% share)
   - Setiap order biasanya memiliki minimal 1 makanan utama + 1 minuman
   - Subtotal = quantity × unit_price
   - Update total_amount di orders setelah generate items

7. **Inventory** (60 records):
   - 3 cabang × 20 bahan
   - Quantity random tapi realistis (misal: beras 50-200 kg, cabai 5-20 kg)

**Output**: Print summary jumlah record per tabel setelah selesai insert.

**Penting**:
- Gunakan `TRUNCATE ... CASCADE` di awal untuk idempotency
- Gunakan batch insert untuk performance
- Seed random dengan `random.seed(42)` untuk reproducibility

---

## Task 8: Buat `dlt_pipelines/pos_pipeline.py`

**File**: `case-sme/dlt_pipelines/pos_pipeline.py`

Pipeline dlt yang membaca data dari CSV (simulasi POS export) dan load ke PostgreSQL.

### Spesifikasi:

```python
import dlt
import os
import csv
from pathlib import Path

# Untuk demo: membaca langsung dari PostgreSQL raw tables
# Dalam real scenario: ini akan baca dari CSV export POS

@dlt.source
def pos_source():
    """Source: POS system export (simulated)"""

    @dlt.resource(name="orders", write_disposition="merge", primary_key="order_id")
    def orders_resource():
        """Orders from POS - incremental by order_date"""
        # Connect ke PostgreSQL dan baca dari raw.orders
        # Yield rows sebagai dict
        ...

    @dlt.resource(name="order_items", write_disposition="merge", primary_key="item_id")
    def order_items_resource():
        """Order items from POS"""
        ...

    return orders_resource, order_items_resource

def run_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="sme_pos",
        destination="postgres",
        dataset_name="raw_dlt"  # Load ke schema berbeda untuk demo
    )
    load_info = pipeline.run(pos_source())
    print(f"Pipeline completed: {load_info}")
    return load_info

if __name__ == "__main__":
    run_pipeline()
```

> **Catatan**: Karena data sudah di-seed langsung ke PostgreSQL di Task 7, pipeline dlt ini berfungsi sebagai **demo** bagaimana dlt bekerja. Dalam production, source akan membaca dari CSV export POS system atau API.

---

## Task 9: Buat `dlt_pipelines/inventory_pipeline.py`

**File**: `case-sme/dlt_pipelines/inventory_pipeline.py`

Sama seperti Task 8 tapi untuk data inventory (ingredients, suppliers, inventory).

---

## Task 10: Buat dlt config files

**File**: `case-sme/dlt_pipelines/.dlt/config.toml`
```toml
[runtime]
log_level="INFO"
```

**File**: `case-sme/dlt_pipelines/.dlt/secrets.toml`
```toml
[destination.postgres.credentials]
drivername = "postgresql"
database = "sme_db"
password = "sme_password_2024"
username = "sme_user"
host = "postgres"
port = 5432
```

---

## Task 11: Buat dbt project (`transform_dbt/`)

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
│   │   ├── stg_orders.sql
│   │   ├── stg_order_items.sql
│   │   ├── stg_products.sql
│   │   └── stg_inventory.sql
│   ├── intermediate/
│   │   ├── int_daily_sales.sql
│   │   └── int_product_performance.sql
│   └── marts/
│       ├── mart_revenue_summary.sql
│       ├── mart_menu_analytics.sql
│       └── mart_inventory_forecast.sql
```

### `dbt_project.yml`:
```yaml
name: 'sme_bebek_goreng'
version: '1.0.0'
profile: 'sme_bebek_goreng'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

clean-targets:
  - "target"
  - "dbt_packages"

models:
  sme_bebek_goreng:
    staging:
      +materialized: view
      +schema: staging
    intermediate:
      +materialized: view
      +schema: intermediate
    marts:
      +materialized: table
      +schema: marts
```

### `profiles.yml`:
```yaml
sme_bebek_goreng:
  target: dev
  outputs:
    dev:
      type: postgres
      host: "{{ env_var('POSTGRES_HOST', 'postgres') }}"
      port: 5432
      user: "{{ env_var('POSTGRES_USER', 'sme_user') }}"
      pass: "{{ env_var('POSTGRES_PASSWORD', 'sme_password_2024') }}"
      dbname: "{{ env_var('POSTGRES_DB', 'sme_db') }}"
      schema: public
      threads: 4
```

### `models/sources.yml`:
```yaml
version: 2
sources:
  - name: raw
    schema: raw
    tables:
      - name: branches
      - name: products
      - name: orders
      - name: order_items
      - name: suppliers
      - name: ingredients
      - name: inventory
```

### Model SQL Specifications:

**`stg_orders.sql`**: Clean orders — add computed columns (order_date_day, order_hour, day_of_week, is_weekend). Filter total_amount > 0.

**`stg_order_items.sql`**: Join with products to get product_name and category. Calculate margin (unit_price - cost) if cost available.

**`stg_products.sql`**: Simple clean pass-through. Ensure is_active filter.

**`stg_inventory.sql`**: Join ingredients with inventory. Add days_since_update calculation.

**`int_daily_sales.sql`**: Group orders by date & branch. Calculate: daily_revenue, daily_orders, daily_customers, avg_ticket. Join branch name.

**`int_product_performance.sql`**: Group order_items by product. Calculate: total_qty, total_revenue, order_count, avg_qty_per_order. Rank by revenue.

**`mart_revenue_summary.sql`**: Monthly aggregation from int_daily_sales. MoM growth calculation. Running total.

**`mart_menu_analytics.sql`**: Product ranking with: revenue rank, quantity rank, category share %, cumulative revenue (pareto).

**`mart_inventory_forecast.sql`**: Current stock levels with: estimated daily usage (from order_items), days_of_stock_remaining, reorder_flag.

---

## Task 12: Buat Ibis transforms (`transform_ibis/`)

### File Structure:
```
transform_ibis/
├── __init__.py
├── models.py
└── run_transforms.py
```

### `models.py`:
Buat 4 Ibis transform functions yang masing-masing return ibis expression:

1. **`daily_revenue(con)`** — Revenue per hari per cabang
2. **`menu_popularity(con)`** — Ranking menu (quantity, revenue, order count)
3. **`peak_hours(con)`** — Order count per jam per cabang
4. **`branch_comparison(con)`** — Perbandingan metrics antar cabang

### `run_transforms.py`:
Script yang:
1. Connect ke PostgreSQL via ibis
2. Run semua transform functions
3. Materialize hasilnya ke schema `analytics` di PostgreSQL
4. Print summary

---

## Task 13: Buat Streamlit dashboard (`dashboard/`)

### File Structure:
```
dashboard/
├── app.py                    # Main entry point
├── utils.py                  # Database connection & helpers
└── pages/
    ├── 01_ringkasan.py       # KPI Overview
    ├── 02_penjualan.py       # Sales Analysis
    ├── 03_menu_analitik.py   # Menu Analytics
    └── 04_inventori.py       # Inventory
```

### `app.py`:
```python
import streamlit as st

st.set_page_config(
    page_title="🍗 Bebek Goreng Haji Thoriq — Dashboard",
    page_icon="🍗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🍗 Bebek Goreng Spesial Haji Thoriq")
st.markdown("### Dashboard Analitik Bisnis")
st.markdown("---")
st.markdown("Pilih halaman dari sidebar untuk melihat analitik detail.")
```

### `utils.py`:
```python
import os
import sqlalchemy
import pandas as pd
import streamlit as st

@st.cache_resource
def get_engine():
    url = os.environ.get(
        "DATABASE_URL",
        "postgresql://sme_user:sme_password_2024@postgres:5432/sme_db"
    )
    return sqlalchemy.create_engine(url)

def query_df(sql: str) -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql(sql, engine)
```

### Halaman Specifications:

**01_ringkasan.py**: 
- 4 KPI metric cards (st.metric) in st.columns
- Line chart: revenue trend 6 bulan (plotly)
- Bar chart: revenue per cabang (plotly)
- Data table: ringkasan bulan berjalan

**02_penjualan.py**:
- Filter sidebar: date range, branch, payment type
- Daily revenue line chart
- Heatmap: hari × jam (menggunakan plotly heatmap)
- Payment type pie chart
- Top 5 hari revenue tertinggi

**03_menu_analitik.py**:
- Menu ranking bar chart (horizontal)
- Category donut chart
- Pareto line (cumulative % revenue)
- Table: semua menu dengan metrics

**04_inventori.py**:
- Current stock table per cabang
- Low stock alerts (st.warning)
- Ingredient usage chart

### Styling:
- Gunakan plotly untuk semua chart (modern, interactive)
- Color palette konsisten: `["#FF6B35", "#336791", "#4CAF50", "#FF4B4B"]`
- Dark-friendly theme
- Responsive layout (st.columns)

---

## Task 14: Buat Airflow DAGs (`airflow/dags/`)

### File Structure:
```
airflow/dags/
├── sme_full_pipeline.py
└── sme_incremental.py
```

### `sme_full_pipeline.py`:
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/opt/airflow')

default_args = {
    'owner': 'sme-data-team',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'sme_full_pipeline',
    default_args=default_args,
    description='Full refresh pipeline: seed → dlt → dbt → ibis',
    schedule_interval=None,  # Manual trigger only
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['sme', 'full-refresh'],
) as dag:

    seed_data = PythonOperator(
        task_id='seed_data',
        python_callable=lambda: __import__('seed.generate_data', fromlist=['main']).main(),
    )

    dlt_pos = PythonOperator(
        task_id='dlt_pos_ingest',
        python_callable=lambda: __import__('dlt_pipelines.pos_pipeline', fromlist=['run_pipeline']).run_pipeline(),
    )

    dlt_inventory = PythonOperator(
        task_id='dlt_inventory_ingest',
        python_callable=lambda: __import__('dlt_pipelines.inventory_pipeline', fromlist=['run_pipeline']).run_pipeline(),
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/transform_dbt && dbt run --profiles-dir .',
    )

    ibis_transforms = PythonOperator(
        task_id='ibis_transforms',
        python_callable=lambda: __import__('transform_ibis.run_transforms', fromlist=['main']).main(),
    )

    # Task dependencies
    seed_data >> [dlt_pos, dlt_inventory] >> dbt_run >> ibis_transforms
```

### `sme_incremental.py`:
DAG serupa tapi tanpa seed_data, scheduled daily at 05:00 WIB, dan dlt menggunakan incremental mode.

---

## Task 15: Buat `Makefile`

**File**: `case-sme/Makefile`

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

seed:
	docker compose exec airflow-webserver python /opt/airflow/seed/generate_data.py

dbt-run:
	docker compose exec airflow-webserver bash -c "cd /opt/airflow/transform_dbt && dbt run --profiles-dir ."

ibis-run:
	docker compose exec airflow-webserver python /opt/airflow/transform_ibis/run_transforms.py

pipeline: seed dbt-run ibis-run

test:
	docker compose exec postgres psql -U sme_user -d sme_db -c "SELECT count(*) as order_count FROM raw.orders;"
	docker compose exec postgres psql -U sme_user -d sme_db -c "SELECT count(*) as item_count FROM raw.order_items;"
	@echo "✅ Data check passed"

clean:
	docker compose down -v
	@echo "✅ Cleaned all volumes"
```

---

## Task 16: Buat `case-sme/README.md`

Buat README khusus untuk case-sme dengan:
- Quick start instructions
- Architecture diagram (sederhana)
- Available make commands
- Port mapping
- Troubleshooting tips

---

## Task 17: Testing end-to-end

### Test Script:
```bash
cd case-sme
cp .env.example .env
docker compose up -d --build
sleep 60  # Wait for init

# 1. Check all containers healthy
docker compose ps

# 2. Check PostgreSQL
docker compose exec postgres psql -U sme_user -d sme_db -c "\dt raw.*"

# 3. Run seed
docker compose exec airflow-webserver python /opt/airflow/seed/generate_data.py

# 4. Check data
docker compose exec postgres psql -U sme_user -d sme_db -c "SELECT count(*) FROM raw.orders;"
# Expected: ~3000

# 5. Run dbt
docker compose exec airflow-webserver bash -c "cd /opt/airflow/transform_dbt && dbt run --profiles-dir ."

# 6. Check marts
docker compose exec postgres psql -U sme_user -d sme_db -c "SELECT count(*) FROM marts.mart_revenue_summary;"

# 7. Check Streamlit
curl -s http://localhost:8501/_stcore/health

# 8. Check Airflow
curl -s http://localhost:8080/api/v1/health

echo "✅ All tests passed!"
```
