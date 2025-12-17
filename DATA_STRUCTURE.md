# 데이터 구조 상세 문서
## Data Structure Documentation

본 문서는 `data/` 폴더에 위치한 CSV 파일들의 구조와 관계를 설명합니다.

---

## 1. sales_data.csv

### 개요
- **설명**: 판매 트랜잭션 원시 데이터
- **레코드 수**: 103,810 rows
- **기간**: 2024-01-01 ~ 2025-12-31
- **Primary Key**: 없음 (트랜잭션 로그)

### 컬럼 구조

| 컬럼명 | 데이터 타입 | Null 허용 | 설명 | 예시 값 |
|--------|------------|-----------|------|---------|
| Date | String (YYYY-MM-DD) | No | 판매일자 | 2025-01-15 |
| SKU | String | No | 제품 코드 | FS1001 |
| Customer | String | No | 고객명 (대문자) | TJ MAXX DC |
| amount | Float | No | 판매금액 (USD) | 1234.56 |

### 데이터 특성
- **Customer 필드**: 대문자로 저장되어 있음
- **amount**: 소수점 2자리까지 기록
- **Date**: 문자열 형태로 저장 (변환 필요)

### 사용 예시
```python
df_sales = pd.read_csv('./data/sales_data.csv')
df_sales['Date'] = pd.to_datetime(df_sales['Date'])
df_sales['Year'] = df_sales['Date'].dt.year
```

### 주의사항
⚠️ **대문자 변환 필수**: `db_buyer.csv`와 조인 시 Customer 필드를 대문자로 변환해야 함
⚠️ **중복 레코드**: 동일 Date, SKU, Customer 조합이 여러 번 나타날 수 있음 (별도 주문)

---

## 2. item_master.csv

### 개요
- **설명**: 제품 마스터 데이터 (SKU별 상세 정보)
- **레코드 수**: 1,521 rows
- **Primary Key**: SKU
- **갱신 주기**: 신제품 출시 시 업데이트

### ⚠️ 중요: 파일 로딩 시 주의사항
```python
# ✅ 올바른 로딩 방법
df_items = pd.read_csv('./data/item_master.csv', skiprows=[0])

# ❌ 잘못된 로딩 방법 (첫 행이 헤더가 아님)
df_items = pd.read_csv('./data/item_master.csv')  # 컬럼명 오류 발생!
```

### 컬럼 구조

| 컬럼명 | 데이터 타입 | Null 허용 | 설명 | 예시 값 | 사용 영역 |
|--------|------------|-----------|------|---------|-----------|
| SKU | String | No | 제품 코드 (Primary Key) | FS1001 | 전체 |
| UPC | String | Yes | 바코드 번호 | 012345678901 | - |
| ProductName_Short | String | No | 제품명 (짧은 버전) | Smart Seal 19oz Square | - |
| Brand | String | No | 브랜드명 | Lock&Lock | 영역 3, 4 |
| Category | String | No | 카테고리 (원본) | Food Storage Container | 전체 |
| Sub_Category | String | Yes | 서브 카테고리 | Smart Seal Set 12pc | 세트 구분 |
| Size_Capacity | String | Yes | 용량/크기 | 19oz, 46oz Square | 영역 3 (Food Storage) |
| Shape | String | Yes | 형태 | Square, Rectangular, Round | 영역 3 (Food Storage) |
| Color_Pattern | String | Yes | 색상/패턴 | Clear, Blue, Red | - |
| Feature | String | Yes | 제품 특징 | BPA Free, Airtight | - |
| MaterialMain | String | Yes | 주재료 | Plastic, Glass, Stainless | - |
| Vendor | String | Yes | 공급업체 | Vendor A | - |

### Shape & Size_Capacity 값 예시
**Shape 값:**
- Square (정사각형)
- Rectangular (직사각형)
- Round (원형)
- Oval (타원형)

**Size_Capacity 값:**
- 19oz Square
- 46oz Rectangular
- 8PC Glass FS w/ Lids (세트)
- 4.5L

### Sub_Category 세트 구분
**세트 상품 감지 로직:**
```python
is_set = 'set' in str(row['Sub_Category']).lower() or \
         'pc' in str(row['Sub_Category']).lower()
```

**예시:**
- `Smart Seal Set 12pc` → 세트 상품
- `Smart Seal 19oz Square` → 단품

### 사용 예시
```python
# Food Storage 제품의 Shape & Size 분석
df_food = df_items[df_items['Category'].str.contains('Food Storage', na=False)]
shape_size = df_food.groupby(['Brand', 'Shape', 'Size_Capacity']).size()
```

---

## 3. db_buyer.csv

### 개요
- **설명**: 고객(바이어) 정보 및 채널 분류
- **레코드 수**: 121 rows
- **Primary Key**: Customer
- **목적**: Type 코드를 통한 채널 분류

### 컬럼 구조

| 컬럼명 | 데이터 타입 | Null 허용 | 설명 | 예시 값 |
|--------|------------|-----------|------|---------|
| Customer | String | No | 고객명 (대문자) | TJ MAXX DC |
| Name | String | Yes | 정식 회사명 | TJX Companies Inc. |
| Type | String | No | 채널 타입 코드 | MMD, DI, EMD, OBD, CS |

### Type 코드 상세 설명

| Type 코드 | Channel명 | 설명 | 대시보드 포함 여부 | 예시 고객 |
|-----------|-----------|------|-------------------|----------|
| **MMD** | TJX Group | TJX 계열사 (Mass Merchant Distribution) | ✅ Yes | HomeGoods, Marshalls, TJ Maxx |
| **DI** | Direct Import | 직수입 거래 | ✅ Yes | Amazon, Walmart |
| **EMD** | EMD/Local | 현지 유통사 (Emerging Market Distribution) | ✅ Yes | Target, Kroger |
| **OBD** | Online Direct | 온라인 직판 | ✅ Yes | Wayfair, Overstock |
| **CS** | Internal | 내부 거래 (Company Sales) | ❌ No (제외됨) | Internal Transfer |

### TJX Group 구성원

**분석 포함 대상 (5개):**
1. HomeGoods
2. Marshalls
3. TJ Maxx
4. Winners
5. HOMESENSE

**분석 제외 대상:**
- Burlington (TJX 계열이지만 별도 분석 제외)

### Customer 매칭 로직
```python
# 1. sales_data.csv의 Customer를 대문자로 변환
df_sales['Customer'] = df_sales['Customer'].str.upper()

# 2. db_buyer.csv의 Customer도 대문자로 변환
df_buyers['Customer'] = df_buyers['Customer'].str.upper()

# 3. LEFT JOIN
df_merged = df_sales.merge(
    df_buyers[['Customer', 'Type']], 
    on='Customer', 
    how='left'
)

# 4. Type을 Channel로 매핑
df_merged['Channel'] = df_merged['Type'].map({
    'MMD': 'TJX Group',
    'DI': 'Direct Import',
    'EMD': 'EMD/Local',
    'OBD': 'Online Direct',
    'CS': 'Internal'
})

# 5. Internal 제외
df_final = df_merged[df_merged['Channel'] != 'Internal']
```

---

## 4. tjx_item.csv

### 개요
- **설명**: TJX Group에 납품되는 제품 목록
- **레코드 수**: 123 rows
- **Primary Key**: SKU
- **용도**: TJX 전용 제품 필터링

### 컬럼 구조

| 컬럼명 | 데이터 타입 | 설명 |
|--------|------------|------|
| SKU | String | TJX에 납품되는 제품 코드 |
| ... | ... | (추가 정보) |

### 사용 예시
```python
# TJX 전용 제품만 필터링
df_tjx_items = pd.read_csv('./data/tjx_item.csv')
tjx_skus = df_tjx_items['SKU'].unique()

df_tjx_only = df_sales[df_sales['SKU'].isin(tjx_skus)]
```

---

## 데이터 관계도 (ERD)

```
┌─────────────────────┐
│  sales_data.csv     │
│  (103,810 rows)     │
├─────────────────────┤
│ PK: (none)          │
│ Date                │
│ SKU        ──────┐  │
│ Customer ─────┐  │  │
│ amount        │  │  │
└───────────────┼──┼──┘
                │  │
                │  │   ┌────────────────────┐
                │  └───│ item_master.csv    │
                │      │ (1,521 rows)       │
                │      ├────────────────────┤
                │      │ PK: SKU            │
                │      │ Brand              │
                │      │ Category           │
                │      │ Shape              │
                │      │ Size_Capacity      │
                │      └────────────────────┘
                │
                │      ┌────────────────────┐
                └──────│ db_buyer.csv       │
                       │ (121 rows)         │
                       ├────────────────────┤
                       │ PK: Customer       │
                       │ Name               │
                       │ Type               │
                       └────────────────────┘

┌────────────────────┐
│ tjx_item.csv       │
│ (123 rows)         │
├────────────────────┤
│ PK: SKU            │
└────────────────────┘
```

---

## 카테고리 그룹핑 매핑 테이블

| Category_Group | 매핑 키워드 | 원본 Category 예시 |
|----------------|-------------|-------------------|
| Food Storage | food storage, food container, meal prep | Food Storage Container, Glass Food Storage |
| Smart Seal | smart seal | Smart Seal Container |
| Cookware | cookware, bakeware, fry pan, sauce pan | Non-Stick Fry Pan, Stainless Cookware |
| Cutting Board | cutting board, chopping board | Bamboo Cutting Board |
| Canister | canister, jar | Glass Canister, Storage Jar |
| Tableware | tableware, dinnerware, plate, bowl | Dinner Plate, Salad Bowl |
| Kitchen Tool | kitchen tool, utensil, turner, spatula | Silicone Spatula, Kitchen Turner |
| 기타 | (위 키워드 없음) | Miscellaneous Items |

---

## 데이터 품질 체크리스트

### ✅ 데이터 로딩 전 확인사항
- [ ] `item_master.csv`를 `skiprows=[0]`로 로딩했는가?
- [ ] Customer 필드를 대문자로 변환했는가?
- [ ] Date 필드를 datetime으로 변환했는가?

### ✅ 조인 후 확인사항
- [ ] sales_data와 db_buyer 조인 후 Type이 NULL인 레코드는?
- [ ] sales_data와 item_master 조인 후 Brand가 NULL인 레코드는?
- [ ] Internal(CS) 채널을 제외했는가?

### ✅ TJX 분석 전 확인사항
- [ ] Burlington을 제외한 5개 Buyer만 포함했는가?
- [ ] Food Storage 카테고리에 Shape, Size_Capacity가 NULL이 아닌가?

---

## 데이터 업데이트 가이드

### 신규 데이터 추가 시
1. **sales_data.csv 업데이트**
   - 기존 파일 백업: `sales_data_backup_YYYYMMDD.csv`
   - 신규 트랜잭션 추가
   - Customer명이 대문자인지 확인

2. **item_master.csv 업데이트**
   - 신규 SKU 추가 시 모든 컬럼 입력
   - Shape, Size_Capacity는 Food Storage 제품만 필수
   - 첫 행 헤더 유지

3. **db_buyer.csv 업데이트**
   - 신규 고객 추가 시 Type 코드 필수 입력
   - Customer명을 대문자로 입력

### 데이터 검증 스크립트
```python
# 1. Customer 매칭 확인
merged = df_sales.merge(df_buyers, on='Customer', how='left')
unmatched = merged[merged['Type'].isna()]['Customer'].unique()
print(f"매칭 안 된 고객: {len(unmatched)}개")

# 2. SKU 매칭 확인
merged = df_sales.merge(df_items, on='SKU', how='left')
unmatched = merged[merged['Brand'].isna()]['SKU'].unique()
print(f"매칭 안 된 SKU: {len(unmatched)}개")

# 3. 날짜 범위 확인
print(f"데이터 기간: {df_sales['Date'].min()} ~ {df_sales['Date'].max()}")
```

---

## FAQ

### Q1. item_master.csv를 일반적으로 로딩하면 왜 오류가 나나요?
**A1.** 첫 번째 행이 실제 헤더가 아닌 설명 행이기 때문입니다. 반드시 `skiprows=[0]`를 사용하세요.

### Q2. Customer 매칭이 안 되는 경우가 있습니다.
**A2.** sales_data.csv와 db_buyer.csv의 Customer명이 정확히 일치해야 합니다. 공백, 대소문자 차이를 확인하세요.

### Q3. TJX 분석에 Burlington이 포함되어야 하나요?
**A3.** 아니요. Burlington은 TJX 계열이지만 본 분석에서는 제외됩니다. 5개 Buyer만 포함하세요.

### Q4. Shape와 Size_Capacity가 NULL인 제품이 있습니다.
**A4.** 정상입니다. Food Storage 카테고리가 아닌 제품은 해당 필드가 NULL일 수 있습니다.

### Q5. 동일 Date, SKU, Customer 조합이 중복됩니다.
**A5.** 정상입니다. 같은 날 여러 주문이 있을 수 있습니다. 집계 시 `sum()`을 사용하세요.

---

## 데이터 통계 요약

### sales_data.csv
- 총 레코드: 103,810
- 기간: 2024-01-01 ~ 2025-12-31
- 총 판매액: $XX,XXX,XXX
- 고유 고객 수: XXX
- 고유 SKU 수: XXX

### item_master.csv
- 총 SKU: 1,521
- Brand 수: XX
- Category 수: 40+
- Category_Group 수: 8

### db_buyer.csv
- 총 고객: 121
- TJX Group: XX개
- Direct Import: XX개
- EMD/Local: XX개
- Online Direct: XX개
- Internal (제외됨): XX개

---

**문서 버전**: v1.0  
**최종 업데이트**: 2025-12-16  
**작성자**: Sales Analytics Team
