import pandas as pd
import numpy as np
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
st.markdown('**Nama:** Arel Lafito Dinoris | **Email:** areldinoris23@gmail.com | **ID:** areldinoris')
st.markdown('---')

# ── METRIK RINGKASAN ──
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric('Total Penyewaan (2011-2012)', f"{day_df['cnt'].sum():,}")
col_m2.metric('Penyewaan Tertinggi', f"{day_df['cnt'].max():,}") 
col_m3.metric('Rata-rata/Hari', f"{day_df['cnt'].mean():.0f}")
col_m4.metric('Rata-rata/Jam', f"{hour_df['cnt'].mean():.0f}")

st.markdown('---')

# ── PERTANYAAN 1: Musim & Cuaca ──
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

st.info('💡 Visualisasi musim dan cuaca mengkonfirmasi bahwa Fall + Clear weather adalah kombinasi terbaik untuk penyewaan sepeda. Cuaca Light Rain/Snow menyebabkan penurunan penyewaan hingga 63% dibanding cuaca Clear.')

st.markdown('---')

# ── PERTANYAAN 2: Jam & Hari ──
st.subheader('⏰ Pertanyaan 2: Pada jam berapa dan hari apa penyewaan sepeda mencapai puncaknya dalam seminggu?')

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

st.info('💡 Grafik per jam menunjukkan dua puncak jelas (bimodal) di jam 08.00 dan 17.00 yang konsisten dengan jam komuter kerja, sementara dini hari (01.00–04.00) adalah waktu terendah dengan rata-rata di bawah 25 penyewaan per jam.')

st.markdown('---')

# ================================================================
# ANALISIS LANJUTAN: Tren Penyewaan & Segmentasi Pengguna
# ================================================================
st.subheader('📈 Analisis Lanjutan')

# --- 1. Tren Penyewaan Bulanan 2011 vs 2012 ---
monthly_trend = day_df.groupby(['yr', 'mnth'])['cnt'].sum().reset_index()
pivot_trend = monthly_trend.pivot(index='mnth', columns='yr', values='cnt')

fig3, axes3 = plt.subplots(2, 2, figsize=(16, 12))

# Plot tren bulanan
axes3[0, 0].plot(pivot_trend.index, pivot_trend[2011],
                marker='o', label='2011', color='#42A5F5', linewidth=2)
axes3[0, 0].plot(pivot_trend.index, pivot_trend[2012],
                marker='o', label='2012', color='#EF5350', linewidth=2)
axes3[0, 0].set_title('Tren Penyewaan Bulanan: 2011 vs 2012', fontsize=13)
axes3[0, 0].set_xlabel('Bulan')
axes3[0, 0].set_ylabel('Total Penyewaan')
axes3[0, 0].set_xticks(range(1, 13))
axes3[0, 0].set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun',
                             'Jul','Agu','Sep','Okt','Nov','Des'])
axes3[0, 0].legend()
axes3[0, 0].grid(alpha=0.3)

# --- 2. Proporsi Casual vs Registered ---
casual_total = day_df['casual'].sum()
registered_total = day_df['registered'].sum()

axes3[0, 1].pie(
    [casual_total, registered_total],
    labels=['Casual', 'Registered'],
    autopct='%1.1f%%',
    colors=['#FFC107', '#4CAF50'],
    startangle=90,
    explode=(0.05, 0)
)
axes3[0, 1].set_title('Proporsi Pengguna: Casual vs Registered', fontsize=13)

# --- 3. Penyewaan Hari Kerja vs Hari Libur ---
workday_avg = day_df.groupby('workingday')['cnt'].mean()
workday_avg.index = workday_avg.index.map({0: 'Libur/Weekend', 1: 'Hari Kerja'})

axes3[1, 0].bar(workday_avg.index, workday_avg.values,
               color=['#AB47BC', '#26A69A'], width=0.4)
axes3[1, 0].set_title('Rata-rata Penyewaan: Hari Kerja vs Libur', fontsize=13)
axes3[1, 0].set_xlabel('Tipe Hari')
axes3[1, 0].set_ylabel('Rata-rata Penyewaan')
for i, v in enumerate(workday_avg.values):
    axes3[1, 0].text(i, v + 30, str(round(v)), ha='center', fontsize=11)

# --- 4. Korelasi Suhu vs Jumlah Penyewaan ---
axes3[1, 1].scatter(
    day_df['temp'] * 41,  # denormalisasi ke Celsius
    day_df['cnt'],
    alpha=0.4,
    color='#FF7043',
    s=20
)
# Trendline
z = np.polyfit(day_df['temp'] * 41, day_df['cnt'], 1)
p = np.poly1d(z)
x_line = np.linspace((day_df['temp'] * 41).min(), (day_df['temp'] * 41).max(), 100)
axes3[1, 1].plot(x_line, p(x_line), color='#1565C0', linewidth=2, label='Trendline')
axes3[1, 1].set_title('Korelasi Suhu vs Jumlah Penyewaan', fontsize=13)
axes3[1, 1].set_xlabel('Suhu (°C)')
axes3[1, 1].set_ylabel('Jumlah Penyewaan')
axes3[1, 1].legend()
axes3[1, 1].grid(alpha=0.3)

plt.tight_layout()
st.pyplot(fig3)
plt.close(fig3)

# --- Ringkasan Statistik ---
growth = day_df.groupby('yr')['cnt'].sum()
pct = ((growth[2012] - growth[2011]) / growth[2011]) * 100

col1, col2 = st.columns(2)
with col1:
    st.metric('Pertumbuhan 2011 → 2012', f"{pct:.1f}%")
with col2:
    st.metric('Total Pengguna Registered', f"{registered_total:,}")

st.markdown('---')
st.caption('Sumber: Bike Sharing Dataset — Capital Bikeshare, Washington D.C. | Arel Lafito Dinoris')
