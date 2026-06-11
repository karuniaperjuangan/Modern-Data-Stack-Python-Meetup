import os
import sqlalchemy
import pandas as pd
import streamlit as st

@st.cache_resource
def get_engine():
    # Inside docker compose, it connects directly to postgres:5432
    url = os.environ.get(
        "DATABASE_URL",
        "postgresql://sme_user:sme_password_2024@postgres:5432/sme_db"
    )
    return sqlalchemy.create_engine(url)

def query_df(sql: str) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as con:
        df = pd.read_sql(sql, con)
    return df
