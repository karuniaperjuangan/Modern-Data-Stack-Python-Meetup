import streamlit as st
import plotly.express as px
import pandas as pd
from utils import query_df

st.set_page_config(layout="wide")

st.title("📊 Ringkasan Eksekutif Finansial")
st.markdown("---")

try:
    # Read overall KPIs
    kpi_df = query_df("SELECT * FROM mart_executive_summary LIMIT 1;")
    
    if not kpi_df.empty:
        total_rev = kpi_df['total_revenue'].iloc[0]
        total_ord = kpi_df['total_orders'].iloc[0]
        ecom_share = kpi_df['ecommerce_share_pct'].iloc[0]
        mom_growth = kpi_df['mom_growth_pct'].iloc[0]
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Revenue Bulan Berjalan", f"Rp {total_rev:,.0f}", f"{mom_growth}% MoM")
        c2.metric("Total Order", f"{total_ord:,}")
        c3.metric("Kontribusi E-commerce", f"{ecom_share}%")
        c4.metric("Status Operasional", "Sehat")
    
    # 1. 12-month Trend Chart
    trend_df = query_df("SELECT sales_month, total_revenue, ecommerce_revenue FROM mart_executive_summary ORDER BY sales_month ASC;")
    trend_df['sales_month'] = pd.to_datetime(trend_df['sales_month']).dt.strftime('%b %Y')
    
    fig_trend = px.line(
        trend_df,
        x="sales_month",
        y="total_revenue",
        title="Tren Pendapatan Bulanan Konsolidasi PJI Group",
        labels={"total_revenue": "Omzet (Rp)", "sales_month": "Bulan"},
        color_discrete_sequence=["#C72C48"]
    )
    fig_trend.update_layout(template="plotly_dark")
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # 2. Regional Performance & Brand contribution
    col1, col2 = st.columns(2)
    
    regional_df = query_df("SELECT region, SUM(total_revenue) as revenue FROM analytics.regional_performance GROUP BY 1;")
    fig_region = px.bar(
        regional_df,
        x="revenue",
        y="region",
        orientation="h",
        title="Kontribusi Penjualan per Wilayah Kerja",
        labels={"revenue": "Total Pendapatan (Rp)", "region": "Wilayah"},
        color_discrete_sequence=["#4A90D9"]
    )
    fig_region.update_layout(template="plotly_dark")
    col1.plotly_chart(fig_region, use_container_width=True)
    
    brand_df = query_df("SELECT brand, SUM(total_revenue) as revenue FROM mart_brand_performance GROUP BY 1;")
    fig_brand = px.pie(
        brand_df,
        values="revenue",
        names="brand",
        title="Pangsa Pasar Omzet per Brand Lini Produk",
        color_discrete_sequence=["#C72C48", "#4A90D9", "#6C5CE7", "#FF6B35", "#00C853"]
    )
    fig_brand.update_layout(template="plotly_dark")
    col2.plotly_chart(fig_brand, use_container_width=True)

except Exception as e:
    st.warning(f"Gagal memuat visualisasi Ringkasan Eksekutif: {e}")
