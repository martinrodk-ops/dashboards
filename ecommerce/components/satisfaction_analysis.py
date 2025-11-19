"""
Customer Satisfaction Analysis Component with Viridis Theme - CORREGIDO
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.helpers import apply_viridis_style, get_viridis_color, format_currency, format_number

def show_satisfaction_analysis(conn):
    st.header("😊 Customer Satisfaction Analysis")
    
    # Load satisfaction data
    df_satisfaction = get_satisfaction_data(conn)
    
    if df_satisfaction.empty:
        st.warning("No satisfaction data found.")
        return
    
    # Quick metrics - CORREGIDO: cálculo correcto del promedio
    col1, col2, col3 = st.columns(3)
    with col1:
        # CORRECCIÓN: Calcular promedio ponderado por cantidad de reviews
        total_reviews = df_satisfaction['total_reviews'].sum()
        weighted_sum = (df_satisfaction['review_score'] * df_satisfaction['total_reviews']).sum()
        avg_score = weighted_sum / total_reviews if total_reviews > 0 else 0
        formatted_avg = f"{avg_score:.1f}"
        st.metric("⭐ Average Review Score", formatted_avg)
    
    with col2:
        st.metric("📝 Total Reviews", f"{total_reviews:,}")
    
    with col3:
        most_common_score = df_satisfaction.loc[df_satisfaction['total_reviews'].idxmax(), 'review_score']
        st.metric("🎯 Most Common Score", str(most_common_score))
    
    st.markdown("---")
    
    # CONFIGURACIÓN DE SUBPLOTS CON ESPACIADO OPTIMIZADO
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Distribution of Review Scores', 
            'Average Price vs Review Score',
            'Average Shipping Cost vs Review Score', 
            'Average Shipping Cost vs Price by Review Score'
        ),
        specs=[
            [{"type": "bar"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "scatter"}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.10,
        row_heights=[0.5, 0.5]
    )
    
    # Viridis colors for review scores
    n_scores = len(df_satisfaction)
    colors = [get_viridis_color(i, n_scores) for i in range(n_scores)]
    
    # Chart 1: Distribution of Review Scores (Bar)
    fig.add_trace(
        go.Bar(
            x=df_satisfaction['review_score'],
            y=df_satisfaction['total_reviews'],
            marker_color=colors,
            marker_line=dict(color='#E0E0E0', width=1),
            hovertemplate='<b>Review Score: %{x}</b><br>Total Reviews: %{y:,}<extra></extra>',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Chart 2: Average Price vs Review Score
    fig.add_trace(
        go.Scatter(
            x=df_satisfaction['review_score'],
            y=df_satisfaction['average_order_price'],
            mode='lines+markers',
            line=dict(color=px.colors.sequential.Viridis[0], width=3),
            marker=dict(size=8, line=dict(color='#E0E0E0', width=1)),
            hovertemplate='<b>Review Score: %{x}</b><br>Average Price: $%{customdata:.1f}<extra></extra>',
            customdata=df_satisfaction['average_order_price'],
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Chart 3: Average Shipping Cost vs Review Score
    fig.add_trace(
        go.Scatter(
            x=df_satisfaction['review_score'],
            y=df_satisfaction['average_shipping_cost'],
            mode='lines+markers',
            line=dict(color=px.colors.sequential.Viridis[2], width=3),
            marker=dict(size=8, line=dict(color='#E0E0E0', width=1)),
            hovertemplate='<b>Review Score: %{x}</b><br>Average Shipping Cost: $%{customdata:.1f}<extra></extra>',
            customdata=df_satisfaction['average_shipping_cost'],
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Chart 4: Price vs Shipping Cost by Review Score
    fig.add_trace(
        go.Scatter(
            x=df_satisfaction['average_order_price'],
            y=df_satisfaction['average_shipping_cost'],
            mode='markers',
            marker=dict(
                size=df_satisfaction['review_score'] * 8 + 10,
                color=df_satisfaction['review_score'],
                colorscale='Viridis',
                line=dict(color='#E0E0E0', width=1),
                showscale=True,
                colorbar=dict(title="Review Score")
            ),
            text=df_satisfaction['review_score'],
            hovertemplate='<b>Review Score: %{text}</b><br>Average Price: $%{customdata[0]:.1f}<br>Average Shipping Cost: $%{customdata[1]:.1f}<extra></extra>',
            customdata=df_satisfaction[['average_order_price', 'average_shipping_cost']],
            showlegend=False
        ),
        row=2, col=2
    )
    
    # LAYOUT MEJORADO
    fig.update_layout(
        height=800,
        showlegend=False,
        title={
            'text': "Customer Satisfaction Analysis",
            'x': 0.5,
            'y': 0.999,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20, 'color': '#440154', 'family': "Segoe UI, sans-serif"}
        },
        margin=dict(t=100, b=60, l=60, r=60, pad=10)
    )
    
    # Aplicar estilo Viridis base
    fig = apply_viridis_style(fig)
    
    # Update axes
    fig.update_xaxes(title_text="Review Score", row=1, col=1)
    fig.update_yaxes(title_text="Total Reviews", row=1, col=1)
    fig.update_xaxes(title_text="Review Score", row=1, col=2)
    fig.update_yaxes(title_text="Average Price ($)", row=1, col=2)
    fig.update_xaxes(title_text="Review Score", row=2, col=1)
    fig.update_yaxes(title_text="Average Shipping Cost ($)", row=2, col=1)
    fig.update_xaxes(title_text="Average Price ($)", row=2, col=2)
    fig.update_yaxes(title_text="Average Shipping Cost ($)", row=2, col=2)
    
    # CONFIGURACIÓN DE TÍTULOS DE SUBPLOTS - MEJORADA
    for i, annotation in enumerate(fig.layout.annotations):
        col_pos = 0.23 if i % 2 == 0 else 0.78
        row_pos = 1.045 if i < 2 else 0.475
        
        annotation.update(
            text=annotation.text,
            x=col_pos,
            y=row_pos,
            xanchor='center',
            yanchor='top',
            font=dict(size=14, color="#440154", family="Segoe UI, sans-serif"),
            xref='paper',
            yref='paper'
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ESPACIADO ENTRE SECCIONES
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    
    # GRÁFICOS INDIVIDUALES UNO DEBAJO DEL OTRO, OCUPANDO TODO EL ANCHO
    
    # Sección 1: Satisfaction by State (ocupa todo el ancho)
    st.subheader("🏢 Satisfaction by State")
    
    df_satisfaction_state = get_satisfaction_by_state(conn)
    
    if not df_satisfaction_state.empty:
        state_fig = px.bar(
            df_satisfaction_state, 
            x='state', 
            y='average_review_score',
            color='average_review_score',
            color_continuous_scale='Viridis',
            labels={'average_review_score': 'Average Score', 'state': 'State'}
        )
        
        # Aplicar estilo manualmente SIN usar apply_viridis_style
        state_fig.update_layout(
            height=250,  # Altura ajustada a 250
            margin=dict(t=30, b=60, l=60, r=30),
            showlegend=False,
            xaxis_title="State",
            yaxis_title="Average Review Score",  # Etiqueta del eje Y agregada
            font=dict(size=10),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        state_fig.update_traces(
            hovertemplate='<b>State: %{x}</b><br>Average Score: %{customdata:.1f}<extra></extra>',
            customdata=df_satisfaction_state['average_review_score']
        )
        state_fig.update_xaxes(
            tickangle=45, 
            tickfont=dict(size=9),
            gridcolor='rgba(128,128,128,0.2)'
        )
        state_fig.update_yaxes(
            tickfont=dict(size=9),
            gridcolor='rgba(128,128,128,0.2)'
        )
        st.plotly_chart(state_fig, use_container_width=True)
    
    # ESPACIADO ENTRE SECCIONES
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    
    # Sección 2: Satisfaction Over Time (ocupa todo el ancho)
    st.subheader("⏰ Satisfaction Over Time")
    
    df_satisfaction_temporal = get_satisfaction_temporal(conn)
    
    if not df_satisfaction_temporal.empty:
        temporal_fig = px.line(
            df_satisfaction_temporal, 
            x='month', 
            y='average_review_score',
            markers=True, 
            line_shape='linear',
            labels={'average_review_score': 'Average Score', 'month': 'Month'}
        )
        
        # Aplicar estilo manualmente SIN usar apply_viridis_style
        temporal_fig.update_layout(
            height=250,  # Altura ajustada a 250
            margin=dict(t=30, b=70, l=60, r=30),
            showlegend=False,
            xaxis_title="Month",
            yaxis_title="Average Review Score",  # Etiqueta del eje Y agregada
            font=dict(size=10),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        temporal_fig.update_traces(
            hovertemplate='<b>Month: %{x}</b><br>Average Score: %{customdata:.1f}<extra></extra>',
            customdata=df_satisfaction_temporal['average_review_score'],
            line=dict(width=2),
            marker=dict(size=4)
        )
        temporal_fig.update_xaxes(
            tickangle=45, 
            tickfont=dict(size=9),
            gridcolor='rgba(128,128,128,0.2)'
        )
        temporal_fig.update_yaxes(
            tickfont=dict(size=9),
            gridcolor='rgba(128,128,128,0.2)'
        )
        st.plotly_chart(temporal_fig, use_container_width=True)

def get_satisfaction_data(conn):
    """Get customer satisfaction data"""
    query = """
    SELECT
        orr.review_score as review_score,
        COUNT(*) as total_reviews,
        AVG(oi.price) as average_order_price,
        AVG(oi.freight_value) as average_shipping_cost
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
