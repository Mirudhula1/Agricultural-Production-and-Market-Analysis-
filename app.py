
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Agricultural Production And Market Analysis",
    page_icon="🌿",
    layout="wide",
)

# =========================================================
# 2. GREEN COLOUR PALETTE
# =========================================================
PALETTE = {
    "background": "#FFFFFF",
    "surface": "#F7F9F5",
    "pale_green": "#E8EFE3",
    "sage": "#C6D5BC",
    "sage_mid": "#A8BE9B",
    "green": "#66865B",
    "green_mid": "#54764A",
    "green_text": "#476440",
    "border": "#D8E2D2",
    "grid": "#E8EDE5",
    "text": "#40533D",
    "muted_text": "#6C7D66",
    "white": "#FFFFFF",
}

CROP_COLORS = [
    "#A8BE9B",
    "#8FAA83",
    "#C6D5BC",
    "#B6C9A9",
    "#D5E0CC",
    "#92AD87",
    "#BBCDB0",
    "#DCE6D5",
    "#78966D",
    "#E4EBDD",
]

# =========================================================
# 3. GLOBAL STYLING
# =========================================================
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(180deg, #FFFFFF 0%, #F7F9F5 100%);
        color: {PALETTE["text"]};
    }}

    [data-testid="stHeader"] {{
        background-color: {PALETTE["background"]};
    }}

    [data-testid="stSidebar"] {{
        background-color: {PALETTE["surface"]};
        border-right: 1px solid {PALETTE["border"]};
    }}

    h1, h2, h3, h4 {{
        color: {PALETTE["green_text"]} !important;
        letter-spacing: -0.02em;
    }}

    p, label, li, .stMarkdown,
    [data-testid="stCaptionContainer"] {{
        color: {PALETTE["text"]};
    }}

    [data-baseweb="select"] > div {{
        background-color: {PALETTE["surface"]} !important;
        border: 1px solid {PALETTE["border"]} !important;
        box-shadow: none !important;
        border-radius: 8px !important;
    }}

    [data-baseweb="select"] input {{
        color: {PALETTE["green_text"]} !important;
        -webkit-text-fill-color: {PALETTE["green_text"]} !important;
        caret-color: {PALETTE["green_text"]} !important;
    }}

    [data-baseweb="select"] span,
    [data-baseweb="select"] div {{
        color: {PALETTE["green_text"]};
    }}

    [data-baseweb="select"] svg {{
        fill: {PALETTE["green_text"]} !important;
        color: {PALETTE["green_text"]} !important;
    }}

    [data-baseweb="tag"] {{
        background-color: {PALETTE["pale_green"]} !important;
        border: 1px solid {PALETTE["border"]} !important;
        border-radius: 6px !important;
    }}

    [data-baseweb="tag"] *,
    [data-baseweb="tag"] span {{
        color: {PALETTE["green_text"]} !important;
        -webkit-text-fill-color: {PALETTE["green_text"]} !important;
    }}

    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"] {{
        background-color: {PALETTE["surface"]} !important;
        border: 1px solid {PALETTE["border"]} !important;
    }}

    [role="option"] {{
        background-color: {PALETTE["surface"]} !important;
        color: {PALETTE["green_text"]} !important;
    }}

    [role="option"] *,
    [role="option"] span {{
        color: {PALETTE["green_text"]} !important;
        -webkit-text-fill-color: {PALETTE["green_text"]} !important;
    }}

    [role="option"]:hover,
    [role="option"][aria-selected="true"] {{
        background-color: {PALETTE["pale_green"]} !important;
        color: {PALETTE["green_text"]} !important;
    }}

    [data-testid="stMetric"] {{
        background: linear-gradient(135deg, #F7F9F5 0%, #E8EFE3 100%);
        border: 1px solid {PALETTE["border"]};
        border-radius: 14px;
        padding: 18px 16px;
        box-shadow: 0 3px 12px rgba(71, 100, 64, 0.06);
    }}

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricValue"] {{
        color: {PALETTE["green_text"]} !important;
    }}

    .stDownloadButton button {{
        background-color: {PALETTE["pale_green"]};
        color: {PALETTE["green_text"]};
        border: 1px solid {PALETTE["border"]};
        border-radius: 8px;
    }}

    .stDownloadButton button:hover {{
        background-color: {PALETTE["sage"]};
        color: {PALETTE["green_text"]};
        border-color: {PALETTE["sage_mid"]};
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid {PALETTE["border"]};
        border-radius: 8px;
        overflow: hidden;
    }}

    [data-testid="stAlert"] {{
        background-color: {PALETTE["surface"]};
        border-color: {PALETTE["border"]};
        color: {PALETTE["green_text"]};
        border-radius: 10px;
    }}

    hr {{
        border-color: {PALETTE["border"]};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 4. CHART STYLING
# =========================================================
def style_chart(fig, height=430):
    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor=PALETTE["background"],
        plot_bgcolor=PALETTE["background"],
        font=dict(
            family="Arial, sans-serif",
            color=PALETTE["green_text"],
            size=12,
        ),
        title_font=dict(
            color=PALETTE["green_text"],
            size=17,
        ),
        legend=dict(
            font=dict(color=PALETTE["green_text"]),
            bgcolor=PALETTE["background"],
            bordercolor=PALETTE["border"],
            borderwidth=0,
        ),
        margin=dict(l=25, r=25, t=65, b=35),
        colorway=CROP_COLORS,
    )

    fig.update_xaxes(
        title_font=dict(color=PALETTE["green_text"]),
        tickfont=dict(color=PALETTE["green_text"]),
        showgrid=True,
        gridcolor=PALETTE["grid"],
        zerolinecolor=PALETTE["border"],
        linecolor=PALETTE["border"],
    )

    fig.update_yaxes(
        title_font=dict(color=PALETTE["green_text"]),
        tickfont=dict(color=PALETTE["green_text"]),
        showgrid=True,
        gridcolor=PALETTE["grid"],
        zerolinecolor=PALETTE["border"],
        linecolor=PALETTE["border"],
    )

    return fig


def show_chart(fig):
    st.plotly_chart(
        style_chart(fig),
        use_container_width=True,
        config={"displaylogo": False},
    )


# =========================================================
# 5. DASHBOARD HEADING
# =========================================================
st.title("Agricultural Production And Market Analysis")
st.caption(
    "Insights Into Crop Productivity, Agricultural Inputs, And Market Prices"
)
st.divider()

# =========================================================
# 6. UPLOAD EXCEL WORKBOOK
# =========================================================
uploaded_file = st.file_uploader(
    "Upload Your Agricultural Data Excel Workbook",
    type=["xlsx", "xls"],
)

if uploaded_file is None:
    st.info("Upload your Excel workbook to view the dashboard.")
    st.stop()

try:
    df = pd.read_excel(
        BytesIO(uploaded_file.getvalue()),
        sheet_name="Agriculture Data",
    )
except Exception as error:
    st.error(
        "The workbook could not be read. Check that it contains a worksheet "
        "named 'Agriculture Data' and that the file is a valid Excel workbook."
    )
    st.caption(f"Details: {error}")
    st.stop()

# =========================================================
# 7. VALIDATE AND CLEAN DATA
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
    "Modal_Price_Rs_per_Quintal",
]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(
        "The workbook is missing these required columns: "
        + ", ".join(missing_columns)
    )
    st.stop()

numeric_columns = [
    "Year",
    "Month",
    "Yield_Tonnes_per_Hectare",
    "Production_Tonnes",
    "Annual_Rainfall_mm",
    "Fertilizer_NPK_kg_per_Hectare",
    "Modal_Price_Rs_per_Quintal",
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

for col in ["State", "District", "Crop", "Season", "Market"]:
    df[col] = df[col].astype("string").str.strip()

df = df.dropna(subset=["State", "District", "Crop", "Year"])

if df.empty:
    st.warning("The uploaded workbook has no usable records.")
    st.stop()

df["Year"] = df["Year"].astype(int)

production_df = df.drop_duplicates(
    subset=["State", "District", "Crop", "Year", "Season"]
).copy()

market_df = df.drop_duplicates(
    subset=["State", "District", "Crop", "Year", "Month", "Market"]
).copy()

# =========================================================
# 8. DASHBOARD FILTERS
# =========================================================
st.sidebar.title("Dashboard Filters")

state_options = ["All"] + sorted(df["State"].dropna().unique().tolist())
crop_options = ["All"] + sorted(df["Crop"].dropna().unique().tolist())
season_options = ["All"] + sorted(df["Season"].dropna().unique().tolist())
year_options = sorted(df["Year"].dropna().unique().astype(int).tolist())

selected_state = st.sidebar.selectbox("State", state_options, index=0)
selected_crop = st.sidebar.selectbox("Crop", crop_options, index=0)
selected_season = st.sidebar.selectbox("Season", season_options, index=0)
selected_years = st.sidebar.multiselect(
    "Year",
    options=year_options,
    default=year_options,
)


def apply_filters(data):
    result = data.copy()

    if selected_state != "All":
        result = result[result["State"] == selected_state]

    if selected_crop != "All":
        result = result[result["Crop"] == selected_crop]

    if selected_season != "All":
        result = result[result["Season"] == selected_season]

    return result[result["Year"].isin(selected_years)]


filtered_production = apply_filters(production_df)
filtered_market = apply_filters(market_df)

# =========================================================
# 9. KEY PERFORMANCE INDICATORS
# =========================================================
st.header("Key Performance Indicators")

total_production = filtered_production["Production_Tonnes"].sum(min_count=1)
average_yield = filtered_production["Yield_Tonnes_per_Hectare"].mean()
average_market_price = filtered_market["Modal_Price_Rs_per_Quintal"].mean()
average_rainfall = filtered_production["Annual_Rainfall_mm"].mean()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    value = (
        f"{total_production / 1_000_000:,.2f}M"
        if pd.notna(total_production)
        else "N/A"
    )
    st.metric("Total Production", value)
    st.caption("Tonnes")

with kpi2:
    value = f"{average_yield:,.2f}" if pd.notna(average_yield) else "N/A"
    st.metric("Average Yield", value)
    st.caption("Tonnes Per Hectare")

with kpi3:
    value = (
        f"₹{average_market_price:,.2f}"
        if pd.notna(average_market_price)
        else "N/A"
    )
    st.metric("Average Market Price", value)
    st.caption("Per Quintal")

with kpi4:
    value = (
        f"{average_rainfall:,.2f}"
        if pd.notna(average_rainfall)
        else "N/A"
    )
    st.metric("Average Rainfall", value)
    st.caption("Millimeters")

st.divider()

# =========================================================
# 10. PREPARE HEATMAP DATA AND CORRELATION
# =========================================================
heatmap_columns = {
    "Yield_Tonnes_per_Hectare": "Crop Yield",
    "Production_Tonnes": "Production",
    "Annual_Rainfall_mm": "Rainfall",
    "Fertilizer_NPK_kg_per_Hectare": "Fertilizer",
    "Modal_Price_Rs_per_Quintal": "Market Price",
}

market_prices_for_heatmap = (
    filtered_market
    .groupby(
        ["State", "District", "Crop", "Year", "Season"],
        as_index=False,
        dropna=False,
    )["Modal_Price_Rs_per_Quintal"]
    .mean()
)

heatmap_source = filtered_production[
    [
        "State",
        "District",
        "Crop",
        "Year",
        "Season",
        "Yield_Tonnes_per_Hectare",
        "Production_Tonnes",
        "Annual_Rainfall_mm",
        "Fertilizer_NPK_kg_per_Hectare",
    ]
].merge(
    market_prices_for_heatmap,
    on=["State", "District", "Crop", "Year", "Season"],
    how="left",
)

heatmap_source = heatmap_source[
    [
        "Yield_Tonnes_per_Hectare",
        "Production_Tonnes",
        "Annual_Rainfall_mm",
        "Fertilizer_NPK_kg_per_Hectare",
        "Modal_Price_Rs_per_Quintal",
    ]
].rename(columns=heatmap_columns)

correlation_matrix = heatmap_source.corr(min_periods=2)

# Important: use the renamed display labels here.
rainfall_corr = heatmap_source[
    ["Rainfall", "Crop Yield"]
].corr(min_periods=2).iloc[0, 1]

# =========================================================
# 11. AGRICULTURAL INSIGHTS: EIGHT CHARTS
# =========================================================
st.header("Agricultural Insights")

if filtered_production.empty:
    st.warning(
        "No production records match the selected filters. "
        "Change your filters to view the charts."
    )
    st.stop()

st.subheader("1. Agricultural Yield Trend")

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
        "Yield_Tonnes_per_Hectare": "Yield (Tonnes Per Hectare)",
    },
)
fig1.update_traces(
    line=dict(color=PALETTE["green"], width=3),
    marker=dict(
        color=PALETTE["sage_mid"],
        size=8,
        line=dict(color=PALETTE["green"], width=1),
    ),
)
show_chart(fig1)

st.subheader("2. Top-Performing Districts")

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
    title="Top 15 Districts By Average Yield",
    labels={
        "Yield_Tonnes_per_Hectare": "Yield (Tonnes Per Hectare)",
        "District": "District",
        "State": "State",
    },
    color_discrete_sequence=CROP_COLORS,
)
show_chart(fig2)
# ---------------------------------------------------------
# CHART 3: MONTHLY MARKET PRICE TREND
# ---------------------------------------------------------
st.subheader("3. Monthly Market Price Trend")

monthly_prices = (
    filtered_market
    .dropna(subset=["Month", "Modal_Price_Rs_per_Quintal"])
    .groupby(["Month", "Crop"], as_index=False)
    ["Modal_Price_Rs_per_Quintal"]
    .mean()
    .sort_values("Month")
)

if not monthly_prices.empty:
    fig3 = px.line(
        monthly_prices,
        x="Month",
        y="Modal_Price_Rs_per_Quintal",
        color="Crop",
        markers=True,
        title="Average Market Price By Month And Crop",
        labels={
            "Month": "Month",
            "Modal_Price_Rs_per_Quintal": "Price (₹ Per Quintal)",
            "Crop": "Crop",
        },
        color_discrete_sequence=CROP_COLORS,
    )

    fig3.update_xaxes(
        tickmode="array",
        tickvals=list(range(1, 13)),
        ticktext=[
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ],
    )
    show_chart(fig3)
else:
    st.info("There is not enough monthly market-price data for this chart.")


st.subheader("4. Market Price Comparison By Crop")

crop_prices = (
    filtered_market
    .groupby("Crop", as_index=False)["Modal_Price_Rs_per_Quintal"]
    .mean()
    .sort_values("Modal_Price_Rs_per_Quintal", ascending=False)
)

if not crop_prices.empty:
    fig4 = px.bar(
        crop_prices,
        x="Crop",
        y="Modal_Price_Rs_per_Quintal",
        title="Average Market Price By Crop",
        labels={
            "Crop": "Crop",
            "Modal_Price_Rs_per_Quintal": "Price (₹ Per Quintal)",
        },
        color_discrete_sequence=[PALETTE["sage_mid"]],
    )
    fig4.update_traces(
        marker_line_color=PALETTE["green"],
        marker_line_width=0.7,
    )
    show_chart(fig4)
else:
    st.info("No market-price records match the selected filters.")

st.subheader("5. Market Price Distribution")

price_box_data = filtered_market.dropna(
    subset=["Crop", "Modal_Price_Rs_per_Quintal"]
)

if not price_box_data.empty:
    fig5 = px.box(
        price_box_data,
        x="Crop",
        y="Modal_Price_Rs_per_Quintal",
        color="Crop",
        title="Market Price Variation By Crop",
        labels={
            "Crop": "Crop",
            "Modal_Price_Rs_per_Quintal": "Price (₹ Per Quintal)",
        },
        color_discrete_sequence=CROP_COLORS,
        points="outliers",
    )
    fig5.update_traces(
        line=dict(color=PALETTE["green"]),
        marker=dict(color=PALETTE["sage_mid"], size=5, opacity=0.65),
        fillcolor=PALETTE["pale_green"],
        selector=dict(type="box"),
    )
    show_chart(fig5)
else:
    st.info("There are no market-price observations for the box plot.")

st.subheader("6. Crop Productivity Comparison")

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
    title="Average Yield By Crop",
    labels={
        "Crop": "Crop",
        "Yield_Tonnes_per_Hectare": "Yield (Tonnes Per Hectare)",
    },
    color_discrete_sequence=[PALETTE["sage_mid"]],
)
fig6.update_traces(
    marker_line_color=PALETTE["green"],
    marker_line_width=0.7,
)
show_chart(fig6)
# ---------------------------------------------------------
# CHART 7: YIELD BY SEASON AND CROP
# ---------------------------------------------------------
st.subheader("7. Yield By Season And Crop")

season_yield = (
    filtered_production
    .dropna(subset=["Season", "Crop", "Yield_Tonnes_per_Hectare"])
    .groupby(["Season", "Crop"], as_index=False)
    ["Yield_Tonnes_per_Hectare"]
    .mean()
)

if not season_yield.empty:
    fig7 = px.bar(
        season_yield,
        x="Season",
        y="Yield_Tonnes_per_Hectare",
        color="Crop",
        barmode="group",
        title="Average Crop Yield Across Seasons",
        labels={
            "Season": "Season",
            "Yield_Tonnes_per_Hectare": "Yield (Tonnes Per Hectare)",
            "Crop": "Crop",
        },
        color_discrete_sequence=CROP_COLORS,
    )
    show_chart(fig7)
else:
    st.info("There is not enough season and yield data for this chart.")

st.subheader("8. Agricultural Variable Relationship Heatmap")

if correlation_matrix.notna().any().any():
    fig8 = go.Figure(
        data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns.tolist(),
            y=correlation_matrix.index.tolist(),
            zmin=-1,
            zmax=1,
            zmid=0,
            colorscale=[
                [0.0, "#D5E0CC"],
                [0.5, "#F7F9F5"],
                [1.0, "#8FAA83"],
            ],
            xgap=3,
            ygap=3,
            colorbar=dict(
                title=dict(
                    text="Correlation",
                    font=dict(color=PALETTE["green_text"]),
                ),
                tickfont=dict(color=PALETTE["green_text"]),
                outlinecolor=PALETTE["border"],
            ),
            hovertemplate=(
                "%{y} Vs %{x}<br>"
                "Correlation: %{z:.2f}<extra></extra>"
            ),
        )
    )

    fig8.update_layout(
        title="Correlation Between Agricultural Variables",
        height=500,
        paper_bgcolor=PALETTE["background"],
        plot_bgcolor=PALETTE["background"],
        font=dict(color=PALETTE["green_text"]),
        xaxis=dict(side="bottom", tickfont=dict(color=PALETTE["green_text"])),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(color=PALETTE["green_text"]),
        ),
    )

    for row_index, row_name in enumerate(correlation_matrix.index):
        for col_index, col_name in enumerate(correlation_matrix.columns):
            value = correlation_matrix.iloc[row_index, col_index]
            if pd.notna(value):
                fig8.add_annotation(
                    x=col_name,
                    y=row_name,
                    text=f"{value:.2f}",
                    showarrow=False,
                    font=dict(color=PALETTE["green_text"], size=11),
                )

    show_chart(fig8)
else:
    st.info(
        "Not enough complete numeric observations to calculate "
        "the correlation heatmap."
    )

# =========================================================
# 12. BUSINESS INSIGHTS
# =========================================================
st.divider()
st.header("Business Insights")

yield_summary = (
    filtered_production.groupby("Crop")["Yield_Tonnes_per_Hectare"]
    .mean()
    .dropna()
)

price_summary = (
    filtered_market.groupby("Crop")["Modal_Price_Rs_per_Quintal"]
    .mean()
    .dropna()
)

district_summary = (
    filtered_production.groupby(["State", "District"])
    ["Yield_Tonnes_per_Hectare"]
    .mean()
    .dropna()
)

fertilizer_by_crop = (
    filtered_production.groupby("Crop")["Fertilizer_NPK_kg_per_Hectare"]
    .mean()
    .dropna()
)

insight_points = []

if not yield_summary.empty:
    insight_points.append(
        f"**Highest-Yielding Crop:** {yield_summary.idxmax()} has an average "
        f"yield of {yield_summary.max():,.2f} tonnes per hectare."
    )
    insight_points.append(
        f"**Lowest-Yielding Crop:** {yield_summary.idxmin()} has an average "
        f"yield of {yield_summary.min():,.2f} tonnes per hectare."
    )
else:
    insight_points.extend([
        "Crop-yield comparisons are unavailable for the current filters.",
        "The lowest-yielding crop could not be identified.",
    ])

if not district_summary.empty:
    best_district = district_summary.idxmax()
    insight_points.append(
        f"**Top-Performing District:** {best_district[1]}, {best_district[0]}, "
        f"has an average yield of {district_summary.max():,.2f} tonnes per hectare."
    )
else:
    insight_points.append(
        "District-level productivity comparisons are unavailable."
    )

if not price_summary.empty:
    insight_points.append(
        f"**Highest Average Market Price:** {price_summary.idxmax()} records "
        f"an average modal price of ₹{price_summary.max():,.2f} per quintal."
    )
else:
    insight_points.append(
        "Average crop market prices are unavailable for these filters."
    )

if pd.notna(rainfall_corr):
    relationship = (
        "positive" if rainfall_corr > 0.1
        else "negative" if rainfall_corr < -0.1
        else "weak or close to zero"
    )
    insight_points.append(
        f"**Rainfall And Yield:** The observed correlation is "
        f"{rainfall_corr:.2f}, indicating a {relationship} relationship. "
        "Correlation does not establish causation."
    )
else:
    insight_points.append(
        "There are insufficient complete rainfall and yield observations "
        "to estimate their correlation."
    )

for i, point in enumerate(insight_points, start=1):
    st.markdown(f"**{i}.** {point}")

# =========================================================
# 13. BUSINESS RECOMMENDATIONS
# =========================================================
st.divider()
st.header("Business Recommendations")

recommendations = []

if not yield_summary.empty:
    recommendations.append(
        f"**Benchmark Crop Productivity:** Review the practices and local "
        f"conditions associated with {yield_summary.idxmax()}. Test suitable "
        "practices in lower-yielding crops before scaling them."
    )
else:
    recommendations.append(
        "**Improve Productivity Tracking:** Collect consistent crop-yield "
        "records to identify gaps and compare performance."
    )

if len(yield_summary) >= 2:
    recommendations.append(
        f"**Investigate Lower-Yielding Crops:** Review {yield_summary.idxmin()} "
        "at field level, comparing rainfall, soil, fertilizer use, and "
        "cultivation conditions before changing inputs."
    )
else:
    recommendations.append(
        "**Investigate Yield Differences:** Compare productivity across "
        "crops, districts, and seasons as more observations become available."
    )

if not price_summary.empty:
    recommendations.append(
        f"**Strengthen Market Planning:** Monitor prices and buyer demand for "
        f"{price_summary.idxmax()}. Check transport, storage, quality, and "
        "production costs before making sales decisions."
    )
else:
    recommendations.append(
        "**Improve Price Monitoring:** Maintain regular market-level price "
        "records before making crop-selling decisions."
    )

if not fertilizer_by_crop.empty:
    recommendations.append(
        "**Review Fertilizer Use:** Compare fertilizer application with yield. "
        "Use soil testing and local agronomic guidance rather than assuming "
        "higher fertilizer use will automatically increase yield."
    )
else:
    recommendations.append(
        "**Improve Input Records:** Record fertilizer use consistently to "
        "support crop-level input-efficiency reviews."
    )

if pd.notna(rainfall_corr):
    recommendations.append(
        "**Plan For Rainfall Variability:** Monitor rainfall alongside yield. "
        "Consider locally appropriate water-management measures based on "
        "field conditions; correlation alone is not enough to select a measure."
    )
else:
    recommendations.append(
        "**Strengthen Climate Planning:** Track rainfall and yield over "
        "multiple years and plan water management with local agronomic guidance."
    )

for i, recommendation in enumerate(recommendations, start=1):
    st.markdown(f"**{i}.** {recommendation}")

st.caption(
    "Recommendations are data-informed starting points. Validate them against "
    "local growing conditions, costs, market demand, and agronomic guidance."
)

# =========================================================
# 14. FILTERED DATA TABLE AND DOWNLOAD
# =========================================================
st.divider()
st.header("Filtered Agricultural Data")

st.caption(
    "The table reflects the selected dashboard filters. Up to 500 rows are displayed."
)

st.dataframe(
    filtered_market.head(500),
    use_container_width=True,
    hide_index=True,
)

csv_data = filtered_market.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data As CSV",
    data=csv_data,
    file_name="filtered_agricultural_data.csv",
    mime="text/csv",
)
