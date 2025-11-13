"""
Google Drive configuration for CSV files
Replace with your actual file IDs
"""

# Dictionary with file IDs from Google Drive
CSV_FILE_IDS = {
    'customers': '1DKdBDiYZt1lW5PqU-V8dmD8OCz5SQ1qb',
    'orders': '1O_yhdmftIVi0rcOe2bpE8Q_zbK-B3ksp',
    'order_items': '1Awoq9fV3uIRpVlsYg85WAkxHR7J4nfgK',
    'order_payments': '1A9Ae4C1-4eySrvvWM_XTh78Zq_lDCtlj',
    'products': '1twXjiKDF-UMVc6D29mvCNux-ggRys2aD',
    'sellers': '1i_XbP5Zihdvylp-sbdtPufq13lz4elP8',
    'geolocation': '1snjgYLRUDYVdYAByuKVltex9SZvQd11o',
    'order_reviews': '15PfwofcRz2kQGuTSZvajOfL605nWmroN',
    'category_translations': '1X_437Ajwkcy2PmQnkDNvCjWL4ycv7XMN'
}

def get_direct_download_url(file_id):
    """Generate direct download URL from Google Drive"""
    return f"https://drive.google.com/uc?export=download&id={file_id}"

def get_file_urls():
    """Return dictionary with complete URLs for each file"""
    return {name: get_direct_download_url(file_id) 
            for name, file_id in CSV_FILE_IDS.items()}