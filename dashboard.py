import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import os

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

# Filter hari dalam seminggu
st.sidebar.markdown('---')
st.sidebar.subheader('📅 Filter Hari')
day_options = ['Semua', 'Weekday (Sen-Jum)', 'Weekend (Sab-Min)']
selected_day_type = st.sidebar.radio('Pilih Tipe Hari:', day_options, index=0)

# Apply filters
def apply_filters(df, year, season, weather, month_range, day_type):
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
    
    # Filter tipe hari (hanya untuk hour_df yang memiliki kolom weekday)
    if 'weekday' in df_filtered.columns and day_type != 'Semua':
        if day_type == 'Weekday (Sen-Jum)':
            df_filtered = df_filtered[df_filtered['weekday'].isin([0, 1, 2, 3, 4])]  # 0=Sen, 4=Jum
        elif day_type == 'Weekend (Sab-Min)':
            df_filtered = df_filtered[df_filtered['weekday'].isin([5, 6])]  # 5=Sab, 6=Min
    
    return df_filtered

day_df_filtered = apply_filters(day_df, selected_year, selected_season, selected_weather, month_range, 'Semua')
hour_df_filtered = apply_filters(hour_df, selected_year, selected_season, selected_weather, month_range, selected_day_type)

# ── HEADER ──
st.title('🚴 Bike Sharing Dashboard')
st.markdown('**Nama:** Arel Lafito Dinoris | **Email:** areldinoris23@gmail.com | **ID:** areldinoris')
st.markdown('---')

# ── METRIK RINGKASAN ──
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric('Total Penyewaan (Filtered)', f"{day_df_filtered['cnt'].sum():,}")
col_m2.metric('Penyewaan Tertinggi', f"{day_df_filtered['cnt'].max():,}" if not day_df_filtered.empty else "0") 
col_m3.metric('Rata-rata/Hari', f"{day_df_filtered['cnt'].mean():.0f}" if not day_df_filtered.empty else "0")
col_m4.metric('Rata-rata/Jam', f"{hour_df_filtered['cnt'].mean():.0f}" if not hour_df_filtered.empty else "0")

st.markdown('---')

# ── TAB INTERAKTIF ──
tab1, tab2, tab3, tab4 = st.tabs([
    '📊 Musim & Cuaca', 
    '⏰ Jam & Hari', 
    '📈 Analisis Lanjutan', 
    '📋 Eksplorasi Data'
])

# ── TAB 1: PERTANYAAN 1 ──
with tab1:
    st.subheader('📊 Bagaimana pengaruh kondisi cuaca dan musim terhadap jumlah penyewaan sepeda harian?')
    
    if day_df_filtered.empty:
        st.warning('⚠️ Tidak ada data yang sesuai dengan filter terpilih. Silakan ubah filter.')
    else:
        # Opsi tampilan chart
        col_chart, col_info = st.columns([3, 1])
        
        with col_info:
            st.markdown('**🎨 Opsi Visualisasi:**')
            chart_type_1 = st.radio(
                'Pilih tipe chart:',
                ['Bar Chart', 'Horizontal Bar', 'Pie Chart'],
                key='chart_type_1'
            )
            
            st.markdown('---')
            st.markdown('**📊 Statistik Cepat:**')
            best_season = day_df_filtered.groupby('season')['cnt'].mean().idxmax()
            best_weather = day_df_filtered.groupby('weathersit')['cnt'].mean().idxmax()
            st.metric('Musim Terbaik', best_season)
            st.metric('Cuaca Terbaik', best_weather)
        
        if chart_type_1 == 'Bar Chart':
            fig1, axes = plt.subplots(1, 2, figsize=(14, 5))
            
            # Plot musim
            season_order = ['Spring', 'Summer', 'Fall', 'Winter']
            season_avg = day_df_filtered.groupby('season')['cnt'].mean().reindex(season_order)
            colors_season = ['#4CAF50', '#FFC107', '#F44336', '#2196F3']
            axes[0].bar(season_avg.index, season_avg.values, color=colors_season, edgecolor='black', linewidth=0.5)
            axes[0].set_title('Rata-rata Penyewaan per Musim', fontsize=14, fontweight='bold')
            axes[0].set_xlabel('Musim')
            axes[0].set_ylabel('Rata-rata Penyewaan')
            axes[0].grid(axis='y', alpha=0.3)
            for i, v in enumerate(season_avg.values):
                if not np.isnan(v):
                    axes[0].text(i, v + 50, f'{v:,.0f}', ha='center', fontsize=10, fontweight='bold')
            
            # Plot cuaca
            weather_avg = day_df_filtered.groupby('weathersit')['cnt'].mean().sort_values(ascending=True)
            colors_weather = plt.cm.Blues(np.linspace(0.4, 0.9, len(weather_avg)))
            axes[1].barh(weather_avg.index, weather_avg.values, color=colors_weather, edgecolor='black', linewidth=0.5)
            axes[1].set_title('Rata-rata Penyewaan per Kondisi Cuaca', fontsize=14, fontweight='bold')
            axes[1].set_xlabel('Rata-rata Penyewaan')
            axes[1].grid(axis='x', alpha=0.3)
            for i, v in enumerate(weather_avg.values):
                if not np.isnan(v):
                    axes[1].text(v + 30, i, f'{v:,.0f}', va='center', fontsize=10, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig1)
            plt.close(fig1)
        
        elif chart_type_1 == 'Horizontal Bar':
            fig1, axes = plt.subplots(2, 1, figsize=(10, 8))
            
            # Plot musim horizontal
            season_order = ['Spring', 'Summer', 'Fall', 'Winter']
            season_avg = day_df_filtered.groupby('season')['cnt'].mean().reindex(season_order)
            colors_season = ['#4CAF50', '#FFC107', '#F44336', '#2196F3']
            axes[0].barh(season_avg.index, season_avg.values, color=colors_season, edgecolor='black', linewidth=0.5)
            axes[0].set_title('Rata-rata Penyewaan per Musim', fontsize=14, fontweight='bold')
            axes[0].set_xlabel('Rata-rata Penyewaan')
            axes[0].grid(axis='x', alpha=0.3)
            for i, v in enumerate(season_avg.values):
                if not np.isnan(v):
                    axes[0].text(v + 50, i, f'{v:,.0f}', va='center', fontsize=10, fontweight='bold')
            
            # Plot cuaca horizontal
            weather_avg = day_df_filtered.groupby('weathersit')['cnt'].mean().sort_values(ascending=True)
            colors_weather = plt.cm.Oranges(np.linspace(0.4, 0.9, len(weather_avg)))
            axes[1].barh(weather_avg.index, weather_avg.values, color=colors_weather, edgecolor='black', linewidth=0.5)
            axes[1].set_title('Rata-rata Penyewaan per Kondisi Cuaca', fontsize=14, fontweight='bold')
            axes[1].set_xlabel('Rata-rata Penyewaan')
            axes[1].grid(axis='x', alpha=0.3)
            for i, v in enumerate(weather_avg.values):
                if not np.isnan(v):
                    axes[1].text(v + 30, i, f'{v:,.0f}', va='center', fontsize=10, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig1)
            plt.close(fig1)
        
        else:  # Pie Chart
            fig1, axes = plt.subplots(1, 2, figsize=(14, 6))
            
            # Pie musim
            season_sum = day_df_filtered.groupby('season')['cnt'].sum()
            colors_season = ['#4CAF50', '#FFC107', '#F44336', '#2196F3']
            wedges1, texts1, autotexts1 = axes[0].pie(
                season_sum.values, 
                labels=season_sum.index, 
                autopct='%1.1f%%',
                colors=colors_season,
                startangle=90,
                explode=[0.05]*len(season_sum)
            )
            axes[0].set_title('Proporsi Penyewaan per Musim', fontsize=14, fontweight='bold')
            
            # Pie cuaca
            weather_sum = day_df_filtered.groupby('weathersit')['cnt'].sum()
            colors_weather = plt.cm.Set3(np.linspace(0, 1, len(weather_sum)))
            wedges2, texts2, autotexts2 = axes[1].pie(
                weather_sum.values,
                labels=weather_sum.index,
                autopct='%1.1f%%',
                colors=colors_weather,
                startangle=90,
                explode=[0.02]*len(weather_sum)
            )
            axes[1].set_title('Proporsi Penyewaan per Cuaca', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig1)
            plt.close(fig1)
    
    st.info('💡 Visualisasi musim dan cuaca mengkonfirmasi bahwa Fall + Clear weather adalah kombinasi terbaik untuk penyewaan sepeda. Cuaca Light Rain/Snow menyebabkan penurunan penyewaan hingga 63% dibanding cuaca Clear.')

# ── TAB 2: PERTANYAAN 2 ──
with tab2:
    st.subheader('⏰ Pada jam berapa dan hari apa penyewaan sepeda mencapai puncaknya dalam seminggu?')
    
    if hour_df_filtered.empty:
        st.warning('⚠️ Tidak ada data yang sesuai dengan filter terpilih. Silakan ubah filter.')
    else:
        col_chart2, col_info2 = st.columns([3, 1])
        
        with col_info2:
            st.markdown('**🎨 Opsi Visualisasi:**')
            chart_type_2 = st.radio(
                'Pilih tipe chart:',
                ['Line & Bar Chart', 'Area Chart', 'Tabel Pivot'],
                key='chart_type_2'
            )
            
            st.markdown('---')
            st.markdown('**📍 Highlight Puncak:**')
            show_peaks = st.checkbox('Tandai jam puncak', value=True)
            
            st.markdown('---')
            st.markdown('**📊 Statistik Cepat:**')
            peak_hour = hour_df_filtered.groupby('hr')['cnt'].mean().idxmax()
            peak_day = hour_df_filtered.groupby('weekday')['cnt'].mean().idxmax()
            day_map = {0:'Minggu', 1:'Senin', 2:'Selasa', 3:'Rabu', 4:'Kamis', 5:'Jumat', 6:'Sabtu'}
            st.metric('Jam Tersibuk', f'{peak_hour:.0f}:00')
            st.metric('Hari Tersibuk', day_map.get(int(peak_day), str(peak_day)))
        
        if chart_type_2 == 'Line & Bar Chart':
            fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
            
            # Plot per jam
            hour_avg = hour_df_filtered.groupby('hr')['cnt'].mean()
            axes2[0].plot(hour_avg.index, hour_avg.values, marker='o', color='#E53935', linewidth=2, markersize=4)
            axes2[0].fill_between(hour_avg.index, hour_avg.values, alpha=0.2, color='#E53935')
            axes2[0].set_title('Rata-rata Penyewaan per Jam', fontsize=14, fontweight='bold')
            axes2[0].set_xlabel('Jam')
            axes2[0].set_ylabel('Rata-rata Penyewaan')
            axes2[0].set_xticks(range(0, 24))
            axes2[0].grid(alpha=0.3)
            
            if show_peaks:
                axes2[0].axvline(x=8, color='gray', linestyle='--', alpha=0.7, linewidth=1.5, label='Jam 08.00')
                axes2[0].axvline(x=17, color='blue', linestyle='--', alpha=0.7, linewidth=1.5, label='Jam 17.00')
                axes2[0].legend(loc='upper left')
            
            # Plot per hari
            day_map = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
            weekday_avg = hour_df_filtered.groupby('weekday')['cnt'].mean().rename(index=day_map)
            day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            weekday_avg = weekday_avg.reindex([d for d in day_order if d in weekday_avg.index])
            
            colors_days = ['#2196F3' if d not in ['Sat', 'Sun'] else '#FF9800' for d in weekday_avg.index]
            axes2[1].bar(weekday_avg.index, weekday_avg.values, color=colors_days, edgecolor='black', linewidth=0.5)
            axes2[1].set_title('Rata-rata Penyewaan per Hari', fontsize=14, fontweight='bold')
            axes2[1].set_xlabel('Hari')
            axes2[1].set_ylabel('Rata-rata Penyewaan')
            axes2[1].grid(axis='y', alpha=0.3)
            for i, v in enumerate(weekday_avg.values):
                if not np.isnan(v):
                    axes2[1].text(i, v + 5, f'{v:,.0f}', ha='center', fontsize=9, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)
        
        elif chart_type_2 == 'Area Chart':
            fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
            
            # Area chart per jam
            hour_avg = hour_df_filtered.groupby('hr')['cnt'].mean()
            axes2[0].fill_between(hour_avg.index, hour_avg.values, alpha=0.5, color='#E53935')
            axes2[0].plot(hour_avg.index, hour_avg.values, color='#C62828', linewidth=2)
            axes2[0].set_title('Pola Penyewaan per Jam (Area Chart)', fontsize=14, fontweight='bold')
            axes2[0].set_xlabel('Jam')
            axes2[0].set_ylabel('Rata-rata Penyewaan')
            axes2[0].set_xticks(range(0, 24, 2))
            axes2[0].grid(alpha=0.3)
            
            # Area chart per hari
            day_map = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
            weekday_avg = hour_df_filtered.groupby('weekday')['cnt'].mean().rename(index=day_map)
            day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            weekday_avg = weekday_avg.reindex([d for d in day_order if d in weekday_avg.index])
            
            axes2[1].fill_between(range(len(weekday_avg)), weekday_avg.values, alpha=0.5, color='#AB47BC')
            axes2[1].plot(range(len(weekday_avg)), weekday_avg.values, color='#6A1B9A', linewidth=2, marker='o')
            axes2[1].set_title('Pola Penyewaan per Hari (Area Chart)', fontsize=14, fontweight='bold')
            axes2[1].set_xlabel('Hari')
            axes2[1].set_ylabel('Rata-rata Penyewaan')
            axes2[1].set_xticks(range(len(weekday_avg)))
            axes2[1].set_xticklabels(weekday_avg.index)
            axes2[1].grid(alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)
        
        else:  # Tabel Pivot
            st.markdown('**📊 Tabel Pivot: Rata-rata Penyewaan per Jam & Hari**')
            pivot_table = hour_df_filtered.pivot_table(
                values='cnt',
                index='weekday',
                columns='hr',
                aggfunc='mean'
            ).round(0)
            
            day_map = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
            pivot_table.index = [day_map.get(int(i), str(i)) for i in pivot_table.index]
            
            # Highlight max values
            st.dataframe(
                pivot_table.style.background_gradient(cmap='YlOrRd', axis=None),
                use_container_width=True
            )
            
            st.markdown('**Warna merah = penyewaan tinggi, kuning = penyewaan rendah**')
    
    st.info('💡 Grafik per jam menunjukkan dua puncak jelas (bimodal) di jam 08.00 dan 17.00 yang konsisten dengan jam komuter kerja, sementara dini hari (01.00–04.00) adalah waktu terendah dengan rata-rata di bawah 25 penyewaan per jam.')

# ── TAB 3: ANALISIS LANJUTAN ──
with tab3:
    st.subheader('📈 Analisis Lanjutan')
    
    if day_df_filtered.empty:
        st.warning('⚠️ Tidak ada data yang sesuai dengan filter terpilih. Silakan ubah filter.')
    else:
        # Ringkasan Statistik
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
                st.markdown('**📈 Tren Bulanan**')
                monthly_trend = day_df_filtered.groupby(['yr', 'mnth'])['cnt'].sum().reset_index()
                
                fig_trend, ax_trend = plt.subplots(figsize=(8, 5))
                
                for year in monthly_trend['yr'].unique():
                    year_data = monthly_trend[monthly_trend['yr'] == year]
                    ax_trend.plot(year_data['mnth'], year_data['cnt'], 
                                 marker='o', linewidth=2, label=f'Tahun {year}', markersize=6)
                
                ax_trend.set_title('Tren Penyewaan Bulanan', fontsize=14, fontweight='bold')
                ax_trend.set_xlabel('Bulan')
                ax_trend.set_ylabel('Total Penyewaan')
                ax_trend.set_xticks(range(1, 13))
                ax_trend.set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun',
                                         'Jul','Agu','Sep','Okt','Nov','Des'])
                ax_trend.legend()
                ax_trend.grid(alpha=0.3)
                plt.tight_layout()
                st.pyplot(fig_trend)
                plt.close(fig_trend)
            
            with col_right:
                st.markdown('**🥧 Proporsi Pengguna**')
                casual_total = day_df_filtered['casual'].sum()
                registered_total = day_df_filtered['registered'].sum()
                
                fig_pie, ax_pie = plt.subplots(figsize=(8, 5))
                ax_pie.pie(
                    [casual_total, registered_total],
                    labels=['Casual', 'Registered'],
                    autopct='%1.1f%%',
                    colors=['#FFC107', '#4CAF50'],
                    startangle=90,
                    explode=(0.05, 0)
                )
                ax_pie.set_title('Proporsi Pengguna: Casual vs Registered', fontsize=14, fontweight='bold')
                plt.tight_layout()
                st.pyplot(fig_pie)
                plt.close(fig_pie)
        
        with sub_tab2:
            col_left2, col_right2 = st.columns(2)
            
            with col_left2:
                st.markdown('**💼 Hari Kerja vs Libur**')
                workday_avg = day_df_filtered.groupby('workingday')['cnt'].mean()
                workday_labels = ['Libur/Weekend', 'Hari Kerja']
                
                fig_workday, ax_workday = plt.subplots(figsize=(8, 5))
                colors_workday = ['#AB47BC', '#26A69A']
                bars = ax_workday.bar(workday_labels, workday_avg.values, color=colors_workday, 
                                     edgecolor='black', linewidth=0.5, width=0.4)
                ax_workday.set_title('Rata-rata Penyewaan: Hari Kerja vs Libur', fontsize=14, fontweight='bold')
                ax_workday.set_xlabel('Tipe Hari')
                ax_workday.set_ylabel('Rata-rata Penyewaan')
                ax_workday.grid(axis='y', alpha=0.3)
                
                for i, (bar, v) in enumerate(zip(bars, workday_avg.values)):
                    if not np.isnan(v):
                        ax_workday.text(bar.get_x() + bar.get_width()/2., v + 30, 
                                      f'{v:,.0f}', ha='center', fontsize=11, fontweight='bold')
                
                plt.tight_layout()
                st.pyplot(fig_workday)
                plt.close(fig_workday)
            
            with col_right2:
                st.markdown('**🌡️ Korelasi Suhu vs Penyewaan**')
                
                fig_scatter, ax_scatter = plt.subplots(figsize=(8, 5))
                
                # Scatter plot
                ax_scatter.scatter(
                    day_df_filtered['temp'] * 41,
                    day_df_filtered['cnt'],
                    alpha=0.4,
                    color='#FF7043',
                    s=20,
                    edgecolors='black',
                    linewidth=0.3
                )
                
                # Trendline
                z = np.polyfit(day_df_filtered['temp'] * 41, day_df_filtered['cnt'], 1)
                p = np.poly1d(z)
                x_line = np.linspace((day_df_filtered['temp'] * 41).min(), 
                                    (day_df_filtered['temp'] * 41).max(), 100)
                ax_scatter.plot(x_line, p(x_line), color='#1565C0', linewidth=2, 
                              label=f'Trendline (y={z[0]:.1f}x + {z[1]:.0f})')
                
                ax_scatter.set_title('Korelasi Suhu vs Jumlah Penyewaan', fontsize=14, fontweight='bold')
                ax_scatter.set_xlabel('Suhu (°C)')
                ax_scatter.set_ylabel('Jumlah Penyewaan')
                ax_scatter.legend()
                ax_scatter.grid(alpha=0.3)
                
                plt.tight_layout()
                st.pyplot(fig_scatter)
                plt.close(fig_scatter)
        
        # Tambahan: Download button
        st.markdown('---')
        st.markdown('**📥 Download Data Terfilter**')
        
        col_download1, col_download2 = st.columns(2)
        with col_download1:
            csv_day = day_df_filtered.to_csv(index=False)
            st.download_button(
                label='📥 Download Data Harian (CSV)',
                data=csv_day,
                file_name='bike_sharing_daily_filtered.csv',
                mime='text/csv',
                use_container_width=True
            )
        
        with col_download2:
            csv_hour = hour_df_filtered.to_csv(index=False)
            st.download_button(
                label='📥 Download Data Per Jam (CSV)',
                data=csv_hour,
                file_name='bike_sharing_hourly_filtered.csv',
                mime='text/csv',
                use_container_width=True
            )

# ── TAB 4: EKSPLORASI DATA ──
with tab4:
    st.subheader('📋 Eksplorasi Data')
    
    # Pilihan dataset
    dataset_choice = st.radio(
        'Pilih Dataset:',
        ['Data Harian (day.csv)', 'Data Per Jam (hour.csv)'],
        horizontal=True
    )
    
    df_to_explore = day_df_filtered if 'Harian' in dataset_choice else hour_df_filtered
    
    if df_to_explore.empty:
        st.warning('⚠️ Tidak ada data yang sesuai dengan filter terpilih. Silakan ubah filter.')
    else:
        # Data viewer dengan filter kolom
        st.markdown('**🔍 Preview Data (Filtered)**')
        
        # Pilih kolom yang ingin ditampilkan
        all_columns = df_to_explore.columns.tolist()
        default_columns = ['dteday', 'season', 'weathersit', 'temp', 'cnt', 'casual', 'registered']
        if 'hr' in all_columns:
            default_columns.insert(1, 'hr')
        
        selected_columns = st.multiselect(
            'Pilih kolom yang ingin ditampilkan:',
            all_columns,
            default=[col for col in default_columns if col in all_columns]
        )
        
        # Slider untuk jumlah baris
        n_rows = st.slider('Jumlah baris ditampilkan:', 5, 100, 20)
        
        if selected_columns:
            st.dataframe(
                df_to_explore[selected_columns].head(n_rows),
                use_container_width=True,
                hide_index=True
            )
        
        st.markdown('---')
        
        # Statistik deskriptif
        col_stat1, col_stat2 = st.columns(2)
        
        with col_stat1:
            st.markdown('**📊 Statistik Deskriptif (Numerikal)**')
            numerical_cols = df_to_explore.select_dtypes(include=[np.number]).columns
            if len(numerical_cols) > 0:
                st.dataframe(
                    df_to_explore[numerical_cols].describe(),
                    use_container_width=True
                )
            else:
                st.info('Tidak ada kolom numerikal.')
        
        with col_stat2:
            st.markdown('**📊 Distribusi Kategorikal**')
            
            cat_columns = ['season', 'weathersit', 'yr', 'mnth', 'holiday', 'weekday', 'workingday']
            if 'hr' in df_to_explore.columns:
                cat_columns.insert(3, 'hr')
            
            available_cat = [col for col in cat_columns if col in df_to_explore.columns]
            
            if available_cat:
                selected_cat = st.selectbox('Pilih kolom kategorikal:', available_cat)
                
                dist = df_to_explore[selected_cat].value_counts().reset_index()
                dist.columns = [selected_cat, 'count']
                dist = dist.sort_values(by=selected_cat)
                
                fig_dist, ax_dist = plt.subplots(figsize=(10, 4))
                ax_dist.bar(range(len(dist)), dist['count'], color='#42A5F5', edgecolor='black', linewidth=0.5)
                ax_dist.set_xticks(range(len(dist)))
                ax_dist.set_xticklabels(dist[selected_cat], rotation=45 if len(dist) > 10 else 0)
                ax_dist.set_title(f'Distribusi {selected_cat}', fontsize=14, fontweight='bold')
                ax_dist.set_ylabel('Count')
                ax_dist.grid(axis='y', alpha=0.3)
                
                for i, v in enumerate(dist['count']):
                    ax_dist.text(i, v + max(dist['count'])*0.01, str(v), ha='center', fontsize=9)
                
                plt.tight_layout()
                st.pyplot(fig_dist)
                plt.close(fig_dist)
            else:
                st.info('Tidak ada kolom kategorikal tersedia.')
        
        st.markdown('---')
        
        # Info data
        st.markdown('**ℹ️ Informasi Dataset**')
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.metric('Jumlah Data (Filtered)', len(df_to_explore))
            st.metric('Total Data (Keseluruhan)', len(day_df) if 'Harian' in dataset_choice else len(hour_df))
        
        with col_info2:
            missing_data = df_to_explore.isnull().sum().sum()
            duplicate_data = df_to_explore.duplicated().sum()
            st.metric('Missing Values', missing_data)
            st.metric('Duplicate Rows', duplicate_data)
        
        with col_info3:
            if not df_to_explore.empty:
                st.metric('Range Tanggal', 
                         f"{df_to_explore['dteday'].min().strftime('%d %b %Y')} - {df_to_explore['dteday'].max().strftime('%d %b %Y')}")
                st.metric('Total Kolom', len(df_to_explore.columns))

# ── KESIMPULAN ──
st.markdown('---')
st.subheader('✅ Kesimpulan')

col_kesimpulan1, col_kesimpulan2 = st.columns(2)

with col_kesimpulan1:
    st.markdown('**Pertanyaan 1: Musim & Cuaca**')
    st.markdown("""
    - **Musim Fall** dan **cuaca Clear** secara konsisten menghasilkan jumlah penyewaan tertinggi sepanjang 2011–2012.
    - Kondisi cuaca buruk (**Light Rain/Snow**) terbukti menurunkan penyewaan secara drastis hingga **63%** dibanding cuaca Clear.
    
    **Rekomendasi bisnis:**
    - Tingkatkan ketersediaan armada sepeda di **musim Fall** dengan cuaca cerah.
    - Kurangi operasional saat **cuaca buruk** untuk efisiensi biaya.
    """)

with col_kesimpulan2:
    st.markdown('**Pertanyaan 2: Jam & Hari**')
    st.markdown("""
    - Penyewaan memuncak pada pukul **08.00** dan **17.00–18.00** yang mencerminkan pola penggunaan sepeda sebagai moda transportasi **komuter**.
    - **Hari Jumat** mencatat penyewaan tertinggi dalam seminggu.
    
    **Rekomendasi bisnis:**
    - Prioritaskan ketersediaan sepeda di **titik-titik strategis** (stasiun, perkantoran) pada jam dan hari tersebut.
    - Siapkan armada tambahan untuk mengakomodasi lonjakan permintaan di jam sibuk.
    """)

st.markdown('---')
st.caption('Sumber: Bike Sharing Dataset — Capital Bikeshare, Washington D.C. | Arel Lafito Dinoris')
