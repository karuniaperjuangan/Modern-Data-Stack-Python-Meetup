import streamlit as st
import plotly.express as px
import pandas as pd
from utils import query_df

st.set_page_config(layout="wide")

st.title("💰 Analitik Penjualan Detail")
st.markdown("---")

# Branch filter
try:
    branches_list = query_df("SELECT DISTINCT branch_name FROM analytics.daily_revenue;")['branch_name'].tolist()
    selected_branch = st.sidebar.selectbox("Pilih Cabang", ["Semua Cabang"] + branches_list)
except Exception:
    selected_branch = "Semua Cabang"
    st.error("Gagal terhubung ke database. Harap jalankan pipelines terlebih dahulu.")

# Base query construction
where_clause = ""
if selected_branch != "Semua Cabang":
    where_clause = f"WHERE branch_name = '{selected_branch}'"

try:
    # 1. Daily revenue line chart
    daily_sales = query_df(f"""
        SELECT order_date_day, SUM(daily_revenue) as revenue
        FROM analytics.daily_revenue
        {where_clause}
        GROUP BY 1
        ORDER BY 1 ASC;
    """)
    
    fig_daily = px.line(
        daily_sales,
        x="order_date_day",
        y="revenue",
        title=f"Tren Penjualan Harian — {selected_branch}",
        labels={"revenue": "Omzet (Rp)", "order_date_day": "Tanggal"},
        color_discrete_sequence=["#FF6B35"]
    )
    fig_daily.update_layout(template="plotly_dark")
    st.plotly_chart(fig_daily, use_container_width=True)
    
    # 2. Payment methods pie chart
    payment_where = ""
    if selected_branch != "Semua Cabang":
        payment_where = f"WHERE b.branch_name = '{selected_branch}'"
        
    payment_df = query_df(f"""
        SELECT o.payment_type, SUM(o.total_amount) as total_amount
        FROM raw.orders o
        JOIN raw.branches b ON o.branch_id = b.branch_id
        {payment_where}
        GROUP BY 1;
    """)
    
    col1, col2 = st.columns(2)
    
    fig_pay = px.pie(
        payment_df,
        values="total_amount",
        names="payment_type",
        title="Distribusi Tipe Pembayaran",
        color_discrete_sequence=["#336791", "#FF6B35", "#4CAF50"]
    )
    fig_pay.update_layout(template="plotly_dark")
    col1.plotly_chart(fig_pay, use_container_width=True)
    
    # 3. Peak hours heatmap
    peak_where = ""
    if selected_branch != "Semua Cabang":
        peak_where = f"WHERE branch_name = '{selected_branch}'"
        
    peak_df = query_df(f"""
        SELECT hour, SUM(order_count) as total_orders
        FROM analytics.peak_hours
        {peak_where}
        GROUP BY 1
        ORDER BY 1;
    """)
    
    fig_peak = px.bar(
        peak_df,
        x="hour",
        y="total_orders",
        title="Pola Distribusi Waktu Pemesanan (Jam)",
        labels={"total_orders": "Jumlah Order", "hour": "Jam (WIB)"},
        color_discrete_sequence=["#4CAF50"]
    )
    fig_peak.update_layout(template="plotly_dark")
    col2.plotly_chart(fig_peak, use_container_width=True)

except Exception as e:
    st.warning(f"Error memuat analitik penjualan: {e}")
