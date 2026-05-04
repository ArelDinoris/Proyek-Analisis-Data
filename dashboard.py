import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import os

plt.style.use('default')

# =====================================================
# LOAD DATA (ASLI TIDAK DIUBAH)
# =====================================================
day_df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'main_data.csv'))
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

hour_df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'hour.csv'))
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Mapping untuk hour_df (karena aslinya angka)
hour_df['season'] = hour_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})
hour_df['weathersit'] = hour_df['weathersit'].map({
    1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'
})
hour_df['yr'] = hour_df['yr'].map({0: 2011, 1: 2012})

# =====================================================
# SIAPKAN KOLOM LABEL UNTUK day_df (TANPA MENGHAPUS KOLOM ASLI)
# =====================================================
# Untuk kolom 'yr': deteksi apakah masih 0/1 atau sudah tahun
if day_df['yr'].max() <= 1:
    day_df['yr_label'] = day_df['yr'].map({0: 2011, 1: 2012})
else:
    day_df['yr_label'] = day_df['yr']

# Untuk 'season': deteksi apakah sudah string atau masih angka
if day_df['season'].dtype == object:
    day_df['season_label'] = day_df['season']
else:
    day_df['season_label'] = day_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})

# Untuk 'weathersit': deteksi apakah sudah string atau masih angka
if day_df['weathersit'].dtype == object:
    day_df['weather_label'] = day_df['weathersit']
else:
    day_df['weather_label'] = day_df['weathersit'].map({
        1:'Clear', 2:'Mist', 3:'Light Rain/Snow', 4:'Heavy Rain/Snow'
    })

# =====================================================
# KONFIGURASI HALAMAN (INTERAKTIF)
# =====================================================
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚴", layout="wide")

# =====================================================
# SIDEBAR FILTER HANYA TAHUN & MUSIM
# =====================================================
st.sidebar.header("🔎 Filter Tahun & Musim")

# Ambil daftar tahun dan musim yang tersedia
available_years = sorted(day_df['yr_label'].unique())
available_seasons = ['Spring', 'Summer', 'Fall', 'Winter']

# Multiselect untuk tahun
selected_years = st.sidebar.multiselect(
    "Pilih Tahun",
    options=available_years,
    default=available_years   # default: semua terpilih
)

# Multiselect untuk musim
selected_seasons = st.sidebar.multiselect(
    "Pilih Musim",
    options=available_seasons,
    default=available_seasons  # default: semua terpilih
)

# Tambahkan opsi "Semua" dengan tombol (opsional)
if st.sidebar.button("🔄 Tampilkan Semua Data"):
    selected_years = available_years
    selected_seasons = available_seasons
    st.rerun()

# =====================================================
# TERAPKAN FILTER KE SALINAN DATA (TIDAK MERUSAK ASLI)
# =====================================================
filtered_day = day_df[
    (day_df['yr_label'].isin(selected_years)) &
    (day_df['season_label'].isin(selected_seasons))
].copy()

filtered_hour = hour_df[
    (hour_df['yr'].isin(selected_years)) &
    (hour_df['season'].isin(selected_seasons))
].copy()

# =====================================================
# HEADER & IDENTITAS
# =====================================================
st.title("🚴 Bike Sharing Dashboard")
st.markdown("**Nama:** Arel Lafito Dinoris | **Email:** areldinoris23@gmail.com | **ID:** areldinoris")
st.markdown("---")

# =====================================================
# METRIK RINGKASAN (MENGGUNAKAN DATA TERFILTER)
# =====================================================
total_filt = filtered_day['cnt'].sum()
max_filt   = filtered_day['cnt'].max()
avg_day_filt = filtered_day['cnt'].mean()
avg_hr_filt  = filtered_hour['cnt'].mean() if len(filtered_hour) > 0 else 0

# Baseline dari seluruh data (sebagai delta)
total_all = day_df['cnt'].sum()
avg_day_all = day_df['cnt'].mean()
avg_hour_all = hour_df['cnt'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("🚲 Total Penyewaan", f"{total_filt:,.0f}",
            delta=f"dari {total_all:,.0f} total")
col2.metric("📈 Penyewaan Tertinggi", f"{max_filt:,.0f}")
col3.metric("📊 Rata-rata/Hari", f"{avg_day_filt:.0f}",
            delta=f"baseline {avg_day_all:.0f}")
col4.metric("⏱ Rata-rata/Jam", f"{avg_hr_filt:.0f}",
            delta=f"baseline {avg_hour_all:.0f}")

st.markdown("---")

# =====================================================
# TAB INTERAKTIF
# =====================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📌 Ringkasan Eksekutif",
    "🌦 Pertanyaan 1 (Musim & Cuaca)",
    "⏰ Pertanyaan 2 (Waktu & Hari)",
    "📈 Analisis Lanjutan",
    "✅ Kesimpulan"
])

# =====================================================
# TAB 1 – RINGKASAN EKSEKUTIF DENGAN TREN BULANAN
# =====================================================
with tab1:
    st.subheader("📌 Executive Summary")

    if len(filtered_day) == 0:
        st.warning("Tidak ada data dengan filter saat ini.")
    else:
        # Pilihan metrik
        metric_choice = st.radio(
            "Pilih Metrik Tren Bulanan:",
            ["Total Rentals", "Casual", "Registered"],
            horizontal=True
        )
        metric_map = {"Total Rentals": "cnt", "Casual": "casual", "Registered": "registered"}

        # Agregasi bulanan
        monthly = filtered_day.groupby(filtered_day['dteday'].dt.month)[metric_map[metric_choice]].sum()

        # Plot
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.fill_between(monthly.index, monthly.values, alpha=0.25, color='#42A5F5')
        ax.plot(monthly.index, monthly.values, marker='o', color='#1565C0', linewidth=2.5)
        ax.set_title(f"Tren Bulanan – {metric_choice}", fontsize=14, fontweight='bold')
        ax.set_xlabel("Bulan")
        ax.set_ylabel(metric_choice)
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
                            'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'])
        ax.grid(alpha=0.3)
        for x, y in zip(monthly.index, monthly.values):
            ax.text(x, y + y*0.02, f'{y:,.0f}', ha='center', fontsize=8)
        st.pyplot(fig)
        plt.close(fig)

        # Ringkasan tambahan
        colA, colB = st.columns(2)
        with colA:
            # Total per tahun (jika ada 2 tahun terpilih)
            yearly = filtered_day.groupby('yr_label')['cnt'].sum()
            if len(yearly) > 0:
                fig2, ax2 = plt.subplots(figsize=(5, 3.5))
                ax2.bar(yearly.index.astype(str), yearly.values,
                        color=['#42A5F5', '#EF5350'][:len(yearly)])
                ax2.set_title("Total Penyewaan per Tahun", fontsize=12)
                ax2.set_ylabel("Total")
                for i, v in enumerate(yearly.values):
                    ax2.text(i, v + 200, f'{v:,}', ha='center', fontweight='bold')
                plt.tight_layout()
                st.pyplot(fig2)
                plt.close(fig2)
        with colB:
            # Pie casual vs registered
            if len(filtered_day) > 0:
                fig3, ax3 = plt.subplots(figsize=(5, 3.5))
                ax3.pie([filtered_day['casual'].sum(), filtered_day['registered'].sum()],
                        labels=['Casual', 'Registered'], autopct='%1.1f%%',
                        colors=['#FFC107', '#4CAF50'], startangle=90, explode=(0.05, 0))
                ax3.set_title("Proporsi Pengguna", fontsize=12)
                st.pyplot(fig3)
                plt.close(fig3)

# =====================================================
# TAB 2 – PERTANYAAN 1 (MUSIM & CUACA)
# =====================================================
with tab2:
    st.subheader("📊 Pertanyaan 1: Pengaruh Musim & Cuaca terhadap Penyewaan")

    if len(filtered_day) == 0:
        st.warning("Tidak ada data dengan filter saat ini.")
    else:
        fig1, axes = plt.subplots(1, 2, figsize=(14, 5))

        # --- Musim ---
        season_order = ['Spring', 'Summer', 'Fall', 'Winter']
        season_avg = filtered_day.groupby('season_label')['cnt'].mean().reindex(season_order).dropna()
        axes[0].bar(season_avg.index, season_avg.values,
                    color=['#4CAF50', '#FFC107', '#F44336', '#2196F3'][:len(season_avg)])
        axes[0].set_title('Rata-rata Penyewaan per Musim', fontsize=13)
        axes[0].set_xlabel('Musim')
        axes[0].set_ylabel('Rata-rata Penyewaan')
        for i, v in enumerate(season_avg.values):
            axes[0].text(i, v + 50, str(round(v)), ha='center', fontsize=10)

        # --- Cuaca ---
        weather_avg = filtered_day.groupby('weather_label')['cnt'].mean().sort_values(ascending=False)
        axes[1].bar(range(len(weather_avg)), weather_avg.values, color='#42A5F5')
        axes[1].set_xticks(range(len(weather_avg)))
        axes[1].set_xticklabels(weather_avg.index, rotation=15, ha='right')
        axes[1].set_title('Rata-rata Penyewaan per Kondisi Cuaca', fontsize=13)
        axes[1].set_xlabel('Kondisi Cuaca')
        axes[1].set_ylabel('Rata-rata Penyewaan')
        for i, v in enumerate(weather_avg.values):
            axes[1].text(i, v + 50, str(round(v)), ha='center', fontsize=10)
        axes[1].tick_params(axis='x', rotation=15)

        plt.tight_layout()
        st.pyplot(fig1)
        plt.close(fig1)

        st.info("💡 Fall + Clear weather = kombinasi terbaik. Light Rain/Snow turunkan penyewaan hingga 63%.")

        # Heatmap opsional
        st.markdown("**Heatmap Musim × Cuaca**")
        heatmap_data = filtered_day.groupby(['season_label', 'weather_label'])['cnt'].mean().unstack(fill_value=0)
        if not heatmap_data.empty:
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            im = ax2.imshow(heatmap_data.values, cmap='YlOrRd', aspect='auto')
            ax2.set_xticks(range(len(heatmap_data.columns)))
            ax2.set_xticklabels(heatmap_data.columns, fontsize=10)
            ax2.set_yticks(range(len(heatmap_data.index)))
            ax2.set_yticklabels(heatmap_data.index, fontsize=10)
            ax2.set_title("Heatmap Rata-rata Penyewaan: Musim × Cuaca", fontsize=13, fontweight='bold')
            plt.colorbar(im, ax=ax2)
            max_val = heatmap_data.values.max()
            for i in range(heatmap_data.shape[0]):
                for j in range(heatmap_data.shape[1]):
                    val = heatmap_data.values[i, j]
                    color = 'white' if val > max_val * 0.7 else 'black'
                    ax2.text(j, i, f'{val:.0f}', ha='center', va='center', fontsize=9, color=color)
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)

# =====================================================
# TAB 3 – PERTANYAAN 2 (WAKTU & HARI)
# =====================================================
with tab3:
    st.subheader("⏰ Pertanyaan 2: Pola Penyewaan Berdasarkan Waktu")

    if len(filtered_hour) == 0:
        st.warning("Tidak ada data jam dengan filter saat ini.")
    else:
        fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))

        # --- Per Jam ---
        hour_avg = filtered_hour.groupby('hr')['cnt'].mean()
        axes2[0].plot(hour_avg.index, hour_avg.values, marker='o', color='#E53935', linewidth=2)
        axes2[0].set_title('Rata-rata Penyewaan per Jam', fontsize=13)
        axes2[0].set_xlabel('Jam')
        axes2[0].set_ylabel('Rata-rata Penyewaan')
        axes2[0].set_xticks(range(0, 24))
        axes2[0].axvline(x=8, color='gray', linestyle='--', alpha=0.5, label='Jam 08.00')
        axes2[0].axvline(x=17, color='blue', linestyle='--', alpha=0.5, label='Jam 17.00')
        axes2[0].legend()
        axes2[0].grid(alpha=0.3)

        # --- Per Hari ---
        day_map = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
        weekday_avg = filtered_hour.groupby('weekday')['cnt'].mean().rename(index=day_map)
        axes2[1].bar(weekday_avg.index, weekday_avg.values,
                     color=['#AB47BC' if d not in ['Sat','Sun'] else '#26A69A' for d in weekday_avg.index])
        axes2[1].set_title('Rata-rata Penyewaan per Hari', fontsize=13)
        axes2[1].set_xlabel('Hari')
        axes2[1].set_ylabel('Rata-rata Penyewaan')
        for i, v in enumerate(weekday_avg.values):
            axes2[1].text(i, v + 2, str(round(v)), ha='center', fontsize=9)
        axes2[1].grid(alpha=0.3, axis='y')

        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

        st.info("💡 Puncak di 08.00 & 17.00 (komuter). Hari Jumat tertinggi.")

        # Pola jam kerja vs libur
        st.markdown("**Perbandingan Pola Jam: Hari Kerja vs Libur**")
        workday_hour = filtered_hour.groupby(['workingday', 'hr'])['cnt'].mean().unstack(level=0)
        workday_hour.columns = ['Libur/Weekend' if c == 0 else 'Hari Kerja' for c in workday_hour.columns]
        fig3, ax3 = plt.subplots(figsize=(12, 4))
        if 'Hari Kerja' in workday_hour.columns:
            ax3.plot(workday_hour.index, workday_hour['Hari Kerja'],
                     marker='o', label='Hari Kerja', color='#1565C0', linewidth=2)
        if 'Libur/Weekend' in workday_hour.columns:
            ax3.plot(workday_hour.index, workday_hour['Libur/Weekend'],
                     marker='s', label='Libur/Weekend', color='#EF5350', linewidth=2, linestyle='--')
        ax3.set_title("Pola Penyewaan per Jam: Hari Kerja vs Libur", fontsize=13, fontweight='bold')
        ax3.set_xlabel("Jam")
        ax3.set_ylabel("Rata-rata Penyewaan")
        ax3.set_xticks(range(0, 24))
        ax3.legend()
        ax3.grid(alpha=0.3)
        st.pyplot(fig3)
        plt.close(fig3)

# =====================================================
# TAB 4 – ANALISIS LANJUTAN
# =====================================================
with tab4:
    st.subheader("📈 Analisis Lanjutan")

    if len(filtered_day) == 0:
        st.warning("Tidak ada data dengan filter saat ini.")
    else:
        # Statistik
        growth = filtered_day.groupby('yr_label')['cnt'].sum()
        pct = 0
        if 2011 in growth.index and 2012 in growth.index:
            pct = ((growth[2012] - growth[2011]) / growth[2011]) * 100
        casual_total = filtered_day['casual'].sum()
        registered_total = filtered_day['registered'].sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            if 2011 in growth.index:
                st.metric('Total 2011', f"{growth[2011]:,}")
            if 2012 in growth.index:
                st.metric('Total 2012', f"{growth[2012]:,}")
            if pct != 0:
                st.metric('Pertumbuhan', f"{pct:.1f}%")
        with col2:
            st.metric('Casual', f"{casual_total:,}")
            st.metric('Registered', f"{registered_total:,}")
        with col3:
            total_users = casual_total + registered_total
            if total_users > 0:
                st.metric('Proporsi Casual', f"{casual_total/total_users*100:.1f}%")
                st.metric('Proporsi Registered', f"{registered_total/total_users*100:.1f}%")

        st.markdown("---")

        # Figure 2x2
        fig3, axes3 = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Tren bulanan
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

        # 2. Pie
        axes3[0, 1].pie([casual_total, registered_total],
                        labels=['Casual', 'Registered'], autopct='%1.1f%%',
                        colors=['#FFC107', '#4CAF50'], startangle=90, explode=(0.05, 0))
        axes3[0, 1].set_title('Proporsi Pengguna: Casual vs Registered', fontsize=13)

        # 3. Hari kerja vs libur
        workday_avg = filtered_day.groupby('workingday')['cnt'].mean()
        workday_avg.index = workday_avg.index.map({0: 'Libur/Weekend', 1: 'Hari Kerja'})
        axes3[1, 0].bar(workday_avg.index, workday_avg.values,
                       color=['#AB47BC', '#26A69A'], width=0.4)
        axes3[1, 0].set_title('Rata-rata Penyewaan: Hari Kerja vs Libur', fontsize=13)
        axes3[1, 0].set_xlabel('Tipe Hari')
        axes3[1, 0].set_ylabel('Rata-rata Penyewaan')
        axes3[1, 0].grid(alpha=0.3, axis='y')
        for i, v in enumerate(workday_avg.values):
            axes3[1, 0].text(i, v + 30, str(round(v)), ha='center', fontsize=11)

        # 4. Suhu vs penyewaan
        temp_c = filtered_day['temp'] * 41
        axes3[1, 1].scatter(temp_c, filtered_day['cnt'], alpha=0.4, color='#FF7043', s=20)
        z = np.polyfit(temp_c, filtered_day['cnt'], 1)
        p_line = np.poly1d(z)
        x_line = np.linspace(temp_c.min(), temp_c.max(), 100)
        axes3[1, 1].plot(x_line, p_line(x_line), color='#1565C0', linewidth=2, label='Trendline')
        axes3[1, 1].set_title('Korelasi Suhu vs Jumlah Penyewaan', fontsize=13)
        axes3[1, 1].set_xlabel('Suhu (°C)')
        axes3[1, 1].set_ylabel('Jumlah Penyewaan')
        axes3[1, 1].legend()
        axes3[1, 1].grid(alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

        # Bonus: casual vs registered monthly
        st.markdown("**Tren Bulanan Casual vs Registered**")
        monthly_seg = filtered_day.groupby(filtered_day['dteday'].dt.month)[['casual', 'registered']].sum()
        fig4, ax4 = plt.subplots(figsize=(12, 4))
        ax4.plot(monthly_seg.index, monthly_seg['casual'], marker='o',
                 label='Casual', color='#FFC107', linewidth=2)
        ax4.plot(monthly_seg.index, monthly_seg['registered'], marker='s',
                 label='Registered', color='#4CAF50', linewidth=2)
        ax4.set_title("Tren Bulanan Casual vs Registered", fontsize=13, fontweight='bold')
        ax4.set_xlabel("Bulan")
        ax4.set_ylabel("Total Penyewaan")
        ax4.set_xticks(range(1, 13))
        ax4.set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'])
        ax4.legend()
        ax4.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close(fig4)

# =====================================================
# TAB 5 – KESIMPULAN
# =====================================================
with tab5:
    st.subheader("✅ Kesimpulan")

    col_kes1, col_kes2 = st.columns(2)
    with col_kes1:
        st.markdown("""
        **Pertanyaan 1**  
        - **Musim Fall** dan **cuaca Clear** menghasilkan penyewaan tertinggi.  
        - **Light Rain/Snow** menurunkan penyewaan hingga 63%.  
        **Rekomendasi:** Optimalkan armada di Fall & cuaca cerah.
        """)
    with col_kes2:
        st.markdown("""
        **Pertanyaan 2**  
        - Puncak di **08.00** dan **17.00** (pola komuter).  
        - **Hari Jumat** adalah hari tersibuk.  
        **Rekomendasi:** Prioritas di jam sibuk & lokasi strategis.
        """)

    st.markdown("---")
    st.markdown("""
    **Analisis Lanjutan**  
    - Pertumbuhan 2011→2012 positif, menunjukkan adopsi meningkat.  
    - Pengguna **Registered** mendominasi (~80%), basis pelanggan loyal.  
    - Korelasi positif suhu dengan penyewaan.
    """)

    st.markdown("---")
    st.caption("Sumber: Bike Sharing Dataset — Capital Bikeshare, Washington D.C. | Arel Lafito Dinoris")
