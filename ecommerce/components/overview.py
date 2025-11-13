"""
Componente de Resumen General
"""
import streamlit as st
import pandas as pd

def show_overview(conn):
    st.header("📊 Resumen General del E-commerce")
    
    # Consultas para métricas principales
    metrics = get_overview_metrics(conn)
    
    # Mostrar métricas en columnas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Pedidos Entregados", f"{metrics['total_orders']:,}")
    
    with col2:
        st.metric("👥 Clientes Únicos", f"{metrics['unique_customers']:,}")
    
    with col3:
        st.metric("💰 Ingresos Totales", f"${metrics['total_revenue']:,.2f}")
    
    with col4:
        st.metric("📚 Productos Únicos", f"{metrics['unique_products']:,}")
    
    st.markdown("---")
    
    # Métricas secundarias
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric("🏪 Vendedores Activos", f"{metrics['active_sellers']:,}")
    
    with col6:
        st.metric("📈 Ticket Promedio", f"${metrics['avg_ticket']:.2f}")
    
    with col7:
        st.metric("🔄 Pedidos/Cliente", f"{metrics['orders_per_customer']:.2f}")
    
    with col8:
        st.metric("⭐ Puntuación Promedio", f"{metrics['avg_review_score']:.2f}")
    
    # Tabla de resumen detallada
    st.subheader("📋 Estadísticas Detalladas")
    summary_df = create_summary_table(metrics)
    st.dataframe(summary_df, use_container_width=True)

def get_overview_metrics(conn):
    """Obtiene las métricas principales para el resumen"""
    queries = {
        'total_orders': """
            SELECT COUNT(DISTINCT order_id) 
            FROM orders 
            WHERE order_status = 'delivered'
        """,
        'unique_customers': """
            SELECT COUNT(DISTINCT customer_unique_id) 
            FROM customers
        """,
        'total_revenue': """
            SELECT SUM(oi.price) 
            FROM order_items oi 
            JOIN orders o ON oi.order_id = o.order_id 
            WHERE o.order_status = 'delivered'
        """,
        'unique_products': """
            SELECT COUNT(DISTINCT product_id) 
            FROM products
        """,
        'active_sellers': """
            SELECT COUNT(DISTINCT seller_id) 
            FROM sellers
        """,
        'avg_ticket': """
            SELECT AVG(sub.total) 
            FROM (
                SELECT oi.order_id, SUM(oi.price) as total
                FROM order_items oi 
                JOIN orders o ON oi.order_id = o.order_id 
                WHERE o.order_status = 'delivered'
                GROUP BY oi.order_id
            ) sub
        """,
        'orders_per_customer': """
            SELECT COUNT(DISTINCT o.order_id) / COUNT(DISTINCT c.customer_unique_id) 
            FROM orders o 
            JOIN customers c ON o.customer_id = c.customer_id 
            WHERE o.order_status = 'delivered'
        """,
        'avg_review_score': """
            SELECT AVG(review_score) 
            FROM order_reviews
        """
    }
    
    metrics = {}
    for key, query in queries.items():
        try:
            result = pd.read_sql_query(query, conn).iloc[0, 0]
            metrics[key] = result if result is not None else 0
        except:
            metrics[key] = 0
    
    return metrics

def create_summary_table(metrics):
    """Crea tabla de resumen formateada"""
    summary_data = {
        'Métrica': [
            'Total de Pedidos Entregados',
            'Clientes Únicos Registrados', 
            'Ingresos Totales Generados',
            'Productos en Catálogo',
            'Vendedores Registrados',
            'Ticket Promedio por Pedido',
            'Pedidos por Cliente (Promedio)',
            'Puntuación de Reseñas (Promedio)'
        ],
        'Valor': [
            f"{metrics['total_orders']:,}",
            f"{metrics['unique_customers']:,}",
            f"${metrics['total_revenue']:,.2f}",
            f"{metrics['unique_products']:,}",
            f"{metrics['active_sellers']:,}",
            f"${metrics['avg_ticket']:.2f}",
            f"{metrics['orders_per_customer']:.2f}",
            f"{metrics['avg_review_score']:.2f}/5.0"
        ]
    }
    
    return pd.DataFrame(summary_data)