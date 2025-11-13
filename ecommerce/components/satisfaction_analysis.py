"""
Customer Satisfaction Analysis Component
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.helpers import apply_custom_style

def show_satisfaction_analysis(conn):
    st.header("😊 Customer Satisfaction Analysis")
    
    # Load satisfaction data
    df_satisfaction = get_satisfaction_data(conn)
    
    if df_satisfaction.empty:
        st.warning("No satisfaction data found.")
        return
    
    # Quick metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_score = df_satisfaction['review_score'].mean()
        st.metric("⭐ Average Review Score", f"{avg_score:.2f}")
    with col2:
        total_reviews = df_satisfaction['total_reviews'].sum()
        st.metric("📝 Total Reviews", f"{total_reviews:,}")
    with col3:
        most_common_score = df_satisfaction.loc[df_satisfaction['total_reviews'].idxmax(), 'review_score']
        st.metric("🎯 Most Common Score", most_common_score)
    
    st.markdown("---")
    
    # Review score distribution
    st.subheader("📊 Review Score Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart
        fig = px.bar(df_satisfaction, x='review_score', y='total_reviews',
                     color='total_reviews', color_continuous_scale='viridis',
                     labels={'total_reviews': 'Total Reviews', 'review_score': 'Review Score'})
        fig = apply_custom_style(fig, "Review Score Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Pie chart
        fig = px.pie(df_satisfaction, values='total_reviews', names='review_score',
                     hover_data=['average_order_price'])
        fig = apply_custom_style(fig, "Percentage by Review Score")
        st.plotly_chart(fig, use_container_width=True)
    
    # Relationship between price and satisfaction
    st.subheader("💲 Relationship: Price vs Satisfaction")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Average price vs review score
        fig = px.scatter(df_satisfaction, x='review_score', y='average_order_price',
                         size='total_reviews', color='review_score',
                         trendline="lowess",
                         labels={'average_order_price': 'Average Order Price ($)', 
                                'review_score': 'Review Score'})
        fig = apply_custom_style(fig, "Average Price vs Review Score")
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        # Shipping cost vs review score
        fig = px.scatter(df_satisfaction, x='review_score', y='average_freight_value',
                         size='total_reviews', color='review_score',
                         trendline="lowess",
                         labels={'average_freight_value': 'Average Shipping Cost ($)',
                                'review_score': 'Review Score'})
        fig = apply_custom_style(fig, "Shipping Cost vs Review Score")
        st.plotly_chart(fig, use_container_width=True)
    
    # Analysis by state
    st.subheader("🏢 Satisfaction by State")
    
    df_satisfaction_state = get_satisfaction_by_state(conn)
    
    if not df_satisfaction_state.empty:
        col5, col6 = st.columns(2)
        
        with col5:
            # Average review score by state
            fig = px.bar(df_satisfaction_state, x='state', y='average_review_score',
                         color='average_review_score', color_continuous_scale='plasma',
                         labels={'average_review_score': 'Average Review Score', 
                                'state': 'State'})
            fig = apply_custom_style(fig, "Average Review Score by State")
            st.plotly_chart(fig, use_container_width=True)
        
        with col6:
            # Reviews by state heatmap
            st.subheader("📈 Reviews by State")
            display_df = df_satisfaction_state[['state', 'total_reviews', 'average_review_score']].copy()
            display_df['average_review_score'] = display_df['average_review_score'].round(2)
            display_df = display_df.sort_values('average_review_score', ascending=False)
            st.dataframe(display_df, use_container_width=True)
    
    # Temporal satisfaction analysis
    st.subheader("⏰ Temporal Satisfaction Evolution")
    
    df_satisfaction_temporal = get_satisfaction_temporal(conn)
    
    if not df_satisfaction_temporal.empty:
        fig = px.line(df_satisfaction_temporal, x='month', y='average_review_score',
                      markers=True, line_shape='linear',
                      labels={'average_review_score': 'Average Review Score', 'month': 'Month'})
        fig = apply_custom_style(fig, "Satisfaction Evolution Over Time")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Complete data table
    st.subheader("📋 Detailed Satisfaction Data")
    display_df = df_satisfaction.copy()
    display_df['average_order_price'] = display_df['average_order_price'].apply(lambda x: f"${x:.2f}")
    display_df['average_freight_value'] = display_df['average_freight_value'].apply(lambda x: f"${x:.2f}")
    
    st.dataframe(display_df, use_container_width=True)

def get_satisfaction_data(conn):
    """Get customer satisfaction data"""
    query = """
    SELECT
        orr.review_score as review_score,
        COUNT(*) as total_reviews,
        AVG(oi.price) as average_order_price,
        AVG(oi.freight_value) as average_freight_value
    FROM order_reviews orr
    JOIN orders o ON orr.order_id = o.order_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY orr.review_score
    ORDER BY orr.review_score
    """
    
    return pd.read_sql_query(query, conn)

def get_satisfaction_by_state(conn):
    """Get satisfaction data by state"""
    query = """
    SELECT
        c.customer_state as state,
        AVG(orr.review_score) as average_review_score,
        COUNT(orr.review_id) as total_reviews,
        AVG(oi.price) as average_order_price
    FROM order_reviews orr
    JOIN orders o ON orr.order_id = o.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_state
    HAVING COUNT(orr.review_id) > 100
    ORDER BY average_review_score DESC
    """
    
    return pd.read_sql_query(query, conn)

def get_satisfaction_temporal(conn):
    """Get temporal evolution of satisfaction"""
    query = """
    SELECT
        strftime('%Y-%m', o.order_purchase_timestamp) as month,
        AVG(orr.review_score) as average_review_score,
        COUNT(orr.review_id) as total_reviews
    FROM order_reviews orr
    JOIN orders o ON orr.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY month
    HAVING COUNT(orr.review_id) > 10
    ORDER BY month
    """
    
    return pd.read_sql_query(query, conn)