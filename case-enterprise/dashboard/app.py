import streamlit as st

st.set_page_config(
    page_title="💄 PJI Group — Enterprise Dashboard",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar brand image placeholder / custom style
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <span style="font-size: 60px;">💄</span>
        <h2 style="margin-top: 10px; color: #C72C48;">PJI Group</h2>
        <small style="color: #888;">PT Pesona Jelita Indonesia</small>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("💄 PT Pesona Jelita Indonesia (PJI Group)")
st.markdown("## Platform Analitik Enterprise Lakehouse (Apache Iceberg)")
st.markdown("---")

st.markdown(
    """
    Selamat datang di Portal Analitik Eksekutif **PJI Group**. 
    Aplikasi dashboard enterprise ini membaca secara direct-scan dari format tabel modern **Apache Iceberg** 
    yang tersimpan pada cloud object storage (MinIO) menggunakan database engine analitis **DuckDB**.
    
    ### Halaman Analisis:
    *   **📊 Ringkasan Eksekutif**: Konsolidasi performa finansial bulanan, margin kotor, dan pertumbuhan YoY.
    *   **🏷️ Analitik Brand**: Kinerja penjualan per lini brand kosmetik (Jelita, Pesona, Cahaya, dsb).
    *   **🚚 Jaringan Distribusi**: Evaluasi performa distributor daerah dan pemanfaatan limit kredit.
    *   **📈 Perbandingan Channel**: Komparasi kinerja General Trade, Modern Trade, vs marketplace E-commerce.
    *   **📦 Optimalisasi Inventori**: Analisis aging stock gudang (dead stock) untuk menekan capital loss.
    
    ---
    *Silakan pilih menu analisis dari panel navigasi di sidebar kiri.*
    """
)
