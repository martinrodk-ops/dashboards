import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import get_database_connection

# Importar componentes
from components.overview import show_overview
from components.sales_analysis import show_sales_analysis
from components.temporal_analysis import show_temporal_analysis
from components.payment_analysis import show_payment_analysis
from components.product_analysis import show_product_analysis
from components.satisfaction_analysis import show_satisfaction_analysis

# Configuración de la página
st.set_page_config(
    page_title="Dashboard E-commerce Brasil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Dashboard de Análisis - E-commerce Brasileño")
st.markdown("---")

# Barra lateral para navegación
st.sidebar.title("🌎 Navegación")
st.sidebar.markdown("Selecciona una sección del análisis:")

# Cargar datos con spinner
with st.spinner('🔄 Cargando datos... Esto puede tomar unos segundos'):
    conn = get_database_connection()

# Menú de navegación en sidebar
opcion = st.sidebar.radio(
    "Secciones del Dashboard:",
    [
        "📈 Resumen Ejecutivo",
        "🌎 Ventas por Estado", 
        "📅 Análisis Temporal",
        "💳 Métodos de Pago",
        "📦 Productos y Categorías",
        "😊 Satisfacción del Cliente"
    ]
)

# Mostrar la sección seleccionada
if opcion == "📈 Resumen Ejecutivo":
    show_overview(conn)
    
elif opcion == "🌎 Ventas por Estado":
    show_sales_analysis(conn)
    
elif opcion == "📅 Análisis Temporal":
    show_temporal_analysis(conn)
    
elif opcion == "💳 Métodos de Pago":
    show_payment_analysis(conn)
    
elif opcion == "📦 Productos y Categorías":
    show_product_analysis(conn)
    
elif opcion == "😊 Satisfacción del Cliente":
    show_satisfaction_analysis(conn)

# Información adicional en el sidebar
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **💡 Información del Dashboard:**
    - Datos: Brazilian E-commerce
    - Período: 2016-2018
    - Total de pedidos analizados: ~100k
    - Fuente: Olist Store
    """
)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        Dashboard desarrollado con Streamlit y Plotly | Datos: Olist Brazilian E-commerce
    </div>
    """,
    unsafe_allow_html=True
)
