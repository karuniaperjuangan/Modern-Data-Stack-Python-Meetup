import streamlit as st
import pandas as pd
from utils import query_df

st.set_page_config(layout="wide")

st.title("📦 Manajemen Inventori & Stok")
st.markdown("---")

try:
    # Query forecast data
    inventory_df = query_df("SELECT * FROM marts.mart_inventory_forecast;")
    
    # 1. Alert section for low stock
    low_stock = inventory_df[inventory_df['reorder_flag'] == True]
    if not low_stock.empty:
        st.warning(f"⚠️ **Peringatan Reorder!** Ada {len(low_stock)} bahan baku yang kritis dan perlu dipesan segera.")
        with st.expander("Lihat Detail Bahan Baku Kritis"):
            st.dataframe(
                low_stock[['branch_name', 'ingredient_name', 'current_stock', 'unit', 'est_daily_usage', 'days_of_stock_remaining']],
                use_container_width=True
            )
    else:
        st.success("✅ Semua tingkat stok bahan baku berada pada tingkat aman.")
        
    # 2. Tabs to display per branch inventory status
    st.markdown("### Status Inventori per Cabang")
    branches = inventory_df['branch_name'].unique().tolist()
    
    tabs = st.tabs(branches)
    for i, branch in enumerate(branches):
        with tabs[i]:
            branch_df = inventory_df[inventory_df['branch_name'] == branch]
            
            # Sub KPIs
            val_total = branch_df['stock_value'].sum()
            critical_count = branch_df['reorder_flag'].sum()
            
            c1, c2 = st.columns(2)
            c1.metric("Nilai Stok Gudang", f"Rp {val_total:,.0f}")
            c2.metric("Bahan Baku Kritis", f"{critical_count} bahan")
            
            # Stock list
            st.dataframe(
                branch_df[['ingredient_name', 'current_stock', 'unit', 'unit_cost', 'stock_value', 'days_of_stock_remaining', 'reorder_flag']],
                use_container_width=True
            )

except Exception as e:
    st.warning(f"Error memuat inventori: {e}")
