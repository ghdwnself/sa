"""
Data Loading and Transformation Module
Handles all ETL operations for the Executive Sales Dashboard
"""

import pandas as pd
import streamlit as st
from pathlib import Path


@st.cache_data
def load_sales_data():
    """
    Load and preprocess sales data
    - Convert Customer to UPPERCASE
    - Parse Date to datetime
    - Filter for Years 2024 & 2025
    """
    df = pd.read_csv('data/sales_data.csv')
    df['Customer'] = df['Customer'].str.upper()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    # Filter for 2024 and 2025 only
    df = df[df['Year'].isin([2024, 2025])].copy()
    return df


@st.cache_data
def load_item_master():
    """
    Load item master data
    CRITICAL: Use skiprows=[0] as Row 0 is description, Row 1 is header
    """
    df = pd.read_csv('data/item_master.csv', skiprows=[0])
    return df


@st.cache_data
def load_tjx_items():
    """
    Load list of on-going (active) TJX items
    """
    df = pd.read_csv('data/tjx_item.csv')
    return df['SKU'].tolist()


@st.cache_data
def load_buyer_db():
    """
    Load buyer database
    - Convert Customer to UPPERCASE before joining
    """
    df = pd.read_csv('data/db_buyer.csv')
    df['Customer'] = df['Customer'].str.upper()
    return df


def map_channel(type_value):
    """
    Map Type to Channel
    - MMD -> 'TJX Group'
    - DI -> 'Direct Import'
    - EMD -> 'EMD/Local'
    - OBD -> 'Online Direct'
    - CS -> DROP (Internal Sales)
    - NaN -> 'EMD/Local' (CRITICAL: Unmatched customers default to EMD/Local)
    """
    if pd.isna(type_value):
        return 'EMD/Local'
    
    mapping = {
        'MMD': 'TJX Group',
        'DI': 'Direct Import',
        'EMD': 'EMD/Local',
        'OBD': 'Online Direct',
        'CS': None  # Will be dropped
    }
    return mapping.get(type_value, 'EMD/Local')


def categorize_product(category_str):
    """
    Map raw categories to 8 Groups using keyword matching
    - Food Storage
    - Smart Seal
    - Cookware
    - Cutting Board
    - Canister
    - Tableware
    - Kitchen Tool
    - Others
    """
    if pd.isna(category_str):
        return 'Others'
    
    category_lower = category_str.lower()
    
    if 'smart seal' in category_lower:
        return 'Smart Seal'
    elif 'food storage' in category_lower:
        return 'Food Storage'
    elif 'cookware' in category_lower or 'pan' in category_lower or 'pot' in category_lower:
        return 'Cookware'
    elif 'cutting board' in category_lower:
        return 'Cutting Board'
    elif 'canister' in category_lower:
        return 'Canister'
    elif 'tableware' in category_lower:
        return 'Tableware'
    elif 'kitchen tool' in category_lower or 'peeler' in category_lower:
        return 'Kitchen Tool'
    else:
        return 'Others'


def identify_tjx_buyer(customer):
    """
    Identify TJX buyer segment
    Keywords: HOMEGOODS, MARSHALLS, TJ MAXX, WINNERS, HOMESENSE
    EXCLUDE: BURLINGTON
    """
    if pd.isna(customer):
        return None
    
    customer_upper = customer.upper()
    
    if 'BURLINGTON' in customer_upper:
        return None
    elif 'HOMEGOODS' in customer_upper or 'HOME GOODS' in customer_upper:
        return 'HomeGoods'
    elif 'MARSHALLS' in customer_upper:
        return 'Marshalls'
    elif 'TJ MAXX' in customer_upper or 'TJMAXX' in customer_upper:
        return 'TJ Maxx'
    elif 'WINNERS' in customer_upper:
        return 'Winners'
    elif 'HOMESENSE' in customer_upper or 'HOME SENSE' in customer_upper:
        return 'HomeSense'
    else:
        return None


@st.cache_data
def process_data():
    """
    Main ETL pipeline
    Returns fully processed dataframe with all transformations applied
    """
    # Load all data sources
    sales_df = load_sales_data()
    item_master_df = load_item_master()
    tjx_items = load_tjx_items()
    buyer_db = load_buyer_db()
    
    # Join with item master
    df = sales_df.merge(item_master_df, on='SKU', how='left')
    
    # Join with buyer database to get Type
    df = df.merge(buyer_db, on='Customer', how='left')
    
    # Map Type to Channel
    df['Channel'] = df['Type'].apply(map_channel)
    
    # Drop CS (Internal Sales)
    df = df[df['Channel'].notna()].copy()
    
    # Categorize products
    df['Category_Group'] = df['Category'].apply(categorize_product)
    
    # Identify TJX buyers (excluding Burlington)
    df['TJX_Buyer'] = df['Customer'].apply(identify_tjx_buyer)
    
    # Tag active/on-going items
    df['Is_Active_TJX'] = df['SKU'].isin(tjx_items)
    
    return df


@st.cache_data
def get_yoy_comparison(df):
    """
    Calculate Year-over-Year comparison
    Returns aggregated data by year
    """
    yoy_data = df.groupby('Year').agg({
        'Sales': 'sum',
        'Quantity': 'sum'
    }).reset_index()
    return yoy_data


@st.cache_data
def get_channel_data(df):
    """
    Get sales by channel and year
    """
    channel_data = df.groupby(['Channel', 'Year']).agg({
        'Sales': 'sum'
    }).reset_index()
    return channel_data


@st.cache_data
def get_category_data(df):
    """
    Get sales by category group
    """
    category_data = df.groupby(['Category_Group', 'Year']).agg({
        'Sales': 'sum',
        'Quantity': 'sum'
    }).reset_index()
    return category_data


@st.cache_data
def get_tjx_buyer_breakdown(df):
    """
    Get TJX buyer breakdown with top categories
    """
    tjx_df = df[df['TJX_Buyer'].notna()].copy()
    
    buyer_data = {}
    for buyer in ['HomeGoods', 'Marshalls', 'TJ Maxx', 'Winners', 'HomeSense']:
        buyer_df = tjx_df[tjx_df['TJX_Buyer'] == buyer]
        if len(buyer_df) > 0:
            top_cats = buyer_df.groupby('Category_Group')['Sales'].sum().sort_values(ascending=False).head(3)
            buyer_data[buyer] = top_cats
        else:
            buyer_data[buyer] = pd.Series()
    
    return buyer_data


@st.cache_data
def get_food_storage_analysis(df):
    """
    Get Food Storage analysis for TJX
    Returns sales by Brand and by Shape/Size
    """
    fs_df = df[(df['Category_Group'] == 'Food Storage') & (df['Channel'] == 'TJX Group')].copy()
    
    # By Brand
    brand_data = fs_df.groupby(['Brand', 'Year'])['Sales'].sum().reset_index()
    
    # By Shape and Size
    shape_size_data = fs_df.groupby(['Shape', 'Size_Capacity', 'Year'])['Sales'].sum().reset_index()
    
    return brand_data, shape_size_data


@st.cache_data
def get_sku_performance(df):
    """
    Get SKU performance - Top 5 Growing vs Top 5 Declining
    Includes active item indicator
    """
    # Calculate YoY change by SKU
    sku_data = df.groupby(['SKU', 'Year', 'Is_Active_TJX'])['Sales'].sum().reset_index()
    
    # Pivot to get 2024 and 2025 columns
    sku_pivot = sku_data.pivot_table(
        index=['SKU', 'Is_Active_TJX'], 
        columns='Year', 
        values='Sales', 
        fill_value=0
    ).reset_index()
    
    if 2024 in sku_pivot.columns and 2025 in sku_pivot.columns:
        sku_pivot['Growth_Pct'] = ((sku_pivot[2025] - sku_pivot[2024]) / sku_pivot[2024] * 100).round(1)
        sku_pivot = sku_pivot[sku_pivot[2024] > 0]  # Only items with 2024 sales
        
        # Top 5 Growing
        top_growing = sku_pivot.nlargest(5, 'Growth_Pct')
        
        # Top 5 Declining
        top_declining = sku_pivot.nsmallest(5, 'Growth_Pct')
        
        return top_growing, top_declining
    
    return pd.DataFrame(), pd.DataFrame()


@st.cache_data
def get_emd_customers(df):
    """
    Get top 10 EMD/Local customers
    """
    emd_df = df[df['Channel'] == 'EMD/Local'].copy()
    
    customer_sales = emd_df.groupby('Customer')['Sales'].sum().sort_values(ascending=False).head(10)
    total_emd = emd_df['Sales'].sum()
    
    result = pd.DataFrame({
        'Customer': customer_sales.index,
        'Revenue': customer_sales.values,
        'Share_Pct': (customer_sales.values / total_emd * 100).round(1)
    })
    
    return result


@st.cache_data
def get_churn_analysis(df):
    """
    Analyze customer churn
    - New: Customers active in 2025 ONLY
    - Churned: Customers active in 2024 but ZERO in 2025
    """
    customers_2024 = set(df[df['Year'] == 2024]['Customer'].unique())
    customers_2025 = set(df[df['Year'] == 2025]['Customer'].unique())
    
    new_customers = customers_2025 - customers_2024
    churned_customers = customers_2024 - customers_2025
    
    return len(new_customers), len(churned_customers), list(churned_customers)


@st.cache_data
def calculate_kpis(df, channel_filter=None):
    """
    Calculate KPIs for dashboard
    Returns dict with 2024, 2025 values and YoY growth
    """
    if channel_filter:
        df_filtered = df[df['Channel'] == channel_filter].copy()
    else:
        df_filtered = df.copy()
    
    sales_2024 = df_filtered[df_filtered['Year'] == 2024]['Sales'].sum()
    sales_2025 = df_filtered[df_filtered['Year'] == 2025]['Sales'].sum()
    
    if sales_2024 > 0:
        growth_pct = ((sales_2025 - sales_2024) / sales_2024 * 100)
    else:
        growth_pct = 0
    
    return {
        '2024': sales_2024,
        '2025': sales_2025,
        'growth': growth_pct
    }
