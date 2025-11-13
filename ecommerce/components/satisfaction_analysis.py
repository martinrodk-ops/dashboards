"""
Componente de Análisis de Satisfacción del Cliente
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.helpers import apply_custom_style

def show_satisfaction_analysis(conn):
    st.header("😊 Análisis de Satisfacción del Cliente")
    
    # Cargar datos de satisfacción
    df_satisfaccion = get_satisfaction_data(conn)
    
    if df_satisfaccion.empty:
        st.warning("No se encontraron datos de satisfacción.")
        return
    
    # Métricas rápidas
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_score = df_satisfaccion['puntuacion'].mean()
        st.metric("⭐ Puntuación Promedio", f"{avg_score:.2f}")
    with col2:
        total_reviews = df_satisfaccion['total_resenas'].sum()
        st.metric("📝 Total de Reseñas", f"{total_reviews:,}")
    with col3:
        most_common_score = df_satisfaccion.loc[df_satisfaccion['total_resenas'].idxmax(), 'puntuacion']
        st.metric("🎯 Puntuación Más Común", most_common_score)
    
    st.markdown("---")
    
    # Distribución de puntuaciones
    st.subheader("📊 Distribución de Puntuaciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras
        fig = px.bar(df_satisfaccion, x='puntuacion', y='total_resenas',
                     color='total_resenas', color_continuous_scale='viridis',
                     labels={'total_resenas': 'Total Reseñas', 'puntuacion': 'Puntuación'})
        fig = apply_custom_style(fig, "Distribución de Puntuaciones")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de pie
        fig = px.pie(df_satisfaccion, values='total_resenas', names='puntuacion',
                     hover_data=['precio_promedio_pedido'])
        fig = apply_custom_style(fig, "Porcentaje por Puntuación")
        st.plotly_chart(fig, use_container_width=True)
    
    # Relación entre precio y satisfacción
    st.subheader("💲 Relación: Precio vs Satisfacción")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Precio promedio vs puntuación
        fig = px.scatter(df_satisfaccion, x='puntuacion', y='precio_promedio_pedido',
                         size='total_resenas', color='puntuacion',
                         trendline="lowess",
                         labels={'precio_promedio_pedido': 'Precio Promedio ($)', 
                                'puntuacion': 'Puntuación'})
        fig = apply_custom_style(fig, "Precio Promedio vs Puntuación")
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        # Costo de envío vs puntuación
        fig = px.scatter(df_satisfaccion, x='puntuacion', y='freight_promedio',
                         size='total_resenas', color='puntuacion',
                         trendline="lowess",
                         labels={'freight_promedio': 'Costo de Envío Promedio ($)',
                                'puntuacion': 'Puntuación'})
        fig = apply_custom_style(fig, "Costo de Envío vs Puntuación")
        st.plotly_chart(fig, use_container_width=True)
    
    # Análisis detallado por estado
    st.subheader("🏢 Satisfacción por Estado")
    
    df_satisfaccion_estado = get_satisfaction_by_state(conn)
    
    if not df_satisfaccion_estado.empty:
        col5, col6 = st.columns(2)
        
        with col5:
            # Puntuación promedio por estado
            fig = px.bar(df_satisfaccion_estado, x='estado', y='puntuacion_promedio',
                         color='puntuacion_promedio', color_continuous_scale='plasma',
                         labels={'puntuacion_promedio': 'Puntuación Promedio', 
                                'estado': 'Estado'})
            fig = apply_custom_style(fig, "Puntuación Promedio por Estado")
            st.plotly_chart(fig, use_container_width=True)
        
        with col6:
            # Mapa de calor de correlaciones
            st.subheader("📈 Reseñas por Estado")
            display_df = df_satisfaccion_estado[['estado', 'total_resenas', 'puntuacion_promedio']].copy()
            display_df['puntuacion_promedio'] = display_df['puntuacion_promedio'].round(2)
            display_df = display_df.sort_values('puntuacion_promedio', ascending=False)
            st.dataframe(display_df, use_container_width=True)
    
    # Análisis temporal de satisfacción
    st.subheader("⏰ Evolución Temporal de la Satisfacción")
    
    df_satisfaccion_temporal = get_satisfaction_temporal(conn)
    
    if not df_satisfaccion_temporal.empty:
        fig = px.line(df_satisfaccion_temporal, x='mes', y='puntuacion_promedio',
                      markers=True, line_shape='linear',
                      labels={'puntuacion_promedio': 'Puntuación Promedio', 'mes': 'Mes'})
        fig = apply_custom_style(fig, "Evolución de la Satisfacción en el Tiempo")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabla de datos completa
    st.subheader("📋 Datos Detallados de Satisfacción")
    display_df = df_satisfaccion.copy()
    display_df['precio_promedio_pedido'] = display_df['precio_promedio_pedido'].apply(lambda x: f"${x:.2f}")
    display_df['freight_promedio'] = display_df['freight_promedio'].apply(lambda x: f"${x:.2f}")
    
    st.dataframe(display_df, use_container_width=True)

def get_satisfaction_data(conn):
    """Obtiene datos de satisfacción del cliente"""
    query = """
    SELECT
        orr.review_score as puntuacion,
        COUNT(*) as total_resenas,
        AVG(oi.price) as precio_promedio_pedido,
        AVG(oi.freight_value) as freight_promedio
    FROM order_reviews orr
    JOIN orders o ON orr.order_id = o.order_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY orr.review_score
    ORDER BY orr.review_score
    """
    
    return pd.read_sql_query(query, conn)

def get_satisfaction_by_state(conn):
    """Obtiene datos de satisfacción por estado"""
    query = """
    SELECT
        c.customer_state as estado,
        AVG(orr.review_score) as puntuacion_promedio,
        COUNT(orr.review_id) as total_resenas,
        AVG(oi.price) as precio_promedio_pedido
    FROM order_reviews orr
    JOIN orders o ON orr.order_id = o.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_state
    HAVING COUNT(orr.review_id) > 100
    ORDER BY puntuacion_promedio DESC
    """
    
    return pd.read_sql_query(query, conn)

def get_satisfaction_temporal(conn):
    """Obtiene evolución temporal de la satisfacción"""
    query = """
    SELECT
        strftime('%Y-%m', o.order_purchase_timestamp) as mes,
        AVG(orr.review_score) as puntuacion_promedio,
        COUNT(orr.review_id) as total_resenas
    FROM order_reviews orr
    JOIN orders o ON orr.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY mes
    HAVING COUNT(orr.review_id) > 10
    ORDER BY mes
    """
    
    return pd.read_sql_query(query, conn)