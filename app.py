
import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Agriculture Analytics Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. PROFESSIONAL WHITE AND GREEN THEME
# =========================================================
st.markdown("""
<style>
.stApp {
    background-color: #F7F9F6;
    color: #000000;
}

[data-testid="stHeader"] {
    background-color: #F7F9F6;
}

h1, h2, h3, h4 {
    color: #205B3B !important;
}

.stApp p,
.stApp label,
.stApp [data-testid="stMarkdownContainer"] {
    color: #000000;
}

[data-testid="stSidebar"] {
    background-color: #EAF1E9;
}

[data-testid="stSidebar"] * {
    color: #000000;
}

div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #DCE7DC;
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 2px 8px rgba(32, 91, 59, 0.06);
}

[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p {
    color: #000000 !important;
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
    border-radius: 8px;
    border: none;
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

# =========================================================
# 3. COLOURS AND CHART STYLE
# =========================================================
GREEN = "#246B45"
DARK_GREEN = "#205B3B"

CROP_COLORS = [
    "#246B45", "#E3A72F", "#3977A8", "#C65D45",
    "#7B61A8", "#299D91", "#A66B3D", "#718096",
    "#D16B9A", "#789C42", "#557C9B", "#B07D4F"
]


def style_chart(fig, height=430):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial, sans-serif",
            size=13,
            color="#000000"
        ),
        title_font=dict(size=19, color=DARK_GREEN),
        title_x=0.02,
        height=height,
        margin=dict(l=25, r=25, t=75, b=45),
        legend=dict(
            font=dict(color="#000000"),
            bgcolor="rgba(255,255,255,0.9)"
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_color="#000000"
        )
    )

    fig.update_xaxes(
        title_font=dict(color="#000000"),
        tickfont=dict(color="#000000"),
        showgrid=True,
        gridcolor="#E8EEE8",
        zerolinecolor="#D5DFD5",
        automargin=True
    )

    fig.update_yaxes(
        title_font=dict(color="#000000"),
        tickfont=dict(color="#000000"),
        showgrid=True,
        gridcolor="#E8EEE8",
        zerolinecolor="#D5DFD5",
        automargin=True
    )

    return fig


# =========================================================
# 4. TITLE AND INTRODUCTION
# =========================================================
st.title("🌾 Agriculture Crop Marketplace Dashboard")

st.markdown(
    "An interactive business analytics dashboard exploring "
    "crop productivity, regional performance, market prices, "
    "rainfall and fertilizer usage."
)

# =========================================================
# 5. EXCEL UPLOAD
# =========================================================
@st.cache_data
def load_data(file_bytes):
    from io import BytesIO

    return pd.read_excel(
        BytesIO(file_bytes),
        sheet_name="Agriculture Data"
    )


uploaded = st.file_uploader(
    "Upload your agriculture Excel workbook",
    type=["xlsx"]
)

if uploaded is None:
    st.info(
        "Upload your Excel workbook to view the dashboard. "
        "The workbook is not stored in this GitHub repository."
    )

    st.markdown("""
    ### Dashboard features

    - Crop yield trends over time
    - Top 15 regions by average yield
    - Rainfall versus crop yield
    - Market price variability by crop
    - Production versus market price
    - Crop productivity comparison
    - Fertilizer use versus yield
    - Business insights based on your filters
    """)

    st.stop()

try:
    df = load_data(uploaded.getvalue()).copy()

except Exception as error:
    st.error(
        "Unable to read the workbook. Make sure it is a valid "
        "Excel file with a sheet named 'Agriculture Data'."
    )
    st.exception(error)
    st.stop()


# =========================================================
# 6. VALIDATE AND CLEAN DATA
# =========================================================
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
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "The workbook is missing these required columns: "
        + ", ".join(missing_columns)
    )
    st.write("Columns found in workbook:", df.columns.tolist())
    st.stop()

numeric_columns = [
    "Year",
    "Month",
    "Yield_Tonnes_per_Hectare",
    "Production_Tonnes",
    "Annual_Rainfall_mm",
    "Fertilizer_NPK_kg_per_Hectare",
    "Modal_Price_Rs_per_Quintal"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

for column in ["State", "District", "Crop", "Season", "Market"]:
    df[column] = df[column].astype("string").str.strip()

# Production data can repeat across months and markets.
production_df = df.drop_duplicates(
    subset=["State", "District", "Crop", "Year", "Season"]
).copy()

# Preserve distinct market/month records for price analysis.
market_df = df.drop_duplicates(
    subset=["State", "District", "Crop", "Year", "Month", "Market"]
).copy()


# =========================================================
# 7. SIDEBAR FILTERS
# =========================================================
st.sidebar.title("Dashboard Filters")
st.sidebar.caption("Change the selections to explore your data.")

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
        year_range = st.sidebar.slider(
            "Year range",
            min_value=min(available_years),
            max_value=max(available_years),
            value=(min(available_years), max(available_years))
        )

        year_min, year_max = year_range

    else:
        year_min = year_max = available_years[0]
        st.sidebar.caption(f"Selected year: {year_min}")

    filtered_production = filtered_production[
        filtered_production["Year"].between(year_min, year_max)
    ]

    filtered_market = filtered_market[
        filtered_market["Year"].between(year_min, year_max)
    ]

if filtered_production.empty:
    st.warning(
        "No records match your filters. Change the state, crop, "
        "season or year selection."
    )
    st.stop()


# =========================================================
# 8. KEY PERFORMANCE INDICATORS
# =========================================================
st.subheader("Agriculture at a Glance")

average_yield = filtered_production[
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
    f"{average_yield:,.2f} t/ha"
    if pd.notna(average_yield) else "N/A"
)

if pd.notna(total_production):
    st.caption(
        f"Sum of production across filtered records: "
        f"{total_production:,.0f} tonnes"
    )

st.divider()


# =========================================================
# CHART 1: CROP YIELD TREND
# =========================================================
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


# =========================================================
# CHART 2: TOP 15 REGIONS BY YIELD
# =========================================================
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
).sort_values("Average_Yield")

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
    st.plotly_chart(
        style_chart(fig, 520),
        use_container_width=True
    )

else:
    st.info("No regional yield data is available.")


# =========================================================
# CHART 3: RAINFALL VERSUS YIELD
# =========================================================
st.subheader("3. Rainfall vs Yield")

rainfall_data = filtered_production.dropna(
    subset=[
        "Annual_Rainfall_mm",
        "Yield_Tonnes_per_Hectare",
        "Crop"
    ]
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


# =========================================================
# CHART 4: PRICE VARIABILITY BY CROP
# Monthly price trend has been removed.
# =========================================================
st.subheader("4. Price Variability by Crop")

price_data = filtered_market.dropna(
    subset=["Crop", "Modal_Price_Rs_per_Quintal"]
)

if not price_data.empty:
    fig = px.box(
        price_data,
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
    st.plotly_chart(
        style_chart(fig, 480),
        use_container_width=True
    )

else:
    st.info("No market price data is available.")


# =========================================================
# CHART 5: PRODUCTION VERSUS MARKET PRICE
# =========================================================
st.subheader("5. Production vs Market Price")

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
        title="Crop Production Compared with Market Price",
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


# =========================================================
# CHART 6: CROP PRODUCTIVITY
# =========================================================
st.subheader("6. Crop Productivity Comparison")

crop_productivity = filtered_production.dropna(
    subset=["Crop", "Yield_Tonnes_per_Hectare"]
).groupby(
    "Crop", as_index=False
).agg(
    Average_Yield=("Yield_Tonnes_per_Hectare", "mean")
).sort_values("Average_Yield")

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
    st.plotly_chart(
        style_chart(fig, 450),
        use_container_width=True
    )

else:
    st.info("No crop productivity data is available.")


# =========================================================
# CHART 7: FERTILIZER USE VERSUS YIELD
# =========================================================
st.subheader("7. Fertilizer Use vs Yield")

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
            "x": "Fertilizer range (kg/hectare)",
            "y": "Season",
            "color": "Average yield"
        }
    )

    st.plotly_chart(
        style_chart(fig, 400),
        use_container_width=True
    )

else:
    st.info(
        "There is not enough variation in fertilizer data to "
        "create a heatmap for the selected filters."
    )


# =========================================================
# 9. BUSINESS INSIGHTS
# =========================================================
st.divider()
st.header("📊 Business Insights")

st.caption(
    "Insights are recalculated from the currently selected "
    "states, crops, seasons and years."
)

# Crop productivity ranking
crop_insight = filtered_production.dropna(
    subset=["Crop", "Yield_Tonnes_per_Hectare"]
).groupby("Crop")["Yield_Tonnes_per_Hectare"].mean().sort_values(
    ascending=False
)

# District productivity ranking
region_insight = filtered_production.dropna(
    subset=["State", "District", "Yield_Tonnes_per_Hectare"]
).groupby(
    ["State", "District"]
)["Yield_Tonnes_per_Hectare"].mean().sort_values(
    ascending=False
)

# Average modal price by crop
price_insight = filtered_market.dropna(
    subset=["Crop", "Modal_Price_Rs_per_Quintal"]
).groupby("Crop")["Modal_Price_Rs_per_Quintal"].mean().sort_values(
    ascending=False
)

# KPI insight cards
i1, i2, i3 = st.columns(3)

if not crop_insight.empty:
    i1.metric(
        "Highest-yielding crop",
        str(crop_insight.index[0]),
        f"{crop_insight.iloc[0]:.2f} tonnes/ha"
    )
else:
    i1.metric("Highest-yielding crop", "N/A")

if not region_insight.empty:
    best_region = region_insight.index[0]

    i2.metric(
        "Highest-yielding district",
        str(best_region[1]),
        str(best_region[0])
    )
else:
    i2.metric("Highest-yielding district", "N/A")

if not price_insight.empty:
    i3.metric(
        "Highest average-price crop",
        str(price_insight.index[0]),
        f"₹{price_insight.iloc[0]:,.0f}/quintal"
    )
else:
    i3.metric("Highest average-price crop", "N/A")

st.subheader("Key Findings")

# Insight 1: Highest productivity
if not crop_insight.empty:
    st.markdown(
        f"**1. Crop productivity:** "
        f"{crop_insight.index[0]} has the highest average yield "
        f"among the selected crops, at "
        f"{crop_insight.iloc[0]:.2f} tonnes per hectare. "
        "Its cultivation practices may be worth investigating "
        "for potential productivity lessons."
    )

# Insight 2: Lowest productivity
if len(crop_insight) >= 2:
    st.markdown(
        f"**2. Improvement opportunity:** "
        f"{crop_insight.index[-1]} has the lowest average yield "
        f"among the selected crops, at "
        f"{crop_insight.iloc[-1]:.2f} tonnes per hectare. "
        "Review growing conditions, input use and production "
        "costs before choosing an intervention."
    )

# Insight 3: Regional benchmarking
if not region_insight.empty:
    best_region = region_insight.index[0]

    st.markdown(
        f"**3. Regional benchmarking:** "
        f"{best_region[1]}, {best_region[0]}, has the highest "
        "average yield among the selected districts. "
        "Compare its growing conditions and farming practices "
        "with lower-yielding districts."
    )

# Insight 4: Market prices
if not price_insight.empty:
    st.markdown(
        f"**4. Market positioning:** "
        f"{price_insight.index[0]} has the highest average modal "
        f"price in the selected data, at "
        f"₹{price_insight.iloc[0]:,.2f} per quintal. "
        "A higher selling price alone does not mean a higher profit."
    )

# Insight 5: Rainfall and yield association
rainfall_insight = filtered_production.dropna(
    subset=["Annual_Rainfall_mm", "Yield_Tonnes_per_Hectare"]
)

if len(rainfall_insight) >= 3:
    rainfall_corr = rainfall_insight[
        "Annual_Rainfall_mm"
    ].corr(
        rainfall_insight["Yield_Tonnes_per_Hectare"]
    )

    if pd.notna(rainfall_corr):
        if rainfall_corr >= 0.3:
            rainfall_message = "a positive linear association"
        elif rainfall_corr <= -0.3:
            rainfall_message = "a negative linear association"
        else:
            rainfall_message = "a weak linear association"

        st.markdown(
            f"**5. Rainfall and yield:** The correlation is "
            f"{rainfall_corr:.2f}, indicating {rainfall_message} "
            "in the selected data. Correlation does not prove "
            "that rainfall caused the observed yield pattern."
        )

# Insight 6: Fertilizer and yield association
fertilizer_insight = filtered_production.dropna(
    subset=[
        "Fertilizer_NPK_kg_per_Hectare",
        "Yield_Tonnes_per_Hectare"
    ]
)

if (
    len(fertilizer_insight) >= 3
    and fertilizer_insight[
        "Fertilizer_NPK_kg_per_Hectare"
    ].nunique() > 1
):
    fertilizer_corr = fertilizer_insight[
        "Fertilizer_NPK_kg_per_Hectare"
    ].corr(
        fertilizer_insight["Yield_Tonnes_per_Hectare"]
    )

    if pd.notna(fertilizer_corr):
        st.markdown(
            f"**6. Fertilizer and yield:** The correlation is "
            f"{fertilizer_corr:.2f}. Treat this as an initial "
            "association for further analysis, not evidence that "
            "increasing fertilizer use will necessarily improve yield."
        )

# Business limitations
st.info(
    "Business recommendation: use these findings to identify "
    "areas for further investigation. To determine crop profitability, "
    "additional information on cultivation costs, selling quantities, "
    "revenue and other relevant factors is required."
)


# =========================================================
# 10. FILTERED DATA AND CSV DOWNLOAD
# =========================================================
st.divider()
st.subheader("Filtered Agriculture Data")

st.caption(
    f"Showing up to 500 of {len(filtered_market):,} filtered "
    "market records."
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
