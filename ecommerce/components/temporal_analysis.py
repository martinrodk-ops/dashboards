"""
Componente de Análisis Temporal - Versión Mejorada
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.helpers import apply_custom_style

def show_temporal_analysis(conn):
    st.header("⏰ Análisis Temporal de Ventas")
    
    # Cargar datos
    df_temporal = get_temporal_data(conn)
    
    if df_temporal.empty:
        st.warning("No se encontraron datos temporales.")
        return
    
    # Filtros y controles
    col1, col2 = st.columns(2)
    with col1:
        min_date = df_temporal['mes'].min()
        max_date = df_temporal['mes'].max()
        st.info(f"📅 Período de datos: {min_date} a {max_date}")
    
    with col2:
        selected_metric = st.selectbox(
            "📊 Seleccionar métrica principal:",
            ['ingresos_totales', 'total_pedidos', 'precio_promedio', 'clientes_unicos'],
            format_func=lambda x: {
                'ingresos_totales': 'Ingresos Totales',
                'total_pedidos': 'Total de Pedidos', 
                'precio_promedio': 'Precio Promedio',
                'clientes_unicos': 'Clientes Únicos'
            }[x]
        )
    
    # Gráfico principal de evolución
    st.subheader("📈 Evolución Temporal Principal")
    
    fig = go.Figure()
    
    # Configurar colores y métricas
    metric_config = {
        'ingresos_totales': {'color': '#1f77b4', 'name': 'Ingresos', 'suffix': '$', 'format': ',.0f'},
        'total_pedidos': {'color': '#ff7f0e', 'name': 'Pedidos', 'suffix': '', 'format': ',.0f'},
        'precio_promedio': {'color': '#2ca02c', 'name': 'Precio Promedio', 'suffix': '$', 'format': '.2f'},
        'clientes_unicos': {'color': '#d62728', 'name': 'Clientes Únicos', 'suffix': '', 'format': ',.0f'}
    }
    
    config = metric_config[selected_metric]
    
    fig.add_trace(go.Scatter(
        x=df_temporal['mes'],
        y=df_temporal[selected_metric],
        mode='lines+markers',
        name=config['name'],
        line=dict(color=config['color'], width=3),
        marker=dict(size=6),
        hovertemplate=f"<b>%{{x}}</b><br>{config['name']}: {config['suffix']}%{{y:{config['format']}}}<extra></extra>"
    ))
    
    fig = apply_custom_style(fig, f"Evolución de {config['name']}")
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Métricas de tendencia
    st.subheader("📊 Métricas de Tendencia")
    
    if len(df_temporal) > 1:
        # Calcular métricas de crecimiento
        first_value = df_temporal[selected_metric].iloc[0]
        last_value = df_temporal[selected_metric].iloc[-1]
        growth = ((last_value - first_value) / first_value) * 100 if first_value != 0 else 0
        
        # Calcular CAGR (si hay suficientes datos)
        if len(df_temporal) >= 2:
            periods = len(df_temporal) - 1
            cagr = ((last_value / first_value) ** (1/periods) - 1) * 100 if first_value != 0 else 0
        else:
            cagr = 0
        
        col3, col4, col5, col6 = st.columns(4)
        
        with col3:
            st.metric(f"{config['name']} Inicial", 
                     f"{config['suffix']}{first_value:{config['format']}}")
        with col4:
            st.metric(f"{config['name']} Final", 
                     f"{config['suffix']}{last_value:{config['format']}}",
                     delta=f"{growth:+.1f}%")
        with col5:
            avg_value = df_temporal[selected_metric].mean()
            st.metric(f"Promedio Mensual", f"{config['suffix']}{avg_value:{config['format']}}")
        with col6:
            st.metric("Crecimiento Anualizado", f"{cagr:+.1f}%")
    
    # Gráficos comparativos
    st.subheader("📊 Comparación de Métricas")
    
    # Normalizar métricas para comparación
    df_normalized = df_temporal.copy()
    for col in ['ingresos_totales', 'total_pedidos', 'clientes_unicos']:
        if col in df_normalized.columns and df_normalized[col].max() > 0:
            df_normalized[f'{col}_normalized'] = df_normalized[col] / df_normalized[col].max()
    
    fig = go.Figure()
    
    if 'ingresos_totales_normalized' in df_normalized.columns:
        fig.add_trace(go.Scatter(
            x=df_normalized['mes'], y=df_normalized['ingresos_totales_normalized'],
            mode='lines', name='Ingresos (normalizado)', line=dict(width=2)
        ))
    
    if 'total_pedidos_normalized' in df_normalized.columns:
        fig.add_trace(go.Scatter(
            x=df_normalized['mes'], y=df_normalized['total_pedidos_normalized'],
            mode='lines', name='Pedidos (normalizado)', line=dict(width=2)
        ))
    
    if 'clientes_unicos_normalized' in df_normalized.columns:
        fig.add_trace(go.Scatter(
            x=df_normalized['mes'], y=df_normalized['clientes_unicos_normalized'],
            mode='lines', name='Clientes (normalizado)', line=dict(width=2)
        ))
    
    fig = apply_custom_style(fig, "Comparación de Métricas (Normalizado)")
    fig.update_xaxes(tickangle=45)
    fig.update_yaxes(title_text="Valor Normalizado (0-1)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Análisis de estacionalidad
    st.subheader("📅 Análisis de Estacionalidad")
    
    df_temporal['mes_num'] = pd.to_datetime(df_temporal['mes']).dt.month
    estacionalidad = df_temporal.groupby('mes_num').agg({
        'ingresos_totales': 'mean',
        'total_pedidos': 'mean',
        'clientes_unicos': 'mean'
    }).reset_index()
    
    col7, col8 = st.columns(2)
    
    with col7:
        fig = px.bar(estacionalidad, x='mes_num', y='ingresos_totales',
                     labels={'mes_num': 'Mes del Año', 'ingresos_totales': 'Ingresos Promedio ($)'})
        fig = apply_custom_style(fig, "Estacionalidad - Ingresos Promedio por Mes")
        st.plotly_chart(fig, use_container_width=True)
    
    with col8:
        fig = px.line(estacionalidad, x='mes_num', y='total_pedidos', markers=True,
                     labels={'mes_num': 'Mes del Año', 'total_pedidos': 'Pedidos Promedio'})
        fig = apply_custom_style(fig, "Estacionalidad - Pedidos Promedio por Mes")
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabla de datos
    st.subheader("📋 Datos Mensuales Detallados")
    display_df = df_temporal.copy()
    
    # Formatear columnas numéricas
    if 'ingresos_totales' in display_df.columns:
        display_df['ingresos_totales'] = display_df['ingresos_totales'].apply(lambda x: f"${x:,.2f}")
    if 'precio_promedio' in display_df.columns:
        display_df['precio_promedio'] = display_df['precio_promedio'].apply(lambda x: f"${x:.2f}")
    
    st.dataframe(display_df, use_container_width=True)

def get_temporal_data(conn):
    """Obtiene datos agregados por mes"""
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
    
    return pd.read_sql_query(query, conn)