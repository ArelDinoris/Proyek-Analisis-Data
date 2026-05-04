import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import os

plt.style.use('default')

# =====================================================
# LOAD DATA (ASLI - TIDAK DIUBAH)
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

# Tambahan kolom label untuk day_df (tidak menghapus kolom asli)
day_df['yr_label'] = day_df['yr'].map({0: 2011, 1: 2012})
day_df['season_label'] = day_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})
day_df['weather_label'] = day_df['weathersit'].map({
    1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'
})

# =====================================================
# KONFIGURASI HALAMAN
# =====================================================
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚴", layout="wide")

# =====================================================
# SIDEBAR FILTERS (INTERAKTIF, TIDAK MERUBAH DATA)
# =====================================================
st.sidebar.header("🔎 Dashboard Filters")

year_filter = st.sidebar.multiselect(
    "📅 Pilih Tahun",
    options=sorted(hour_df['yr'].unique()),
    default=sorted(hour_df['yr'].unique())
)

season_filter = st.sidebar.multiselect(
    "🍂 Pilih Musim",
    options=['Spring', 'Summer', 'Fall', 'Winter'],
    default=['Spring', 'Summer', 'Fall', 'Winter']
)

weather_filter = st.sidebar.multiselect(
    "🌤 Pilih Cuaca",
    options=hour_df['weathersit'].dropna().unique().tolist(),
    default=hour_df['weathersit'].dropna().unique().tolist()
)

workingday_filter = st.sidebar.selectbox(
    "📆 Tipe Hari",
    ["Semua", "Hari Kerja", "Libur/Weekend"]
)

date_range = st.sidebar.date_input(
    "📆 Rentang Tanggal",
    [day_df['dteday'].min(), day_df['dteday'].max()]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**👤 Dibuat oleh:**")
st.sidebar.markdown("Arel Lafito Dinoris")
st.sidebar.markdown("areldinoris23@gmail.com")

# =====================================================
# APLIKASI FILTER KE SALINAN DATA
# =====================================================
filtered_hour = hour_df[
    (hour_df['yr'].isin(year_filter)) &
    (hour_df['season'].isin(season_filter)) &
    (hour_df['weathersit'].isin(weather_filter))
]

if len(date_range) == 2:
    filtered_day = day_df[
        (day_df['dteday'] >= pd.to_datetime(date_range[0])) &
        (day_df['dteday'] <= pd.to_datetime(date_range[1]))
    ]
else:
    filtered_day = day_df.copy()

filtered_day = filtered_day[filtered_day['yr_label'].isin(year_filter)]
filtered_day = filtered_day[filtered_day['season_label'].isin(season_filter)]
filtered_day = filtered_day[filtered_day['weather_label'].isin(weather_filter)]

if workingday_filter == "Hari Kerja":
    filtered_day = filtered_day[filtered_day['workingday'] == 1]
elif workingday_filter == "Libur/Weekend":
    filtered_day = filtered_day[filtered_day['workingday'] == 0]

# =====================================================
# HEADER
# =====================================================
st.title("🚴 Bike Sharing Dashboard")
st.markdown(f"**Nama:** Arel Lafito Dinoris | **Email:** areldinoris23@gmail.com | **ID:** areldinoris")
st.markdown("---")

# =====================================================
# METRIK RINGKASAN (MENGGUNAKAN DATA TERFILTER)
# =====================================================
total_rentals = filtered_day['cnt'].sum() if len(filtered_day) > 0 else 0
max_rentals = filtered_day['cnt'].max() if len(filtered_day) > 0 else 0
avg_day = filtered_day['cnt'].mean() if len(filtered_day) > 0 else 0
avg_hour = filtered_hour['cnt'].mean() if len(filtered_hour) > 0 else 0

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric('Total Penyewaan', f"{total_rentals:,}")
col_m2.metric('Penyewaan Tertinggi', f"{max_rentals:,}")
col_m3.metric('Rata-rata/Hari', f"{avg_day:.0f}")
col_m4.metric('Rata-rata/Jam', f"{avg_hour:.0f}")

# Hitung pertumbuhan jika tersedia
growth_pct = 0
if len(filtered_day) > 0:
    g = filtered_day.groupby('yr_label')['cnt'].sum()
    if 2011 in g.index and 2012 in g.index:
        growth_pct = ((g[2012] - g[2011]) / g[2011]) * 100
col_extra1, col_extra2 = st.columns(2)
col_extra1.metric('Pertumbuhan 2011-2012', f"{growth_pct:.1f}%" if growth_pct != 0 else "N/A")

st.markdown("---")

# =====================================================
# TAB INTERAKTIF
# =====================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📌 Executive Summary",
    "🌦 Pertanyaan 1: Musim & Cuaca",
    "⏰ Pertanyaan 2: Waktu & Hari",
    "📈 Analisis Lanjutan",
    "✅ Kesimpulan"
])

# =====================================================
# TAB 1 — EXECUTIVE SUMMARY
# =====================================================
with tab1:
    st.subheader("📌 Executive Summary")

    metric_choice = st.selectbox(
        "Pilih Metrik untuk Tren Bulanan",
        ["Total Rentals", "Casual", "Registered"]
    )
    metric_map = {"Total Rentals": "cnt", "Casual": "casual", "Registered": "registered"}

    if len(filtered_day) > 0:
        monthly = filtered_day.groupby(filtered_day['dteday'].dt.month)[metric_map[metric_choice]].sum()
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.fill_between(monthly.index, monthly.values, alpha=0.3, color='#42A5F5')
        ax.plot(monthly.index, monthly.values, marker='o', color='#1565C0', linewidth=2.5)
        ax.set_title(f"Tren Bulanan — {metric_choice}", fontsize=13)
        ax.set_xlabel("Bulan")
        ax.set_ylabel(metric_choice)
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'])
        ax.grid(alpha=0.3)
        for x, y in zip(monthly.index, monthly.values):
            ax.annotate(f'{y:,.0f}', (x, y), textcoords="offset points", xytext=(0, 8),
                        ha='center', fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.warning("Tidak ada data yang sesuai dengan filter. Silakan sesuaikan filter.")

# =====================================================
# TAB 2 — PERTANYAAN 1: MUSIM & CUACA
# =====================================================
with tab2:
    st.subheader("📊 Pertanyaan 1: Pengaruh Musim dan Cuaca terhadap Penyewaan")

    chart_type = st.radio("Tipe Visualisasi", ["Bar Chart", "Line Chart"], horizontal=True)

    col_s, col_w = st.columns(2)

    with col_s:
        if len(filtered_hour) > 0:
            season_order = ['Spring', 'Summer', 'Fall', 'Winter']
            season_avg = filtered_hour.groupby('season')['cnt'].mean().reindex(season_order).dropna()

            fig, ax = plt.subplots(figsize=(6, 4))
            colors = ['#4CAF50', '#FFC107', '#F44336', '#2196F3'][:len(season_avg)]
            if chart_type == "Bar Chart":
                bars = ax.bar(season_avg.index, season_avg.values, color=colors)
                for bar, val in zip(bars, season_avg.values):
                    ax.text(bar.get_x() + bar.get_width()/2, val + 50,
                            f'{val:.0f}', ha='center', fontsize=10)
            else:
                ax.plot(season_avg.index, season_avg.values, marker='o',
                        color='#F44336', linewidth=2.5)
            ax.set_title('Rata-rata Penyewaan per Musim', fontsize=13)
            ax.set_xlabel('Musim')
            ax.set_ylabel('Rata-rata Penyewaan')
            ax.grid(alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.warning("Tidak ada data jam dengan filter ini.")

    with col_w:
        if len(filtered_hour) > 0:
            weather_avg = filtered_hour.groupby('weathersit')['cnt'].mean().sort_values(ascending=False)

            fig2, ax2 = plt.subplots(figsize=(6, 4))
            if chart_type == "Bar Chart":
                bars2 = ax2.bar(range(len(weather_avg)), weather_avg.values, color='#42A5F5')
                ax2.set_xticks(range(len(weather_avg)))
                ax2.set_xticklabels(weather_avg.index, rotation=15, ha='right', fontsize=9)
                for bar, val in zip(bars2, weather_avg.values):
                    ax2.text(bar.get_x() + bar.get_width()/2, val + 50,
                             f'{val:.0f}', ha='center', fontsize=10)
            else:
                ax2.plot(range(len(weather_avg)), weather_avg.values, marker='o',
                         color='#1565C0', linewidth=2.5)
                ax2.set_xticks(range(len(weather_avg)))
                ax2.set_xticklabels(weather_avg.index, rotation=15, ha='right', fontsize=9)
            ax2.set_title('Rata-rata Penyewaan per Kondisi Cuaca', fontsize=13)
            ax2.set_xlabel('Kondisi Cuaca')
            ax2.set_ylabel('Rata-rata Penyewaan')
            ax2.grid(alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)
        else:
            st.warning("Tidak ada data jam dengan filter ini.")

    st.info('💡 Fall + Clear weather adalah kombinasi terbaik. Cuaca Light Rain/Snow menurunkan penyewaan hingga 63% dibanding cuaca Clear.')

# =====================================================
# TAB 3 — PERTANYAAN 2: WAKTU & HARI
# =====================================================
with tab3:
    st.subheader("⏰ Pertanyaan 2: Pola Penyewaan Berdasarkan Jam dan Hari")

    col_h, col_d = st.columns(2)

    with col_h:
        if len(filtered_hour) > 0:
            hour_avg = filtered_hour.groupby('hr')['cnt'].mean()
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(hour_avg.index, hour_avg.values, marker='o', color='#E53935', linewidth=2)
            ax.axvline(x=8, color='gray', linestyle='--', alpha=0.7, label='Jam 08.00')
            ax.axvline(x=17, color='blue', linestyle='--', alpha=0.7, label='Jam 17.00')
            ax.set_title('Rata-rata Penyewaan per Jam', fontsize=13)
            ax.set_xlabel('Jam')
            ax.set_ylabel('Rata-rata Penyewaan')
            ax.set_xticks(range(0, 24))
            ax.legend()
            ax.grid(alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    with col_d:
        if len(filtered_hour) > 0:
            day_map = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
            weekday_avg = filtered_hour.groupby('weekday')['cnt'].mean().rename(index=day_map)
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            bars = ax2.bar(weekday_avg.index, weekday_avg.values, color='#AB47BC')
            ax2.set_title('Rata-rata Penyewaan per Hari', fontsize=13)
            ax2.set_xlabel('Hari')
            ax2.set_ylabel('Rata-rata Penyewaan')
            for bar, val in zip(bars, weekday_avg.values):
                ax2.text(bar.get_x() + bar.get_width()/2, val + 2,
                         f'{val:.0f}', ha='center', fontsize=9)
            ax2.grid(alpha=0.3, axis='y')
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)

    st.info('💡 Puncak di jam 08.00 dan 17.00 (pola komuter), dengan hari Jumat sebagai hari tersibuk.')

# =====================================================
# TAB 4 — ANALISIS LANJUTAN
# =====================================================
with tab4:
    st.subheader("📈 Analisis Lanjutan")

    if len(filtered_day) > 0:
        # Ringkasan statistik
        growth = filtered_day.groupby('yr_label')['cnt'].sum()
        if 2011 in growth.index and 2012 in growth.index:
            pct = ((growth[2012] - growth[2011]) / growth[2011]) * 100
        else:
            pct = None
        casual_total = filtered_day['casual'].sum()
        registered_total = filtered_day['registered'].sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('Total 2011', f"{growth.get(2011, 0):,}")
            st.metric('Total 2012', f"{growth.get(2012, 0):,}")
            if pct is not None:
                st.metric('Pertumbuhan', f"{pct:.1f}%")
        with col2:
            st.metric('Casual', f"{casual_total:,}")
            st.metric('Registered', f"{registered_total:,}")
        with col3:
            total = casual_total + registered_total
            st.metric('Proporsi Casual', f"{casual_total/total*100:.1f}%" if total else "N/A")
            st.metric('Proporsi Registered', f"{registered_total/total*100:.1f}%" if total else "N/A")

        st.markdown("---")

        # 4 plot dalam 2x2 grid
        fig3, axes3 = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Tren bulanan 2011 vs 2012
        monthly_trend = filtered_day.groupby(['yr_label', 'mnth'])['cnt'].sum().reset_index()
        pivot_trend = monthly_trend.pivot(index='mnth', columns='yr_label', values='cnt')
        if 2011 in pivot_trend.columns:
            axes3[0, 0].plot(pivot_trend.index, pivot_trend[2011],
                           marker='o', label='2011', color='#42A5F5', linewidth=2)
        if 2012 in pivot_trend.columns:
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

        # 2. Pie casual vs registered
        axes3[0, 1].pie(
            [casual_total, registered_total],
            labels=['Casual', 'Registered'],
            autopct='%1.1f%%',
            colors=['#FFC107', '#4CAF50'],
            startangle=90,
            explode=(0.05, 0)
        )
        axes3[0, 1].set_title('Proporsi Pengguna: Casual vs Registered', fontsize=13)

        # 3. Hari Kerja vs Libur
        workday_avg = filtered_day.groupby('workingday')['cnt'].mean()
        workday_avg.index = workday_avg.index.map({0: 'Libur/Weekend', 1: 'Hari Kerja'})
        axes3[1, 0].bar(workday_avg.index, workday_avg.values,
                       color=['#AB47BC', '#26A69A'], width=0.4)
        axes3[1, 0].set_title('Rata-rata Penyewaan: Hari Kerja vs Libur', fontsize=13)
        axes3[1, 0].set_xlabel('Tipe Hari')
        axes3[1, 0].set_ylabel('Rata-rata Penyewaan')
        for i, v in enumerate(workday_avg.values):
            axes3[1, 0].text(i, v + 30, str(round(v)), ha='center', fontsize=11)

        # 4. Korelasi suhu vs penyewaan
        axes3[1, 1].scatter(filtered_day['temp'] * 41, filtered_day['cnt'],
                           alpha=0.4, color='#FF7043', s=20)
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

        # Bonus: Casual vs Registered per bulan
        st.markdown("**Tren Casual vs Registered per Bulan**")
        monthly_seg = filtered_day.groupby(filtered_day['dteday'].dt.month)[['casual','registered']].sum()
        fig2, ax2 = plt.subplots(figsize=(12, 4))
        ax2.plot(monthly_seg.index, monthly_seg['casual'], marker='o',
                 label='Casual', color='#FFC107', linewidth=2)
        ax2.plot(monthly_seg.index, monthly_seg['registered'], marker='s',
                 label='Registered', color='#4CAF50', linewidth=2)
        ax2.set_title("Tren Bulanan Casual vs Registered", fontsize=13)
        ax2.set_xlabel("Bulan")
        ax2.set_ylabel("Total Penyewaan")
        ax2.set_xticks(range(1, 13))
        ax2.set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'])
        ax2.legend()
        ax2.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)
    else:
        st.warning("Tidak ada data harian yang sesuai dengan filter.")

# =====================================================
# TAB 5 — KESIMPULAN
# =====================================================
with tab5:
    st.subheader('✅ Kesimpulan')

    col_kes1, col_kes2 = st.columns(2)

    with col_kes1:
        st.markdown('**Pertanyaan 1**')
        st.markdown("""
        - **Musim Fall** dan **cuaca Clear** secara konsisten menghasilkan jumlah penyewaan tertinggi sepanjang 2011–2012.
        - Kondisi cuaca buruk (**Light Rain/Snow**) terbukti menurunkan penyewaan secara drastis hingga **63%** dibanding cuaca Clear.
        
        **Rekomendasi bisnis:**
        - Tingkatkan ketersediaan armada sepeda di **musim Fall** dengan cuaca cerah.
        - Kurangi operasional saat **cuaca buruk** untuk efisiensi biaya.
        """)

    with col_kes2:
        st.markdown('**Pertanyaan 2**')
        st.markdown("""
        - Penyewaan memuncak pada pukul **08.00** dan **17.00–18.00** yang mencerminkan pola penggunaan sepeda sebagai moda transportasi **komuter**.
        - **Hari Jumat** mencatat penyewaan tertinggi dalam seminggu.
        
        **Rekomendasi bisnis:**
        - Prioritaskan ketersediaan sepeda di **titik-titik strategis** (stasiun, perkantoran) pada jam dan hari tersebut.
        - Siapkan armada tambahan untuk mengakomodasi lonjakan permintaan di jam sibuk.
        """)

st.markdown('---')
st.caption('Sumber: Bike Sharing Dataset — Capital Bikeshare, Washington D.C. | Arel Lafito Dinoris')
