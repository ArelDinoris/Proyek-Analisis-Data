import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Load data
base_dir = os.path.dirname(__file__)
day_df = pd.read_csv(os.path.join(base_dir, 'main_data.csv'))
hour_df = pd.read_csv(os.path.join(base_dir, 'hour_data.csv'))

day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

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
filtered_day = day_df[
    (day_df['yr'] == selected_year) &
    (day_df['dteday'] >= pd.Timestamp(start_date)) &
    (day_df['dteday'] <= pd.Timestamp(end_date))
]
filtered_hour = hour_df[
    (hour_df['yr'] == selected_year) &
    (hour_df['dteday'] >= pd.Timestamp(start_date)) &
    (hour_df['dteday'] <= pd.Timestamp(end_date))
]

st.sidebar.markdown(f'**Total data:** {len(filtered_day)} hari')

# ── METRIK RINGKASAN ──
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric('Total Penyewaan', f"{filtered_day['cnt'].sum():,}")
col_m2.metric('Rata-rata/Hari', f"{filtered_day['cnt'].mean():.0f}")
col_m3.metric('Penyewaan Tertinggi', f"{filtered_day['cnt'].max():,}")

st.markdown('---')

# ── PERTANYAAN 1: Musim & Cuaca ──
st.subheader('📊 Pertanyaan 1: Bagaimana pengaruh kondisi cuaca dan musim terhadap jumlah penyewaan sepeda harian pada tahun 2011–2012?')

fig1, axes1 = plt.subplots(1, 2, figsize=(14, 5))

# Plot musim
season_order = ['Spring', 'Summer', 'Fall', 'Winter']
season_avg = filtered_day.groupby('season')['cnt'].mean().reindex(season_order)
axes1[0].bar(season_avg.index, season_avg.values,
             color=['#4CAF50', '#FFC107', '#F44336', '#2196F3'])
axes1[0].set_title('Rata-rata Penyewaan per Musim', fontsize=13)
axes1[0].set_xlabel('Musim')
axes1[0].set_ylabel('Rata-rata Penyewaan')
for i, v in enumerate(season_avg.values):
    axes1[0].text(i, v + 50, str(round(v)), ha='center', fontsize=10)

# Plot cuaca
weather_avg = filtered_day.groupby('weathersit')['cnt'].mean().sort_values(ascending=False)
axes1[1].bar(weather_avg.index, weather_avg.values, color='#42A5F5')
axes1[1].set_title('Rata-rata Penyewaan per Kondisi Cuaca', fontsize=13)
axes1[1].set_xlabel('Kondisi Cuaca')
axes1[1].set_ylabel('Rata-rata Penyewaan')
axes1[1].tick_params(axis='x', rotation=15)
for i, v in enumerate(weather_avg.values):
    axes1[1].text(i, v + 50, str(round(v)), ha='center', fontsize=10)

plt.tight_layout()
st.pyplot(fig1)

st.info('💡 Musim Fall dan cuaca Clear menghasilkan penyewaan tertinggi. Cuaca buruk menurunkan penyewaan drastis.')

st.markdown('---')

# ── PERTANYAAN 2: Peak Hour & Hari ──
st.subheader('⏰ Pertanyaan 2: Pada jam berapa dan hari apa penyewaan sepeda mencapai puncaknya dalam seminggu?')

fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))

# Plot per jam
hour_avg = filtered_hour.groupby('hr')['cnt'].mean()
axes2[0].plot(hour_avg.index, hour_avg.values, marker='o', color='#E53935', linewidth=2)
axes2[0].set_title('Rata-rata Penyewaan per Jam', fontsize=13)
axes2[0].set_xlabel('Jam')
axes2[0].set_ylabel('Rata-rata Penyewaan')
axes2[0].set_xticks(range(0, 24))
axes2[0].axvline(x=8, color='gray', linestyle='--', alpha=0.5, label='Jam 08.00')
axes2[0].axvline(x=17, color='blue', linestyle='--', alpha=0.5, label='Jam 17.00')
axes2[0].legend()

# Plot per hari
day_map = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
weekday_avg = filtered_hour.groupby('weekday')['cnt'].mean().rename(index=day_map)
axes2[1].bar(weekday_avg.index, weekday_avg.values, color='#AB47BC')
axes2[1].set_title('Rata-rata Penyewaan per Hari', fontsize=13)
axes2[1].set_xlabel('Hari')
axes2[1].set_ylabel('Rata-rata Penyewaan')
for i, v in enumerate(weekday_avg.values):
    axes2[1].text(i, v + 2, str(round(v)), ha='center', fontsize=9)

plt.tight_layout()
st.pyplot(fig2)

st.info('💡 Grafik per jam menunjukkan dua puncak jelas (bimodal) di jam 08.00 dan 17.00 yang konsisten dengan jam komuter kerja, sementara dini hari (01.00–04.00) adalah waktu terendah.')

st.markdown('---')
st.caption('Sumber: Bike Sharing Dataset — Capital Bikeshare, Washington D.C. | Arel Lafito Dinoris')
