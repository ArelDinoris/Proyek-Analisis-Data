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

hour_df['season'] = hour_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})
hour_df['weathersit'] = hour_df['weathersit'].map({
    1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'
})
hour_df['yr'] = hour_df['yr'].map({0: 2011, 1: 2012})

day_df['yr_label'] = day_df['yr'].map({0: 2011, 1: 2012})
day_df['season_label'] = day_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})
day_df['weather_label'] = day_df['weathersit'].map({
    1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'
})

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚴", layout="wide")

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1565C0, #42A5F5);
        padding: 20px 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p { margin: 5px 0 0 0; opacity: 0.85; font-size: 0.95rem; }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #42A5F5;
        text-align: center;
    }
    .insight-box {
        background: #E3F2FD;
        border-left: 4px solid #1565C0;
        padding: 12px 16px;
        border-radius: 6px;
        margin: 10px 0;
    }
    div[data-testid="stTabs"] button { font-size: 0.95rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR FILTERS
# =====================================================
st.sidebar.markdown("## 🔎 Dashboard Filters")
st.sidebar.markdown("---")

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
# APPLY FILTERS
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
st.markdown("""
<div class="main-header">
    <h1>🚴 Bike Sharing Dashboard</h1>
    <p>Nama: Arel Lafito Dinoris &nbsp;|&nbsp; Email: areldinoris23@gmail.com &nbsp;|&nbsp; ID: areldinoris</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# KPI METRICS
# =====================================================
col1, col2, col3, col4, col5 = st.columns(5)

total_rentals = filtered_day['cnt'].sum() if len(filtered_day) > 0 else 0
max_rentals = filtered_day['cnt'].max() if len(filtered_day) > 0 else 0
avg_day = filtered_day['cnt'].mean() if len(filtered_day) > 0 else 0
avg_hour = filtered_hour['cnt'].mean() if len(filtered_hour) > 0 else 0
growth_pct = 0
if len(filtered_day) > 0:
    g = filtered_day.groupby('yr_label')['cnt'].sum()
    if 2011 in g.index and 2012 in g.index:
        growth_pct = ((g[2012] - g[2011]) / g[2011]) * 100

col1.metric("🚲 Total Penyewaan", f"{total_rentals:,}")
col2.metric("📈 Tertinggi/Hari", f"{max_rentals:,}")
col3.metric("📊 Rata-rata/Hari", f"{avg_day:.0f}")
col4.metric("⏱ Rata-rata/Jam", f"{avg_hour:.0f}")
col5.metric("📉 Pertumbuhan YoY", f"{growth_pct:.1f}%" if growth_pct != 0 else "N/A")

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

# =====================================================
# TAB 1 — EXECUTIVE SUMMARY
# =====================================================
with tab1:
    st.subheader("📌 Executive Summary")

    metric_choice = st.selectbox(
        "Pilih Metric Trend Bulanan",
        ["Total Rentals", "Casual", "Registered"],
        key="metric_tab1"
    )
    metric_map = {"Total Rentals": "cnt", "Casual": "casual", "Registered": "registered"}

    if len(filtered_day) > 0:
        monthly = filtered_day.groupby(filtered_day['dteday'].dt.month)[metric_map[metric_choice]].sum()

        fig, ax = plt.subplots(figsize=(12, 4))
        ax.fill_between(monthly.index, monthly.values, alpha=0.3, color='#42A5F5')
        ax.plot(monthly.index, monthly.values, marker='o', color='#1565C0', linewidth=2.5)
        ax.set_title(f"Tren Bulanan — {metric_choice}", fontsize=14, fontweight='bold')
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
        st.warning("Tidak ada data untuk filter yang dipilih.")

    col_a, col_b = st.columns(2)

    with col_a:
        if len(filtered_day) > 0:
            st.markdown("**Tren per Tahun**")
            yearly = filtered_day.groupby('yr_label')['cnt'].sum()
            fig2, ax2 = plt.subplots(figsize=(5, 3.5))
            bars = ax2.bar(yearly.index.astype(str), yearly.values,
                           color=['#42A5F5', '#EF5350'], width=0.4)
            ax2.set_title("Total Penyewaan per Tahun", fontsize=12)
            ax2.set_ylabel("Total")
            for bar, val in zip(bars, yearly.values):
                ax2.text(bar.get_x() + bar.get_width()/2, val + 500,
                         f'{val:,}', ha='center', fontsize=10, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)

    with col_b:
        if len(filtered_day) > 0:
            st.markdown("**Distribusi Tipe Pengguna**")
            casual_t = filtered_day['casual'].sum()
            reg_t = filtered_day['registered'].sum()
            fig3, ax3 = plt.subplots(figsize=(5, 3.5))
            ax3.pie([casual_t, reg_t], labels=['Casual', 'Registered'],
                    autopct='%1.1f%%', colors=['#FFC107', '#4CAF50'],
                    startangle=90, explode=(0.05, 0))
            ax3.set_title("Proporsi Pengguna", fontsize=12)
            plt.tight_layout()
            st.pyplot(fig3)
            plt.close(fig3)

# =====================================================
# TAB 2 — MUSIM & CUACA
# =====================================================
with tab2:
    st.subheader("🌦 Pertanyaan 1: Pengaruh Musim & Cuaca terhadap Penyewaan")

    chart_type = st.radio("Tipe Visualisasi", ["Bar Chart", "Line Chart"], horizontal=True, key="radio_tab2")

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
                    ax.text(bar.get_x() + bar.get_width()/2, val + 0.5,
                            f'{val:.0f}', ha='center', fontsize=9)
            else:
                ax.plot(season_avg.index, season_avg.values, marker='o',
                        color='#F44336', linewidth=2.5)
            ax.set_title("Rata-rata Penyewaan per Musim", fontsize=12, fontweight='bold')
            ax.set_xlabel("Musim")
            ax.set_ylabel("Rata-rata Penyewaan/Jam")
            ax.grid(alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    with col_w:
        if len(filtered_hour) > 0:
            weather_avg = filtered_hour.groupby('weathersit')['cnt'].mean().sort_values(ascending=False)

            fig2, ax2 = plt.subplots(figsize=(6, 4))
            if chart_type == "Bar Chart":
                bars2 = ax2.bar(range(len(weather_avg)), weather_avg.values, color='#42A5F5')
                ax2.set_xticks(range(len(weather_avg)))
                ax2.set_xticklabels(weather_avg.index, rotation=15, ha='right', fontsize=9)
                for bar, val in zip(bars2, weather_avg.values):
                    ax2.text(bar.get_x() + bar.get_width()/2, val + 0.5,
                             f'{val:.0f}', ha='center', fontsize=9)
            else:
                ax2.plot(range(len(weather_avg)), weather_avg.values, marker='o',
                         color='#1565C0', linewidth=2.5)
                ax2.set_xticks(range(len(weather_avg)))
                ax2.set_xticklabels(weather_avg.index, rotation=15, ha='right', fontsize=9)
            ax2.set_title("Rata-rata Penyewaan per Cuaca", fontsize=12, fontweight='bold')
            ax2.set_ylabel("Rata-rata Penyewaan/Jam")
            ax2.grid(alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)

    if len(filtered_day) > 0:
        st.markdown("**Heatmap: Musim × Cuaca (dari data harian)**")
        heatmap_data = filtered_day.groupby(['season_label', 'weather_label'])['cnt'].mean().unstack(fill_value=0)
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        im = ax3.imshow(heatmap_data.values, cmap='YlOrRd', aspect='auto')
        ax3.set_xticks(range(len(heatmap_data.columns)))
        ax3.set_xticklabels(heatmap_data.columns, fontsize=10)
        ax3.set_yticks(range(len(heatmap_data.index)))
        ax3.set_yticklabels(heatmap_data.index, fontsize=10)
        ax3.set_title("Heatmap Rata-rata Penyewaan: Musim × Cuaca", fontsize=13, fontweight='bold')
        plt.colorbar(im, ax=ax3)
        for i in range(len(heatmap_data.index)):
            for j in range(len(heatmap_data.columns)):
                val = heatmap_data.values[i, j]
                ax3.text(j, i, f'{val:.0f}', ha='center', va='center', fontsize=9,
                         color='black' if val < heatmap_data.values.max()*0.7 else 'white')
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

    st.info("💡 Fall + Clear weather adalah kombinasi terbaik. Cuaca Light Rain/Snow menurunkan penyewaan hingga 63% dibanding cuaca Clear.")

# =====================================================
# TAB 3 — ANALISIS WAKTU
# =====================================================
with tab3:
    st.subheader("⏰ Pertanyaan 2: Pola Penyewaan Berdasarkan Waktu")

    col_h, col_d = st.columns(2)

    with col_h:
        if len(filtered_hour) > 0:
            hour_avg = filtered_hour.groupby('hr')['cnt'].mean()
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.fill_between(hour_avg.index, hour_avg.values, alpha=0.25, color='#E53935')
            ax.plot(hour_avg.index, hour_avg.values, marker='o', color='#E53935', linewidth=2)
            ax.axvline(x=8, color='gray', linestyle='--', alpha=0.6, label='Jam 08.00')
            ax.axvline(x=17, color='blue', linestyle='--', alpha=0.6, label='Jam 17.00')
            ax.set_title("Rata-rata Penyewaan per Jam", fontsize=12, fontweight='bold')
            ax.set_xlabel("Jam")
            ax.set_ylabel("Rata-rata Penyewaan")
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
            bars = ax2.bar(weekday_avg.index, weekday_avg.values,
                           color=['#AB47BC' if d not in ['Sat','Sun'] else '#26A69A' for d in weekday_avg.index])
            ax2.set_title("Rata-rata Penyewaan per Hari", fontsize=12, fontweight='bold')
            ax2.set_xlabel("Hari")
            ax2.set_ylabel("Rata-rata Penyewaan")
            for bar, val in zip(bars, weekday_avg.values):
                ax2.text(bar.get_x() + bar.get_width()/2, val + 1,
                         f'{val:.0f}', ha='center', fontsize=9)
            ax2.grid(alpha=0.3, axis='y')
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)

    if len(filtered_hour) > 0:
        st.markdown("**Pola Penyewaan per Jam berdasarkan Tipe Hari**")
        workday_hour = filtered_hour.groupby(['workingday', 'hr'])['cnt'].mean().unstack(level=0)
        workday_hour.columns = ['Libur/Weekend', 'Hari Kerja']
        fig3, ax3 = plt.subplots(figsize=(12, 4))
        ax3.plot(workday_hour.index, workday_hour['Hari Kerja'],
                 marker='o', label='Hari Kerja', color='#1565C0', linewidth=2)
        ax3.plot(workday_hour.index, workday_hour['Libur/Weekend'],
                 marker='s', label='Libur/Weekend', color='#EF5350', linewidth=2, linestyle='--')
        ax3.set_title("Pola Penyewaan per Jam: Hari Kerja vs Libur", fontsize=13, fontweight='bold')
        ax3.set_xlabel("Jam")
        ax3.set_ylabel("Rata-rata Penyewaan")
        ax3.set_xticks(range(0, 24))
        ax3.legend()
        ax3.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

    st.info("💡 Bimodal peak di jam 08.00 dan 17.00 konsisten dengan jam komuter. Hari Jumat mencatat penyewaan tertinggi dalam seminggu.")

# =====================================================
# TAB 4 — ANALISIS LANJUTAN
# =====================================================
with tab4:
    st.subheader("📈 Analisis Lanjutan")

    if len(filtered_day) > 0:
        g = filtered_day.groupby('yr_label')['cnt'].sum()
        pct = ((g[2012] - g[2011]) / g[2011]) * 100 if (2011 in g.index and 2012 in g.index) else 0
        casual_total = filtered_day['casual'].sum()
        registered_total = filtered_day['registered'].sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            if 2011 in g.index:
                st.metric('Total 2011', f"{g[2011]:,}")
            if 2012 in g.index:
                st.metric('Total 2012', f"{g[2012]:,}")
            if pct != 0:
                st.metric('Pertumbuhan YoY', f"{pct:.1f}%")
        with col2:
            st.metric('Total Casual', f"{casual_total:,}")
            st.metric('Total Registered', f"{registered_total:,}")
        with col3:
            total_u = casual_total + registered_total
            st.metric('Proporsi Casual', f"{casual_total/total_u*100:.1f}%" if total_u > 0 else "N/A")
            st.metric('Proporsi Registered', f"{registered_total/total_u*100:.1f}%" if total_u > 0 else "N/A")

        st.markdown("---")

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Tren bulanan 2011 vs 2012
        monthly_trend = filtered_day.groupby(['yr_label', 'mnth'])['cnt'].sum().reset_index()
        pivot_trend = monthly_trend.pivot(index='mnth', columns='yr_label', values='cnt')
        if 2011 in pivot_trend.columns:
            axes[0, 0].plot(pivot_trend.index, pivot_trend[2011],
                           marker='o', label='2011', color='#42A5F5', linewidth=2)
        if 2012 in pivot_trend.columns:
            axes[0, 0].plot(pivot_trend.index, pivot_trend[2012],
                           marker='o', label='2012', color='#EF5350', linewidth=2)
        axes[0, 0].set_title('Tren Penyewaan Bulanan: 2011 vs 2012', fontsize=13, fontweight='bold')
        axes[0, 0].set_xlabel('Bulan')
        axes[0, 0].set_ylabel('Total Penyewaan')
        axes[0, 0].set_xticks(range(1, 13))
        axes[0, 0].set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun',
                                    'Jul','Agu','Sep','Okt','Nov','Des'])
        axes[0, 0].legend()
        axes[0, 0].grid(alpha=0.3)

        # 2. Pie casual vs registered
        axes[0, 1].pie(
            [casual_total, registered_total],
            labels=['Casual', 'Registered'],
            autopct='%1.1f%%',
            colors=['#FFC107', '#4CAF50'],
            startangle=90,
            explode=(0.05, 0)
        )
        axes[0, 1].set_title('Proporsi Pengguna: Casual vs Registered', fontsize=13, fontweight='bold')

        # 3. Hari kerja vs libur
        workday_avg = filtered_day.groupby('workingday')['cnt'].mean()
        workday_avg.index = workday_avg.index.map({0: 'Libur/Weekend', 1: 'Hari Kerja'})
        bars = axes[1, 0].bar(workday_avg.index, workday_avg.values,
                              color=['#AB47BC', '#26A69A'], width=0.4)
        axes[1, 0].set_title('Rata-rata Penyewaan: Hari Kerja vs Libur', fontsize=13, fontweight='bold')
        axes[1, 0].set_xlabel('Tipe Hari')
        axes[1, 0].set_ylabel('Rata-rata Penyewaan')
        axes[1, 0].grid(alpha=0.3, axis='y')
        for bar, val in zip(bars, workday_avg.values):
            axes[1, 0].text(bar.get_x() + bar.get_width()/2, val + 30,
                            str(round(val)), ha='center', fontsize=11, fontweight='bold')

        # 4. Suhu vs penyewaan
        axes[1, 1].scatter(filtered_day['temp'] * 41, filtered_day['cnt'],
                           alpha=0.4, color='#FF7043', s=20)
        z = np.polyfit(filtered_day['temp'] * 41, filtered_day['cnt'], 1)
        p = np.poly1d(z)
        x_line = np.linspace((filtered_day['temp'] * 41).min(), (filtered_day['temp'] * 41).max(), 100)
        axes[1, 1].plot(x_line, p(x_line), color='#1565C0', linewidth=2, label='Trendline')
        axes[1, 1].set_title('Korelasi Suhu vs Jumlah Penyewaan', fontsize=13, fontweight='bold')
        axes[1, 1].set_xlabel('Suhu (°C)')
        axes[1, 1].set_ylabel('Jumlah Penyewaan')
        axes[1, 1].legend()
        axes[1, 1].grid(alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        # Bonus: Casual vs Registered per bulan
        st.markdown("**Tren Casual vs Registered per Bulan**")
        monthly_seg = filtered_day.groupby(filtered_day['dteday'].dt.month)[['casual','registered']].sum()
        fig2, ax2 = plt.subplots(figsize=(12, 4))
        ax2.plot(monthly_seg.index, monthly_seg['casual'], marker='o',
                 label='Casual', color='#FFC107', linewidth=2)
        ax2.plot(monthly_seg.index, monthly_seg['registered'], marker='s',
                 label='Registered', color='#4CAF50', linewidth=2)
        ax2.set_title("Tren Bulanan Casual vs Registered", fontsize=13, fontweight='bold')
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
        st.warning("Tidak ada data untuk filter yang dipilih.")

# =====================================================
# TAB 5 — KESIMPULAN
# =====================================================
with tab5:
    st.subheader("✅ Kesimpulan & Rekomendasi")

    col_k1, col_k2 = st.columns(2)

    with col_k1:
        st.markdown("""
        <div style="background:#E3F2FD; border-left:4px solid #1565C0; padding:16px; border-radius:8px;">
        <b>📊 Pertanyaan 1: Musim & Cuaca</b><br><br>
        • <b>Musim Fall</b> dan <b>cuaca Clear</b> secara konsisten menghasilkan jumlah penyewaan tertinggi sepanjang 2011–2012.<br><br>
        • Kondisi cuaca buruk (<b>Light Rain/Snow</b>) terbukti menurunkan penyewaan secara drastis hingga <b>63%</b> dibanding cuaca Clear.<br><br>
        <b>🎯 Rekomendasi:</b><br>
        • Tingkatkan ketersediaan armada sepeda di <b>musim Fall</b> dengan cuaca cerah.<br>
        • Kurangi operasional saat <b>cuaca buruk</b> untuk efisiensi biaya.
        </div>
        """, unsafe_allow_html=True)

    with col_k2:
        st.markdown("""
        <div style="background:#E8F5E9; border-left:4px solid #2E7D32; padding:16px; border-radius:8px;">
        <b>⏰ Pertanyaan 2: Waktu & Hari</b><br><br>
        • Penyewaan memuncak pada pukul <b>08.00</b> dan <b>17.00–18.00</b> yang mencerminkan pola penggunaan sebagai moda <b>komuter</b>.<br><br>
        • <b>Hari Jumat</b> mencatat penyewaan tertinggi dalam seminggu.<br><br>
        <b>🎯 Rekomendasi:</b><br>
        • Prioritaskan ketersediaan sepeda di <b>titik strategis</b> (stasiun, perkantoran) pada jam sibuk.<br>
        • Siapkan armada tambahan untuk mengakomodasi lonjakan permintaan.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="background:#FFF8E1; border-left:4px solid #F9A825; padding:16px; border-radius:8px; margin-top:10px;">
    <b>📈 Analisis Lanjutan</b><br><br>
    • Pertumbuhan penyewaan dari 2011 ke 2012 menunjukkan kenaikan signifikan, membuktikan tren positif adopsi bike sharing.<br>
    • Pengguna <b>Registered</b> mendominasi (~80%) dibanding Casual (~20%), menunjukkan base pelanggan loyal yang kuat.<br>
    • Terdapat korelasi positif antara <b>suhu</b> dan jumlah penyewaan — semakin hangat, semakin banyak yang bersepeda.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Sumber: Bike Sharing Dataset — Capital Bikeshare, Washington D.C. | Arel Lafito Dinoris")
