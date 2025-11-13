"""
Temporal Analysis Component
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.helpers import apply_custom_style

def show_temporal_analysis(conn):
    st.header("⏰ Temporal Sales Analysis")
    
    # Load data
    df_temporal = get_temporal_data(conn)
    
    if df_temporal.empty:
        st.warning("No temporal data found.")
        return
    
    # Filters and controls
    col1, col2 = st.columns(2)
    with col1:
        min_date = df_temporal['month'].min()
        max_date = df_temporal['month'].max()
        st.info(f"📅 Data period: {min_date} to {max_date}")
    
    with col2:
        selected_metric = st.selectbox(
            "📊 Select main metric:",
            ['total_revenue', 'total_orders', 'average_price', 'unique_customers'],
            format_func=lambda x: {
                'total_revenue': 'Total Revenue',
                'total_orders': 'Total Orders', 
                'average_price': 'Average Price',
                'unique_customers': 'Unique Customers'
            }[x]
        )
    
    # Main evolution chart
    st.subheader("📈 Main Temporal Evolution")
    
    fig = go.Figure()
    
    # Configure colors and metrics
    metric_config = {
        'total_revenue': {'color': '#1f77b4', 'name': 'Revenue', 'suffix': '$', 'format': ',.0f'},
        'total_orders': {'color': '#ff7f0e', 'name': 'Orders', 'suffix': '', 'format': ',.0f'},
        'average_price': {'color': '#2ca02c', 'name': 'Average Price', 'suffix': '$', 'format': '.2f'},
        'unique_customers': {'color': '#d62728', 'name': 'Unique Customers', 'suffix': '', 'format': ',.0f'}
    }
    
    config = metric_config[selected_metric]
    
    fig.add_trace(go.Scatter(
        x=df_temporal['month'],
        y=df_temporal[selected_metric],
        mode='lines+markers',
        name=config['name'],
        line=dict(color=config['color'], width=3),
        marker=dict(size=6),
        hovertemplate=f"<b>%{{x}}</b><br>{config['name']}: {config['suffix']}%{{y:{config['format']}}}<extra></extra>"
    ))
    
    fig = apply_custom_style(fig, f"Evolution of {config['name']}")
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Trend metrics
    st.subheader("📊 Trend Metrics")
    
    if len(df_temporal) > 1:
        # Calculate growth metrics
        first_value = df_temporal[selected_metric].iloc[0]
        last_value = df_temporal[selected_metric].iloc[-1]
        growth = ((last_value - first_value) / first_value) * 100 if first_value != 0 else 0
        
        # Calculate CAGR (if enough data)
        if len(df_temporal) >= 2:
            periods = len(df_temporal) - 1
            cagr = ((last_value / first_value) ** (1/periods) - 1) * 100 if first_value != 0 else 0
        else:
            cagr = 0
        
        col3, col4, col5, col6 = st.columns(4)
        
        with col3:
            st.metric(f"{config['name']} Initial", 
                     f"{config['suffix']}{first_value:{config['format']}}")
        with col4:
            st.metric(f"{config['name']} Final", 
                     f"{config['suffix']}{last_value:{config['format']}}",
                     delta=f"{growth:+.1f}%")
        with col5:
            avg_value = df_temporal[selected_metric].mean()
            st.metric(f"Monthly Average", f"{config['suffix']}{avg_value:{config['format']}}")
        with col6:
            st.metric("Annualized Growth", f"{cagr:+.1f}%")
    
    # Comparative charts
    st.subheader("📊 Metrics Comparison")
    
    # Normalize metrics for comparison
    df_normalized = df_temporal.copy()
    for col in ['total_revenue', 'total_orders', 'unique_customers']:
        if col in df_normalized.columns and df_normalized[col].max() > 0:
            df_normalized[f'{col}_normalized'] = df_normalized[col] / df_normalized[col].max()
    
    fig = go.Figure()
    
    if 'total_revenue_normalized' in df_normalized.columns:
        fig.add_trace(go.Scatter(
            x=df_normalized['month'], y=df_normalized['total_revenue_normalized'],
            mode='lines', name='Revenue (normalized)', line=dict(width=2)
        ))
    
    if 'total_orders_normalized' in df_normalized.columns:
        fig.add_trace(go.Scatter(
            x=df_normalized['month'], y=df_normalized['total_orders_normalized'],
            mode='lines', name='Orders (normalized)', line=dict(width=2)
        ))
    
    if 'unique_customers_normalized' in df_normalized.columns:
        fig.add_trace(go.Scatter(
            x=df_normalized['month'], y=df_normalized['unique_customers_normalized'],
            mode='lines', name='Customers (normalized)', line=dict(width=2)
        ))
    
    fig = apply_custom_style(fig, "Metrics Comparison (Normalized)")
    fig.update_xaxes(tickangle=45)
    fig.update_yaxes(title_text="Normalized Value (0-1)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Seasonality analysis
    st.subheader("📅 Seasonality Analysis")
    
    df_temporal['month_num'] = pd.to_datetime(df_temporal['month']).dt.month
    seasonality = df_temporal.groupby('month_num').agg({
        'total_revenue': 'mean',
        'total_orders': 'mean',
        'unique_customers': 'mean'
    }).reset_index()
    
    col7, col8 = st.columns(2)
    
    with col7:
        fig = px.bar(seasonality, x='month_num', y='total_revenue',
                     labels={'month_num': 'Month of the Year', 'total_revenue': 'Average Revenue ($)'})
        fig = apply_custom_style(fig, "Seasonality - Average Revenue by Month")
        st.plotly_chart(fig, use_container_width=True)
    
    with col8:
        fig = px.line(seasonality, x='month_num', y='total_orders', markers=True,
                     labels={'month_num': 'Month of the Year', 'total_orders': 'Average Orders'})
        fig = apply_custom_style(fig, "Seasonality - Average Orders by Month")
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("📋 Detailed Monthly Data")
    display_df = df_temporal.copy()
    
    # Format numeric columns
    if 'total_revenue' in display_df.columns:
        display_df['total_revenue'] = display_df['total_revenue'].apply(lambda x: f"${x:,.2f}")
    if 'average_price' in display_df.columns:
        display_df['average_price'] = display_df['average_price'].apply(lambda x: f"${x:.2f}")
    
    st.dataframe(display_df, use_container_width=True)

def get_temporal_data(conn):
    """Get data aggregated by month"""
    query = """
    SELECT
        strftime('%Y-%m', o.order_purchase_timestamp) as month,
        COUNT(DISTINCT o.order_id) as total_orders,
        SUM(oi.price) as total_revenue,
        AVG(oi.price) as average_price,
        COUNT(DISTINCT c.customer_unique_id) as unique_customers
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY month
    ORDER BY month
    """
    
    return pd.read_sql_query(query, conn)