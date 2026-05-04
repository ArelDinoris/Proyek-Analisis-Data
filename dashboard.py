import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import os

# Set style matplotlib agar background putih
plt.style.use('default')

# Load data asli – TIDAK DIUBAH
day_df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'main_data.csv'))
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

hour_df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'hour.csv'))
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Mapping di hour_df (sesuai kode awal)
hour_df['season'] = hour_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})
hour_df['weathersit'] = hour_df['weathersit'].map({1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'})
hour_df['yr'] = hour_df['yr'].map({0: 2011, 1: 2012})

# ─── SIDEBAR FILTER INTERAKTIF ───────────────────────────────
st.sidebar.header('🔍 Filter Data')

# Filter tahun (0=2011, 1=2012 di day_df)
tahun_options = ['Semua', 2011, 2012]
tahun = st.sidebar.selectbox('Tahun', tahun_options)

# Filter musim (day_df season masih integer, kita petakan sementara)
season_label = ['Spring', 'Summer', 'Fall', 'Winter']
musim = st.sidebar.multiselect('Musim', season_label, default=season_label)

# Filter cuaca
weather_label = ['Clear', 'Mist', 'Light Rain/Snow', 'Heavy Rain/Snow']
cuaca = st.sidebar.multiselect('Kondisi Cuaca', weather_label, default=weather_label)

# Tambahan filter hari (opsional untuk hour/day)
hari_options = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
hari = st.sidebar.multiselect('Hari dalam Minggu', hari_options, default=hari_options)

# ─── SIAPKAN DATA VIEW TANPA MENGUBAH ASLI ─────────────────
# Buat DataFrame sementara dengan kolom bantu untuk filter
day_view = day_df.assign(
    season_str = day_df['season'].map({1:'Spring',2:'Summer',3:'Fall',4:'Winter'}),
    weather_str = day_df['weathersit'].map({1:'Clear',2:'Mist',3:'Light Rain/Snow',4:'Heavy Rain/Snow'}),
    year_str   = day_df['yr'].map({0:2011, 1:2012}),
    weekday_str = day_df['weekday'].map({0:'Sun',1:'Mon',2:'Tue',3:'Wed',4:'Thu',5:'Fri',6:'Sat'})
)

# Filter day_view
mask_day = pd.Series(True, index=day_view.index)
if tahun != 'Semua':
    mask_day &= (day_view['year_str'] == tahun)
mask_day &= day_view['season_str'].isin(musim)
mask_day &= day_view['weather_str'].isin(cuaca)
if hari:
    mask_day &= day_view['weekday_str'].isin(hari)
filtered_day = day_view[mask_day]

# hour_df sudah punya season, weathersit, yr sebagai string/int
mask_hour = pd.Series(True, index=hour_df.index)
if tahun != 'Semua':
    mask_hour &= (hour_df['yr'] == tahun)
mask_hour &= hour_df['season'].isin(musim)
mask_hour &= hour_df['weathersit'].isin(cuaca)
# map weekday ke nama
hour_weekday_str = hour_df['weekday'].map({0:'Sun',1:'Mon',2:'Tue',3:'Wed',4:'Thu',5:'Fri',6:'Sat'})
if hari:
    mask_hour &= hour_weekday_str.isin(hari)
filtered_hour = hour_df[mask_hour]

# ─── HEADER ─────────────────────────────────────────────────
st.title('🚴 Bike Sharing Dashboard')
st.markdown('**Nama:** Arel Lafito Dinoris | **Email:** areldinoris23@gmail.com | **ID:** areldinoris')
st.markdown('---')

# ─── TABS ────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(['📊 Ringkasan', '🌦 Cuaca & Musim', '⏰ Jam & Hari', '📈 Analisis Lanjutan'])

# ================================================================
# TAB 1: RINGKASAN (METRIK UTAMA)
# ================================================================
with tab1:
    if filtered_day.empty:
        st.warning('Tidak ada data dengan filter yang dipilih.')
    else:
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric('Total Penyewaan', f"{filtered_day['cnt'].sum():,}")
        col_m2.metric('Penyewaan Tertinggi (hari)', f"{filtered_day['cnt'].max():,}") 
        col_m3.metric('Rata-rata/Hari', f"{filtered_day['cnt'].mean():.0f}")
        if not filtered_hour.empty:
            col_m4.metric('Rata-rata/Jam', f"{filtered_hour['cnt'].mean():.0f}")

        # Growth hanya jika semua tahun
        if tahun == 'Semua':
            growth_series = filtered_day.groupby('year_str')['cnt'].sum()
            if 2011 in growth_series.index and 2012 in growth_series.index:
                pct_growth = ((growth_series[2012] - growth_series[2011]) / growth_series[2011]) * 100
                st.metric('Pertumbuhan 2011→2012', f"{pct_growth:.1f}%")
            else:
                st.caption('Pertumbuhan: data tidak lengkap')
        st.info('🔎 Data sesuai filter sidebar. Filter tahun, musim, cuaca, dan hari untuk melihat perubahan metrik.')

# ================================================================
# TAB 2: CUACA & MUSIM (PERTANYAAN 1)
# ================================================================
with tab2:
    st.subheader('📊 Pertanyaan 1: Pengaruh Cuaca & Musim terhadap Penyewaan')
    if filtered_day.empty:
        st.warning('Data tidak tersedia untuk filter ini.')
    else:
        fig1, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Plot musim
        season_order = ['Spring', 'Summer', 'Fall', 'Winter']
        season_avg = filtered_day.groupby('season_str')['cnt'].mean().reindex(season_order)
        axes[0].bar(season_avg.index, season_avg.values,
                    color=['#4CAF50', '#FFC107', '#F44336', '#2196F3'])
        axes[0].set_title('Rata-rata Penyewaan per Musim', fontsize=13)
        axes[0].set_xlabel('Musim')
        axes[0].set_ylabel('Rata-rata Penyewaan')
        for i, v in enumerate(season_avg.values):
            if not np.isnan(v):
                axes[0].text(i, v + 50, str(round(v)), ha='center', fontsize=10)

        # Plot cuaca
        weather_avg = filtered_day.groupby('weather_str')['cnt'].mean().sort_values(ascending=False)
        axes[1].bar(weather_avg.index, weather_avg.values, color='#42A5F5')
        axes[1].set_title('Rata-rata Penyewaan per Kondisi Cuaca', fontsize=13)
        axes[1].set_xlabel('Kondisi Cuaca')
        axes[1].set_ylabel('Rata-rata Penyewaan')
        axes[1].tick_params(axis='x', rotation=15)
        for i, v in enumerate(weather_avg.values):
            if not np.isnan(v):
                axes[1].text(i, v + 50, str(round(v)), ha='center', fontsize=10)

        plt.tight_layout()
        st.pyplot(fig1)
        plt.close(fig1)

        st.info('💡 Musim Fall + cuaca Clear adalah kombinasi terbaik. Cuaca Light Rain/Snow menurunkan penyewaan drastis.')

# ================================================================
# TAB 3: JAM & HARI (PERTANYAAN 2)
# ================================================================
with tab3:
    st.subheader('⏰ Pertanyaan 2: Puncak Penyewaan per Jam dan Hari')
    if filtered_hour.empty:
        st.warning('Data per jam tidak tersedia untuk filter ini.')
    else:
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
            if not np.isnan(v):
                axes2[1].text(i, v + 2, str(round(v)), ha='center', fontsize=9)

        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

        st.info('💡 Pola bimodal: puncak di jam 08.00 dan 17.00 (komuter). Hari Jumat tertinggi.')

# ================================================================
# TAB 4: ANALISIS LANJUTAN
# ================================================================
with tab4:
    st.subheader('📈 Analisis Lanjutan')
    if filtered_day.empty:
        st.warning('Data harian tidak tersedia untuk filter ini.')
    else:
        # Ringkasan statistik ringan
        casual_total = filtered_day['casual'].sum()
        registered_total = filtered_day['registered'].sum()
        prop_casual = casual_total/(casual_total+registered_total)*100 if (casual_total+registered_total)>0 else 0
        col_a, col_b, col_c = st.columns(3)
        col_a.metric('Casual', f"{casual_total:,}")
        col_b.metric('Registered', f"{registered_total:,}")
        col_c.metric('Proporsi Casual', f"{prop_casual:.1f}%")

        # Siapkan figure 2x2
        fig3, axes3 = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Tren Bulanan
        if 'year_str' in filtered_day.columns:
            monthly_trend = filtered_day.groupby(['year_str', 'mnth'])['cnt'].sum().reset_index()
            pivot_trend = monthly_trend.pivot(index='mnth', columns='year_str', values='cnt')
            for year_val in pivot_trend.columns:
                axes3[0, 0].plot(pivot_trend.index, pivot_trend[year_val],
                                marker='o', label=str(year_val), linewidth=2)
            axes3[0, 0].set_title('Tren Penyewaan Bulanan', fontsize=13)
            axes3[0, 0].set_xlabel('Bulan')
            axes3[0, 0].set_ylabel('Total Penyewaan')
            axes3[0, 0].set_xticks(range(1, 13))
            axes3[0, 0].set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun',
                                         'Jul','Agu','Sep','Okt','Nov','Des'])
            axes3[0, 0].legend()
            axes3[0, 0].grid(alpha=0.3)

        # 2. Proporsi Casual vs Registered
        axes3[0, 1].pie(
            [casual_total, registered_total],
            labels=['Casual', 'Registered'],
            autopct='%1.1f%%',
            colors=['#FFC107', '#4CAF50'],
            startangle=90,
            explode=(0.05, 0)
        )
        axes3[0, 1].set_title('Proporsi Pengguna', fontsize=13)

        # 3. Hari Kerja vs Libur
        workday_avg = filtered_day.groupby('workingday')['cnt'].mean()
        workday_labels = workday_avg.index.map({0: 'Libur/Weekend', 1: 'Hari Kerja'})
        axes3[1, 0].bar(workday_labels, workday_avg.values,
                       color=['#AB47BC', '#26A69A'], width=0.4)
        axes3[1, 0].set_title('Rata-rata Penyewaan: Hari Kerja vs Libur', fontsize=13)
        axes3[1, 0].set_ylabel('Rata-rata')
        for i, v in enumerate(workday_avg.values):
            axes3[1, 0].text(i, v + 30, str(round(v)), ha='center', fontsize=11)

        # 4. Scatter suhu vs penyewaan
        axes3[1, 1].scatter(
            filtered_day['temp'] * 41,  # denormalisasi
            filtered_day['cnt'],
            alpha=0.4,
            color='#FF7043',
            s=20
        )
        # Trendline
        z = np.polyfit(filtered_day['temp'] * 41, filtered_day['cnt'], 1)
        p = np.poly1d(z)
        x_line = np.linspace((filtered_day['temp'] * 41).min(), (filtered_day['temp'] * 41).max(), 100)
        axes3[1, 1].plot(x_line, p(x_line), color='#1565C0', linewidth=2, label='Trendline')
        axes3[1, 1].set_title('Korelasi Suhu vs Jumlah Penyewaan', fontsize=13)
        axes3[1, 1].set_xlabel('Suhu (°C)')
        axes3[1, 1].set_ylabel('Jumlah Penyewaan')
        axes3[1, 1].legend()
        axes3[1, 1].grid(alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

# ─── KESIMPULAN (MUNCUL DI BAWAH TABS) ─────────────────────
st.markdown('---')
st.subheader('✅ Kesimpulan')

col_kes1, col_kes2 = st.columns(2)
with col_kes1:
    st.markdown('**Pertanyaan 1**')
    st.markdown("""
    - Musim **Fall** dan cuaca **Clear** menghasilkan penyewaan tertinggi.
    - Cuaca buruk (**Light Rain/Snow**) turunkan penyewaan hingga 63%.
    **Rekomendasi:** Maksimalkan armada saat Fall + Clear, kurangi saat cuaca buruk.
    """)
with col_kes2:
    st.markdown('**Pertanyaan 2**')
    st.markdown("""
    - Puncak jam **08.00** dan **17.00** (komuter), hari **Jumat** tertinggi.
    **Rekomendasi:** Pastikan stok sepeda di titik strategis pada jam dan hari tersebut.
    """)

st.markdown('---')
st.caption('Sumber: Bike Sharing Dataset — Capital Bikeshare, Washington D.C. | Arel Lafito Dinoris')
