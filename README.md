# India Water Quality Dashboard 
# Data-Driven Assessment of Surface & Groundwater Quality for SDG-6

Interactive dashboard analysing 2022 NWMP lake, pond, tank & wetland monitoring data across 31 Indian states — aligned with **SDG 6: Clean Water and Sanitation**.

## Live Demo
🔗 [View Dashboard](https://india-water-quality-analysis-123456.streamlit.app/)

## Features
- KPI summary cards (locations, states, critical BOD sites, avg dissolved oxygen)
- Interactive Plotly charts with hover tooltips
- State-level BOD and location-count bar charts
- Water body type distribution (pie)
- BOD vs Dissolved Oxygen scatter plot (pollution signal)
- Parameter averages vs WHO safe limits
- Water quality grading system (A–F) based on BOD
- Top 20 most polluted water bodies table
- Full filterable + searchable data table
- CSV download of filtered data
- Auto-generated key insights

## Dataset
- **Source:** Central Pollution Control Board (CPCB), India
- **Programme:** National Water Monitoring Programme (NWMP) 2022
- **Coverage:** 639 monitoring locations across 31 states/UTs
- **Parameters:** Temperature, Dissolved Oxygen, pH, BOD, Conductivity, Nitrate, Fecal Coliform, Total Coliform

## Run Locally

```bash
pip install -r requirements.txt
# Place 2022_lake_data.csv in the same folder as app.py
streamlit run app.py
```

## WHO / CPCB Thresholds Used
| Parameter | Safe Limit |
|---|---|
| BOD | ≤ 3 mg/L |
| Dissolved Oxygen | ≥ 5 mg/L |
| pH | 6.5 – 8.5 |
| Fecal Coliform | ≤ 500 MPN/100mL |
| Nitrate | ≤ 10 mg/L |

## Tech Stack
- Python 3.9+
- [Streamlit](https://streamlit.io/) — dashboard framework
- [Plotly](https://plotly.com/python/) — interactive charts
- [Pandas](https://pandas.pydata.org/) — data manipulation
