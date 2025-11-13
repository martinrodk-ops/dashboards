"""
Overview Component
"""
import streamlit as st
import pandas as pd

def show_overview(conn):
    st.header("📊 E-commerce Overview")
    
    # Queries for main metrics
    metrics = get_overview_metrics(conn)
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Delivered Orders", f"{metrics['total_orders']:,}")
    
    with col2:
        st.metric("👥 Unique Customers", f"{metrics['unique_customers']:,}")
    
    with col3:
        st.metric("💰 Total Revenue", f"${metrics['total_revenue']:,.2f}")
    
    with col4:
        st.metric("📚 Unique Products", f"{metrics['unique_products']:,}")
    
    st.markdown("---")
    
    # Secondary metrics
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric("🏪 Active Sellers", f"{metrics['active_sellers']:,}")
    
    with col6:
        st.metric("📈 Average Ticket", f"${metrics['avg_ticket']:.2f}")
    
    with col7:
        st.metric("🔄 Orders/Customer", f"{metrics['orders_per_customer']:.2f}")
    
    with col8:
        st.metric("⭐ Average Review Score", f"{metrics['avg_review_score']:.2f}")
    
    # Detailed summary table
    st.subheader("📋 Detailed Statistics")
    summary_df = create_summary_table(metrics)
    st.dataframe(summary_df, use_container_width=True)

def get_overview_metrics(conn):
    """Get main metrics for the overview"""
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
    """Create formatted summary table"""
    summary_data = {
        'Metric': [
            'Total Delivered Orders',
            'Unique Registered Customers', 
            'Total Generated Revenue',
            'Products in Catalog',
            'Registered Sellers',
            'Average Ticket per Order',
            'Orders per Customer (Average)',
            'Review Score (Average)'
        ],
        'Value': [
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