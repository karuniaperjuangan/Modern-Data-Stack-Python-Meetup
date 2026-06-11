import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import query_df

st.set_page_config(layout="wide")

st.title("🍗 Analitik Menu & Performa")
st.markdown("---")

try:
    # Fetch menu ranking from marts
    menu_df = query_df("SELECT * FROM marts.mart_menu_analytics;")
    
    col1, col2 = st.columns(2)
    
    # 1. Bar Chart menu rankings
    fig_bar = px.bar(
        menu_df.head(10),
        x="total_revenue",
        y="product_name",
        orientation="h",
        title="Top 10 Menu Berdasarkan Omzet",
        labels={"total_revenue": "Omzet (Rp)", "product_name": "Menu"},
        color="category",
        color_discrete_sequence=["#FF6B35", "#336791", "#4CAF50", "#E056FD"]
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, template="plotly_dark")
    col1.plotly_chart(fig_bar, use_container_width=True)
    
    # 2. Donut chart categories
    fig_cat = px.pie(
        menu_df,
        values="total_revenue",
        names="category",
        title="Distribusi Omzet per Kategori Menu",
        hole=0.4,
        color_discrete_sequence=["#FF6B35", "#336791", "#4CAF50", "#E056FD"]
    )
    fig_cat.update_layout(template="plotly_dark")
    col2.plotly_chart(fig_cat, use_container_width=True)
    
    # 3. Pareto Chart
    st.markdown("### Analisis Pareto (Kontribusi Menu)")
    
    fig_pareto = go.Figure()
    fig_pareto.add_trace(
        go.Bar(
            x=menu_df['product_name'],
            y=menu_df['total_revenue'],
            name="Revenue",
            marker_color="#FF6B35"
        )
    )
    fig_pareto.add_trace(
        go.Scatter(
            x=menu_df['product_name'],
            y=menu_df['cumulative_revenue_share_pct'],
            name="Kumulatif %",
            yaxis="y2",
            line=dict(color="#4CAF50", width=3)
        )
    )
    
    fig_pareto.update_layout(
        title="Bagan Pareto Kontribusi Menu terhadap Omzet",
        yaxis=dict(title="Revenue (Rp)"),
        yaxis2=dict(title="Kumulatif %", overlaying="y", side="right", range=[0, 105]),
        showlegend=True,
        template="plotly_dark"
    )
    st.plotly_chart(fig_pareto, use_container_width=True)
    
    # Raw Data Table
    st.markdown("#### Detail Performa Seluruh Menu")
    st.dataframe(
        menu_df[['product_name', 'category', 'total_qty', 'total_revenue', 'gross_margin_pct', 'revenue_share_pct']],
        use_container_width=True
    )

except Exception as e:
    st.warning(f"Error memuat menu analitik: {e}")
