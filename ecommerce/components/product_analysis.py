import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show_product_analysis(conn):
    """
    Muestra el análisis de productos y categorías
    """
    st.header("📦 Análisis de Productos y Categorías")
    
    # Cargar traducciones
    try:
        df_translations = pd.read_csv('brazil_e_commerce/product_category_name_translation.csv')
    except:
        st.error("No se pudo cargar el archivo de traducciones")
        return
    
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
    LIMIT 15
    """
    
    df_categorias = pd.read_sql_query(query, conn)
    
    # Traducir categorías
    df_categorias = df_categorias.merge(
        df_translations,
        left_on='categoria',
        right_on='product_category_name',
        how='left'
    )
    df_categorias['categoria'] = df_categorias['product_category_name_english'].fillna(df_categorias['categoria'])
    
    # Filtro interactivo
    min_pedidos = st.slider(
        "Filtrar por mínimo de pedidos:",
        min_value=100,
        max_value=1000,
        value=100,
        step=50
    )
    
    df_filtrado = df_categorias[df_categorias['total_pedidos'] >= min_pedidos]
    
    # Visualizaciones
    tab1, tab2, tab3 = st.tabs(["Treemap", "Relación Pedidos-Precio", "Comparativas"])
    
    with tab1:
        fig_treemap = px.treemap(
            df_filtrado,
            path=['categoria'],
            values='ingresos_totales',
            title='Top Categorías por Ingresos (Treemap)'
        )
        st.plotly_chart(fig_treemap, use_container_width=True)
    
    with tab2:
        fig_scatter = px.scatter(
            df_filtrado,
            x='total_pedidos',
            y='precio_promedio',
            size='ingresos_totales',
            color='categoria',
            title='Relación: Pedidos vs Precio Promedio',
            hover_name='categoria'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pedidos = px.bar(
                df_filtrado.nlargest(10, 'total_pedidos'),
                x='categoria',
                y='total_pedidos',
                title='Top 10 Categorías por Pedidos'
            )
            st.plotly_chart(fig_pedidos, use_container_width=True)
        
        with col2:
            fig_productos = px.bar(
                df_filtrado.nlargest(10, 'productos_unicos'),
                x='categoria',
                y='productos_unicos',
                title='Top 10 Categorías por Productos Únicos'
            )
            st.plotly_chart(fig_productos, use_container_width=True)
    
    # Datos completos
    with st.expander("📋 Ver todas las categorías"):
        st.dataframe(df_filtrado, use_container_width=True)