"""
Payment Methods Analysis Component with Viridis Theme
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.helpers import apply_viridis_style, get_viridis_color, format_currency, format_number

def show_payment_analysis(conn):
    st.header("💳 Payment Methods Analysis")
    
    # Load data
    df_payments = get_payment_data(conn)
    
    if df_payments.empty:
        st.warning("No payment data found.")
        return
    
    # Quick metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        top_method = df_payments.iloc[0]['payment_method']
        st.metric("🏆 Most Popular Method", top_method)
    with col2:
        st.metric("💰 Total Value", f"${df_payments['total_value'].sum():,.0f}")
    with col3:
        st.metric("🔄 Total Transactions", f"{df_payments['total_transactions'].sum():,}")
    
    st.markdown("---")
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Distribution by Total Value', 
            'Total Transactions by Method',
            'Average Value per Transaction', 
            'Unique Orders by Method'
        ),
        specs=[
            [{"type": "pie"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "bar"}]
        ],
        vertical_spacing=0.2,
        horizontal_spacing=0.1
    )
    
    # Viridis colors for payment methods
    n_methods = len(df_payments)
    colors = [get_viridis_color(i, n_methods) for i in range(n_methods)]
    
    # Chart 1: Distribution by Total Value (Pie)
    total_value = df_payments['total_value'].sum()
    percentages = (df_payments['total_value'] / total_value) * 100
    
    custom_labels = [
        f"{method}<br>{percentage:.1f}%" if percentage > 5 else ""
        for method, percentage in zip(df_payments['payment_method'], percentages)
    ]
    
    fig.add_trace(
        go.Pie(
            labels=df_payments['payment_method'],
            values=df_payments['total_value'],
            name='Total Value',
            text=custom_labels,
            textinfo='text',
            marker=dict(colors=colors, line=dict(color='#E0E0E0', width=1)),
            hovertemplate='<b>%{label}</b><br>Total Value: $%{value:,.2f}<br>Percentage: %{percent:.1%}<extra></extra>',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Chart 2: Total Transactions by Method (Bar)
    fig.add_trace(
        go.Bar(
            x=df_payments['payment_method'],
            y=df_payments['total_transactions'],
            marker_color=colors,
            marker_line=dict(color='#E0E0E0', width=1),
            hovertemplate='<b>%{x}</b><br>Total Transactions: %{y:,}<extra></extra>',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Chart 3: Average Value per Transaction (Bar)
    fig.add_trace(
        go.Bar(
            x=df_payments['payment_method'],
            y=df_payments['average_value'],
            marker_color=colors,
            marker_line=dict(color='#E0E0E0', width=1),
            hovertemplate='<b>%{x}</b><br>Average Value: $%{y:.2f}<extra></extra>',
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Chart 4: Unique Orders by Method (Bar)
    fig.add_trace(
        go.Bar(
            x=df_payments['payment_method'],
            y=df_payments['unique_orders'],
            marker_color=colors,
            marker_line=dict(color='#E0E0E0', width=1),
            hovertemplate='<b>%{x}</b><br>Unique Orders: %{y:,}<extra></extra>',
            showlegend=False
        ),
        row=2, col=2
    )
    
    # Update layout with Viridis style
    fig = apply_viridis_style(fig, "Payment Methods Analysis", height=900)
    
    # Add more spacing between the main title and subplots
    fig.update_layout(
        margin=dict(t=120),  # Increased top margin to create more space for the title
        title_y=0.95  # Position title closer to the top
    )
    
    # Update axes
    fig.update_xaxes(title_text="Payment Method", row=1, col=2, tickangle=45)
    fig.update_yaxes(title_text="Total Transactions", row=1, col=2)
    fig.update_xaxes(title_text="Payment Method", row=2, col=1, tickangle=45)
    fig.update_yaxes(title_text="Average Value ($)", row=2, col=1)
    fig.update_xaxes(title_text="Payment Method", row=2, col=2, tickangle=45)
    fig.update_yaxes(title_text="Unique Orders", row=2, col=2)
    
    # Hide axes for pie chart
    fig.update_xaxes(showticklabels=False, row=1, col=1)
    fig.update_yaxes(showticklabels=False, row=1, col=1)
    
    # Update subplot titles with better positioning
    for annotation in fig.layout.annotations:
        annotation.update(
            font=dict(size=14, color="#440154", family="Segoe UI, sans-serif"),
            y=annotation.y + 0.02
        )
    
    st.plotly_chart(fig, use_container_width=True)

def get_payment_data(conn):
    """Get payment methods data with bank_slip instead of boleto"""
    query = """
    SELECT
        CASE 
            WHEN op.payment_type = 'boleto' THEN 'bank_slip'
            ELSE op.payment_type 
        END as payment_method,
        COUNT(*) as total_transactions,
        SUM(op.payment_value) as total_value,
        AVG(op.payment_value) as average_value,
        COUNT(DISTINCT op.order_id) as unique_orders
    FROM order_payments op
    JOIN orders o ON op.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY payment_method
    ORDER BY total_value DESC
    """
    
    return pd.read_sql_query(query, conn)