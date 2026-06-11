# 00 — Pendahuluan: Modern Python Data Stack

## Apa itu Modern Data Stack?

**Modern Data Stack (MDS)** adalah pendekatan arsitektur data yang menggunakan tool-tool cloud-native, modular, dan umumnya open-source untuk mengelola seluruh lifecycle data — dari ingestion hingga visualization. Berbeda dengan pendekatan tradisional yang monolitik (satu vendor untuk semua), MDS mengadopsi filosofi **"best-of-breed"**: pilih tool terbaik untuk setiap layer, lalu integrasikan.

### Karakteristik Modern Data Stack

| Karakteristik | Tradisional | Modern |
|:-------------|:------------|:-------|
| **Deployment** | On-premise, monolitik | Cloud-native, containerized |
| **Paradigma** | ETL (Extract-Transform-Load) | ELT (Extract-Load-Transform) |
| **Scaling** | Vertical (beli server lebih besar) | Horizontal (tambah node) |
| **Vendor** | Single vendor (Oracle, SAP, IBM) | Best-of-breed, open-source |
| **Time to Value** | Bulan - tahun | Hari - minggu |
| **Biaya Awal** | Ratusan juta - miliaran | Gratis (open-source) - jutaan |
| **Skill Set** | Java, proprietary tools | Python, SQL |

### Evolusi: ETL → ELT

```
ETL Tradisional (2000-2015):
┌──────────┐    ┌─────────────────────┐    ┌──────────────┐
│  Source   │───►│  Transform Server   │───►│  Data        │
│  Systems  │    │  (Informatica/SSIS) │    │  Warehouse   │
└──────────┘    └─────────────────────┘    └──────────────┘
                 ↑ Bottleneck!
                 ↑ Transform di staging server yang mahal

ELT Modern (2015-sekarang):
┌──────────┐    ┌──────────────┐    ┌──────────────────────┐
│  Source   │───►│  Data        │───►│  Transform in-place  │
│  Systems  │    │  Warehouse / │    │  (dbt, Ibis, SQL)    │
└──────────┘    │  Lakehouse   │    └──────────────────────┘
                └──────────────┘
                 ↑ Storage murah, compute powerful
                 ↑ Load dulu, transform kemudian
```

---

## Mengapa Python?

Python telah menjadi **lingua franca** di dunia data engineering, data science, dan machine learning. Berikut alasannya:

### 1. Ekosistem yang Lengkap

```
Data Engineering    : dlt, Airflow, Prefect, Dagster
Data Transformation : dbt (Python models), Ibis, Polars, Pandas
Data Science        : scikit-learn, statsmodels, Prophet
Machine Learning    : PyTorch, TensorFlow, Hugging Face
Visualization       : Streamlit, Plotly, Matplotlib
Infrastructure      : Docker SDK, Boto3, Pulumi
```

### 2. Satu Bahasa, Seluruh Pipeline

Dengan Python, satu tim data engineer bisa menangani **seluruh pipeline** — dari ingestion hingga dashboard — tanpa harus belajar bahasa atau tool yang berbeda di setiap layer.

### 3. Komunitas & Talent Pool

- Python adalah bahasa pemrograman **#1 di dunia** (TIOBE Index 2026)
- Lebih mudah merekrut talent Python dibanding Java/Scala
- Komunitas Indonesia yang aktif (Python ID, Data Engineering ID)

### 4. Cocok untuk Semua Skala

| Skala | Python Bisa? | Contoh |
|:------|:-------------|:-------|
| UMKM / Startup | ✅ | Script sederhana + PostgreSQL |
| Mid-market | ✅ | Airflow + dbt + warehouse |
| Enterprise | ✅ | Lakehouse + distributed compute |

---

## Komponen Modern Python Data Stack

Dalam presentasi ini, kita menggunakan stack berikut:

### Layer 1: Orchestration — Apache Airflow

```
┌─────────────────────────────────────────┐
│           Apache Airflow                │
│  ┌──────┐  ┌──────┐  ┌──────┐         │
│  │ DAG 1│  │ DAG 2│  │ DAG 3│  ...    │
│  └──┬───┘  └──┬───┘  └──┬───┘         │
│     │         │         │               │
│  Schedule  Schedule  Schedule           │
│  Monitor   Monitor   Monitor            │
│  Retry     Retry     Retry              │
└─────────────────────────────────────────┘
```

**Apache Airflow** adalah platform orchestration paling populer di dunia. Dibuat oleh Airbnb, sekarang menjadi proyek top-level Apache Foundation.

- **Kenapa Airflow?**: Standard industri, DAG-based, UI monitoring, extensive integrations
- **Versi**: 3.x (2026) dengan Task SDK baru dan improved UI

### Layer 2: Ingestion — dlt (data load tool)

```python
import dlt

pipeline = dlt.pipeline(
    pipeline_name="pos_data",
    destination="postgres",
    dataset_name="raw"
)

# Satu baris untuk load data!
pipeline.run(pos_data_source())
```

**dlt** adalah library Python yang membuat ingestion data menjadi semudah menulis script Python biasa.

- **Kenapa dlt?**: Pythonic, schema evolution otomatis, incremental loading built-in
- **Keunggulan vs Airbyte/Fivetran**: Tidak perlu server terpisah, berjalan di mana saja Python berjalan

### Layer 3: Storage — PostgreSQL + pg_duckdb / Apache Iceberg

**Untuk SME:**
```sql
-- pg_duckdb: DuckDB engine di dalam PostgreSQL!
CREATE EXTENSION pg_duckdb;
SET duckdb.force_execution = true;

-- Query analitik jadi 10-100x lebih cepat
SELECT date_trunc('month', order_date), sum(total_amount)
FROM orders GROUP BY 1 ORDER BY 1;
```

**Untuk Enterprise:**
```python
# Apache Iceberg: Table format untuk lakehouse
from pyiceberg.catalog import load_catalog

catalog = load_catalog("rest", uri="http://iceberg-rest:8181")
table = catalog.load_table("analytics.sales_orders")
```

### Layer 4: Transformation — dbt + Ibis

**dbt (SQL):**
```sql
-- models/marts/mart_revenue_summary.sql
SELECT
    date_trunc('month', order_date) AS month,
    branch_name,
    SUM(total_amount) AS total_revenue,
    COUNT(DISTINCT order_id) AS total_orders
FROM {{ ref('stg_orders') }}
GROUP BY 1, 2
```

**Ibis (Python):**
```python
import ibis

# Sama logicnya, tapi dalam Python!
orders = ibis.table("orders")
revenue = (
    orders
    .group_by([orders.order_date.truncate("M"), orders.branch_name])
    .agg(
        total_revenue=orders.total_amount.sum(),
        total_orders=orders.order_id.nunique()
    )
)
```

### Layer 5: BI Dashboard — Streamlit

```python
import streamlit as st
import plotly.express as px

st.title("📊 Dashboard Penjualan")

# Query langsung dari database
df = query_revenue_data()
fig = px.line(df, x="month", y="total_revenue", color="branch")
st.plotly_chart(fig)
```

---

## Kenapa Open Source Stack Penting untuk Indonesia?

1. **Biaya**: UMKM dan startup Indonesia tidak perlu membayar lisensi mahal
2. **Kedaulatan Data**: Data tetap di infrastruktur sendiri, tidak tergantung vendor asing
3. **Talent Development**: Skill yang dipelajari berlaku universal, tidak terikat vendor
4. **Komunitas Lokal**: Bisa berkontribusi dan mendapat support dari komunitas global
5. **Customizable**: Bisa disesuaikan dengan kebutuhan bisnis lokal (regulasi OJK, pajak, BPOM)

---

## Peta Jalan Presentasi

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 00. Intro    │────►│ 01. Arsitek  │────►│ 02. SME Case │
│ (Anda di     │     │ tur Overview │     │ Haji Thoriq  │
│  sini!)      │     │              │     │              │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
┌──────────────┐     ┌──────────────┐     ┌──────▼───────┐
│ 05. Kesimpu  │◄────│ 04. Perban   │◄────│ 03. Enterpr  │
│ lan          │     │ dingan Stack │     │ ise Case PJI │
└──────────────┘     └──────────────┘     └──────────────┘
```

Selanjutnya: [01 — Arsitektur Overview →](01-arsitektur-overview.md)
