import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import os

plt.style.use('default')

# =====================================================
# LOAD DATA
# =====================================================
day_df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'main_data.csv'))
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

hour_df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'hour.csv'))
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# ── Deteksi & normalisasi kolom yr ──
if hour_df['yr'].max() <= 1:
    hour_df['yr'] = hour_df['yr'].map({0: 2011, 1: 2012})
if day_df['yr'].max() <= 1:
    day_df['yr'] = day_df['yr'].map({0: 2011, 1: 2012})

# ── Mapping season ──
season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
if hour_df['season'].dtype != object:
    hour_df['season'] = hour_df['season'].map(season_map)
if day_df['season'].dtype != object:
    day_df['season'] = day_df['season'].map(season_map)

# ── Mapping weathersit ──
weather_map = {1: 'Clear', 2: 'Mist', 3: 'Light Rain/Snow', 4: 'Heavy Rain/Snow'}
if hour_df['weathersit'].dtype != object:
    hour_df['weathersit'] = hour_df['weathersit'].map(weather_map)
if day_df['weathersit'].dtype != object:
    day_df['weathersit'] = day_df['weathersit'].map(weather_map)

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚴", layout="wide")

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1565C0, #42A5F5);
        padding: 22px 32px;
        border-radius: 14px;
        color: white;
        margin-bottom: 18px;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p  { margin: 6px 0 0 0; opacity: 0.88; font-size: 0.95rem; }
    div[data-testid="stTabs"] button { font-size: 0.93rem; font-weight: 600; }
    div[data-testid="metric-container"] {
        background: white;
        border-radius: 10px;
        padding: 10px 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border-left: 4px solid #42A5F5;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR FILTERS
# =====================================================
st.sidebar.markdown("## 🔎 Dashboard Filters")
st.sidebar.markdown("---")

year_options   = sorted(day_df['yr'].dropna().unique().tolist())
season_options = ['Spring', 'Summer', 'Fall', 'Winter']

year_filter = st.sidebar.multiselect(
    "📅 Pilih Tahun",
    options=year_options,
    default=year_options,
    help="Pilih 2011, 2012, atau keduanya"
)
season_filter = st.sidebar.multiselect(
    "🍂 Pilih Musim",
    options=season_options,
    default=season_options,
    help="Pilih satu atau semua musim"
)

st.sidebar.markdown("---")
st.sidebar.markdown("**👤 Dibuat oleh:**")
st.sidebar.markdown("Arel Lafito Dinoris")
st.sidebar.markdown("areldinoris23@gmail.com | ID: areldinoris")

# =====================================================
# APPLY FILTERS
# =====================================================
if not year_filter:
    year_filter = year_options
if not season_filter:
    season_filter = season_options

filtered_day = day_df[
    (day_df['yr'].isin(year_filter)) &
    (day_df['season'].isin(season_filter))
].copy()

filtered_hour = hour_df[
    (hour_df['yr'].isin(year_filter)) &
    (hour_df['season'].isin(season_filter))
].copy()

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<div class="main-header">
    <h1>🚴 Bike Sharing Dashboard</h1>
    <p><b>Nama:</b> Arel Lafito Dinoris &nbsp;|&nbsp;
       <b>Email:</b> areldinoris23@gmail.com &nbsp;|&nbsp;
       <b>ID:</b> areldinoris</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# KPI METRICS
# =====================================================
total_filt   = int(filtered_day['cnt'].sum())  if len(filtered_day) > 0 else 0
highest_filt = int(filtered_day['cnt'].max())  if len(filtered_day) > 0 else 0
avg_day_filt = filtered_day['cnt'].mean()       if len(filtered_day) > 0 else 0
avg_hr_filt  = filtered_hour['cnt'].mean()      if len(filtered_hour) > 0 else 0

total_all    = int(day_df['cnt'].sum())
avg_day_all  = day_df['cnt'].mean()
avg_hour_all = hour_df['cnt'].mean()

growth_pct = 0
if len(filtered_day) > 0:
    g = filtered_day.groupby('yr')['cnt'].sum()
    if 2011 in g.index and 2012 in g.index:
        growth_pct = ((g[2012] - g[2011]) / g[2011]) * 100

col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
col_m1.metric("🚲 Total Penyewaan",     f"{total_filt:,}",
              delta=f"dari {total_all:,} total")
col_m2.metric("📈 Penyewaan Tertinggi", f"{highest_filt:,}")
col_m3.metric("📊 Rata-rata/Hari",      f"{avg_day_filt:.0f}",
              delta=f"baseline {avg_day_all:.0f}")
col_m4.metric("⏱ Rata-rata/Jam",       f"{avg_hr_filt:.0f}",
              delta=f"baseline {avg_hour_all:.0f}")
col_m5.metric("📉 Pertumbuhan YoY",
              f"{growth_pct:.1f}%" if growth_pct != 0 else "N/A")

st.markdown("---")

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📌 Executive Summary",
    "🌦 Musim & Cuaca",
    "⏰ Analisis Waktu",
    "📈 Analisis Lanjutan",
    "✅ Kesimpulan"
])

# ─────────────────────────────────────────────────────
# TAB 1 — EXECUTIVE SUMMARY
# ─────────────────────────────────────────────────────
with tab1:
    st.subheader("📌 Executive Summary")

    if len(filtered_day) == 0:
        st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
    else:
        metric_choice = st.selectbox(
            "Pilih Metric Tren Bulanan",
            ["Total Rentals", "Casual", "Registered"],
            key="metric_tab1"
        )
        metric_map = {"Total Rentals": "cnt", "Casual": "casual", "Registered": "registered"}
        col_metric = metric_map[metric_choice]

        monthly = filtered_day.groupby(filtered_day['dteday'].dt.month)[col_metric].sum()

        fig, ax = plt.subplots(figsize=(13, 4))
        ax.fill_between(monthly.index, monthly.values, alpha=0.25, color='#42A5F5')
        ax.plot(monthly.index, monthly.values, marker='o', color='#1565C0', linewidth=2.5)
        ax.set_title(f"Tren Bulanan — {metric_choice}", fontsize=14, fontweight='bold')
        ax.set_xlabel("Bulan")
        ax.set_ylabel(metric_choice)
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun',
                            'Jul','Agu','Sep','Okt','Nov','Des'])
        ax.grid(alpha=0.3)
        for x, y in zip(monthly.index, monthly.values):
            ax.annotate(f'{y:,.0f}', (x, y),
                        textcoords="offset points", xytext=(0, 8),
                        ha='center', fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Total Penyewaan per Tahun**")
            yearly = filtered_day.groupby('yr')['cnt'].sum()
            fig2, ax2 = plt.subplots(figsize=(5, 3.5))
            bars = ax2.bar(yearly.index.astype(str), yearly.values,
                           color=['#42A5F5','#EF5350'][:len(yearly)], width=0.4)
            ax2.set_title("Total Penyewaan per Tahun", fontsize=12)
            ax2.set_ylabel("Total")
            ax2.grid(alpha=0.3, axis='y')
            for bar, val in zip(bars, yearly.values):
                ax2.text(bar.get_x() + bar.get_width()/2, val + 300,
                         f'{val:,}', ha='center', fontsize=10, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)

        with col_b:
            st.markdown("**Distribusi Tipe Pengguna**")
            fig3, ax3 = plt.subplots(figsize=(5, 3.5))
            ax3.pie([filtered_day['casual'].sum(), filtered_day['registered'].sum()],
                    labels=['Casual','Registered'], autopct='%1.1f%%',
                    colors=['#FFC107','#4CAF50'], startangle=90, explode=(0.05,0))
            ax3.set_title("Proporsi Pengguna", fontsize=12)
            plt.tight_layout()
            st.pyplot(fig3)
            plt.close(fig3)

# ─────────────────────────────────────────────────────
# TAB 2 — MUSIM & CUACA
# ─────────────────────────────────────────────────────
with tab2:
    st.subheader("📊 Pertanyaan 1: Bagaimana pengaruh kondisi cuaca dan musim terhadap jumlah penyewaan sepeda harian pada tahun 2011–2012?")

    if len(filtered_day) == 0:
        st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
    else:
        chart_type = st.radio("Tipe Visualisasi", ["Bar Chart", "Line Chart"],
                              horizontal=True, key="chart_tab2")

        fig1, axes = plt.subplots(1, 2, figsize=(14, 5))

        season_order = ['Spring', 'Summer', 'Fall', 'Winter']
        season_avg = (filtered_day.groupby('season')['cnt']
                      .mean().reindex(season_order).dropna())
        colors_s = ['#4CAF50','#FFC107','#F44336','#2196F3'][:len(season_avg)]

        if chart_type == "Bar Chart":
            axes[0].bar(season_avg.index, season_avg.values, color=colors_s)
            for i, v in enumerate(season_avg.values):
                axes[0].text(i, v + 50, str(round(v)), ha='center', fontsize=10)
        else:
            axes[0].plot(range(len(season_avg)), season_avg.values,
                         marker='o', color='#F44336', linewidth=2.5)
            axes[0].set_xticks(range(len(season_avg)))
            axes[0].set_xticklabels(season_avg.index)
        axes[0].set_title('Rata-rata Penyewaan per Musim (2011-2012)', fontsize=13)
        axes[0].set_xlabel('Musim')
        axes[0].set_ylabel('Rata-rata Penyewaan')
        axes[0].grid(alpha=0.3)

        weather_avg = (filtered_day.groupby('weathersit')['cnt']
                       .mean().sort_values(ascending=False))
        if chart_type == "Bar Chart":
            axes[1].bar(range(len(weather_avg)), weather_avg.values, color='#42A5F5')
            axes[1].set_xticks(range(len(weather_avg)))
            axes[1].set_xticklabels(weather_avg.index, rotation=15, ha='right')
            for i, v in enumerate(weather_avg.values):
                axes[1].text(i, v + 50, str(round(v)), ha='center', fontsize=10)
        else:
            axes[1].plot(range(len(weather_avg)), weather_avg.values,
                         marker='o', color='#1565C0', linewidth=2.5)
            axes[1].set_xticks(range(len(weather_avg)))
            axes[1].set_xticklabels(weather_avg.index, rotation=15, ha='right')
        axes[1].set_title('Rata-rata Penyewaan per Kondisi Cuaca (2011-2012)', fontsize=13)
        axes[1].set_xlabel('Kondisi Cuaca')
        axes[1].set_ylabel('Rata-rata Penyewaan')
        axes[1].grid(alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig1)
        plt.close(fig1)

        st.info("💡 Visualisasi musim dan cuaca mengkonfirmasi bahwa Fall + Clear weather adalah kombinasi terbaik untuk penyewaan sepeda. Cuaca Light Rain/Snow menyebabkan penurunan penyewaan hingga 63% dibanding cuaca Clear.")

        st.markdown("**Heatmap: Musim × Cuaca**")
        heatmap_data = (filtered_day
                        .groupby(['season','weathersit'])['cnt']
                        .mean().unstack(fill_value=0))
        if heatmap_data.shape[0] > 0 and heatmap_data.shape[1] > 0:
            fig3, ax3 = plt.subplots(figsize=(10, 4))
            im = ax3.imshow(heatmap_data.values, cmap='YlOrRd', aspect='auto')
            ax3.set_xticks(range(len(heatmap_data.columns)))
            ax3.set_xticklabels(heatmap_data.columns, fontsize=10)
            ax3.set_yticks(range(len(heatmap_data.index)))
            ax3.set_yticklabels(heatmap_data.index, fontsize=10)
            ax3.set_title("Heatmap Rata-rata Penyewaan: Musim × Cuaca", fontsize=13, fontweight='bold')
            plt.colorbar(im, ax=ax3)
            max_val = heatmap_data.values.max()
            for i in range(len(heatmap_data.index)):
                for j in range(len(heatmap_data.columns)):
                    val = heatmap_data.values[i, j]
                    ax3.text(j, i, f'{val:.0f}', ha='center', va='center', fontsize=9,
                             color='white' if val > max_val * 0.7 else 'black')
            plt.tight_layout()
            st.pyplot(fig3)
            plt.close(fig3)

# ─────────────────────────────────────────────────────
# TAB 3 — ANALISIS WAKTU
# ─────────────────────────────────────────────────────
with tab3:
    st.subheader("⏰ Pertanyaan 2: Pada jam berapa dan hari apa penyewaan sepeda mencapai puncaknya dalam seminggu?")

    if len(filtered_hour) == 0:
        st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
    else:
        fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))

        hour_avg = filtered_hour.groupby('hr')['cnt'].mean()
        axes2[0].plot(hour_avg.index, hour_avg.values,
                      marker='o', color='#E53935', linewidth=2)
        axes2[0].set_title('Rata-rata Penyewaan per Jam (2011-2012)', fontsize=13)
        axes2[0].set_xlabel('Jam')
        axes2[0].set_ylabel('Rata-rata Penyewaan')
        axes2[0].set_xticks(range(0, 24))
        axes2[0].axvline(x=8,  color='gray', linestyle='--', alpha=0.5, label='Jam 08.00')
        axes2[0].axvline(x=17, color='blue', linestyle='--', alpha=0.5, label='Jam 17.00')
        axes2[0].legend()
        axes2[0].grid(alpha=0.3)

        day_map     = {0:'Sun',1:'Mon',2:'Tue',3:'Wed',4:'Thu',5:'Fri',6:'Sat'}
        weekday_avg = filtered_hour.groupby('weekday')['cnt'].mean().rename(index=day_map)
        axes2[1].bar(weekday_avg.index, weekday_avg.values,
                     color=['#AB47BC' if d not in ['Sat','Sun'] else '#26A69A'
                            for d in weekday_avg.index])
        axes2[1].set_title('Rata-rata Penyewaan per Hari (2011-2012)', fontsize=13)
        axes2[1].set_xlabel('Hari')
        axes2[1].set_ylabel('Rata-rata Penyewaan')
        for i, v in enumerate(weekday_avg.values):
            axes2[1].text(i, v + 2, str(round(v)), ha='center', fontsize=9)
        axes2[1].grid(alpha=0.3, axis='y')

        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

        st.info("💡 Grafik per jam menunjukkan dua puncak jelas (bimodal) di jam 08.00 dan 17.00 yang konsisten dengan jam komuter kerja, sementara dini hari (01.00–04.00) adalah waktu terendah dengan rata-rata di bawah 25 penyewaan per jam.")

        st.markdown("---")
        st.markdown("**Pola Penyewaan per Jam: Hari Kerja vs Libur/Weekend**")
        workday_hour = (filtered_hour
                        .groupby(['workingday','hr'])['cnt']
                        .mean().unstack(level=0))
        workday_hour.columns = [
            'Libur/Weekend' if c == 0 else 'Hari Kerja'
            for c in workday_hour.columns
        ]
        fig3, ax3 = plt.subplots(figsize=(13, 4))
        if 'Hari Kerja' in workday_hour.columns:
            ax3.plot(workday_hour.index, workday_hour['Hari Kerja'],
                     marker='o', label='Hari Kerja', color='#1565C0', linewidth=2)
        if 'Libur/Weekend' in workday_hour.columns:
            ax3.plot(workday_hour.index, workday_hour['Libur/Weekend'],
                     marker='s', label='Libur/Weekend', color='#EF5350',
                     linewidth=2, linestyle='--')
        ax3.axvline(x=8,  color='gray', linestyle=':', alpha=0.5)
        ax3.axvline(x=17, color='gray', linestyle=':', alpha=0.5)
        ax3.set_title("Pola Penyewaan per Jam: Hari Kerja vs Libur", fontsize=13, fontweight='bold')
        ax3.set_xlabel("Jam")
        ax3.set_ylabel("Rata-rata Penyewaan")
        ax3.set_xticks(range(0, 24))
        ax3.legend()
        ax3.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

# ─────────────────────────────────────────────────────
# TAB 4 — ANALISIS LANJUTAN
# ─────────────────────────────────────────────────────
with tab4:
    st.subheader("📈 Analisis Lanjutan")

    if len(filtered_day) == 0:
        st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
    else:
        growth           = filtered_day.groupby('yr')['cnt'].sum()
        casual_total     = filtered_day['casual'].sum()
        registered_total = filtered_day['registered'].sum()

        pct = 0
        if 2011 in growth.index and 2012 in growth.index:
            pct = ((growth[2012] - growth[2011]) / growth[2011]) * 100

        col1, col2, col3 = st.columns(3)
        with col1:
            if 2011 in growth.index:
                st.metric('Total 2011', f"{growth[2011]:,}")
            if 2012 in growth.index:
                st.metric('Total 2012', f"{growth[2012]:,}")
            if pct != 0:
                st.metric('Pertumbuhan', f"{pct:.1f}%")
        with col2:
            st.metric('Casual',     f"{casual_total:,}")
            st.metric('Registered', f"{registered_total:,}")
        with col3:
            total_u = casual_total + registered_total
            if total_u > 0:
                st.metric('Proporsi Casual',     f"{casual_total/total_u*100:.1f}%")
                st.metric('Proporsi Registered', f"{registered_total/total_u*100:.1f}%")

        st.markdown("---")

        fig3, axes3 = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Tren bulanan 2011 vs 2012
        monthly_trend = filtered_day.groupby(['yr','mnth'])['cnt'].sum().reset_index()
        pivot_trend   = monthly_trend.pivot(index='mnth', columns='yr', values='cnt')
        if 2011 in pivot_trend.columns:
            axes3[0,0].plot(pivot_trend.index, pivot_trend[2011],
                            marker='o', label='2011', color='#42A5F5', linewidth=2)
        if 2012 in pivot_trend.columns:
            axes3[0,0].plot(pivot_trend.index, pivot_trend[2012],
                            marker='o', label='2012', color='#EF5350', linewidth=2)
        axes3[0,0].set_title('Tren Penyewaan Bulanan: 2011 vs 2012', fontsize=13)
        axes3[0,0].set_xlabel('Bulan')
        axes3[0,0].set_ylabel('Total Penyewaan')
        axes3[0,0].set_xticks(range(1,13))
        axes3[0,0].set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun',
                                    'Jul','Agu','Sep','Okt','Nov','Des'])
        axes3[0,0].legend()
        axes3[0,0].grid(alpha=0.3)

        # 2. Pie
        axes3[0,1].pie([casual_total, registered_total],
                       labels=['Casual','Registered'], autopct='%1.1f%%',
                       colors=['#FFC107','#4CAF50'], startangle=90, explode=(0.05,0))
        axes3[0,1].set_title('Proporsi Pengguna: Casual vs Registered', fontsize=13)

        # 3. Hari Kerja vs Libur
        workday_avg = filtered_day.groupby('workingday')['cnt'].mean()
        workday_avg.index = workday_avg.index.map({0:'Libur/Weekend', 1:'Hari Kerja'})
        axes3[1,0].bar(workday_avg.index, workday_avg.values,
                       color=['#AB47BC','#26A69A'], width=0.4)
        axes3[1,0].set_title('Rata-rata Penyewaan: Hari Kerja vs Libur', fontsize=13)
        axes3[1,0].set_xlabel('Tipe Hari')
        axes3[1,0].set_ylabel('Rata-rata Penyewaan')
        axes3[1,0].grid(alpha=0.3, axis='y')
        for i, v in enumerate(workday_avg.values):
            axes3[1,0].text(i, v + 30, str(round(v)), ha='center', fontsize=11)

        # 4. Suhu vs Penyewaan
        axes3[1,1].scatter(filtered_day['temp']*41, filtered_day['cnt'],
                           alpha=0.4, color='#FF7043', s=20)
        z      = np.polyfit(filtered_day['temp']*41, filtered_day['cnt'], 1)
        p_line = np.poly1d(z)
        x_line = np.linspace((filtered_day['temp']*41).min(),
                              (filtered_day['temp']*41).max(), 100)
        axes3[1,1].plot(x_line, p_line(x_line), color='#1565C0', linewidth=2, label='Trendline')
        axes3[1,1].set_title('Korelasi Suhu vs Jumlah Penyewaan', fontsize=13)
        axes3[1,1].set_xlabel('Suhu (°C)')
        axes3[1,1].set_ylabel('Jumlah Penyewaan')
        axes3[1,1].legend()
        axes3[1,1].grid(alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

        st.markdown("---")
        st.markdown("**Tren Bulanan Casual vs Registered**")
        monthly_seg = (filtered_day
                       .groupby(filtered_day['dteday'].dt.month)[['casual','registered']]
                       .sum())
        fig4, ax4 = plt.subplots(figsize=(13, 4))
        ax4.plot(monthly_seg.index, monthly_seg['casual'],
                 marker='o', label='Casual', color='#FFC107', linewidth=2)
        ax4.plot(monthly_seg.index, monthly_seg['registered'],
                 marker='s', label='Registered', color='#4CAF50', linewidth=2)
        ax4.set_title("Tren Bulanan Casual vs Registered", fontsize=13, fontweight='bold')
        ax4.set_xlabel("Bulan")
        ax4.set_ylabel("Total Penyewaan")
        ax4.set_xticks(range(1,13))
        ax4.set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun',
                             'Jul','Agu','Sep','Okt','Nov','Des'])
        ax4.legend()
        ax4.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close(fig4)

# ─────────────────────────────────────────────────────
# TAB 5 — KESIMPULAN
# ─────────────────────────────────────────────────────
with tab5:
    st.subheader("✅ Kesimpulan")

    col_kesimpulan1, col_kesimpulan2 = st.columns(2)
    with col_kesimpulan1:
        st.markdown("**Pertanyaan 1**")
        st.markdown("""
- **Musim Fall** dan **cuaca Clear** secara konsisten menghasilkan jumlah penyewaan tertinggi sepanjang 2011–2012.
- Kondisi cuaca buruk (**Light Rain/Snow**) terbukti menurunkan penyewaan secara drastis hingga **63%** dibanding cuaca Clear.

**Rekomendasi bisnis:**
- Tingkatkan ketersediaan armada sepeda di **musim Fall** dengan cuaca cerah.
- Kurangi operasional saat **cuaca buruk** untuk efisiensi biaya.
        """)

    with col_kesimpulan2:
        st.markdown("**Pertanyaan 2**")
        st.markdown("""
- Penyewaan memuncak pada pukul **08.00** dan **17.00–18.00** yang mencerminkan pola penggunaan sepeda sebagai moda transportasi **komuter**.
- **Hari Jumat** mencatat penyewaan tertinggi dalam seminggu.

**Rekomendasi bisnis:**
- Prioritaskan ketersediaan sepeda di **titik-titik strategis** (stasiun, perkantoran) pada jam dan hari tersebut.
- Siapkan armada tambahan untuk mengakomodasi lonjakan permintaan di jam sibuk.
        """)

    st.markdown("---")
    st.markdown("""
<div style="background:#FFF8E1;border-left:4px solid #F9A825;padding:16px;border-radius:8px;">
<b>📈 Analisis Lanjutan</b><br><br>
- Pertumbuhan penyewaan dari 2011 ke 2012 menunjukkan kenaikan signifikan, membuktikan tren positif adopsi bike sharing.<br>
- Pengguna <b>Registered</b> mendominasi (~80%) dibanding Casual (~20%), menunjukkan base pelanggan loyal yang kuat.<br>
- Terdapat korelasi positif antara <b>suhu</b> dan jumlah penyewaan — semakin hangat, semakin banyak yang bersepeda.
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Sumber: Bike Sharing Dataset — Capital Bikeshare, Washington D.C. | Arel Lafito Dinoris")
