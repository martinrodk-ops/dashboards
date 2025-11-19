"""
Product and Category Analysis Component with Viridis Theme - LAYOUT OPTIMIZADO
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.helpers import apply_viridis_style, get_viridis_color, format_currency, format_number

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
        total_rev = df_categories['total_revenue'].sum()
        st.metric("💰 Total Revenue", format_currency(total_rev))
    with col3:
        total_orders = df_categories['total_orders'].sum()
        st.metric("📦 Total Orders", format_number(total_orders))
    
    st.markdown("---")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        top_n = st.slider("Number of categories to display:", 5, 20, 10)
    with col2:
        min_orders = st.slider("Minimum orders per category:", 0, 1000, 100)
    
    # Filter data
    filtered_df = df_categories[df_categories['total_orders'] >= min_orders].head(top_n)
    
    # CALCULAR PORCENTAJES MANUALMENTE PARA EL TREEMAP
    total_revenue = filtered_df['total_revenue'].sum()
    filtered_df = filtered_df.copy()
    filtered_df['percentage'] = (filtered_df['total_revenue'] / total_revenue * 100).round(1)

    # NUEVO LAYOUT: Treemap en primera fila completa, 3 gráficos en segunda fila
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=(
            'Top Categories by Revenue', 
            'Relationship: Orders vs Average Price',
            'Top Categories by Total Orders', 
            'Unique Products by Category'
        ),
        specs=[
            [{"type": "domain", "colspan": 3}, None, None],  # Treemap ocupa 3 columnas
            [{"type": "xy"}, {"type": "xy"}, {"type": "xy"}]  # 3 gráficos en segunda fila
        ],
        vertical_spacing=0.15,  # Buen espacio entre filas
        horizontal_spacing=0.10, # Buen espacio entre columnas
        row_heights=[0.6, 0.4]  # Treemap más alto
    )
    
    # Viridis colors for categories
    n_categories = len(filtered_df)
    colors = [get_viridis_color(i, n_categories) for i in range(n_categories)]
    
    # Chart 1: Treemap of categories by revenue - PRIMERA FILA COMPLETA
    fig.add_trace(
        go.Treemap(
            labels=filtered_df['category'],
            parents=[''] * len(filtered_df),
            values=filtered_df['total_revenue'],
            textinfo="label+value+percent root",
            textfont=dict(size=14, family="Segoe UI, sans-serif"),
            marker=dict(
                colors=colors, 
                line=dict(color='#E0E0E0', width=2),
                depthfade=True
            ),
            hovertemplate=(
            '<b>%{label}</b><br>' +
            'Total Revenue: $%{value:,.0f}<br>' +
            'Percentage: %{customdata:.1f}%<br>' +
            '<extra></extra>'
            ),
            customdata=filtered_df['percentage'],
            name='Revenue Treemap',
            pathbar=dict(visible=True),
            tiling=dict(pad=10)
        ),
        row=1, col=1  # Ocupa toda la primera fila debido al colspan=3
    )
    
    # Chart 2: Scatter plot of orders vs price - SEGUNDA FILA, COLUMNA 1
    fig.add_trace(
        go.Scatter(
            x=filtered_df['total_orders'],
            y=filtered_df['average_price'],
            mode='markers',
            marker=dict(
                size=filtered_df['total_revenue'] / filtered_df['total_revenue'].max() * 40 + 12,
                color=colors,
                line=dict(color='#E0E0E0', width=1),
                opacity=0.8
            ),
            text=filtered_df['category'],
            hovertemplate='<b>%{text}</b><br>Total Orders: %{x:,}<br>Average Price: $%{y:.2f}<extra></extra>',
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Chart 3: Total orders by category - SEGUNDA FILA, COLUMNA 2
    fig.add_trace(
        go.Bar(
            x=filtered_df['category'],
            y=filtered_df['total_orders'],
            marker_color=colors,
            marker_line=dict(color='#E0E0E0', width=1),
            hovertemplate='<b>%{x}</b><br>Total Orders: %{y:,}<extra></extra>',
            showlegend=False
        ),
        row=2, col=2
    )
    
    # Chart 4: Unique products by category - SEGUNDA FILA, COLUMNA 3
    fig.add_trace(
        go.Bar(
            x=filtered_df['category'],
            y=filtered_df['unique_products'],
            marker_color=colors,
            marker_line=dict(color='#E0E0E0', width=1),
            hovertemplate='<b>%{x}</b><br>Unique Products: %{y:,}<extra></extra>',
            showlegend=False
        ),
        row=2, col=3
    )
    
    # LAYOUT CON ESPACIADO OPTIMIZADO
    fig.update_layout(
        height=2000,  # Altura adecuada para el nuevo layout
        showlegend=False,
        title={
            'text': f"Product Analysis by Category (Top {top_n})",
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 22, 'color': '#440154', 'family': "Segoe UI, sans-serif"}
        },
        margin=dict(t=140, b=80, l=80, r=80, pad=15)  # Márgenes generosos
    )
    
    # Aplicar estilo Viridis base
    fig = apply_viridis_style(fig)
    
    # Update axes para los gráficos de la segunda fila
    fig.update_xaxes(title_text="Total Orders", row=2, col=1)
    fig.update_yaxes(title_text="Average Price ($)", row=2, col=1)
    fig.update_xaxes(title_text="Category", row=2, col=2, tickangle=45)
    fig.update_yaxes(title_text="Total Orders", row=2, col=2)
    fig.update_xaxes(title_text="Category", row=2, col=3, tickangle=45)
    fig.update_yaxes(title_text="Unique Products", row=2, col=3)
    
    # Hide axes for treemap
    fig.update_xaxes(showticklabels=False, showgrid=False, row=1, col=1)
    fig.update_yaxes(showticklabels=False, showgrid=False, row=1, col=1)
    
    # AJUSTE DE TÍTULOS DE SUBPLOTS CON BUEN ESPACIADO
    for i, annotation in enumerate(fig.layout.annotations):
        if i == 0:  # Título del treemap (primera fila)
            annotation.update(
                x=0.5,  # Centrado en toda la fila
                y=0.999,  # Muy arriba del treemap
                xanchor='center',
                yanchor='top',
                font=dict(size=16, color="#440154", family="Segoe UI, sans-serif")
            )
        else:  # Títulos de los gráficos de la segunda fila
            # Posiciones X para cada columna (0.17, 0.5, 0.83)
            col_positions = [0.13, 0.5, 0.87]
            annotation.update(
                x=col_positions[i-1],  # i-1 porque el primer título es el del treemap
                y=0.4,  # Bien arriba de los gráficos de la segunda fila
                xanchor='center',
                yanchor='top',
                font=dict(size=14, color="#440154", family="Segoe UI, sans-serif")
            )
    
    st.plotly_chart(fig, use_container_width=True)

def get_category_data(conn):
    """Get product and category data with proper translations - CORREGIDO"""
    # CORRECCIÓN: Cargar traducciones desde la tabla correcta
    try:
        # Cambiar el nombre de la tabla a 'category_translations'
        df_translations = pd.read_sql_query("SELECT * FROM category_translations", conn)
    except Exception as e:
        st.warning(f"⚠️ No se pudieron cargar las traducciones: {e}")
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

    # Apply translations if available - CORREGIDO
    if not df_translations.empty:
        # Verificar las columnas disponibles en las traducciones
        portuguese_col = df_translations.columns[0]
        english_col = df_translations.columns[1]
        
        df_categories = df_categories.merge(
            df_translations,
            left_on='category',
            right_on=portuguese_col,
            how='left'
        )
        
        # Usar nombres en inglés donde estén disponibles
        df_categories['category'] = df_categories[english_col].fillna(df_categories['category'])

    return df_categories