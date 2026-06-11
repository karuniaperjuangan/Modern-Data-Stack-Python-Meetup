FROM apache/airflow:2.10.2-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python dependencies
RUN pip install --no-cache-dir \
    "dlt[postgres]" \
    "dbt-postgres<2.0.0" \
    "dbt-core<2.0.0" \
    "ibis-framework[postgres]" \
    "psycopg2-binary" \
    "faker" \
    "plotly" \
    "streamlit"
