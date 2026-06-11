# 01 — Arsitektur Overview

## Arsitektur Referensi: Modern Python Data Stack

Berikut adalah arsitektur referensi yang digunakan di kedua studi kasus. Setiap layer menggunakan komponen yang **sama secara konseptual**, hanya berbeda di skala dan pilihan storage.

```mermaid
graph TB
    subgraph "Layer 5: Serve / BI"
        STREAMLIT["🖥️ Streamlit Dashboard"]
    end

    subgraph "Layer 4: Transform"
        DBT["📐 dbt Core<br/>(SQL Transforms)"]
        IBIS["🐍 Ibis Framework<br/>(Python Transforms)"]
    end

    subgraph "Layer 3: Storage"
        subgraph "SME"
            PG["🐘 PostgreSQL<br/>+ pg_duckdb"]
        end
        subgraph "Enterprise"
            ICEBERG["🧊 Apache Iceberg<br/>MinIO + REST Catalog"]
        end
    end

    subgraph "Layer 2: Ingestion"
        DLT["📥 dlt<br/>(data load tool)"]
    end

    subgraph "Layer 1: Orchestration"
        AIRFLOW["🔄 Apache Airflow"]
    end

    subgraph "Sources"
        SRC1["📝 CSV / Excel<br/>(POS Export)"]
        SRC2["🏢 SAP / Oracle<br/>(ERP Systems)"]
        SRC3["🛒 E-commerce<br/>(Marketplace APIs)"]
    end

    SRC1 --> DLT
    SRC2 --> DLT
    SRC3 --> DLT
    DLT --> PG
    DLT --> ICEBERG
    PG --> DBT
    PG --> IBIS
    ICEBERG --> DBT
    ICEBERG --> IBIS
    DBT --> STREAMLIT
    IBIS --> STREAMLIT
    AIRFLOW -.->|orchestrates| DLT
    AIRFLOW -.->|orchestrates| DBT
    AIRFLOW -.->|orchestrates| IBIS

    style AIRFLOW fill:#017CEE,color:#fff
    style DLT fill:#FF6B35,color:#fff
    style PG fill:#336791,color:#fff
    style ICEBERG fill:#4A90D9,color:#fff
    style DBT fill:#FF694B,color:#fff
    style IBIS fill:#6C5CE7,color:#fff
    style STREAMLIT fill:#FF4B4B,color:#fff
```

---

## Mapping Komponen per Layer

| Layer | Fungsi | SME (Haji Thoriq) | Enterprise (PJI Group) |
|:------|:-------|:-------------------|:----------------------|
| **Sources** | Sumber data | CSV export dari POS, catatan manual | SAP S/4HANA (SD, MM, FI), Oracle (manufaktur), marketplace APIs |
| **Orchestration** | Scheduling & monitoring | Apache Airflow 3.x | Apache Airflow 3.x |
| **Ingestion** | Extract & Load | dlt → PostgreSQL | dlt → Apache Iceberg (via PyIceberg) |
| **Storage (OLTP)** | Operational data | PostgreSQL 16 | PostgreSQL 16 (simulasi SAP) |
| **Storage (OLAP)** | Analytical queries | pg_duckdb (in-process) | Apache Iceberg + MinIO + REST Catalog |
| **Transform (SQL)** | SQL-based transforms | dbt-postgres | dbt-duckdb (Iceberg support) |
| **Transform (Python)** | Python-based transforms | Ibis (PostgreSQL backend) | Ibis (DuckDB + Iceberg backend) |
| **BI / Serve** | Dashboard & reporting | Streamlit | Streamlit |

---

## Studi Kasus 1: Bebek Goreng Spesial Haji Thoriq (SME)

### BEFORE: Arsitektur Legacy

```mermaid
graph LR
    subgraph "Operasional Harian"
        POS["🧾 Kasir / POS<br/>Mesin Kasir Sederhana"]
        EXCEL["📊 Excel<br/>Rekap Manual"]
        WA["📱 WhatsApp<br/>Laporan Harian"]
        BUKU["📒 Buku Catatan<br/>Stok & Belanja"]
    end

    subgraph "Proses Reporting"
        OWNER["👤 Pemilik<br/>(Pak Thoriq)"]
        MANUAL["✍️ Hitung Manual<br/>Kalkulator"]
    end

    POS -->|"Struk kertas"| EXCEL
    BUKU -->|"Catat pengeluaran"| EXCEL
    EXCEL -->|"Kirim file"| WA
    WA -->|"Terima laporan"| OWNER
    OWNER -->|"Cek untung/rugi"| MANUAL

    style POS fill:#FFB74D,color:#000
    style EXCEL fill:#4CAF50,color:#fff
    style WA fill:#25D366,color:#fff
    style BUKU fill:#FF7043,color:#fff
    style OWNER fill:#78909C,color:#fff
    style MANUAL fill:#EF5350,color:#fff
```

#### Pain Points Arsitektur Legacy SME

| # | Pain Point | Dampak Bisnis |
|:--|:-----------|:-------------|
| 1 | **Data silos** — data tersebar di Excel, WhatsApp, buku | Tidak bisa lihat gambaran menyeluruh |
| 2 | **Manual entry** — rentan human error | Selisih stok, salah hitung laba |
| 3 | **No real-time visibility** — laporan T+1 atau lebih | Keputusan terlambat (stok habis, menu tidak laku) |
| 4 | **Tidak scalable** — tambah cabang = tambah Excel | Makin rumit seiring pertumbuhan |
| 5 | **No historical analysis** — data lama hilang/tercecer | Tidak bisa analisis tren musiman |

### AFTER: Modern Python Data Stack (SME)

```mermaid
graph TB
    subgraph "Sources"
        POS["🧾 POS System<br/>Export CSV"]
        INV["📦 Catatan Inventori<br/>CSV / Google Sheets"]
    end

    subgraph "Orchestration"
        AF["🔄 Apache Airflow<br/>Schedule & Monitor"]
    end

    subgraph "Ingestion"
        DLT["📥 dlt Pipeline<br/>Auto-schema, Incremental"]
    end

    subgraph "Storage & OLAP"
        PG["🐘 PostgreSQL 16<br/>+ pg_duckdb Extension<br/>OLTP + OLAP dalam satu DB"]
    end

    subgraph "Transformation"
        DBT["📐 dbt-postgres<br/>SQL Models:<br/>staging → intermediate → marts"]
        IBIS["🐍 Ibis Framework<br/>Python Models:<br/>analytics & metrics"]
    end

    subgraph "BI Dashboard"
        ST["🖥️ Streamlit<br/>4 halaman interaktif:<br/>Ringkasan | Penjualan |<br/>Menu | Inventori"]
    end

    POS --> DLT
    INV --> DLT
    DLT --> PG
    PG --> DBT
    PG --> IBIS
    DBT --> PG
    IBIS --> PG
    PG --> ST
    AF -.->|schedule| DLT
    AF -.->|trigger| DBT
    AF -.->|trigger| IBIS

    style AF fill:#017CEE,color:#fff
    style DLT fill:#FF6B35,color:#fff
    style PG fill:#336791,color:#fff
    style DBT fill:#FF694B,color:#fff
    style IBIS fill:#6C5CE7,color:#fff
    style ST fill:#FF4B4B,color:#fff
```

#### Keunggulan Arsitektur Baru SME

| # | Keunggulan | Detail |
|:--|:-----------|:-------|
| 1 | **Single source of truth** | Semua data di PostgreSQL, satu database |
| 2 | **Automated pipeline** | Airflow menjalankan pipeline otomatis setiap hari |
| 3 | **OLAP performance** | pg_duckdb mempercepat query analitik 10-100x |
| 4 | **Dashboard real-time** | Streamlit bisa diakses dari HP/tablet |
| 5 | **Biaya ~Rp 0** | Semua open-source, bisa jalan di laptop/VPS murah |
| 6 | **Scalable** | Tambah cabang? Cukup tambah data source di dlt |

---

## Studi Kasus 2: PT Pesona Jelita Indonesia (Enterprise)

### BEFORE: Arsitektur Legacy Enterprise

```mermaid
graph TB
    subgraph "Source Systems"
        SAP["🏢 SAP S/4HANA<br/>SD, MM, FI/CO, PP"]
        ORACLE["🏭 Oracle DB<br/>Manufacturing"]
        ECOM["🛒 E-commerce<br/>Shopee, Tokopedia,<br/>TikTok Shop"]
        LEGACY["📁 Legacy Systems<br/>Custom Apps"]
    end

    subgraph "ETL Layer"
        INFORMATICA["⚙️ Informatica<br/>PowerCenter<br/>(Lisensi ~$200K/tahun)"]
        SSIS["⚙️ SSIS<br/>Custom ETL Jobs"]
    end

    subgraph "Data Warehouse"
        ODW["🗄️ Oracle<br/>Data Warehouse<br/>(Lisensi ~$500K/tahun)"]
    end

    subgraph "Reporting"
        SAPBO["📊 SAP Business<br/>Objects<br/>(Lisensi ~$150K/tahun)"]
        CRYSTAL["📋 Crystal Reports"]
        EXCEL2["📊 Excel<br/>Manual Download"]
    end

    subgraph "Consumers"
        MGT["👔 Management"]
        FINANCE["💰 Finance Team"]
        SALES["📈 Sales Team"]
    end

    SAP --> INFORMATICA
    ORACLE --> INFORMATICA
    LEGACY --> SSIS
    ECOM -.->|"Manual download"| EXCEL2
    INFORMATICA --> ODW
    SSIS --> ODW
    ODW --> SAPBO
    ODW --> CRYSTAL
    SAPBO --> MGT
    CRYSTAL --> FINANCE
    EXCEL2 --> SALES

    style SAP fill:#0058A3,color:#fff
    style ORACLE fill:#F80000,color:#fff
    style INFORMATICA fill:#FF6D00,color:#fff
    style ODW fill:#F80000,color:#fff
    style SAPBO fill:#0058A3,color:#fff
    style CRYSTAL fill:#0058A3,color:#fff
```

#### Pain Points Arsitektur Legacy Enterprise

| # | Pain Point | Dampak Bisnis |
|:--|:-----------|:-------------|
| 1 | **Vendor lock-in** — SAP + Oracle + Informatica | Total lisensi ~$850K+/tahun |
| 2 | **T+3 reporting** — ETL batch semalam, data baru available H+3 | Keputusan bisnis terlambat |
| 3 | **Siloed e-commerce data** — tidak terintegrasi dengan ERP | Tidak bisa analisis omnichannel |
| 4 | **Rigid schema** — change request ke DW butuh minggu-bulan | Tidak agile mengikuti perubahan bisnis |
| 5 | **Skill gap** — butuh ABAP developer, Oracle DBA (mahal & langka) | Sulit rekrut & retain talent |
| 6 | **No data lake** — raw data tidak disimpan | Tidak bisa retrain ML models |
| 7 | **Single point of failure** — Oracle DW down = semua report mati | Downtime = lost revenue visibility |

### AFTER: Modern Python Data Stack (Enterprise)

```mermaid
graph TB
    subgraph "Source Systems"
        SAP2["🏢 SAP S/4HANA<br/>(tetap sebagai OLTP)"]
        ORACLE2["🏭 Oracle DB<br/>(Manufacturing)"]
        ECOM2["🛒 E-commerce APIs<br/>Shopee, Tokopedia,<br/>TikTok Shop"]
    end

    subgraph "Orchestration"
        AF2["🔄 Apache Airflow<br/>Schedule, Monitor,<br/>Alerting"]
    end

    subgraph "Ingestion"
        DLT2["📥 dlt Pipelines<br/>ERP Sales | ERP Inventory |<br/>ERP Finance | E-commerce"]
    end

    subgraph "Lakehouse Storage"
        MINIO["📦 MinIO<br/>(S3-compatible)"]
        ICEBERG2["🧊 Apache Iceberg<br/>Table Format<br/>+ REST Catalog"]
        MINIO --- ICEBERG2
    end

    subgraph "Transformation"
        DBT2["📐 dbt-duckdb<br/>SQL Models (Iceberg-native):<br/>staging → intermediate → marts"]
        IBIS2["🐍 Ibis Framework<br/>Python Models:<br/>advanced analytics"]
    end

    subgraph "BI Dashboard"
        ST2["🖥️ Streamlit<br/>5 halaman:<br/>Executive | Brand | Distribution |<br/>Channel | Inventory"]
    end

    SAP2 --> DLT2
    ORACLE2 --> DLT2
    ECOM2 --> DLT2
    DLT2 --> MINIO
    ICEBERG2 --> DBT2
    ICEBERG2 --> IBIS2
    DBT2 --> ICEBERG2
    IBIS2 --> ICEBERG2
    ICEBERG2 --> ST2
    AF2 -.->|schedule| DLT2
    AF2 -.->|trigger| DBT2
    AF2 -.->|trigger| IBIS2

    style AF2 fill:#017CEE,color:#fff
    style DLT2 fill:#FF6B35,color:#fff
    style MINIO fill:#C72C48,color:#fff
    style ICEBERG2 fill:#4A90D9,color:#fff
    style DBT2 fill:#FF694B,color:#fff
    style IBIS2 fill:#6C5CE7,color:#fff
    style ST2 fill:#FF4B4B,color:#fff
```

#### Keunggulan Arsitektur Baru Enterprise

| # | Keunggulan | Detail |
|:--|:-----------|:-------|
| 1 | **Hemat biaya 70-80%** | Open-source menggantikan lisensi SAP BO + Oracle DW + Informatica |
| 2 | **Near real-time** | Pipeline bisa berjalan setiap 15 menit, bukan batch semalam |
| 3 | **Omnichannel analytics** | E-commerce data terintegrasi di lakehouse yang sama |
| 4 | **Schema evolution** | Iceberg mendukung schema evolution tanpa downtime |
| 5 | **Time travel** | Iceberg snapshot memungkinkan query data historis |
| 6 | **Talent friendly** | Python + SQL — skillset yang lebih umum & mudah direkrut |
| 7 | **Open format** | Iceberg = open table format, tidak ada vendor lock-in |
| 8 | **Separation of storage & compute** | MinIO (storage) bisa scale independen dari compute |

---

## Perbandingan Arsitektur Side-by-Side

```mermaid
graph LR
    subgraph "SME Stack"
        direction TB
        S1["📥 dlt"] --> S2["🐘 PostgreSQL<br/>+ pg_duckdb"]
        S2 --> S3["📐 dbt-postgres"]
        S2 --> S4["🐍 Ibis"]
        S3 --> S5["🖥️ Streamlit"]
        S4 --> S5
    end

    subgraph "Enterprise Stack"
        direction TB
        E1["📥 dlt"] --> E2["🧊 Iceberg<br/>MinIO + REST Catalog"]
        E2 --> E3["📐 dbt-duckdb"]
        E2 --> E4["🐍 Ibis"]
        E3 --> E5["🖥️ Streamlit"]
        E4 --> E5
    end

    S5 ~~~ E1

    style S2 fill:#336791,color:#fff
    style E2 fill:#4A90D9,color:#fff
```

> **Perhatikan**: Layer ingestion, transformation, orchestration, dan BI **identik**. Hanya layer storage/OLAP yang berbeda. Ini adalah kekuatan utama modern Python data stack — **portabilitas**.

---

## Data Flow Detail

### Alur Data End-to-End

```mermaid
sequenceDiagram
    participant AF as Airflow
    participant DLT as dlt
    participant SRC as Source
    participant STG as Storage (PG/Iceberg)
    participant DBT as dbt
    participant IBIS as Ibis
    participant ST as Streamlit

    AF->>DLT: Trigger ingestion DAG
    DLT->>SRC: Extract data (incremental)
    SRC-->>DLT: Raw data
    DLT->>STG: Load ke raw schema/namespace
    DLT-->>AF: Task success

    AF->>DBT: Trigger dbt run
    DBT->>STG: Read from raw
    DBT->>STG: Write to staging
    DBT->>STG: Write to intermediate
    DBT->>STG: Write to marts
    DBT-->>AF: Task success

    AF->>IBIS: Trigger Ibis transforms
    IBIS->>STG: Read from staging/marts
    IBIS->>STG: Write analytics tables
    IBIS-->>AF: Task success

    ST->>STG: Query marts & analytics
    STG-->>ST: Data for visualization
```

---

Selanjutnya: [02 — Studi Kasus SME: Bebek Goreng Haji Thoriq →](02-studi-kasus-sme.md)
