"""
Dashboard Principal de E-commerce Brasil
"""
import streamlit as st
from data_loader import data_loader
import components as comp

# Configuración de la página
st.set_page_config(
    page_title="Dashboard E-commerce Brasil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Dashboard de Análisis E-commerce - Brasil")
st.markdown("---")

# Sidebar - Navegación
st.sidebar.header("🧭 Navegación")

# Opciones de análisis
analysis_options = {
    "📊 Resumen General": comp.show_overview,
    "🏢 Ventas por Estado": comp.show_sales_analysis, 
    "⏰ Análisis Temporal": comp.show_temporal_analysis,
    "💳 Métodos de Pago": comp.show_payment_analysis,
    "📦 Análisis de Productos": comp.show_product_analysis,
    "😊 Satisfacción del Cliente": comp.show_satisfaction_analysis
}

selected_analysis = st.sidebar.radio(
    "Selecciona el análisis:",
    list(analysis_options.keys())
)

# Sidebar - Información de la base de datos
st.sidebar.markdown("---")
st.sidebar.header("🗃️ Base de Datos")

if st.sidebar.checkbox("Mostrar estructura de tablas"):
    table_info = data_loader.get_table_info()
    for table_name, columns in table_info.items():
        with st.sidebar.expander(f"📁 {table_name}"):
            for col_name, col_type in columns:
                st.sidebar.write(f"  ├─ {col_name} ({col_type})")

# Sidebar - Información del proyecto
st.sidebar.markdown("---")
st.sidebar.header("ℹ️ Información")
st.sidebar.info(
    "Este dashboard analiza datos de e-commerce brasileño. "
    "Los datos se cargan automáticamente desde Google Drive."
)

# Cargar datos
conn = data_loader.get_connection()

# Mostrar el análisis seleccionado
if selected_analysis in analysis_options:
    analysis_function = analysis_options[selected_analysis]
    analysis_function(conn)

# Footer
st.markdown("---")
st.markdown(
    "📊 *Dashboard desarrollado con Streamlit | "
    "Datos: Brazilian E-commerce Public Dataset*"
)
