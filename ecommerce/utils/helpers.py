"""
Helper functions for the dashboard with Viridis Theme - CORREGIDO
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Viridis color scale
VIRIDIS_COLORS = px.colors.sequential.Viridis
VIRIDIS_COLORS_R = px.colors.sequential.Viridis_r

def apply_viridis_style(fig, title=None, height=1000, width=None):
    """Apply consistent Viridis style to all charts - CORREGIDO"""
    layout_updates = {
        'height': height,
        'width': width,
        'paper_bgcolor': 'white',
        'plot_bgcolor': 'white',
        'font': dict(family="Segoe UI, Arial, sans-serif", size=13, color="#2C3E50"),
        'showlegend': True,
        'margin': dict(t=80, b=80, l=80, r=80),  # Margen reducido para mejor posicionamiento
        'hoverlabel': dict(
            bgcolor="#440154",
            font_size=12,
            font_family="Segoe UI, sans-serif",
            font_color="white"
        )
    }
    
    # CORRECCIÓN: Solo agregar título si se proporciona y con formato centrado
    if title:
        layout_updates['title'] = {
            'text': title, 
            'x': 0.5, 
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20, color="#440154", family="Segoe UI, sans-serif"),
            'y': 0.95
        }
    
    fig.update_layout(**layout_updates)
    
    fig.update_xaxes(
        showline=True, 
        linewidth=2, 
        linecolor='#E0E0E0',
        gridcolor='#F5F5F5', 
        griddash='dot',
        mirror=True,
        title_font=dict(size=12, color="#2C3E50"),
        tickfont=dict(size=11, color="#2C3E50")
    )
    
    fig.update_yaxes(
        showline=True, 
        linewidth=2, 
        linecolor='#E0E0E0',
        gridcolor='#F5F5F5', 
        griddash='dot',
        mirror=True,
        title_font=dict(size=12, color="#2C3E50"),
        tickfont=dict(size=11, color="#2C3E50")
    )
    
    return fig

def get_viridis_color(index, total_items):
    """Get Viridis color based on index - CORREGIDO manejo de división por cero"""
    if total_items <= 1:
        return VIRIDIS_COLORS[5]
    if total_items == 0:
        return VIRIDIS_COLORS[0]
    return VIRIDIS_COLORS[int(index / (total_items - 1) * (len(VIRIDIS_COLORS) - 1))]

def format_currency(value):
    """Format values as currency - CORREGIDO formato decimal"""
    if pd.isna(value) or value is None:
        return "$0.00"
    try:
        value = float(value)
        if value == int(value):
            return f"${int(value):,}"
        else:
            return f"${value:,.2f}"
    except (ValueError, TypeError):
        return f"${value}"

def format_number(value):
    """Format numbers with proper decimal places - CORREGIDO"""
    if pd.isna(value) or value is None:
        return "0"
    try:
        value = float(value)
        if value == int(value):
            return f"{int(value):,}"
        else:
            return f"{value:,.1f}"
    except (ValueError, TypeError):
        return str(value)

def format_integer(value):
    """Format numbers as integers - CORREGIDO"""
    if pd.isna(value) or value is None:
        return "0"
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return str(value)