"""
Module for loading and managing data from Google Drive to SQLite
"""
import sqlite3
import pandas as pd
import streamlit as st
from config.gdrive_config import get_file_urls

class DataLoader:
    def __init__(self, db_name='ecommerce.db'):
        self.db_name = db_name
        self.file_urls = get_file_urls()
        self.conn = None
    
    @st.cache_resource
    def load_database(_self):
        """Load all data from Google Drive to SQLite"""
        _self.conn = sqlite3.connect(_self.db_name)
        
        st.info("📥 Starting data load from Google Drive...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_files = len(_self.file_urls)
        
        for i, (table_name, url) in enumerate(_self.file_urls.items()):
            try:
                status_text.text(f"📋 Loading {table_name}...")
                
                # Download and load CSV
                df = pd.read_csv(url)
                df.to_sql(table_name, _self.conn, if_exists='replace', index=False)
                
                progress_bar.progress((i + 1) / total_files)
                
            except Exception as e:
                st.error(f"❌ Error loading {table_name}: {str(e)}")
                continue
        
        status_text.text("✅ Database loaded successfully!")
        return _self.conn
    
    def get_connection(self):
        """Return database connection"""
        if self.conn is None:
            self.conn = self.load_database()
        return self.conn
    
    def get_table_info(self):
        """Get information about tables in the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        table_info = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            table_info[table_name] = [(col[1], col[2]) for col in columns]
        
        return table_info

# Global instance of the data loader
data_loader = DataLoader()
