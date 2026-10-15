import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

from climaguard.data import read_dataset
from climaguard.risk import add_project_risk
from climaguard.styles import inject_styles
from climaguard.charts import plot_style

# ============================================================
# CLIMAGUARD
# DBMS + FODS CLIMATE INTELLIGENCE DASHBOARD
# Modular Streamlit application
# ============================================================

st.set_page_config(
    page_title="ClimaGuard | Climate Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# POWER-BI STYLE DESIGN
# ============================================================

inject_styles()


# ============================================================
# DATA LOADING
# ============================================================

DATA_FILE = Path(__file__).parent / "data" / "heatwave_imd_aws_dataset (1).csv"

@st.cache_data
def load_dataset(path):
    return read_dataset(path)


try:
    df = load_dataset(str(DATA_FILE))
except FileNotFoundError:
    st.error(
        "Dataset not found. Put 'heatwave_imd_aws_dataset (1).csv' "
        "in the same folder as main.py."
    )
    st.stop()
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()


# ============================================================
# DATASET HELPERS
# ============================================================

def first_existing(*names):
    for name in names:
        if name in df.columns:
            return name
    return None


TEMP_COL = first_existing("Max_Temperature_C")
MIN_TEMP_COL = first_existing("Min_Temperature_C")
HUMIDITY_COL = first_existing("Relative_Humidity_Pct")
WIND_COL = first_existing("Wind_Speed_kmh")
ANOMALY_COL = first_existing("Temp_Anomaly_C")
NORMAL_TEMP_COL = first_existing("Hist_Normal_MaxTemp_C")
REGION_COL = first_existing("IMD_Region")
STATION_COL = first_existing("AWS_Station_ID")
SEASON_COL = first_existing("Climatic_Season")
HOT_DAYS_COL = first_existing("Consecutive_Hot_Days")
HOTSPOT_COL = first_existing("Heatwave_Hotspot_Flag")
SEVERITY_COL = first_existing("Heatwave_Severity_Class")
ADVISORY_COL = first_existing("LLM_Advisory_Alert_Level")
LAT_COL = first_existing("Latitude")
LON_COL = first_existing("Longitude")
RAIN_COL = first_existing("Rainfall_mm", "Rainfall")
PRESSURE_COL = first_existing("Pressure_hPa", "Pressure")


def safe_mean(data, col):
    if col is None or col not in data.columns:
        return np.nan
    return pd.to_numeric(data[col], errors="coerce").mean()


def safe_max(data, col):
    if col is None or col not in data.columns:
        return np.nan
    return pd.to_numeric(data[col], errors="coerce").max()


def safe_min(data, col):
    if col is None or col not in data.columns:
        return np.nan
    return pd.to_numeric(data[col], errors="coerce").min()


def fmt_num(value, suffix=""):
    if pd.isna(value):
        return "N/A"
    return f"{value:.1f}{suffix}"


df = add_project_risk(
    df,
    temp_col=TEMP_COL,
    anomaly_col=ANOMALY_COL,
    hot_days_col=HOT_DAYS_COL,
)


# ============================================================
# PLOT STYLE
# ============================================================


def panel_title(title, accent=""):
    if accent:
        return f'<div class="panel-title">{title} <span class="accent">{accent}</span></div>'
    return f'<div class="panel-title">{title}</div>'


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    '<div class="sidebar-brand">🌍 CLIMAGUARD</div>',
    unsafe_allow_html=True
)
st.sidebar.markdown(
    '<div class="sidebar-caption">Climate Intelligence & Multi-Hazard Early Warning</div>',
    unsafe_allow_html=True
)
st.sidebar.divider()

page = st.sidebar.radio(
    "DASHBOARD",
    [
        "🏠 Command Center",
        "🌡️ Weather Intelligence",
        "🔥 Heatwave Intelligence",
        "🌧️ Disaster Center",
        "📊 Climate Analytics",
        "🗺️ Regional Comparison",
        "📈 Historical Climate",
        "🤖 AI Risk Analysis",
        "🚨 Alerts & Advisories",
        "📋 Reports",
        "🗄️ Database Explorer"
    ]
)

st.sidebar.divider()

if REGION_COL:
    region_options = ["All"] + sorted(df[REGION_COL].dropna().astype(str).unique().tolist())
    selected_region = st.sidebar.selectbox("📍 IMD REGION", region_options)
else:
    selected_region = "All"

if SEASON_COL:
    season_options = ["All"] + sorted(df[SEASON_COL].dropna().astype(str).unique().tolist())
    selected_season = st.sidebar.selectbox("🌦️ SEASON", season_options)
else:
    selected_season = "All"

risk_filter = st.sidebar.selectbox(
    "🔥 PROJECT RISK",
    ["All", "NORMAL", "WATCH", "HIGH", "CRITICAL"]
)

if "Timestamp" in df.columns and df["Timestamp"].notna().any():
    min_date = df["Timestamp"].min().date()
    max_date = df["Timestamp"].max().date()
    selected_dates = st.sidebar.date_input(
        "📅 DATE RANGE",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
else:
    selected_dates = None

st.sidebar.divider()
st.sidebar.caption(f"📡 {len(df):,} dataset records")
st.sidebar.caption(f"🧭 {df[REGION_COL].nunique() if REGION_COL else 'N/A'} IMD regions")
st.sidebar.caption(f"🏭 {df[STATION_COL].nunique() if STATION_COL else 'N/A'} AWS stations")
st.sidebar.caption("● DATASET MODE")


# ============================================================
# GLOBAL FILTERING
# ============================================================

filtered = df.copy()

if REGION_COL and selected_region != "All":
    filtered = filtered[
        filtered[REGION_COL].astype(str) == selected_region
    ]

if SEASON_COL and selected_season != "All":
    filtered = filtered[
        filtered[SEASON_COL].astype(str) == selected_season
    ]

if risk_filter != "All":
    filtered = filtered[
        filtered["_Project_Risk_Level"] == risk_filter
    ]

if (
    "Timestamp" in filtered.columns
    and selected_dates is not None
    and isinstance(selected_dates, tuple)
    and len(selected_dates) == 2
):
    filtered = filtered[
        (filtered["Timestamp"].dt.date >= selected_dates[0]) &
        (filtered["Timestamp"].dt.date <= selected_dates[1])
    ]


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="dashboard-head">
    <div class="dashboard-title">
        CLIMATE INTELLIGENCE & <span>HEATWAVE</span>
    </div>
    <div class="dashboard-subtitle">
        🌡 Temperature Monitoring &nbsp;•&nbsp;
        🔥 Hotspot Analysis &nbsp;•&nbsp;
        🌍 Environmental Conditions &nbsp;•&nbsp;
        📊 FODS Analytics
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# COMMAND CENTER
# ============================================================

if page == "🏠 Command Center":

    avg_temp = safe_mean(filtered, TEMP_COL)
    max_temp = safe_max(filtered, TEMP_COL)
    min_temp = safe_min(filtered, MIN_TEMP_COL or TEMP_COL)
    avg_humidity = safe_mean(filtered, HUMIDITY_COL)

    if HOTSPOT_COL:
        high_hotspots = int(
            filtered[HOTSPOT_COL]
            .astype(str)
            .str.lower()
            .isin(["1", "true", "yes", "y", "hotspot"])
            .sum()
        )
    else:
        high_hotspots = int((filtered["_Project_Risk_Score"] >= 60).sum())

    kpis = [
        ("🌡", "AVERAGE TEMPERATURE", fmt_num(avg_temp, " °C"), "Filtered observations"),
        ("🔥", "MAXIMUM TEMPERATURE", fmt_num(max_temp, " °C"), "Highest observation"),
        ("❄", "MINIMUM TEMPERATURE", fmt_num(min_temp, " °C"), "Lowest observation"),
        ("🚨", "HIGH-RISK OBSERVATIONS", f"{high_hotspots:,}", "Heatwave / project risk"),
        ("🌍", "IMD REGIONS", f"{filtered[REGION_COL].nunique():,}" if REGION_COL else "N/A", "Regions in filter"),
        ("📡", "OBSERVATIONS", f"{len(filtered):,}", "Dataset records"),
    ]

    cols = st.columns(6)
    for col, (icon, label, value, note) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="kpi">
                <div class="kpi-label">{icon} {label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-small">{note}</div>
            </div>
            """, unsafe_allow_html=True)

    max_anomaly = safe_max(filtered, ANOMALY_COL)
    if pd.notna(max_anomaly) and max_anomaly >= 3:
        alert_text = (
            f"🚨 Elevated temperature anomaly detected. Maximum observed anomaly: "
            f"{max_anomaly:.1f} °C in the current filter."
        )
    else:
        alert_text = (
            "🟢 Dashboard operating normally. Use the sidebar filters to explore "
            "regions, seasons, dates and project-level heatwave risk."
        )

    st.markdown(
        f'<div class="alert-strip">{alert_text}</div>',
        unsafe_allow_html=True
    )

    # Temperature by region
    c1, c2 = st.columns([1.15, 1])

    with c1:
        st.markdown(
            panel_title("🌍 Average Temperature by IMD Region"),
            unsafe_allow_html=True
        )

        if REGION_COL and TEMP_COL and not filtered.empty:
            region_temp = (
                filtered.groupby(REGION_COL)[TEMP_COL]
                .mean()
                .sort_values()
                .reset_index()
            )

            fig = px.bar(
                region_temp,
                x=TEMP_COL,
                y=REGION_COL,
                orientation="h",
                color=TEMP_COL,
                color_continuous_scale=["#2bb3d6", "#f7c948", "#ff7a18", "#e84424"],
                text=TEMP_COL
            )
            fig.update_traces(texttemplate="%{text:.1f}°C", textposition="outside")
            fig.update_coloraxes(showscale=False)
            plot_style(fig, 285)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        else:
            st.info("Region/temperature data unavailable.")

    with c2:
        st.markdown(
            panel_title("🌡 Temperature Trend", "OVER TIME"),
            unsafe_allow_html=True
        )

        if "Timestamp" in filtered.columns and TEMP_COL and not filtered.empty:
            trend = (
                filtered.dropna(subset=["Timestamp", TEMP_COL])
                .set_index("Timestamp")[TEMP_COL]
                .resample("D")
                .mean()
                .reset_index()
            )

            fig = px.area(
                trend,
                x="Timestamp",
                y=TEMP_COL,
                color_discrete_sequence=["#ff8a24"]
            )

            fig.add_hline(
                y=40,
                line_dash="dash",
                line_color="#ef4444",
                annotation_text="Project heatwave reference: 40°C"
            )

            plot_style(fig, 285)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        else:
            st.info("Timestamp/temperature data unavailable.")

    # Three-card row
    c1, c2, c3 = st.columns([1, 1.05, 1])

    with c1:
        st.markdown(
            panel_title("🔥 Heatwave Severity Distribution"),
            unsafe_allow_html=True
        )

        if SEVERITY_COL and not filtered.empty:
            counts = filtered[SEVERITY_COL].astype(str).value_counts()
        else:
            counts = filtered["_Project_Risk_Level"].value_counts()

        fig = px.pie(
            values=counts.values,
            names=counts.index,
            hole=.62
        )
        fig.update_traces(textinfo="percent", textfont_size=10)
        fig.add_annotation(
            text=f"<b>{len(filtered):,}</b><br>Records",
            x=.5, y=.5, showarrow=False,
            font=dict(size=13, color="#f0f4f6")
        )
        plot_style(fig, 250)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with c2:
        st.markdown(
            panel_title("🔥 Top Heatwave Hotspots"),
            unsafe_allow_html=True
        )

        if REGION_COL:
            if HOTSPOT_COL:
                hotspot_mask = filtered[HOTSPOT_COL].astype(str).str.lower().isin(
                    ["1", "true", "yes", "y", "hotspot"]
                )
                hotspot_data = filtered[hotspot_mask]
            else:
                hotspot_data = filtered[filtered["_Project_Risk_Score"] >= 60]

            top = (
                hotspot_data.groupby(REGION_COL)
                .size()
                .sort_values(ascending=False)
                .head(8)
                .reset_index(name="Hotspot Observations")
            )

            if not top.empty:
                fig = px.bar(
                    top.sort_values("Hotspot Observations"),
                    x="Hotspot Observations",
                    y=REGION_COL,
                    orientation="h",
                    text="Hotspot Observations",
                    color="Hotspot Observations",
                    color_continuous_scale=["#f7c948", "#ff8a24", "#e84424"]
                )
                fig.update_traces(textposition="outside")
                fig.update_coloraxes(showscale=False)
                plot_style(fig, 250)
                st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            else:
                st.info("No hotspot observations in the selected filter.")
        else:
            st.info("Region column unavailable.")

    with c3:
        st.markdown(
            panel_title("🌦️ Season Distribution"),
            unsafe_allow_html=True
        )

        if SEASON_COL and not filtered.empty:
            season_counts = (
                filtered[SEASON_COL]
                .astype(str)
                .value_counts()
                .reset_index()
            )
            season_counts.columns = ["Season", "Observations"]

            fig = px.bar(
                season_counts.sort_values("Observations"),
                x="Observations",
                y="Season",
                orientation="h",
                color="Observations",
                color_continuous_scale=["#2bb3d6", "#8b7cf6", "#ff8a24"]
            )
            fig.update_coloraxes(showscale=False)
            plot_style(fig, 250)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        else:
            st.info("Season data unavailable.")

    # FODS visual row
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            panel_title("💧 Humidity Analysis", "OVER TIME"),
            unsafe_allow_html=True
        )
        if "Timestamp" in filtered.columns and HUMIDITY_COL:
            hum = (
                filtered.dropna(subset=["Timestamp", HUMIDITY_COL])
                .set_index("Timestamp")[HUMIDITY_COL]
                .resample("D")
                .mean()
                .reset_index()
            )
            fig = px.line(hum, x="Timestamp", y=HUMIDITY_COL,
                          color_discrete_sequence=["#2bb3d6"])
            plot_style(fig, 220)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with c2:
        st.markdown(
            panel_title("📈 Temperature Anomaly", "OVER TIME"),
            unsafe_allow_html=True
        )
        if "Timestamp" in filtered.columns and ANOMALY_COL:
            anom = (
                filtered.dropna(subset=["Timestamp", ANOMALY_COL])
                .set_index("Timestamp")[ANOMALY_COL]
                .resample("D")
                .mean()
                .reset_index()
            )
            fig = px.bar(
                anom, x="Timestamp", y=ANOMALY_COL,
                color=ANOMALY_COL,
                color_continuous_scale=["#2bb3d6", "#f7c948", "#e84424"]
            )
            fig.add_hline(y=0, line_color="rgba(255,255,255,.5)")
            fig.update_coloraxes(showscale=False)
            plot_style(fig, 220)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with c3:
        st.markdown(
            panel_title("💨 Wind Speed Analysis", "OVER TIME"),
            unsafe_allow_html=True
        )
        if "Timestamp" in filtered.columns and WIND_COL:
            wind = (
                filtered.dropna(subset=["Timestamp", WIND_COL])
                .set_index("Timestamp")[WIND_COL]
                .resample("D")
                .mean()
                .reset_index()
            )
            fig = px.area(wind, x="Timestamp", y=WIND_COL,
                          color_discrete_sequence=["#62c78e"])
            plot_style(fig, 220)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


# ============================================================
# WEATHER INTELLIGENCE
# ============================================================

elif page == "🌡️ Weather Intelligence":

    st.subheader("🌡️ Weather Intelligence")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Average Max Temperature", fmt_num(safe_mean(filtered, TEMP_COL), " °C"))
    c2.metric("Average Humidity", fmt_num(safe_mean(filtered, HUMIDITY_COL), " %"))
    c3.metric("Average Wind", fmt_num(safe_mean(filtered, WIND_COL), " km/h"))
    c4.metric("Average Anomaly", fmt_num(safe_mean(filtered, ANOMALY_COL), " °C"))

    c1, c2 = st.columns(2)

    with c1:
        if TEMP_COL and HUMIDITY_COL:
            fig = px.scatter(
                filtered,
                x=TEMP_COL,
                y=HUMIDITY_COL,
                color=SEASON_COL if SEASON_COL else None,
                hover_data=[REGION_COL] if REGION_COL else None,
                title="Temperature vs Relative Humidity"
            )
            plot_style(fig, 360)
            st.plotly_chart(fig, width="stretch")

    with c2:
        if TEMP_COL and WIND_COL:
            fig = px.scatter(
                filtered,
                x=TEMP_COL,
                y=WIND_COL,
                color=ANOMALY_COL if ANOMALY_COL else None,
                title="Temperature vs Wind Speed"
            )
            plot_style(fig, 360)
            st.plotly_chart(fig, width="stretch")

    if TEMP_COL and MIN_TEMP_COL:
        fig = px.histogram(
            filtered,
            x=TEMP_COL,
            marginal="box",
            title="Maximum Temperature Distribution",
            nbins=35,
            color_discrete_sequence=["#ff8a24"]
        )
        plot_style(fig, 350)
        st.plotly_chart(fig, width="stretch")


# ============================================================
# HEATWAVE INTELLIGENCE
# ============================================================

elif page == "🔥 Heatwave Intelligence":

    st.subheader("🔥 Heatwave Intelligence")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Peak Temperature", fmt_num(safe_max(filtered, TEMP_COL), " °C"))
    c2.metric("Peak Anomaly", fmt_num(safe_max(filtered, ANOMALY_COL), " °C"))
    c3.metric(
        "Longest Hot-Day Run",
        f"{safe_max(filtered, HOT_DAYS_COL):.0f}" if pd.notna(safe_max(filtered, HOT_DAYS_COL)) else "N/A"
    )
    c4.metric(
        "Hotspot Records",
        f"{int(filtered[HOTSPOT_COL].astype(str).str.lower().isin(['1','true','yes','y','hotspot']).sum()):,}"
        if HOTSPOT_COL else f"{int((filtered['_Project_Risk_Score'] >= 60).sum()):,}"
    )

    c1, c2 = st.columns(2)

    with c1:
        if TEMP_COL and ANOMALY_COL:
            fig = px.scatter(
                filtered,
                x=TEMP_COL,
                y=ANOMALY_COL,
                size=HOT_DAYS_COL if HOT_DAYS_COL else None,
                color=SEVERITY_COL if SEVERITY_COL else None,
                hover_data=[REGION_COL] if REGION_COL else None,
                title="Heatwave Signal: Temperature vs Anomaly"
            )
            plot_style(fig, 370)
            st.plotly_chart(fig, width="stretch")

    with c2:
        if REGION_COL and TEMP_COL:
            region = (
                filtered.groupby(REGION_COL)
                .agg(
                    Avg_Temperature=(TEMP_COL, "mean"),
                    Max_Temperature=(TEMP_COL, "max"),
                    Avg_Anomaly=(ANOMALY_COL, "mean") if ANOMALY_COL else (TEMP_COL, "mean")
                )
                .reset_index()
                .sort_values("Max_Temperature", ascending=False)
                .head(12)
            )

            fig = px.bar(
                region.sort_values("Max_Temperature"),
                x="Max_Temperature",
                y=REGION_COL,
                orientation="h",
                color="Avg_Anomaly",
                color_continuous_scale=["#2bb3d6", "#f7c948", "#e84424"],
                title="Regional Heatwave Exposure"
            )
            plot_style(fig, 370)
            st.plotly_chart(fig, width="stretch")

    st.markdown("### Heatwave severity records")
    display_cols = [
        c for c in [
            "Timestamp", STATION_COL, REGION_COL, TEMP_COL,
            ANOMALY_COL, HOT_DAYS_COL, HOTSPOT_COL, SEVERITY_COL,
            ADVISORY_COL
        ] if c
    ]
    st.dataframe(
        filtered[display_cols].head(100),
        width="stretch",
        hide_index=True
    )


# ============================================================
# DISASTER CENTER
# ============================================================

elif page == "🌧️ Disaster Center":

    st.subheader("🌧️ Multi-Hazard Disaster Center")

    # Project-level indicators derived from available climate variables.
    disaster = []

    avg_temp = safe_mean(filtered, TEMP_COL)
    max_temp = safe_max(filtered, TEMP_COL)
    avg_anom = safe_mean(filtered, ANOMALY_COL)
    avg_wind = safe_mean(filtered, WIND_COL)

    heat_risk = min(100, max(0, ((max_temp - 30) / 15) * 100)) if pd.notna(max_temp) else 0
    anomaly_risk = min(100, max(0, ((avg_anom + 1) / 6) * 100)) if pd.notna(avg_anom) else 0
    wind_risk = min(100, max(0, (avg_wind / 50) * 100)) if pd.notna(avg_wind) else 0

    if RAIN_COL:
        avg_rain = safe_mean(filtered, RAIN_COL)
        rain_risk = min(100, max(0, (avg_rain / 100) * 100))
    else:
        rain_risk = 0

    disaster = pd.DataFrame({
        "Hazard": ["Heatwave", "Temperature Anomaly", "Heavy Rainfall", "High Wind"],
        "Project Risk": [heat_risk, anomaly_risk, rain_risk, wind_risk]
    })

    fig = px.bar(
        disaster.sort_values("Project Risk"),
        x="Project Risk",
        y="Hazard",
        orientation="h",
        color="Project Risk",
        color_continuous_scale=["#32c48d", "#f7c948", "#ff8a24", "#e84424"],
        text="Project Risk"
    )
    fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    fig.update_coloraxes(showscale=False)
    plot_style(fig, 330)
    st.plotly_chart(fig, width="stretch")

    st.info(
        "These hazard scores are project analytics derived from the supplied dataset. "
        "They are not official disaster warnings."
    )

    if ADVISORY_COL:
        st.markdown("### Advisory level distribution")
        advisory = filtered[ADVISORY_COL].astype(str).value_counts().reset_index()
        advisory.columns = ["Advisory Level", "Records"]
        fig = px.pie(advisory, names="Advisory Level", values="Records", hole=.55)
        plot_style(fig, 300)
        st.plotly_chart(fig, width="stretch")


# ============================================================
# CLIMATE ANALYTICS — FODS
# ============================================================

elif page == "📊 Climate Analytics":

    st.subheader("📊 Climate Analytics — FODS")

    st.markdown(
        "This page uses the supplied FODS lab dataset for exploratory data analysis."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{len(filtered):,}")
    c2.metric("Columns", f"{len(filtered.columns):,}")
    c3.metric("Missing Cells", f"{int(filtered.isna().sum().sum()):,}")
    c4.metric(
        "Duplicate Rows",
        f"{int(filtered.duplicated().sum()):,}"
    )

    # Correlation heatmap
    numeric_cols = filtered.select_dtypes(include=np.number).columns.tolist()

    if len(numeric_cols) >= 2:
        corr = filtered[numeric_cols].corr()

        fig = px.imshow(
            corr,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale=["#2bb3d6", "#f5f5f5", "#e84424"],
            title="Correlation Heatmap"
        )
        plot_style(fig, 550)
        st.plotly_chart(fig, width="stretch")

    # Region-season heatmap
    if REGION_COL and SEASON_COL and TEMP_COL:
        pivot = filtered.pivot_table(
            index=REGION_COL,
            columns=SEASON_COL,
            values=TEMP_COL,
            aggfunc="mean"
        )

        fig = px.imshow(
            pivot,
            text_auto=".1f",
            aspect="auto",
            color_continuous_scale=["#2bb3d6", "#f7c948", "#e84424"],
            title="Region × Climatic Season Average Maximum Temperature"
        )
        plot_style(fig, 480)
        st.plotly_chart(fig, width="stretch")

    # 3D scatter
    if TEMP_COL and HUMIDITY_COL and WIND_COL:
        sample = filtered.dropna(
            subset=[TEMP_COL, HUMIDITY_COL, WIND_COL]
        )

        if len(sample) > 1500:
            sample = sample.sample(1500, random_state=42)

        fig = px.scatter_3d(
            sample,
            x=TEMP_COL,
            y=HUMIDITY_COL,
            z=WIND_COL,
            color=ANOMALY_COL if ANOMALY_COL else None,
            hover_data=[REGION_COL] if REGION_COL else None,
            title="3D Climate Feature Space"
        )
        fig.update_layout(
            height=600,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#dbe5ea")
        )
        st.plotly_chart(fig, width="stretch")

    # Outlier analysis
    if TEMP_COL:
        st.markdown("### Temperature outlier analysis")

        q1 = filtered[TEMP_COL].quantile(.25)
        q3 = filtered[TEMP_COL].quantile(.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = filtered[
            (filtered[TEMP_COL] < lower) |
            (filtered[TEMP_COL] > upper)
        ]

        c1, c2 = st.columns(2)
        c1.metric("IQR Lower Bound", f"{lower:.2f} °C")
        c2.metric("IQR Upper Bound", f"{upper:.2f} °C")

        st.dataframe(
            outliers.head(100),
            width="stretch",
            hide_index=True
        )


# ============================================================
# REGIONAL COMPARISON
# ============================================================

elif page == "🗺️ Regional Comparison":

    st.subheader("🗺️ Regional Climate Comparison")

    if REGION_COL and TEMP_COL:
        regional = filtered.groupby(REGION_COL).agg(
            Average_Temperature=(TEMP_COL, "mean"),
            Maximum_Temperature=(TEMP_COL, "max"),
            Minimum_Temperature=(MIN_TEMP_COL, "min") if MIN_TEMP_COL else (TEMP_COL, "min"),
            Average_Anomaly=(ANOMALY_COL, "mean") if ANOMALY_COL else (TEMP_COL, "mean"),
            Observations=(TEMP_COL, "count")
        ).reset_index()

        st.dataframe(regional, width="stretch", hide_index=True)

        fig = px.scatter(
            regional,
            x="Average_Temperature",
            y="Average_Anomaly",
            size="Observations",
            color="Maximum_Temperature",
            hover_name=REGION_COL,
            color_continuous_scale=["#2bb3d6", "#f7c948", "#e84424"],
            title="Regional Temperature vs Temperature Anomaly"
        )
        plot_style(fig, 430)
        st.plotly_chart(fig, width="stretch")


# ============================================================
# HISTORICAL CLIMATE
# ============================================================

elif page == "📈 Historical Climate":

    st.subheader("📈 Historical Climate Trends")

    if "Timestamp" in filtered.columns and TEMP_COL:
        historical = (
            filtered.dropna(subset=["Timestamp", TEMP_COL])
            .set_index("Timestamp")
            .resample("W")
            .agg(
                Average_Temperature=(TEMP_COL, "mean"),
                Maximum_Temperature=(TEMP_COL, "max"),
                Minimum_Temperature=(MIN_TEMP_COL, "min") if MIN_TEMP_COL else (TEMP_COL, "min")
            )
            .reset_index()
        )

        fig = px.line(
            historical,
            x="Timestamp",
            y=[
                "Average_Temperature",
                "Maximum_Temperature",
                "Minimum_Temperature"
            ],
            title="Weekly Temperature Trend"
        )
        plot_style(fig, 420)
        st.plotly_chart(fig, width="stretch")

    if ANOMALY_COL:
        anomaly_stats = (
            filtered.groupby(REGION_COL)[ANOMALY_COL].mean()
            .sort_values()
            .reset_index()
            if REGION_COL
            else pd.DataFrame()
        )

        if not anomaly_stats.empty:
            fig = px.bar(
                anomaly_stats,
                x=ANOMALY_COL,
                y=REGION_COL,
                orientation="h",
                color=ANOMALY_COL,
                color_continuous_scale=["#2bb3d6", "#f7c948", "#e84424"],
                title="Average Temperature Anomaly by Region"
            )
            fig.update_coloraxes(showscale=False)
            plot_style(fig, 380)
            st.plotly_chart(fig, width="stretch")


# ============================================================
# AI RISK ANALYSIS
# ============================================================

elif page == "🤖 AI Risk Analysis":

    st.subheader("🤖 Explainable Climate Risk Analysis")

    risk_summary = (
        filtered.groupby("_Project_Risk_Level")
        .size()
        .reindex(["NORMAL", "WATCH", "HIGH", "CRITICAL"], fill_value=0)
        .reset_index()
    )
    risk_summary.columns = ["Risk Level", "Records"]

    fig = px.bar(
        risk_summary,
        x="Risk Level",
        y="Records",
        color="Risk Level",
        title="Project-Level Risk Classification"
    )
    plot_style(fig, 350)
    st.plotly_chart(fig, width="stretch")

    peak = safe_max(filtered, TEMP_COL)
    anomaly = safe_max(filtered, ANOMALY_COL)
    hot_days = safe_max(filtered, HOT_DAYS_COL)

    st.markdown("### Explainable risk factors")

    factors = pd.DataFrame({
        "Factor": [
            "Maximum Temperature",
            "Temperature Anomaly",
            "Consecutive Hot Days"
        ],
        "Value": [
            peak if pd.notna(peak) else 0,
            anomaly if pd.notna(anomaly) else 0,
            hot_days if pd.notna(hot_days) else 0
        ]
    })

    fig = px.bar(
        factors,
        x="Value",
        y="Factor",
        orientation="h",
        color="Value",
        color_continuous_scale=["#2bb3d6", "#f7c948", "#e84424"]
    )
    fig.update_coloraxes(showscale=False)
    plot_style(fig, 300)
    st.plotly_chart(fig, width="stretch")

    st.info(
        "The risk score shown here is an explainable project feature-engineering "
        "model for the mini-project. It should not be presented as an official "
        "IMD warning algorithm."
    )


# ============================================================
# ALERTS & ADVISORIES
# ============================================================

elif page == "🚨 Alerts & Advisories":

    st.subheader("🚨 Alerts & Advisories")

    if ADVISORY_COL:
        alerts = (
            filtered.groupby(ADVISORY_COL)
            .size()
            .reset_index(name="Records")
            .sort_values("Records", ascending=False)
        )

        fig = px.bar(
            alerts,
            x="Records",
            y=ADVISORY_COL,
            orientation="h",
            color="Records",
            color_continuous_scale=["#32c48d", "#f7c948", "#ff8a24", "#e84424"]
        )
        fig.update_coloraxes(showscale=False)
        plot_style(fig, 360)
        st.plotly_chart(fig, width="stretch")

    alert_cols = [
        c for c in [
            "Timestamp", REGION_COL, STATION_COL, TEMP_COL,
            ANOMALY_COL, HOT_DAYS_COL, HOTSPOT_COL,
            SEVERITY_COL, ADVISORY_COL
        ] if c
    ]

    st.dataframe(
        filtered.sort_values(
            TEMP_COL, ascending=False
        )[alert_cols].head(150) if TEMP_COL else filtered[alert_cols].head(150),
        width="stretch",
        hide_index=True
    )


# ============================================================
# REPORTS
# ============================================================

elif page == "📋 Reports":

    st.subheader("📋 Climate Intelligence Reports")

    report = {}

    report["Generated At"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report["Records Analysed"] = len(filtered)
    report["Average Max Temperature"] = safe_mean(filtered, TEMP_COL)
    report["Maximum Temperature"] = safe_max(filtered, TEMP_COL)
    report["Average Humidity"] = safe_mean(filtered, HUMIDITY_COL)
    report["Average Wind Speed"] = safe_mean(filtered, WIND_COL)
    report["Average Temperature Anomaly"] = safe_mean(filtered, ANOMALY_COL)

    if REGION_COL:
        report["Regions"] = filtered[REGION_COL].nunique()

    report_df = pd.DataFrame(
        list(report.items()),
        columns=["Metric", "Value"]
    )

    st.dataframe(report_df, width="stretch", hide_index=True)

    csv_bytes = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Filtered Dataset CSV",
        data=csv_bytes,
        file_name="climaguard_filtered_data.csv",
        mime="text/csv"
    )


# ============================================================
# DATABASE EXPLORER
# ============================================================

elif page == "🗄️ Database Explorer":

    st.subheader("🗄️ Database Explorer")

    st.info(
        "The current version uses the supplied FODS CSV as the primary data source. "
        "This page prepares the project for the DBMS/MySQL layer."
    )

    st.markdown("### Dataset schema")

    schema = pd.DataFrame({
        "Column": filtered.columns,
        "Data Type": [str(filtered[c].dtype) for c in filtered.columns],
        "Missing Values": [int(filtered[c].isna().sum()) for c in filtered.columns],
        "Unique Values": [int(filtered[c].nunique()) for c in filtered.columns]
    })

    st.dataframe(schema, width="stretch", hide_index=True)

    st.markdown("### Sample records")
    st.dataframe(filtered.head(100), width="stretch", hide_index=True)

    st.markdown("### Future MySQL mapping")

    mapping = pd.DataFrame({
        "Relational Table": [
            "REGION",
            "WEATHER_STATION",
            "WEATHER_OBSERVATION",
            "HEATWAVE_EVENT",
            "ALERT"
        ],
        "Dataset Information": [
            "IMD_Region",
            "AWS_Station_ID, Latitude, Longitude, Elevation_m",
            "Timestamp, temperatures, humidity, wind, anomaly",
            "Heatwave_Hotspot_Flag, Heatwave_Severity_Class, Consecutive_Hot_Days",
            "LLM_Advisory_Alert_Level"
        ]
    })

    st.dataframe(mapping, width="stretch", hide_index=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption(
    "CLIMAGUARD • DBMS + FODS Mini Project • "
    "Dataset-driven prototype • Project risk indicators are illustrative, not official warnings."
)
