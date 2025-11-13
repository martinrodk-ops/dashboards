"""
Componente de Análisis de Métodos de Pago
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.helpers import apply_custom_style

def show_payment_analysis(conn):
    st.header("💳 Análisis de Métodos de Pago")
    
    # Cargar datos
    df_pagos = get_payment_data(conn)
    
    if df_pagos.empty:
        st.warning("No se encontraron datos de pagos.")
        return
    
    # Métricas rápidas
    col1, col2, col3 = st.columns(3)
    with col1:
        top_method = df_pagos.iloc[0]['metodo_pago']
        st.metric("🏆 Método Más Popular", top_method)
    with col2:
        st.metric("💰 Valor Total", f"${df_pagos['valor_total'].sum():,.2f}")
    with col3:
        st.metric("🔄 Transacciones", f"{df_pagos['total_transacciones'].sum():,}")
    
    st.markdown("---")
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribución por Valor")
        fig = px.pie(df_pagos, values='valor_total', names='metodo_pago',
                    hover_data=['total_transacciones'])
        fig = apply_custom_style(fig, "Distribución por Valor Total")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Transacciones por Método")
        fig = px.bar(df_pagos, x='metodo_pago', y='total_transacciones',
                    color='total_transacciones', color_continuous_scale='viridis')
        fig = apply_custom_style(fig, "Total de Transacciones por Método")
        st.plotly_chart(fig, use_container_width=True)
    
    # Gráficos secundarios
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("💲 Valor Promedio por Transacción")
        fig = px.bar(df_pagos, x='metodo_pago', y='valor_promedio',
                    color='valor_promedio', color_continuous_scale='plasma')
        fig = apply_custom_style(fig, "Valor Promedio por Transacción")
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.subheader("🎯 Pedidos Únicos por Método")
        fig = px.bar(df_pagos, x='metodo_pago', y='pedidos_unicos',
                    color='pedidos_unicos', color_continuous_scale='thermal')
        fig = apply_custom_style(fig, "Pedidos Únicos por Método de Pago")
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabla de datos
    st.subheader("📋 Resumen de Métodos de Pago")
    display_df = df_pagos.copy()
    display_df['valor_total'] = display_df['valor_total'].apply(
        lambda x: f"${x:,.2f}")
    display_df['valor_promedio'] = display_df['valor_promedio'].apply(
        lambda x: f"${x:.2f}")
    
    st.dataframe(display_df, use_container_width=True)

def get_payment_data(conn):
    """Obtiene datos de métodos de pago"""
    query = """
    SELECT
        op.payment_type as metodo_pago,
        COUNT(*) as total_transacciones,
        SUM(op.payment_value) as valor_total,
        AVG(op.payment_value) as valor_promedio,
        COUNT(DISTINCT op.order_id) as pedidos_unicos
    FROM order_payments op
    JOIN orders o ON op.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY op.payment_type
    ORDER BY valor_total DESC
    """
    
    return pd.read_sql_query(query, conn)