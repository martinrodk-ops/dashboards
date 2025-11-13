"""
Helper functions for the dashboard
"""
import plotly.graph_objects as go
import pandas as pd

def apply_custom_style(fig, title, height=500, width=None):
    """Apply consistent style to all charts"""
    fig.update_layout(
        height=height,
        width=width,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color="black"),
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=16)),
        showlegend=True,
        margin=dict(t=60, b=50, l=50, r=50),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    
    fig.update_xaxes(
        showline=True, linewidth=2, linecolor='darkgray',
        gridcolor='lightgray', griddash='dash', mirror=True,
        title_font=dict(size=12)
    )
    
    fig.update_yaxes(
        showline=True, linewidth=2, linecolor='darkgray',
        gridcolor='lightgray', griddash='dash', mirror=True,
        title_font=dict(size=12)
    )
    
    return fig

def format_currency(value):
    """Format values as currency"""
    if pd.isna(value) or value is None:
        return "N/A"
    return f"${value:,.2f}"

def format_number(value):
    """Format numbers with thousand separators"""
    if pd.isna(value) or value is None:
        return "N/A"
    return f"{value:,.0f}"

def create_metric_card(value, title, delta=None, delta_color="normal"):
    """Create a styled metric card"""
    if delta is not None:
        return {
            "value": value,
            "title": title,
            "delta": delta,
            "delta_color": delta_color
        }
    else:
        return {
            "value": value,
            "title": title
        }

def calculate_growth(current, previous):
    """Calculate percentage growth"""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100