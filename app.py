import streamlit as st
import pandas as pd
from agriculture import load_data, create_charts


# --------------------------------------------------
# 1. PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="Agriculture Production and Market Analysis",
    page_icon="🌱",
    layout="wide"
)


# --------------------------------------------------
# 2. CUSTOM DASHBOARD DESIGN
# --------------------------------------------------

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #101713;
    color: #F2F6F2;
}

/* Page spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1600px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #17251D;
    border-right: 1px solid #2C4435;
}

/* Headings */
h1 {
    color: #F5F8F4 !important;
    font-weight: 800 !important;
}

h2, h3 {
    color: #D5F2D2 !important;
}

/* KPI cards */
.kpi-card {
    background: linear-gradient(145deg, #1D3B2A, #172D21);
    border: 1px solid #31583D;
    border-radius: 14px;
    padding: 20px;
    min-height: 140px;
    margin-bottom: 10px;
}

/* KPI labels */
.kpi-label {
    color: #B9D2BF;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 14px;
}

/* KPI values */
.kpi-value {
    color: #C9F27C;
    font-size: clamp(20px, 2vw, 29px);
    font-weight: 750;
    line-height: 1.3;
    overflow-wrap: anywhere;
}

/* KPI notes */
.kpi-note {
    color: #B9D2BF;
    font-size: 12px;
    margin-top: 8px;
}

/* Dividers */
hr {
    border-color: #2C4435 !important;
    margin-top: 25px;
    margin-bottom: 25px;
}

/* Download button */
.stDownloadButton button {
    background-color: #2E7547;
    color: white;
    border: none;
    border-radius: 8px;
}

.stDownloadButton button:hover {
    background-color: #398A56;
    color: white;
}

/* Data section */
div[data-testid="stExpander"] {
    border: 1px solid #31503A;
    border-radius: 10px;
}

/* Header card */
.dashboard-header {
    background: linear-gradient(110deg, #1D3B2A, #101713);
    border: 1px solid #31583D;
    border-radius: 16px;
    padding: 25px 28px;
    margin-bottom: 20px;
}

.dashboard-eyebrow {
    color: #C9F27C;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 10px;
}

.dashboard-title {
    color: #F5F8F4;
    font-size: 34px;
    font-weight: 800;
    line-height: 1.25;
}

.dashboard-description {
    color: #B9D2BF;
    font-size: 14px;
    margin-top: 14px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 3. LOAD DATA
# --------------------------------------------------

production_df, market_df = load_data()


# --------------------------------------------------
# 4. DASHBOARD HEADER
# --------------------------------------------------

st.markdown(
    """
    <div style="
        background-color: #1D3B2A;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #31583D;
    ">
        <p style="color: #C9F27C; font-size: 12px;
                  letter-spacing: 2px;">
            AGRICULTURE ANALYTICS
        </p>
        <h1 style="color: white; font-size: 32px;">
            Agriculture Production and Market Analysis
        </h1>
        <p style="color: #B9D2BF;">
            Explore crop productivity, rainfall, fertilizer
            usage and agricultural market prices.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# 5. SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.markdown("## ⚙️ Dashboard Filters")
st.sidebar.caption("Choose the data you want to analyse.")
st.sidebar.divider()


# STATE FILTER
states = ["All States"] + sorted(
    production_df["State"].dropna().unique().tolist()
)

selected_state = st.sidebar.selectbox(
    "State",
    states
)


# CROP FILTER
# Crop options are based on the complete dataset.
crops = ["All Crops"] + sorted(
    production_df["Crop"].dropna().unique().tolist()
)

selected_crop = st.sidebar.selectbox(
    "Crop",
    crops
)


# SEASON FILTER
seasons = ["All Seasons"] + sorted(
    production_df["Season"].dropna().unique().tolist()
)

selected_season = st.sidebar.selectbox(
    "Season",
    seasons
)


# YEAR FILTER
years = sorted(
    pd.to_numeric(
        production_df["Year"],
        errors="coerce"
    )
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)

selected_years = st.sidebar.multiselect(
    "Year",
    years,
    default=years
)


# --------------------------------------------------
# 6. APPLY FILTERS
# --------------------------------------------------

def apply_filters(data):

    # Copy the original data before filtering.
    filtered = data.copy()

    if selected_state != "All States":
        filtered = filtered[
            filtered["State"] == selected_state
        ]

    if selected_crop != "All Crops":
        filtered = filtered[
            filtered["Crop"] == selected_crop
        ]

    if selected_season != "All Seasons":
        filtered = filtered[
            filtered["Season"] == selected_season
        ]

    if selected_years:
        filtered = filtered[
            pd.to_numeric(
                filtered["Year"],
                errors="coerce"
            ).isin(selected_years)
        ]
    else:
        filtered = filtered.iloc[0:0]

    return filtered


# Apply the same filters to both datasets.
filtered_production = apply_filters(production_df)
filtered_market = apply_filters(market_df)


# STOP IF NO MATCHING DATA EXISTS
if filtered_production.empty or filtered_market.empty:

    st.warning(
        "No matching data is available for these filters. "
        "Try selecting different options."
    )

    st.stop()


# --------------------------------------------------
# 7. CALCULATE KPI VALUES
# --------------------------------------------------

total_production = filtered_production[
    "Production_Tonnes"
].sum()

average_yield = filtered_production[
    "Yield_Tonnes_per_Hectare"
].mean()

average_price = filtered_market[
    "Modal_Price_Rs_per_Quintal"
].mean()

average_rainfall = filtered_production[
    "Annual_Rainfall_mm"
].mean()


# SHORTEN LARGE NUMBERS
def compact_number(value):

    if pd.isna(value):
        return "N/A"

    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"

    if abs(value) >= 1_000:
        return f"{value / 1_000:.2f}K"

    return f"{value:,.2f}"


# --------------------------------------------------
# 8. KEY PERFORMANCE INDICATORS
# --------------------------------------------------

st.markdown("## Key Performance Indicators")
st.caption("Summary of the currently selected data")

k1, k2, k3, k4 = st.columns(4, gap="medium")


with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">🌾 TOTAL PRODUCTION</div>
        <div class="kpi-value">
            {compact_number(total_production)}
        </div>
        <div class="kpi-note">Tonnes</div>
    </div>
    """, unsafe_allow_html=True)


with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">📈 AVERAGE YIELD</div>
        <div class="kpi-value">
            {compact_number(average_yield)}
        </div>
        <div class="kpi-note">Tonnes per hectare</div>
    </div>
    """, unsafe_allow_html=True)


with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">₹ AVERAGE MARKET PRICE</div>
        <div class="kpi-value">
            ₹{compact_number(average_price)}
        </div>
        <div class="kpi-note">Per quintal</div>
    </div>
    """, unsafe_allow_html=True)


with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">🌧️ AVERAGE RAINFALL</div>
        <div class="kpi-value">
            {compact_number(average_rainfall)}
        </div>
        <div class="kpi-note">Millimetres</div>
    </div>
    """, unsafe_allow_html=True)


st.divider()


# --------------------------------------------------
# 9. CREATE CHARTS
# --------------------------------------------------

charts = create_charts(
    filtered_production,
    filtered_market
)


# --------------------------------------------------
# 10. CLEAN CHART LABELS AND APPEARANCE
# --------------------------------------------------

def clean_chart_labels(fig):

    # Clean the chart title.
    title = fig.layout.title.text

    if title:
        fig.update_layout(
            title_text=title.replace("_", " ")
        )

    # Clean X-axis titles.
    for axis in fig.select_xaxes():
        if axis.title.text:
            axis.title.text = axis.title.text.replace(
                "_", " "
            )

    # Clean Y-axis titles.
    for axis in fig.select_yaxes():
        if axis.title.text:
            axis.title.text = axis.title.text.replace(
                "_", " "
            )

    # Clean the legend heading.
    if fig.layout.legend and fig.layout.legend.title.text:
        fig.layout.legend.title.text = (
            fig.layout.legend.title.text.replace("_", " ")
        )

    # Clean supported chart legend names and hover labels.
    for trace in fig.data:

        if trace.name:
            trace.name = trace.name.replace("_", " ")

        if trace.hovertemplate:
            trace.hovertemplate = trace.hovertemplate.replace(
                "_", " "
            )

    # Apply consistent colours and spacing.
    fig.update_layout(
        paper_bgcolor="#101713",
        plot_bgcolor="#101713",
        font=dict(
            color="#E7EEE8",
            family="Arial",
            size=12
        ),
        title_font=dict(
            color="#D5F2D2",
            size=17
        ),
        margin=dict(
            l=45,
            r=25,
            t=65,
            b=45
        ),
        legend=dict(
            font=dict(size=11)
        ),
        hoverlabel=dict(
            bgcolor="#1D3B2A",
            font_color="#FFFFFF"
        )
    )

    # Improve axis readability.
    fig.update_xaxes(
        title_font=dict(size=12),
        tickfont=dict(size=10),
        gridcolor="#29382F",
        zerolinecolor="#405447"
    )

    fig.update_yaxes(
        title_font=dict(size=12),
        tickfont=dict(size=10),
        gridcolor="#29382F",
        zerolinecolor="#405447"
    )

    return fig


# Clean all eight charts.
for chart_name in charts:
    charts[chart_name] = clean_chart_labels(
        charts[chart_name]
    )


# --------------------------------------------------
# 11. DISPLAY THE EIGHT CHARTS
# --------------------------------------------------

st.markdown("## Agriculture Insights")
st.caption(
    "Explore crop performance, weather patterns and market behaviour."
)


# CHART 1 - FULL WIDTH
st.markdown("### 01 · Crop Performance")

st.plotly_chart(
    charts["fig1"],
    use_container_width=True,
    key="chart_1"
)


# CHART 2 - FULL WIDTH
st.markdown("### 02 · Regional Productivity")

st.plotly_chart(
    charts["fig2"],
    use_container_width=True,
    key="chart_2"
)


st.divider()


# CHARTS 3 AND 4
st.markdown("### 03 · Weather and Market Trends")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.plotly_chart(
        charts["fig3"],
        use_container_width=True,
        key="chart_3"
    )

with col2:
    st.plotly_chart(
        charts["fig4"],
        use_container_width=True,
        key="chart_4"
    )


st.divider()


# CHARTS 5 AND 6
st.markdown("### 04 · Market Analysis")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.plotly_chart(
        charts["fig5"],
        use_container_width=True,
        key="chart_5"
    )

with col2:
    st.plotly_chart(
        charts["fig6"],
        use_container_width=True,
        key="chart_6"
    )


st.divider()


# CHARTS 7 AND 8
st.markdown("### 05 · Productivity and Resources")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.plotly_chart(
        charts["fig7"],
        use_container_width=True,
        key="chart_7"
    )

with col2:
    st.plotly_chart(
        charts["fig8"],
        use_container_width=True,
        key="chart_8"
    )


# --------------------------------------------------
# 12. FILTERED DATA TABLE AND DOWNLOAD
# --------------------------------------------------

st.divider()

with st.expander("📁 Explore and download filtered data"):

    st.caption(
        f"{len(filtered_production):,} production records "
        "match your filters."
    )

    st.dataframe(
        filtered_production,
        use_container_width=True,
        hide_index=True
    )

    csv = filtered_production.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=csv,
        file_name="agriculture_filtered_data.csv",
        mime="text/csv"
    )


# --------------------------------------------------
# 13. FOOTER
# --------------------------------------------------

st.markdown("""
<div style="
    text-align: center;
    color: #82988A;
    font-size: 12px;
    padding: 25px 0 8px 0;
">
    Agriculture Production and Market Analysis
    · Agriculture Analytics Dashboard
</div>
""", unsafe_allow_html=True)