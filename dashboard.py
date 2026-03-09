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
st.markdown('**Nama:** Arel Lafito Dinoris | **Email:** [areldinoris23@gmail.com] | **ID:** areldinoris')
st.markdown('---')

# ── METRIK RINGKASAN ──
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric('Total Penyewaan (2011-2012)', f"{day_df['cnt'].sum():,}")
col_m2.metric('Rata-rata/Hari', f"{day_df['cnt'].mean():.0f}")
col_m3.metric('Penyewaan Tertinggi', f"{day_df['cnt'].max():,}")
col_m4.metric('Rata-rata/Jam', f"{hour_df['cnt'].mean():.0f}")

st.markdown('---')

# ── PERTANYAAN 1: Musim & Cuaca (Persis seperti IPYNB) ──
st.subheader('📊 Pertanyaan 1: Bagaimana pengaruh kondisi cuaca dan musim terhadap jumlah penyewaan sepeda harian pada tahun 2011–2012?')

fig1, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot musim
season_order = ['Spring', 'Summer', 'Fall', 'Winter']
season_avg = day_df.groupby('season')['cnt'].mean().reindex(season_order)
axes[0].bar(season_avg.index, season_avg.values,
            color=['#4CAF50', '#FFC107', '#F44336', '#2196F3'])
axes[0].set_title('Rata-rata Penyewaan per Musim (2011-2012)', fontsize=13)
axes[0].set_xlabel('Musim')
axes[0].set_ylabel('Rata-rata Penyewaan')
for i, v in enumerate(season_avg.values):
    axes[0].text(i, v + 50, str(round(v)), ha='center', fontsize=10)

# Plot cuaca
weather_avg = day_df.groupby('weathersit')['cnt'].mean().sort_values(ascending=False)
axes[1].bar(weather_avg.index, weather_avg.values, color='#42A5F5')
axes[1].set_title('Rata-rata Penyewaan per Kondisi Cuaca (2011-2012)', fontsize=13)
axes[1].set_xlabel('Kondisi Cuaca')
axes[1].set_ylabel('Rata-rata Penyewaan')
axes[1].tick_params(axis='x', rotation=15)
for i, v in enumerate(weather_avg.values):
    axes[1].text(i, v + 50, str(round(v)), ha='center', fontsize=10)

plt.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

st.info('💡Visualisasi musim dan cuaca mengkonfirmasi bahwa Fall + Clear weather adalah kombinasi terbaik untuk penyewaan sepeda. Cuaca Light Rain/Snow menyebabkan penurunan penyewaan hingga 63% dibanding cuaca Clear.')

st.markdown('---')

# ── PERTANYAAN 2: Pada jam berapa dan hari apa penyewaan sepeda mencapai puncaknya dalam seminggu?──
st.subheader('⏰ Pertanyaan 2: Pola Jam dan Hari dalam Seminggu')

fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))

# Plot per jam
hour_avg = hour_df.groupby('hr')['cnt'].mean()
axes2[0].plot(hour_avg.index, hour_avg.values, marker='o', color='#E53935', linewidth=2)
axes2[0].set_title('Rata-rata Penyewaan per Jam (2011-2012)', fontsize=13)
axes2[0].set_xlabel('Jam')
axes2[0].set_ylabel('Rata-rata Penyewaan')
axes2[0].set_xticks(range(0, 24))
axes2[0].axvline(x=8, color='gray', linestyle='--', alpha=0.5, label='Jam 08.00')
axes2[0].axvline(x=17, color='blue', linestyle='--', alpha=0.5, label='Jam 17.00')
axes2[0].legend()

# Plot per hari
day_map = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
weekday_avg = hour_df.groupby('weekday')['cnt'].mean().rename(index=day_map)
axes2[1].bar(weekday_avg.index, weekday_avg.values, color='#AB47BC')
axes2[1].set_title('Rata-rata Penyewaan per Hari (2011-2012)', fontsize=13)
axes2[1].set_xlabel('Hari')
axes2[1].set_ylabel('Rata-rata Penyewaan')
for i, v in enumerate(weekday_avg.values):
    axes2[1].text(i, v + 2, str(round(v)), ha='center', fontsize=9)

plt.tight_layout()
st.pyplot(fig2)
plt.close(fig2)

st.info('💡Grafik per jam menunjukkan dua puncak jelas (bimodal) di jam 08.00 dan 17.00 yang konsisten dengan jam komuter kerja, sementara dini hari (01.00–04.00) adalah waktu terendah dengan rata-rata di bawah 25 penyewaan per jam.')

st.markdown('---')
st.caption('Sumber: Bike Sharing Dataset — Capital Bikeshare, Washington D.C. | Arel Lafito Dinoris')
