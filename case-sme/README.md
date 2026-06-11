# 🍗 SME Case: Bebek Goreng Spesial Haji Thoriq

Proyek ini mendemonstrasikan implementasi **Modern Python Data Stack** skala kecil (SME/UMKM) menggunakan basis database PostgreSQL yang dimodernisasi dengan extension `pg_duckdb` untuk pemrosesan analitik langsung di dalam database (OLAP).

## Arsitektur Stack

```
[POS System (Source)] ---> [PostgreSQL (raw)] 
                              |
                              +---> [dlt] ---> [PostgreSQL (raw_dlt)]
                                                  |
                                                  +---> [dbt] ---> [PostgreSQL (staging/marts)]
                                                  |
                                                  +---> [Ibis] ---> [PostgreSQL (analytics)]
                                                                       |
                                                                       v
                                                                 [Streamlit]
```

Orkestrasi seluruh pipeline dikendalikan oleh **Apache Airflow**.

## Port Mapping

*   **PostgreSQL (Aplikasi & Analitik)**: `5432`
*   **PostgreSQL (Airflow Metadata)**: `5433`
*   **Airflow Webserver**: `8080` (Username/Password: `airflow` / `airflow`)
*   **Streamlit Dashboard**: `8501`

## Panduan Cepat Menjalankan

1.  **Salin environment variables**:
    ```bash
    cp .env.example .env
    ```
2.  **Bangun & Jalankan kontainer**:
    ```bash
    make setup
    make start
    ```
3.  **Jalankan seluruh Data Pipeline (Seed -> DLT -> dbt -> Ibis)**:
    ```bash
    # Seeding database
    make seed
    
    # Jalankan orkestrasi pipeline
    make pipeline
    ```
4.  **Verifikasi data**:
    ```bash
    make test
    ```
5.  **Buka Dashboard**:
    Akses dashboard Streamlit di web browser: [http://localhost:8501](http://localhost:8501)

## Struktur Folder

*   `docker/`: Konfigurasi Dockerfile Postgres, Airflow, dan Streamlit.
*   `seed/`: Script Python generator data sintetis.
*   `dlt_pipelines/`: Pipeline data ingestion berbasis `dlt`.
*   `transform_dbt/`: Transformasi modeling berbasis SQL menggunakan `dbt`.
*   `transform_ibis/`: Transformasi modeling berbasis Python menggunakan `Ibis`.
*   `dashboard/`: Halaman visualisasi data interaktif menggunakan `Streamlit`.
*   `airflow/dags/`: Orkestrator task pipeline data.
