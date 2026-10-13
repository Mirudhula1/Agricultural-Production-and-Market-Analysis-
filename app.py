
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Agriculture Analytics Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# PROFESSIONAL GREEN AND WHITE THEME
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #F6F9F5;
    color: #26382C;
}

[data-testid="stHeader"] {
    background-color: #F6F9F5;
}

h1, h2, h3, h4 {
    color: #205B3B !important;
}

.stApp p,
.stApp label,
.stApp [data-testid="stMarkdownContainer"] {
    color: #34483B;
}

[data-testid="stSidebar"] {
    background-color: #EAF1E9;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: #244632 !important;
}

div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #DCE7DC;
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 2px 8px rgba(32, 91, 59, 0.06);
}

[data-testid="stMetricLabel"] {
    color: #53675A !important;
}

[data-testid="stMetricLabel"] p {
    color: #53675A !important;
}

[data-testid="stMetricValue"] {
    color: #205B3B !important;
    font-weight: 700;
}

div[data-testid="stPlotlyChart"] {
    background-color: #FFFFFF;
    border: 1px solid #E0E8E0;
    border-radius: 12px;
    padding: 8px;
}

.stDownloadButton button {
    background-color: #246B45;
    color: #FFFFFF !important;
    border: none;
    border-radius: 8px;
}

.stDownloadButton button:hover {
    background-color: #174B30;
    color: #FFFFFF !important;
}

hr {
    border-color: #DCE5DC;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# COLOUR PALETTE
# --------------------------------------------------
CROP_COLORS = [
    "#246B45", "#E3A72F", "#3977A8", "#C65D45",
    "#7B61A8", "#299D91", "#A66B3D", "#718096",
    "#D16B9A", "#789C42"
]

GREEN = "#246B45"
DARK_GREEN = "#205B3B"
GOLD = "#D5A02E"

# --------------------------------------------------
# CHART STYLING FUNCTION
# --------------------------------------------------
def style_chart(fig, height=430):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial, sans-serif",
            size=13,
            color="#26382C"
        ),
        title_font=dict(size=19, color=DARK_GREEN),
        title_x=0.02,
        height=height,
        margin=dict(l=25, r=25, t=75, b=45),
        legend=dict(
            bgcolor="rgba(255,255,255,0.85)",
            borderwidth=0
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_color="#26382C"
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#E8EEE8",
        zerolinecolor="#D5DFD5",
        automargin=True
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E8EEE8",
        zerolinecolor="#D5DFD5",
        automargin=True
    )

    return fig

# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.title("🌾 Agriculture Crop Marketplace Dashboard")
st.markdown(
    "Explore crop production, agricultural productivity, "
    "rainfall, fertilizer usage and market price patterns."
)

# --------------------------------------------------
# EXCEL WORKBOOK UPLOAD
# --------------------------------------------------
@st.cache_data
def load_data(file_bytes):
    from io import BytesIO
    return pd.read_excel(
        BytesIO(file_bytes),
        sheet_name="Agriculture Data"
    )

uploaded = st.file_uploader(
    "Upload your agriculture Excel workbook (.xlsx)",
    type=["xlsx"]
)

if uploaded is None:
    st.info(
        "Please upload your agriculture Excel workbook to view "
        "the dashboard and its charts."
    )

    st.markdown("""
    ### Dashboard features
    - Crop yield trends over time
    - Top 15 regions by average yield
    - Rainfall versus crop yield
    - Monthly market price trends
    - Price variability across crops
    - Production versus market price
    - Crop productivity comparison
    - Fertilizer usage versus yield

    Your workbook is not included in the GitHub repository.
    Upload it here when you want to analyse your data.
    """)
    st.stop()

try:
    df = load_data(uploaded.getvalue()).copy()
except Exception as error:
    st.error(
        "Unable to read the workbook. Please check that it is a "
        "valid Excel file with a sheet named 'Agriculture Data'."
    )
    st.exception(error)
    st.stop()

# --------------------------------------------------
# CHECK REQUIRED COLUMNS
# --------------------------------------------------
required_columns = [
    "State",
    "District",
    "Crop",
    "Year",
    "Month",
    "Season",
    "Market",
    "Yield_Tonnes_per_Hectare",
    "Production_Tonnes",
    "Annual_Rainfall_mm",
    "Fertilizer_NPK_kg_per_Hectare",
    "Modal_Price_Rs_per_Quintal"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error(
        "These required columns are missing from the workbook: "
        + ", ".join(missing_columns)
    )
    st.write("Available columns:", df.columns.tolist())
    st.stop()

# --------------------------------------------------
# DATA CLEANING
# --------------------------------------------------
numeric_columns = [
    "Year",
    "Month",
    "Yield_Tonnes_per_Hectare",
    "Production_Tonnes",
    "Annual_Rainfall_mm",
    "Fertilizer_NPK_kg_per_Hectare",
    "Modal_Price_Rs_per_Quintal"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

for col in ["State", "District", "Crop", "Season", "Market"]:
    df[col] = df[col].astype("string").str.strip()

# Production is repeated across market/month records.
# Remove those repeats for production-focused analysis.
production_df = df.drop_duplicates(
    subset=["State", "District", "Crop", "Year", "Season"]
).copy()

# Keep separate market records for price analysis.
market_df = df.drop_duplicates(
    subset=["State", "District", "Crop", "Year", "Month", "Market"]
).copy()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.title("Dashboard Filters")
st.sidebar.caption("Choose the data you want to explore.")

states = sorted(production_df["State"].dropna().unique().tolist())
crops = sorted(production_df["Crop"].dropna().unique().tolist())
seasons = sorted(production_df["Season"].dropna().unique().tolist())

selected_states = st.sidebar.multiselect(
    "State",
    states,
    default=states
)

selected_crops = st.sidebar.multiselect(
    "Crop",
    crops,
    default=crops
)

selected_seasons = st.sidebar.multiselect(
    "Season",
    seasons,
    default=seasons
)

filtered_production = production_df[
    production_df["State"].isin(selected_states)
    & production_df["Crop"].isin(selected_crops)
    & production_df["Season"].isin(selected_seasons)
].copy()

filtered_market = market_df[
    market_df["State"].isin(selected_states)
    & market_df["Crop"].isin(selected_crops)
    & market_df["Season"].isin(selected_seasons)
].copy()

available_years = sorted(
    filtered_production["Year"].dropna().astype(int).unique().tolist()
)

if available_years:
    if len(available_years) > 1:
        selected_years = st.sidebar.slider(
            "Year range",
            min_value=min(available_years),
            max_value=max(available_years),
            value=(min(available_years), max(available_years))
        )
        year_min, year_max = selected_years
    else:
        year_min = year_max = available_years[0]
        st.sidebar.caption(f"Year: {year_min}")

    filtered_production = filtered_production[
        filtered_production["Year"].between(year_min, year_max)
    ]

    filtered_market = filtered_market[
        filtered_market["Year"].between(year_min, year_max)
    ]

if filtered_production.empty:
    st.warning(
        "No production records match these filters. "
        "Please select different states, crops, seasons or years."
    )
    st.stop()

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------
st.subheader("Agriculture at a Glance")

avg_yield = filtered_production[
    "Yield_Tonnes_per_Hectare"
].mean()

total_production = filtered_production[
    "Production_Tonnes"
].sum(min_count=1)

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Production records",
    f"{len(filtered_production):,}"
)

k2.metric(
    "Crops",
    f"{filtered_production['Crop'].nunique():,}"
)

k3.metric(
    "States",
    f"{filtered_production['State'].nunique():,}"
)

k4.metric(
    "Average yield",
    f"{avg_yield:,.2f} t/ha" if pd.notna(avg_yield) else "N/A"
)

if pd.notna(total_production):
    st.caption(
        f"Total production across filtered production records: "
        f"{total_production:,.0f} tonnes"
    )

st.divider()

# --------------------------------------------------
# CHART 1: CROP YIELD TREND OVER YEARS
# --------------------------------------------------
st.subheader("1. Crop Yield Trend Over Years")

yield_trend = filtered_production.dropna(
    subset=["Year", "Yield_Tonnes_per_Hectare"]
).groupby("Year", as_index=False).agg(
    Average_Yield=("Yield_Tonnes_per_Hectare", "mean")
)

if not yield_trend.empty:
    fig = px.line(
        yield_trend,
        x="Year",
        y="Average_Yield",
        markers=True,
        title="Average Crop Yield by Year",
        labels={
            "Year": "Year",
            "Average_Yield": "Average yield (tonnes/hectare)"
        },
        color_discrete_sequence=[GREEN]
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    st.plotly_chart(style_chart(fig), use_container_width=True)
else:
    st.info("No yield data is available for this chart.")

# --------------------------------------------------
# CHART 2: TOP 15 REGIONS BY YIELD
# --------------------------------------------------
st.subheader("2. Top 15 Regions by Yield")

region_yield = filtered_production.dropna(
    subset=["State", "District", "Yield_Tonnes_per_Hectare"]
).groupby(
    ["State", "District"], as_index=False
).agg(
    Average_Yield=("Yield_Tonnes_per_Hectare", "mean")
)

region_yield["Region"] = (
    region_yield["District"].astype(str)
    + ", "
    + region_yield["State"].astype(str)
)

top_regions = region_yield.nlargest(
    15, "Average_Yield"
).sort_values("Average_Yield", ascending=True)

if not top_regions.empty:
    fig = px.bar(
        top_regions,
        x="Average_Yield",
        y="Region",
        orientation="h",
        title="15 Highest-Yielding Districts",
        labels={
            "Average_Yield": "Average yield (tonnes/hectare)",
            "Region": "District and state"
        },
        color="Average_Yield",
        color_continuous_scale=["#B9D9C2", GREEN]
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(style_chart(fig, 520), use_container_width=True)
else:
    st.info("No regional yield data is available.")

# --------------------------------------------------
# CHART 3: RAINFALL VS YIELD
# --------------------------------------------------
st.subheader("3. Rainfall vs Yield")

rainfall_data = filtered_production.dropna(
    subset=["Annual_Rainfall_mm", "Yield_Tonnes_per_Hectare", "Crop"]
)

if not rainfall_data.empty:
    fig = px.scatter(
        rainfall_data,
        x="Annual_Rainfall_mm",
        y="Yield_Tonnes_per_Hectare",
        color="Crop",
        color_discrete_sequence=CROP_COLORS,
        hover_data=["State", "District", "Year"],
        title="Relationship Between Rainfall and Crop Yield",
        labels={
            "Annual_Rainfall_mm": "Annual rainfall (mm)",
            "Yield_Tonnes_per_Hectare": "Yield (tonnes/hectare)"
        },
        opacity=0.8
    )
    fig.update_traces(marker=dict(size=9))
    st.plotly_chart(style_chart(fig), use_container_width=True)
else:
    st.info("No rainfall and yield data is available.")

# --------------------------------------------------
# CHART 4: MONTHLY MARKET PRICE TREND
# --------------------------------------------------
st.subheader("4. Monthly Market Price Trend")

price_data = filtered_market.dropna(
    subset=["Year", "Month", "Modal_Price_Rs_per_Quintal", "Crop"]
).copy()

price_data = price_data[
    price_data["Month"].between(1, 12)
    & price_data["Year"].between(1900, 2200)
]

if not price_data.empty:
    price_data["Date"] = pd.to_datetime(
        {
            "year": price_data["Year"].astype(int),
            "month": price_data["Month"].astype(int),
            "day": 1
        },
        errors="coerce"
    )

    monthly_prices = price_data.dropna(
        subset=["Date"]
    ).groupby(
        ["Date", "Crop"], as_index=False
    ).agg(
        Average_Price=("Modal_Price_Rs_per_Quintal", "mean")
    )

    fig = px.line(
        monthly_prices,
        x="Date",
        y="Average_Price",
        color="Crop",
        color_discrete_sequence=CROP_COLORS,
        title="Monthly Average Market Price by Crop",
        labels={
            "Date": "Month",
            "Average_Price": "Average price (₹/quintal)"
        }
    )
    fig.update_traces(line=dict(width=2.5))
    st.plotly_chart(style_chart(fig, 470), use_container_width=True)
else:
    st.info("No valid monthly market price data is available.")

# --------------------------------------------------
# CHART 5: PRICE VARIABILITY BY CROP
# --------------------------------------------------
st.subheader("5. Price Variability by Crop")

box_data = filtered_market.dropna(
    subset=["Crop", "Modal_Price_Rs_per_Quintal"]
)

if not box_data.empty:
    fig = px.box(
        box_data,
        x="Crop",
        y="Modal_Price_Rs_per_Quintal",
        color="Crop",
        color_discrete_sequence=CROP_COLORS,
        title="Distribution of Market Prices Across Crops",
        labels={
            "Crop": "Crop",
            "Modal_Price_Rs_per_Quintal": "Price (₹/quintal)"
        },
        points=False
    )
    fig.update_layout(showlegend=False)
    fig.update_xaxes(tickangle=-30)
    st.plotly_chart(style_chart(fig, 480), use_container_width=True)
else:
    st.info("No market price data is available.")

# --------------------------------------------------
# CHART 6: PRODUCTION VS MARKET PRICE
# --------------------------------------------------
st.subheader("6. Production vs Market Price")

comparison_data = filtered_market.dropna(
    subset=[
        "Crop",
        "Year",
        "Production_Tonnes",
        "Modal_Price_Rs_per_Quintal"
    ]
).groupby(
    ["Crop", "Year"], as_index=False
).agg(
    Production_Tonnes=("Production_Tonnes", "mean"),
    Average_Price=("Modal_Price_Rs_per_Quintal", "mean")
)

if not comparison_data.empty:
    fig = px.scatter(
        comparison_data,
        x="Production_Tonnes",
        y="Average_Price",
        color="Crop",
        color_discrete_sequence=CROP_COLORS,
        hover_data=["Year"],
        title="Crop Production Compared with Average Market Price",
        labels={
            "Production_Tonnes": "Production (tonnes)",
            "Average_Price": "Average price (₹/quintal)"
        },
        opacity=0.85
    )
    fig.update_traces(marker=dict(size=11))
    st.plotly_chart(style_chart(fig), use_container_width=True)
else:
    st.info("No matching production and price data is available.")

# --------------------------------------------------
# CHART 7: CROP PRODUCTIVITY COMPARISON
# --------------------------------------------------
st.subheader("7. Crop Productivity Comparison")

crop_productivity = filtered_production.dropna(
    subset=["Crop", "Yield_Tonnes_per_Hectare"]
).groupby(
    "Crop", as_index=False
).agg(
    Average_Yield=("Yield_Tonnes_per_Hectare", "mean")
).sort_values("Average_Yield", ascending=True)

if not crop_productivity.empty:
    fig = px.bar(
        crop_productivity,
        x="Average_Yield",
        y="Crop",
        orientation="h",
        title="Average Yield by Crop",
        labels={
            "Average_Yield": "Average yield (tonnes/hectare)",
            "Crop": "Crop"
        },
        color="Average_Yield",
        color_continuous_scale=["#B9D9C2", GREEN]
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(style_chart(fig, 450), use_container_width=True)
else:
    st.info("No crop productivity data is available.")

# --------------------------------------------------
# CHART 8: FERTILIZER USE VS YIELD
# --------------------------------------------------
st.subheader("8. Fertilizer Use vs Yield")

fertilizer_data = filtered_production.dropna(
    subset=[
        "Fertilizer_NPK_kg_per_Hectare",
        "Yield_Tonnes_per_Hectare",
        "Season"
    ]
).copy()

if (
    len(fertilizer_data) >= 5
    and fertilizer_data["Fertilizer_NPK_kg_per_Hectare"].nunique() > 1
):
    fertilizer_data["Fertilizer_Range"] = pd.qcut(
        fertilizer_data["Fertilizer_NPK_kg_per_Hectare"],
        q=5,
        duplicates="drop"
    )

    heatmap_data = fertilizer_data.pivot_table(
        index="Season",
        columns="Fertilizer_Range",
        values="Yield_Tonnes_per_Hectare",
        aggfunc="mean",
        observed=False
    )

    heatmap_data.columns = heatmap_data.columns.astype(str)

    fig = px.imshow(
        heatmap_data,
        aspect="auto",
        text_auto=".2f",
        color_continuous_scale=[
            "#F0F5EC", "#A9D1AE", GREEN
        ],
        title="Average Yield Across Fertilizer Usage Ranges",
        labels={
            "x": "Fertilizer usage range (kg/hectare)",
            "y": "Season",
            "color": "Average yield"
        }
    )

    st.plotly_chart(style_chart(fig, 400), use_container_width=True)
else:
    st.info(
        "There is not enough variation in fertilizer data to build "
        "the heatmap for the selected filters."
    )

# --------------------------------------------------
# FILTERED DATA TABLE AND DOWNLOAD
# --------------------------------------------------
st.divider()
st.subheader("Filtered Agriculture Data")

st.caption(
    f"Showing up to 500 of {len(filtered_market):,} filtered market records."
)

st.dataframe(
    filtered_market.head(500),
    use_container_width=True,
    hide_index=True
)

st.download_button(
    label="⬇ Download Filtered Data as CSV",
    data=filtered_market.to_csv(index=False).encode("utf-8"),
    file_name="agriculture_filtered_data.csv",
    mime="text/csv"
)

st.caption(
    "Agriculture Crop Marketplace Analytics | "
    "CA4 Capstone Business Analytics Project"
)
