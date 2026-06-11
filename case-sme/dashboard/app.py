import streamlit as st

st.set_page_config(
    page_title="🍗 Bebek Goreng Haji Thoriq — Dashboard",
    page_icon="🍗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar brand image placeholder / custom style
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <span style="font-size: 60px;">🍗</span>
        <h2 style="margin-top: 10px; color: #FF6B35;">Haji Thoriq</h2>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🍗 Bebek Goreng Spesial Haji Thoriq")
st.markdown("## Platform Analitik Modern Python Data Stack")
st.markdown("---")

st.markdown(
    """
    Selamat datang di Dashboard Analitik **Bebek Goreng Spesial Haji Thoriq**. 
    Aplikasi ini dibangun menggunakan arsitektur data stack modern berbasis Python untuk membantu 
    pemilik bisnis menganalisis performa penjualan cabang, efisiensi menu, dan optimalisasi stok inventori secara real-time.
    
    ### Fitur Utama:
    *   **📊 Ringkasan Eksekutif**: Ringkasan performa finansial dan KPI utama bisnis.
    *   **💰 Analitik Penjualan**: Tren harian, pola jam ramai (peak hours), dan tipe pembayaran.
    *   **🍗 Analitik Menu**: Evaluasi performa menu favorit menggunakan visualisasi Pareto.
    *   **📦 Manajemen Inventori**: Monitoring tingkat stok bahan baku dan alarm reorder otomatis.
    
    ---
    *Silakan pilih menu analitik di sidebar sebelah kiri untuk memulai.*
    """
)
