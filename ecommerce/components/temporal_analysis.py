import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show_temporal_analysis(conn):
    """
    Muestra el análisis temporal de ventas
    """
    st.header("📅 Análisis Temporal de Ventas")
    
    query = """
    SELECT
        strftime('%Y-%m', o.order_purchase_timestamp) as mes,
        COUNT(DISTINCT o.order_id) as total_pedidos,
        SUM(oi.price) as ingresos_totales,
        AVG(oi.price) as precio_promedio,
        COUNT(DISTINCT c.customer_unique_id) as clientes_unicos
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY mes
    ORDER BY mes
    """
    
    df_temporal = pd.read_sql_query(query, conn)
    
    # Filtros interactivos
    col1, col2 = st.columns(2)
    
    with col1:
        mostrar_metricas = st.checkbox("📈 Mostrar Métricas Mensuales", value=True)
    
    with col2:
        tipo_grafico = st.selectbox(
            "Tipo de Gráfico Principal",
            ["Líneas", "Barras", "Área"]
        )
    
    if mostrar_metricas:
        st.subheader("Métricas Mensuales")
        st.dataframe(df_temporal, use_container_width=True)
    
    # Gráfico de evolución temporal
    st.subheader("Evolución Temporal")
    
    tab1, tab2, tab3 = st.tabs(["Ingresos", "Pedidos", "Clientes Únicos"])
    
    with tab1:
        if tipo_grafico == "Líneas":
            fig = px.line(df_temporal, x='mes', y='ingresos_totales', 
                         title='Evolución de Ingresos Mensuales')
        elif tipo_grafico == "Barras":
            fig = px.bar(df_temporal, x='mes', y='ingresos_totales',
                        title='Evolución de Ingresos Mensuales')
        else:
            fig = px.area(df_temporal, x='mes', y='ingresos_totales',
                         title='Evolución de Ingresos Mensuales')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig_pedidos = px.line(df_temporal, x='mes', y='total_pedidos',
                             title='Evolución de Pedidos Mensuales')
        st.plotly_chart(fig_pedidos, use_container_width=True)
    
    with tab3:
        fig_clientes = px.line(df_temporal, x='mes', y='clientes_unicos',
                              title='Evolución de Clientes Únicos Mensuales')
        st.plotly_chart(fig_clientes, use_container_width=True)
    
    # Gráfico de precio promedio
    st.subheader("Evolución del Precio Promedio")
    fig_precio = px.line(df_temporal, x='mes', y='precio_promedio',
                        title='Precio Promedio por Mes')
    st.plotly_chart(fig_precio, use_container_width=True)