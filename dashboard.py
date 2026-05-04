import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import os

plt.style.use('default')

# =====================================================
# LOAD DATA (TIDAK DIUBAH)
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

# Tambahan mapping untuk day_df agar konsisten
day_df['season'] = day_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})
day_df['weathersit'] = day_df['weathersit'].map({
    1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'
})
day_df['yr'] = day_df['yr'].map({0: 2011, 1: 2012})

# =====================================================
# SIDEBAR FILTERS (INTERAKTIF)
# =====================================================
st.sidebar.header("🔎 Dashboard Filters")

# Filter Tahun
year_filter = st.sidebar.multiselect(
    "Pilih Tahun",
    options=sorted(day_df['yr'].unique()),
    default=sorted(day_df['yr'].unique())
)

# Filter Musim
season_filter = st.sidebar.multiselect(
    "Pilih Musim",
    options=['Spring', 'Summer', 'Fall', 'Winter'],
    default=['Spring', 'Summer', 'Fall', 'Winter']
)

# Filter Cuaca
weather_filter = st.sidebar.multiselect(
    "Pilih Cuaca",
    options=['Clear', 'Mist', 'Light Rain/Snow', 'Heavy Rain/Snow'],
    default=['Clear', 'Mist', 'Light Rain/Snow', 'Heavy Rain/Snow']
)

# Filter Tipe Hari
workingday_filter = st.sidebar.radio(
    "Tipe Hari",
    ["Semua", "Hari Kerja", "Libur/Weekend"],
    horizontal=True
)

# Filter Range Bulan
st.sidebar.markdown("---")
month_range = st.sidebar.slider(
    "Rentang Bulan",
    min_value=1,
    max_value=12,
    value=(1, 12)
)

# Filter Tanggal
st.sidebar.markdown("---")
date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    value=[day_df['dteday'].min().date(), day_df['dteday'].max().date()],
    min_value=day_df['dteday'].min().date(),
    max_value=day_df['dteday'].max().date()
)

# Reset Button
if st.sidebar.button("🔄 Reset All Filters"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Filter mempengaruhi seluruh dashboard")

# =====================================================
# APPLY FILTERS (TANPA MERUBAH DATA ASLI)
# =====================================================
filtered_day = day_df[
    (day_df['yr'].isin(year_filter)) &
    (day_df['season'].isin(season_filter)) &
    (day_df['weathersit'].isin(weather_filter)) &
    (day_df['mnth'] >= month_range[0]) &
    (day_df['mnth'] <= month_range[1]) &
    (day_df['dteday'] >= pd.to_datetime(date_range[0])) &
    (day_df['dteday'] <= pd.to_datetime(date_range[1]))
]

filtered_hour = hour_df[
    (hour_df['yr'].isin(year_filter)) &
    (hour_df['season'].isin(season_filter)) &
    (hour_df['weathersit'].isin(weather_filter)) &
    (hour_df['mnth'] >= month_range[0]) &
    (hour_df['mnth'] <= month_range[1])
]

if len(date_range) == 2:
    filtered_hour = filtered_hour[
        (filtered_hour['dteday'] >= pd.to_datetime(date_range[0])) &
        (filtered_hour['dteday'] <= pd.to_datetime(date_range[1]))
    ]

if workingday_filter == "Hari Kerja":
    filtered_day = filtered_day[filtered_day['workingday'] == 1]
    filtered_hour = filtered_hour[filtered_hour['workingday'] == 1]
elif workingday_filter == "Libur/Weekend":
    filtered_day = filtered_day[filtered_day['workingday'] == 0]
    filtered_hour = filtered_hour[filtered_hour['workingday'] == 0]

# =====================================================
# HEADER
# =====================================================
st.title("🚴 BIKE SHARING INTERACTIVE DASHBOARD")
st.markdown("### Data Analyst Portfolio Version")
st.markdown(f"**Menampilkan {len(filtered_day)} hari dan {len(filtered_hour)} jam data**")

# =====================================================
# TABS NAVIGATION
# =====================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📌 Executive Summary",
    "🌦 Season & Weather Analysis",
    "⏰ Time Pattern Analysis",
    "📈 Advanced Analysis"
])

# =====================================================
# TAB 1 — EXECUTIVE SUMMARY
# =====================================================
with tab1:
    st.subheader("📊 Key Performance Metrics")
    
    # Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Rentals", 
            f"{filtered_day['cnt'].sum():,}",
            help="Total penyewaan berdasarkan filter"
        )
    with col2:
        st.metric(
            "Highest Daily Rentals", 
            f"{filtered_day['cnt'].max():,}",
            delta=f"Day: {filtered_day.loc[filtered_day['cnt'].idxmax(), 'dteday'].strftime('%d %b %Y')}" if not filtered_day.empty else ""
        )
    with col3:
        st.metric(
            "Avg / Day", 
            f"{filtered_day['cnt'].mean():.0f}",
            help="Rata-rata penyewaan per hari"
        )
    with col4:
        st.metric(
            "Avg / Hour", 
            f"{filtered_hour['cnt'].mean():.0f}" if not filtered_hour.empty else "0",
            help="Rata-rata penyewaan per jam"
        )

    # Growth metrics
    if len(filtered_day[filtered_day['yr'] == 2011]) > 0 and len(filtered_day[filtered_day['yr'] == 2012]) > 0:
        st.markdown("---")
        col_g1, col_g2, col_g3 = st.columns(3)
        
        total_2011 = filtered_day[filtered_day['yr'] == 2011]['cnt'].sum()
        total_2012 = filtered_day[filtered_day['yr'] == 2012]['cnt'].sum()
        growth = ((total_2012 - total_2011) / total_2011) * 100
        
        with col_g1:
            st.metric("Total 2011", f"{total_2011:,}")
        with col_g2:
            st.metric("Total 2012", f"{total_2012:,}")
        with col_g3:
            st.metric("Pertumbuhan", f"{growth:.1f}%")

    st.markdown("---")
    
    # Interactive Trend Selector
    st.subheader("📈 Tren Bulanan Interaktif")
    
    col_sel1, col_sel2 = st.columns([2, 1])
    
    with col_sel1:
        metric_choice = st.selectbox(
            "Pilih Metrik untuk Trend:",
            ["Total Rentals", "Casual Users", "Registered Users", "Both User Types"],
            key="metric_trend"
        )
    
    with col_sel2:
        show_data_labels = st.checkbox("Tampilkan Label Data", value=True)
    
    # Plot trend based on selection
    if not filtered_day.empty:
        fig, ax = plt.subplots(figsize=(12, 5))
        
        if metric_choice == "Both User Types":
            monthly_casual = filtered_day.groupby(filtered_day['dteday'].dt.month)['casual'].sum()
            monthly_registered = filtered_day.groupby(filtered_day['dteday'].dt.month)['registered'].sum()
            
            ax.plot(monthly_casual.index, monthly_casual.values, marker='o', label='Casual', linewidth=2)
            ax.plot(monthly_registered.index, monthly_registered.values, marker='s', label='Registered', linewidth=2)
            ax.legend()
            ax.set_ylabel("Number of Users")
        else:
            metric_map = {
                "Total Rentals": "cnt",
                "Casual Users": "casual",
                "Registered Users": "registered"
            }
            
            monthly = filtered_day.groupby(filtered_day['dteday'].dt.month)[metric_map[metric_choice]].sum()
            ax.plot(monthly.index, monthly.values, marker='o', linewidth=2, color='#2E86AB')
            ax.set_ylabel(metric_choice)
            
            if show_data_labels:
                for i, v in enumerate(monthly.values):
                    ax.text(monthly.index[i], v + (v*0.02), f'{v:,.0f}', ha='center', fontsize=9)
        
        ax.set_xlabel("Bulan")
        ax.set_title(f"Monthly Trend — {metric_choice}", fontsize=14, fontweight='bold')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 
                           'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'])
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)
    else:
        st.warning("⚠️ Tidak ada data yang sesuai dengan filter. Silakan sesuaikan filter.")

# =====================================================
# TAB 2 — SEASON & WEATHER ANALYSIS
# =====================================================
with tab2:
    st.subheader("🌦 Analisis Musim dan Cuaca")
    
    # Visualization type selector
    col_viz1, col_viz2 = st.columns([1, 3])
    
    with col_viz1:
        chart_type = st.radio(
            "Tipe Visualisasi:",
            ["Bar Chart", "Line Chart", "Keduanya"],
            key="season_chart_type"
        )
        
        sort_option = st.selectbox(
            "Urutkan Berdasarkan:",
            ["Nama", "Nilai Tertinggi", "Nilai Terendah"],
            key="season_sort"
        )
    
    with col_viz2:
        # Season Analysis
        if not filtered_day.empty:
            season_avg = filtered_day.groupby('season')['cnt'].mean()
            
            # Sorting
            if sort_option == "Nilai Tertinggi":
                season_avg = season_avg.sort_values(ascending=False)
            elif sort_option == "Nilai Terendah":
                season_avg = season_avg.sort_values(ascending=True)
            
            # Color mapping
            color_map = {
                'Spring': '#4CAF50',
                'Summer': '#FFC107', 
                'Fall': '#F44336',
                'Winter': '#2196F3'
            }
            colors = [color_map.get(s, '#999999') for s in season_avg.index]
            
            if chart_type in ["Bar Chart", "Keduanya"]:
                fig, ax = plt.subplots(figsize=(10, 5))
                bars = ax.bar(season_avg.index, season_avg.values, color=colors)
                ax.set_title('Rata-rata Penyewaan per Musim', fontsize=13, fontweight='bold')
                ax.set_xlabel('Musim')
                ax.set_ylabel('Rata-rata Penyewaan')
                
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 50,
                           f'{height:.0f}', ha='center', fontsize=10)
                
                st.pyplot(fig)
            
            if chart_type in ["Line Chart", "Keduanya"]:
                if chart_type == "Line Chart":
                    fig, ax = plt.subplots(figsize=(10, 5))
                else:
                    st.markdown("---")
                    fig, ax = plt.subplots(figsize=(10, 5))
                
                ax.plot(season_avg.index, season_avg.values, marker='o', linewidth=2, 
                       color='#E53935', markersize=10)
                ax.set_title('Rata-rata Penyewaan per Musim (Line)', fontsize=13, fontweight='bold')
                ax.set_xlabel('Musim')
                ax.set_ylabel('Rata-rata Penyewaan')
                ax.grid(True, alpha=0.3)
                
                for i, v in enumerate(season_avg.values):
                    ax.text(i, v + 50, f'{v:.0f}', ha='center', fontsize=10)
                
                st.pyplot(fig)
    
    st.markdown("---")
    
    # Weather Analysis
    st.subheader("🌤 Dampak Cuaca terhadap Penyewaan")
    
    if not filtered_day.empty:
        weather_avg = filtered_day.groupby('weathersit')['cnt'].mean().sort_values(ascending=False)
        
        col_w1, col_w2 = st.columns([2, 1])
        
        with col_w1:
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            weather_colors = {
                'Clear': '#4CAF50',
                'Mist': '#FFC107',
                'Light Rain/Snow': '#FF9800',
                'Heavy Rain/Snow': '#F44336'
            }
            bar_colors = [weather_colors.get(w, '#999999') for w in weather_avg.index]
            
            bars2 = ax2.bar(weather_avg.index, weather_avg.values, color=bar_colors)
            ax2.set_title('Rata-rata Penyewaan per Kondisi Cuaca', fontsize=13, fontweight='bold')
            ax2.set_xlabel('Kondisi Cuaca')
            ax2.set_ylabel('Rata-rata Penyewaan')
            ax2.tick_params(axis='x', rotation=15)
            
            for bar in bars2:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 50,
                       f'{height:.0f}', ha='center', fontsize=10)
            
            st.pyplot(fig2)
        
        with col_w2:
            st.markdown("**📊 Perbandingan dengan Clear:**")
            if 'Clear' in weather_avg.index:
                clear_value = weather_avg['Clear']
                for weather in weather_avg.index:
                    if weather != 'Clear':
                        decrease = ((clear_value - weather_avg[weather]) / clear_value) * 100
                        st.metric(
                            f"vs {weather}",
                            f"↓ {decrease:.1f}%",
                            delta=f"-{weather_avg[weather]:.0f} rentals",
                            delta_color="inverse"
                        )
    else:
        st.warning("⚠️ Tidak ada data yang sesuai dengan filter. Silakan sesuaikan filter.")

# =====================================================
# TAB 3 — TIME PATTERN ANALYSIS
# =====================================================
with tab3:
    st.subheader("⏰ Pola Waktu Penyewaan")
    
    # Interactive hour selector
    st.markdown("### Analisis per Jam")
    
    col_h1, col_h2 = st.columns([1, 2])
    
    with col_h1:
        hour_detail = st.checkbox("Tampilkan Detail per Jam", value=False)
        show_peak_lines = st.checkbox("Tandai Jam Sibuk", value=True)
    
    if not filtered_hour.empty:
        hour_avg = filtered_hour.groupby('hr')['cnt'].mean()
        
        with col_h2:
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(hour_avg.index, hour_avg.values, marker='o', color='#E53935', 
                   linewidth=2, markersize=4)
            
            if show_peak_lines:
                ax.axvline(x=8, color='gray', linestyle='--', alpha=0.7, label='Jam 08:00 (Pagi)')
                ax.axvline(x=17, color='blue', linestyle='--', alpha=0.7, label='Jam 17:00 (Sore)')
                ax.legend()
            
            ax.set_title('Rata-rata Penyewaan per Jam', fontsize=13, fontweight='bold')
            ax.set_xlabel('Jam')
            ax.set_ylabel('Rata-rata Penyewaan')
            ax.set_xticks(range(0, 24))
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)
        
        if hour_detail:
            st.markdown("---")
            st.markdown("**Detail Data per Jam:**")
            
            hour_df_display = pd.DataFrame({
                'Jam': hour_avg.index,
                'Rata-rata Penyewaan': hour_avg.values.round(0).astype(int)
            })
            
            # Highlight peak hours
            peak_morning = hour_avg.nlargest(1).index[0]
            peak_evening = hour_avg.nlargest(2).index[1] if len(hour_avg) > 1 else None
            
            st.dataframe(
                hour_df_display.style.highlight_max(subset=['Rata-rata Penyewaan'], color='#FFC107'),
                use_container_width=True,
                hide_index=True
            )
            
            st.info(f"📌 Jam tersibuk: **{peak_morning}:00** ({hour_avg.max():.0f} rentals/jam)")
    
    st.markdown("---")
    
    # Weekday Analysis
    st.markdown("### Analisis per Hari")
    
    col_wd1, col_wd2 = st.columns(2)
    
    with col_wd1:
        if not filtered_hour.empty:
            day_map = {0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 
                      4: 'Thu', 5: 'Fri', 6: 'Sat'}
            weekday_avg = filtered_hour.groupby('weekday')['cnt'].mean()
            weekday_avg.index = [day_map.get(i, str(i)) for i in weekday_avg.index]
            
            fig, ax = plt.subplots(figsize=(8, 5))
            day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            weekday_avg = weekday_avg.reindex([d for d in day_order if d in weekday_avg.index])
            
            bars = ax.bar(weekday_avg.index, weekday_avg.values, color='#AB47BC')
            ax.set_title('Rata-rata Penyewaan per Hari', fontsize=13, fontweight='bold')
            ax.set_xlabel('Hari')
            ax.set_ylabel('Rata-rata Penyewaan')
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                       f'{height:.0f}', ha='center', fontsize=9)
            
            st.pyplot(fig)
    
    with col_wd2:
        if not filtered_day.empty:
            st.markdown("**📊 Perbandingan Hari Kerja vs Libur:**")
            workday_avg = filtered_day.groupby('workingday')['cnt'].mean()
            
            fig, ax = plt.subplots(figsize=(8, 5))
            labels = ['Libur/Weekend', 'Hari Kerja']
            values = [workday_avg.get(0, 0), workday_avg.get(1, 0)]
            colors = ['#AB47BC', '#26A69A']
            
            bars = ax.bar(labels, values, color=colors)
            ax.set_title('Rata-rata Penyewaan: Hari Kerja vs Libur', fontsize=13, fontweight='bold')
            ax.set_ylabel('Rata-rata Penyewaan')
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 30,
                       f'{height:.0f}', ha='center', fontsize=11)
            
            st.pyplot(fig)

# =====================================================
# TAB 4 — ADVANCED ANALYSIS
# =====================================================
with tab4:
    st.subheader("📈 Analisis Lanjutan")
    
    # Sub-tabs for better organization
    sub_tab1, sub_tab2, sub_tab3 = st.tabs([
        "👥 User Segmentation",
        "🌡 Temperature Impact",
        "📊 Cross Analysis"
    ])
    
    # SUB-TAB 1: User Segmentation
    with sub_tab1:
        st.markdown("### Segmentasi Pengguna: Casual vs Registered")
        
        if not filtered_day.empty:
            col_seg1, col_seg2 = st.columns(2)
            
            with col_seg1:
                casual = filtered_day['casual'].sum()
                registered = filtered_day['registered'].sum()
                
                fig, ax = plt.subplots(figsize=(8, 6))
                wedges, texts, autotexts = ax.pie(
                    [casual, registered], 
                    labels=['Casual', 'Registered'],
                    autopct='%1.1f%%',
                    colors=['#FFC107', '#4CAF50'],
                    startangle=90,
                    explode=(0.05, 0)
                )
                ax.set_title('Proporsi Pengguna', fontsize=13, fontweight='bold')
                
                # Make percentage text bold
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                
                st.pyplot(fig)
            
            with col_seg2:
                st.markdown("**📊 Detail Segmentasi:**")
                total = casual + registered
                
                st.metric("Casual Users", f"{casual:,}", 
                         delta=f"{(casual/total)*100:.1f}% dari total" if total > 0 else "0%")
                st.metric("Registered Users", f"{registered:,}", 
                         delta=f"{(registered/total)*100:.1f}% dari total" if total > 0 else "0%")
                
                st.markdown("---")
                
                # Seasonal breakdown
                st.markdown("**Berdasarkan Musim:**")
                season_user = filtered_day.groupby('season').agg({
                    'casual': 'sum',
                    'registered': 'sum'
                })
                
                if not season_user.empty:
                    st.dataframe(
                        season_user.style.format("{:,.0f}"),
                        use_container_width=True
                    )
    
    # SUB-TAB 2: Temperature Impact
    with sub_tab2:
        st.markdown("### Hubungan Suhu dengan Penyewaan")
        
        if not filtered_day.empty:
            col_temp1, col_temp2 = st.columns([2, 1])
            
            with col_temp1:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Scatter plot dengan warna berdasarkan musim
                temp_celsius = filtered_day['temp'] * 41
                
                scatter = ax.scatter(
                    temp_celsius,
                    filtered_day['cnt'],
                    alpha=0.5,
                    c=filtered_day['season'].map({
                        'Spring': 0, 'Summer': 1, 'Fall': 2, 'Winter': 3
                    }),
                    cmap='viridis',
                    s=30
                )
                
                # Trendline
                z = np.polyfit(temp_celsius, filtered_day['cnt'], 1)
                p = np.poly1d(z)
                x_line = np.linspace(temp_celsius.min(), temp_celsius.max(), 100)
                ax.plot(x_line, p(x_line), color='#1565C0', linewidth=2, 
                       label='Trendline', linestyle='--')
                
                ax.set_xlabel("Temperature (°C)", fontsize=12)
                ax.set_ylabel("Total Rentals", fontsize=12)
                ax.set_title('Korelasi Suhu vs Jumlah Penyewaan', fontsize=13, fontweight='bold')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                # Add correlation coefficient
                corr = filtered_day['temp'].corr(filtered_day['cnt'])
                ax.text(0.95, 0.95, f'Correlation: {corr:.3f}', 
                       transform=ax.transAxes, fontsize=10,
                       verticalalignment='top', horizontalalignment='right',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
                
                st.pyplot(fig)
            
            with col_temp2:
                st.markdown("**🌡 Statistik Suhu:**")
                st.metric("Suhu Rata-rata", f"{(filtered_day['temp']*41).mean():.1f}°C")
                st.metric("Suhu Minimum", f"{(filtered_day['temp']*41).min():.1f}°C")
                st.metric("Suhu Maksimum", f"{(filtered_day['temp']*41).max():.1f}°C")
                
                st.markdown("---")
                st.markdown("**💡 Insight:**")
                st.info(f"""
                Korelasi suhu dengan penyewaan: **{corr:.2f}**
                
                {'Korelasi positif kuat - semakin tinggi suhu, semakin banyak penyewaan' if corr > 0.5 else 'Korelasi moderat'}
                """)
    
    # SUB-TAB 3: Cross Analysis
    with sub_tab3:
        st.markdown("### Analisis Silang Multi-Variabel")
        
        if not filtered_day.empty:
            # Select metrics
            col_cross1, col_cross2 = st.columns(2)
            
            with col_cross1:
                x_axis = st.selectbox(
                    "Pilih Variabel X:",
                    ['season', 'weathersit', 'mnth', 'weekday', 'workingday'],
                    format_func=lambda x: {
                        'season': 'Musim',
                        'weathersit': 'Cuaca',
                        'mnth': 'Bulan',
                        'weekday': 'Hari',
                        'workingday': 'Tipe Hari'
                    }.get(x, x)
                )
            
            with col_cross2:
                y_metric = st.selectbox(
                    "Pilih Metrik Y:",
                    ['cnt', 'casual', 'registered'],
                    format_func=lambda x: {
                        'cnt': 'Total',
                        'casual': 'Casual',
                        'registered': 'Registered'
                    }.get(x, x)
                )
            
            # Grouped analysis
            cross_data = filtered_day.groupby(x_axis)[y_metric].agg(['mean', 'sum']).round(0)
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            
            # Mean plot
            cross_data['mean'].plot(kind='bar', ax=ax1, color='#42A5F5')
            ax1.set_title(f'Rata-rata {y_metric} per {x_axis}', fontweight='bold')
            ax1.set_ylabel('Rata-rata')
            ax1.tick_params(axis='x', rotation=45)
            
            # Sum plot
            cross_data['sum'].plot(kind='bar', ax=ax2, color='#EF5350')
            ax2.set_title(f'Total {y_metric} per {x_axis}', fontweight='bold')
            ax2.set_ylabel('Total')
            ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            st.markdown("---")
            st.markdown("**📋 Data Tabel:**")
            st.dataframe(
                cross_data.style.format("{:,.0f}").highlight_max(color='#FFC107'),
                use_container_width=True
            )
        else:
            st.warning("⚠️ Tidak ada data yang sesuai dengan filter.")

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.markdown("### 💡 Key Insights & Recommendations")

col_ins1, col_ins2 = st.columns(2)

with col_ins1:
    st.info("""
    **🌦 Season & Weather:** 
    - Fall + Clear weather = kombinasi terbaik
    - Light Rain/Snow mengurangi penyewaan hingga 63%
    - Siapkan lebih banyak sepeda saat cuaca cerah di musim Fall
    """)

with col_ins2:
    st.info("""
    **⏰ Time Pattern:**
    - Peak hours: 08:00 dan 17:00 (jam komuter)
    - Hari Jumat adalah hari tersibuk
    - Optimalkan distribusi sepeda di jam dan hari sibuk
    """)

st.markdown("---")
st.caption("📊 Bike Sharing Dataset — Capital Bikeshare, Washington D.C. | Interactive Dashboard by Data Analyst")
