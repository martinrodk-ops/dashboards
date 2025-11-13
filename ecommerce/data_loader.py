import sqlite3
import pandas as pd
import streamlit as st
from config.gdrive_config import get_file_urls

class DataLoader:
    def __init__(self, db_name='ecommerce.db'):
        self.db_name = db_name
        self.file_urls = get_file_urls()

    @st.cache_resource
    def load_database(_self):
        """Cargar todos los datos desde Google Drive a SQLite"""
        conn = sqlite3.connect(_self.db_name)
        
        st.info("📥 Iniciando carga de datos desde Google Drive...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_files = len(_self.file_urls)
        
        for i, (table_name, url) in enumerate(_self.file_urls.items()):
            try:
                status_text.text(f"📋 Cargando {table_name}...")
                
                # Descargar y cargar CSV
                df = pd.read_csv(url)
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                
                progress_bar.progress((i + 1) / total_files)
                
            except Exception as e:
                st.error(f"❌ Error cargando {table_name}: {str(e)}")
                continue
        
        conn.close()  # ¡Importante: cerrar la conexión!
        status_text.text("✅ ¡Base de datos cargada exitosamente!")

    def get_db_path(self):
        return self.db_name

    def create_connection(self):
        """Crear una nueva conexión para el thread actual"""
        return sqlite3.connect(self.db_name)

# Instancia global del cargador de datos
data_loader = DataLoader()
