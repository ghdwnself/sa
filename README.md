# 2025 Executive Sales Dashboard

A high-performance, TV-optimized Streamlit dashboard featuring Executive Dark Mode theme for displaying global sales analytics.

## 🎯 Features

- **Executive Dark Mode UI**: Custom CSS theme with Slate-950 background, optimized for TV displays
- **5-Row Bento Grid Layout**: Organized dashboard sections for different analytics views
- **Real-time KPI Tracking**: Year-over-Year comparisons with color-coded growth indicators
- **Multi-Channel Analysis**: TJX Group, Direct Import, EMD/Local, and Online Direct breakdowns
- **Advanced Filtering**: Brand-based filtering across all metrics
- **TJX Deep Dive**: Detailed buyer segmentation and Food Storage analysis
- **Churn Analysis**: Track new and churned customers
- **Performance Optimized**: Cached data loading with Streamlit's `@st.cache_data`

## 🛠️ Tech Stack

- **Streamlit** 1.52+ - Web application framework
- **Plotly** - Interactive data visualizations
- **Pandas** - Data manipulation and analysis
- **Python** 3.8+

## 📁 Project Structure

```
sa/
├── app.py                  # Main Streamlit application
├── data_loader.py          # Data loading and transformation logic
├── requirements.txt        # Python dependencies
├── assets/
│   └── style.css          # Executive Dark Mode CSS theme
└── data/
    ├── sales_data.csv     # Sales transaction data
    ├── item_master.csv    # Product master data (with description row)
    ├── tjx_item.csv       # Active/On-going TJX items list
    └── db_buyer.csv       # Customer-to-channel mapping
```

## 🚀 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ghdwnself/sa.git
   cd sa
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare data files**:
   - Ensure all CSV files are in the `data/` directory
   - `item_master.csv` should have a description row (row 0) followed by headers
   - All customer names will be auto-converted to UPPERCASE

4. **Run the dashboard**:
   ```bash
   streamlit run app.py
   ```

5. **Access the dashboard**:
   - Open browser to `http://localhost:8501`
   - For TV display, use fullscreen mode (F11)

## 📊 Dashboard Sections

### Row 1: KPI Overview
Five key metrics cards showing:
- Total Sales
- TJX Sales
- Direct Import Sales
- EMD/Local Sales
- Online Direct Sales

Each card displays 2025 revenue with YoY growth percentage.

### Row 2: Trend Analysis
- **Left (60%)**: Channel comparison chart (2024 vs 2025)
- **Right (40%)**: Category performance with dual-axis (Sales + Quantity)

### Row 3: TJX Deep Dive
- **Left**: Food Storage analysis by Brand and Shape/Size
- **Right**: Buyer breakdown (HomeGoods, Marshalls, TJ Maxx, Winners, HomeSense)

### Row 4: Growth & Decline
- **Left**: Category growth percentage (horizontal bar chart)
- **Right**: Top 5 Growing and Declining SKUs with Active Item indicators

### Row 5: EMD/Local Insights
- **Left**: Top 10 EMD/Local customers with revenue share
- **Right**: Churn analysis (New vs Churned customers)

## 🔧 Data Processing Logic

### Channel Mapping
- `MMD` → TJX Group
- `DI` → Direct Import
- `EMD` → EMD/Local
- `OBD` → Online Direct
- `CS` → Dropped (Internal Sales)
- **Unmatched** → EMD/Local (default)

### Category Grouping
8 product categories using keyword matching:
1. Food Storage
2. Smart Seal
3. Cookware
4. Cutting Board
5. Canister
6. Tableware
7. Kitchen Tool
8. Others

### TJX Buyer Segmentation
Keywords: `HOMEGOODS`, `MARSHALLS`, `TJ MAXX`, `WINNERS`, `HOMESENSE`
- **Excludes**: `BURLINGTON` from TJX-specific breakdowns

### Active Items
Items listed in `tjx_item.csv` are tagged as "On-going (Active)" items, with special indicators when they appear in declining SKUs (critical alert).

## 🎨 Design System

### Colors
- **Background**: Slate-950 (#020617)
- **Cards**: Slate-900 (#0f172a)
- **Borders**: Slate-800 (#1e293b)
- **Text**: White (#f8fafc) / Slate-400 (#94a3b8)
- **Growth**: Green (#22c55e)
- **Decline**: Red (#ef4444)

### Typography
- **Font**: Inter (Google Fonts)
- **Scale**: 1.2x standard web size for TV readability

## 📝 Data File Requirements

### sales_data.csv
```csv
Date,Customer,SKU,Category,Sales,Quantity
2024-01-15,homegoods,FS-001,Food Storage - Rectangle - 500ml,15000,500
```
- Date format: YYYY-MM-DD
- Customer: Any case (auto-converted to UPPERCASE)
- Years: 2024 and 2025 only

### item_master.csv
```csv
Description: This file contains item master data
SKU,Brand,Shape,Size_Capacity,Material
FS-001,ZipLock,Rectangle,500ml,Plastic
```
**CRITICAL**: First row is description, second row is headers (use `skiprows=[0]`)

### tjx_item.csv
```csv
SKU
FS-001
SS-002
```
Simple list of active/on-going SKU codes.

### db_buyer.csv
```csv
Customer,Type
HOMEGOODS,MMD
ABC TRADING,EMD
```
Maps customers to channel types.

## 🚨 Key Implementation Notes

1. **Performance**: All data loading functions use `@st.cache_data` decorator
2. **Uppercase**: Customer names automatically converted to UPPERCASE in sales_data and db_buyer
3. **Filtering**: Date filtering applied automatically (2024-2025 only)
4. **Default Channel**: Unmatched customers (NaN Type) automatically map to "EMD/Local"
5. **Burlington Exclusion**: Burlington is MMD type but excluded from TJX buyer segmentation
6. **Active Item Alerts**: Declining active items are highlighted in red as critical alerts

## 📈 Future Enhancements

- Real-time data refresh from database
- Export functionality for reports
- Additional drill-down capabilities
- Mobile-responsive layout
- Multi-language support

## 📄 License

This project is proprietary and confidential.

## 👥 Contact

For questions or support, please contact the development team.
