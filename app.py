"""
2025 Executive Sales Dashboard (TV Optimized)
A high-performance Streamlit dashboard with Executive Dark Mode theme
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from data_loader import (
    process_data, 
    calculate_kpis, 
    get_channel_data,
    get_category_data,
    get_tjx_buyer_breakdown,
    get_food_storage_analysis,
    get_sku_performance,
    get_emd_customers,
    get_churn_analysis
)

# Page Configuration
st.set_page_config(
    page_title="2025 Global Sales Report",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load Data
df = process_data()

# Header Section
col_title, col_filter = st.columns([3, 1])

with col_title:
    st.markdown("# 📊 2025 Global Sales Report")

with col_filter:
    # Brand Filter
    brands = ['All Brands'] + sorted(df['Brand'].dropna().unique().tolist())
    selected_brand = st.selectbox("Select Brand", brands, key="brand_filter")

# Apply Brand Filter
if selected_brand != 'All Brands':
    df_filtered = df[df['Brand'] == selected_brand].copy()
else:
    df_filtered = df.copy()

st.markdown("---")

# ===== ROW 1: KPI Overview (5 Cards) =====
st.markdown("### 📈 Key Performance Indicators")

kpi_cols = st.columns(5)

# Calculate KPIs for each channel
kpi_total = calculate_kpis(df_filtered)
kpi_tjx = calculate_kpis(df_filtered, 'TJX Group')
kpi_di = calculate_kpis(df_filtered, 'Direct Import')
kpi_emd = calculate_kpis(df_filtered, 'EMD/Local')
kpi_obd = calculate_kpis(df_filtered, 'Online Direct')

kpis = [
    ("Total Sales", kpi_total),
    ("TJX Sales", kpi_tjx),
    ("DI Sales", kpi_di),
    ("EMD Sales", kpi_emd),
    ("OBD Sales", kpi_obd)
]

for col, (label, kpi_data) in zip(kpi_cols, kpis):
    with col:
        value_2025 = kpi_data['2025']
        growth = kpi_data['growth']
        
        # Format large numbers
        if value_2025 >= 1_000_000:
            display_value = f"${value_2025/1_000_000:.2f}M"
        elif value_2025 >= 1_000:
            display_value = f"${value_2025/1_000:.1f}K"
        else:
            display_value = f"${value_2025:.0f}"
        
        st.metric(
            label=label,
            value=display_value,
            delta=f"{growth:+.1f}%"
        )

st.markdown("---")

# ===== ROW 2: Trend Analysis =====
st.markdown("### 📊 Trend Analysis")

col_channel, col_category = st.columns([3, 2])

with col_channel:
    st.markdown("#### Sales by Channel (2024 vs 2025)")
    
    channel_data = get_channel_data(df_filtered)
    
    # Create grouped bar chart
    fig_channel = go.Figure()
    
    for year in [2024, 2025]:
        year_data = channel_data[channel_data['Year'] == year]
        fig_channel.add_trace(go.Bar(
            x=year_data['Channel'],
            y=year_data['Sales'],
            name=str(year),
            text=year_data['Sales'].apply(lambda x: f'${x/1000:.0f}K'),
            textposition='outside'
        ))
    
    fig_channel.update_layout(
        template='plotly_dark',
        barmode='group',
        height=400,
        showlegend=True,
        xaxis_title="Channel",
        yaxis_title="Sales ($)",
        plot_bgcolor='#0f172a',
        paper_bgcolor='#0f172a',
        font=dict(size=14, family='Inter')
    )
    
    st.plotly_chart(fig_channel, use_container_width=True)

with col_category:
    st.markdown("#### Category Performance")
    
    category_data = get_category_data(df_filtered)
    category_2025 = category_data[category_data['Year'] == 2025].sort_values('Sales', ascending=False).head(8)
    
    # Create combo chart (Bar + Line)
    fig_category = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_category.add_trace(
        go.Bar(
            x=category_2025['Category_Group'],
            y=category_2025['Sales'],
            name='Sales',
            marker_color='#3b82f6'
        ),
        secondary_y=False
    )
    
    fig_category.add_trace(
        go.Scatter(
            x=category_2025['Category_Group'],
            y=category_2025['Quantity'],
            name='Quantity',
            mode='lines+markers',
            line=dict(color='#22c55e', width=3),
            marker=dict(size=8)
        ),
        secondary_y=True
    )
    
    fig_category.update_layout(
        template='plotly_dark',
        height=400,
        showlegend=True,
        plot_bgcolor='#0f172a',
        paper_bgcolor='#0f172a',
        font=dict(size=14, family='Inter')
    )
    
    fig_category.update_xaxes(title_text="Category")
    fig_category.update_yaxes(title_text="Sales ($)", secondary_y=False)
    fig_category.update_yaxes(title_text="Quantity", secondary_y=True)
    
    st.plotly_chart(fig_category, use_container_width=True)

st.markdown("---")

# ===== ROW 3: TJX Deep Dive =====
st.markdown("### 🎯 TJX Deep Dive")

col_food_storage, col_buyers = st.columns(2)

with col_food_storage:
    st.markdown("#### Food Storage Analysis")
    
    brand_data, shape_size_data = get_food_storage_analysis(df_filtered)
    
    if not brand_data.empty:
        st.markdown("**Sales by Brand (2025)**")
        brand_2025 = brand_data[brand_data['Year'] == 2025].sort_values('Sales', ascending=False)
        if not brand_2025.empty:
            for idx, row in brand_2025.iterrows():
                st.markdown(f"- **{row['Brand']}**: ${row['Sales']:,.0f}")
        else:
            st.info("No 2025 data available")
    else:
        st.info("No Food Storage data for TJX")
    
    st.markdown("---")
    
    if not shape_size_data.empty:
        st.markdown("**Breakdown by Shape & Size (2025)**")
        shape_2025 = shape_size_data[shape_size_data['Year'] == 2025].sort_values('Sales', ascending=False).head(5)
        if not shape_2025.empty:
            shape_table = shape_2025[['Shape', 'Size_Capacity', 'Sales']].copy()
            shape_table['Sales'] = shape_table['Sales'].apply(lambda x: f"${x:,.0f}")
            st.dataframe(shape_table, hide_index=True, use_container_width=True)
        else:
            st.info("No 2025 data available")

with col_buyers:
    st.markdown("#### TJX Buyer Breakdown")
    
    buyer_data = get_tjx_buyer_breakdown(df_filtered)
    
    for buyer in ['HomeGoods', 'Marshalls', 'TJ Maxx', 'Winners', 'HomeSense']:
        st.markdown(f"**{buyer}**")
        if buyer in buyer_data and not buyer_data[buyer].empty:
            top_cats = buyer_data[buyer]
            for cat, sales in top_cats.items():
                st.markdown(f"- {cat}: ${sales:,.0f}")
        else:
            st.markdown("- *No data*")
        st.markdown("")

st.markdown("---")

# ===== ROW 4: Growth & Decline (TJX Focused) =====
st.markdown("### 📉📈 Growth & Decline Analysis")

col_cat_growth, col_sku_perf = st.columns(2)

with col_cat_growth:
    st.markdown("#### Category Growth % (YoY)")
    
    category_data = get_category_data(df_filtered)
    
    # Calculate growth by category
    cat_pivot = category_data.pivot_table(
        index='Category_Group', 
        columns='Year', 
        values='Sales', 
        fill_value=0
    )
    
    if 2024 in cat_pivot.columns and 2025 in cat_pivot.columns:
        cat_pivot['Growth_Pct'] = ((cat_pivot[2025] - cat_pivot[2024]) / cat_pivot[2024] * 100).round(1)
        cat_pivot = cat_pivot[cat_pivot[2024] > 0]  # Only categories with 2024 sales
        cat_growth = cat_pivot.sort_values('Growth_Pct', ascending=True)
        
        # Horizontal bar chart
        fig_cat_growth = go.Figure()
        
        colors = ['#22c55e' if x >= 0 else '#ef4444' for x in cat_growth['Growth_Pct']]
        
        fig_cat_growth.add_trace(go.Bar(
            y=cat_growth.index,
            x=cat_growth['Growth_Pct'],
            orientation='h',
            marker_color=colors,
            text=cat_growth['Growth_Pct'].apply(lambda x: f'{x:+.1f}%'),
            textposition='outside'
        ))
        
        fig_cat_growth.update_layout(
            template='plotly_dark',
            height=400,
            showlegend=False,
            xaxis_title="Growth %",
            yaxis_title="Category",
            plot_bgcolor='#0f172a',
            paper_bgcolor='#0f172a',
            font=dict(size=14, family='Inter')
        )
        
        st.plotly_chart(fig_cat_growth, use_container_width=True)
    else:
        st.info("Insufficient data for growth calculation")

with col_sku_perf:
    st.markdown("#### SKU Performance (Top 5 Growing vs Declining)")
    
    top_growing, top_declining = get_sku_performance(df_filtered)
    
    if not top_growing.empty:
        st.markdown("**🔥 Top 5 Growing SKUs**")
        for idx, row in top_growing.iterrows():
            active_badge = ' 🟢 Active' if row['Is_Active_TJX'] else ''
            st.markdown(f"- **{row['SKU']}**: {row['Growth_Pct']:+.1f}%{active_badge}")
    
    st.markdown("")
    
    if not top_declining.empty:
        st.markdown("**⚠️ Top 5 Declining SKUs**")
        for idx, row in top_declining.iterrows():
            active_badge = ' 🔴 Active (Alert!)' if row['Is_Active_TJX'] else ''
            st.markdown(f"- **{row['SKU']}**: {row['Growth_Pct']:.1f}%{active_badge}")

st.markdown("---")

# ===== ROW 5: EMD/Local Insights =====
st.markdown("### 🌍 EMD/Local Insights")

col_emd_customers, col_churn = st.columns(2)

with col_emd_customers:
    st.markdown("#### Top 10 EMD/Local Customers")
    
    emd_customers = get_emd_customers(df_filtered)
    
    if not emd_customers.empty:
        emd_display = emd_customers.copy()
        emd_display['Revenue'] = emd_display['Revenue'].apply(lambda x: f"${x:,.0f}")
        emd_display['Share_Pct'] = emd_display['Share_Pct'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(emd_display, hide_index=True, use_container_width=True)
    else:
        st.info("No EMD/Local customer data available")

with col_churn:
    st.markdown("#### Churn Analysis")
    
    new_count, churned_count, churned_list = get_churn_analysis(df_filtered)
    
    # New Customers Card
    st.markdown(f"""
    <div style='background-color: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;'>
        <h4 style='color: #22c55e; margin: 0;'>🆕 New Customers (2025 Only)</h4>
        <p style='font-size: 2.5rem; font-weight: 700; margin: 0.5rem 0; color: #f8fafc;'>{new_count}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Churned Customers Card
    st.markdown(f"""
    <div style='background-color: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 1.5rem;'>
        <h4 style='color: #ef4444; margin: 0;'>⚠️ Churned Customers (2024 Active, 2025 Zero)</h4>
        <p style='font-size: 2.5rem; font-weight: 700; margin: 0.5rem 0; color: #f8fafc;'>{churned_count}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if churned_count > 0:
        with st.expander("View Churned Customer List"):
            for customer in sorted(churned_list):
                st.markdown(f"- {customer}")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #94a3b8;'>Executive Dashboard | Powered by Streamlit & Plotly</p>", unsafe_allow_html=True)
