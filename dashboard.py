import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import os

plt.style.use('default')

# =====================================================
# LOAD DATA (TIDAK DIUBAH)
# =====================================================
day_df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'main_data.csv'))
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

hour_df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'hour.csv'))
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

hour_df['season'] = hour_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})
hour_df['weathersit'] = hour_df['weathersit'].map({
    1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'
})
hour_df['yr'] = hour_df['yr'].map({0: 2011, 1: 2012})

# =====================================================
# SIDEBAR FILTERS (INI YANG BIKIN INTERAKTIF)
# =====================================================
st.sidebar.header("🔎 Dashboard Filters")

year_filter = st.sidebar.multiselect(
    "Pilih Tahun",
    options=hour_df['yr'].unique(),
    default=hour_df['yr'].unique()
)

season_filter = st.sidebar.multiselect(
    "Pilih Musim",
    options=hour_df['season'].unique(),
    default=hour_df['season'].unique()
)

weather_filter = st.sidebar.multiselect(
    "Pilih Cuaca",
    options=hour_df['weathersit'].unique(),
    default=hour_df['weathersit'].unique()
)

workingday_filter = st.sidebar.selectbox(
    "Tipe Hari",
    ["Semua", "Hari Kerja", "Libur/Weekend"]
)

date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    [day_df['dteday'].min(), day_df['dteday'].max()]
)

# APPLY FILTER (TANPA MERUBAH DATA ASLI)
filtered_hour = hour_df[
    (hour_df['yr'].isin(year_filter)) &
    (hour_df['season'].isin(season_filter)) &
    (hour_df['weathersit'].isin(weather_filter))
]

filtered_day = day_df[
    (day_df['dteday'] >= pd.to_datetime(date_range[0])) &
    (day_df['dteday'] <= pd.to_datetime(date_range[1]))
]

if workingday_filter == "Hari Kerja":
    filtered_day = filtered_day[filtered_day['workingday'] == 1]
elif workingday_filter == "Libur/Weekend":
    filtered_day = filtered_day[filtered_day['workingday'] == 0]

# =====================================================
# HEADER
# =====================================================
st.title("🚴 BIKE SHARING INTERACTIVE DASHBOARD")
st.markdown("### Data Analyst Portfolio Version")

# =====================================================
# TABS NAVIGATION
# =====================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📌 Executive Summary",
    "🌦 Season & Weather",
    "⏰ Time Analysis",
    "📈 Advanced Analysis"
])

# =====================================================
# TAB 1 — EXECUTIVE SUMMARY
# =====================================================
with tab1:

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Rentals", f"{filtered_day['cnt'].sum():,}")
    col2.metric("Highest Daily Rentals", f"{filtered_day['cnt'].max():,}")
    col3.metric("Avg / Day", f"{filtered_day['cnt'].mean():.0f}")
    col4.metric("Avg / Hour", f"{filtered_hour['cnt'].mean():.0f}")

    st.markdown("---")

    metric_choice = st.selectbox(
        "Pilih Metric Trend",
        ["Total Rentals", "Casual", "Registered"]
    )

    metric_map = {
        "Total Rentals": "cnt",
        "Casual": "casual",
        "Registered": "registered"
    }

    monthly = filtered_day.groupby(filtered_day['dteday'].dt.month)[metric_map[metric_choice]].sum()

    fig, ax = plt.subplots()
    ax.plot(monthly.index, monthly.values, marker='o')
    ax.set_title(f"Monthly Trend — {metric_choice}")
    ax.set_xlabel("Month")
    ax.set_ylabel(metric_choice)
    st.pyplot(fig)

# =====================================================
# TAB 2 — SEASON & WEATHER
# =====================================================
with tab2:

    chart_type = st.radio("Tipe Visual", ["Bar Chart", "Line Chart"])

    season_avg = filtered_hour.groupby('season')['cnt'].mean()

    fig, ax = plt.subplots()

    if chart_type == "Bar Chart":
        ax.bar(season_avg.index, season_avg.values)
    else:
        ax.plot(season_avg.index, season_avg.values, marker='o')

    ax.set_title("Average Rentals by Season")
    st.pyplot(fig)

    weather_avg = filtered_hour.groupby('weathersit')['cnt'].mean()
    fig2, ax2 = plt.subplots()
    ax2.bar(weather_avg.index, weather_avg.values)
    ax2.set_title("Average Rentals by Weather")
    st.pyplot(fig2)

# =====================================================
# TAB 3 — TIME ANALYSIS
# =====================================================
with tab3:

    colA, colB = st.columns(2)

    with colA:
        hour_avg = filtered_hour.groupby('hr')['cnt'].mean()
        fig, ax = plt.subplots()
        ax.plot(hour_avg.index, hour_avg.values, marker='o')
        ax.set_title("Rentals by Hour")
        st.pyplot(fig)

    with colB:
        day_avg = filtered_hour.groupby('weekday')['cnt'].mean()
        fig2, ax2 = plt.subplots()
        ax2.bar(day_avg.index, day_avg.values)
        ax2.set_title("Rentals by Weekday")
        st.pyplot(fig2)

# =====================================================
# TAB 4 — ADVANCED ANALYSIS
# =====================================================
with tab4:

    st.subheader("Casual vs Registered")

    casual = filtered_day['casual'].sum()
    registered = filtered_day['registered'].sum()

    fig, ax = plt.subplots()
    ax.pie([casual, registered], labels=['Casual','Registered'], autopct='%1.1f%%')
    st.pyplot(fig)

    st.subheader("Temperature vs Rentals")

    fig2, ax2 = plt.subplots()
    ax2.scatter(filtered_day['temp']*41, filtered_day['cnt'], alpha=0.4)
    z = np.polyfit(filtered_day['temp']*41, filtered_day['cnt'], 1)
    p = np.poly1d(z)
    x_line = np.linspace((filtered_day['temp']*41).min(), (filtered_day['temp']*41).max(), 100)
    ax2.plot(x_line, p(x_line))
    ax2.set_xlabel("Temperature °C")
    ax2.set_ylabel("Rentals")
    st.pyplot(fig2)
