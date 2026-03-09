import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import streamlit as st
import os

# ── PAGE CONFIG ──
st.set_page_config(
    page_title='Bike Sharing Dashboard',
    page_icon='🚴',
    layout='wide',
    initial_sidebar_state='expanded'
)

# ── CUSTOM CSS ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    .stApp { background: #0f1117; color: #e8eaf0; }

    section[data-testid="stSidebar"] {
        background: #161b27;
        border-right: 1px solid #2a2f3e;
    }
    section[data-testid="stSidebar"] * { color: #c8cdd8 !important; }

    h1 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 800 !important;
        font-size: 2.4rem !important;
        background: linear-gradient(135deg, #64b5f6, #4dd0e1, #81c784);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    h2, h3 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        color: #e8eaf0 !important;
    }

    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a2035, #1e2540);
        border: 1px solid #2a3050;
        border-radius: 16px;
        padding: 20px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    [data-testid="metric-container"] label {
        color: #7986a3 !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #64b5f6 !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    .stAlert {
        background: linear-gradient(135deg, #1a2a1a, #1e3020) !important;
        border: 1px solid #2d4a2d !important;
        border-left: 4px solid #81c784 !important;
        border-radius: 12px !important;
        color: #a5d6a7 !important;
    }

    hr { border: none; border-top: 1px solid #2a2f3e; margin: 1.5rem 0; }

    .section-label {
        font-family: 'Syne', sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #4dd0e1;
        margin-bottom: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ──
base_dir = os.path.dirname(__file__)
day_df = pd.read_csv(os.path.join(base_dir, 'main_data.csv'))
hour_df = pd.read_csv(os.path.join(base_dir, 'hour.csv'))

day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

hour_df['season'] = hour_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})
hour_df['weathersit'] = hour_df['weathersit'].map({
    1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'
})
hour_df['yr'] = hour_df['yr'].map({0: 2011, 1: 2012})

# ── SIDEBAR ──
with st.sidebar:
    st.markdown('<p class="section-label">🚴 Bike Sharing</p>', unsafe_allow_html=True)
    st.markdown('### Dashboard Analisis')
    st.markdown('**Arel Lafito Dinoris**  \nareldinoris23@gmail.com  \nID: areldinoris')
    st.markdown('---')
    st.markdown('<p class="section-label">Filter Data</p>', unsafe_allow_html=True)

    year_options = ['Semua'] + sorted(day_df['yr'].unique().tolist())
    selected_year = st.selectbox('📅 Tahun', year_options)

    min_date = day_df['dteday'].min()
    max_date = day_df['dteday'].max()
    date_range = st.date_input('📆 Rentang Tanggal',
                               value=[min_date, max_date],
                               min_value=min_date, max_value=max_date)

    st.markdown('---')
    st.markdown('<p class="section-label">Pertanyaan Bisnis</p>', unsafe_allow_html=True)
    st.markdown('**1.** Pengaruh cuaca & musim terhadap penyewaan')
    st.markdown('**2.** Peak hour & hari tersibuk dalam seminggu')

# ── FILTER ──
start_date = pd.Timestamp(date_range[0]) if len(date_range) > 0 else min_date
end_date   = pd.Timestamp(date_range[1]) if len(date_range) > 1 else max_date

if selected_year == 'Semua':
    fd = day_df[(day_df['dteday'] >= start_date) & (day_df['dteday'] <= end_date)]
    fh = hour_df[(hour_df['dteday'] >= start_date) & (hour_df['dteday'] <= end_date)]
else:
    fd = day_df[(day_df['yr'] == selected_year) &
                (day_df['dteday'] >= start_date) & (day_df['dteday'] <= end_date)]
    fh = hour_df[(hour_df['yr'] == selected_year) &
                 (hour_df['dteday'] >= start_date) & (hour_df['dteday'] <= end_date)]

# ── MATPLOTLIB DARK THEME ──
plt.rcParams.update({
    'figure.facecolor': '#1a2035', 'axes.facecolor': '#1a2035',
    'axes.edgecolor': '#2a3050', 'axes.labelcolor': '#8892a4',
    'xtick.color': '#8892a4', 'ytick.color': '#8892a4',
    'text.color': '#e8eaf0', 'grid.color': '#2a3050', 'grid.alpha': 0.5,
})

# ── HEADER ──
st.markdown('# 🚴 Bike Sharing Dashboard')
st.markdown('<p style="color:#7986a3;font-size:0.95rem;margin-top:-10px;">Capital Bikeshare, Washington D.C. — 2011 & 2012</p>', unsafe_allow_html=True)
st.markdown('---')

# ── METRIK ──
c1, c2, c3, c4 = st.columns(4)
c1.metric('🔢 Total Penyewaan', f"{fd['cnt'].sum():,}")
c2.metric('📈 Tertinggi/Hari', f"{fd['cnt'].max():,}")
c3.metric('📊 Rata-rata/Hari', f"{fd['cnt'].mean():.0f}")
c4.metric('⏱ Rata-rata/Jam', f"{fh['cnt'].mean():.0f}")
st.markdown('---')

# ══════════════════════════════
# PERTANYAAN 1
# ══════════════════════════════
st.markdown('<p class="section-label">Pertanyaan 1</p>', unsafe_allow_html=True)
st.subheader('🌤 Pengaruh Kondisi Cuaca & Musim terhadap Jumlah Penyewaan Sepeda')

fig1, axes = plt.subplots(1, 2, figsize=(14, 5))
fig1.patch.set_facecolor('#1a2035')

season_order = ['Spring', 'Summer', 'Fall', 'Winter']
season_avg = fd.groupby('season')['cnt'].mean().reindex(season_order)
axes[0].bar(season_avg.index, season_avg.values,
            color=['#4CAF50','#FFC107','#F44336','#2196F3'], edgecolor='none', width=0.6)
axes[0].set_title('Rata-rata Penyewaan per Musim', fontsize=13, pad=15, fontweight='bold')
axes[0].set_xlabel('Musim', fontsize=10)
axes[0].set_ylabel('Rata-rata Penyewaan', fontsize=10)
axes[0].spines[['top','right']].set_visible(False)
axes[0].grid(axis='y', alpha=0.3)
for i, v in enumerate(season_avg.values):
    axes[0].text(i, v + 50, str(round(v)), ha='center', fontsize=10, fontweight='bold')

weather_avg = fd.groupby('weathersit')['cnt'].mean().sort_values(ascending=False)
axes[1].bar(weather_avg.index, weather_avg.values,
            color=['#64b5f6','#4dd0e1','#ef9a9a'][:len(weather_avg)], edgecolor='none', width=0.5)
axes[1].set_title('Rata-rata Penyewaan per Kondisi Cuaca', fontsize=13, pad=15, fontweight='bold')
axes[1].set_xlabel('Kondisi Cuaca', fontsize=10)
axes[1].set_ylabel('Rata-rata Penyewaan', fontsize=10)
axes[1].tick_params(axis='x', rotation=15)
axes[1].spines[['top','right']].set_visible(False)
axes[1].grid(axis='y', alpha=0.3)
for i, v in enumerate(weather_avg.values):
    axes[1].text(i, v + 50, str(round(v)), ha='center', fontsize=10, fontweight='bold')

plt.tight_layout(pad=2.0)
st.pyplot(fig1)
plt.close(fig1)
st.info('💡 **Insight:** Musim Fall menghasilkan penyewaan tertinggi (5.644). Cuaca Clear vs Light Rain/Snow menunjukkan penurunan penyewaan hingga **63%** — cuaca adalah faktor penentu utama.')
st.markdown('---')

# ══════════════════════════════
# PERTANYAAN 2
# ══════════════════════════════
st.markdown('<p class="section-label">Pertanyaan 2</p>', unsafe_allow_html=True)
st.subheader('⏰ Peak Hour & Hari Tersibuk Penyewaan Sepeda dalam Seminggu')

fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
fig2.patch.set_facecolor('#1a2035')

hour_avg = fh.groupby('hr')['cnt'].mean()
axes2[0].plot(hour_avg.index, hour_avg.values, marker='o', markersize=4,
              color='#ef5350', linewidth=2, markerfacecolor='#ff8a80')
axes2[0].fill_between(hour_avg.index, hour_avg.values, alpha=0.15, color='#ef5350')
axes2[0].axvline(x=8,  color='#90caf9', linestyle='--', alpha=0.7, linewidth=1.5, label='Jam 08.00')
axes2[0].axvline(x=17, color='#80deea', linestyle='--', alpha=0.7, linewidth=1.5, label='Jam 17.00')
axes2[0].set_title('Rata-rata Penyewaan per Jam', fontsize=13, pad=15, fontweight='bold')
axes2[0].set_xlabel('Jam', fontsize=10)
axes2[0].set_ylabel('Rata-rata Penyewaan', fontsize=10)
axes2[0].set_xticks(range(0, 24))
axes2[0].spines[['top','right']].set_visible(False)
axes2[0].grid(axis='y', alpha=0.3)
axes2[0].legend(framealpha=0.2, labelcolor='#e8eaf0')

day_map = {0:'Sun',1:'Mon',2:'Tue',3:'Wed',4:'Thu',5:'Fri',6:'Sat'}
weekday_avg = fh.groupby('weekday')['cnt'].mean().rename(index=day_map)
bars_wd = axes2[1].bar(weekday_avg.index, weekday_avg.values,
                       color='#ab47bc', edgecolor='none', width=0.6)
bars_wd[weekday_avg.values.argmax()].set_color('#ce93d8')
axes2[1].set_title('Rata-rata Penyewaan per Hari', fontsize=13, pad=15, fontweight='bold')
axes2[1].set_xlabel('Hari', fontsize=10)
axes2[1].set_ylabel('Rata-rata Penyewaan', fontsize=10)
axes2[1].spines[['top','right']].set_visible(False)
axes2[1].grid(axis='y', alpha=0.3)
for i, v in enumerate(weekday_avg.values):
    axes2[1].text(i, v + 2, str(round(v)), ha='center', fontsize=9, fontweight='bold')

plt.tight_layout(pad=2.0)
st.pyplot(fig2)
plt.close(fig2)
st.info('💡 **Insight:** Dua puncak jelas di jam **08.00** dan **17.00–18.00** mencerminkan pola komuter harian. Kamis & Jumat adalah hari tersibuk, sementara Minggu paling sepi.')
st.markdown('---')

# ══════════════════════════════
# ANALISIS LANJUTAN
# ══════════════════════════════
st.markdown('<p class="section-label">Analisis Lanjutan</p>', unsafe_allow_html=True)
st.subheader('📈 Tren Penyewaan, Segmentasi Pengguna & Faktor Lingkungan')

fig3 = plt.figure(figsize=(16, 12))
fig3.patch.set_facecolor('#1a2035')
gs = gridspec.GridSpec(2, 2, figure=fig3, hspace=0.4, wspace=0.35)
ax1 = fig3.add_subplot(gs[0,0])
ax2 = fig3.add_subplot(gs[0,1])
ax3 = fig3.add_subplot(gs[1,0])
ax4 = fig3.add_subplot(gs[1,1])

for ax in [ax1, ax3, ax4]:
    ax.set_facecolor('#1a2035')
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y', alpha=0.3)
ax2.set_facecolor('#1a2035')

monthly_trend = day_df.groupby(['yr','mnth'])['cnt'].sum().reset_index()
pivot_trend = monthly_trend.pivot(index='mnth', columns='yr', values='cnt')
ax1.plot(pivot_trend.index, pivot_trend[2011], marker='o', markersize=5,
         label='2011', color='#42A5F5', linewidth=2)
ax1.plot(pivot_trend.index, pivot_trend[2012], marker='o', markersize=5,
         label='2012', color='#EF5350', linewidth=2)
ax1.fill_between(pivot_trend.index, pivot_trend[2011], pivot_trend[2012],
                 alpha=0.1, color='#e8eaf0')
ax1.set_title('Tren Penyewaan Bulanan: 2011 vs 2012', fontsize=12, fontweight='bold', pad=12)
ax1.set_xlabel('Bulan', fontsize=9)
ax1.set_ylabel('Total Penyewaan', fontsize=9)
ax1.set_xticks(range(1,13))
ax1.set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'], fontsize=8)
ax1.legend(framealpha=0.2, labelcolor='#e8eaf0', fontsize=9)

casual_total = day_df['casual'].sum()
registered_total = day_df['registered'].sum()
wedges, texts, autotexts = ax2.pie(
    [casual_total, registered_total],
    labels=['Casual','Registered'],
    autopct='%1.1f%%',
    colors=['#FFC107','#4CAF50'],
    startangle=90, explode=(0.05, 0),
    textprops={'color':'#e8eaf0','fontsize':10}
)
for at in autotexts:
    at.set_color('#1a2035')
    at.set_fontweight('bold')
ax2.set_title('Proporsi Pengguna: Casual vs Registered', fontsize=12, fontweight='bold', pad=12)

workday_avg = day_df.groupby('workingday')['cnt'].mean()
workday_avg.index = workday_avg.index.map({0:'Libur/Weekend', 1:'Hari Kerja'})
ax3.bar(workday_avg.index, workday_avg.values,
        color=['#ab47bc','#26a69a'], width=0.4, edgecolor='none')
ax3.set_title('Rata-rata Penyewaan: Hari Kerja vs Libur', fontsize=12, fontweight='bold', pad=12)
ax3.set_xlabel('Tipe Hari', fontsize=9)
ax3.set_ylabel('Rata-rata Penyewaan', fontsize=9)
for i, v in enumerate(workday_avg.values):
    ax3.text(i, v + 30, str(round(v)), ha='center', fontsize=11, fontweight='bold')

ax4.scatter(day_df['temp']*41, day_df['cnt'], alpha=0.35, color='#ff7043', s=15)
z = np.polyfit(day_df['temp']*41, day_df['cnt'], 1)
p = np.poly1d(z)
x_line = np.linspace((day_df['temp']*41).min(), (day_df['temp']*41).max(), 100)
ax4.plot(x_line, p(x_line), color='#64b5f6', linewidth=2.5, label='Trendline')
ax4.set_title('Korelasi Suhu vs Jumlah Penyewaan', fontsize=12, fontweight='bold', pad=12)
ax4.set_xlabel('Suhu (°C)', fontsize=9)
ax4.set_ylabel('Jumlah Penyewaan', fontsize=9)
ax4.legend(framealpha=0.2, labelcolor='#e8eaf0', fontsize=9)

st.pyplot(fig3)
plt.close(fig3)
st.info('💡 **Insight:** Penyewaan tumbuh ~65% dari 2011 ke 2012. Pengguna Registered mendominasi 81.2%. Suhu berkorelasi positif dengan penyewaan — semakin hangat, semakin banyak yang bersepeda.')

st.markdown('---')
st.caption('© 2024 Arel Lafito Dinoris · areldinoris23@gmail.com · Bike Sharing Dataset — Capital Bikeshare, Washington D.C.')
