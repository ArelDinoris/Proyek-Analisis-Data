import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Syne', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        color: #e8e8f0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(255,255,255,0.04);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    section[data-testid="stSidebar"] * {
        color: #e8e8f0 !important;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 16px;
        backdrop-filter: blur(10px);
    }
    [data-testid="metric-container"] label {
        color: #a0a0c0 !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 1.6rem !important;
        font-weight: 800 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        color: #4ade80 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #a0a0c0;
        font-family: 'Syne', sans-serif;
        font-weight: 600;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white !important;
    }

    /* Info box */
    .stAlert {
        background: rgba(99,102,241,0.12) !important;
        border: 1px solid rgba(99,102,241,0.3) !important;
        border-radius: 10px;
        color: #c7c7f0 !important;
    }

    /* Section header */
    .section-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #a78bfa;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    /* Divider */
    hr { border-color: rgba(255,255,255,0.08) !important; }

    /* Plotly charts background fix */
    .js-plotly-plot .plotly .bg { fill: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ──
BASE_DIR = os.path.dirname(__file__)
day_df = pd.read_csv(os.path.join(BASE_DIR, 'main_data.csv'))
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

hour_df = pd.read_csv(os.path.join(BASE_DIR, 'hour.csv'))
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Mapping
hour_df['season'] = hour_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})
hour_df['weathersit'] = hour_df['weathersit'].map({
    1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'
})
hour_df['yr'] = hour_df['yr'].map({0: 2011, 1: 2012})

day_df['season'] = day_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})
day_df['weathersit'] = day_df['weathersit'].map({
    1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'
})
day_df['yr'] = day_df['yr'].map({0: 2011, 1: 2012})

MONTH_MAP = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'Mei',6:'Jun',
             7:'Jul',8:'Agu',9:'Sep',10:'Okt',11:'Nov',12:'Des'}
DAY_MAP = {0:'Sun',1:'Mon',2:'Tue',3:'Wed',4:'Thu',5:'Fri',6:'Sat'}

PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(255,255,255,0.03)',
    font=dict(color='#e8e8f0', family='DM Sans'),
    title_font=dict(family='Syne', size=14, color='#ffffff'),
    xaxis=dict(gridcolor='rgba(255,255,255,0.06)', linecolor='rgba(255,255,255,0.1)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.06)', linecolor='rgba(255,255,255,0.1)'),
    hoverlabel=dict(bgcolor='#1a1a2e', font_color='white', bordercolor='#6366f1'),
    margin=dict(t=50, b=40, l=50, r=20),
)

# ── SIDEBAR FILTERS ──
st.sidebar.markdown("## 🎛️ Filter & Slicer")
st.sidebar.markdown("---")

# Tahun
st.sidebar.markdown("**📅 Tahun**")
year_options = sorted(day_df['yr'].unique())
selected_years = st.sidebar.multiselect("Pilih Tahun", year_options, default=year_options)

# Musim
st.sidebar.markdown("**🌤️ Musim**")
season_options = ['Spring', 'Summer', 'Fall', 'Winter']
selected_seasons = st.sidebar.multiselect("Pilih Musim", season_options, default=season_options)

# Cuaca
st.sidebar.markdown("**🌦️ Kondisi Cuaca**")
weather_options = day_df['weathersit'].dropna().unique().tolist()
selected_weather = st.sidebar.multiselect("Pilih Cuaca", weather_options, default=weather_options)

# Rentang tanggal
st.sidebar.markdown("**📆 Rentang Tanggal**")
date_min = day_df['dteday'].min().date()
date_max = day_df['dteday'].max().date()
date_range = st.sidebar.date_input("Pilih Rentang", [date_min, date_max], min_value=date_min, max_value=date_max)

# Hari kerja
st.sidebar.markdown("**🗓️ Tipe Hari**")
workday_filter = st.sidebar.radio("Tipe Hari", ["Semua", "Hari Kerja", "Libur/Weekend"])

st.sidebar.markdown("---")
st.sidebar.caption("🚴 Bike Sharing Dashboard | Arel Lafito Dinoris")

# ── APPLY FILTERS ──
def apply_filters(df):
    d = df.copy()
    if selected_years:
        d = d[d['yr'].isin(selected_years)]
    if selected_seasons:
        d = d[d['season'].isin(selected_seasons)]
    if selected_weather:
        d = d[d['weathersit'].isin(selected_weather)]
    if len(date_range) == 2:
        d = d[(d['dteday'].dt.date >= date_range[0]) & (d['dteday'].dt.date <= date_range[1])]
    if workday_filter == "Hari Kerja":
        d = d[d['workingday'] == 1]
    elif workday_filter == "Libur/Weekend":
        d = d[d['workingday'] == 0]
    return d

def apply_filters_hour(df):
    d = df.copy()
    if selected_years:
        d = d[d['yr'].isin(selected_years)]
    if selected_seasons:
        d = d[d['season'].isin(selected_seasons)]
    if len(date_range) == 2:
        d = d[(d['dteday'].dt.date >= date_range[0]) & (d['dteday'].dt.date <= date_range[1])]
    if workday_filter == "Hari Kerja":
        d = d[d['workingday'] == 1]
    elif workday_filter == "Libur/Weekend":
        d = d[d['workingday'] == 0]
    return d

fday = apply_filters(day_df)
fhour = apply_filters_hour(hour_df)

# ── HEADER ──
st.markdown("""
<div style='padding: 2rem 0 1rem 0;'>
  <h1 style='font-family:Syne,sans-serif; font-size:2.6rem; font-weight:800;
             background: linear-gradient(135deg, #a78bfa, #60a5fa);
             -webkit-background-clip: text; -webkit-text-fill-color: transparent;
             margin-bottom:0.3rem;'>
    🚴 Bike Sharing Dashboard
  </h1>
  <p style='color:#7070a0; font-size:0.9rem; margin:0;'>
    Arel Lafito Dinoris &nbsp;·&nbsp; areldinoris23@gmail.com &nbsp;·&nbsp; ID: areldinoris
  </p>
</div>
""", unsafe_allow_html=True)

# ── METRIK ──
if fday.empty:
    st.warning("⚠️ Tidak ada data sesuai filter. Coba ubah pilihan filter.")
    st.stop()

total_rent = fday['cnt'].sum()
max_rent   = fday['cnt'].max()
avg_day    = fday['cnt'].mean()
avg_hour   = fhour['cnt'].mean() if not fhour.empty else 0

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric('🚲 Total Penyewaan', f"{total_rent:,}")
col_m2.metric('📈 Penyewaan Tertinggi', f"{max_rent:,}")
col_m3.metric('📊 Rata-rata/Hari', f"{avg_day:.0f}")
col_m4.metric('⏱️ Rata-rata/Jam', f"{avg_hour:.0f}")

st.markdown("---")

# ══════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌤️ Musim & Cuaca",
    "⏰ Jam & Hari",
    "📈 Tren & Segmentasi",
    "🔥 Heatmap",
    "✅ Kesimpulan"
])

# ────────────────────────────────────────────
# TAB 1 — Musim & Cuaca
# ────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">Pengaruh Musim & Cuaca terhadap Penyewaan Harian</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        season_order = ['Spring', 'Summer', 'Fall', 'Winter']
        season_avg = fday.groupby('season')['cnt'].mean().reindex(
            [s for s in season_order if s in fday['season'].unique()]
        ).reset_index()
        season_avg.columns = ['season', 'avg']

        fig_s = px.bar(season_avg, x='season', y='avg',
                       color='season',
                       color_discrete_map={'Spring':'#4CAF50','Summer':'#FFC107',
                                           'Fall':'#F44336','Winter':'#2196F3'},
                       text=season_avg['avg'].round(0).astype(int),
                       title='Rata-rata Penyewaan per Musim')
        fig_s.update_traces(textposition='outside', textfont_size=12)
        fig_s.update_layout(**PLOTLY_LAYOUT, showlegend=False,
                            xaxis_title='Musim', yaxis_title='Rata-rata Penyewaan')
        st.plotly_chart(fig_s, use_container_width=True)

    with col_b:
        weather_avg = fday.groupby('weathersit')['cnt'].mean().sort_values(ascending=False).reset_index()
        weather_avg.columns = ['weathersit', 'avg']

        fig_w = px.bar(weather_avg, x='weathersit', y='avg',
                       color='avg',
                       color_continuous_scale=['#1565C0','#42A5F5','#90CAF9'],
                       text=weather_avg['avg'].round(0).astype(int),
                       title='Rata-rata Penyewaan per Kondisi Cuaca')
        fig_w.update_traces(textposition='outside', textfont_size=12)
        fig_w.update_layout(**PLOTLY_LAYOUT, showlegend=False,
                            coloraxis_showscale=False,
                            xaxis_title='Kondisi Cuaca', yaxis_title='Rata-rata Penyewaan')
        st.plotly_chart(fig_w, use_container_width=True)

    # Kombinasi musim × cuaca
    st.markdown("#### 🔬 Kombinasi Musim × Cuaca")
    combo = fday.groupby(['season','weathersit'])['cnt'].mean().reset_index()
    combo.columns = ['season','weathersit','avg']
    fig_combo = px.bar(combo, x='season', y='avg', color='weathersit',
                       barmode='group',
                       color_discrete_sequence=px.colors.qualitative.Bold,
                       title='Rata-rata Penyewaan: Kombinasi Musim & Cuaca')
    fig_combo.update_layout(**PLOTLY_LAYOUT,
                            xaxis_title='Musim', yaxis_title='Rata-rata Penyewaan')
    st.plotly_chart(fig_combo, use_container_width=True)

    st.info('💡 Fall + Clear weather adalah kombinasi terbaik. Cuaca Light Rain/Snow menyebabkan penurunan penyewaan hingga 63% dibanding cuaca Clear.')

# ────────────────────────────────────────────
# TAB 2 — Jam & Hari
# ────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">Pola Penyewaan Berdasarkan Jam dan Hari</div>', unsafe_allow_html=True)

    col_c, col_d = st.columns(2)

    with col_c:
        hour_avg = fhour.groupby('hr')['cnt'].mean().reset_index()
        hour_avg.columns = ['hr', 'avg']

        fig_hr = go.Figure()
        fig_hr.add_trace(go.Scatter(
            x=hour_avg['hr'], y=hour_avg['avg'],
            mode='lines+markers',
            line=dict(color='#E53935', width=2.5),
            marker=dict(size=6, color='#FF7043'),
            fill='tozeroy',
            fillcolor='rgba(229,57,53,0.1)',
            name='Rata-rata'
        ))
        fig_hr.add_vline(x=8,  line_dash='dash', line_color='#a78bfa', annotation_text='08:00')
        fig_hr.add_vline(x=17, line_dash='dash', line_color='#60a5fa', annotation_text='17:00')
        fig_hr.update_layout(**PLOTLY_LAYOUT,
                             title='Rata-rata Penyewaan per Jam',
                             xaxis_title='Jam', yaxis_title='Rata-rata Penyewaan',
                             xaxis=dict(tickmode='linear', dtick=2,
                                        gridcolor='rgba(255,255,255,0.06)'))
        st.plotly_chart(fig_hr, use_container_width=True)

    with col_d:
        weekday_avg = fhour.groupby('weekday')['cnt'].mean().reset_index()
        weekday_avg['day_name'] = weekday_avg['weekday'].map(DAY_MAP)
        weekday_avg.columns = ['weekday','avg','day_name']
        weekday_avg = weekday_avg.sort_values('weekday')

        fig_wd = px.bar(weekday_avg, x='day_name', y='avg',
                        color='avg',
                        color_continuous_scale=['#6d28d9','#8b5cf6','#a78bfa','#c4b5fd'],
                        text=weekday_avg['avg'].round(0).astype(int),
                        title='Rata-rata Penyewaan per Hari')
        fig_wd.update_traces(textposition='outside', textfont_size=11)
        fig_wd.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False,
                             xaxis_title='Hari', yaxis_title='Rata-rata Penyewaan')
        st.plotly_chart(fig_wd, use_container_width=True)

    # Breakdown jam per musim
    st.markdown("#### 🕐 Pola Jam per Musim")
    if not fhour.empty and 'season' in fhour.columns:
        hr_season = fhour.groupby(['hr','season'])['cnt'].mean().reset_index()
        hr_season.columns = ['hr','season','avg']
        fig_hrsea = px.line(hr_season, x='hr', y='avg', color='season',
                            color_discrete_map={'Spring':'#4CAF50','Summer':'#FFC107',
                                                'Fall':'#F44336','Winter':'#2196F3'},
                            markers=True,
                            title='Rata-rata Penyewaan per Jam, Dipisah per Musim')
        fig_hrsea.update_layout(**PLOTLY_LAYOUT,
                                xaxis_title='Jam', yaxis_title='Rata-rata Penyewaan')
        st.plotly_chart(fig_hrsea, use_container_width=True)

    st.info('💡 Dua puncak jelas (bimodal) di jam 08.00 dan 17.00 mencerminkan pola komuter. Dini hari (01.00–04.00) adalah waktu terendah.')

# ────────────────────────────────────────────
# TAB 3 — Tren & Segmentasi
# ────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">Tren Bulanan & Segmentasi Pengguna</div>', unsafe_allow_html=True)

    # Ringkasan metrik
    growth = fday.groupby('yr')['cnt'].sum()
    years_avail = sorted(growth.index.tolist())
    casual_total = fday['casual'].sum()
    registered_total = fday['registered'].sum()

    cols_m = st.columns(len(years_avail) + 3)
    for i, yr in enumerate(years_avail):
        cols_m[i].metric(f'Total {yr}', f"{growth[yr]:,}")
    if len(years_avail) == 2:
        pct = ((growth[years_avail[1]] - growth[years_avail[0]]) / growth[years_avail[0]]) * 100
        cols_m[2].metric('Pertumbuhan', f"{pct:.1f}%", delta=f"{pct:.1f}%")
    cols_m[-2].metric('Casual', f"{casual_total:,}")
    cols_m[-1].metric('Registered', f"{registered_total:,}")

    st.markdown("---")

    col_e, col_f = st.columns(2)

    with col_e:
        monthly = fday.groupby(['yr','mnth'])['cnt'].sum().reset_index()
        monthly['bulan'] = monthly['mnth'].map(MONTH_MAP)
        monthly['Tahun'] = monthly['yr'].astype(str)
        fig_trend = px.line(monthly, x='mnth', y='cnt', color='Tahun',
                            color_discrete_map={'2011':'#42A5F5','2012':'#EF5350'},
                            markers=True,
                            title='Tren Penyewaan Bulanan: 2011 vs 2012')
        fig_trend.update_layout(**PLOTLY_LAYOUT,
                                xaxis=dict(tickmode='array',
                                           tickvals=list(range(1,13)),
                                           ticktext=list(MONTH_MAP.values()),
                                           gridcolor='rgba(255,255,255,0.06)'),
                                xaxis_title='Bulan', yaxis_title='Total Penyewaan')
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_f:
        fig_pie = px.pie(
            values=[casual_total, registered_total],
            names=['Casual','Registered'],
            color_discrete_sequence=['#FFC107','#4CAF50'],
            title='Proporsi Pengguna: Casual vs Registered',
            hole=0.4
        )
        fig_pie.update_traces(textposition='outside', textinfo='percent+label',
                              pull=[0.05, 0])
        fig_pie.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_pie, use_container_width=True)

    col_g, col_h = st.columns(2)

    with col_g:
        workday_avg = fday.groupby('workingday')['cnt'].mean().reset_index()
        workday_avg['tipe'] = workday_avg['workingday'].map({0:'Libur/Weekend', 1:'Hari Kerja'})
        fig_work = px.bar(workday_avg, x='tipe', y='cnt',
                          color='tipe',
                          color_discrete_map={'Libur/Weekend':'#AB47BC','Hari Kerja':'#26A69A'},
                          text=workday_avg['cnt'].round(0).astype(int),
                          title='Rata-rata Penyewaan: Hari Kerja vs Libur')
        fig_work.update_traces(textposition='outside', textfont_size=13)
        fig_work.update_layout(**PLOTLY_LAYOUT, showlegend=False,
                               xaxis_title='Tipe Hari', yaxis_title='Rata-rata Penyewaan')
        st.plotly_chart(fig_work, use_container_width=True)

    with col_h:
        temp_c = fday['temp'] * 41
        fig_scatter = px.scatter(
            fday, x=temp_c, y='cnt',
            color='season',
            color_discrete_map={'Spring':'#4CAF50','Summer':'#FFC107',
                                'Fall':'#F44336','Winter':'#2196F3'},
            opacity=0.6, size_max=8,
            trendline='ols',
            trendline_scope='overall',
            trendline_color_override='#60a5fa',
            title='Korelasi Suhu vs Jumlah Penyewaan',
            labels={'x':'Suhu (°C)', 'cnt':'Jumlah Penyewaan', 'season':'Musim'}
        )
        fig_scatter.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_scatter, use_container_width=True)

# ────────────────────────────────────────────
# TAB 4 — Heatmap
# ────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">Heatmap Penyewaan</div>', unsafe_allow_html=True)

    col_i, col_j = st.columns(2)

    with col_i:
        hm_data = fhour.groupby(['weekday','hr'])['cnt'].mean().reset_index()
        hm_pivot = hm_data.pivot(index='weekday', columns='hr', values='cnt')
        hm_pivot.index = [DAY_MAP[i] for i in hm_pivot.index]

        fig_hm = px.imshow(hm_pivot,
                           color_continuous_scale='Viridis',
                           aspect='auto',
                           title='Heatmap: Hari × Jam (Rata-rata Penyewaan)',
                           labels=dict(x='Jam', y='Hari', color='Rata-rata'))
        fig_hm.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_hm, use_container_width=True)

    with col_j:
        hm_data2 = fday.groupby(['season','mnth'])['cnt'].mean().reset_index()
        hm_pivot2 = hm_data2.pivot(index='season', columns='mnth', values='cnt')
        hm_pivot2.columns = [MONTH_MAP[c] for c in hm_pivot2.columns]

        fig_hm2 = px.imshow(hm_pivot2,
                            color_continuous_scale='RdYlGn',
                            aspect='auto',
                            title='Heatmap: Musim × Bulan (Rata-rata Penyewaan)',
                            labels=dict(x='Bulan', y='Musim', color='Rata-rata'))
        fig_hm2.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_hm2, use_container_width=True)

    # Casual vs Registered per hari & jam
    st.markdown("#### 👥 Casual vs Registered per Jam")
    cr_hour = fhour.groupby('hr')[['casual','registered']].mean().reset_index()
    fig_cr = go.Figure()
    fig_cr.add_trace(go.Bar(name='Casual', x=cr_hour['hr'], y=cr_hour['casual'],
                            marker_color='#FFC107'))
    fig_cr.add_trace(go.Bar(name='Registered', x=cr_hour['hr'], y=cr_hour['registered'],
                            marker_color='#4CAF50'))
    fig_cr.update_layout(**PLOTLY_LAYOUT, barmode='stack',
                         title='Casual vs Registered per Jam',
                         xaxis_title='Jam', yaxis_title='Rata-rata Penyewaan')
    st.plotly_chart(fig_cr, use_container_width=True)

# ────────────────────────────────────────────
# TAB 5 — Kesimpulan
# ────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-title">Kesimpulan & Rekomendasi Bisnis</div>', unsafe_allow_html=True)
    st.markdown("")

    col_k, col_l = st.columns(2)

    with col_k:
        st.markdown("""
<div style='background:rgba(99,102,241,0.12); border:1px solid rgba(99,102,241,0.3);
            border-radius:14px; padding:24px;'>
<h4 style='color:#a78bfa; font-family:Syne,sans-serif; margin-top:0;'>
  📊 Pertanyaan 1 — Musim & Cuaca
</h4>
<ul style='color:#d0d0e8; line-height:1.9; padding-left:1.2rem;'>
  <li><strong>Musim Fall</strong> dan <strong>cuaca Clear</strong> secara konsisten menghasilkan jumlah penyewaan tertinggi.</li>
  <li>Kondisi cuaca buruk (<strong>Light Rain/Snow</strong>) menurunkan penyewaan hingga <strong>63%</strong>.</li>
</ul>
<p style='color:#a78bfa; font-size:0.85rem; font-weight:600; margin-bottom:4px;'>💼 Rekomendasi:</p>
<ul style='color:#d0d0e8; line-height:1.9; padding-left:1.2rem;'>
  <li>Tingkatkan ketersediaan armada di <strong>musim Fall</strong> saat cuaca cerah.</li>
  <li>Kurangi operasional saat <strong>cuaca buruk</strong> untuk efisiensi biaya.</li>
</ul>
</div>
""", unsafe_allow_html=True)

    with col_l:
        st.markdown("""
<div style='background:rgba(96,165,250,0.1); border:1px solid rgba(96,165,250,0.3);
            border-radius:14px; padding:24px;'>
<h4 style='color:#60a5fa; font-family:Syne,sans-serif; margin-top:0;'>
  ⏰ Pertanyaan 2 — Jam & Hari
</h4>
<ul style='color:#d0d0e8; line-height:1.9; padding-left:1.2rem;'>
  <li>Penyewaan memuncak pukul <strong>08.00</strong> dan <strong>17.00–18.00</strong> — pola komuter.</li>
  <li><strong>Hari Jumat</strong> mencatat penyewaan tertinggi dalam seminggu.</li>
</ul>
<p style='color:#60a5fa; font-size:0.85rem; font-weight:600; margin-bottom:4px;'>💼 Rekomendasi:</p>
<ul style='color:#d0d0e8; line-height:1.9; padding-left:1.2rem;'>
  <li>Prioritaskan ketersediaan sepeda di <strong>stasiun & perkantoran</strong> pada jam sibuk.</li>
  <li>Siapkan armada tambahan untuk lonjakan permintaan di jam puncak.</li>
</ul>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Sumber: Bike Sharing Dataset — Capital Bikeshare, Washington D.C. | Arel Lafito Dinoris")
