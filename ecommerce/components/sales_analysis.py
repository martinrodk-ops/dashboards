"""
Sales Analysis by State Component with Viridis Theme
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.helpers import apply_viridis_style, get_viridis_color, format_currency, format_number

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
    
    # Create subplots with professional layout
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Total Revenue by State', 
            'Total Orders by State',
            'Revenue Distribution by State', 
            'Average Price Distribution'
        ),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "pie"}, {"type": "box"}]
        ],
        vertical_spacing=0.2,  # Increased vertical spacing
        horizontal_spacing=0.1  # Increased horizontal spacing
    )
    
    # Viridis color scale for states
    n_states = len(df_sales)
    colors = [get_viridis_color(i, n_states) for i in range(n_states)]
    
    # Chart 1: Total Revenue by State
    fig.add_trace(
        go.Bar(
            x=df_sales['state'], 
            y=df_sales['total_revenue'],
            name='Total Revenue',
            marker_color=colors,
            marker_line=dict(color='#E0E0E0', width=1),
            hovertemplate='<b>%{x}</b><br>Total Revenue: $%{y:,.2f}<extra></extra>',  # Changed to 2 decimal places
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Chart 2: Total Orders by State
    fig.add_trace(
        go.Bar(
            x=df_sales['state'], 
            y=df_sales['total_orders'],
            name='Total Orders',
            marker_color=colors,
            marker_line=dict(color='#E0E0E0', width=1),
            hovertemplate='<b>%{x}</b><br>Total Orders: %{y:,.0f}<extra></extra>',  # Changed to 0 decimal places for orders
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Chart 3: Revenue Distribution by State (Pie)
    total_revenue = df_sales['total_revenue'].sum()
    percentages = (df_sales['total_revenue'] / total_revenue) * 100
    
    # CORRECCIÓN: Cambiar el umbral a 3.7% para mostrar etiquetas
    custom_labels = [
        f"{state}<br>{percentage:.1f}%" if percentage >= 3.7 else ""
        for state, percentage in zip(df_sales['state'], percentages)
    ]
    
    fig.add_trace(
        go.Pie(
            labels=df_sales['state'],
            values=df_sales['total_revenue'],
            name='Revenue Distribution',
            text=custom_labels,
            textinfo='text',
            marker=dict(colors=colors, line=dict(color='#E0E0E0', width=1)),
            # CORRECCIÓN: Usar los porcentajes calculados manualmente en el hovertemplate
            hovertemplate='<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>Percentage: %{customdata:.2f}%<extra></extra>',
            customdata=percentages,  # Agregar los porcentajes calculados como customdata
            showlegend=False,
            # Asegurar que las porciones pequeñas tengan línea y etiqueta solo si >= 3.7%
            textposition='inside',
            insidetextorientation='radial'
        ),
        row=2, col=1
    )
    
    # Chart 4: Average Price by State (Box plot)
    # CORRECCIÓN: Usar colores coherentes de la paleta viridis
    viridis_color = get_viridis_color(1, 14)
    viridis_fillcolor = get_viridis_color(3, 14)  # Color más claro de la misma paleta
    
    fig.add_trace(
        go.Box(
            y=df_sales['average_price'],
            name='Average Price',
            marker_color=viridis_color,
            line=dict(color=viridis_color, width=2),
            fillcolor=viridis_fillcolor,  # Color coherente con la paleta viridis
            # CORRECCIÓN: Asegurar 2 decimales en el hovertemplate
            hovertemplate='<b>Average Price</b><br>Min: $%{y.min:.2f}<br>Q1: $%{y.q1:.2f}<br>Median: $%{y.median:.2f}<br>Q3: $%{y.q3:.2f}<br>Max: $%{y.max:.2f}<extra></extra>',
            showlegend=False
        ),
        row=2, col=2
    )
    
    # Update layout with Viridis style
    fig = apply_viridis_style(fig, "Sales Analysis by State", height=900)
    
    # Update axes
    fig.update_xaxes(title_text="State", row=1, col=1, tickangle=45)
    fig.update_yaxes(title_text="Total Revenue ($)", row=1, col=1)
    fig.update_xaxes(title_text="State", row=1, col=2, tickangle=45)
    fig.update_yaxes(title_text="Total Orders", row=1, col=2)
    
    # Hide x-axis labels for box plot
    fig.update_xaxes(
        showticklabels=False,
        showline=True,
        linewidth=2,
        linecolor='#E0E0E0',
        mirror=True,
        ticks="",
        row=2, col=2
    )
    fig.update_yaxes(title_text="Average Price ($)", row=2, col=2)
    
    # Update subplot titles with better spacing
    for annotation in fig.layout.annotations:
        annotation.update(
            font=dict(size=14, color="#440154", family="Segoe UI, sans-serif"),
            y=annotation.y + 0.02  # Add spacing between subplot title and chart
        )
    
    # Additional layout adjustments for better spacing - MOVING TITLE HIGHER
    fig.update_layout(
        margin=dict(t=150, b=50, l=50, r=50),  # Increased top margin from 100 to 150
        title_y=0.98,  # Position title higher (closer to 1.0 means closer to top)
        title_x=0.5,   # Center the title
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Additional scatter plot
    st.subheader("📈 Relationship: Orders vs Average Price")
    
    scatter_fig = px.scatter(
        df_sales, 
        x='total_orders', 
        y='average_price',
        size='total_revenue', 
        color='state',
        hover_name='state',
        log_x=True,
        color_discrete_sequence=px.colors.sequential.Viridis,
        labels={
            'total_orders': 'Total Orders', 
            'average_price': 'Average Price ($)',
            'state': 'State'
        }
    )
    
    # Update hovertemplate for scatter plot to show 2 decimal places
    scatter_fig.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>Total Orders: %{x:,.0f}<br>Average Price: $%{y:.2f}<br>Total Revenue: $%{marker.size:,.2f}<extra></extra>'
    )
    
    scatter_fig = apply_viridis_style(scatter_fig, "Orders vs Average Price by State")
    st.plotly_chart(scatter_fig, use_container_width=True)
    
    # ELIMINADO: Sección "Detailed Data by State" y su tabla
    # Esta sección ha sido removida por solicitud del usuario

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