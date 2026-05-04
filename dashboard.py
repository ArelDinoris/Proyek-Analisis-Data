import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import streamlit as st
import os

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="🚴 Bike Sharing Dashboard",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
}
.main {
    background: #0d1117;
    color: #e6edf3;
}
[data-testid="stSidebar"] {
    background: #161b22;
    border-right: 1px solid #30363d;
}
[data-testid="stSidebar"] * {
    color: #e6edf3 !important;
}
.metric-card {
    background: linear-gradient(135deg, #1c2128, #21262d);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 18px 22px;
    text-align: center;
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-3px); }
.metric-label {
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #7d8590;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 26px;
    font-weight: 800;
    color: #58a6ff;
}
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #e6edf3;
    border-left: 4px solid #58a6ff;
    padding-left: 12px;
    margin: 20px 0 14px 0;
}
.insight-box {
    background: linear-gradient(135deg, #1c2128, #161b22);
    border: 1px solid #388bfd33;
    border-left: 4px solid #58a6ff;
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 13.5px;
    color: #adbac7;
    margin-top: 10px;
}
.stTabs [data-baseweb="tab-list"] {
    background: #161b22;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #7d8590;
    border-radius: 8px;
    font-weight: 600;
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    padding: 8px 18px;
}
.stTabs [aria-selected="true"] {
    background: #21262d !important;
    color: #58a6ff !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif;
    font-size: 22px !important;
    color: #58a6ff !important;
}
[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    color: #7d8590 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# ── MATPLOTLIB DARK THEME ──
plt.rcParams.update({
    'figure.facecolor': '#0d1117',
    'axes.facecolor': '#161b22',
    'axes.edgecolor': '#30363d',
    'axes.labelcolor': '#adbac7',
    'xtick.color': '#7d8590',
    'ytick.color': '#7d8590',
    'text.color': '#e6edf3',
    'grid.color': '#21262d',
    'grid.linewidth': 0.8,
    'legend.facecolor': '#1c2128',
    'legend.edgecolor': '#30363d',
    'legend.labelcolor': '#e6edf3',
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

# ── LOAD DATA ──
@st.cache_data
def load_data():
    base = os.path.dirname(__file__)
    day = pd.read_csv(os.path.join(base, 'main_data.csv'))
    day['dteday'] = pd.to_datetime(day['dteday'])
    hour = pd.read_csv(os.path.join(base, 'hour.csv'))
    hour['dteday'] = pd.to_datetime(hour['dteday'])
    hour['season'] = hour['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})
    hour['weathersit'] = hour['weathersit'].map({
        1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'
    })
    hour['yr'] = hour['yr'].map({0: 2011, 1: 2012})
    return day, hour

day_df, hour_df = load_data()

# ── SIDEBAR FILTERS ──
with st.sidebar:
    st.markdown("## 🎛️ Filter & Slicer")
    st.markdown("---")

    # Tahun
    tahun_options = sorted(day_df['yr'].unique().tolist())
    tahun_map = {0: 2011, 1: 2012}
    tahun_display = [tahun_map.get(y, y) for y in tahun_options]
    selected_tahun_display = st.multiselect(
        "📅 Tahun", tahun_display, default=tahun_display
    )
    selected_tahun = [k for k, v in tahun_map.items() if v in selected_tahun_display]

    # Musim (dari day_df)
    season_map_day = {1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'}
    season_options = ['Spring', 'Summer', 'Fall', 'Winter']
    selected_season = st.multiselect(
        "🌿 Musim", season_options, default=season_options
    )

    # Cuaca (dari day_df)
    weather_options_day = sorted(day_df['weathersit'].dropna().unique().tolist())
    selected_weather = st.multiselect(
        "🌤️ Kondisi Cuaca", weather_options_day, default=weather_options_day
    )

    # Rentang Tanggal
    min_date = day_df['dteday'].min().date()
    max_date = day_df['dteday'].max().date()
    date_range = st.date_input(
        "📆 Rentang Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Hari Kerja
    workday_filter = st.radio(
        "💼 Tipe Hari",
        ["Semua", "Hari Kerja", "Libur/Weekend"],
        index=0
    )

    st.markdown("---")
    st.markdown("**💡 Tips:** Gunakan filter di atas untuk eksplorasi data secara interaktif.")

# ── APPLY FILTERS ──
# Map season string ke angka untuk day_df
season_reverse = {'Spring':1, 'Summer':2, 'Fall':3, 'Winter':4}
selected_season_num = [season_reverse[s] for s in selected_season]

filtered_day = day_df[
    (day_df['yr'].isin(selected_tahun)) &
    (day_df['season'].isin(selected_season_num)) &
    (day_df['weathersit'].isin(selected_weather))
]

if len(date_range) == 2:
    filtered_day = filtered_day[
        (filtered_day['dteday'].dt.date >= date_range[0]) &
        (filtered_day['dteday'].dt.date <= date_range[1])
    ]

if workday_filter == "Hari Kerja":
    filtered_day = filtered_day[filtered_day['workingday'] == 1]
elif workday_filter == "Libur/Weekend":
    filtered_day = filtered_day[filtered_day['workingday'] == 0]

# Filter hour_df by yr and date only
filtered_hour = hour_df[hour_df['yr'].isin(selected_tahun_display)]
if len(date_range) == 2:
    filtered_hour = filtered_hour[
        (filtered_hour['dteday'].dt.date >= date_range[0]) &
        (filtered_hour['dteday'].dt.date <= date_range[1])
    ]

# ── HEADER ──
st.markdown("""
<h1 style="font-family:'Syne',sans-serif; font-size:2.4rem; font-weight:800; color:#e6edf3; margin-bottom:4px;">
🚴 Bike Sharing Dashboard
</h1>
<p style="color:#7d8590; font-size:13px; margin-bottom:0;">
<strong style="color:#adbac7;">Nama:</strong> Arel Lafito Dinoris &nbsp;|&nbsp;
<strong style="color:#adbac7;">Email:</strong> areldinoris23@gmail.com &nbsp;|&nbsp;
<strong style="color:#adbac7;">ID:</strong> areldinoris
</p>
""", unsafe_allow_html=True)
st.markdown("<hr style='border:1px solid #30363d; margin:16px 0;'>", unsafe_allow_html=True)

# ── METRICS ──
if filtered_day.empty:
    st.warning("⚠️ Tidak ada data untuk filter yang dipilih. Silakan ubah filter.")
    st.stop()

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Total Penyewaan</div>
        <div class="metric-value">{filtered_day['cnt'].sum():,}</div>
    </div>""", unsafe_allow_html=True)
with col_m2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Penyewaan Tertinggi</div>
        <div class="metric-value">{filtered_day['cnt'].max():,}</div>
    </div>""", unsafe_allow_html=True)
with col_m3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Rata-rata/Hari</div>
        <div class="metric-value">{filtered_day['cnt'].mean():.0f}</div>
    </div>""", unsafe_allow_html=True)
with col_m4:
    avg_hour = filtered_hour['cnt'].mean() if not filtered_hour.empty else 0
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Rata-rata/Jam</div>
        <div class="metric-value">{avg_hour:.0f}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Musim & Cuaca",
    "⏰ Jam & Hari",
    "📈 Tren & Segmentasi",
    "🌡️ Eksplorasi Data",
    "✅ Kesimpulan"
])

# ══════════════════════════════════════
# TAB 1: Musim & Cuaca
# ══════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Pertanyaan 1: Pengaruh Musim & Cuaca terhadap Penyewaan Harian</div>', unsafe_allow_html=True)

    col_t1a, col_t1b = st.columns(2)

    with col_t1a:
        season_map_rev = {1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'}
        fd = filtered_day.copy()
        fd['season_name'] = fd['season'].map(season_map_rev)
        season_order = ['Spring', 'Summer', 'Fall', 'Winter']
        season_avg = fd.groupby('season_name')['cnt'].mean().reindex(season_order).dropna()

        fig, ax = plt.subplots(figsize=(7, 4.5))
        colors_s = ['#3fb950', '#e3b341', '#f85149', '#388bfd']
        bars = ax.bar(season_avg.index, season_avg.values, color=colors_s[:len(season_avg)], width=0.55, zorder=3)
        ax.set_title('Rata-rata Penyewaan per Musim', fontsize=12, fontweight='bold', pad=12)
        ax.set_xlabel('Musim', fontsize=10)
        ax.set_ylabel('Rata-rata Penyewaan', fontsize=10)
        ax.grid(axis='y', alpha=0.4, zorder=0)
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h + 40, f'{h:,.0f}',
                    ha='center', va='bottom', fontsize=9, color='#e6edf3', fontweight='600')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col_t1b:
        weather_avg = filtered_day.groupby('weathersit')['cnt'].mean().sort_values(ascending=False)
        fig2, ax2 = plt.subplots(figsize=(7, 4.5))
        bars2 = ax2.bar(weather_avg.index, weather_avg.values, color='#58a6ff', width=0.5, zorder=3)
        ax2.set_title('Rata-rata Penyewaan per Kondisi Cuaca', fontsize=12, fontweight='bold', pad=12)
        ax2.set_xlabel('Kondisi Cuaca', fontsize=10)
        ax2.set_ylabel('Rata-rata Penyewaan', fontsize=10)
        ax2.tick_params(axis='x', rotation=15)
        ax2.grid(axis='y', alpha=0.4, zorder=0)
        for bar in bars2:
            h = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, h + 40, f'{h:,.0f}',
                     ha='center', va='bottom', fontsize=9, color='#e6edf3', fontweight='600')
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    # Tabel ringkasan musim
    st.markdown('<div class="section-header" style="font-size:14px;">📋 Tabel Ringkasan per Musim</div>', unsafe_allow_html=True)
    if not fd.empty:
        season_tbl = fd.groupby('season_name')['cnt'].agg(['mean','sum','min','max']).round(0).astype(int)
        season_tbl.columns = ['Rata-rata', 'Total', 'Min', 'Max']
        season_tbl = season_tbl.reindex([s for s in season_order if s in season_tbl.index])
        st.dataframe(season_tbl, use_container_width=True)

    st.markdown('<div class="insight-box">💡 <strong>Insight:</strong> Fall + Clear weather adalah kombinasi terbaik untuk penyewaan sepeda. Cuaca Light Rain/Snow menyebabkan penurunan penyewaan hingga 63% dibanding cuaca Clear.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════
# TAB 2: Jam & Hari
# ══════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">Pertanyaan 2: Puncak Penyewaan per Jam dan Hari</div>', unsafe_allow_html=True)

    col_t2a, col_t2b = st.columns(2)

    with col_t2a:
        if not filtered_hour.empty:
            hour_avg = filtered_hour.groupby('hr')['cnt'].mean()
            fig3, ax3 = plt.subplots(figsize=(7, 4.5))
            ax3.plot(hour_avg.index, hour_avg.values, marker='o', color='#f85149',
                     linewidth=2, markersize=5, zorder=3)
            ax3.fill_between(hour_avg.index, hour_avg.values, alpha=0.15, color='#f85149')
            ax3.axvline(x=8, color='#e3b341', linestyle='--', alpha=0.8, label='Jam 08.00')
            ax3.axvline(x=17, color='#388bfd', linestyle='--', alpha=0.8, label='Jam 17.00')
            ax3.set_title('Rata-rata Penyewaan per Jam', fontsize=12, fontweight='bold', pad=12)
            ax3.set_xlabel('Jam', fontsize=10)
            ax3.set_ylabel('Rata-rata Penyewaan', fontsize=10)
            ax3.set_xticks(range(0, 24))
            ax3.grid(axis='y', alpha=0.3, zorder=0)
            ax3.legend()
            plt.tight_layout()
            st.pyplot(fig3)
            plt.close(fig3)
        else:
            st.info("Tidak ada data jam untuk filter ini.")

    with col_t2b:
        if not filtered_hour.empty:
            day_map = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
            weekday_avg = filtered_hour.groupby('weekday')['cnt'].mean().rename(index=day_map)
            fig4, ax4 = plt.subplots(figsize=(7, 4.5))
            colors_w = ['#ab7df8' if i != weekday_avg.values.argmax() else '#f85149'
                        for i in range(len(weekday_avg))]
            bars4 = ax4.bar(weekday_avg.index, weekday_avg.values, color=colors_w, width=0.55, zorder=3)
            ax4.set_title('Rata-rata Penyewaan per Hari', fontsize=12, fontweight='bold', pad=12)
            ax4.set_xlabel('Hari', fontsize=10)
            ax4.set_ylabel('Rata-rata Penyewaan', fontsize=10)
            ax4.grid(axis='y', alpha=0.4, zorder=0)
            for bar in bars4:
                h = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2, h + 1, f'{h:.0f}',
                         ha='center', va='bottom', fontsize=9, color='#e6edf3', fontweight='600')
            plt.tight_layout()
            st.pyplot(fig4)
            plt.close(fig4)

    # Heatmap jam x hari
    st.markdown('<div class="section-header" style="font-size:14px;">🔥 Heatmap Penyewaan: Jam × Hari</div>', unsafe_allow_html=True)
    if not filtered_hour.empty:
        pivot_hw = filtered_hour.pivot_table(index='hr', columns='weekday', values='cnt', aggfunc='mean')
        pivot_hw.columns = [day_map.get(c, c) for c in pivot_hw.columns]
        fig5, ax5 = plt.subplots(figsize=(12, 5))
        im = ax5.imshow(pivot_hw.values, aspect='auto', cmap='YlOrRd', interpolation='nearest')
        ax5.set_xticks(range(len(pivot_hw.columns)))
        ax5.set_xticklabels(pivot_hw.columns)
        ax5.set_yticks(range(0, 24, 2))
        ax5.set_yticklabels([f'{h:02d}:00' for h in range(0, 24, 2)])
        ax5.set_title('Heatmap Rata-rata Penyewaan per Jam × Hari', fontsize=12, fontweight='bold')
        plt.colorbar(im, ax=ax5, label='Rata-rata Penyewaan')
        plt.tight_layout()
        st.pyplot(fig5)
        plt.close(fig5)

    st.markdown('<div class="insight-box">💡 <strong>Insight:</strong> Dua puncak bimodal di jam 08.00 dan 17.00 konsisten dengan pola komuter. Dini hari (01.00–04.00) mencatat rata-rata di bawah 25 penyewaan/jam.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════
# TAB 3: Tren & Segmentasi
# ══════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Analisis Tren Bulanan & Segmentasi Pengguna</div>', unsafe_allow_html=True)

    # Metrics
    tahun_map_rev = {0: 2011, 1: 2012}
    fd_yr = filtered_day.copy()
    fd_yr['yr_label'] = fd_yr['yr'].map(tahun_map_rev)
    growth = fd_yr.groupby('yr_label')['cnt'].sum()
    casual_total = filtered_day['casual'].sum()
    registered_total = filtered_day['registered'].sum()

    cg1, cg2, cg3, cg4 = st.columns(4)
    with cg1:
        if 2011 in growth.index:
            st.metric('Total 2011', f"{growth[2011]:,}")
    with cg2:
        if 2012 in growth.index:
            st.metric('Total 2012', f"{growth[2012]:,}")
    with cg3:
        if 2011 in growth.index and 2012 in growth.index:
            pct = ((growth[2012] - growth[2011]) / growth[2011]) * 100
            st.metric('Pertumbuhan YoY', f"{pct:.1f}%")
    with cg4:
        total = casual_total + registered_total
        if total > 0:
            st.metric('Proporsi Registered', f"{registered_total/total*100:.1f}%")

    col_t3a, col_t3b = st.columns(2)

    with col_t3a:
        # Tren bulanan
        fd_yr['yr_label'] = fd_yr['yr'].map(tahun_map_rev)
        monthly = fd_yr.groupby(['yr_label', 'mnth'])['cnt'].sum().reset_index()
        fig6, ax6 = plt.subplots(figsize=(7, 4.5))
        for yr_val, color, label in [(2011, '#388bfd', '2011'), (2012, '#f85149', '2012')]:
            subset = monthly[monthly['yr_label'] == yr_val]
            if not subset.empty:
                ax6.plot(subset['mnth'], subset['cnt'], marker='o', label=label,
                         color=color, linewidth=2, markersize=5)
                ax6.fill_between(subset['mnth'], subset['cnt'], alpha=0.1, color=color)
        ax6.set_title('Tren Penyewaan Bulanan: 2011 vs 2012', fontsize=12, fontweight='bold', pad=12)
        ax6.set_xticks(range(1, 13))
        ax6.set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'], rotation=30)
        ax6.set_xlabel('Bulan', fontsize=10)
        ax6.set_ylabel('Total Penyewaan', fontsize=10)
        ax6.legend()
        ax6.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig6)
        plt.close(fig6)

    with col_t3b:
        # Pie casual vs registered
        fig7, ax7 = plt.subplots(figsize=(7, 4.5))
        if casual_total + registered_total > 0:
            wedges, texts, autotexts = ax7.pie(
                [casual_total, registered_total],
                labels=['Casual', 'Registered'],
                autopct='%1.1f%%',
                colors=['#e3b341', '#3fb950'],
                startangle=90,
                explode=(0.05, 0),
                textprops={'color': '#e6edf3', 'fontsize': 11}
            )
            for at in autotexts:
                at.set_color('#0d1117')
                at.set_fontweight('bold')
        ax7.set_title('Proporsi Pengguna: Casual vs Registered', fontsize=12, fontweight='bold', pad=12)
        plt.tight_layout()
        st.pyplot(fig7)
        plt.close(fig7)

    col_t3c, col_t3d = st.columns(2)

    with col_t3c:
        # Hari kerja vs libur
        workday_avg = filtered_day.groupby('workingday')['cnt'].mean()
        workday_avg.index = workday_avg.index.map({0: 'Libur/Weekend', 1: 'Hari Kerja'})
        fig8, ax8 = plt.subplots(figsize=(7, 4))
        bars8 = ax8.bar(workday_avg.index, workday_avg.values,
                        color=['#ab7df8', '#26a69a'], width=0.4, zorder=3)
        ax8.set_title('Rata-rata Penyewaan: Hari Kerja vs Libur', fontsize=12, fontweight='bold', pad=12)
        ax8.set_xlabel('Tipe Hari', fontsize=10)
        ax8.set_ylabel('Rata-rata Penyewaan', fontsize=10)
        ax8.grid(axis='y', alpha=0.4, zorder=0)
        for bar in bars8:
            h = bar.get_height()
            ax8.text(bar.get_x() + bar.get_width()/2, h + 30, f'{h:,.0f}',
                     ha='center', va='bottom', fontsize=10, color='#e6edf3', fontweight='600')
        plt.tight_layout()
        st.pyplot(fig8)
        plt.close(fig8)

    with col_t3d:
        # Scatter suhu
        fig9, ax9 = plt.subplots(figsize=(7, 4))
        temp_c = filtered_day['temp'] * 41
        ax9.scatter(temp_c, filtered_day['cnt'], alpha=0.4, color='#ff7043', s=18, zorder=3)
        z = np.polyfit(temp_c, filtered_day['cnt'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(temp_c.min(), temp_c.max(), 100)
        ax9.plot(x_line, p(x_line), color='#388bfd', linewidth=2.5, label='Trendline', zorder=4)
        ax9.set_title('Korelasi Suhu vs Jumlah Penyewaan', fontsize=12, fontweight='bold', pad=12)
        ax9.set_xlabel('Suhu (°C)', fontsize=10)
        ax9.set_ylabel('Jumlah Penyewaan', fontsize=10)
        ax9.legend()
        ax9.grid(alpha=0.3, zorder=0)
        plt.tight_layout()
        st.pyplot(fig9)
        plt.close(fig9)

# ══════════════════════════════════════
# TAB 4: Eksplorasi Data
# ══════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">🔍 Eksplorasi & Analisis Kustom</div>', unsafe_allow_html=True)

    col_e1, col_e2 = st.columns([1, 2])

    with col_e1:
        x_axis = st.selectbox("Pilih sumbu X", ['temp', 'atemp', 'hum', 'windspeed', 'hr_of_day'])
        y_axis = st.selectbox("Pilih sumbu Y", ['cnt', 'casual', 'registered'])
        chart_type = st.radio("Tipe Chart", ["Line", "Bar", "Scatter"])
        group_by = st.selectbox("Group By", ['Tidak Ada', 'season', 'weathersit', 'workingday', 'yr'])

    with col_e2:
        # Gabung hour info ke day jika perlu
        if x_axis == 'hr_of_day':
            if not filtered_hour.empty:
                plot_df = filtered_hour.rename(columns={'hr': 'hr_of_day'})
                x_col = 'hr_of_day'
            else:
                st.info("Tidak ada data jam untuk filter ini.")
                plot_df = pd.DataFrame()
                x_col = None
        else:
            plot_df = filtered_day.copy()
            x_col = x_axis

        if not plot_df.empty and x_col and y_axis in plot_df.columns and x_col in plot_df.columns:
            fig_e, ax_e = plt.subplots(figsize=(8, 4.5))

            if group_by != 'Tidak Ada' and group_by in plot_df.columns:
                groups = plot_df[group_by].unique()
                palette = ['#388bfd', '#f85149', '#3fb950', '#e3b341', '#ab7df8', '#ff7043']
                for idx, grp in enumerate(sorted(groups)):
                    sub = plot_df[plot_df[group_by] == grp]
                    agg = sub.groupby(x_col)[y_axis].mean()
                    c = palette[idx % len(palette)]
                    label = str(grp)
                    if chart_type == "Line":
                        ax_e.plot(agg.index, agg.values, marker='o', label=label, color=c, linewidth=2, markersize=4)
                    elif chart_type == "Bar":
                        x_pos = np.arange(len(agg))
                        ax_e.bar(x_pos + idx * 0.15, agg.values, width=0.15, label=label, color=c)
                        ax_e.set_xticks(x_pos + 0.3)
                        ax_e.set_xticklabels(agg.index, rotation=30)
                    else:
                        ax_e.scatter(sub[x_col], sub[y_axis], label=label, color=c, alpha=0.5, s=18)
                ax_e.legend()
            else:
                agg = plot_df.groupby(x_col)[y_axis].mean()
                if chart_type == "Line":
                    ax_e.plot(agg.index, agg.values, marker='o', color='#58a6ff', linewidth=2, markersize=4)
                    ax_e.fill_between(agg.index, agg.values, alpha=0.12, color='#58a6ff')
                elif chart_type == "Bar":
                    ax_e.bar(agg.index, agg.values, color='#58a6ff', width=0.6, zorder=3)
                else:
                    ax_e.scatter(plot_df[x_col], plot_df[y_axis], color='#ff7043', alpha=0.4, s=18)

            ax_e.set_xlabel(x_col.replace('_', ' ').title(), fontsize=10)
            ax_e.set_ylabel(y_axis.title(), fontsize=10)
            ax_e.set_title(f'{y_axis.title()} vs {x_col.replace("_"," ").title()}', fontsize=12, fontweight='bold')
            ax_e.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig_e)
            plt.close(fig_e)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="font-size:14px;">📋 Preview Data Terfilter</div>', unsafe_allow_html=True)
    show_rows = st.slider("Jumlah baris", 5, 50, 10)
    st.dataframe(filtered_day.head(show_rows), use_container_width=True)

    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.markdown("**Statistik Deskriptif (cnt)**")
        st.dataframe(filtered_day[['cnt', 'casual', 'registered', 'temp', 'hum', 'windspeed']].describe().round(2), use_container_width=True)
    with col_stat2:
        st.markdown("**Korelasi terhadap cnt**")
        num_cols = ['temp', 'atemp', 'hum', 'windspeed', 'casual', 'registered', 'cnt']
        corr = filtered_day[num_cols].corr()[['cnt']].drop('cnt').sort_values('cnt', ascending=False)
        st.dataframe(corr.round(3), use_container_width=True)

# ══════════════════════════════════════
# TAB 5: Kesimpulan
# ══════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">✅ Kesimpulan & Rekomendasi Bisnis</div>', unsafe_allow_html=True)

    col_k1, col_k2 = st.columns(2)

    with col_k1:
        st.markdown("""
        <div style="background:#1c2128; border:1px solid #30363d; border-top:3px solid #3fb950;
             border-radius:10px; padding:20px; height:100%;">
        <h4 style="color:#3fb950; font-family:'Syne',sans-serif; margin-top:0;">
        📊 Pertanyaan 1: Musim & Cuaca
        </h4>
        <ul style="color:#adbac7; line-height:1.9; font-size:13.5px;">
            <li><strong style="color:#e6edf3;">Musim Fall</strong> dan <strong style="color:#e6edf3;">cuaca Clear</strong> secara konsisten menghasilkan jumlah penyewaan tertinggi sepanjang 2011–2012.</li>
            <li>Kondisi cuaca buruk (<strong style="color:#f85149;">Light Rain/Snow</strong>) terbukti menurunkan penyewaan secara drastis hingga <strong style="color:#f85149;">63%</strong> dibanding cuaca Clear.</li>
        </ul>
        <p style="color:#58a6ff; font-weight:600; font-size:13px; margin-bottom:6px;">🎯 Rekomendasi Bisnis:</p>
        <ul style="color:#adbac7; line-height:1.9; font-size:13.5px;">
            <li>Tingkatkan ketersediaan armada sepeda di <strong style="color:#e6edf3;">musim Fall</strong> dengan cuaca cerah.</li>
            <li>Kurangi operasional saat <strong style="color:#e6edf3;">cuaca buruk</strong> untuk efisiensi biaya.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_k2:
        st.markdown("""
        <div style="background:#1c2128; border:1px solid #30363d; border-top:3px solid #388bfd;
             border-radius:10px; padding:20px; height:100%;">
        <h4 style="color:#388bfd; font-family:'Syne',sans-serif; margin-top:0;">
        ⏰ Pertanyaan 2: Jam & Hari
        </h4>
        <ul style="color:#adbac7; line-height:1.9; font-size:13.5px;">
            <li>Penyewaan memuncak pada pukul <strong style="color:#e6edf3;">08.00</strong> dan <strong style="color:#e6edf3;">17.00–18.00</strong> — pola <strong style="color:#e6edf3;">komuter</strong>.</li>
            <li><strong style="color:#e6edf3;">Hari Jumat</strong> mencatat penyewaan tertinggi dalam seminggu.</li>
        </ul>
        <p style="color:#58a6ff; font-weight:600; font-size:13px; margin-bottom:6px;">🎯 Rekomendasi Bisnis:</p>
        <ul style="color:#adbac7; line-height:1.9; font-size:13.5px;">
            <li>Prioritaskan ketersediaan sepeda di <strong style="color:#e6edf3;">titik strategis</strong> (stasiun, perkantoran) pada jam dan hari tersebut.</li>
            <li>Siapkan armada tambahan untuk mengakomodasi lonjakan permintaan di jam sibuk.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#161b22; border:1px solid #30363d; border-radius:10px; padding:18px; text-align:center;">
        <p style="color:#7d8590; font-size:12px; margin:0;">
        Sumber: Bike Sharing Dataset — Capital Bikeshare, Washington D.C. | 
        <strong style="color:#adbac7;">Arel Lafito Dinoris</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
