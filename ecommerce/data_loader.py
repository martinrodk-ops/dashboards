import sqlite3
import pandas as pd
import streamlit as st
from pathlib import Path

@st.cache_data
def load_csv_to_sqlite(csv_files):
    """
    Carga archivos CSV a una base de datos SQLite en memoria
    con caching para mejor rendimiento
    """
    conn = sqlite3.connect(':memory:')
    
    for table_name, file_path in csv_files.items():
        try:
            df = pd.read_csv(file_path)
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            st.success(f"✅ Tabla {table_name} cargada exitosamente")
        except FileNotFoundError:
            st.error(f"❌ Archivo {file_path} no encontrado")
        except Exception as e:
            st.error(f"❌ Error cargando {table_name}: {str(e)}")
    
    return conn

def get_database_connection():
    """
    Retorna la conexión a la base de datos con los datos cargados
    """
    # Define las rutas de tus archivos CSV
    csv_files = {
        'customers': 'brazil_e_commerce/olist_customers_dataset.csv',
        'orders': 'brazil_e_commerce/olist_orders_dataset.csv',
        'order_items': 'brazil_e_commerce/olist_order_items_dataset.csv',
        'order_payments': 'brazil_e_commerce/olist_order_payments_dataset.csv',
        'products': 'brazil_e_commerce/olist_products_dataset.csv',
        'sellers': 'brazil_e_commerce/olist_sellers_dataset.csv',
        'geolocation': 'brazil_e_commerce/olist_geolocation_dataset.csv',
        'order_reviews': 'brazil_e_commerce/olist_order_reviews_dataset.csv'
    }
    
    return load_csv_to_sqlite(csv_files)