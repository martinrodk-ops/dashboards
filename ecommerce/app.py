import streamlit as st
import sqlite3
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
    # Crear conexión temporal para obtener información
    conn_temp = data_loader.create_connection()
    try:
        cursor = conn_temp.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            with st.sidebar.expander(f"📁 {table[0]}"):
                cursor.execute(f"PRAGMA table_info({table[0]});")
                columns = cursor.fetchall()
                for col in columns:
                    st.sidebar.write(f"  ├─ {col[1]} ({col[2]})")
    finally:
        conn_temp.close()

# Cargar base de datos (esto solo se hace una vez)
data_loader.load_database()

# Mostrar el análisis seleccionado
if selected_analysis in analysis_options:
    analysis_function = analysis_options[selected_analysis]
    
    # Crear una nueva conexión para este thread específico
    conn = data_loader.create_connection()
    try:
        analysis_function(conn)
    except Exception as e:
        st.error(f"Error en el análisis: {str(e)}")
    finally:
        conn.close()  # Siempre cerrar la conexión

# Footer
st.markdown("---")
st.markdown(
    "📊 *Dashboard desarrollado con Streamlit | "
    "Datos: Brazilian E-commerce Public Dataset*"
)
