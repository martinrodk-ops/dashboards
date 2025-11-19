"""
Module for loading and managing data from Google Drive to SQLite - CORREGIDO
"""
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
        """Load all data to SQLite - CORREGIDO con mejor manejo de errores"""
        conn = sqlite3.connect(_self.db_name)
        
        st.info("📥 Loading datasets...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_files = len(_self.file_urls)
        loaded_tables = []
        failed_tables = []
        
        for i, (table_name, url) in enumerate(_self.file_urls.items()):
            try:
                status_text.text(f"📋 Loading {table_name}...")
                
                # Download and load CSV
                df = pd.read_csv(url)
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                loaded_tables.append(table_name)
                
                progress_bar.progress((i + 1) / total_files)
                
            except Exception as e:
                st.error(f"❌ Error loading {table_name}: {str(e)}")
                failed_tables.append(table_name)
                continue
        
        conn.close()
        
        # Mostrar resumen de carga
        if loaded_tables:
            st.success(f"✅ Successfully loaded {len(loaded_tables)} tables")
        if failed_tables:
            st.warning(f"⚠️ Failed to load {len(failed_tables)} tables: {', '.join(failed_tables)}")
        
        status_text.text("✅ Database loading completed!")

    def get_db_path(self):
        return self.db_name

    def create_connection(self):
        """Create a new connection for the current thread"""
        return sqlite3.connect(self.db_name)

# Global instance of the data loader
data_loader = DataLoader()