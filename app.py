
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Agricultural Production and Market Analysis",
    page_icon="🌾",
    layout="wide",
)

# --------------------------------------------------
# PROFESSIONAL WHITE AND GREEN THEME
# --------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
    }

    [data-testid="stHeader"] {
        background-color: #FFFFFF;
    }

    [data-testid="stSidebar"] {
        background-color: #F7FAF7;
    }

    [data-testid="stSidebar"] * {
        color: #000000;
    }

    h1, h2, h3 {
        color: #14532D !important;
    }

    p, label, .stMarkdown, [data-testid="stCaptionContainer"] {
        color: #000000;
    }

    /* White interiors for dropdowns and multiselects */
    [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-color: #B7CDBB !important;
    }

    [data-baseweb="select"] input,
    [data-baseweb="select"] span {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* Dropdown options */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"],
    [role="option"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* Green focus and selection */
    [data-baseweb="select"] > div:focus-within {
        border-color: #176B3A !important;
        box-shadow: 0 0 0 1px #176B3A !important;
    }

    [role="option"][aria-selected="true"] {
        background-color: #DCEFE1 !important;
        color: #14532D !important;
    }

    /* KPI metric cards */
    [data-testid="stMetric"] {
        background-color: #F7FAF7;
        border: 1px solid #D6E5D8;
        border-radius: 10px;
        padding: 18px;
    }

    [data-testid="stMetricLabel"] {
        color: #14532D !important;
    }

    [data-testid="stMetricValue"] {
        color: #14532D !important;
    }

    [data-testid="stMetricDelta"] {
        color: #176B3A !important;
    }

    /* Data table: white background and dark text */
    [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
    }

    /* Download button */
    .stDownloadButton button {
        background-color: #176B3A;
        color: #FFFFFF;
        border: none;
    }

    .stDownloadButton button:hover {
        background-color: #14532D;
        color: #FFFFFF;
    }

    /* General dividers */
    hr {
        border-color: #D6E5D8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# CHART STYLING
# --------------------------------------------------
def style_chart(fig, height=430):
    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#000000"),
        title_font=dict(color="#14532D"),
        legend=dict(
            font=dict(color="#000000"),
            bgcolor="#FFFFFF",
        ),
        margin=dict(l=20, r=20, t=60, b=30),
    )

    fig.update_xaxes(
        title_font=dict(color="#000000"),
        tickfont=dict(color="#000000"),
        showgrid=True,
        gridcolor="#E5E7EB",
        zerolinecolor="#D1D5DB",
    )

    fig.update_yaxes(
        title_font=dict(color="#000000"),
        tickfont=dict(color="#000000"),
        showgrid=True,
        gridcolor="#E5E7EB",
        zerolinecolor="#D1D5DB",
    )

    return fig


CROP_COLORS = px.colors.qualitative.G10

# --------------------------------------------------
# MAIN HEADING
# --------------------------------------------------
st.title("Agricultural production and Market analysis")

st.caption(
    "Providing insights on the crop productivity and the agricultural market prices."
)

st.divider()

# --------------------------------------------------
# WORKBOOK UPLOAD
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload your agricultural data Excel workbook",
    type=["xlsx", "xls"],
)

if uploaded_file is None:
    st.info("Upload your Excel workbook to view the dashboard.")
    st.stop()

try:
    file_bytes = uploaded_file.getvalue()

    df = pd.read_excel(
        BytesIO(file_bytes),
        sheet_name="Agriculture Data",
    )

except Exception as error:
    st.error(
        "Unable to read the workbook or find the worksheet "
        "'Agriculture Data'. Please check your Excel file."
    )
    st.caption(f"Details: {error}")
    st.stop()

# --------------------------------------------------
# REQUIRED COLUMNS
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
    "Modal_Price_Rs_per_Quintal",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "The workbook is missing these required columns: "
        + ", ".join(missing_columns)
    )
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
    "Modal_Price_Rs_per_Quintal",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

for column in ["State", "District", "Crop", "Season", "Market"]:
    df[column] = df[column].astype("string").str.strip()

df = df.dropna(subset=["State", "District", "Crop", "Year"])
df["Year"] = df["Year"].astype(int)

# Production data: avoid repeating production records for each market.
production_df = df.drop_duplicates(
    subset=["State", "District", "Crop", "Year", "Season"]
).copy()

# Market data: retain separate market/month observations.
market_df = df.drop_duplicates(
    subset=["State", "District", "Crop", "Year", "Month", "Market"]
).copy()

# --------------------------------------------------
# SIDEBAR FILTERS
# State, Crop, Season: single-select dropdowns
# Year: multiselect
# --------------------------------------------------
st.sidebar.title("Dashboard Filters")

state_options = ["All"] + sorted(
    df["State"].dropna().unique().tolist()
)
crop_options = ["All"] + sorted(
    df["Crop"].dropna().unique().tolist()
)
season_options = ["All"] + sorted(
    df["Season"].dropna().unique().tolist()
)

year_options = sorted(
    df["Year"].dropna().astype(int).unique().tolist()
)

selected_state = st.sidebar.selectbox(
    "State",
    options=state_options,
    index=0,
)

selected_crop = st.sidebar.selectbox(
    "Crop",
    options=crop_options,
    index=0,
)

selected_season = st.sidebar.selectbox(
    "Season",
    options=season_options,
    index=0,
)

selected_years = st.sidebar.multiselect(
    "Year",
    options=year_options,
    default=year_options,
)

# --------------------------------------------------
# APPLY FILTERS CONSISTENTLY
# --------------------------------------------------
def apply_filters(data):
    result = data.copy()

    if selected_state != "All":
        result = result[result["State"] == selected_state]

    if selected_crop != "All":
        result = result[result["Crop"] == selected_crop]

    if selected_season != "All":
        result = result[result["Season"] == selected_season]

    result = result[result["Year"].isin(selected_years)]

    return result


filtered_production = apply_filters(production_df)
filtered_market = apply_filters(market_df)

# --------------------------------------------------
# KEY PERFORMANCE INDICATORS
# --------------------------------------------------
st.header("Key Performance Indicators")

total_production = filtered_production[
    "Production_Tonnes"
].sum(min_count=1)

average_yield = filtered_production[
    "Yield_Tonnes_per_Hectare"
].mean()

average_market_price = filtered_market[
    "Modal_Price_Rs_per_Quintal"
].mean()

average_rainfall = filtered_production[
    "Annual_Rainfall_mm"
].mean()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    production_value = (
        f"{total_production / 1_000_000:,.2f}M"
        if pd.notna(total_production)
        else "N/A"
    )
    st.metric("Total Production", production_value)
    st.caption("Tonnes")

with kpi2:
    yield_value = (
        f"{average_yield:,.2f}"
        if pd.notna(average_yield)
        else "N/A"
    )
    st.metric("Average Yield", yield_value)
    st.caption("Tonnes per hectare")

with kpi3:
    price_value = (
        f"₹{average_market_price:,.2f}"
        if pd.notna(average_market_price)
        else "N/A"
    )
    st.metric("Average Market Price", price_value)
    st.caption("Per quintal")

with kpi4:
    rainfall_value = (
        f"{average_rainfall:,.2f}"
        if pd.notna(average_rainfall)
        else "N/A"
    )
    st.metric("Average Rainfall", rainfall_value)
    st.caption("Millimeters")

st.divider()

# --------------------------------------------------
# AGRICULTURAL INSIGHTS
# --------------------------------------------------
st.header("Agricultural insights")

if filtered_production.empty:
    st.warning(
        "No production records match the selected filters. "
        "Please change your filter selections."
    )
    st.stop()

# 1. Yield trend over the years
st.subheader("1. Agricultural yield trend")

yield_trend = (
    filtered_production
    .groupby("Year", as_index=False)["Yield_Tonnes_per_Hectare"]
    .mean()
    .sort_values("Year")
)

fig1 = px.line(
    yield_trend,
    x="Year",
    y="Yield_Tonnes_per_Hectare",
    markers=True,
    title="Average Crop Yield Over Time",
    labels={
        "Year": "Year",
        "Yield_Tonnes_per_Hectare": "Yield (tonnes per hectare)",
    },
)
fig1.update_traces(line=dict(color="#176B3A", width=3))
st.plotly_chart(style_chart(fig1), use_container_width=True)

# 2. Top 15 districts by yield
st.subheader("2. Top-performing districts")

district_yield = (
    filtered_production
    .groupby(["State", "District"], as_index=False)
    ["Yield_Tonnes_per_Hectare"]
    .mean()
    .sort_values("Yield_Tonnes_per_Hectare", ascending=False)
    .head(15)
)

fig2 = px.bar(
    district_yield.sort_values("Yield_Tonnes_per_Hectare"),
    x="Yield_Tonnes_per_Hectare",
    y="District",
    color="State",
    orientation="h",
    title="Top 15 Districts by Average Yield",
    labels={
        "Yield_Tonnes_per_Hectare": "Yield (tonnes per hectare)",
        "District": "District",
        "State": "State",
    },
    color_discrete_sequence=CROP_COLORS,
)
st.plotly_chart(style_chart(fig2), use_container_width=True)

# 3. Rainfall versus yield
st.subheader("3. Rainfall and crop yield")

rainfall_data = filtered_production.dropna(
    subset=["Annual_Rainfall_mm", "Yield_Tonnes_per_Hectare"]
)

fig3 = px.scatter(
    rainfall_data,
    x="Annual_Rainfall_mm",
    y="Yield_Tonnes_per_Hectare",
    color="Crop",
    title="Annual Rainfall vs Crop Yield",
    labels={
        "Annual_Rainfall_mm": "Annual Rainfall (mm)",
        "Yield_Tonnes_per_Hectare": "Yield (tonnes per hectare)",
    },
    color_discrete_sequence=CROP_COLORS,
)
st.plotly_chart(style_chart(fig3), use_container_width=True)

# 4. Price variability by crop
st.subheader("4. Market price comparison by crop")

if not filtered_market.empty:
    crop_prices = (
        filtered_market
        .groupby("Crop", as_index=False)["Modal_Price_Rs_per_Quintal"]
        .mean()
        .sort_values("Modal_Price_Rs_per_Quintal", ascending=False)
    )

    fig4 = px.bar(
        crop_prices,
        x="Crop",
        y="Modal_Price_Rs_per_Quintal",
        color="Crop",
        title="Average Market Price by Crop",
        labels={
            "Crop": "Crop",
            "Modal_Price_Rs_per_Quintal": "Price (₹ per quintal)",
        },
        color_discrete_sequence=CROP_COLORS,
    )
    st.plotly_chart(style_chart(fig4), use_container_width=True)
else:
    st.info("No market price records match the selected filters.")

# 5. Production versus market price
st.subheader("5. Production and market price relationship")

if not filtered_market.empty:
    production_price = (
        filtered_market
        .groupby("Crop", as_index=False)
        .agg(
            Production_Tonnes=("Production_Tonnes", "mean"),
            Modal_Price_Rs_per_Quintal=(
                "Modal_Price_Rs_per_Quintal", "mean"
            ),
        )
        .dropna(
            subset=[
                "Production_Tonnes",
                "Modal_Price_Rs_per_Quintal",
            ]
        )
    )

    fig5 = px.scatter(
        production_price,
        x="Production_Tonnes",
        y="Modal_Price_Rs_per_Quintal",
        color="Crop",
        size="Production_Tonnes",
        title="Average Production vs Average Market Price by Crop",
        labels={
            "Production_Tonnes": "Production (tonnes)",
            "Modal_Price_Rs_per_Quintal": "Price (₹ per quintal)",
        },
        color_discrete_sequence=CROP_COLORS,
    )
    st.plotly_chart(style_chart(fig5), use_container_width=True)
else:
    st.info("No market records are available for this comparison.")

# 6. Crop productivity comparison
st.subheader("6. Crop productivity comparison")

crop_productivity = (
    filtered_production
    .groupby("Crop", as_index=False)["Yield_Tonnes_per_Hectare"]
    .mean()
    .sort_values("Yield_Tonnes_per_Hectare", ascending=False)
)

fig6 = px.bar(
    crop_productivity,
    x="Crop",
    y="Yield_Tonnes_per_Hectare",
    color="Crop",
    title="Average Yield by Crop",
    labels={
        "Crop": "Crop",
        "Yield_Tonnes_per_Hectare": "Yield (tonnes per hectare)",
    },
    color_discrete_sequence=CROP_COLORS,
)
st.plotly_chart(style_chart(fig6), use_container_width=True)

# 7. Fertilizer use versus yield
st.subheader("7. Fertilizer use and yield")

fertilizer_data = filtered_production.dropna(
    subset=[
        "Fertilizer_NPK_kg_per_Hectare",
        "Yield_Tonnes_per_Hectare",
    ]
)

fig7 = px.scatter(
    fertilizer_data,
    x="Fertilizer_NPK_kg_per_Hectare",
    y="Yield_Tonnes_per_Hectare",
    color="Crop",
    title="Fertilizer Use vs Crop Yield",
    labels={
        "Fertilizer_NPK_kg_per_Hectare": "Fertilizer NPK (kg per hectare)",
        "Yield_Tonnes_per_Hectare": "Yield (tonnes per hectare)",
    },
    color_discrete_sequence=CROP_COLORS,
)
st.plotly_chart(style_chart(fig7), use_container_width=True)

# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------
st.divider()
st.header("Business insights")

yield_summary = (
    filtered_production
    .groupby("Crop")["Yield_Tonnes_per_Hectare"]
    .mean()
    .dropna()
)

price_summary = (
    filtered_market
    .groupby("Crop")["Modal_Price_Rs_per_Quintal"]
    .mean()
    .dropna()
)

district_summary = (
    filtered_production
    .groupby(["State", "District"])["Yield_Tonnes_per_Hectare"]
    .mean()
    .dropna()
)

insight1, insight2 = st.columns(2)

with insight1:
    st.subheader("Crop productivity")

    if not yield_summary.empty:
        top_crop = yield_summary.idxmax()
        lowest_crop = yield_summary.idxmin()

        st.write(
            f"**Highest average yield:** {top_crop} "
            f"({yield_summary.max():,.2f} tonnes per hectare)"
        )
        st.write(
            f"**Lowest average yield:** {lowest_crop} "
            f"({yield_summary.min():,.2f} tonnes per hectare)"
        )

    if not district_summary.empty:
        best_district = district_summary.idxmax()
        st.write(
            f"**Highest-yielding district:** {best_district[1]}, "
            f"{best_district[0]} "
            f"({district_summary.max():,.2f} tonnes per hectare)"
        )

with insight2:
    st.subheader("Market and resource insights")

    if not price_summary.empty:
        highest_price_crop = price_summary.idxmax()
        st.write(
            f"**Highest average market price:** {highest_price_crop} "
            f"(₹{price_summary.max():,.2f} per quintal)"
        )

    rainfall_corr = filtered_production[
        ["Annual_Rainfall_mm", "Yield_Tonnes_per_Hectare"]
    ].corr().iloc[0, 1]

    fertilizer_corr = filtered_production[
        [
            "Fertilizer_NPK_kg_per_Hectare",
            "Yield_Tonnes_per_Hectare",
        ]
    ].corr().iloc[0, 1]

    if pd.notna(rainfall_corr):
        st.write(
            f"**Rainfall-yield correlation:** {rainfall_corr:.2f}"
        )

    if pd.notna(fertilizer_corr):
        st.write(
            f"**Fertilizer-yield correlation:** {fertilizer_corr:.2f}"
        )

st.caption(
    "Correlations indicate relationships, not causation. "
    "Market price is not the same as profit."
)

# --------------------------------------------------
# FILTERED DATA TABLE
# --------------------------------------------------
st.divider()
st.header("Filtered agricultural data")

st.dataframe(
    filtered_market.head(500),
    use_container_width=True,
    hide_index=True,
)

csv_data = filtered_market.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download filtered data as CSV",
    data=csv_data,
    file_name="filtered_agricultural_data.csv",
    mime="text/csv",
)
