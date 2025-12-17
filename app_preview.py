import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from data_loader import *
from datetime import datetime
import pandas as pd
import numpy as np

# Page config
st.set_page_config(
    page_title="Channel Visualization Preview",
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
    
    /* Metric Container Styling */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.08);
        padding: 1.5rem 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.05);
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4fc3f7, #2196f3);
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.2);
        margin: 2rem 0;
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

# Get YoY data
yoy = calculate_yoy_comparison(df)

# Scorecard component (reusable)
def create_scorecard(channels_metrics):
    scorecard_html = "<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>"
    
    for metric in channels_metrics:
        scorecard_html += f"""
        <div style='background: linear-gradient(135deg, {metric['color']}15, {metric['color']}08);
                    border: 2px solid {metric['color']};
                    border-radius: 12px;
                    padding: 15px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>
            <div style='text-align: center;'>
                <div style='font-size: 20px; font-weight: bold; color: {metric['color']};
                           margin-bottom: 10px;'>{metric['name']}</div>
                
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px;'>
                    <div style='background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px;'>
                        <div style='font-size: 11px; color: #b0bec5;'>매출</div>
                        <div style='font-size: 16px; font-weight: 600; color: white;'>{format_amount(metric['revenue'])}</div>
                    </div>
                    <div style='background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px;'>
                        <div style='font-size: 11px; color: #b0bec5;'>YoY</div>
                        <div style='font-size: 16px; font-weight: 600; color: {"#4caf50" if metric["growth"] > 0 else "#f44336"};'>{metric['growth']:+.1f}%</div>
                    </div>
                    <div style='background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px;'>
                        <div style='font-size: 11px; color: #b0bec5;'>수량</div>
                        <div style='font-size: 16px; font-weight: 600; color: white;'>{metric['qty']:,.0f}</div>
                    </div>
                    <div style='background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px;'>
                        <div style='font-size: 11px; color: #b0bec5;'>평균단가</div>
                        <div style='font-size: 16px; font-weight: 600; color: white;'>${metric['avg_price']:.2f}</div>
                    </div>
                </div>
                
                <div style='margin-top: 10px; padding: 6px; background: rgba(255,255,255,0.03); 
                           border-radius: 6px; font-size: 12px; color: #e0e0e0;'>
                    SKUs: <span style='font-weight: 600; color: white;'>{metric['skus']}</span>
                </div>
            </div>
        </div>
        """
    
    scorecard_html += "</div>"
    return scorecard_html

# Calculate metrics for scorecards
channels_metrics = []
for channel_name, channel_key, color in [
    ('MMD', 'MMD', '#4fc3f7'),
    ('FOB', 'DI', '#81c784'),
    ('EMD', 'EMD', '#ffb74d'),
    ('OBD', 'OBD', '#e57373')
]:
    ch_data = df[df['year'] == 2025]
    if channel_key == 'DI':
        ch_data = ch_data[ch_data['Type'] == 'DI']
    else:
        ch_data = ch_data[ch_data['Type'] == channel_key]
    
    total_rev = ch_data['revenue_clean'].sum()
    total_qty = ch_data['qty_clean'].sum()
    avg_price = total_rev / total_qty if total_qty > 0 else 0
    unique_skus = ch_data['sku'].nunique()
    
    # Get YoY growth
    if channel_key == 'MMD':
        growth = yoy['mmd']['growth']
    elif channel_key == 'DI':
        growth = yoy['fob']['growth']
    elif channel_key == 'EMD':
        growth = yoy['emd']['growth']
    else:
        growth = yoy['obd']['growth']
    
    channels_metrics.append({
        'name': channel_name,
        'color': color,
        'revenue': total_rev,
        'qty': total_qty,
        'avg_price': avg_price,
        'skus': unique_skus,
        'growth': growth
    })

# Title
st.title("📊 Channel Visualization Preview")
st.markdown("### 4가지 옵션을 비교하고 선택하세요")
st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "옵션 1: 채널별 월별 트렌드",
    "옵션 2: 카테고리 × 채널 매트릭스",
    "옵션 3: 채널별 Top 3 제품",
    "옵션 4: 채널 비교 레이더 차트"
])

# TAB 1: Monthly Trend
with tab1:
    st.markdown("## 채널별 월별 트렌드")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("2025년 월별 매출 추이")
        
        # Check if date column exists
        if 'date' in df.columns or 'Date' in df.columns:
            date_col = 'date' if 'date' in df.columns else 'Date'
            df_2025 = df[df['year'] == 2025].copy()
            df_2025[date_col] = pd.to_datetime(df_2025[date_col], errors='coerce')
            df_2025['month'] = df_2025[date_col].dt.to_period('M').astype(str)
            
            # Group by month and channel
            monthly_data = []
            for channel_name, channel_key, color in [
                ('MMD', 'MMD', '#4fc3f7'),
                ('FOB', 'DI', '#81c784'),
                ('EMD', 'EMD', '#ffb74d'),
                ('OBD', 'OBD', '#e57373')
            ]:
                ch_data = df_2025.copy()
                if channel_key == 'DI':
                    ch_data = ch_data[ch_data['Type'] == 'DI']
                else:
                    ch_data = ch_data[ch_data['Type'] == channel_key]
                
                month_revenue = ch_data.groupby('month')['revenue_clean'].sum().reset_index()
                month_revenue['channel'] = channel_name
                month_revenue['color'] = color
                monthly_data.append(month_revenue)
            
            if monthly_data:
                all_months = pd.concat(monthly_data, ignore_index=True)
                
                # Create line chart
                fig = go.Figure()
                
                for channel_name, color in [('MMD', '#4fc3f7'), ('FOB', '#81c784'), 
                                            ('EMD', '#ffb74d'), ('OBD', '#e57373')]:
                    ch_month = all_months[all_months['channel'] == channel_name]
                    fig.add_trace(go.Scatter(
                        x=ch_month['month'],
                        y=ch_month['revenue_clean'],
                        mode='lines+markers',
                        name=channel_name,
                        line=dict(color=color, width=3),
                        marker=dict(size=8, color=color, line=dict(width=2, color='white')),
                        text=ch_month['revenue_clean'].apply(lambda x: format_amount(x)),
                        hovertemplate='%{fullData.name}<br>%{x}<br>%{text}<extra></extra>'
                    ))
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', size=14),
                    xaxis=dict(
                        title='Month',
                        tickfont=dict(size=14),
                        gridcolor='rgba(255,255,255,0.1)'
                    ),
                    yaxis=dict(
                        title='Revenue',
                        tickfont=dict(size=14),
                        gridcolor='rgba(255,255,255,0.1)'
                    ),
                    legend=dict(
                        orientation='h',
                        yanchor='bottom',
                        y=1.02,
                        xanchor='center',
                        x=0.5,
                        bgcolor='rgba(255,255,255,0.05)',
                        font=dict(size=12)
                    ),
                    height=400,
                    margin=dict(l=60, r=20, t=60, b=60)
                )
                
                st.plotly_chart(fig, width='stretch', config={'staticPlot': True})
            else:
                st.info("월별 데이터 없음")
        else:
            st.info("데이터에 날짜 컬럼이 없어 월별 트렌드를 표시할 수 없습니다.")
    
    with col2:
        st.subheader("채널 성과 스코어카드")
        st.markdown(create_scorecard(channels_metrics), unsafe_allow_html=True)

# TAB 2: Category x Channel Matrix (Heatmap)
with tab2:
    st.markdown("## 카테고리 × 채널 매트릭스")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("채널별 카테고리 매출 분포")
        
        # Prepare matrix data
        matrix_data = []
        for channel_name, channel_key in [('MMD', 'MMD'), ('FOB', 'DI'), 
                                          ('EMD', 'EMD'), ('OBD', 'OBD')]:
            ch_data = df[df['year'] == 2025]
            if channel_key == 'DI':
                ch_data = ch_data[ch_data['Type'] == 'DI']
            else:
                ch_data = ch_data[ch_data['Type'] == channel_key]
            
            cat_rev = ch_data.groupby('category')['revenue_clean'].sum().to_dict()
            row = {'Channel': channel_name}
            row.update(cat_rev)
            matrix_data.append(row)
        
        matrix_df = pd.DataFrame(matrix_data).set_index('Channel').fillna(0)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=matrix_df.values,
            x=matrix_df.columns,
            y=matrix_df.index,
            colorscale='Blues',
            text=[[format_amount(val) for val in row] for row in matrix_df.values],
            texttemplate='<b>%{text}</b>',
            textfont=dict(size=14, color='white'),
            hovertemplate='%{y}<br>%{x}<br>%{text}<extra></extra>',
            colorbar=dict(
                title=dict(text='Revenue', font=dict(color='white')),
                tickfont=dict(color='white')
            )
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=14),
            xaxis=dict(
                tickfont=dict(size=14),
                side='bottom'
            ),
            yaxis=dict(
                tickfont=dict(size=16)
            ),
            height=400,
            margin=dict(l=80, r=20, t=40, b=60)
        )
        
        st.plotly_chart(fig, width='stretch', config={'staticPlot': True})
    
    with col2:
        st.subheader("채널 성과 스코어카드")
        st.markdown(create_scorecard(channels_metrics), unsafe_allow_html=True)

# TAB 3: Top 3 Products per Channel
with tab3:
    st.markdown("## 채널별 Top 3 제품")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("채널별 베스트셀러 제품")
        
        # Create compact product list
        products_html = "<div style='display: flex; flex-direction: column; gap: 15px;'>"
        
        for channel_name, channel_key, color in [
            ('MMD', 'MMD', '#4fc3f7'),
            ('FOB', 'DI', '#81c784'),
            ('EMD', 'EMD', '#ffb74d'),
            ('OBD', 'OBD', '#e57373')
        ]:
            ch_data = df[df['year'] == 2025]
            if channel_key == 'DI':
                ch_data = ch_data[ch_data['Type'] == 'DI']
            else:
                ch_data = ch_data[ch_data['Type'] == channel_key]
            
            # Get top 3 products
            top_products = ch_data.groupby('item_display').agg({
                'revenue_clean': 'sum',
                'qty_clean': 'sum'
            }).reset_index().sort_values('revenue_clean', ascending=False).head(3)
            
            products_html += f"""
            <div style='background: linear-gradient(135deg, {color}15, {color}08);
                        border-left: 4px solid {color};
                        border-radius: 8px;
                        padding: 12px;'>
                <div style='font-size: 18px; font-weight: bold; color: {color}; margin-bottom: 8px;'>
                    {channel_name}
                </div>
            """
            
            for idx, row in top_products.iterrows():
                products_html += f"""
                <div style='background: rgba(255,255,255,0.05); padding: 8px; margin: 4px 0;
                           border-radius: 6px; display: flex; justify-content: space-between;'>
                    <span style='color: white; font-size: 14px;'>{row['item_display']}</span>
                    <span style='color: {color}; font-weight: 600; font-size: 14px;'>
                        {format_amount(row['revenue_clean'])}
                    </span>
                </div>
                """
            
            products_html += "</div>"
        
        products_html += "</div>"
        st.markdown(products_html, unsafe_allow_html=True)
    
    with col2:
        st.subheader("채널 성과 스코어카드")
        st.markdown(create_scorecard(channels_metrics), unsafe_allow_html=True)

# TAB 4: Radar Chart
with tab4:
    st.markdown("## 채널 비교 레이더 차트")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("채널별 성과 비교")
        
        # Prepare radar data - normalize metrics to 0-100 scale
        radar_categories = ['매출', '수량', '평균단가', 'SKU 다양성', 'YoY 성장']
        
        # Get max values for normalization
        max_revenue = max([m['revenue'] for m in channels_metrics])
        max_qty = max([m['qty'] for m in channels_metrics])
        max_price = max([m['avg_price'] for m in channels_metrics])
        max_skus = max([m['skus'] for m in channels_metrics])
        max_growth = max([abs(m['growth']) for m in channels_metrics])
        
        fig = go.Figure()
        
        for metric in channels_metrics:
            # Normalize to 0-100
            values = [
                (metric['revenue'] / max_revenue * 100) if max_revenue > 0 else 0,
                (metric['qty'] / max_qty * 100) if max_qty > 0 else 0,
                (metric['avg_price'] / max_price * 100) if max_price > 0 else 0,
                (metric['skus'] / max_skus * 100) if max_skus > 0 else 0,
                (abs(metric['growth']) / max_growth * 100) if max_growth > 0 else 0
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=radar_categories,
                fill='toself',
                name=metric['name'],
                line=dict(color=metric['color'], width=2),
                fillcolor=f"rgba{tuple(list(int(metric['color'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}"
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='rgba(255,255,255,0.2)',
                    tickfont=dict(color='white', size=12)
                ),
                angularaxis=dict(
                    gridcolor='rgba(255,255,255,0.2)',
                    tickfont=dict(color='white', size=14)
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.2,
                xanchor='center',
                x=0.5,
                bgcolor='rgba(255,255,255,0.05)',
                font=dict(size=12)
            ),
            height=450,
            margin=dict(l=80, r=80, t=40, b=80)
        )
        
        st.plotly_chart(fig, width='stretch', config={'staticPlot': True})
    
    with col2:
        st.subheader("채널 성과 스코어카드")
        st.markdown(create_scorecard(channels_metrics), unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f"<div style='text-align:center;color:#888;margin-top:30px'>Preview Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>", unsafe_allow_html=True)
