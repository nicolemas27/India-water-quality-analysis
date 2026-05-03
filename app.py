"""
India Water Quality Dashboard
2022 NWMP Lake, Pond, Tank & Wetland Monitoring Data
SDG 6: Clean Water and Sanitation

"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="India Water Quality Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 16px 20px;
        border-left: 4px solid #1f77b4;
    }
    .metric-card.danger { border-left-color: #d62728; }
    .metric-card.good   { border-left-color: #2ca02c; }
    .block-container { padding-top: 1.5rem; }
    h1 { margin-bottom: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── WHO / CPCB thresholds ─────────────────────────────────────────────────────
BOD_SAFE      = 3.0   # mg/L  (Class B drinking threshold)
DO_MIN        = 5.0   # mg/L
PH_MIN, PH_MAX = 6.5, 8.5
FC_SAFE       = 500   # MPN/100mL

# ── Data loading & cleaning ───────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("2022_lake_data.csv")

    # Normalise column names
    df.columns = df.columns.str.strip()

    # Clean state names (some have embedded newlines)
    df["State Name"] = df["State Name"].str.replace(r"\s+", " ", regex=True).str.strip()
    df["Name of Monitoring Location"] = (
        df["Name of Monitoring Location"]
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Cast numeric columns
    num_cols = [
        "Min Temperature", "Max Temperature",
        "Min Dissolved Oxygen", "Max Dissolved Oxygen",
        "Min pH", "Max pH",
        "Min Conductivity", "Max Conductivity",
        "Min BOD", "Max BOD",
        "Min Nitrate N + Nitrite N", "Max Nitrate N + Nitrite N",
        "Min Fecal Coliform", "Max Fecal Coliform",
        "Min Total Coliform", "Max Total Coliform",
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Derived midpoint columns
    df["Avg BOD"]             = (df["Min BOD"] + df["Max BOD"]) / 2
    df["Avg DO"]              = (df["Min Dissolved Oxygen"] + df["Max Dissolved Oxygen"]) / 2
    df["Avg pH"]              = (df["Min pH"] + df["Max pH"]) / 2
    df["Avg Fecal Coliform"]  = (df["Min Fecal Coliform"] + df["Max Fecal Coliform"]) / 2
    df["Avg Temperature"]     = (df["Min Temperature"] + df["Max Temperature"]) / 2
    df["Avg Nitrate"]         = (
        (df["Min Nitrate N + Nitrite N"] + df["Max Nitrate N + Nitrite N"]) / 2
    )

    # Pollution flag (BOD > safe limit)
    df["BOD Critical"] = df["Avg BOD"] > BOD_SAFE

    # Water Quality Grade (A–F) based on avg BOD
    def wq_grade(bod):
        if pd.isna(bod): return "Unknown"
        if bod <= 2:   return "A – Excellent"
        if bod <= 3:   return "B – Good"
        if bod <= 6:   return "C – Moderate"
        if bod <= 12:  return "D – Poor"
        if bod <= 30:  return "E – Very Poor"
        return "F – Critical"

    df["WQ Grade"] = df["Avg BOD"].apply(wq_grade)

    return df.dropna(subset=["State Name", "Type Water Body"])


df_full = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Flag_of_India.svg/320px-Flag_of_India.svg.png",
        width=120,
    )
    st.title("Filters")

    states = ["All States"] + sorted(df_full["State Name"].dropna().unique().tolist())
    sel_state = st.selectbox("State", states)

    types = ["All Types"] + sorted(df_full["Type Water Body"].dropna().unique().tolist())
    sel_type = st.selectbox("Water Body Type", types)

    st.markdown("---")
    st.markdown(
        "**Data source:** NWMP 2022  \n"
        "[Central Pollution Control Board](https://cpcb.nic.in/)  \n\n"
        "**SDG 6** – Clean Water & Sanitation"
    )

# Apply filters
df = df_full.copy()
if sel_state != "All States":
    df = df[df["State Name"] == sel_state]
if sel_type != "All Types":
    df = df[df["Type Water Body"] == sel_type]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("💧 India Water Quality Dashboard")
st.caption("2022 NWMP Lake, Pond, Tank & Wetland Monitoring Data · SDG 6: Clean Water & Sanitation")

if sel_state != "All States" or sel_type != "All Types":
    parts = []
    if sel_state != "All States": parts.append(sel_state)
    if sel_type != "All Types":   parts.append(sel_type)
    st.info(f"Showing: **{' · '.join(parts)}** — {len(df)} location(s)")

st.markdown("---")

# ── KPI cards ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

total_locs     = len(df)
total_states   = df["State Name"].nunique()
critical_bod   = int(df["BOD Critical"].sum())
avg_do         = df["Avg DO"].mean()
avg_bod        = df["Avg BOD"].mean()

k1.metric("📍 Monitoring Locations", f"{total_locs:,}")
k2.metric("🗺️ States / UTs",         f"{total_states}")
k3.metric("⚠️ Critical BOD Sites",   f"{critical_bod:,}",
          delta=f"{critical_bod/max(total_locs,1)*100:.0f}% of total",
          delta_color="inverse")
k4.metric("🌊 Avg Dissolved Oxygen",  f"{avg_do:.2f} mg/L",
          delta="Safe ≥ 5 mg/L", delta_color="normal" if avg_do >= DO_MIN else "inverse")
k5.metric("🧪 Avg BOD",              f"{avg_bod:.2f} mg/L",
          delta="Safe ≤ 3 mg/L", delta_color="normal" if avg_bod <= BOD_SAFE else "inverse")

st.markdown("---")

# ── State-level charts ────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

# Chart 1 – Top states by location count
with col_left:
    state_agg = (
        df.groupby("State Name")
        .agg(
            Locations=("Name of Monitoring Location", "count"),
            Avg_BOD=("Avg BOD", "mean"),
            Avg_DO=("Avg DO", "mean"),
        )
        .reset_index()
        .sort_values("Locations", ascending=False)
        .head(15)
    )
    fig1 = px.bar(
        state_agg,
        x="State Name", y="Locations",
        color="Avg_BOD",
        color_continuous_scale="RdYlGn_r",
        range_color=[0, state_agg["Avg_BOD"].max()],
        labels={"Avg_BOD": "Avg BOD (mg/L)", "Locations": "# Locations"},
        title="Top 15 States by Monitoring Locations<br><sup>Colour = average BOD (higher = more polluted)</sup>",
    )
    fig1.update_layout(xaxis_tickangle=-40, coloraxis_colorbar_title="Avg BOD", height=380)
    st.plotly_chart(fig1, use_container_width=True)

# Chart 2 – Average BOD by state
with col_right:
    bod_agg = (
        df.groupby("State Name")["Avg BOD"]
        .mean()
        .reset_index()
        .sort_values("Avg BOD", ascending=False)
        .head(15)
    )
    fig2 = px.bar(
        bod_agg,
        x="State Name", y="Avg BOD",
        color="Avg BOD",
        color_continuous_scale="RdYlGn_r",
        labels={"Avg BOD": "Avg BOD (mg/L)"},
        title="Top 15 States by Average BOD<br><sup>WHO safe limit = 3 mg/L (dashed red line)</sup>",
    )
    fig2.add_hline(y=BOD_SAFE, line_dash="dash", line_color="red",
                   annotation_text=f"Safe limit ({BOD_SAFE} mg/L)", annotation_position="top right")
    fig2.update_layout(xaxis_tickangle=-40, height=380)
    st.plotly_chart(fig2, use_container_width=True)

# ── Type distribution + Scatter ───────────────────────────────────────────────
col_l2, col_r2 = st.columns(2)

# Chart 3 – Water body type pie
with col_l2:
    type_counts = df["Type Water Body"].value_counts().reset_index()
    type_counts.columns = ["Type", "Count"]
    fig3 = px.pie(
        type_counts, values="Count", names="Type",
        title="Water Body Type Distribution",
        color_discrete_sequence=px.colors.qualitative.Set2,
        hole=0.4,
    )
    fig3.update_traces(textposition="inside", textinfo="percent+label")
    fig3.update_layout(height=380, showlegend=True)
    st.plotly_chart(fig3, use_container_width=True)

# Chart 4 – BOD vs DO scatter (pollution signal)
with col_r2:
    scatter_df = df.dropna(subset=["Avg BOD", "Avg DO"]).copy()
    scatter_df = scatter_df[scatter_df["Avg BOD"] < 200]  # exclude extreme outliers for readability
    fig4 = px.scatter(
        scatter_df,
        x="Avg BOD", y="Avg DO",
        color="State Name",
        hover_data=["Name of Monitoring Location", "Type Water Body", "WQ Grade"],
        opacity=0.7,
        labels={"Avg BOD": "Avg BOD (mg/L)", "Avg DO": "Avg DO (mg/L)"},
        title="BOD vs Dissolved Oxygen by Location<br><sup>High BOD + Low DO = severely polluted</sup>",
    )
    fig4.add_hline(y=DO_MIN,   line_dash="dot", line_color="blue",  annotation_text="Min safe DO")
    fig4.add_vline(x=BOD_SAFE, line_dash="dot", line_color="red",   annotation_text="Max safe BOD")
    fig4.update_layout(height=380, showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

# ── Parameter comparison bar ──────────────────────────────────────────────────
st.markdown("### Parameter Averages vs Safe Limits")
params = {
    "BOD (mg/L)":    (df["Avg BOD"].mean(),            BOD_SAFE),
    "Dissolved O₂":  (df["Avg DO"].mean(),              DO_MIN),
    "pH":            (df["Avg pH"].mean(),              (PH_MIN + PH_MAX) / 2),
    "Nitrate (mg/L)":(df["Avg Nitrate"].mean(),         10.0),
    "Fecal Coliform":(df["Avg Fecal Coliform"].mean(),  FC_SAFE),
}
param_df = pd.DataFrame(
    [(k, v[0], v[1]) for k, v in params.items()],
    columns=["Parameter", "Observed Average", "Safe Limit"],
).dropna()

fig5 = go.Figure()
fig5.add_bar(x=param_df["Parameter"], y=param_df["Observed Average"],
             name="Observed Avg", marker_color="#1f77b4")
fig5.add_bar(x=param_df["Parameter"], y=param_df["Safe Limit"],
             name="Safe Limit", marker_color="#aec7e8", marker_opacity=0.6)
fig5.update_layout(barmode="group", height=340,
                   legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ── WQ Grade breakdown ────────────────────────────────────────────────────────
st.markdown("### Water Quality Grade Breakdown (by BOD)")
grade_order = ["A – Excellent", "B – Good", "C – Moderate", "D – Poor", "E – Very Poor", "F – Critical", "Unknown"]
grade_colors = {
    "A – Excellent": "#2ca02c",
    "B – Good":      "#98df8a",
    "C – Moderate":  "#ffbb78",
    "D – Poor":      "#ff7f0e",
    "E – Very Poor": "#d62728",
    "F – Critical":  "#8c1c1c",
    "Unknown":       "#aaaaaa",
}
grade_counts = df["WQ Grade"].value_counts().reindex(grade_order).dropna().reset_index()
grade_counts.columns = ["Grade", "Locations"]
grade_counts["Color"] = grade_counts["Grade"].map(grade_colors)

fig6 = px.bar(
    grade_counts, x="Grade", y="Locations",
    color="Grade", color_discrete_map=grade_colors,
    title="Locations by Water Quality Grade",
    labels={"Locations": "# Locations"},
)
fig6.update_layout(showlegend=False, height=320)
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# ── Pollution ranking table ───────────────────────────────────────────────────
st.markdown("### Most Polluted Water Bodies (Top 20 by Avg BOD)")

ranking_cols = [
    "Name of Monitoring Location", "State Name", "Type Water Body",
    "Avg BOD", "Avg DO", "Avg pH", "Avg Fecal Coliform", "WQ Grade",
]
ranking_df = (
    df[ranking_cols]
    .dropna(subset=["Avg BOD"])
    .sort_values("Avg BOD", ascending=False)
    .head(20)
    .reset_index(drop=True)
)
ranking_df.index += 1

st.dataframe(
    ranking_df.style.background_gradient(subset=["Avg BOD"], cmap="RdYlGn_r")
                    .format({"Avg BOD": "{:.2f}", "Avg DO": "{:.2f}",
                             "Avg pH": "{:.2f}", "Avg Fecal Coliform": "{:,.0f}"}),
    use_container_width=True,
)

st.markdown("---")

# ── Full filterable data table ────────────────────────────────────────────────
with st.expander("📋 View / Search All Records", expanded=False):
    search = st.text_input("Search by location name", "")
    display_df = df.copy()
    if search:
        display_df = display_df[
            display_df["Name of Monitoring Location"]
            .str.contains(search, case=False, na=False)
        ]
    st.dataframe(display_df.reset_index(drop=True), use_container_width=True)

    # CSV download
    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=csv_bytes,
        file_name="india_water_quality_filtered.csv",
        mime="text/csv",
    )

# ── Key insights ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Key Insights")

worst_state = (
    df_full.groupby("State Name")["Avg BOD"].mean().idxmax()
    if not df_full.empty else "N/A"
)
worst_bod = df_full.groupby("State Name")["Avg BOD"].mean().max() if not df_full.empty else 0
pct_critical = critical_bod / max(total_locs, 1) * 100

col_i1, col_i2, col_i3 = st.columns(3)
col_i1.info(
    f"**{worst_state}** has the highest average BOD at **{worst_bod:.1f} mg/L** — "
    f"**{worst_bod/BOD_SAFE:.0f}×** the WHO safe limit."
)
col_i2.warning(
    f"**{pct_critical:.0f}%** of monitored water bodies exceed the BOD safe limit of {BOD_SAFE} mg/L, "
    "indicating widespread organic pollution."
)
col_i3.success(
    "Dissolved oxygen averages "
    f"**{avg_do:.1f} mg/L** across monitored locations. "
    f"{'Above' if avg_do >= DO_MIN else 'Below'} the minimum safe threshold of {DO_MIN} mg/L."
)

st.caption("Dashboard built with Python · Streamlit · Plotly | Data: CPCB NWMP 2022")
