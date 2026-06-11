import streamlit as st
import plotly.express as px
from utils import query_df

st.set_page_config(layout="wide")

st.title("🚚 Evaluasi Jaringan Distribusi")
st.markdown("---")

try:
    dist_df = query_df("SELECT * FROM marts.mart_distribution_network;")
    
    col1, col2 = st.columns(2)
    
    # 1. Top Distributors Bar Chart
    fig_dist = px.bar(
        dist_df.head(15),
        x="total_revenue",
        y="distributor_name",
        orientation="h",
        title="Top 15 Distributor Nasional Terbesar",
        labels={"total_revenue": "Omzet (Rp)", "distributor_name": "Distributor"},
        color="region",
        color_discrete_sequence=["#C72C48", "#4A90D9", "#6C5CE7", "#FF6B35", "#00C853"]
    )
    fig_dist.update_layout(yaxis={'categoryorder':'total ascending'}, template="plotly_dark")
    col1.plotly_chart(fig_dist, use_container_width=True)
    
    # 2. Scorecard detail
    score_df = query_df("SELECT distributor_name, region, credit_limit, total_revenue, credit_utilization_pct FROM analytics.distributor_scorecard;")
    
    fig_scatter = px.scatter(
        score_df,
        x="credit_limit",
        y="credit_utilization_pct",
        color="region",
        size="total_revenue",
        hover_name="distributor_name",
        title="Pemanfaatan Kredit Limit vs Kredit Tersedia",
        labels={"credit_limit": "Limit Kredit (Rp)", "credit_utilization_pct": "% Pemanfaatan Limit"},
        color_discrete_sequence=["#C72C48", "#4A90D9", "#6C5CE7", "#FF6B35", "#00C853"]
    )
    fig_scatter.update_layout(template="plotly_dark")
    col2.plotly_chart(fig_scatter, use_container_width=True)
    
    # Table coverage
    st.markdown("#### Detail Finansial Jaringan Kerja Sama")
    st.dataframe(dist_df, use_container_width=True)

except Exception as e:
    st.warning(f"Error memuat analitik distribusi: {e}")
