import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Load data
day_df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'main_data.csv'))
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

# Load hour data
hour_df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'hour.csv'))
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Mapping season dan weather seperti di notebook
hour_df['season'] = hour_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})
hour_df['weathersit'] = hour_df['weathersit'].map({
    1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'
})
hour_df['yr'] = hour_df['yr'].map({0: 2011, 1: 2012})

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

# Terapkan filter ke day_df
filtered_day = day_df[
    (day_df['yr'] == selected_year) &
    (day_df['dteday'] >= pd.Timestamp(start_date)) &
    (day_df['dteday'] <= pd.Timestamp(end_date))
]

# Terapkan filter ke hour_df
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

# ── PERTANYAAN 1: Musim & Cuaca (Seperti di IPYNB) ──
st.subheader('📊 Pertanyaan 1: Pengaruh Musim & Cuaca terhadap Penyewaan')

fig1, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot musim
season_order = ['Spring', 'Summer', 'Fall', 'Winter']
season_avg = filtered_day.groupby('season')['cnt'].mean().reindex(season_order).dropna()
axes[0].bar(season_avg.index, season_avg.values,
            color=['#4CAF50', '#FFC107', '#F44336', '#2196F3'])
axes[0].set_title(f'Rata-rata Penyewaan per Musim ({selected_year})', fontsize=13)
axes[0].set_xlabel('Musim')
axes[0].set_ylabel('Rata-rata Penyewaan')
for i, v in enumerate(season_avg.values):
    axes[0].text(i, v + 50, str(round(v)), ha='center', fontsize=10)

# Plot cuaca
weather_avg = filtered_day.groupby('weathersit')['cnt'].mean().sort_values(ascending=False)
axes[1].bar(weather_avg.index, weather_avg.values, color='#42A5F5')
axes[1].set_title(f'Rata-rata Penyewaan per Kondisi Cuaca ({selected_year})', fontsize=13)
axes[1].set_xlabel('Kondisi Cuaca')
axes[1].set_ylabel('Rata-rata Penyewaan')
axes[1].tick_params(axis='x', rotation=15)
for i, v in enumerate(weather_avg.values):
    axes[1].text(i, v + 50, str(round(v)), ha='center', fontsize=10)

plt.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

st.info('💡 Musim Fall dan cuaca Clear menghasilkan penyewaan tertinggi. Cuaca buruk menurunkan penyewaan drastis.')

st.markdown('---')

# ── PERTANYAAN 2: Jam & Hari (Seperti di IPYNB) ──
st.subheader('⏰ Pertanyaan 2: Pola Jam dan Hari dalam Seminggu')

fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))

# Plot per jam
hour_avg = filtered_hour.groupby('hr')['cnt'].mean()
axes2[0].plot(hour_avg.index, hour_avg.values, marker='o', color='#E53935', linewidth=2)
axes2[0].set_title(f'Rata-rata Penyewaan per Jam ({selected_year})', fontsize=13)
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
axes2[1].set_title(f'Rata-rata Penyewaan per Hari ({selected_year})', fontsize=13)
axes2[1].set_xlabel('Hari')
axes2[1].set_ylabel('Rata-rata Penyewaan')
for i, v in enumerate(weekday_avg.values):
    axes2[1].text(i, v + 2, str(round(v)), ha='center', fontsize=9)

plt.tight_layout()
st.pyplot(fig2)
plt.close(fig2)

st.info('💡 Penyewaan memuncak jam 08.00 dan 17.00-18.00 (pola komuter). Kamis-Jumat adalah hari tersibuk.')

st.markdown('---')
st.caption('Sumber: Bike Sharing Dataset — Capital Bikeshare, Washington D.C. | Arel Lafito Dinoris')
