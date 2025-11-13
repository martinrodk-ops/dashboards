"""
Payment Methods Analysis Component
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.helpers import apply_custom_style

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
        st.metric("💰 Total Value", f"${df_payments['total_value'].sum():,.2f}")
    with col3:
        st.metric("🔄 Transactions", f"{df_payments['total_transactions'].sum():,}")
    
    st.markdown("---")
    
    # Main charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribution by Value")
        fig = px.pie(df_payments, values='total_value', names='payment_method',
                    hover_data=['total_transactions'])
        fig = apply_custom_style(fig, "Distribution by Total Value")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Transactions by Method")
        fig = px.bar(df_payments, x='payment_method', y='total_transactions',
                    color='total_transactions', color_continuous_scale='viridis')
        fig = apply_custom_style(fig, "Total Transactions by Payment Method")
        st.plotly_chart(fig, use_container_width=True)
    
    # Secondary charts
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("💲 Average Value per Transaction")
        fig = px.bar(df_payments, x='payment_method', y='average_value',
                    color='average_value', color_continuous_scale='plasma')
        fig = apply_custom_style(fig, "Average Value per Transaction")
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.subheader("🎯 Unique Orders by Method")
        fig = px.bar(df_payments, x='payment_method', y='unique_orders',
                    color='unique_orders', color_continuous_scale='thermal')
        fig = apply_custom_style(fig, "Unique Orders by Payment Method")
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("📋 Payment Methods Summary")
    display_df = df_payments.copy()
    display_df['total_value'] = display_df['total_value'].apply(
        lambda x: f"${x:,.2f}")
    display_df['average_value'] = display_df['average_value'].apply(
        lambda x: f"${x:.2f}")
    
    st.dataframe(display_df, use_container_width=True)

def get_payment_data(conn):
    """Get payment methods data"""
    query = """
    SELECT
        op.payment_type as payment_method,
        COUNT(*) as total_transactions,
        SUM(op.payment_value) as total_value,
        AVG(op.payment_value) as average_value,
        COUNT(DISTINCT op.order_id) as unique_orders
    FROM order_payments op
    JOIN orders o ON op.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY op.payment_type
    ORDER BY total_value DESC
    """
    
    return pd.read_sql_query(query, conn)