"""
Overview Component with Viridis Theme - CORRECTED
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.helpers import apply_viridis_style, format_currency, format_number, format_integer

def show_overview(conn):
    st.header("📊 E-commerce Overview")
    
    # Get main metrics
    metrics = get_overview_metrics(conn)
    
    # Display metrics in columns with Viridis colors
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📦 Delivered Orders", 
            format_integer(metrics['total_orders'])
        )
    
    with col2:
        st.metric(
            "👥 Unique Customers", 
            format_integer(metrics['unique_customers'])
        )
    
    with col3:
        st.metric(
            "💰 Total Revenue", 
            format_currency(metrics['total_revenue'])
        )
    
    with col4:
        st.metric(
            "📚 Unique Products", 
            format_integer(metrics['unique_products'])
        )
    
    st.markdown("---")
    
    # Secondary metrics
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric("🏪 Active Sellers", format_integer(metrics['active_sellers']))
    
    with col6:
        st.metric("📈 Average Ticket", format_currency(metrics['avg_ticket']))
    
    with col7:
        # Calculate and show Revenue per Customer directly
        revenue_per_customer = metrics['total_revenue'] / max(metrics['unique_customers'], 1)
        st.metric("💰 Revenue per Customer", format_currency(revenue_per_customer))
    
    with col8:
        # Corrected format for review score
        review_score = metrics['avg_review_score']
        if review_score == int(review_score):
            formatted_score = str(int(review_score))
        else:
            formatted_score = f"{review_score:.1f}"
        st.metric("⭐ Avg Review Score", formatted_score)
    
    # Performance indicators - ONLY VALID INDICATORS
    st.subheader("📈 Performance Indicators")
    
    # MEANINGFUL CALCULATIONS - Only revenue efficiency and service quality
    perf_data = {
        'Metric': ['Revenue Efficiency', 'Service Quality'],
        'Value': [
            # Revenue Efficiency: Revenue per customer vs reasonable target
            min((metrics['total_revenue'] / max(metrics['unique_customers'], 1)) / 500 * 100, 100),
            
            # Service Quality: Convert 5-star scale to percentage
            min(metrics['avg_review_score'] / 5 * 100, 100)
        ]
    }
    
    perf_df = pd.DataFrame(perf_data)
    
    fig = go.Figure()
    
    # Use Viridis colors correctly
    viridis_colors = px.colors.sequential.Viridis
    
    for i, row in perf_df.iterrows():
        fig.add_trace(go.Bar(
            x=[row['Value']],
            y=[row['Metric']],
            orientation='h',
            name=row['Metric'],
            marker_color=viridis_colors[i * 3 % len(viridis_colors)],
            hovertemplate=f"<b>{row['Metric']}</b><br>Score: {row['Value']:.1f}%<extra></extra>"
        ))
    
    fig = apply_viridis_style(fig, "Business Performance Metrics")
    fig.update_layout(
        showlegend=False, 
        height=200,
        title={
            'text': "Business Performance Metrics",
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 16}
        }
    )
    fig.update_xaxes(range=[0, 100], title_text="Score (%)")
    
    st.plotly_chart(fig, use_container_width=True)

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