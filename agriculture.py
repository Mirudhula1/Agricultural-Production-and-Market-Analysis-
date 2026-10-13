from pathlib import Path
import pandas as pd
import plotly.express as px


def load_data():
    """Load the workbook stored beside this Python file."""
    file_path = Path(__file__).parent / "Agriculture dataset.xlsx"
    if not file_path.exists():
        # Optional fallback for the original Google Colab setup.
        colab_path = Path("/content/drive/MyDrive/Capstone /Agriculture dataset.xlsx")
        if colab_path.exists():
            file_path = colab_path
        else:
            raise FileNotFoundError(
                "Could not find 'Agriculture dataset.xlsx'. Place the workbook "
                "in the same folder as app.py and agriculture.py."
            )

    df = pd.read_excel(file_path, sheet_name="Agriculture Data")
    required = [
        "State", "District", "Crop", "Year", "Season",
        "Yield_Tonnes_per_Hectare", "Production_Tonnes",
        "Annual_Rainfall_mm", "Fertilizer_NPK_kg_per_Hectare",
        "Modal_Price_Rs_per_Quintal", "Month", "Market"
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Workbook is missing required columns: {missing}")

    for col in [
        "Year", "Yield_Tonnes_per_Hectare", "Production_Tonnes",
        "Annual_Rainfall_mm", "Fertilizer_NPK_kg_per_Hectare",
        "Modal_Price_Rs_per_Quintal"
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    production_df = df.drop_duplicates(
        subset=["State", "District", "Crop", "Year", "Season"]
    ).copy()
    market_df = df.drop_duplicates(
        subset=["State", "District", "Crop", "Year", "Month", "Market"]
    ).copy()

    month_text = market_df["Month"].astype("string").str.strip()
    month_num = pd.to_numeric(month_text, errors="coerce")
    month_num = month_num.fillna(
        pd.to_datetime(month_text, format="%B", errors="coerce").dt.month
    )
    month_num = month_num.fillna(
        pd.to_datetime(month_text, format="%b", errors="coerce").dt.month
    )
    market_df["Date"] = pd.to_datetime(
        {"year": market_df["Year"], "month": month_num, "day": 1},
        errors="coerce"
    )
    return production_df, market_df


def create_charts(production_df, market_df):
    charts = {}

    yield_data = production_df.groupby("Year", as_index=False)["Yield_Tonnes_per_Hectare"].mean()
    charts["fig1"] = px.line(
        yield_data, x="Year", y="Yield_Tonnes_per_Hectare", markers=True,
        title="Crop Yield Trend Over the Years", template="plotly_white"
    )

    regions = production_df.copy()
    regions["Region"] = regions["District"].fillna("Unknown").astype(str) + ", " + regions["State"].fillna("Unknown").astype(str)
    regions = regions.groupby("Region", as_index=False)["Yield_Tonnes_per_Hectare"].mean()
    regions = regions.nlargest(15, "Yield_Tonnes_per_Hectare")
    charts["fig2"] = px.bar(
        regions, x="Yield_Tonnes_per_Hectare", y="Region", orientation="h",
        title="Top 15 Regions by Average Yield", color="Yield_Tonnes_per_Hectare",
        color_continuous_scale="Greens", template="plotly_white"
    )

    charts["fig3"] = px.scatter(
        production_df, x="Annual_Rainfall_mm", y="Yield_Tonnes_per_Hectare",
        color="Season", hover_data=["Crop", "State", "District", "Year"],
        title="Annual Rainfall vs Crop Yield", template="plotly_white"
    )

    price_data = market_df.dropna(subset=["Date"]).groupby("Date", as_index=False)["Modal_Price_Rs_per_Quintal"].mean().sort_values("Date")
    charts["fig4"] = px.line(
        price_data, x="Date", y="Modal_Price_Rs_per_Quintal", markers=True,
        title="Monthly Market Price Trend", template="plotly_white"
    )

    charts["fig5"] = px.box(
        market_df, x="Crop", y="Modal_Price_Rs_per_Quintal", color="Crop",
        title="Market Price Variation by Crop", template="plotly_white"
    )

    production_by_crop_year = production_df.groupby(["Crop", "Year"], as_index=False)["Production_Tonnes"].sum()
    price_by_crop_year = market_df.groupby(["Crop", "Year"], as_index=False)["Modal_Price_Rs_per_Quintal"].mean()
    comparison = production_by_crop_year.merge(price_by_crop_year, on=["Crop", "Year"], how="inner")
    charts["fig6"] = px.scatter(
        comparison, x="Production_Tonnes", y="Modal_Price_Rs_per_Quintal",
        color="Crop", hover_data=["Year"], title="Yearly Crop Production vs Market Price",
        template="plotly_white"
    )

    productivity = production_df.groupby("Crop", as_index=False)["Yield_Tonnes_per_Hectare"].mean().dropna().sort_values("Yield_Tonnes_per_Hectare")
    fig7 = px.bar(
        productivity, x="Yield_Tonnes_per_Hectare", y="Crop", orientation="h",
        text="Yield_Tonnes_per_Hectare", title="Average Crop Productivity Comparison",
        labels={"Yield_Tonnes_per_Hectare": "Average Yield (tonnes/ha)", "Crop": "Crop"},
        template="plotly_white"
    )
    fig7.update_traces(texttemplate="%{x:.2f}", textposition="outside", marker_color="#2E7547")
    fig7.update_layout(showlegend=False)
    charts["fig7"] = fig7

    fert = production_df.copy()
    fert["Fertilizer_NPK_kg_per_Hectare"] = pd.to_numeric(fert["Fertilizer_NPK_kg_per_Hectare"], errors="coerce")
    fert = fert.dropna(subset=["Fertilizer_NPK_kg_per_Hectare", "Yield_Tonnes_per_Hectare", "Season"])
    if not fert.empty and fert["Fertilizer_NPK_kg_per_Hectare"].nunique() > 1:
        fert["Fertilizer_Range"] = pd.cut(fert["Fertilizer_NPK_kg_per_Hectare"], bins=5, duplicates="drop")
        heatmap = fert.pivot_table(index="Season", columns="Fertilizer_Range", values="Yield_Tonnes_per_Hectare", aggfunc="mean", observed=False)
        heatmap.columns = [str(c) for c in heatmap.columns]
        fig8 = px.imshow(
            heatmap, text_auto=".2f", color_continuous_scale="YlGn",
            title="Fertilizer Use vs Crop Yield",
            labels={"x": "Fertilizer Use (kg/ha)", "y": "Season", "color": "Average Yield (tonnes/ha)"},
            aspect="auto", template="plotly_white"
        )
    else:
        fig8 = px.scatter(title="Fertilizer Use vs Crop Yield — insufficient data")
    charts["fig8"] = fig8
    return charts
