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
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }

    .main { background-color: #0f1117; }

    .stApp {
        background: linear-gradient(135deg, #0f1117 0%, #1a1d2e 50%, #0f1117 100%);
    }

    .metric-card {
        background: linear-gradient(135deg, #1e2030, #252840);
        border: 1px solid #3d4166;
        border-radius: 16px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 4px 24px rgba(99,102,241,0.12);
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-2px); }
    .metric-label {
        font-size: 12px;
        color: #8b8fa8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
        font-family: 'DM Mono', monospace;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #e8eaf6;
    }
    .metric-sub {
        font-size: 12px;
        color: #6366f1;
        margin-top: 4px;
    }

    .section-header {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .insight-box {
        background: linear-gradient(135deg, #1e2030, #1a2040);
        border-left: 4px solid #6366f1;
        border-radius: 0 12px 12px 0;
        padding: 16px 20px;
        color: #c5c8e6;
        font-size: 14px;
        margin-top: 12px;
    }

    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e2030;
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #8b8fa8;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #6366f1 !important;
        color: white !important;
    }

    .sidebar-title {
        color: #6366f1;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 16px;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e2030, #252840);
        border: 1px solid #3d4166;
        border-radius: 12px;
        padding: 16px;
    }
    div[data-testid="stMetric"] label {
        color: #8b8fa8 !important;
        font-size: 12px !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #e8eaf6 !important;
        font-weight: 700;
    }

    hr { border-color: #2d3155; }
</style>
""", unsafe_allow_html=True)

plt.style.use('dark_background')
CHART_BG    = '#1e2030'
GRID_COLOR  = '#2d3155'
TEXT_COLOR  = '#c5c8e6'
ACCENT1     = '#6366f1'
ACCENT2     = '#ec4899'
ACCENT3     = '#10b981'
ACCENT4     = '#f59e0b'
PALETTE     = [ACCENT1, ACCENT2, ACCENT3, ACCENT4]

def style_ax(ax, title=''):
    ax.set_facecolor(CHART_BG)
    ax.figure.patch.set_facecolor(CHART_BG)
    ax.spines[['top','right']].set_visible(False)
    ax.spines[['bottom','left']].set_color(GRID_COLOR)
    ax.tick_params(colors=TEXT_COLOR, labelsize=10)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.grid(axis='y', color=GRID_COLOR, alpha=0.5, linestyle='--')
    if title:
        ax.set_title(title, color=TEXT_COLOR, fontsize=13, fontweight='600', pad=14)


# ── LOAD DATA (tidak diubah) ──
BASE = os.path.dirname(__file__)
day_df  = pd.read_csv(os.path.join(BASE, 'main_data.csv'))
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

hour_df = pd.read_csv(os.path.join(BASE, 'hour.csv'))
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

hour_df['season']     = hour_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})
hour_df['weathersit'] = hour_df['weathersit'].map({
    1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'
})
hour_df['yr'] = hour_df['yr'].map({0: 2011, 1: 2012})

# day_df season & weather mapping (jika belum ada)
if day_df['season'].dtype != object:
    day_df['season'] = day_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})
if day_df['weathersit'].dtype != object:
    day_df['weathersit'] = day_df['weathersit'].map({
        1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'
    })
if day_df['yr'].dtype != object:
    day_df['yr'] = day_df['yr'].map({0: 2011, 1: 2012})

day_map = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
hour_df['weekday_name'] = hour_df['weekday'].map(day_map)

# ── SIDEBAR FILTERS ──
with st.sidebar:
    st.markdown('<div class="sidebar-title">🎛️ Filter & Slicer</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Tahun
    st.markdown("**📅 Tahun**")
    year_options = sorted(day_df['yr'].unique())
    selected_years = st.multiselect("Pilih Tahun", year_options, default=year_options)

    # Musim
    st.markdown("**🌿 Musim**")
    season_options = ['Spring','Summer','Fall','Winter']
    selected_seasons = st.multiselect("Pilih Musim", season_options, default=season_options)

    # Kondisi Cuaca
    st.markdown("**⛅ Kondisi Cuaca**")
    weather_options = [w for w in ['Clear','Mist','Light Rain/Snow','Heavy Rain/Snow']
                       if w in day_df['weathersit'].unique()]
    selected_weather = st.multiselect("Pilih Cuaca", weather_options, default=weather_options)

    # Rentang Tanggal
    st.markdown("**📆 Rentang Tanggal**")
    min_date = day_df['dteday'].min().date()
    max_date = day_df['dteday'].max().date()
    date_range = st.date_input("Pilih Rentang", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)

    # Hari Kerja
    st.markdown("**🗓️ Tipe Hari**")
    workday_filter = st.radio("Tampilkan", ["Semua", "Hari Kerja", "Libur/Weekend"])

    st.markdown("---")
    st.markdown('<div style="color:#8b8fa8;font-size:12px;">Arel Lafito Dinoris<br>areldinoris23@gmail.com</div>',
                unsafe_allow_html=True)

# ── APPLY FILTERS ──
if len(date_range) == 2:
    start_d, end_d = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_d, end_d = day_df['dteday'].min(), day_df['dteday'].max()

mask_day = (
    day_df['yr'].isin(selected_years) &
    day_df['season'].isin(selected_seasons) &
    day_df['weathersit'].isin(selected_weather) &
    day_df['dteday'].between(start_d, end_d)
)
if workday_filter == "Hari Kerja":
    mask_day &= day_df['workingday'] == 1
elif workday_filter == "Libur/Weekend":
    mask_day &= day_df['workingday'] == 0

filtered_day  = day_df[mask_day]

mask_hour = (
    hour_df['yr'].isin(selected_years) &
    hour_df['season'].isin(selected_seasons) &
    hour_df['weathersit'].isin(selected_weather) &
    hour_df['dteday'].between(start_d, end_d)
)
filtered_hour = hour_df[mask_hour]

# ── HEADER ──
st.markdown("""
<div style="padding:24px 0 8px 0">
    <div style="font-size:36px;font-weight:800;background:linear-gradient(90deg,#6366f1,#ec4899);
         -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        🚴 Bike Sharing Dashboard
    </div>
    <div style="color:#8b8fa8;font-size:14px;margin-top:4px;font-family:'DM Mono',monospace;">
        Capital Bikeshare · Washington D.C. · 2011–2012
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── METRIK ──
c1, c2, c3, c4, c5 = st.columns(5)
metrics = [
    ("Total Penyewaan", f"{filtered_day['cnt'].sum():,}", "periode terpilih"),
    ("Penyewaan Tertinggi", f"{filtered_day['cnt'].max():,}" if len(filtered_day) else "–", "dalam sehari"),
    ("Rata-rata/Hari", f"{filtered_day['cnt'].mean():.0f}" if len(filtered_day) else "–", "hari terpilih"),
    ("Rata-rata/Jam", f"{filtered_hour['cnt'].mean():.0f}" if len(filtered_hour) else "–", "jam terpilih"),
    ("Hari Dianalisis", f"{len(filtered_day):,}", "hari data"),
]
for col, (label, val, sub) in zip([c1,c2,c3,c4,c5], metrics):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════
#  TAB NAVIGASI
# ══════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Musim & Cuaca",
    "⏰ Jam & Hari",
    "📈 Tren & Segmentasi",
    "🔥 Heatmap & Distribusi",
    "✅ Kesimpulan"
])

# ──────────────────────────────
# TAB 1 — Musim & Cuaca
# ──────────────────────────────
with tab1:
    st.markdown('<div class="section-header">Pengaruh Musim & Cuaca terhadap Penyewaan Sepeda</div>',
                unsafe_allow_html=True)
    st.markdown("Pertanyaan: *Bagaimana kondisi cuaca dan musim memengaruhi jumlah penyewaan harian (2011–2012)?*")

    col_left, col_right = st.columns(2)

    with col_left:
        season_order = [s for s in ['Spring','Summer','Fall','Winter'] if s in selected_seasons]
        if season_order and len(filtered_day):
            season_avg = filtered_day.groupby('season')['cnt'].mean().reindex(season_order).dropna()
            fig, ax = plt.subplots(figsize=(7,4.5))
            fig.patch.set_facecolor(CHART_BG)
            colors = [ACCENT1, ACCENT4, ACCENT2, ACCENT3][:len(season_avg)]
            bars = ax.bar(season_avg.index, season_avg.values, color=colors,
                         width=0.55, edgecolor='none', zorder=3)
            for bar, v in zip(bars, season_avg.values):
                ax.text(bar.get_x()+bar.get_width()/2, v+60, f'{v:,.0f}',
                        ha='center', color=TEXT_COLOR, fontsize=10, fontweight='600')
            style_ax(ax, 'Rata-rata Penyewaan per Musim')
            ax.set_xlabel('Musim', color=TEXT_COLOR)
            ax.set_ylabel('Rata-rata Penyewaan', color=TEXT_COLOR)
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.warning("Tidak ada data untuk filter yang dipilih.")

    with col_right:
        if len(filtered_day):
            weather_avg = filtered_day.groupby('weathersit')['cnt'].mean().sort_values(ascending=False)
            fig, ax = plt.subplots(figsize=(7,4.5))
            fig.patch.set_facecolor(CHART_BG)
            bars = ax.bar(weather_avg.index, weather_avg.values,
                         color=[ACCENT3, ACCENT1, ACCENT4, ACCENT2][:len(weather_avg)],
                         width=0.55, edgecolor='none', zorder=3)
            for bar, v in zip(bars, weather_avg.values):
                ax.text(bar.get_x()+bar.get_width()/2, v+60, f'{v:,.0f}',
                        ha='center', color=TEXT_COLOR, fontsize=10, fontweight='600')
            style_ax(ax, 'Rata-rata Penyewaan per Kondisi Cuaca')
            ax.set_xlabel('Kondisi Cuaca', color=TEXT_COLOR)
            ax.set_ylabel('Rata-rata Penyewaan', color=TEXT_COLOR)
            ax.tick_params(axis='x', rotation=15)
            st.pyplot(fig)
            plt.close(fig)

    # Grouped bar: musim per tahun
    if len(filtered_day) and len(selected_years) > 0:
        st.markdown("#### Perbandingan Musim per Tahun")
        season_year = filtered_day.groupby(['yr','season'])['cnt'].mean().reset_index()
        pivot_sy    = season_year.pivot(index='season', columns='yr', values='cnt').reindex(
            [s for s in ['Spring','Summer','Fall','Winter'] if s in filtered_day['season'].unique()])

        fig, ax = plt.subplots(figsize=(10,4))
        fig.patch.set_facecolor(CHART_BG)
        x       = np.arange(len(pivot_sy))
        n_cols  = len(pivot_sy.columns)
        width   = 0.35 if n_cols == 2 else 0.6
        offset  = width / n_cols
        clrs    = [ACCENT1, ACCENT2, ACCENT3, ACCENT4]

        for i, yr in enumerate(pivot_sy.columns):
            vals  = pivot_sy[yr].fillna(0).values
            rects = ax.bar(x + i*offset - (n_cols-1)*offset/2, vals,
                          width=offset*0.85, label=str(yr), color=clrs[i], zorder=3)
            for r,v in zip(rects, vals):
                if v > 0:
                    ax.text(r.get_x()+r.get_width()/2, v+40, f'{v:,.0f}',
                            ha='center', color=TEXT_COLOR, fontsize=9)

        ax.set_xticks(x)
        ax.set_xticklabels(pivot_sy.index, color=TEXT_COLOR)
        style_ax(ax, 'Rata-rata Penyewaan per Musim & Tahun')
        ax.set_xlabel('Musim', color=TEXT_COLOR)
        ax.set_ylabel('Rata-rata Penyewaan', color=TEXT_COLOR)
        ax.legend(title='Tahun', title_fontsize=10, fontsize=10,
                 facecolor=CHART_BG, labelcolor=TEXT_COLOR)
        st.pyplot(fig)
        plt.close(fig)

    st.markdown('<div class="insight-box">💡 <b>Insight:</b> Fall + Clear weather adalah kombinasi terbaik untuk penyewaan sepeda. '
                'Cuaca Light Rain/Snow menyebabkan penurunan hingga 63% dibanding cuaca Clear.</div>',
                unsafe_allow_html=True)

# ──────────────────────────────
# TAB 2 — Jam & Hari
# ──────────────────────────────
with tab2:
    st.markdown('<div class="section-header">Pola Penyewaan per Jam & Hari</div>', unsafe_allow_html=True)
    st.markdown("Pertanyaan: *Pada jam berapa dan hari apa penyewaan sepeda mencapai puncaknya?*")

    col_l, col_r = st.columns(2)

    with col_l:
        if len(filtered_hour):
            hour_avg = filtered_hour.groupby('hr')['cnt'].mean()
            fig, ax  = plt.subplots(figsize=(7,4.5))
            fig.patch.set_facecolor(CHART_BG)
            ax.fill_between(hour_avg.index, hour_avg.values,
                           alpha=0.25, color=ACCENT1)
            ax.plot(hour_avg.index, hour_avg.values, marker='o', markersize=4,
                   color=ACCENT1, linewidth=2.5, zorder=3)
            ax.axvline(x=8,  color=ACCENT4, linestyle='--', alpha=0.8, linewidth=1.5, label='Jam 08:00')
            ax.axvline(x=17, color=ACCENT2, linestyle='--', alpha=0.8, linewidth=1.5, label='Jam 17:00')
            ax.set_xticks(range(0,24))
            style_ax(ax, 'Rata-rata Penyewaan per Jam')
            ax.set_xlabel('Jam', color=TEXT_COLOR)
            ax.set_ylabel('Rata-rata Penyewaan', color=TEXT_COLOR)
            ax.legend(facecolor=CHART_BG, labelcolor=TEXT_COLOR, fontsize=10)
            st.pyplot(fig)
            plt.close(fig)

    with col_r:
        if len(filtered_hour):
            wkday_order = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
            weekday_avg = (filtered_hour.groupby('weekday_name')['cnt'].mean()
                          .reindex([d for d in wkday_order if d in filtered_hour['weekday_name'].unique()]))
            fig, ax = plt.subplots(figsize=(7,4.5))
            fig.patch.set_facecolor(CHART_BG)
            clrs = [ACCENT2 if d == weekday_avg.idxmax() else ACCENT1 for d in weekday_avg.index]
            bars = ax.bar(weekday_avg.index, weekday_avg.values, color=clrs,
                         width=0.55, edgecolor='none', zorder=3)
            for bar, v in zip(bars, weekday_avg.values):
                ax.text(bar.get_x()+bar.get_width()/2, v+2, f'{v:,.0f}',
                        ha='center', color=TEXT_COLOR, fontsize=9, fontweight='600')
            style_ax(ax, 'Rata-rata Penyewaan per Hari')
            ax.set_xlabel('Hari', color=TEXT_COLOR)
            ax.set_ylabel('Rata-rata Penyewaan', color=TEXT_COLOR)
            st.pyplot(fig)
            plt.close(fig)

    # Pola jam per musim
    if len(filtered_hour):
        st.markdown("#### Pola Jam per Musim (Line Multi-Series)")
        hour_season = filtered_hour.groupby(['season','hr'])['cnt'].mean().reset_index()
        fig, ax     = plt.subplots(figsize=(12,4.5))
        fig.patch.set_facecolor(CHART_BG)
        season_colors = {'Spring':ACCENT3,'Summer':ACCENT4,'Fall':ACCENT2,'Winter':ACCENT1}
        for i, (season, grp) in enumerate(hour_season.groupby('season')):
            ax.plot(grp['hr'], grp['cnt'], label=season,
                   color=season_colors.get(season, PALETTE[i%4]), linewidth=2.5, marker='o', markersize=3)
        ax.set_xticks(range(0,24))
        style_ax(ax, 'Pola Penyewaan per Jam berdasarkan Musim')
        ax.set_xlabel('Jam', color=TEXT_COLOR)
        ax.set_ylabel('Rata-rata Penyewaan', color=TEXT_COLOR)
        ax.legend(title='Musim', facecolor=CHART_BG, labelcolor=TEXT_COLOR, fontsize=10)
        st.pyplot(fig)
        plt.close(fig)

    st.markdown('<div class="insight-box">💡 <b>Insight:</b> Dua puncak jelas (bimodal) di jam 08:00 dan 17:00 '
                'mencerminkan pola komuter. Hari Jumat mencatat penyewaan tertinggi dalam seminggu.</div>',
                unsafe_allow_html=True)

# ──────────────────────────────
# TAB 3 — Tren & Segmentasi
# ──────────────────────────────
with tab3:
    st.markdown('<div class="section-header">Tren Bulanan & Segmentasi Pengguna</div>', unsafe_allow_html=True)

    # Metrik pertumbuhan
    if len(filtered_day):
        growth  = filtered_day.groupby('yr')['cnt'].sum()
        reg_tot = filtered_day['registered'].sum()
        cas_tot = filtered_day['casual'].sum()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Registered", f"{reg_tot:,}")
        m2.metric("Total Casual",     f"{cas_tot:,}")
        m3.metric("% Registered",     f"{reg_tot/(reg_tot+cas_tot)*100:.1f}%")
        m4.metric("% Casual",         f"{cas_tot/(reg_tot+cas_tot)*100:.1f}%")

        st.markdown("<br>", unsafe_allow_html=True)
        col_l, col_r = st.columns(2)

        # Tren bulanan
        with col_l:
            monthly = filtered_day.groupby(['yr','mnth'])['cnt'].sum().reset_index()
            pivot   = monthly.pivot(index='mnth', columns='yr', values='cnt')
            fig, ax = plt.subplots(figsize=(7,4.5))
            fig.patch.set_facecolor(CHART_BG)
            clr_map = [ACCENT1, ACCENT2, ACCENT3, ACCENT4]
            for i, yr in enumerate(pivot.columns):
                ax.plot(pivot.index, pivot[yr], marker='o', label=str(yr),
                       color=clr_map[i], linewidth=2.5)
                ax.fill_between(pivot.index, pivot[yr], alpha=0.08, color=clr_map[i])
            ax.set_xticks(range(1,13))
            ax.set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun',
                               'Jul','Agu','Sep','Okt','Nov','Des'],
                              color=TEXT_COLOR, fontsize=9, rotation=30)
            style_ax(ax, 'Tren Penyewaan Bulanan per Tahun')
            ax.set_xlabel('Bulan', color=TEXT_COLOR)
            ax.set_ylabel('Total Penyewaan', color=TEXT_COLOR)
            ax.legend(facecolor=CHART_BG, labelcolor=TEXT_COLOR)
            st.pyplot(fig)
            plt.close(fig)

        # Donut chart casual vs registered
        with col_r:
            fig, ax = plt.subplots(figsize=(7,4.5))
            fig.patch.set_facecolor(CHART_BG)
            wedge_props = {'linewidth':3, 'edgecolor': CHART_BG}
            wedges, texts, autotexts = ax.pie(
                [cas_tot, reg_tot],
                labels=['Casual','Registered'],
                autopct='%1.1f%%',
                colors=[ACCENT4, ACCENT1],
                startangle=90,
                explode=(0.04, 0),
                wedgeprops=wedge_props,
                pctdistance=0.82,
                textprops={'color': TEXT_COLOR, 'fontsize': 12}
            )
            for at in autotexts:
                at.set_color('white')
                at.set_fontweight('bold')
            # inner circle for donut
            inner = plt.Circle((0,0), 0.55, color=CHART_BG)
            ax.add_artist(inner)
            ax.set_title('Proporsi Casual vs Registered', color=TEXT_COLOR, fontsize=13, fontweight='600')
            st.pyplot(fig)
            plt.close(fig)

        # Tren casual vs registered per bulan
        st.markdown("#### Tren Casual vs Registered per Bulan")
        monthly_seg = filtered_day.groupby('mnth')[['casual','registered']].sum().reset_index()
        fig, ax     = plt.subplots(figsize=(12,4.5))
        fig.patch.set_facecolor(CHART_BG)
        ax.bar(monthly_seg['mnth'], monthly_seg['registered'],
              label='Registered', color=ACCENT1, zorder=3)
        ax.bar(monthly_seg['mnth'], monthly_seg['casual'],
              bottom=monthly_seg['registered'], label='Casual', color=ACCENT4, zorder=3)
        ax.set_xticks(range(1,13))
        ax.set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun',
                           'Jul','Agu','Sep','Okt','Nov','Des'],
                          color=TEXT_COLOR, fontsize=10)
        style_ax(ax, 'Tren Penyewaan: Casual vs Registered (Stacked)')
        ax.set_xlabel('Bulan', color=TEXT_COLOR)
        ax.set_ylabel('Total Penyewaan', color=TEXT_COLOR)
        ax.legend(facecolor=CHART_BG, labelcolor=TEXT_COLOR)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.warning("Tidak ada data untuk filter yang dipilih.")

# ──────────────────────────────
# TAB 4 — Heatmap & Distribusi
# ──────────────────────────────
with tab4:
    st.markdown('<div class="section-header">Heatmap, Korelasi & Distribusi</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    # Heatmap jam vs hari
    with col_l:
        if len(filtered_hour):
            pivot_hm = filtered_hour.groupby(['weekday','hr'])['cnt'].mean().unstack()
            pivot_hm.index = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][:len(pivot_hm)]
            fig, ax   = plt.subplots(figsize=(10,4.5))
            fig.patch.set_facecolor(CHART_BG)
            im = ax.imshow(pivot_hm.values, aspect='auto', cmap='magma', interpolation='nearest')
            ax.set_xticks(range(24))
            ax.set_xticklabels(range(24), color=TEXT_COLOR, fontsize=8)
            ax.set_yticks(range(len(pivot_hm.index)))
            ax.set_yticklabels(pivot_hm.index, color=TEXT_COLOR, fontsize=10)
            cbar = plt.colorbar(im, ax=ax)
            cbar.ax.tick_params(colors=TEXT_COLOR)
            cbar.set_label('Rata-rata Penyewaan', color=TEXT_COLOR)
            ax.set_title('Heatmap: Jam vs Hari', color=TEXT_COLOR, fontsize=13, fontweight='600')
            ax.set_xlabel('Jam', color=TEXT_COLOR)
            ax.set_ylabel('Hari', color=TEXT_COLOR)
            fig.patch.set_facecolor(CHART_BG)
            st.pyplot(fig)
            plt.close(fig)

    # Scatter suhu vs penyewaan
    with col_r:
        if len(filtered_day):
            temp_c = filtered_day['temp'] * 41
            fig, ax = plt.subplots(figsize=(7,4.5))
            fig.patch.set_facecolor(CHART_BG)
            sc = ax.scatter(temp_c, filtered_day['cnt'],
                           alpha=0.45, c=filtered_day['cnt'],
                           cmap='plasma', s=18, edgecolors='none', zorder=3)
            z  = np.polyfit(temp_c, filtered_day['cnt'], 1)
            p  = np.poly1d(z)
            x_ln = np.linspace(temp_c.min(), temp_c.max(), 200)
            ax.plot(x_ln, p(x_ln), color=ACCENT3, linewidth=2.5, label='Trendline')
            cbar = plt.colorbar(sc, ax=ax)
            cbar.ax.tick_params(colors=TEXT_COLOR)
            cbar.set_label('Jumlah Penyewaan', color=TEXT_COLOR)
            style_ax(ax, 'Korelasi Suhu vs Penyewaan')
            ax.set_xlabel('Suhu (°C)', color=TEXT_COLOR)
            ax.set_ylabel('Jumlah Penyewaan', color=TEXT_COLOR)
            ax.legend(facecolor=CHART_BG, labelcolor=TEXT_COLOR)
            st.pyplot(fig)
            plt.close(fig)

    # Boxplot penyewaan per musim
    if len(filtered_day):
        st.markdown("#### Distribusi Penyewaan per Musim (Boxplot)")
        season_order = [s for s in ['Spring','Summer','Fall','Winter']
                       if s in filtered_day['season'].unique()]
        data_box = [filtered_day[filtered_day['season']==s]['cnt'].values for s in season_order]
        fig, ax  = plt.subplots(figsize=(10,4.5))
        fig.patch.set_facecolor(CHART_BG)
        bp = ax.boxplot(data_box, labels=season_order, patch_artist=True,
                       medianprops=dict(color='white', linewidth=2))
        clrs_box = [ACCENT3, ACCENT4, ACCENT2, ACCENT1]
        for patch, c in zip(bp['boxes'], clrs_box[:len(data_box)]):
            patch.set_facecolor(c)
            patch.set_alpha(0.75)
        for element in ['whiskers','caps','fliers']:
            for item in bp[element]:
                item.set_color(GRID_COLOR)
        style_ax(ax, 'Distribusi Penyewaan per Musim')
        ax.set_xlabel('Musim', color=TEXT_COLOR)
        ax.set_ylabel('Jumlah Penyewaan', color=TEXT_COLOR)
        st.pyplot(fig)
        plt.close(fig)

    # Hari kerja vs libur
    if len(filtered_day):
        st.markdown("#### Rata-rata Penyewaan: Hari Kerja vs Libur")
        workday_avg = filtered_day.groupby('workingday')['cnt'].mean()
        workday_avg.index = workday_avg.index.map({0:'Libur/Weekend', 1:'Hari Kerja'})
        fig, ax = plt.subplots(figsize=(6,4))
        fig.patch.set_facecolor(CHART_BG)
        bars = ax.bar(workday_avg.index, workday_avg.values,
                     color=[ACCENT2, ACCENT3], width=0.4, edgecolor='none', zorder=3)
        for bar, v in zip(bars, workday_avg.values):
            ax.text(bar.get_x()+bar.get_width()/2, v+30, f'{v:,.0f}',
                   ha='center', color=TEXT_COLOR, fontsize=11, fontweight='600')
        style_ax(ax, 'Hari Kerja vs Libur/Weekend')
        ax.set_ylabel('Rata-rata Penyewaan', color=TEXT_COLOR)
        st.pyplot(fig)
        plt.close(fig)

# ──────────────────────────────
# TAB 5 — Kesimpulan
# ──────────────────────────────
with tab5:
    st.markdown('<div class="section-header">✅ Kesimpulan & Rekomendasi Bisnis</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#1e2030,#252840);border-radius:16px;
                    padding:24px;border:1px solid #3d4166">
            <div style="color:#6366f1;font-size:16px;font-weight:700;margin-bottom:12px">
                📊 Pertanyaan 1 — Musim & Cuaca
            </div>
            <ul style="color:#c5c8e6;line-height:2;font-size:14px">
                <li><b>Musim Fall</b> dan <b>cuaca Clear</b> secara konsisten menghasilkan penyewaan tertinggi sepanjang 2011–2012.</li>
                <li>Kondisi cuaca buruk (<b>Light Rain/Snow</b>) menurunkan penyewaan hingga <b>63%</b> dibanding cuaca Clear.</li>
            </ul>
            <div style="color:#f59e0b;font-size:13px;margin-top:12px;font-weight:600">⚡ Rekomendasi Bisnis:</div>
            <ul style="color:#c5c8e6;line-height:2;font-size:13px">
                <li>Tingkatkan armada di <b>musim Fall</b> dengan cuaca cerah.</li>
                <li>Kurangi operasional saat <b>cuaca buruk</b> untuk efisiensi biaya.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#1e2030,#252840);border-radius:16px;
                    padding:24px;border:1px solid #3d4166">
            <div style="color:#ec4899;font-size:16px;font-weight:700;margin-bottom:12px">
                ⏰ Pertanyaan 2 — Jam & Hari
            </div>
            <ul style="color:#c5c8e6;line-height:2;font-size:14px">
                <li>Penyewaan memuncak pukul <b>08:00</b> dan <b>17:00–18:00</b> — pola <b>komuter</b>.</li>
                <li><b>Hari Jumat</b> mencatat penyewaan tertinggi dalam seminggu.</li>
            </ul>
            <div style="color:#f59e0b;font-size:13px;margin-top:12px;font-weight:600">⚡ Rekomendasi Bisnis:</div>
            <ul style="color:#c5c8e6;line-height:2;font-size:13px">
                <li>Prioritaskan ketersediaan sepeda di <b>stasiun & perkantoran</b> pada jam sibuk.</li>
                <li>Siapkan <b>armada tambahan</b> untuk lonjakan permintaan jam 08:00 & 17:00.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Summary stats dari data terfilter
    if len(filtered_day):
        st.markdown("#### 📋 Ringkasan Statistik (Data Terfilter)")
        summary = filtered_day[['cnt','casual','registered','temp','hum','windspeed']].describe().T
        summary.columns = ['Count','Mean','Std','Min','25%','50%','75%','Max']
        st.dataframe(summary.style
                    .format("{:.1f}")
                    .background_gradient(cmap='Blues', subset=['Mean','Max']),
                    use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;color:#8b8fa8;font-size:13px;font-family:'DM Mono',monospace">
        Sumber: Bike Sharing Dataset — Capital Bikeshare, Washington D.C.<br>
        <b style="color:#6366f1">Arel Lafito Dinoris</b> · areldinoris23@gmail.com · areldinoris
    </div>
    """, unsafe_allow_html=True)
