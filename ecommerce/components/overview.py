import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def show_overview(conn):
    """
    Muestra el resumen estadístico ejecutivo
    """
    st.header("📊 Resumen Ejecutivo - E-commerce Brasileño")
    
    # Query para métricas principales
    query_base = """
    WITH pedidos_entregados AS (
        SELECT
            o.order_id,
            c.customer_unique_id,
            SUM(oi.price) as total_pedido
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY o.order_id, c.customer_unique_id
    )
    SELECT
        COUNT(DISTINCT order_id) as total_pedidos_entregados,
        COUNT(DISTINCT customer_unique_id) as clientes_unicos,
        AVG(total_pedido) as ticket_promedio,
        SUM(total_pedido) as ingresos_totales
    FROM pedidos_entregados
    """
    
    cursor = conn.cursor()
    cursor.execute(query_base)
    base_result = cursor.fetchone()
    total_pedidos, clientes_unicos, ticket_promedio, ingresos_totales = base_result
    
    # Otras métricas
    otras_queries = {
        'Total Productos en Catálogo': "SELECT COUNT(DISTINCT product_id) FROM products",
        'Vendedores Registrados': "SELECT COUNT(DISTINCT seller_id) FROM sellers",
        'Productos Vendidos': """
            SELECT COUNT(DISTINCT oi.product_id)
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_status = 'delivered'
        """
    }
    
    estadisticas = {
        'Pedidos Entregados': total_pedidos,
        'Clientes Únicos': clientes_unicos,
        'Ingresos Totales': ingresos_totales,
        'Ticket Promedio': ticket_promedio,
        'Pedidos por Cliente': total_pedidos / clientes_unicos if clientes_unicos > 0 else 0
    }
    
    for nombre, query in otras_queries.items():
        cursor.execute(query)
        estadisticas[nombre] = cursor.fetchone()[0]
    
    # Mostrar métricas en columnas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Pedidos Entregados", f"{estadisticas['Pedidos Entregados']:,}")
        st.metric("👥 Clientes Únicos", f"{estadisticas['Clientes Únicos']:,}")
    
    with col2:
        st.metric("💰 Ingresos Totales", f"${estadisticas['Ingresos Totales']:,.2f}")
        st.metric("🎫 Ticket Promedio", f"${estadisticas['Ticket Promedio']:.2f}")
    
    with col3:
        st.metric("📊 Pedidos/Cliente", f"{estadisticas['Pedidos por Cliente']:.2f}")
        st.metric("🏪 Vendedores", f"{estadisticas['Vendedores Registrados']:,}")
    
    with col4:
        st.metric("📦 Productos Catálogo", f"{estadisticas['Total Productos en Catálogo']:,}")
        st.metric("🛒 Productos Vendidos", f"{estadisticas['Productos Vendidos']:,}")
    
    # Tabla de resumen
    df_resumen = pd.DataFrame(list(estadisticas.items()), columns=['Métrica', 'Valor'])
    
    st.subheader("Resumen Estadístico Detallado")
    st.dataframe(df_resumen, use_container_width=True)