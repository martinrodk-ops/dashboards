"""
Product and Category Analysis Component
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.helpers import apply_custom_style

def show_product_analysis(conn):
    st.header("📦 Product and Category Analysis")
    
    # Load category data
    df_categories = get_category_data(conn)
    
    if df_categories.empty:
        st.warning("No product data found.")
        return
    
    # Quick metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        top_category = df_categories.iloc[0]['category']
        st.metric("🏆 Leading Category", top_category)
    with col2:
        st.metric("💰 Total Revenue", f"${df_categories['total_revenue'].sum():,.0f}")
    with col3:
        st.metric("📦 Total Orders", f"{df_categories['total_orders'].sum():,}")
    
    st.markdown("---")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        top_n = st.slider("Number of categories to display:", 5, 20, 10)
    with col2:
        min_orders = st.slider("Minimum orders per category:", 0, 1000, 100)
    
    # Filter data
    filtered_df = df_categories[df_categories['total_orders'] >= min_orders].head(top_n)
    
    # Main charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Top Categories by Revenue")
        fig = px.bar(filtered_df, x='category', y='total_revenue',
                     color='total_revenue', color_continuous_scale='viridis')
        fig = apply_custom_style(fig, f"Top {top_n} Categories by Revenue")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Relationship: Orders vs Average Price")
        fig = px.scatter(filtered_df, x='total_orders', y='average_price',
                         size='total_revenue', color='category',
                         hover_name='category', log_x=True,
                         labels={'total_orders': 'Total Orders', 
                                'average_price': 'Average Price ($)'})
        fig = apply_custom_style(fig, "Orders vs Average Price")
        st.plotly_chart(fig, use_container_width=True)
    
    # Secondary charts
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🥧 Revenue Distribution by Category")
        fig = px.pie(filtered_df, values='total_revenue', names='category')
        fig = apply_custom_style(fig, f"Revenue Distribution (Top {top_n})")
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.subheader("📦 Unique Products by Category")
        fig = px.bar(filtered_df, x='category', y='unique_products',
                     color='unique_products', color_continuous_scale='plasma')
        fig = apply_custom_style(fig, f"Unique Products by Category (Top {top_n})")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Individual product analysis
    st.subheader("🔍 Individual Product Analysis")
    
    df_top_products = get_top_products(conn)
    
    if not df_top_products.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top Selling Products")
            fig = px.bar(df_top_products.head(10), x='product_id', y='total_sold',
                         color='total_sold', color_continuous_scale='viridis',
                         labels={'total_sold': 'Total Sold ($)', 'product_id': 'Product'})
            fig = apply_custom_style(fig, "Top 10 Products by Sales")
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Product Sales Distribution")
            fig = px.box(df_top_products, y='total_sold', 
                         labels={'total_sold': 'Total Sold per Product ($)'})
            fig = apply_custom_style(fig, "Product Sales Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("📋 Detailed Data by Category")
    display_df = filtered_df.copy()
    display_df['total_revenue'] = display_df['total_revenue'].apply(lambda x: f"${x:,.2f}")
    display_df['average_price'] = display_df['average_price'].apply(lambda x: f"${x:.2f}")
    
    st.dataframe(display_df, use_container_width=True)

def get_category_data(conn):
    """Get product and category data"""
    # First, try to load category translations
    try:
        # Note: We assume the translation file is in Google Drive and loaded as 'product_category_name_translation'
        df_translations = pd.read_sql_query("SELECT * FROM product_category_name_translation", conn)
    except:
        df_translations = pd.DataFrame()

    query = """
    SELECT
        p.product_category_name as category,
        COUNT(DISTINCT oi.order_id) as total_orders,
        SUM(oi.price) as total_revenue,
        AVG(oi.price) as average_price,
        COUNT(DISTINCT oi.product_id) as unique_products
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY p.product_category_name
    HAVING COUNT(DISTINCT oi.order_id) > 100
    ORDER BY total_revenue DESC
    LIMIT 20
    """

    df_categories = pd.read_sql_query(query, conn)

    # If we have translations, translate category names
    if not df_translations.empty:
        df_categories = df_categories.merge(
            df_translations,
            left_on='category',
            right_on='product_category_name',
            how='left'
        )
        # Replace Portuguese names with English ones
        df_categories['category'] = df_categories['product_category_name_english'].fillna(df_categories['category'])

    return df_categories

def get_top_products(conn):
    """Get top selling products"""
    query = """
    SELECT
        p.product_id,
        p.product_category_name as category,
        COUNT(DISTINCT oi.order_id) as total_orders,
        SUM(oi.price) as total_sold,
        AVG(oi.price) as average_price
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY p.product_id, p.product_category_name
    HAVING COUNT(DISTINCT oi.order_id) >= 5
    ORDER BY total_sold DESC
    LIMIT 50
    """
    
    return pd.read_sql_query(query, conn)