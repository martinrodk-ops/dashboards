"""
Sales Analysis by State Component
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.helpers import apply_custom_style

def show_sales_analysis(conn):
    st.header("🏢 Sales Analysis by State")
    
    # Load data
    df_sales = get_sales_by_state(conn)
    
    if df_sales.empty:
        st.warning("No sales data by state found.")
        return
    
    # Quick metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏆 Leading State", df_sales.iloc[0]['state'])
    with col2:
        st.metric("💰 Max Revenue", f"${df_sales['total_revenue'].max():,.0f}")
    with col3:
        st.metric("📦 Total Orders", f"{df_sales['total_orders'].sum():,}")
    
    st.markdown("---")
    
    # Main charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Revenue by State")
        fig = px.bar(df_sales, x='state', y='total_revenue',
                    color='total_revenue', color_continuous_scale='viridis',
                    labels={'total_revenue': 'Total Revenue ($)', 'state': 'State'})
        fig = apply_custom_style(fig, "Revenue Distribution by State")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Orders by State")
        fig = px.bar(df_sales, x='state', y='total_orders',
                    color='total_orders', color_continuous_scale='plasma',
                    labels={'total_orders': 'Total Orders', 'state': 'State'})
        fig = apply_custom_style(fig, "Orders Distribution by State")
        st.plotly_chart(fig, use_container_width=True)
    
    # Secondary charts
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🥧 Revenue Distribution")
        fig = px.pie(df_sales, values='total_revenue', names='state',
                    hover_data=['total_orders'])
        fig = apply_custom_style(fig, "Revenue Share by State")
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.subheader("💲 Average Price by State")
        fig = px.scatter(df_sales, x='total_orders', y='average_price',
                        size='total_revenue', color='state',
                        hover_name='state', log_x=True,
                        labels={'total_orders': 'Total Orders', 
                               'average_price': 'Average Price ($)'})
        fig = apply_custom_style(fig, "Relationship: Orders vs Average Price")
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("📋 Detailed Data by State")
    display_df = df_sales.copy()
    display_df['total_revenue'] = display_df['total_revenue'].apply(
        lambda x: f"${x:,.2f}")
    display_df['average_price'] = display_df['average_price'].apply(
        lambda x: f"${x:.2f}")
    
    st.dataframe(display_df, use_container_width=True)

def get_sales_by_state(conn):
    """Get sales data grouped by state"""
    query = """
    SELECT 
        c.customer_state as state,
        COUNT(DISTINCT o.order_id) as total_orders,
        SUM(oi.price) as total_revenue,
        AVG(oi.price) as average_price
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_state
    ORDER BY total_revenue DESC
    """
    
    return pd.read_sql_query(query, conn)