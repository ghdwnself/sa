import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from data_loader import *
from datetime import datetime

# Page config
st.set_page_config(
    page_title="2025 채널 분석 리포트",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Professional Dark Theme
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* All Text Elements - White for Visibility */
    .stApp, .stApp * {
        color: #ffffff !important;
    }
    
    /* Headers */
    h1 {
        color: #ffffff !important;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    h2 {
        color: #4fc3f7 !important;
        font-weight: 600;
        font-size: 1.8rem;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 2px solid #4fc3f7;
        padding-bottom: 0.5rem;
    }
    
    h3 {
        color: #81c784 !important;
        font-weight: 600;
        font-size: 1.3rem;
        margin: 1rem 0 0.5rem 0;
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #b0bec5 !important;
        font-size: 1rem !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 1.1rem !important;
        font-weight: 600;
    }
    
    /* Metric Container Styling */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.08);
        padding: 1.5rem 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.2);
        margin: 2rem 0;
    }
    
    /* DataFrame Styling */
    [data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
    }
    
    /* Main Container */
    .block-container {
        padding: 2rem 3rem;
        max-width: 100%;
    }
    
    /* Column Spacing */
    [data-testid="column"] {
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_cached_data():
    return load_data()

df = load_cached_data()

# Helper function for formatting
def format_amount(value):
    """Format amount as M or K"""
    if value >= 1_000_000:
        return f"${value/1e6:.1f}M"
    else:
        return f"${value/1e3:.0f}K"

# Title
st.title("2025 채널별 매출 분석")
st.markdown("---")

# Overall KPIs
kpis_2025 = calculate_kpis(df, 2025)
yoy = calculate_yoy_comparison(df)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("전체 매출", f"${kpis_2025['total_sales']:,.0f}", f"{yoy['total']['growth']:+.1f}%")
with col2:
    st.metric("MMD", f"${kpis_2025['mmd_sales']:,.0f}", f"{yoy['mmd']['growth']:+.1f}%")
with col3:
    st.metric("FOB (DI)", f"${kpis_2025['fob_sales']:,.0f}", f"{yoy['fob']['growth']:+.1f}%")
with col4:
    st.metric("EMD", f"${kpis_2025['emd_sales']:,.0f}", f"{yoy['emd']['growth']:+.1f}%")
with col5:
    st.metric("OBD", f"${kpis_2025['obd_sales']:,.0f}", f"{yoy['obd']['growth']:+.1f}%")

st.markdown("---")

# Channel comparison
st.header("📊 채널 비교")
col1, col2 = st.columns(2)

with col1:
    # Channel Revenue Distribution - Donut Chart
    st.subheader("채널별 매출 구성")
    
    channel_data = {
        'Channel': ['MMD', 'FOB', 'EMD', 'OBD'],
        'Revenue': [
            kpis_2025['mmd_sales'],
            kpis_2025['fob_sales'],
            kpis_2025['emd_sales'],
            kpis_2025['obd_sales']
        ],
        'Color': ['#4fc3f7', '#81c784', '#ffb74d', '#e57373']
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=channel_data['Channel'],
        values=channel_data['Revenue'],
        hole=0.4,
        marker=dict(
            colors=channel_data['Color'],
            line=dict(color='white', width=2)
        ),
        textinfo='label+percent',
        textfont=dict(size=16, color='white', family='Arial Black'),
        hovertemplate='<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=14),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.1,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(255,255,255,0.05)',
            font=dict(size=14)
        ),
        height=400,
        margin=dict(l=20, r=20, t=40, b=60)
    )
    
    st.plotly_chart(fig, width='stretch', config={'staticPlot': True})

with col2:
    # YoY Growth Comparison - Bar Chart
    st.subheader("채널별 YoY 성장률")
    
    growth_data = {
        'Channel': ['MMD', 'FOB', 'EMD', 'OBD'],
        'Growth': [
            yoy['mmd']['growth'],
            yoy['fob']['growth'],
            yoy['emd']['growth'],
            yoy['obd']['growth']
        ],
        'Color': ['#4fc3f7', '#81c784', '#ffb74d', '#e57373']
    }
    
    fig = go.Figure(data=[go.Bar(
        x=growth_data['Channel'],
        y=growth_data['Growth'],
        marker=dict(
            color=growth_data['Color'],
            line=dict(color='white', width=2)
        ),
        text=[f'<b>{val:+.1f}%</b>' for val in growth_data['Growth']],
        textposition='auto',
        textfont=dict(size=18, color='white'),
        hovertemplate='<b>%{x}</b><br>%{y:+.1f}%<extra></extra>'
    )])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=14),
        xaxis=dict(
            title='',
            tickfont=dict(size=16, color='white')
        ),
        yaxis=dict(
            title='성장률 (%)',
            gridcolor='rgba(255,255,255,0.1)',
            tickfont=dict(size=14, color='white'),
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.3)',
            zerolinewidth=2
        ),
        height=400,
        margin=dict(l=60, r=20, t=60, b=40)
    )
    
    st.plotly_chart(fig, width='stretch', config={'staticPlot': True})

st.markdown("---")

# Detailed channel analysis
top_buyers = get_top_buyers_by_channel(df, 2025, 5)
channel_cat = get_channel_category_breakdown(df, 2025)

# MMD Channel with TJX Group analysis
st.header("🎯 MMD 채널 분석")

# Filter MMD data
mmd_data = df[(df['year'] == 2025) & (df['Type'] == 'MMD')]

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("상위 5개 바이어")
    
    # Get top buyers by revenue and use Name column from db_buyer
    buyer_stats = mmd_data.groupby(['customer', 'Name']).agg({
        'revenue_clean': 'sum',
        'qty_clean': 'sum'
    }).reset_index()
    buyer_stats = buyer_stats.sort_values('revenue_clean', ascending=False).head(5)
    buyer_stats = buyer_stats.sort_values('revenue_clean', ascending=True)  # For display
    
    # Use Name if available, otherwise customer
    buyer_stats['display_name'] = buyer_stats['Name'].fillna(buyer_stats['customer'])
    
    fig = go.Figure(go.Bar(
        y=buyer_stats['display_name'],
        x=buyer_stats['revenue_clean'],
        orientation='h',
        marker=dict(color='#4fc3f7', line=dict(color='white', width=1.5)),
        text=buyer_stats['revenue_clean'].apply(lambda x: f'<b>{format_amount(x)}</b>'),
        textposition='auto',
        textfont=dict(size=16, color='white')
    ))
    fig.update_layout(
        height=350,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=14),
        xaxis=dict(title="매출액", gridcolor='rgba(255,255,255,0.1)', tickfont=dict(size=16)),
        yaxis=dict(tickfont=dict(size=16)),
        margin=dict(l=150,r=10,t=10,b=40)
    )
    st.plotly_chart(fig, width='stretch')

with col2:
    st.subheader("상위 5개 제품 (수량 기준)")
    
    # Get top products by quantity
    top_products = mmd_data.groupby('item_display').agg({
        'revenue_clean': 'sum',
        'qty_clean': 'sum'
    }).reset_index()
    top_products = top_products.sort_values('qty_clean', ascending=False).head(5)
    # Sort ascending for horizontal bar (highest at top)
    top_products = top_products.sort_values('qty_clean', ascending=True)
    
    fig = go.Figure(go.Bar(
        y=top_products['item_display'],
        x=top_products['qty_clean'],
        orientation='h',
        marker=dict(color='#81c784', line=dict(color='white', width=1.5)),
        text=top_products['qty_clean'].apply(lambda x: f'<b>{int(x):,}</b>'),
        textposition='auto',
        textfont=dict(size=16, color='white')
    ))
    fig.update_layout(
        height=350,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=14),
        xaxis=dict(title="판매 수량", gridcolor='rgba(255,255,255,0.1)', tickfont=dict(size=16)),
        yaxis=dict(tickfont=dict(size=16)),
        margin=dict(l=150,r=10,t=10,b=40)
    )
    st.plotly_chart(fig, width='stretch')

# Channel summary
total_rev = mmd_data['revenue_clean'].sum()
st.metric("채널 총 매출", format_amount(total_rev))

# TJX Group Analysis
st.subheader("📍 TJX Group 상세 분석")

# Filter TJX data (exclude HomeGoods French Bull)
tjx_data_2025 = df[(df['year'] == 2025) & (df['customer'].str.contains('TJX', na=False)) & (~df['customer'].str.contains('French Bull', na=False))]
tjx_data_2024 = df[(df['year'] == 2024) & (df['customer'].str.contains('TJX', na=False)) & (~df['customer'].str.contains('French Bull', na=False))]

# TJX Buyers YoY comparison
st.markdown("#### TJX 바이어별 매출 (YoY 비교)")

tjx_buyers_2025 = tjx_data_2025.groupby(['Name', 'customer']).agg({
    'revenue_clean': 'sum'
}).reset_index()
tjx_buyers_2025.columns = ['Name', 'customer', 'revenue_2025']

tjx_buyers_2024 = tjx_data_2024.groupby(['Name', 'customer']).agg({
    'revenue_clean': 'sum'
}).reset_index()
tjx_buyers_2024.columns = ['Name', 'customer', 'revenue_2024']

tjx_comparison = tjx_buyers_2025.merge(tjx_buyers_2024, on=['Name', 'customer'], how='outer').fillna(0)
tjx_comparison['growth'] = ((tjx_comparison['revenue_2025'] - tjx_comparison['revenue_2024']) / tjx_comparison['revenue_2024'].replace(0, 1)) * 100
tjx_comparison['display_name'] = tjx_comparison['Name'].fillna(tjx_comparison['customer'])
tjx_comparison = tjx_comparison.sort_values('revenue_2025', ascending=False)

# Create grouped bar chart for YoY comparison
col1, col2 = st.columns([2, 1])

with col1:
    fig = go.Figure()
    
    # Sort for display
    tjx_display = tjx_comparison.sort_values('revenue_2025', ascending=True)
    
    # Add 2024 bars
    fig.add_trace(go.Bar(
        y=tjx_display['display_name'],
        x=tjx_display['revenue_2024'],
        name='2024',
        orientation='h',
        marker=dict(color='#90caf9', line=dict(color='white', width=1)),
        text=tjx_display['revenue_2024'].apply(lambda x: f'{format_amount(x)}'),
        textposition='auto',
        textfont=dict(size=14, color='white')
    ))
    
    # Add 2025 bars
    fig.add_trace(go.Bar(
        y=tjx_display['display_name'],
        x=tjx_display['revenue_2025'],
        name='2025',
        orientation='h',
        marker=dict(color='#4fc3f7', line=dict(color='white', width=1)),
        text=tjx_display['revenue_2025'].apply(lambda x: f'{format_amount(x)}'),
        textposition='auto',
        textfont=dict(size=14, color='white')
    ))
    
    fig.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=14),
        xaxis=dict(title="매출액", gridcolor='rgba(255,255,255,0.1)', tickfont=dict(size=14)),
        yaxis=dict(tickfont=dict(size=14)),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='rgba(255,255,255,0.05)',
            font=dict(size=12)
        ),
        height=400,
        margin=dict(l=150, r=20, t=50, b=40)
    )
    
    st.plotly_chart(fig, width='stretch', config={'staticPlot': True})

with col2:
    # YoY Growth metrics
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    for _, row in tjx_comparison.head(5).iterrows():
        growth_color = '#4caf50' if row['growth'] > 0 else '#f44336'
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.05); padding: 10px; margin: 5px 0; border-radius: 8px; border-left: 4px solid {growth_color};'>
            <div style='font-size: 14px; color: #b0bec5;'>{row['display_name']}</div>
            <div style='font-size: 20px; font-weight: bold; color: {growth_color};'>{row['growth']:+.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

# TJX Category Analysis
st.markdown("#### TJX 주요 카테고리별 제품 분석")

# Get top categories
category_sales = tjx_data_2025.groupby('category')['revenue_clean'].sum().sort_values(ascending=False)
top_categories = category_sales.head(3).index.tolist()

for category in top_categories:
    st.markdown(f"**{category}**")
    
    cat_data = tjx_data_2025[tjx_data_2025['category'] == category]
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Analyze by brand, shape, size
        if 'Set' in category or 'set' in category:
            # For sets, group by brand and size (pc count)
            product_analysis = cat_data.groupby(['brand', 'size_capacity']).agg({
                'qty_clean': 'sum',
                'revenue_clean': 'sum'
            }).reset_index()
            product_analysis = product_analysis.sort_values('qty_clean', ascending=False).head(10)
            
            # Create stacked bar chart by brand
            brands = product_analysis['brand'].unique()
            
            fig = go.Figure()
            
            for brand in brands[:5]:  # Top 5 brands
                brand_data = product_analysis[product_analysis['brand'] == brand]
                brand_data = brand_data.sort_values('qty_clean', ascending=False)
                
                fig.add_trace(go.Bar(
                    name=str(brand),
                    x=brand_data['size_capacity'].astype(str),
                    y=brand_data['qty_clean'],
                    text=brand_data['qty_clean'].apply(lambda x: f'{int(x):,}'),
                    textposition='auto',
                    textfont=dict(size=12, color='white')
                ))
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=12),
                xaxis=dict(title="사이즈", tickfont=dict(size=12)),
                yaxis=dict(title="판매 수량", gridcolor='rgba(255,255,255,0.1)', tickfont=dict(size=12)),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5,
                    bgcolor='rgba(255,255,255,0.05)',
                    font=dict(size=10)
                ),
                height=300,
                margin=dict(l=60, r=20, t=50, b=40),
                barmode='group'
            )
            
            st.plotly_chart(fig, width='stretch', config={'staticPlot': True})
        else:
            # For non-sets, group by brand
            brand_analysis = cat_data.groupby('brand').agg({
                'qty_clean': 'sum',
                'revenue_clean': 'sum'
            }).reset_index()
            brand_analysis = brand_analysis.sort_values('qty_clean', ascending=False).head(8)
            brand_analysis = brand_analysis.sort_values('qty_clean', ascending=True)  # For horizontal display
            
            fig = go.Figure(go.Bar(
                y=brand_analysis['brand'].astype(str),
                x=brand_analysis['qty_clean'],
                orientation='h',
                marker=dict(color='#ffb74d', line=dict(color='white', width=1)),
                text=brand_analysis['qty_clean'].apply(lambda x: f'{int(x):,}'),
                textposition='auto',
                textfont=dict(size=12, color='white')
            ))
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=12),
                xaxis=dict(title="판매 수량", gridcolor='rgba(255,255,255,0.1)', tickfont=dict(size=12)),
                yaxis=dict(tickfont=dict(size=12)),
                height=300,
                margin=dict(l=100, r=20, t=10, b=40)
            )
            
            st.plotly_chart(fig, width='stretch', config={'staticPlot': True})
    
    with col2:
        # Summary metrics for this category
        total_qty = cat_data['qty_clean'].sum()
        total_rev = cat_data['revenue_clean'].sum()
        avg_price = total_rev / total_qty if total_qty > 0 else 0
        
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        st.metric("총 판매 수량", f"{int(total_qty):,}")
        st.metric("총 매출", format_amount(total_rev))
        st.metric("평균 단가", f"${avg_price:.2f}")

st.markdown("---")

# Other channels
for channel_name, channel_key in [('FOB (DI)', 'DI'), ('EMD', 'EMD'), ('OBD-French Bull', 'OBD-FB'), ('OBD-Neoflam', 'OBD-NF')]:
    st.header(f"🎯 {channel_name} 채널 분석")
    
    # Filter channel data
    channel_data = df[df['year'] == 2025]
    if channel_key == 'DI':
        channel_data = channel_data[channel_data['Type'] == 'DI']
    else:
        channel_data = channel_data[channel_data['Type'] == channel_key]
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("상위 5개 바이어")
        
        # Get top buyers by revenue and use Name column from db_buyer
        buyer_stats = channel_data.groupby(['customer', 'Name']).agg({
            'revenue_clean': 'sum',
            'qty_clean': 'sum'
        }).reset_index()
        buyer_stats = buyer_stats.sort_values('revenue_clean', ascending=False).head(5)
        buyer_stats = buyer_stats.sort_values('revenue_clean', ascending=True)  # For display
        
        # Use Name if available, otherwise customer
        buyer_stats['display_name'] = buyer_stats['Name'].fillna(buyer_stats['customer'])
        
        fig = go.Figure(go.Bar(
            y=buyer_stats['display_name'],
            x=buyer_stats['revenue_clean'],
            orientation='h',
            marker=dict(color='#4fc3f7', line=dict(color='white', width=1.5)),
            text=buyer_stats['revenue_clean'].apply(lambda x: f'<b>{format_amount(x)}</b>'),
            textposition='auto',
            textfont=dict(size=16, color='white')
        ))
        fig.update_layout(
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=14),
            xaxis=dict(title="매출액", gridcolor='rgba(255,255,255,0.1)', tickfont=dict(size=16)),
            yaxis=dict(tickfont=dict(size=16)),
            margin=dict(l=150,r=10,t=10,b=40)
        )
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.subheader("상위 5개 제품 (수량 기준)")
        
        # Get top products by quantity
        top_products = channel_data.groupby('item_display').agg({
            'revenue_clean': 'sum',
            'qty_clean': 'sum'
        }).reset_index()
        top_products = top_products.sort_values('qty_clean', ascending=False).head(5)
        # Sort ascending for horizontal bar (highest at top)
        top_products = top_products.sort_values('qty_clean', ascending=True)
        
        fig = go.Figure(go.Bar(
            y=top_products['item_display'],
            x=top_products['qty_clean'],
            orientation='h',
            marker=dict(color='#81c784', line=dict(color='white', width=1.5)),
            text=top_products['qty_clean'].apply(lambda x: f'<b>{int(x):,}</b>'),
            textposition='auto',
            textfont=dict(size=16, color='white')
        ))
        fig.update_layout(
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=14),
            xaxis=dict(title="판매 수량", gridcolor='rgba(255,255,255,0.1)', tickfont=dict(size=16)),
            yaxis=dict(tickfont=dict(size=16)),
            margin=dict(l=150,r=10,t=10,b=40)
        )
        st.plotly_chart(fig, width='stretch')
    
    # Channel summary - Only Revenue
    total_rev = channel_data['revenue_clean'].sum()
    st.metric("채널 총 매출", format_amount(total_rev))
    
    st.markdown("---")

# Footer
st.markdown(f"<div style='text-align:center;color:#888;margin-top:30px'>리포트 생성: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>", unsafe_allow_html=True)
