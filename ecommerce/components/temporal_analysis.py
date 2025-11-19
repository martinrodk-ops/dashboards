"""
Temporal Analysis Component with Viridis Theme
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.helpers import apply_viridis_style, format_currency, format_number

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
    
    # Main evolution chart
    st.subheader("📈 Temporal Evolution")
    
    # Create subplots for comprehensive analysis
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Revenue Evolution Over Time', 
            'Orders Evolution Over Time',
            'Seasonality - Average Revenue by Month', 
            'Unique Customers Evolution'
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "bar"}, {"type": "scatter"}]
        ],
        vertical_spacing=0.22,  # Adjusted spacing for better balance
        horizontal_spacing=0.1
    )
    
    # Viridis colors
    colors = px.colors.sequential.Viridis
    
    # Chart 1: Revenue Evolution
    fig.add_trace(
        go.Scatter(
            x=df_temporal['month'],
            y=df_temporal['total_revenue'],
            mode='lines+markers',
            line=dict(color=colors[0], width=3),
            marker=dict(size=6, line=dict(color='#E0E0E0', width=1)),
            hovertemplate='<b>%{x}</b><br>Total Revenue: $%{y:,.0f}<extra></extra>',
            showlegend=False,
            name='Revenue'
        ),
        row=1, col=1
    )
    
    # Chart 2: Orders Evolution
    fig.add_trace(
        go.Scatter(
            x=df_temporal['month'],
            y=df_temporal['total_orders'],
            mode='lines+markers',
            line=dict(color=colors[2], width=3),
            marker=dict(size=6, line=dict(color='#E0E0E0', width=1)),
            hovertemplate='<b>%{x}</b><br>Total Orders: %{y:,}<extra></extra>',
            showlegend=False,
            name='Orders'
        ),
        row=1, col=2
    )
    
    # Chart 3: Seasonality (Average revenue by month)
    df_temporal['month_num'] = pd.to_datetime(df_temporal['month']).dt.month
    seasonality = df_temporal.groupby('month_num').agg({
        'total_revenue': 'mean',
        'total_orders': 'mean',
        'average_price': 'mean',
        'unique_customers': 'mean'
    }).reset_index()
    
    fig.add_trace(
        go.Bar(
            x=seasonality['month_num'],
            y=seasonality['total_revenue'],
            marker_color=colors[4],
            marker_line=dict(color='#E0E0E0', width=1),
            hovertemplate='<b>Month: %{x}</b><br>Average Revenue: $%{y:,.0f}<extra></extra>',
            showlegend=False,
            name='Avg Revenue'
        ),
        row=2, col=1
    )
    
    # Chart 4: Unique Customers
    fig.add_trace(
        go.Scatter(
            x=df_temporal['month'],
            y=df_temporal['unique_customers'],
            mode='lines+markers',
            line=dict(color=colors[6], width=3),
            marker=dict(size=6, line=dict(color='#E0E0E0', width=1)),
            hovertemplate='<b>%{x}</b><br>Unique Customers: %{y:,}<extra></extra>',
            showlegend=False,
            name='Unique Customers'
        ),
        row=2, col=2
    )
    
    # Update layout with Viridis style
    fig = apply_viridis_style(fig, "Comprehensive Temporal Analysis", height=800)
    
    # Update axes
    fig.update_xaxes(title_text="Month", row=1, col=1, tickangle=45)
    fig.update_yaxes(title_text="Total Revenue ($)", row=1, col=1)
    fig.update_xaxes(title_text="Month", row=1, col=2, tickangle=45)
    fig.update_yaxes(title_text="Total Orders", row=1, col=2)
    fig.update_xaxes(title_text="Month of Year", row=2, col=1)
    fig.update_yaxes(title_text="Average Revenue ($)", row=2, col=1)
    fig.update_xaxes(title_text="Month", row=2, col=2, tickangle=45)
    fig.update_yaxes(title_text="Unique Customers", row=2, col=2)
    
    # Update subplot titles with better positioning
    for annotation in fig.layout.annotations:
        annotation.update(
            font=dict(size=14, color="#440154", family="Segoe UI, sans-serif"),
            y=annotation.y + 0.02  # Move titles up slightly
        )
    
    # Add more spacing between the main title and subplots
    fig.update_layout(
        margin=dict(t=120, b=80),  # Adjusted margins for better balance
        title_y=0.95  # Position title closer to the top
    )
    
    st.plotly_chart(fig, use_container_width=True)

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
