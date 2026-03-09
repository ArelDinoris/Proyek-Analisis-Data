import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Load data
day_df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'main_data.csv'))
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

# ── HEADER ──
st.title('🚴 Bike Sharing Dashboard')
st.markdown('**Nama:** Arel Lafito Dinoris | **ID:** areldinoris')
st.markdown('---')

# ── SIDEBAR FILTER ──
st.sidebar.header('🔍 Filter Data')

# Filter tahun
year_options = sorted(day_df['yr'].unique())
selected_year = st.sidebar.selectbox('Pilih Tahun', year_options)

# Filter date range
min_date = day_df['dteday'].min()
max_date = day_df['dteday'].max()
start_date, end_date = st.sidebar.date_input(
    'Pilih Rentang Tanggal',
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Terapkan filter
filtered = day_df[
    (day_df['yr'] == selected_year) &
    (day_df['dteday'] >= pd.Timestamp(start_date)) &
    (day_df['dteday'] <= pd.Timestamp(end_date))
]

st.sidebar.markdown(f'**Total data:** {len(filtered)} hari')

# ── METRIK RINGKASAN ──
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric('Total Penyewaan', f"{filtered['cnt'].sum():,}")
col_m2.metric('Rata-rata/Hari', f"{filtered['cnt'].mean():.0f}")
col_m3.metric('Penyewaan Tertinggi', f"{filtered['cnt'].max():,}")

st.markdown('---')

# ── PERTANYAAN 1: Musim & Cuaca ──
st.subheader('📊 Pertanyaan 1: Pengaruh Musim & Cuaca terhadap Penyewaan')

col1, col2 = st.columns(2)

with col1:
    season_order = ['Spring', 'Summer', 'Fall', 'Winter']
    season_avg = filtered.groupby('season')['cnt'].mean().reindex(season_order).dropna()
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    bars = ax1.bar(season_avg.index, season_avg.values,
                   color=['#4CAF50', '#FFC107', '#F44336', '#2196F3'])
    ax1.set_title(f'Rata-rata Penyewaan per Musim ({selected_year})', fontsize=11)
    ax1.set_xlabel('Musim')
    ax1.set_ylabel('Rata-rata Penyewaan')
    for i, v in enumerate(season_avg.values):
        ax1.text(i, v + 30, str(round(v)), ha='center', fontsize=9)
    st.pyplot(fig1)

with col2:
    weather_avg = filtered.groupby('weathersit')['cnt'].mean().sort_values(ascending=False)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.bar(weather_avg.index, weather_avg.values, color='#42A5F5')
    ax2.set_title(f'Rata-rata Penyewaan per Cuaca ({selected_year})', fontsize=11)
    ax2.set_xlabel('Kondisi Cuaca')
    ax2.set_ylabel('Rata-rata Penyewaan')
    ax2.tick_params(axis='x', rotation=15)
    for i, v in enumerate(weather_avg.values):
        ax2.text(i, v + 30, str(round(v)), ha='center', fontsize=9)
    st.pyplot(fig2)

st.info('💡 Musim Fall dan cuaca Clear menghasilkan penyewaan tertinggi. Cuaca buruk menurunkan penyewaan drastis.')

st.markdown('---')

# ── PERTANYAAN 2: Peak Hour & Hari ──
st.subheader('⏰ Pertanyaan 2: Tren Penyewaan Harian')

# Tren harian dalam rentang tanggal
daily_trend = filtered.groupby('dteday')['cnt'].sum().reset_index()
fig3, ax3 = plt.subplots(figsize=(12, 4))
ax3.plot(daily_trend['dteday'], daily_trend['cnt'],
         color='#E53935', linewidth=1.5)
ax3.fill_between(daily_trend['dteday'], daily_trend['cnt'],
                 alpha=0.2, color='#E53935')
ax3.set_title(f'Tren Penyewaan Harian ({start_date} s/d {end_date})', fontsize=11)
ax3.set_xlabel('Tanggal')
ax3.set_ylabel('Total Penyewaan')
ax3.tick_params(axis='x', rotation=45)
ax3.grid(alpha=0.3)
st.pyplot(fig3)

col3, col4 = st.columns(2)

with col3:
    day_map = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
    weekday_avg = filtered.groupby('weekday')['cnt'].mean().rename(index=day_map)
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    ax4.bar(weekday_avg.index, weekday_avg.values, color='#AB47BC')
    ax4.set_title('Rata-rata Penyewaan per Hari', fontsize=11)
    ax4.set_xlabel('Hari')
    ax4.set_ylabel('Rata-rata Penyewaan')
    for i, v in enumerate(weekday_avg.values):
        ax4.text(i, v + 10, str(round(v)), ha='center', fontsize=9)
    st.pyplot(fig4)

with col4:
    workday_avg = filtered.groupby('workingday')['cnt'].mean()
    workday_avg.index = workday_avg.index.map({0: 'Libur/Weekend', 1: 'Hari Kerja'})
    fig5, ax5 = plt.subplots(figsize=(6, 4))
    ax5.bar(workday_avg.index, workday_avg.values,
            color=['#AB47BC', '#26A69A'], width=0.4)
    ax5.set_title('Hari Kerja vs Libur', fontsize=11)
    ax5.set_xlabel('Tipe Hari')
    ax5.set_ylabel('Rata-rata Penyewaan')
    for i, v in enumerate(workday_avg.values):
        ax5.text(i, v + 30, str(round(v)), ha='center', fontsize=11)
    st.pyplot(fig5)

st.info('💡 Penyewaan tertinggi terjadi Kamis-Jumat. Hari kerja lebih tinggi dari hari libur, mengkonfirmasi penggunaan sebagai moda komuter.')

st.markdown('---')
st.caption('Sumber: Bike Sharing Dataset — Capital Bikeshare, Washington D.C. | Arel Lafito Dinoris')
