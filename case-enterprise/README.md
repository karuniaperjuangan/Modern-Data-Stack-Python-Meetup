# 💄 Enterprise Case: PT Pesona Jelita Indonesia (PJI Group)

Proyek ini mendemonstrasikan implementasi **Modern Python Data Stack** skala besar (Enterprise) menggunakan **Lakehouse Architecture** berbasis **Apache Iceberg** dengan penyimpanan object storage S3-compatible (**MinIO**) dan catalog manager (**Iceberg REST Catalog**).

## Arsitektur Stack

```
[ERP Source (Postgres)] ---> [dlt] ---> [MinIO (raw parquet)]
                                           |
                                           +---> [PyIceberg (REST Catalog)]
                                                    |
                                                    +---> [dbt-duckdb] ---> [MinIO (Iceberg tables)]
                                                    |
                                                    +---> [Ibis-duckdb] ---> [MinIO (analytics tables)]
                                                                                |
                                                                                v
                                                                          [Streamlit]
```

Orkestrasi seluruh pipeline dikendalikan oleh **Apache Airflow**.

## Port Mapping

*   **ERP Source (PostgreSQL)**: `5433`
*   **MinIO Console (S3 Storage UI)**: `9001` (Username/Password: `minioadmin` / `minioadmin`)
*   **MinIO API**: `9000`
*   **Iceberg REST Catalog API**: `8181`
*   **Airflow Webserver**: `8080` (Username/Password: `airflow` / `airflow`)
*   **Streamlit Dashboard**: `8502`

## Panduan Cepat Menjalankan

1.  **Salin environment variables**:
    ```bash
    cp .env.example .env
    ```
2.  **Bangun & Jalankan kontainer** (Pastikan Docker RAM dialokasikan minimal **6 GB**):
    ```bash
    make setup
    make start
    ```
3.  **Jalankan seluruh Data Pipeline (Seed -> DLT -> Register Iceberg -> dbt -> Ibis)**:
    ```bash
    # Seeding database ERP sumber
    make seed
    
    # Jalankan orkestrasi pipeline
    make pipeline
    ```
4.  **Verifikasi data**:
    ```bash
    make test
    ```
5.  **Buka Dashboard**:
    Akses dashboard Streamlit eksekutif di web browser: [http://localhost:8502](http://localhost:8502)

## Struktur Folder

*   `docker/`: Konfigurasi Dockerfile Postgres, MinIO setup, Airflow, dan Streamlit.
*   `seed/`: Script Python generator data sintetis skala enterprise.
*   `dlt_pipelines/`: Pipeline data ingestion berbasis `dlt` ( filesystem target).
*   `transform_dbt/`: Transformasi modeling berbasis SQL menggunakan `dbt-duckdb`.
*   `transform_ibis/`: Transformasi modeling berbasis Python menggunakan `Ibis-duckdb` pada Iceberg.
*   `dashboard/`: Halaman visualisasi eksekutif menggunakan `Streamlit`.
*   `airflow/dags/`: Orkestrator task pipeline data.
