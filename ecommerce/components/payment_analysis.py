import streamlit as st
import pandas as pd
import plotly.express as px

def show_payment_analysis(conn):
    """
    Muestra el análisis de métodos de pago
    """
    st.header("💳 Análisis de Métodos de Pago")
    
    query = """
    SELECT
        op.payment_type as metodo_pago,
        COUNT(*) as total_transacciones,
        SUM(op.payment_value) as valor_total,
        AVG(op.payment_value) as valor_promedio,
        COUNT(DISTINCT op.order_id) as pedidos_unicos
    FROM order_payments op
    JOIN orders o ON op.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY op.payment_type
    ORDER BY valor_total DESC
    """
    
    df_pagos = pd.read_sql_query(query, conn)
    
    # Mostrar resumen rápido
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Métodos de Pago", len(df_pagos))
    
    with col2:
        total_transacciones = df_pagos['total_transacciones'].sum()
        st.metric("Total Transacciones", f"{total_transacciones:,}")
    
    with col3:
        valor_total = df_pagos['valor_total'].sum()
        st.metric("Valor Total", f"${valor_total:,.2f}")
    
    # Visualizaciones
    tab1, tab2, tab3, tab4 = st.tabs(["Distribución", "Transacciones", 
                                     "Valor Promedio", "Datos Crudos"])
    
    with tab1:
        fig_torta = px.pie(
            df_pagos,
            values='valor_total',
            names='metodo_pago',
            title='Distribución por Valor Total'
        )
        st.plotly_chart(fig_torta, use_container_width=True)
    
    with tab2:
        fig_barras = px.bar(
            df_pagos,
            x='metodo_pago',
            y='total_transacciones',
            title='Total de Transacciones por Método de Pago',
            color='total_transacciones'
        )
        st.plotly_chart(fig_barras, use_container_width=True)
    
    with tab3:
        fig_valor = px.bar(
            df_pagos,
            x='metodo_pago',
            y='valor_promedio',
            title='Valor Promedio por Transacción',
            color='valor_promedio'
        )
        st.plotly_chart(fig_valor, use_container_width=True)
    
    with tab4:
        st.dataframe(df_pagos, use_container_width=True)