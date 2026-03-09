import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
from datetime import datetime

# Load data - perbaiki path
try:
    # Coba load dari direktori yang sama dengan script
    day_df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'main_data.csv'))
except:
    # Fallback untuk local development
    day_df = pd.read_csv('main_data.csv')

day_df['dteday'] = pd.to_datetime(day_df['dteday'])

# ── HEADER ──
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")
st.title('🚴 Bike Sharing Dashboard')
st.markdown('**Nama:** Arel Lafito Dinoris | **ID:** areldinoris')
st.markdown('---')

# ── SIDEBAR FILTER ──
st.sidebar.header('🔍 Filter Data')

# Filter tahun
year_options = sorted(day_df['yr'].unique())
selected_year = st.sidebar.selectbox('Pilih Tahun', year_options, index=0)

# Filter date range
min_date = day_df['dteday'].min().date()
max_date = day_df['dteday'].max().date()

start_date = st.sidebar.date_input(
    'Tanggal Mulai', 
    value=min_date,
    min_value=min_date,
    max_value=max_date
)

end_date = st.sidebar.date_input(
    'Tanggal Akhir', 
    value=max_date,
    min_value=min_date,
    max_value=max_date
)

# Validasi tanggal
if start_date > end_date:
    st.sidebar.error("Tanggal akhir harus setelah tanggal mulai")
    st.stop()

# Terapkan filter
filtered = day_df[
    (day_df['yr'] == selected_year) &
    (day_df['dteday'].dt.date >= start_date) &
    (day_df['dteday'].dt.date <= end_date)
]

if len(filtered) == 0:
    st.warning("⚠️ Tidak ada data untuk periode yang dipilih")
    st.stop()

st.sidebar.markdown(f'**Total data:** {len(filtered)} hari')

# ── METRIK RINGKASAN ──
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric('Total Penyewaan', f"{filtered['cnt'].sum():,}")
with col_m2:
    st.metric('Rata-rata/Hari', f"{filtered['cnt'].mean():.0f}")
with col_m3:
    st.metric('Penyewaan Tertinggi', f"{filtered['cnt'].max():,}")

st.markdown('---')

# ── PERTANYAAN 1: Musim & Cuaca ──
st.subheader('📊 Pertanyaan 1: Pengaruh Musim & Cuaca terhadap Penyewaan')

col1, col2 = st.columns(2)

with col1:
    season_order = ['Spring', 'Summer', 'Fall', 'Winter']
    season_avg = filtered.groupby('season')['cnt'].mean().reindex(season_order).dropna()
    
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    colors = ['#4CAF50', '#FFC107', '#F44336', '#2196F3']
    bars = ax1.bar(season_avg.index, season_avg.values, color=colors)
    ax1.set_title(f'Rata-rata Penyewaan per Musim ({selected_year})', fontsize=12, pad=15)
    ax1.set_xlabel('Musim')
    ax1.set_ylabel('Rata-rata Penyewaan')
    ax1.tick_params(axis='x', rotation=0)
    
    for i, v in enumerate(season_avg.values):
        ax1.text(i, v + 30, f'{int(v):,}', ha='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

with col2:
    weather_avg = filtered.groupby('weathersit')['cnt'].mean().sort_values(ascending=False)
    
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    bars = ax2.bar(weather_avg.index, weather_avg.values, color='#42A5F5')
    ax2.set_title(f'Rata-rata Penyewaan per Cuaca ({selected_year})', fontsize=12, pad=15)
    ax2.set_xlabel('Kondisi Cuaca')
    ax2.set_ylabel('Rata-rata Penyewaan')
    ax2.tick_params(axis='x', rotation=15)
    
    for i, v in enumerate(weather_avg.values):
        ax2.text(i, v + 30, f'{int(v):,}', ha='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

st.info('💡 **Insight:** Musim Fall dan cuaca Clear menghasilkan penyewaan tertinggi. Cuaca buruk menurunkan penyewaan drastis.')

st.markdown('---')

# ── PERTANYAAN 2: Tren Harian ──
st.subheader('⏰ Pertanyaan 2: Tren Penyewaan Harian')

# Tren harian
daily_trend = filtered.groupby('dteday')['cnt'].sum().reset_index()

fig3, ax3 = plt.subplots(figsize=(12, 5))
ax3.plot(daily_trend['dteday'], daily_trend['cnt'],
         color='#E53935', linewidth=2, marker='o', markersize=4)
ax3.fill_between(daily_trend['dteday'], daily_trend['cnt'],
                 alpha=0.2, color='#E53935')
ax3.set_title(f'Tren Penyewaan Harian ({start_date.strftime("%d %b %Y")} s/d {end_date.strftime("%d %b %Y")})', 
              fontsize=12, pad=15)
ax3.set_xlabel('Tanggal')
ax3.set_ylabel('Total Penyewaan')
ax3.tick_params(axis='x', rotation=45)
ax3.grid(True, alpha=0.3)

plt.tight_layout()
st.pyplot(fig3)
plt.close(fig3)

col3, col4 = st.columns(2)

with col3:
    day_map = {0:'Minggu', 1:'Senin', 2:'Selasa', 3:'Rabu', 4:'Kamis', 5:'Jumat', 6:'Sabtu'}
    weekday_avg = filtered.groupby('weekday')['cnt'].mean().rename(index=day_map)
    
    # Urutkan hari
    day_order = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    weekday_avg = weekday_avg.reindex(day_order)
    
    fig4, ax4 = plt.subplots(figsize=(8, 5))
    bars = ax4.bar(weekday_avg.index, weekday_avg.values, color='#AB47BC')
    ax4.set_title('Rata-rata Penyewaan per Hari', fontsize=12, pad=15)
    ax4.set_xlabel('Hari')
    ax4.set_ylabel('Rata-rata Penyewaan')
    ax4.tick_params(axis='x', rotation=45)
    
    for i, v in enumerate(weekday_avg.values):
        ax4.text(i, v + 10, f'{int(v):,}', ha='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig4)
    plt.close(fig4)

with col4:
    workday_avg = filtered.groupby('workingday')['cnt'].mean()
    labels = ['Libur/Weekend', 'Hari Kerja']
    workday_avg.index = [labels[i] for i in workday_avg.index]
    
    fig5, ax5 = plt.subplots(figsize=(8, 5))
    colors = ['#AB47BC', '#26A69A']
    bars = ax5.bar(workday_avg.index, workday_avg.values, color=colors, width=0.5)
    ax5.set_title('Hari Kerja vs Libur', fontsize=12, pad=15)
    ax5.set_xlabel('Tipe Hari')
    ax5.set_ylabel('Rata-rata Penyewaan')
    
    for i, v in enumerate(workday_avg.values):
        ax5.text(i, v + 30, f'{int(v):,}', ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig5)
    plt.close(fig5)

st.info('💡 **Insight:** Penyewaan tertinggi terjadi pada hari kerja, mengkonfirmasi penggunaan sebagai moda komuter.')

st.markdown('---')
st.caption('Sumber: Bike Sharing Dataset — Capital Bikeshare, Washington D.C.')
