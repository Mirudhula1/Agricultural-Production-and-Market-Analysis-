
%%writefile app.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Agriculture Analytics Dashboard",
    page_icon="🌾",
    layout="wide"
)

st.markdown("""
<style>
.stApp {background-color: #f7f9f5;}
h1, h2, h3 {color: #24543b;}
div[data-testid="stMetric"] {
    background: white;
    padding: 14px;
    border-radius: 12px;
    border: 1px solid #e0e8df;
}
</style>
""", unsafe_allow_html=True)

st.title("🌾 Agriculture Crop Marketplace Dashboard")
st.caption("Explore crop production, yield, rainfall, fertilizer and market prices.")

@st.cache_data
def load_data(file_bytes):
    from io import BytesIO
    return pd.read_excel(BytesIO(file_bytes), sheet_name="Agriculture Data")

uploaded = st.file_uploader(
    "Upload your agriculture Excel workbook",
    type=["xlsx"]
)

if uploaded is None:
    st.info("Upload your Excel workbook to open the interactive dashboard.")
    st.markdown("""
    **Your dashboard includes:**
    - Crop yield trends over time
    - Top 15 regions by yield
    - Rainfall vs yield
    - Monthly market price trends
    - Price variability by crop
    - Production vs market price
    - Crop productivity comparison
    - Fertilizer use vs yield
    """)
    st.stop()

try:
    df = load_data(uploaded.getvalue())
except Exception as e:
    st.error(f"Could not read the Agriculture Data sheet: {e}")
    st.stop()

required = [
    "State", "District", "Year", "Month", "Crop", "Season",
    "Yield_Tonnes_per_Hectare", "Production_Tonnes",
    "Annual_Rainfall_mm", "Fertilizer_NPK_kg_per_Hectare",
    "Modal_Price_Rs_per_Quintal", "Market"
]
missing = [c for c in required if c not in df.columns]

if missing:
    st.error("Missing columns: " + ", ".join(missing))
    st.stop()

numeric_cols = [
    "Year", "Month", "Yield_Tonnes_per_Hectare", "Production_Tonnes",
    "Annual_Rainfall_mm", "Fertilizer_NPK_kg_per_Hectare",
    "Modal_Price_Rs_per_Quintal", "Market_Price_Rs_per_Tonne"
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Sidebar filters
st.sidebar.header("Dashboard Filters")

states = sorted(df["State"].dropna().unique().tolist())
crops = sorted(df["Crop"].dropna().unique().tolist())
seasons = sorted(df["Season"].dropna().unique().tolist())

sel_states = st.sidebar.multiselect("State", states, default=states)
sel_crops = st.sidebar.multiselect("Crop", crops, default=crops)
sel_seasons = st.sidebar.multiselect("Season", seasons, default=seasons)

data = df[
    df["State"].isin(sel_states)
    & df["Crop"].isin(sel_crops)
    & df["Season"].isin(sel_seasons)
].copy()

years = sorted(data["Year"].dropna().astype(int).unique().tolist())
if years:
    year_range = st.sidebar.slider(
        "Year range", min(years), max(years), (min(years), max(years))
    )
    data = data[data["Year"].between(*year_range)]

if data.empty:
    st.warning("No data matches your filters. Please change your selections.")
    st.stop()

# Production values repeat across monthly/market records.
production = data.drop_duplicates(
    subset=["State", "District", "Crop", "Year", "Season"]
).copy()

# KPI cards
k1, k2, k3, k4 = st.columns(4)
k1.metric("Production records", f"{len(production):,}")
k2.metric("Crops", f"{production['Crop'].nunique():,}")
k3.metric("States", f"{production['State'].nunique():,}")
k4.metric(
    "Average yield",
    f"{production['Yield_Tonnes_per_Hectare'].mean():,.2f} t/ha"
)

st.divider()

# 1. Crop yield trend
st.subheader("1. Crop Yield Trend Over Years")
trend = production.groupby("Year", as_index=False)[
    "Yield_Tonnes_per_Hectare"
].mean()
fig = px.line(
    trend, x="Year", y="Yield_Tonnes_per_Hectare", markers=True,
    labels={"Yield_Tonnes_per_Hectare": "Yield (tonnes/hectare)"}
)
st.plotly_chart(fig, use_container_width=True)

# 2. Top 15 regions
st.subheader("2. Top 15 Regions by Yield")
region = production.groupby(
    ["State", "District"], as_index=False
)["Yield_Tonnes_per_Hectare"].mean()
region["Region"] = region["District"] + ", " + region["State"]
region = region.nlargest(15, "Yield_Tonnes_per_Hectare").sort_values(
    "Yield_Tonnes_per_Hectare"
)
fig = px.bar(
    region, x="Yield_Tonnes_per_Hectare", y="Region",
    orientation="h",
    labels={"Yield_Tonnes_per_Hectare": "Yield (tonnes/hectare)"}
)
st.plotly_chart(fig, use_container_width=True)

# 3. Rainfall vs yield
st.subheader("3. Rainfall vs Yield")
fig = px.scatter(
    production, x="Annual_Rainfall_mm",
    y="Yield_Tonnes_per_Hectare", color="Crop",
    hover_data=["State", "District", "Year"],
    labels={
        "Annual_Rainfall_mm": "Annual rainfall (mm)",
        "Yield_Tonnes_per_Hectare": "Yield (tonnes/hectare)"
    }
)
st.plotly_chart(fig, use_container_width=True)

# 4. Monthly market price trend
st.subheader("4. Monthly Market Price Trend")
market = data.copy()
market["Date"] = pd.to_datetime(
    dict(
        year=market["Year"].astype("Int64"),
        month=market["Month"].astype("Int64"),
        day=1
    ),
    errors="coerce"
)
monthly = market.dropna(subset=["Date"]).groupby(
    ["Date", "Crop"], as_index=False
)["Modal_Price_Rs_per_Quintal"].mean()
fig = px.line(
    monthly, x="Date", y="Modal_Price_Rs_per_Quintal",
    color="Crop",
    labels={"Modal_Price_Rs_per_Quintal": "Price (₹/quintal)"}
)
st.plotly_chart(fig, use_container_width=True)

# 5. Price variability
st.subheader("5. Price Variability by Crop")
fig = px.box(
    market, x="Crop", y="Modal_Price_Rs_per_Quintal",
    labels={"Modal_Price_Rs_per_Quintal": "Price (₹/quintal)"}
)
fig.update_layout(xaxis_tickangle=-35)
st.plotly_chart(fig, use_container_width=True)

# 6. Production vs price
st.subheader("6. Production vs Market Price")
comparison = data.groupby(["Crop", "Year"], as_index=False).agg(
    Production_Tonnes=("Production_Tonnes", "mean"),
    Modal_Price_Rs_per_Quintal=("Modal_Price_Rs_per_Quintal", "mean")
)
fig = px.scatter(
    comparison, x="Production_Tonnes",
    y="Modal_Price_Rs_per_Quintal", color="Crop",
    hover_data=["Year"],
    labels={
        "Production_Tonnes": "Production (tonnes)",
        "Modal_Price_Rs_per_Quintal": "Price (₹/quintal)"
    }
)
st.plotly_chart(fig, use_container_width=True)

# 7. Crop productivity
st.subheader("7. Crop Productivity Comparison")
productivity = production.groupby("Crop", as_index=False)[
    "Yield_Tonnes_per_Hectare"
].mean().sort_values("Yield_Tonnes_per_Hectare")
fig = px.bar(
    productivity, x="Yield_Tonnes_per_Hectare", y="Crop",
    orientation="h",
    labels={"Yield_Tonnes_per_Hectare": "Yield (tonnes/hectare)"}
)
st.plotly_chart(fig, use_container_width=True)

# 8. Fertilizer vs yield heatmap
st.subheader("8. Fertilizer Use vs Yield")
fert = "Fertilizer_NPK_kg_per_Hectare"
heat_data = production.dropna(
    subset=[fert, "Yield_Tonnes_per_Hectare"]
).copy()

if len(heat_data) >= 5 and heat_data[fert].nunique() > 1:
    heat_data["Fertilizer range"] = pd.qcut(
        heat_data[fert], q=5, duplicates="drop"
    )
    heat = heat_data.pivot_table(
        index="Season", columns="Fertilizer range",
        values="Yield_Tonnes_per_Hectare",
        aggfunc="mean", observed=False
    )
    heat.columns = heat.columns.astype(str)
    fig = px.imshow(
        heat, aspect="auto", text_auto=".2f",
        labels={"x": "Fertilizer range", "y": "Season", "color": "Yield"}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Not enough fertilizer data to create the heatmap.")

# Data preview and download
st.divider()
st.subheader("Filtered Data")
st.dataframe(data.head(500), use_container_width=True)

st.download_button(
    "Download filtered data as CSV",
    data=data.to_csv(index=False).encode("utf-8"),
    file_name="agriculture_filtered_data.csv",
    mime="text/csv"
)
