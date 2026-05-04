import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set style matplotlib agar background putih
plt.style.use('default')

# Konfigurasi halaman
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
day_df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'main_data.csv'))
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

# Load hour data
hour_df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'hour.csv'))
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Mapping season dan weather seperti di notebook
hour_df['season'] = hour_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})
day_df['season'] = day_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})

hour_df['weathersit'] = hour_df['weathersit'].map({
    1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'
})
day_df['weathersit'] = day_df['weathersit'].map({
    1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'
})

hour_df['yr'] = hour_df['yr'].map({0: 2011, 1: 2012})
day_df['yr'] = day_df['yr'].map({0: 2011, 1: 2012})

# ── SIDEBAR: FILTER GLOBAL ──
st.sidebar.header('🔍 Filter Global')

# Filter tahun
year_options = ['Semua'] + sorted(day_df['yr'].unique().tolist())
selected_year = st.sidebar.selectbox('Pilih Tahun:', year_options, index=0)

# Filter musim
season_options = ['Semua'] + sorted(day_df['season'].unique().tolist())
selected_season = st.sidebar.multiselect(
    'Pilih Musim:',
    season_options,
    default=['Semua']
)

# Filter cuaca
weather_options = ['Semua'] + sorted(day_df['weathersit'].unique().tolist())
selected_weather = st.sidebar.multiselect(
    'Pilih Kondisi Cuaca:',
    weather_options,
    default=['Semua']
)

# Filter range bulan
st.sidebar.markdown('---')
st.sidebar.subheader('📅 Filter Bulan')
month_range = st.sidebar.slider(
    'Pilih Range Bulan (1-12):',
    min_value=1,
    max_value=12,
    value=(1, 12)
)

# Apply filters
def apply_filters(df, year, season, weather, month_range):
    df_filtered = df.copy()
    
    if year != 'Semua':
        df_filtered = df_filtered[df_filtered['yr'] == year]
    
    if 'Semua' not in season and len(season) > 0:
        df_filtered = df_filtered[df_filtered['season'].isin(season)]
    
    if 'Semua' not in weather and len(weather) > 0:
        df_filtered = df_filtered[df_filtered['weathersit'].isin(weather)]
    
    df_filtered = df_filtered[
        (df_filtered['mnth'] >= month_range[0]) & 
        (df_filtered['mnth'] <= month_range[1])
    ]
    
    return df_filtered

day_df_filtered = apply_filters(day_df, selected_year, selected_season, selected_weather, month_range)
hour_df_filtered = apply_filters(hour_df, selected_year, selected_season, selected_weather, month_range)

# ── HEADER ──
st.title('🚴 Bike Sharing Dashboard')
st.markdown('**Nama:** Arel Lafito Dinoris | **Email:** areldinoris23@gmail.com | **ID:** areldinoris')
st.markdown('---')

# ── METRIK RINGKASAN ──
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric('Total Penyewaan (Filtered)', f"{day_df_filtered['cnt'].sum():,}")
col_m2.metric('Penyewaan Tertinggi', f"{day_df_filtered['cnt'].max():,}") 
col_m3.metric('Rata-rata/Hari', f"{day_df_filtered['cnt'].mean():.0f}")
col_m4.metric('Rata-rata/Jam', f"{hour_df_filtered['cnt'].mean():.0f}" if len(hour_df_filtered) > 0 else "0")

st.markdown('---')

# ── TAB INTERAKTIF ──
tab1, tab2, tab3, tab4 = st.tabs([
    '📊 Pertanyaan 1', 
    '⏰ Pertanyaan 2', 
    '📈 Analisis Lanjutan', 
    '📋 Data Eksplorer'
])

# ── TAB 1: PERTANYAAN 1 ──
with tab1:
    st.subheader('📊 Bagaimana pengaruh kondisi cuaca dan musim terhadap jumlah penyewaan sepeda harian?')
    
    # Opsi tampilan chart
    col_chart, col_info = st.columns([3, 1])
    
    with col_info:
        st.markdown('**🎨 Opsi Visualisasi:**')
        chart_type_1 = st.radio(
            'Pilih tipe chart:',
            ['Bar Chart', 'Line Chart', 'Box Plot'],
            key='chart_type_1'
        )
    
    if chart_type_1 == 'Bar Chart':
        # Plot musim - Matplotlib
        fig1, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        season_order = ['Spring', 'Summer', 'Fall', 'Winter']
        season_avg = day_df_filtered.groupby('season')['cnt'].mean().reindex(season_order)
        axes[0].bar(season_avg.index, season_avg.values,
                    color=['#4CAF50', '#FFC107', '#F44336', '#2196F3'])
        axes[0].set_title('Rata-rata Penyewaan per Musim', fontsize=13)
        axes[0].set_xlabel('Musim')
        axes[0].set_ylabel('Rata-rata Penyewaan')
        for i, v in enumerate(season_avg.values):
            if not np.isnan(v):
                axes[0].text(i, v + 50, str(round(v)), ha='center', fontsize=10)
        
        weather_avg = day_df_filtered.groupby('weathersit')['cnt'].mean().sort_values(ascending=False)
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
    
    elif chart_type_1 == 'Line Chart':
        # Plotly interactive charts
        season_avg = day_df_filtered.groupby('season')['cnt'].mean().reset_index()
        weather_avg = day_df_filtered.groupby('weathersit')['cnt'].mean().reset_index()
        
        fig1_plotly = make_subplots(rows=1, cols=2, subplot_titles=('Rata-rata per Musim', 'Rata-rata per Cuaca'))
        
        fig1_plotly.add_trace(
            go.Scatter(x=season_avg['season'], y=season_avg['cnt'], mode='lines+markers',
                      marker=dict(size=10, color=['#4CAF50', '#FFC107', '#F44336', '#2196F3'])),
            row=1, col=1
        )
        fig1_plotly.add_trace(
            go.Scatter(x=weather_avg['weathersit'], y=weather_avg['cnt'], mode='lines+markers',
                      marker=dict(size=10, color='#42A5F5')),
            row=1, col=2
        )
        
        fig1_plotly.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig1_plotly, use_container_width=True)
    
    else:  # Box Plot
        fig1_box = make_subplots(rows=1, cols=2, subplot_titles=('Distribusi per Musim', 'Distribusi per Cuaca'))
        
        for season in day_df_filtered['season'].unique():
            if pd.notna(season):
                data = day_df_filtered[day_df_filtered['season'] == season]['cnt']
                fig1_box.add_trace(
                    go.Box(y=data, name=season, marker_color=['#4CAF50', '#FFC107', '#F44336', '#2196F3'][
                        ['Spring', 'Summer', 'Fall', 'Winter'].index(season) if season in ['Spring', 'Summer', 'Fall', 'Winter'] else 0
                    ]),
                    row=1, col=1
                )
        
        for weather in day_df_filtered['weathersit'].unique():
            if pd.notna(weather):
                data = day_df_filtered[day_df_filtered['weathersit'] == weather]['cnt']
                fig1_box.add_trace(
                    go.Box(y=data, name=weather),
                    row=1, col=2
                )
        
        fig1_box.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig1_box, use_container_width=True)
    
    st.info('💡 Visualisasi musim dan cuaca mengkonfirmasi bahwa Fall + Clear weather adalah kombinasi terbaik untuk penyewaan sepeda. Cuaca Light Rain/Snow menyebabkan penurunan penyewaan hingga 63% dibanding cuaca Clear.')

# ── TAB 2: PERTANYAAN 2 ──
with tab2:
    st.subheader('⏰ Pada jam berapa dan hari apa penyewaan sepeda mencapai puncaknya dalam seminggu?')
    
    col_chart2, col_info2 = st.columns([3, 1])
    
    with col_info2:
        st.markdown('**🎨 Opsi Visualisasi:**')
        chart_type_2 = st.radio(
            'Pilih tipe chart:',
            ['Bar/Line Chart', 'Heatmap'],
            key='chart_type_2'
        )
        
        st.markdown('**📍 Highlight:**')
        highlight_peaks = st.checkbox('Tandai jam puncak', value=True)
    
    if chart_type_2 == 'Bar/Line Chart':
        fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
        
        hour_avg = hour_df_filtered.groupby('hr')['cnt'].mean()
        axes2[0].plot(hour_avg.index, hour_avg.values, marker='o', color='#E53935', linewidth=2)
        axes2[0].set_title('Rata-rata Penyewaan per Jam', fontsize=13)
        axes2[0].set_xlabel('Jam')
        axes2[0].set_ylabel('Rata-rata Penyewaan')
        axes2[0].set_xticks(range(0, 24))
        
        if highlight_peaks:
            axes2[0].axvline(x=8, color='gray', linestyle='--', alpha=0.5, label='Jam 08.00')
            axes2[0].axvline(x=17, color='blue', linestyle='--', alpha=0.5, label='Jam 17.00')
            axes2[0].legend()
        
        day_map = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
        weekday_avg = hour_df_filtered.groupby('weekday')['cnt'].mean().rename(index=day_map)
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
    
    else:  # Heatmap
        pivot_hour_day = hour_df_filtered.pivot_table(
            values='cnt', 
            index='weekday', 
            columns='hr', 
            aggfunc='mean'
        )
        
        day_labels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        if not pivot_hour_day.empty:
            pivot_hour_day.index = [day_labels[int(i)] if int(i) < len(day_labels) else str(i) for i in pivot_hour_day.index]
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=pivot_hour_day.values,
            x=pivot_hour_day.columns,
            y=pivot_hour_day.index,
            colorscale='YlOrRd',
            colorbar=dict(title='Avg Rentals')
        ))
        
        fig_heatmap.update_layout(
            title='Heatmap Penyewaan: Hari vs Jam',
            xaxis_title='Jam',
            yaxis_title='Hari',
            height=400
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.info('💡 Grafik per jam menunjukkan dua puncak jelas (bimodal) di jam 08.00 dan 17.00 yang konsisten dengan jam komuter kerja, sementara dini hari (01.00–04.00) adalah waktu terendah dengan rata-rata di bawah 25 penyewaan per jam.')

# ── TAB 3: ANALISIS LANJUTAN ──
with tab3:
    st.subheader('📈 Analisis Lanjutan')
    
    # Ringkasan Statistik
    if not day_df_filtered.empty:
        growth = day_df_filtered.groupby('yr')['cnt'].sum()
        years_available = growth.index.tolist()
        
        if len(years_available) > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                for year in years_available:
                    st.metric(f'Total {year}', f"{growth[year]:,}")
                if len(years_available) == 2:
                    pct = ((growth[2012] - growth[2011]) / growth[2011]) * 100 if 2011 in years_available and 2012 in years_available else 0
                    st.metric('Pertumbuhan', f"{pct:.1f}%")
            
            casual_total = day_df_filtered['casual'].sum()
            registered_total = day_df_filtered['registered'].sum()
            
            with col2:
                st.metric('Casual', f"{casual_total:,}")
                st.metric('Registered', f"{registered_total:,}")
            
            with col3:
                total = casual_total + registered_total
                if total > 0:
                    st.metric('Proporsi Casual', f"{(casual_total/total)*100:.1f}%")
                    st.metric('Proporsi Registered', f"{(registered_total/total)*100:.1f}%")
    
    st.markdown('---')
    
    # Sub-tab untuk analisis lanjutan
    sub_tab1, sub_tab2 = st.tabs(['📊 Tren & Proporsi', '🔍 Korelasi & Perbandingan'])
    
    with sub_tab1:
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown('**Tren Bulanan**')
            if not day_df_filtered.empty:
                monthly_trend = day_df_filtered.groupby(['yr', 'mnth'])['cnt'].sum().reset_index()
                
                fig_trend = px.line(
                    monthly_trend, 
                    x='mnth', 
                    y='cnt', 
                    color='yr',
                    markers=True,
                    labels={'mnth': 'Bulan', 'cnt': 'Total Penyewaan', 'yr': 'Tahun'}
                )
                fig_trend.update_layout(height=400)
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.warning('Tidak ada data dengan filter terpilih.')
        
        with col_right:
            st.markdown('**Proporsi Pengguna**')
            if not day_df_filtered.empty:
                casual_total = day_df_filtered['casual'].sum()
                registered_total = day_df_filtered['registered'].sum()
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Casual', 'Registered'],
                    values=[casual_total, registered_total],
                    hole=0.3,
                    marker_colors=['#FFC107', '#4CAF50']
                )])
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.warning('Tidak ada data dengan filter terpilih.')
    
    with sub_tab2:
        col_left2, col_right2 = st.columns(2)
        
        with col_left2:
            st.markdown('**Hari Kerja vs Libur**')
            if not day_df_filtered.empty:
                workday_avg = day_df_filtered.groupby('workingday')['cnt'].mean()
                workday_labels = {0: 'Libur/Weekend', 1: 'Hari Kerja'}
                
                fig_workday = go.Figure(data=[
                    go.Bar(
                        x=[workday_labels.get(k, str(k)) for k in workday_avg.index],
                        y=workday_avg.values,
                        marker_color=['#AB47BC', '#26A69A']
                    )
                ])
                fig_workday.update_layout(
                    height=400,
                    xaxis_title='Tipe Hari',
                    yaxis_title='Rata-rata Penyewaan'
                )
                st.plotly_chart(fig_workday, use_container_width=True)
            else:
                st.warning('Tidak ada data dengan filter terpilih.')
        
        with col_right2:
            st.markdown('**Korelasi Suhu vs Penyewaan**')
            if not day_df_filtered.empty:
                fig_scatter = px.scatter(
                    day_df_filtered,
                    x=day_df_filtered['temp'] * 41,
                    y='cnt',
                    trendline='ols',
                    labels={'x': 'Suhu (°C)', 'cnt': 'Jumlah Penyewaan'},
                    opacity=0.6
                )
                fig_scatter.update_layout(height=400)
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.warning('Tidak ada data dengan filter terpilih.')
    
    # Tambahan: Download button
    st.markdown('---')
    st.markdown('**📥 Download Data Filtered**')
    
    if st.button('Siapkan Data untuk Download'):
        csv = day_df_filtered.to_csv(index=False)
        st.download_button(
            label='Download CSV',
            data=csv,
            file_name='bike_sharing_filtered.csv',
            mime='text/csv'
        )

# ── TAB 4: DATA EKSPLORER ──
with tab4:
    st.subheader('📋 Eksplorasi Data')
    
    # Data viewer dengan filter kolom
    st.markdown('**🔍 Preview Data Harian (Filtered)**')
    
    # Pilih kolom yang ingin ditampilkan
    all_columns = day_df_filtered.columns.tolist()
    default_columns = ['dteday', 'season', 'weathersit', 'temp', 'cnt', 'casual', 'registered']
    selected_columns = st.multiselect(
        'Pilih kolom yang ingin ditampilkan:',
        all_columns,
        default=[col for col in default_columns if col in all_columns]
    )
    
    if selected_columns:
        st.dataframe(
            day_df_filtered[selected_columns].head(20),
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown('---')
    
    # Statistik deskriptif
    col_stat1, col_stat2 = st.columns(2)
    
    with col_stat1:
        st.markdown('**📊 Statistik Deskriptif (Numerikal)**')
        numerical_cols = day_df_filtered.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) > 0:
            st.dataframe(
                day_df_filtered[numerical_cols].describe(),
                use_container_width=True
            )
    
    with col_stat2:
        st.markdown('**📊 Distribusi Kategorikal**')
        
        selected_cat = st.selectbox(
            'Pilih kolom kategorikal:',
            ['season', 'weathersit', 'yr', 'mnth', 'holiday', 'weekday', 'workingday']
        )
        
        if selected_cat in day_df_filtered.columns:
            dist = day_df_filtered[selected_cat].value_counts().reset_index()
            dist.columns = [selected_cat, 'count']
            
            fig_dist = px.bar(
                dist, 
                x=selected_cat, 
                y='count',
                text='count'
            )
            fig_dist.update_layout(height=300)
            st.plotly_chart(fig_dist, use_container_width=True)
    
    st.markdown('---')
    
    # Info data
    st.markdown('**ℹ️ Informasi Dataset**')
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.metric('Jumlah Hari (Filtered)', len(day_df_filtered))
        st.metric('Total Hari (Keseluruhan)', len(day_df))
    
    with col_info2:
        st.metric('Jumlah Jam (Filtered)', len(hour_df_filtered))
        st.metric('Total Jam (Keseluruhan)', len(hour_df))
    
    with col_info3:
        missing_data = day_df_filtered.isnull().sum().sum()
        st.metric('Missing Values', missing_data)
        st.metric('Range Tanggal', f"{day_df_filtered['dteday'].min().strftime('%d %b %Y')} - {day_df_filtered['dteday'].max().strftime('%d %b %Y')}" if not day_df_filtered.empty else "N/A")

st.markdown('---')

# ── KESIMPULAN ──
st.subheader('✅ Kesimpulan')

col_kesimpulan1, col_kesimpulan2 = st.columns(2)

with col_kesimpulan1:
    st.markdown('**Pertanyaan 1**')
    st.markdown("""
    - **Musim Fall** dan **cuaca Clear** secara konsisten menghasilkan jumlah penyewaan tertinggi sepanjang 2011–2012.
    - Kondisi cuaca buruk (**Light Rain/Snow**) terbukti menurunkan penyewaan secara drastis hingga **63%** dibanding cuaca Clear.
    
    **Rekomendasi bisnis:**
    - Tingkatkan ketersediaan armada sepeda di **musim Fall** dengan cuaca cerah.
    - Kurangi operasional saat **cuaca buruk** untuk efisiensi biaya.
    """)

with col_kesimpulan2:
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
