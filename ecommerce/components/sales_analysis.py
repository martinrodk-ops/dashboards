"""
Componente de Análisis de Ventas por Estado
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.helpers import apply_custom_style

def show_sales_analysis(conn):
    st.header("🏢 Análisis de Ventas por Estado")
    
    # Cargar datos
    df_ventas = get_sales_by_state(conn)
    
    if df_ventas.empty:
        st.warning("No se encontraron datos de ventas por estado.")
        return
    
    # Métricas rápidas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏆 Estado Líder", df_ventas.iloc[0]['estado'])
    with col2:
        st.metric("💰 Ingreso Máximo", f"${df_ventas['ingresos_totales'].max():,.0f}")
    with col3:
        st.metric("📦 Pedidos Totales", f"{df_ventas['total_pedidos'].sum():,}")
    
    st.markdown("---")
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Ingresos por Estado")
        fig = px.bar(df_ventas, x='estado', y='ingresos_totales',
                    color='ingresos_totales', color_continuous_scale='viridis',
                    labels={'ingresos_totales': 'Ingresos Totales ($)', 'estado': 'Estado'})
        fig = apply_custom_style(fig, "Distribución de Ingresos por Estado")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Pedidos por Estado")
        fig = px.bar(df_ventas, x='estado', y='total_pedidos',
                    color='total_pedidos', color_continuous_scale='plasma',
                    labels={'total_pedidos': 'Total de Pedidos', 'estado': 'Estado'})
        fig = apply_custom_style(fig, "Distribución de Pedidos por Estado")
        st.plotly_chart(fig, use_container_width=True)
    
    # Gráficos secundarios
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🥧 Distribución de Ingresos")
        fig = px.pie(df_ventas, values='ingresos_totales', names='estado',
                    hover_data=['total_pedidos'])
        fig = apply_custom_style(fig, "Participación por Estado")
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.subheader("💲 Precio Promedio por Estado")
        fig = px.scatter(df_ventas, x='total_pedidos', y='precio_promedio',
                        size='ingresos_totales', color='estado',
                        hover_name='estado', log_x=True,
                        labels={'total_pedidos': 'Total Pedidos', 
                               'precio_promedio': 'Precio Promedio ($)'})
        fig = apply_custom_style(fig, "Relación: Pedidos vs Precio Promedio")
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabla de datos
    st.subheader("📋 Datos Detallados por Estado")
    display_df = df_ventas.copy()
    display_df['ingresos_totales'] = display_df['ingresos_totales'].apply(
        lambda x: f"${x:,.2f}")
    display_df['precio_promedio'] = display_df['precio_promedio'].apply(
        lambda x: f"${x:.2f}")
    
    st.dataframe(display_df, use_container_width=True)

def get_sales_by_state(conn):
    """Obtiene datos de ventas agrupados por estado"""
    query = """
    SELECT 
        c.customer_state as estado,
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
    
    return pd.read_sql_query(query, conn)