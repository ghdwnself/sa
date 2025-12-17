import pandas as pd
from datetime import datetime

def load_data():
    """Load and merge sales_total.csv with db_buyer.csv"""
    # Load sales data
    sales = pd.read_csv('data/sales_total.csv')
    
    # Clean revenue column - remove $ and commas
    sales['revenue_clean'] = pd.to_numeric(
        sales['revenue'].astype(str).str.replace('$','', regex=False).str.replace(',','', regex=False),
        errors='coerce'
    ).fillna(0)
    
    # Clean qty column - remove commas
    sales['qty_clean'] = pd.to_numeric(
        sales['qty'].astype(str).str.replace(',','', regex=False),
        errors='coerce'
    ).fillna(0).astype(int)
    
    # Clean price column - remove $ and commas
    sales['price_clean'] = pd.to_numeric(
        sales['price'].astype(str).str.replace('$','', regex=False).str.replace(',','', regex=False),
        errors='coerce'
    ).fillna(0)
    
    # Convert date
    sales['date'] = pd.to_datetime(sales['date'])
    sales['year'] = sales['date'].dt.year
    sales['month'] = sales['date'].dt.month
    sales['quarter'] = sales['date'].dt.quarter
    
    # Load buyer data
    buyers = pd.read_csv('data/db_buyer.csv')
    
    # Merge
    df = sales.merge(buyers, left_on='customer', right_on='Customer', how='left')
    
    # Fill missing types
    df['Type'] = df['Type'].fillna('Other')
    
    # Subdivide OBD into French Bull and Neoflam
    def classify_obd(row):
        if row['Type'] == 'OBD':
            customer_lower = str(row['customer']).lower()
            if 'french bull' in customer_lower or 'fb' in customer_lower:
                return 'OBD-FB'
            elif 'neoflam' in customer_lower or 'nf' in customer_lower:
                return 'OBD-NF'
            else:
                return 'OBD-Other'
        return row['Type']
    
    df['Type'] = df.apply(classify_obd, axis=1)
    
    # Filter out non-numeric SKUs (like "Discount", "Other Income", etc.)
    df['sku_str'] = df['sku'].astype(str)
    df = df[df['sku_str'].str.match(r'^\d+', na=False) | df['sku_str'].str.contains('CP$|NT$|NB$', na=False, regex=True)].copy()
    
    # Create item display name: brand shape size
    def create_display_name(row):
        brand = str(row['brand']) if pd.notna(row['brand']) else ''
        shape = str(row['shape']) if pd.notna(row['shape']) else ''
        size = str(row['size_capacity']) if pd.notna(row['size_capacity']) else ''
        
        parts = [p for p in [brand, shape, size] if p and p != 'nan']
        if parts:
            return ' '.join(parts)
        else:
            # If no brand/shape/size, use item name or SKU
            if pd.notna(row['item']) and str(row['item']) != 'nan':
                return str(row['item'])
            else:
                return f"SKU {row['sku']}"
    
    df['item_display'] = df.apply(create_display_name, axis=1)
    
    return df

def calculate_kpis(df, year=2025):
    """Calculate KPI metrics for dashboard"""
    df_year = df[df['year'] == year]
    
    kpis = {
        'total_sales': df_year['revenue_clean'].sum(),
        'mmd_sales': df_year[df_year['Type'] == 'MMD']['revenue_clean'].sum(),
        'fob_sales': df_year[df_year['Type'] == 'DI']['revenue_clean'].sum(),
        'emd_sales': df_year[df_year['Type'] == 'EMD']['revenue_clean'].sum(),
        'obd_sales': df_year[df_year['Type'].str.startswith('OBD', na=False)]['revenue_clean'].sum(),
        'obd_fb_sales': df_year[df_year['Type'] == 'OBD-FB']['revenue_clean'].sum(),
        'obd_nf_sales': df_year[df_year['Type'] == 'OBD-NF']['revenue_clean'].sum()
    }
    
    return kpis

def calculate_yoy_comparison(df):
    """Calculate year-over-year comparison"""
    stats_2024 = {
        'total': df[df['year'] == 2024]['revenue_clean'].sum(),
        'mmd': df[(df['year'] == 2024) & (df['Type'] == 'MMD')]['revenue_clean'].sum(),
        'fob': df[(df['year'] == 2024) & (df['Type'] == 'DI')]['revenue_clean'].sum(),
        'emd': df[(df['year'] == 2024) & (df['Type'] == 'EMD')]['revenue_clean'].sum(),
        'obd': df[(df['year'] == 2024) & (df['Type'].str.startswith('OBD', na=False))]['revenue_clean'].sum(),
        'obd_fb': df[(df['year'] == 2024) & (df['Type'] == 'OBD-FB')]['revenue_clean'].sum(),
        'obd_nf': df[(df['year'] == 2024) & (df['Type'] == 'OBD-NF')]['revenue_clean'].sum(),
    }
    
    stats_2025 = {
        'total': df[df['year'] == 2025]['revenue_clean'].sum(),
        'mmd': df[(df['year'] == 2025) & (df['Type'] == 'MMD')]['revenue_clean'].sum(),
        'fob': df[(df['year'] == 2025) & (df['Type'] == 'DI')]['revenue_clean'].sum(),
        'emd': df[(df['year'] == 2025) & (df['Type'] == 'EMD')]['revenue_clean'].sum(),
        'obd': df[(df['year'] == 2025) & (df['Type'].str.startswith('OBD', na=False))]['revenue_clean'].sum(),
        'obd_fb': df[(df['year'] == 2025) & (df['Type'] == 'OBD-FB')]['revenue_clean'].sum(),
        'obd_nf': df[(df['year'] == 2025) & (df['Type'] == 'OBD-NF')]['revenue_clean'].sum(),
    }
    
    comparison = {}
    for key in stats_2024.keys():
        if stats_2024[key] > 0:
            growth = ((stats_2025[key] - stats_2024[key]) / stats_2024[key]) * 100
        else:
            growth = 0
        comparison[key] = {
            '2024': stats_2024[key],
            '2025': stats_2025[key],
            'growth': growth,
            'diff': stats_2025[key] - stats_2024[key]
        }
    
    return comparison

def get_top_buyers_by_channel(df, year=2025, top_n=5):
    """Get top N buyers for each channel"""
    df_year = df[df['year'] == year]
    
    channels = ['MMD', 'DI', 'EMD', 'OBD-FB', 'OBD-NF']
    top_buyers = {}
    
    for channel in channels:
        channel_data = df_year[df_year['Type'] == channel]
        buyers = channel_data.groupby('customer').agg({
            'revenue_clean': 'sum',
            'qty_clean': 'sum'
        }).reset_index()
        buyers = buyers.sort_values('revenue_clean', ascending=False).head(top_n)
        top_buyers[channel] = buyers
    
    return top_buyers

def get_category_performance(df, year=2025):
    """Get category-wise performance metrics"""
    df_year = df[df['year'] == year]
    
    category_stats = df_year.groupby('category').agg({
        'revenue_clean': 'sum',
        'qty_clean': 'sum',
        'sku': 'nunique'
    }).reset_index()
    
    category_stats.columns = ['category', 'revenue', 'quantity', 'sku_count']
    category_stats = category_stats.sort_values('revenue', ascending=False)
    
    return category_stats

def get_category_yoy_growth(df):
    """Get detailed YoY growth by category"""
    categories = ['Food Storage', 'Smart Seal', 'Cookware']
    
    growth_data = []
    
    for category in categories:
        cat_2024 = df[(df['year'] == 2024) & (df['category'] == category)]
        cat_2025 = df[(df['year'] == 2025) & (df['category'] == category)]
        
        revenue_2024 = cat_2024['revenue_clean'].sum()
        revenue_2025 = cat_2025['revenue_clean'].sum()
        
        qty_2024 = cat_2024['qty_clean'].sum()
        qty_2025 = cat_2025['qty_clean'].sum()
        
        revenue_growth = ((revenue_2025 - revenue_2024) / revenue_2024 * 100) if revenue_2024 > 0 else 0
        qty_growth = ((qty_2025 - qty_2024) / qty_2024 * 100) if qty_2024 > 0 else 0
        
        # Get top items
        top_items_2025 = cat_2025.groupby('item_display').agg({
            'revenue_clean': 'sum',
            'qty_clean': 'sum'
        }).reset_index().sort_values('revenue_clean', ascending=False).head(5)
        
        growth_data.append({
            'category': category,
            'revenue_2024': revenue_2024,
            'revenue_2025': revenue_2025,
            'revenue_growth': revenue_growth,
            'qty_2024': qty_2024,
            'qty_2025': qty_2025,
            'qty_growth': qty_growth,
            'top_items': top_items_2025
        })
    
    return growth_data

def get_channel_category_breakdown(df, year=2025):
    """Get revenue breakdown by channel and category"""
    df_year = df[df['year'] == year]
    
    breakdown = df_year.groupby(['Type', 'category']).agg({
        'revenue_clean': 'sum',
        'qty_clean': 'sum'
    }).reset_index()
    
    breakdown = breakdown.sort_values(['Type', 'revenue_clean'], ascending=[True, False])
    
    return breakdown
