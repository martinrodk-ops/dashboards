"""
Componente de Análisis de Productos y Categorías
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.helpers import apply_custom_style

def show_product_analysis(conn):
    st.header("📦 Análisis de Productos y Categorías")
    
    # Cargar datos de categorías
    df_categorias = get_category_data(conn)
    
    if df_categorias.empty:
        st.warning("No se encontraron datos de productos.")
        return
    
    # Métricas rápidas
    col1, col2, col3 = st.columns(3)
    with col1:
        top_category = df_categorias.iloc[0]['categoria']
        st.metric("🏆 Categoría Líder", top_category)
    with col2:
        st.metric("💰 Ingresos Totales", f"${df_categorias['ingresos_totales'].sum():,.0f}")
    with col3:
        st.metric("📦 Pedidos Totales", f"{df_categorias['total_pedidos'].sum():,}")
    
    st.markdown("---")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        top_n = st.slider("Número de categorías a mostrar:", 5, 20, 10)
    with col2:
        min_orders = st.slider("Pedidos mínimos por categoría:", 0, 1000, 100)
    
    # Filtrar datos
    filtered_df = df_categorias[df_categorias['total_pedidos'] >= min_orders].head(top_n)
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Top Categorías por Ingresos")
        fig = px.bar(filtered_df, x='categoria', y='ingresos_totales',
                     color='ingresos_totales', color_continuous_scale='viridis')
        fig = apply_custom_style(fig, f"Top {top_n} Categorías por Ingresos")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Relación: Pedidos vs Precio Promedio")
        fig = px.scatter(filtered_df, x='total_pedidos', y='precio_promedio',
                         size='ingresos_totales', color='categoria',
                         hover_name='categoria', log_x=True,
                         labels={'total_pedidos': 'Total Pedidos', 
                                'precio_promedio': 'Precio Promedio ($)'})
        fig = apply_custom_style(fig, "Pedidos vs Precio Promedio")
        st.plotly_chart(fig, use_container_width=True)
    
    # Gráficos secundarios
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🥧 Distribución de Ingresos por Categoría")
        fig = px.pie(filtered_df, values='ingresos_totales', names='categoria')
        fig = apply_custom_style(fig, f"Distribución de Ingresos (Top {top_n})")
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.subheader("📦 Productos Únicos por Categoría")
        fig = px.bar(filtered_df, x='categoria', y='productos_unicos',
                     color='productos_unicos', color_continuous_scale='plasma')
        fig = apply_custom_style(fig, f"Productos Únicos por Categoría (Top {top_n})")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Análisis de productos individuales
    st.subheader("🔍 Análisis de Productos Individuales")
    
    df_top_products = get_top_products(conn)
    
    if not df_top_products.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Productos Más Vendidos")
            fig = px.bar(df_top_products.head(10), x='product_id', y='total_vendido',
                         color='total_vendido', color_continuous_scale='viridis',
                         labels={'total_vendido': 'Total Vendido ($)', 'product_id': 'Producto'})
            fig = apply_custom_style(fig, "Top 10 Productos por Ventas")
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Distribución de Ventas de Productos")
            fig = px.box(df_top_products, y='total_vendido', 
                         labels={'total_vendido': 'Total Vendido por Producto ($)'})
            fig = apply_custom_style(fig, "Distribución de Ventas por Producto")
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabla de datos
    st.subheader("📋 Datos Detallados por Categoría")
    display_df = filtered_df.copy()
    display_df['ingresos_totales'] = display_df['ingresos_totales'].apply(lambda x: f"${x:,.2f}")
    display_df['precio_promedio'] = display_df['precio_promedio'].apply(lambda x: f"${x:.2f}")
    
    st.dataframe(display_df, use_container_width=True)

def get_category_data(conn):
    """Obtiene datos de productos y categorías"""
    # Primero, intentamos cargar las traducciones de categorías
    try:
        # Nota: Asumimos que el archivo de traducciones está en Google Drive y se cargó como 'product_category_name_translation'
        df_translations = pd.read_sql_query("SELECT * FROM product_category_name_translation", conn)
    except:
        df_translations = pd.DataFrame()

    query = """
    SELECT
        p.product_category_name as categoria,
        COUNT(DISTINCT oi.order_id) as total_pedidos,
        SUM(oi.price) as ingresos_totales,
        AVG(oi.price) as precio_promedio,
        COUNT(DISTINCT oi.product_id) as productos_unicos
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY p.product_category_name
    HAVING COUNT(DISTINCT oi.order_id) > 100
    ORDER BY ingresos_totales DESC
    LIMIT 20
    """

    df_categorias = pd.read_sql_query(query, conn)

    # Si tenemos traducciones, traducir los nombres de las categorías
    if not df_translations.empty:
        df_categorias = df_categorias.merge(
            df_translations,
            left_on='categoria',
            right_on='product_category_name',
            how='left'
        )
        # Reemplazar los nombres en portugués por los en inglés
        df_categorias['categoria'] = df_categorias['product_category_name_english'].fillna(df_categorias['categoria'])

    return df_categorias

def get_top_products(conn):
    """Obtiene los productos más vendidos"""
    query = """
    SELECT
        p.product_id,
        p.product_category_name as categoria,
        COUNT(DISTINCT oi.order_id) as total_pedidos,
        SUM(oi.price) as total_vendido,
        AVG(oi.price) as precio_promedio
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY p.product_id, p.product_category_name
    HAVING COUNT(DISTINCT oi.order_id) >= 5
    ORDER BY total_vendido DESC
    LIMIT 50
    """
    
    return pd.read_sql_query(query, conn)