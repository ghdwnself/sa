# 개발자 가이드
## Developer Guide for 2025 US Sales Dashboard

본 문서는 개발자가 프로젝트를 이해하고 유지보수할 수 있도록 작성되었습니다.

---

## 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [개발 환경 설정](#개발-환경-설정)
3. [코드 구조 설명](#코드-구조-설명)
4. [핵심 로직 상세](#핵심-로직-상세)
5. [UI/UX 디자인 시스템](#uiux-디자인-시스템)
6. [성능 최적화](#성능-최적화)
7. [디버깅 가이드](#디버깅-가이드)
8. [확장 및 커스터마이징](#확장-및-커스터마이징)

---

## 프로젝트 개요

### 비즈니스 목적
- 2025년 미국 시장 판매 실적 분석
- TJX Group (HomeGoods, Marshalls 등) 상세 분석
- EMD/Local 고객 집중도 및 이탈 분석
- 한국 본사 임원진 대상 TV 프레젠테이션

### 기술 스택
```
Python 3.14
├── Streamlit 1.52.1    (웹 프레임워크)
├── Pandas 2.3.3        (데이터 처리)
├── Plotly              (차트 시각화)
└── Python-dateutil     (날짜 처리)
```

### 디자인 철학
- **데이터 우선**: 불필요한 장식 제거, 정보 전달에 집중
- **전문성**: Bloomberg Terminal/Tableau Enterprise 스타일
- **컴팩트**: TV 화면 최적화, 스크롤 최소화

---

## 개발 환경 설정

### 1. Python 환경 준비
```bash
# Python 3.14 이상 권장
python --version

# 가상환경 생성 (옵션)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### 2. 패키지 설치
```bash
cd C:\Users\james\OneDrive\Desktop\Project\sa
pip install -r requirements.txt
```

### 3. 데이터 파일 확인
```bash
# data 폴더 구조 확인
ls data/
# 출력:
# sales_data.csv     (103,810 rows)
# item_master.csv    (1,521 rows)
# db_buyer.csv       (121 rows)
# tjx_item.csv       (123 rows)
```

### 4. 실행
```bash
python -m streamlit run app.py --server.port 8507
```

### 5. 브라우저 접속
```
http://localhost:8507
```

---

## 코드 구조 설명

### 파일 구조
```
sa/
├── app.py                  # 메인 애플리케이션 (458 lines)
├── assets/
│   └── style.css          # 커스텀 스타일 (523 lines)
├── data/
│   ├── sales_data.csv     # 판매 데이터
│   ├── item_master.csv    # 제품 마스터
│   ├── db_buyer.csv       # 고객 정보
│   └── tjx_item.csv       # TJX 제품
├── requirements.txt        # Python 패키지
├── README.md              # 프로젝트 개요
├── DATA_STRUCTURE.md      # 데이터 구조 상세
└── DEVELOPER_GUIDE.md     # 본 문서
```

### app.py 구조 분석

#### 1. Import & Config (1-33 lines)
```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="2025 US Sales Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)
```

**주요 설정:**
- `layout="wide"`: 전체 화면 사용
- `initial_sidebar_state="collapsed"`: 사이드바 숨김

---

#### 2. Data Loading Function (35-80 lines)
```python
@st.cache_data
def load_and_process_data():
    # 1. CSV 로드
    # 2. Date 파싱
    # 3. Customer 대문자 변환
    # 4. 조인 (buyer, item)
    # 5. Channel/Category 매핑
    # 6. Buyer Group 파싱
    # 7. Internal 제외
    return df
```

**캐싱 전략:**
- `@st.cache_data`: 데이터가 변경되지 않는 한 한 번만 로드
- 재실행 시 캐시에서 즉시 반환 (성능 향상)

**중요 포인트:**
```python
# ✅ item_master.csv 로딩 시 첫 행 스킵
df_items = pd.read_csv('./data/item_master.csv', skiprows=[0])

# ✅ Customer 대문자 변환 (조인 전 필수)
df_sales['Customer'] = df_sales['Customer'].str.upper()
df_buyers['Customer'] = df_buyers['Customer'].str.upper()
```

---

#### 3. Business Logic Functions (82-180 lines)

##### map_type_to_channel()
```python
def map_type_to_channel(type_value):
    """Type 코드 → Channel명 매핑"""
    type_mapping = {
        'MMD': 'TJX Group',
        'DI': 'Direct Import',
        'EMD': 'EMD/Local',
        'OBD': 'Online Direct',
        'CS': 'Internal'
    }
    return type_mapping.get(type_value, 'Other')
```

##### map_category_to_group()
```python
def map_category_to_group(category):
    """40+ 카테고리 → 8개 그룹"""
    category_lower = category.lower()
    
    if 'food storage' in category_lower:
        return 'Food Storage'
    elif 'smart seal' in category_lower:
        return 'Smart Seal'
    # ... (나머지 6개 그룹)
    else:
        return '기타'
```

##### parse_buyer_group()
```python
def parse_buyer_group(customer):
    """Customer명 → TJX Buyer 이름 추출"""
    customer_upper = str(customer).upper()
    
    if 'HOMEGOODS' in customer_upper:
        return 'HomeGoods'
    elif 'MARSHALLS' in customer_upper:
        return 'Marshalls'
    # ... (TJ Maxx, Winners, HOMESENSE)
```

---

#### 4. Main Dashboard Function (182-458 lines)

**구조:**
```python
def main():
    df = load_and_process_data()
    
    # 영역 1: 채널별 KPI (5 cards)
    # 영역 2: YoY 비교 + 카테고리 분석
    # 영역 3: TJX 고객 분석
    # 영역 4: TJX 성과
    # 영역 5: EMD 고객 분석
```

**영역별 주요 로직:**

##### 영역 1: 채널별 KPI
```python
# 2024/2025 데이터 분리
df_2024 = df[df['Year'] == 2024]
df_2025 = df[df['Year'] == 2025]

# 채널별 집계
channel_2024 = df_2024.groupby('Channel')['amount'].sum()
channel_2025 = df_2025.groupby('Channel')['amount'].sum()

# 증감률 계산
change = ((val_2025 - val_2024) / val_2024 * 100)
```

##### 영역 2: YoY 비교 차트
```python
# Grouped Bar Chart (겹치지 않게)
fig = px.bar(
    data,
    x='Channel',
    y='Sales',
    color='Year',
    barmode='group',  # 중요!
    color_discrete_map={'2024': '#6c757d', '2025': '#0066ff'}
)
```

##### 영역 3: Food Storage 분석
```python
# Shape & Size 다중 그룹핑
shape_size = df_food_storage.groupby([
    'Brand', 
    'Shape', 
    'Size_Capacity'
]).agg({
    'amount': 'sum',
    'SKU': 'count'
}).reset_index()
```

##### 영역 4: 성장률 계산
```python
# 카테고리 성장률
growth_rate = ((cat_2025 - cat_2024) / cat_2024) * 100

# Top 5 & Bottom 5
top5 = growth_data.head(5)
bottom5 = growth_data.tail(5)
```

##### 영역 5: 신규/이탈 고객
```python
# Set 연산으로 신규/이탈 고객 추출
customers_2024 = set(df_emd_2024['Customer'].unique())
customers_2025 = set(df_emd_2025['Customer'].unique())

new_customers = customers_2025 - customers_2024
churned_customers = customers_2024 - customers_2025
```

---

## 핵심 로직 상세

### 1. 데이터 통합 프로세스

```
┌─────────────────┐
│ sales_data.csv  │
│ Date, SKU,      │
│ Customer, amount│
└────────┬────────┘
         │
         │ 1. Customer 대문자 변환
         ▼
┌─────────────────────────┐
│ df_sales (전처리)        │
│ Customer: 대문자         │
└────────┬────────────────┘
         │
         │ 2. LEFT JOIN on Customer
         ├─────► db_buyer.csv (Type)
         │
         ▼
┌─────────────────────────┐
│ df_sales + Type         │
└────────┬────────────────┘
         │
         │ 3. Type → Channel 매핑
         ▼
┌─────────────────────────┐
│ df_sales + Channel      │
└────────┬────────────────┘
         │
         │ 4. LEFT JOIN on SKU
         ├─────► item_master.csv (Brand, Category, Shape, Size)
         │
         ▼
┌─────────────────────────────────┐
│ df_sales + Channel + Product    │
└────────┬────────────────────────┘
         │
         │ 5. Category → Category_Group
         │ 6. Customer → Buyer_Group
         │ 7. Channel != 'Internal' 필터
         ▼
┌─────────────────────────────────┐
│ 최종 DataFrame (통합 완료)       │
│ - Year, Month                   │
│ - Channel (4개)                 │
│ - Category_Group (8개)          │
│ - Buyer_Group (TJX 5개)         │
└─────────────────────────────────┘
```

---

### 2. KPI 카드 생성 로직

```python
# HTML/CSS 커스텀 카드
st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-label">Total Sales</div>
    <div class="kpi-value">${total_2025:,.0f}</div>
    <div class="kpi-change {'positive' if change >= 0 else 'negative'}">
        {'▲' if change >= 0 else '▼'} {abs(change):.1f}% vs 2024
    </div>
</div>
""", unsafe_allow_html=True)
```

**CSS 클래스 (style.css):**
```css
.kpi-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 8px;
    color: white;
}

.kpi-value {
    font-size: 2.5rem;
    font-weight: 900;
}

.kpi-change.positive {
    color: #10b981;
}

.kpi-change.negative {
    color: #ef4444;
}
```

---

### 3. Plotly 차트 설정

#### Grouped Bar Chart (겹치지 않게)
```python
fig = px.bar(
    data,
    x='Channel',
    y='Sales',
    color='Year',
    barmode='group',  # 'overlay'가 아님!
    title='2024 vs 2025 Channel Sales'
)
fig.update_layout(
    height=400,
    template='plotly_white',  # 깔끔한 배경
    showlegend=True
)
st.plotly_chart(fig, width='stretch')  # Streamlit 1.52.1+
```

#### Dual Axis Chart
```python
fig = go.Figure()

# Primary Y-axis (Bar)
fig.add_trace(go.Bar(
    x=data['Category'],
    y=data['Sales'],
    name='Sales ($)',
    marker_color='#0066ff',
    yaxis='y'
))

# Secondary Y-axis (Line)
fig.add_trace(go.Scatter(
    x=data['Category'],
    y=data['Quantity'],
    name='Quantity',
    marker_color='#28a745',
    yaxis='y2',
    mode='lines+markers'
))

fig.update_layout(
    yaxis=dict(title='Sales ($)', side='left'),
    yaxis2=dict(title='Quantity', side='right', overlaying='y')
)
```

---

## UI/UX 디자인 시스템

### CSS 변수 시스템 (Design Tokens)

```css
:root {
    /* 색상 */
    --color-primary: #0066ff;
    --color-success: #10b981;
    --color-danger: #ef4444;
    
    /* 여백 */
    --space-xs: 0.5rem;
    --space-sm: 1rem;
    --space-md: 1.5rem;
    
    /* 폰트 */
    --font-size-base: 1.1rem;
    --font-size-xl: 1.75rem;
    --font-size-3xl: 3.25rem;
}
```

### 컴포넌트 스타일

#### 1. Section Header
```css
.section-header {
    font-size: var(--font-size-2xl);
    font-weight: 800;
    margin-top: var(--space-lg);
    margin-bottom: var(--space-md);
    color: var(--color-neutral-900);
}
```

#### 2. Data Table
```css
/* Sticky header */
thead th {
    position: sticky;
    top: 0;
    background: var(--color-neutral-100);
    z-index: 10;
}

/* Alternating rows */
tbody tr:nth-child(even) {
    background: var(--color-neutral-50);
}
```

#### 3. Streamlit 헤더 숨김
```css
header {
    display: none !important;
}

[data-testid="stHeader"] {
    display: none;
}
```

---

## 성능 최적화

### 1. 데이터 캐싱
```python
@st.cache_data
def load_and_process_data():
    # 이 함수는 한 번만 실행됨
    # 이후 호출은 캐시에서 즉시 반환
    return df
```

**캐시 무효화 조건:**
- 함수 코드 변경
- 함수 파라미터 변경
- CSV 파일 수정 (자동 감지)

### 2. 그룹핑 최적화
```python
# ✅ 좋은 방법: 한 번만 그룹핑
channel_summary = df.groupby('Channel')['amount'].sum()
tjx_sales = channel_summary.get('TJX Group', 0)
di_sales = channel_summary.get('Direct Import', 0)

# ❌ 나쁜 방법: 반복 필터링
tjx_sales = df[df['Channel']=='TJX Group']['amount'].sum()
di_sales = df[df['Channel']=='Direct Import']['amount'].sum()
```

### 3. 조건부 렌더링
```python
# Buyer별 데이터가 없으면 건너뛰기
for buyer in tjx_buyers:
    df_buyer = df_tjx[df_tjx['Buyer_Group'] == buyer]
    if len(df_buyer) == 0:
        continue  # 렌더링 스킵
    
    # 데이터 표시
    st.dataframe(...)
```

---

## 디버깅 가이드

### 1. 데이터 로딩 오류

#### 문제: KeyError: 'SKU'
```python
# 원인: item_master.csv 첫 행을 스킵하지 않음
df_items = pd.read_csv('./data/item_master.csv')  # ❌

# 해결책
df_items = pd.read_csv('./data/item_master.csv', skiprows=[0])  # ✅
```

#### 문제: Customer 매칭 안 됨
```python
# 원인: 대소문자 불일치
df_sales['Customer'] = 'tj maxx dc'
df_buyers['Customer'] = 'TJ MAXX DC'
# 조인 결과: Type = NaN

# 해결책
df_sales['Customer'] = df_sales['Customer'].str.upper()
df_buyers['Customer'] = df_buyers['Customer'].str.upper()
```

---

### 2. 차트 표시 오류

#### 문제: Streamlit 경고 "use_container_width deprecated"
```python
# 구버전
st.plotly_chart(fig, use_container_width=True)  # ⚠️ Deprecated

# 신버전 (Streamlit 1.52.1+)
st.plotly_chart(fig, width='stretch')  # ✅
```

#### 문제: 바 차트가 겹쳐서 보임
```python
# 원인: barmode='overlay'
fig = px.bar(..., barmode='overlay')  # ❌

# 해결책
fig = px.bar(..., barmode='group')  # ✅
```

---

### 3. 성능 문제

#### 문제: 페이지 로딩이 느림
```python
# 캐싱 확인
@st.cache_data  # 이 데코레이터가 있는지 확인
def load_and_process_data():
    ...
```

#### 문제: 그룹핑이 느림
```python
# 프로파일링
import time

start = time.time()
result = df.groupby('Category')['amount'].sum()
print(f"그룹핑 시간: {time.time() - start:.2f}초")
```

---

### 4. CSS 스타일 적용 안 됨

#### 문제: 스타일이 보이지 않음
```python
# 확인: style.css 파일 경로
with open('./assets/style.css', encoding='utf-8') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
```

#### 문제: 브라우저 캐시 문제
```bash
# 해결: 하드 리프레시
# Chrome: Ctrl + Shift + R (Windows)
# Chrome: Cmd + Shift + R (macOS)
```

---

## 확장 및 커스터마이징

### 1. 새로운 영역 추가

```python
def main():
    df = load_and_process_data()
    
    # 기존 영역 1-5
    # ...
    
    # 새로운 영역 6: 제품별 상세 분석
    st.markdown('<h1 class="section-header">Product Deep Dive</h1>', 
                unsafe_allow_html=True)
    
    # 상위 10개 SKU
    top_skus = df_2025.groupby('SKU')['amount'].sum().nlargest(10)
    st.dataframe(top_skus)
```

---

### 2. 필터링 기능 추가

```python
# 사이드바에 필터 추가
st.sidebar.title("필터")

# 날짜 필터
date_range = st.sidebar.date_input(
    "기간 선택",
    value=(df['Date'].min(), df['Date'].max())
)

# 채널 필터
selected_channels = st.sidebar.multiselect(
    "채널 선택",
    options=['TJX Group', 'Direct Import', 'EMD/Local', 'Online Direct'],
    default=['TJX Group', 'Direct Import', 'EMD/Local', 'Online Direct']
)

# 필터 적용
df_filtered = df[
    (df['Date'] >= date_range[0]) &
    (df['Date'] <= date_range[1]) &
    (df['Channel'].isin(selected_channels))
]
```

---

### 3. PDF 내보내기 기능

```python
import plotly.io as pio

# 차트를 이미지로 저장
fig.write_image("chart.png")

# 또는 HTML 저장
with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(fig.to_html())
```

---

### 4. 데이터베이스 연동

```python
import sqlite3

@st.cache_data
def load_from_database():
    conn = sqlite3.connect('sales.db')
    df = pd.read_sql_query("SELECT * FROM sales_data", conn)
    conn.close()
    return df
```

---

## 배포 가이드

### 1. Streamlit Cloud 배포

```bash
# 1. GitHub에 푸시
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/username/sales-dashboard.git
git push -u origin main

# 2. Streamlit Cloud에서
# - New app 클릭
# - GitHub repo 선택
# - app.py 지정
# - Deploy 클릭
```

### 2. Docker 배포

```dockerfile
# Dockerfile
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8507

CMD ["streamlit", "run", "app.py", "--server.port=8507"]
```

```bash
# 빌드 및 실행
docker build -t sales-dashboard .
docker run -p 8507:8507 sales-dashboard
```

---

## 트러블슈팅 체크리스트

### 데이터 관련
- [ ] item_master.csv를 skiprows=[0]로 로딩했는가?
- [ ] Customer 필드를 대문자로 변환했는가?
- [ ] Internal(CS) 채널을 제외했는가?
- [ ] Burlington을 TJX 분석에서 제외했는가?

### 성능 관련
- [ ] @st.cache_data 데코레이터를 사용했는가?
- [ ] 불필요한 반복 그룹핑을 피했는가?
- [ ] 조건부 렌더링으로 빈 데이터를 스킵했는가?

### UI 관련
- [ ] style.css가 정상 로드되는가?
- [ ] Plotly 차트에 width='stretch'를 사용했는가?
- [ ] 브라우저 캐시를 클리어했는가?

---

## 참고 자료

### 공식 문서
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Python Documentation](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

### 프로젝트 내부 문서
- `README.md`: 프로젝트 개요
- `DATA_STRUCTURE.md`: 데이터 구조 상세
- `DEVELOPER_GUIDE.md`: 본 문서

---

**문서 버전**: v1.0  
**최종 업데이트**: 2025-12-16  
**작성자**: Development Team
