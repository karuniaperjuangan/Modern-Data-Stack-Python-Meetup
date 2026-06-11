FROM apache/airflow:2.10.2-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python dependencies
RUN pip install --no-cache-dir \
    "dlt[filesystem]" \
    "dbt-duckdb>=0.9,<2.0.0" \
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
