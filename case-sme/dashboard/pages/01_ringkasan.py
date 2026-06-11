import streamlit as st
import plotly.express as px
import pandas as pd
from utils import query_df

st.set_page_config(layout="wide")

st.title("📊 Ringkasan Performa Bisnis")
st.markdown("---")

# Fetch overall KPI metrics from dbt marts
try:
    kpi_df = query_df("""
        SELECT 
            SUM(monthly_revenue) as total_rev,
            SUM(monthly_orders) as total_ord,
            SUM(monthly_customers) as total_cust,
            ROUND(SUM(monthly_revenue) / NULLIF(SUM(monthly_orders), 0), 0) as avg_tkt
        FROM marts.mart_revenue_summary;
    """)
    
    # Get last month comparison
    last_month_df = query_df("""
        SELECT monthly_revenue, monthly_orders, mom_growth_pct 
        FROM marts.mart_revenue_summary 
        ORDER BY month DESC 
        LIMIT 3; -- gets the most recent month sums
    """)
    
    total_revenue = kpi_df['total_rev'].iloc[0] or 0
    total_orders = kpi_df['total_ord'].iloc[0] or 0
    total_customers = kpi_df['total_cust'].iloc[0] or 0
    avg_ticket = kpi_df['avg_tkt'].iloc[0] or 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Omzet (6 Bulan)", f"Rp {total_revenue:,.0f}")
    col2.metric("Total Transaksi", f"{total_orders:,}")
    col3.metric("Total Pelanggan", f"{total_customers:,}")
    col4.metric("Rata-rata Keranjang", f"Rp {avg_ticket:,.0f}")
    
except Exception as e:
    st.error(f"Gagal memuat metrics. Pastikan dbt run telah dieksekusi. Detail: {e}")

st.markdown("### Performa Tren Omzet Bulanan")

try:
    trend_df = query_df("""
        SELECT 
            month, 
            branch_name, 
            monthly_revenue, 
            monthly_orders 
        FROM marts.mart_revenue_summary 
        ORDER BY month ASC;
    """)
    
    trend_df['month'] = pd.to_datetime(trend_df['month']).dt.strftime('%B %Y')
    
    fig1 = px.line(
        trend_df, 
        x="month", 
        y="monthly_revenue", 
        color="branch_name",
        title="Tren Omzet per Cabang",
        labels={"monthly_revenue": "Omzet (Rp)", "month": "Bulan", "branch_name": "Cabang"},
        color_discrete_sequence=["#FF6B35", "#336791", "#4CAF50"]
    )
    fig1.update_layout(template="plotly_dark")
    st.plotly_chart(fig1, use_container_width=True)
    
    # Double column layout below
    c1, c2 = st.columns(2)
    
    # Cumulative branch performance
    branch_perf = query_df("""
        SELECT branch_name, SUM(daily_revenue) as total_rev 
        FROM analytics.daily_revenue 
        GROUP BY 1;
    """)
    
    fig2 = px.bar(
        branch_perf,
        x="branch_name",
        y="total_rev",
        title="Total Kontribusi Omzet per Cabang",
        labels={"total_rev": "Total Omzet (Rp)", "branch_name": "Cabang"},
        color="branch_name",
        color_discrete_sequence=["#FF6B35", "#336791", "#4CAF50"]
    )
    fig2.update_layout(template="plotly_dark")
    c1.plotly_chart(fig2, use_container_width=True)
    
    # Recent monthly raw data
    c2.markdown("#### Detail Finansial Bulanan")
    raw_monthly = query_df("""
        SELECT month, branch_name, monthly_revenue, mom_growth_pct 
        FROM marts.mart_revenue_summary 
        ORDER BY month DESC, branch_name ASC
        LIMIT 6;
    """)
    raw_monthly['month'] = pd.to_datetime(raw_monthly['month']).dt.strftime('%Y-%m')
    c2.dataframe(raw_monthly, use_container_width=True)

except Exception as e:
    st.warning(f"Gagal memuat visualisasi detail: {e}")
