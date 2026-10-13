# Agriculture Production and Market Analysis Dashboard

This Streamlit project explores crop productivity, production, rainfall, fertilizer use, and agricultural market prices.

## Files
- `app.py` — Streamlit dashboard interface and filters.
- `agriculture.py` — loads the workbook and creates eight Plotly charts.
- `Agriculture dataset.xlsx` — workbook used by the dashboard.
- `requirements.txt` — Python packages required to run the app.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the dashboard:
   ```bash
   streamlit run app.py
   ```

The workbook must contain a sheet named `Agriculture Data` and the expected columns used in the code.

## Deploy with Streamlit Community Cloud
1. Upload `app.py`, `agriculture.py`, `requirements.txt`, and the workbook to a GitHub repository you control.
2. Confirm you are permitted to share the workbook publicly and that it contains no sensitive information. If you cannot publish it, remove it from the repository and modify the app to load data from an approved private source or use the sidebar uploader.
3. In Streamlit Community Cloud, create an app from that repository, select branch `main`, and set the main file path to `app.py`.

## Data-source note
Before submitting this project, document and verify the workbook's original source, license/usage terms, and any faculty approval required by your capstone. The included workbook is bundled because the app needs it to run; its public-domain status has not been independently verified here.
