import streamlit as st
import plotly.express as px
import pandas as pd
from utils import query_df

st.set_page_config(layout="wide")

st.title("📈 Komparasi Kinerja Penjualan Channel")
st.markdown("---")

try:
    # 1. Total channel performance over time
    mix_df = query_df("SELECT * FROM analytics.channel_sales_mix ORDER BY sales_month ASC;")
    mix_df['sales_month'] = pd.to_datetime(mix_df['sales_month']).dt.strftime('%b %Y')
    
    col1, col2 = st.columns(2)
    
    fig_mix = px.line(
        mix_df,
        x="sales_month",
        y="monthly_revenue",
        color="distribution_channel",
        title="Tren Pendapatan Bulanan per Saluran Distribusi (Ibis)",
        labels={"monthly_revenue": "Omzet (Rp)", "sales_month": "Bulan", "distribution_channel": "Channel"},
        color_discrete_sequence=["#C72C48", "#4A90D9", "#6C5CE7"]
    )
    fig_mix.update_layout(template="plotly_dark")
    col1.plotly_chart(fig_mix, use_container_width=True)
    
    # 2. Cumulative share chart
    cum_channel = query_df("SELECT channel, SUM(monthly_revenue) as rev FROM mart_channel_comparison GROUP BY 1;")
    fig_cum = px.pie(
        cum_channel,
        values="rev",
        names="channel",
        title="Total Kontribusi Omzet per Saluran Distribusi",
        hole=0.4,
        color_discrete_sequence=["#C72C48", "#4A90D9", "#6C5CE7"]
    )
    fig_cum.update_layout(template="plotly_dark")
    col2.plotly_chart(fig_cum, use_container_width=True)
    
    # E-commerce platform breakdown
    st.markdown("### Detail Penjualan Platform Marketplace (E-commerce)")
    ecom_df = query_df("SELECT platform, SUM(revenue) as total_rev, COUNT(ecom_order_id) as total_ord, SUM(platform_fee) as total_fee FROM sap.ecommerce_orders GROUP BY 1;")
    
    fig_ecom = px.bar(
        ecom_df,
        x="platform",
        y="total_rev",
        title="Revenue share per Platform Marketplace",
        labels={"total_rev": "Revenue (Rp)", "platform": "Platform"},
        color="platform",
        color_discrete_sequence=["#FF6B35", "#4CAF50", "#EE5A24", "#0652DD"]
    )
    fig_ecom.update_layout(template="plotly_dark")
    st.plotly_chart(fig_ecom, use_container_width=True)
    
    st.dataframe(ecom_df, use_container_width=True)

except Exception as e:
    st.warning(f"Error memuat analitik perbandingan channel: {e}")
