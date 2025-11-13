"""
Main E-commerce Brazil Dashboard
"""
import streamlit as st
from data_loader import data_loader
import components as comp

# Page configuration
st.set_page_config(
    page_title="E-commerce Brazil Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("📊 E-commerce Brazil Analysis Dashboard")
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
    "Select analysis:",
    list(analysis_options.keys())
)

# Sidebar - Database information
st.sidebar.markdown("---")
st.sidebar.header("🗃️ Database")

if st.sidebar.checkbox("Show table structure"):
    table_info = data_loader.get_table_info()
    for table_name, columns in table_info.items():
        with st.sidebar.expander(f"📁 {table_name}"):
            for col_name, col_type in columns:
                st.sidebar.write(f"  ├─ {col_name} ({col_type})")

# Sidebar - Project information
st.sidebar.markdown("---")
st.sidebar.header("ℹ️ Information")
st.sidebar.info(
    "This dashboard analyzes Brazilian e-commerce data. "
    "Data is automatically loaded from Google Drive."
)

# Load data
conn = data_loader.get_connection()

# Display selected analysis
if selected_analysis in analysis_options:
    analysis_function = analysis_options[selected_analysis]
    analysis_function(conn)

# Footer
st.markdown("---")
st.markdown(
    "📊 *Dashboard developed with Streamlit | "
    "Data: Brazilian E-commerce Public Dataset*"
)
