import streamlit as st
import plotly.express as px
from utils import query_df

st.set_page_config(layout="wide")

st.title("📦 Analisis Inventori Gudang & Dead Stock")
st.markdown("---")

try:
    inv_df = query_df("SELECT * FROM mart_inventory_optimization;")
    
    # Dead stock calculations
    dead_stock = inv_df[inv_df['dead_stock_flag'] == True]
    
    if not dead_stock.empty:
        total_lost_val = dead_stock['inventory_value'].sum()
        st.error(f"⚠️ **Peringatan Dead Stock!** Ada {len(dead_stock)} SKU/bahan baku yang mengendap lebih dari 90 hari di gudang (Potensi kerugian capital: **Rp {total_lost_val:,.0f}**).")
        with st.expander("Lihat Detail Dead Stock Gudang"):
            st.dataframe(
                dead_stock[['material_name', 'plant', 'current_quantity', 'inventory_value', 'stock_age_days']],
                use_container_width=True
            )
    else:
        st.success("✅ Semua tingkat stok bergerak di bawah batas aging kritis (90 hari).")
        
    col1, col2 = st.columns(2)
    
    # 1. Stock Age distribution chart
    fig_age = px.histogram(
        inv_df,
        x="stock_age_days",
        color="plant",
        nbins=20,
        title="Distribusi Umur Stok Bahan/Produk per Plant Gudang",
        labels={"stock_age_days": "Umur Stok (Hari)", "count": "Jumlah SKU"},
        color_discrete_sequence=["#C72C48", "#4A90D9", "#6C5CE7"]
    )
    fig_age.update_layout(template="plotly_dark")
    col1.plotly_chart(fig_age, use_container_width=True)
    
    # 2. Stock Value per plant
    plant_val = query_df("SELECT plant, SUM(inventory_value) as val FROM mart_inventory_optimization GROUP BY 1;")
    fig_val = px.bar(
        plant_val,
        x="plant",
        y="val",
        title="Total Nilai Inventori Aset per Gudang Pabrik",
        labels={"val": "Nilai Aset (Rp)", "plant": "Pabrik"},
        color="plant",
        color_discrete_sequence=["#C72C48", "#4A90D9", "#6C5CE7"]
    )
    fig_val.update_layout(template="plotly_dark")
    col2.plotly_chart(fig_val, use_container_width=True)
    
    st.markdown("#### Daftar Seluruh Aset Inventori Nasional")
    st.dataframe(inv_df, use_container_width=True)

except Exception as e:
    st.warning(f"Error memuat analitik inventori: {e}")
