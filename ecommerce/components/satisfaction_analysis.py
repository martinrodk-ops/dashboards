import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show_satisfaction_analysis(conn):
    """
    Muestra el análisis de satisfacción del cliente
    """
    st.header("😊 Análisis de Satisfacción del Cliente")
    
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
    
    df_satisfaccion = pd.read_sql_query(query, conn)
    
    # Métricas rápidas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        promedio_puntuacion = (df_satisfaccion['puntuacion'] * df_satisfaccion['total_resenas']).sum() / df_satisfaccion['total_resenas'].sum()
        st.metric("⭐ Puntuación Promedio", f"{promedio_puntuacion:.2f}")
    
    with col2:
        total_resenas = df_satisfaccion['total_resenas'].sum()
        st.metric("📝 Total Reseñas", f"{total_resenas:,}")
    
    with col3:
        puntuacion_5 = df_satisfaccion[df_satisfaccion['puntuacion'] == 5]['total_resenas'].sum()
        porcentaje_5 = (puntuacion_5 / total_resenas) * 100
        st.metric("🎯 Reseñas 5 Estrellas", f"{porcentaje_5:.1f}%")
    
    # Visualizaciones
    tab1, tab2, tab3, tab4 = st.tabs(["Distribución", "Precio vs Puntuación", 
                                     "Costo Envío vs Puntuación", "Relación Completa"])
    
    with tab1:
        fig_barras = px.bar(
            df_satisfaccion,
            x='puntuacion',
            y='total_resenas',
            title='Distribución de Puntuaciones de Reseñas',
            color='puntuacion',
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_barras, use_container_width=True)
    
    with tab2:
        fig_precio = px.scatter(
            df_satisfaccion,
            x='puntuacion',
            y='precio_promedio_pedido',
            size='total_resenas',
            title='Relación: Puntuación vs Precio Promedio',
            trendline="lowess"
        )
        st.plotly_chart(fig_precio, use_container_width=True)
    
    with tab3:
        fig_freight = px.scatter(
            df_satisfaccion,
            x='puntuacion',
            y='freight_promedio',
            size='total_resenas',
            title='Relación: Puntuación vs Costo de Envío Promedio',
            trendline="lowess"
        )
        st.plotly_chart(fig_freight, use_container_width=True)
    
    with tab4:
        fig_relacion = px.scatter(
            df_satisfaccion,
            x='precio_promedio_pedido',
            y='freight_promedio',
            size='total_resenas',
            color='puntuacion',
            title='Relación: Precio vs Costo Envío (Color por Puntuación)',
            hover_name='puntuacion'
        )
        st.plotly_chart(fig_relacion, use_container_width=True)
    
    # Análisis detallado
    with st.expander("🔍 Análisis Detallado"):
        st.write("""
        **Interpretación de los resultados:**
        - Puntuaciones más altas pueden correlacionarse con ciertos rangos de precio
        - El costo de envío puede influir en la satisfacción del cliente
        - Patrones específicos pueden indicar áreas de mejora
        """)
        st.dataframe(df_satisfaccion, use_container_width=True)