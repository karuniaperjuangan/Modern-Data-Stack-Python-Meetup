import streamlit as st
import plotly.express as px
from utils import query_df

st.set_page_config(layout="wide")

st.title("🏷️ Analitik Kinerja Brand & Kategori")
st.markdown("---")

try:
    brand_df = query_df("SELECT * FROM marts.mart_brand_performance;")
    
    col1, col2 = st.columns(2)
    
    # 1. Bar Chart Brand Revenue
    fig_brand = px.bar(
        brand_df,
        x="brand",
        y="total_revenue",
        color="category",
        title="Pendapatan Lini Brand per Kategori Produk",
        labels={"total_revenue": "Omzet (Rp)", "brand": "Brand"},
        color_discrete_sequence=["#C72C48", "#4A90D9", "#6C5CE7", "#FF6B35"]
    )
    fig_brand.update_layout(template="plotly_dark")
    col1.plotly_chart(fig_brand, use_container_width=True)
    
    # 2. Scatter plot Revenue vs Margin
    margin_df = query_df("SELECT brand, category, SUM(gross_revenue) as rev, AVG(gross_margin_pct) as margin FROM analytics.brand_margin_analysis GROUP BY 1, 2;")
    fig_scatter = px.scatter(
        margin_df,
        x="rev",
        y="margin",
        color="brand",
        size="rev",
        hover_name="category",
        title="Profitabilitas Margin vs Total Revenue Kategori",
        labels={"rev": "Revenue (Rp)", "margin": "Rata-rata Margin %"},
        color_discrete_sequence=["#C72C48", "#4A90D9", "#6C5CE7", "#FF6B35", "#00C853"]
    )
    fig_scatter.update_layout(template="plotly_dark")
    col2.plotly_chart(fig_scatter, use_container_width=True)
    
    # Raw Data list
    st.markdown("#### Detail Finansial Performa Brand")
    st.dataframe(brand_df, use_container_width=True)

except Exception as e:
    st.warning(f"Error memuat brand analytics: {e}")
