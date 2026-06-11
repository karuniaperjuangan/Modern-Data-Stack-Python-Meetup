# 🐍 Building Modern Python Data Stack: Scaling from SMEs to Large Scale Enterprise

> Materi presentasi dan hands-on lab untuk Python Meetup — membangun modern data stack berbasis Python yang scalable, dari usaha kecil hingga enterprise besar.

---

## 📋 Daftar Isi

- [Tentang Proyek](#tentang-proyek)
- [Studi Kasus](#studi-kasus)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Struktur Proyek](#struktur-proyek)
- [Dokumentasi](#dokumentasi)
- [Lisensi](#lisensi)

---

## Tentang Proyek

Proyek ini berisi **dokumentasi lengkap** dan **hands-on code** untuk dua studi kasus modernisasi data stack menggunakan ekosistem Python open-source. Tujuannya adalah menunjukkan bahwa stack yang **sama secara konseptual** dapat di-scale dari usaha kecil (UMKM) hingga enterprise besar — hanya komponen storage/OLAP yang berbeda.

### Filosofi Utama

```
"Satu stack, dua skala. Python sebagai lingua franca."
```

| Layer | Komponen | Fungsi |
|:------|:---------|:-------|
| **Orchestration** | Apache Airflow | Penjadwalan & monitoring pipeline |
| **Ingestion** | dlt (data load tool) | Extract & Load dari berbagai sumber |
| **Transform (Python)** | Ibis Framework | Transformasi data deklaratif dalam Python |
| **Transform (SQL)** | dbt Core | Transformasi data dalam SQL |
| **BI / Dashboard** | Streamlit | Visualisasi & reporting interaktif |

---

## Studi Kasus

### 🍗 Case 1: Bebek Goreng Spesial Haji Thoriq (SME)

Warung makan dengan 3 cabang di Surabaya. Migrasi dari pencatatan manual (Excel + WhatsApp) ke modern data stack berbasis PostgreSQL + pg_duckdb.

- **OLTP**: PostgreSQL 16
- **OLAP**: pg_duckdb (DuckDB engine di dalam PostgreSQL)
- **Data volume**: ~3,000 orders / 6 bulan
- **Docker RAM**: ~2 GB

### 💄 Case 2: PT Pesona Jelita Indonesia — PJI Group (Enterprise)

Perusahaan FMCG kosmetik nasional dengan 15+ brand, 50+ distributor, dan 200K+ outlet. Migrasi dari SAP/Oracle + Informatica + Oracle DW ke lakehouse berbasis Apache Iceberg.

- **OLTP Source**: PostgreSQL 16 (simulasi SAP S/4HANA)
- **OLAP**: Apache Iceberg (MinIO + REST Catalog)
- **Data volume**: ~15,000 sales orders / 12 bulan, 50K+ line items
- **Docker RAM**: ~6 GB

---

## Tech Stack

| Teknologi | Versi | Peran | SME | Enterprise |
|:----------|:------|:------|:---:|:----------:|
| PostgreSQL | 16 | OLTP Database | ✅ | ✅ |
| pg_duckdb | 1.1+ | OLAP Engine (in-PG) | ✅ | ❌ |
| Apache Iceberg | Latest | Table Format (Lakehouse) | ❌ | ✅ |
| MinIO | Latest | S3-compatible Object Storage | ❌ | ✅ |
| Iceberg REST Catalog | Latest | Metadata Catalog | ❌ | ✅ |
| Apache Airflow | 3.x | Orchestration | ✅ | ✅ |
| dlt | Latest | Data Ingestion | ✅ | ✅ |
| Ibis Framework | 12.x | Python Transformations | ✅ | ✅ |
| dbt Core | Latest | SQL Transformations | ✅ | ✅ |
| Streamlit | Latest | BI Dashboard | ✅ | ✅ |
| Docker Compose | 2.14+ | Container Orchestration | ✅ | ✅ |

---

## Prerequisites

- **Docker Desktop** ≥ 4.x dengan Docker Compose v2.14+
- **RAM**: Minimal 4 GB untuk SME case, 8 GB untuk Enterprise case
- **Disk**: ~5 GB free space
- **Port** yang harus tersedia:
  - `5432` — PostgreSQL (SME)
  - `5433` — PostgreSQL (Enterprise)
  - `8080` — Airflow Webserver
  - `8501` — Streamlit Dashboard (SME)
  - `8502` — Streamlit Dashboard (Enterprise)
  - `9000`, `9001` — MinIO (Enterprise)
  - `8181` — Iceberg REST Catalog (Enterprise)

---

## Quick Start

### Studi Kasus SME

```bash
cd case-sme
cp .env.example .env
docker compose up -d
# Tunggu ~2-3 menit untuk inisialisasi

# Akses:
# - Airflow UI:  http://localhost:8080  (user: airflow, pass: airflow)
# - Dashboard:   http://localhost:8501
```

### Studi Kasus Enterprise

```bash
cd case-enterprise
cp .env.example .env
docker compose up -d
# Tunggu ~3-5 menit untuk inisialisasi

# Akses:
# - Airflow UI:  http://localhost:8080  (user: airflow, pass: airflow)
# - Dashboard:   http://localhost:8502
# - MinIO UI:    http://localhost:9001  (user: minioadmin, pass: minioadmin)
```

### Jalankan Pipeline

```bash
# Trigger full pipeline via Airflow UI, atau via CLI:
docker compose exec airflow-webserver airflow dags trigger <dag_name>
```

---

## Struktur Proyek

```
PythonMeetup/
├── README.md                    # ← Anda di sini
├── docs/                        # Dokumentasi lengkap
│   ├── 00-pendahuluan.md
│   ├── 01-arsitektur-overview.md
│   ├── 02-studi-kasus-sme.md
│   ├── 03-studi-kasus-enterprise.md
│   ├── 04-perbandingan-stack.md
│   ├── 05-kesimpulan.md
│   └── tasks/                   # Task files untuk implementasi
│       ├── task-sme.md
│       └── task-enterprise.md
├── case-sme/                    # Hands-on code SME
│   ├── docker-compose.yml
│   ├── .env.example
│   ├── seed/
│   ├── dlt_pipelines/
│   ├── transform_ibis/
│   ├── transform_dbt/
│   ├── dashboard/
│   └── airflow/
├── case-enterprise/             # Hands-on code Enterprise
│   ├── docker-compose.yml
│   ├── .env.example
│   ├── seed/
│   ├── dlt_pipelines/
│   ├── transform_ibis/
│   ├── transform_dbt/
│   ├── dashboard/
│   └── airflow/
└── diagrams/                    # Diagram sumber (Mermaid)
```

---

## Dokumentasi

| Dokumen | Deskripsi |
|:--------|:----------|
| [Pendahuluan](docs/00-pendahuluan.md) | Apa itu Modern Python Data Stack |
| [Arsitektur Overview](docs/01-arsitektur-overview.md) | Perbandingan arsitektur & diagram |
| [Studi Kasus SME](docs/02-studi-kasus-sme.md) | Bebek Goreng Haji Thoriq |
| [Studi Kasus Enterprise](docs/03-studi-kasus-enterprise.md) | PT Pesona Jelita Indonesia |
| [Perbandingan Stack](docs/04-perbandingan-stack.md) | SME vs Enterprise decision framework |
| [Kesimpulan](docs/05-kesimpulan.md) | Key takeaways & roadmap |

---

## Lisensi

MIT License — Bebas digunakan untuk keperluan edukasi dan presentasi.
