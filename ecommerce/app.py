"""
Main E-commerce Brazil Dashboard with Viridis Theme - CORREGIDO
"""
import streamlit as st
import sqlite3
from data_loader import data_loader
import components as comp

# Page configuration
st.set_page_config(
    page_title="E-commerce Brazil Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for Viridis theme - MODIFICADO: Eliminar centrado forzado de tablas
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #440154;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
        font-family: 'Segoe UI', sans-serif;
    }
    .sidebar .sidebar-content {
        background-color: #F8F9FA;
    }
    .metric-card {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #440154;
    }
    /* Mejorar el espaciado de los títulos de gráficos */
    .js-plotly-plot .plotly .main-svg .title {
        text-anchor: middle !important;
    }
</style>
""", unsafe_allow_html=True)

# Main title with custom styling
st.markdown('<h1 class="main-header">📊 Brazilian E-commerce Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar - Navigation
st.sidebar.header("🧭 Navigation")

# Analysis options
analysis_options = {
    "📊 Overview": comp.show_overview,
    "🏢 Sales by State": comp.show_sales_analysis, 
    "⏰ Temporal Analysis": comp.show_temporal_analysis,
    "💳 Payment Methods": comp.show_payment_analysis,
    "📦 Product Analysis": comp.show_product_analysis,
    "😊 Customer Satisfaction": comp.show_satisfaction_analysis
}

selected_analysis = st.sidebar.radio(
    "Select Analysis Section:",
    list(analysis_options.keys())
)

# Sidebar - Project information
st.sidebar.markdown("---")
st.sidebar.header("ℹ️ About")
st.sidebar.info("This analysis utilizes the Brazilian E-Commerce Public Dataset by Olist (Olist & Sionek, 2018).")
st.sidebar.info("Olist, and André Sionek. (2018). Brazilian E-Commerce Public Dataset by Olist [Data set]. Kaggle. https://doi.org/10.34740/KAGGLE/DSV/195341.")
st.sidebar.info("The dataset is made available under the CC BY-NC-SA 4.0 license.")

# Load database (cached) - CORREGIDO manejo de estado
if 'db_loaded' not in st.session_state:
    data_loader.load_database()
    st.session_state.db_loaded = True

# Display selected analysis
if selected_analysis in analysis_options:
    analysis_function = analysis_options[selected_analysis]
    
    # Create a new connection for this thread
    conn = data_loader.create_connection()
    try:
        analysis_function(conn)
    except Exception as e:
        st.error(f"Error in analysis: {str(e)}")
        st.info("Please check the database connection and try again.")
    finally:
        conn.close()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-family: Segoe UI, sans-serif;'>"
    "📊 <b>Brazilian E-commerce Analytics Dashboard</b> | "
    "Developed with Streamlit"

    "</div>",
    unsafe_allow_html=True
)