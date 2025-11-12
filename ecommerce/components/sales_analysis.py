import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

def show_sales_analysis(conn):
    """
    Muestra el análisis de ventas por estado
    """
    st.header("🌎 Análisis de Ventas por Estado")
    
    query = """
    SELECT c.customer_state as estado,
           COUNT(DISTINCT o.order_id) as total_pedidos,
           SUM(oi.price) as ingresos_totales,
           AVG(oi.price) as precio_promedio
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_state
    ORDER BY ingresos_totales DESC
    """
    
    df_ventas = pd.read_sql_query(query, conn)
    
    # Mostrar datos crudos
    with st.expander("📋 Ver datos de ventas por estado"):
        st.dataframe(df_ventas, use_container_width=True)
    
    # Crear pestañas para diferentes visualizaciones
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Ingresos Totales", "📦 Total Pedidos", 
                                     "🥧 Distribución", "📦 Precio Promedio"])
    
    with tab1:
        fig_barras = px.bar(
            df_ventas, 
            x='estado', 
            y='ingresos_totales',
            title='Ingresos Totales por Estado',
            color='ingresos_totales',
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_barras, use_container_width=True)
    
    with tab2:
        fig_pedidos = px.bar(
            df_ventas,
            x='estado',
            y='total_pedidos',
            title='Total de Pedidos por Estado',
            color='total_pedidos',
            color_continuous_scale='plasma'
        )
        st.plotly_chart(fig_pedidos, use_container_width=True)
    
    with tab3:
        fig_torta = px.pie(
            df_ventas,
            values='ingresos_totales',
            names='estado',
            title='Distribución de Ingresos por Estado'
        )
        st.plotly_chart(fig_torta, use_container_width=True)
    
    with tab4:
        fig_precio = px.box(
            df_ventas,
            y='precio_promedio',
            title='Distribución de Precios Promedio por Estado'
        )
        st.plotly_chart(fig_precio, use_container_width=True)