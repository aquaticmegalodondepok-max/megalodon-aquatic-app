import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Sistem Manajemen Les Renang",
    page_icon="🏊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING (EMERALD THEME) ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #0F7B5F;
    }
    .css-1544g2n {
        padding: 2rem 1rem;
    }
    h1, h2, h3 {
        color: #0F7B5F;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE DATABASE (SESSION STATE) ---
if 'pelatih' not in st.session_state:
    st.session_state.pelatih = pd.DataFrame([
        {"ID": "PLT-001", "Nama": "Budi Santoso", "No HP": "081234567890", "Tarif/Sesi": 75000, "Status": "Aktif"},
        {"ID": "PLT-002", "Nama": "Siti Aminah", "No HP": "082198765432", "Tarif/Sesi": 85000, "Status": "Aktif"},
        {"ID": "PLT-003", "Nama": "Rian Hidayat", "No HP": "083811223344", "Tarif/Sesi": 75000, "Status": "Aktif"},
        {"ID": "PLT-004", "Nama": "Dewi Lestari", "No HP": "085755667788", "Tarif/Sesi": 90000, "Status": "Aktif"}
    ])

if 'siswa' not in st.session_state:
    st.session_state.siswa = pd.DataFrame([
        {"ID": "SW-001", "Nama": "Andi Pratama", "Level": "Pemula", "Pelatih": "Budi Santoso", "Status": "Aktif"},
        {"ID": "SW-002", "Nama": "Citra Kirana", "Level": "Menengah", "Pelatih": "Siti Aminah", "Status": "Naik Level"},
        {"ID": "SW-003", "Nama": "Dimas Anggara", "Level": "Pemula", "Pelatih": "Rian Hidayat", "Status": "Aktif"},
        {"ID": "SW-004", "Nama": "Eka Putri", "Level": "Lanjutan", "Pelatih": "Dewi Lestari", "Status": "Naik Level"},
        {"ID": "SW-005", "Nama": "Faris Naufal", "Level": "Pemula", "Pelatih": "Budi Santoso", "Status": "Aktif"}
    ])

if 'absensi' not in st.session_state:
    st.session_state.absensi = pd.DataFrame([
        {"Tanggal": "2026-08-01", "Nama Pelatih": "Budi Santoso", "Kelas": "Pemula A", "Status": "Hadir", "Sesi": 1, "Catatan": "Latihan meluncur"},
        {"Tanggal": "2026-08-01", "Nama Pelatih": "Siti Aminah", "Kelas": "Menengah B", "Status": "Hadir", "Sesi": 2, "Catatan": "Gaya dada"},
        {"Tanggal": "2026-08-02", "Nama Pelatih": "Rian Hidayat", "Kelas": "Pemula B", "Status": "Hadir", "Sesi": 1, "Catatan": "Pengenalan air"},
        {"Tanggal": "2026-08-02", "Nama Pelatih": "Dewi Lestari", "Kelas": "Lanjutan A", "Status": "Hadir", "Sesi": 2, "Catatan": "Gaya bebas 50m"},
        {"Tanggal": "2026-08-03", "Nama Pelatih": "Budi Santoso", "Kelas": "Pemula A", "Status": "Hadir", "Sesi": 1, "Catatan": "Latihan napas"}
    ])

if 'progres' not in st.session_state:
    st.session_state.progres = pd.DataFrame([
        {"Tanggal": "2026-08-01", "Nama Siswa": "Andi Pratama", "Keberanian": 8, "Napas": 7, "Floating": 7, "Teknik": 6, "Rata-rata": 7.0, "Rekomendasi": "Tetap"},
        {"Tanggal": "2026-08-01", "Nama Siswa": "Citra Kirana", "Keberanian": 9, "Napas": 9, "Floating": 8, "Teknik": 9, "Rata-rata": 8.75, "Rekomendasi": "Naik Level"},
        {"Tanggal": "2026-08-02", "Nama Siswa": "Dimas Anggara", "Keberanian": 6, "Napas": 6, "Floating": 5, "Teknik": 6, "Rata-rata": 5.75, "Rekomendasi": "Tetap"},
        {"Tanggal": "2026-08-02", "Nama Siswa": "Eka Putri", "Keberanian": 9, "Napas": 10, "Floating": 9, "Teknik": 9, "Rata-rata": 9.25, "Rekomendasi": "Naik Level"}
    ])

if 'evaluasi' not in st.session_state:
    st.session_state.evaluasi = pd.DataFrame([
        {"Nama Pelatih": "Budi Santoso", "Bulan": "Agustus", "Kedisiplinan": 95, "Mengajar": 90, "Keselamatan": 95, "Total Nilai": 93.3},
        {"Nama Pelatih": "Siti Aminah", "Bulan": "Agustus", "Kedisiplinan": 85, "Mengajar": 90, "Keselamatan": 90, "Total Nilai": 88.3},
        {"Nama Pelatih": "Rian Hidayat", "Bulan": "Agustus", "Kedisiplinan": 100, "Mengajar": 95, "Keselamatan": 95, "Total Nilai": 96.6},
        {"Nama Pelatih": "Dewi Lestari", "Bulan": "Agustus", "Kedisiplinan": 90, "Mengajar": 92, "Keselamatan": 95, "Total Nilai": 92.3}
    ])

# --- NAVIGATION SIDEBAR ---
st.sidebar.image("https://img.icons8.com/color/96/swimming.png", width=70)
st.sidebar.title("Les Renang Academy")
st.sidebar.caption("Sistem Manajemen Operasional & Keuangan")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "MENU UTAMA",
    [
        "📊 Dashboard Management",
        "📝 Absensi Pelatih",
        "📈 Progres & Evaluasi Siswa",
        "💰 Penggajian & Bonus",
        "👥 Master Pelatih",
        "🏊 Master Siswa",
        "📥 Export / Backup Data"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tips:** Semua data interaktif dan dapat diperbarui secara langsung.")

# ----------------------------------------------------------------------
# 1. DASHBOARD MANAGEMENT
# ----------------------------------------------------------------------
if menu == "📊 Dashboard Management":
    st.title("📊 Management Executive Dashboard")
    st.write("Ringkasan real-time performa akademi renang, keuangan, dan siswa.")
    st.markdown("---")

    # Metrics Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Siswa Aktif", len(st.session_state.siswa[st.session_state.siswa['Status'] == 'Aktif']))
    with c2:
        st.metric("Total Pelatih Aktif", len(st.session_state.pelatih[st.session_state.pelatih['Status'] == 'Aktif']))
    with c3:
        total_sesi = st.session_state.absensi[st.session_state.absensi['Status'] == 'Hadir']['Sesi'].sum()
        st.metric("Total Sesi Terlaksana", int(total_sesi))
    with c4:
        naik_level = len(st.session_state.siswa[st.session_state.siswa['Status'] == 'Naik Level'])
        st.metric("Siswa Siap Naik Level", naik_level)

    st.write("")
    
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("💰 Ringkasan Pengeluaran Gaji Bulanan")
        df_gaji_summary = st.session_state.absensi[st.session_state.absensi['Status'] == 'Hadir'].groupby('Nama Pelatih')['Sesi'].sum().reset_index()
        df_gaji_summary = pd.merge(st.session_state.pelatih[['Nama', 'Tarif/Sesi']], df_gaji_summary, left_on='Nama', right_on='Nama Pelatih', how='left').fillna(0)
        df_gaji_summary['Gaji Sesi'] = df_gaji_summary['Sesi'] * df_gaji_summary['Tarif/Sesi']
        
        st.dataframe(
            df_gaji_summary[['Nama', 'Sesi', 'Tarif/Sesi', 'Gaji Sesi']].style.format({'Tarif/Sesi': 'Rp {:,.0f}', 'Gaji Sesi': 'Rp {:,.0f}'}),
            use_container_width=True
        )
        total_pengeluaran = df_gaji_summary['Gaji Sesi'].sum()
        st.success(f"**Total Estimasi Pengeluaran Gaji:** Rp {total_pengeluaran:,.0f}")

    with col_r:
        st.subheader("🏆 Pelatih Teraktif & Siswa Naik Level")
        tab_p, tab_s = st.tabs(["Pelatih Sesi Terbanyak", "Siswa Naik Level"])
        
        with tab_p:
            st.bar_chart(data=df_gaji_summary, x='Nama', y='Sesi')
            
        with tab_s:
            df_nl = st.session_state.siswa[st.session_state.siswa['Status'] == 'Naik Level']
            st.dataframe(df_nl[['Nama', 'Level', 'Pelatih']], use_container_width=True)

# ----------------------------------------------------------------------
# 2. ABSENSI PELATIH
# ----------------------------------------------------------------------
elif menu == "📝 Absensi Pelatih":
    st.title("📝 Absensi Kehadiran Pelatih")
    
    col_form, col_table = st.columns([1, 2])
    
    with col_form:
        st.subheader("Input Absensi Baru")
        with st.form("form_absensi_input"):
            tgl = st.date_input("Tanggal", datetime.now())
            nama_p = st.selectbox("Nama Pelatih", st.session_state.pelatih['Nama'].tolist())
            kelas = st.text_input("Nama / Level Kelas", "Pemula A")
            status = st.selectbox("Status Kehadiran", ["Hadir", "Izin", "Sakit", "Alpha"])
            sesi = st.number_input("Jumlah Sesi", min_value=0, max_value=5, value=1)
            catatan = st.text_area("Catatan Materi / Kendala", "Latihan dasar")
            
            if st.form_submit_button("Simpan Absensi"):
                new_row = pd.DataFrame([{
                    "Tanggal": str(tgl), "Nama Pelatih": nama_p, "Kelas": kelas,
                    "Status": status, "Sesi": sesi, "Catatan": catatan
                }])
                st.session_state.absensi = pd.concat([st.session_state.absensi, new_row], ignore_index=True)
                st.success(f"Absensi {nama_p} berhasil disimpan!")

    with col_table:
        st.subheader("Riwayat Kehadiran Pelatih")
        st.dataframe(st.session_state.absensi, use_container_width=True)

# ----------------------------------------------------------------------
# 3. PROGRES & EVALUASI SISWA
# ----------------------------------------------------------------------
elif menu == "📈 Progres & Evaluasi Siswa":
    st.title("📈 Laporan Progres Siswa")
    
    c_in, c_view = st.columns([1, 2])
    
    with c_in:
        st.subheader("Form Input Nilai Siswa")
        with st.form("form_progres_siswa"):
            tgl_p = st.date_input("Tanggal Evaluasi", datetime.now())
            nama_s = st.selectbox("Pilih Siswa", st.session_state.siswa['Nama'].tolist())
            
            k1 = st.slider("Keberanian Air (1-10)", 1, 10, 8)
            k2 = st.slider("Teknik Pernapasan (1-10)", 1, 10, 7)
            k3 = st.slider("Floating / Meluncur (1-10)", 1, 10, 7)
            k4 = st.slider("Penguasaan Teknik Gaya (1-10)", 1, 10, 7)
            
            rekom = st.selectbox("Rekomendasi", ["Tetap", "Naik Level", "Remedial"])
            
            if st.form_submit_button("Simpan Laporan Progres"):
                rata2 = (k1 + k2 + k3 + k4) / 4.0
                new_p = pd.DataFrame([{
                    "Tanggal": str(tgl_p), "Nama Siswa": nama_s, "Keberanian": k1,
                    "Napas": k2, "Floating": k3, "Teknik": k4,
                    "Rata-rata": rata2, "Rekomendasi": rekom
                }])
                st.session_state.progres = pd.concat([st.session_state.progres, new_p], ignore_index=True)
                
                # Auto update status siswa jika naik level
                if rekom == "Naik Level":
                    st.session_state.siswa.loc[st.session_state.siswa['Nama'] == nama_s, 'Status'] = "Naik Level"
                    
                st.success(f"Nilai {nama_s} tersimpan dengan Rata-rata: {rata2:.2f}")

    with c_view:
        st.subheader("Rekap Perkembangan Siswa")
        st.dataframe(
            st.session_state.progres.style.format({'Rata-rata': '{:.2f}'}),
            use_container_width=True
        )

# ----------------------------------------------------------------------
# 4. PENGGAJIAN & BONUS
# ----------------------------------------------------------------------
elif menu == "💰 Penggajian & Bonus":
    st.title("💰 Perhitungan Gaji & Bonus Pelatih")
    
    st.write("Sistem menghitung otomatis total sesi dari Sheet Absensi dikalikan tarif per sesi, ditambah bonus performa.")
    
    # Process Calculation
    df_abs_hadir = st.session_state.absensi[st.session_state.absensi['Status'] == 'Hadir']
    rekap_sesi = df_abs_hadir.groupby('Nama Pelatih')['Sesi'].sum().reset_index()
    
    df_payroll = pd.merge(st.session_state.pelatih, rekap_sesi, left_on='Nama', right_on='Nama Pelatih', how='left').fillna(0)
    
    # Merge Evaluasi for Bonus
    df_payroll = pd.merge(df_payroll, st.session_state.evaluasi[['Nama Pelatih', 'Total Nilai']], left_on='Nama', right_on='Nama Pelatih', how='left').fillna(0)
    
    # Calculate Gaji & Bonus Formulas
    df_payroll['Gaji Pokok'] = df_payroll['Sesi'] * df_payroll['Tarif/Sesi']
    df_payroll['Bonus Kehadiran'] = df_payroll['Sesi'].apply(lambda x: 200000 if x >= 2 else 0)
    df_payroll['Bonus Evaluasi'] = df_payroll['Total Nilai'].apply(lambda x: 300000 if x >= 90 else 0)
    df_payroll['Total Bonus'] = df_payroll['Bonus Kehadiran'] + df_payroll['Bonus Evaluasi']
    df_payroll['TOTAL GAJI'] = df_payroll['Gaji Pokok'] + df_payroll['Total Bonus']
    
    st.subheader("📋 Slip Gaji & Rekapitulasi Bulan Ini")
    
    st.dataframe(
        df_payroll[['Nama', 'Sesi', 'Tarif/Sesi', 'Gaji Pokok', 'Bonus Kehadiran', 'Bonus Evaluasi', 'TOTAL GAJI']].style.format({
            'Tarif/Sesi': 'Rp {:,.0f}',
            'Gaji Pokok': 'Rp {:,.0f}',
            'Bonus Kehadiran': 'Rp {:,.0f}',
            'Bonus Evaluasi': 'Rp {:,.0f}',
            'TOTAL GAJI': 'Rp {:,.0f}'
        }),
        use_container_width=True
    )
    
    st.markdown("---")
    st.subheader("💡 Rincian Rumus Otomatis")
    st.caption("1. **Gaji Pokok** = Total Sesi Hadir × Tarif Sesi")
    st.caption("2. **Bonus Kehadiran** = Rp 200.000 jika Kehadiran Penuh")
    st.caption("3. **Bonus Evaluasi** = Rp 300.000 jika Nilai Evaluasi ≥ 90")

# ----------------------------------------------------------------------
# 5. MASTER PELATIH
# ----------------------------------------------------------------------
elif menu == "👥 Master Pelatih":
    st.title("👥 Management Data Pelatih")
    
    with st.expander("➕ Tambah Pelatih Baru", expanded=False):
        with st.form("add_pelatih"):
            new_id = f"PLT-00{len(st.session_state.pelatih)+1}"
            n_pelatih = st.text_input("Nama Pelatih")
            hp_pelatih = st.text_input("Nomor HP")
            tarif = st.number_input("Tarif per Sesi (Rp)", value=75000, step=5000)
            st_pelatih = st.selectbox("Status", ["Aktif", "Non-Aktif"])
            
            if st.form_submit_button("Simpan Pelatih"):
                p_row = pd.DataFrame([{"ID": new_id, "Nama": n_pelatih, "No HP": hp_pelatih, "Tarif/Sesi": tarif, "Status": st_pelatih}])
                st.session_state.pelatih = pd.concat([st.session_state.pelatih, p_row], ignore_index=True)
                st.success(f"Pelatih {n_pelatih} berhasil didaftarkan!")
                
    st.subheader("Daftar Seluruh Pelatih")
    st.data_editor(st.session_state.pelatih, num_rows="dynamic", use_container_width=True)

# ----------------------------------------------------------------------
# 6. MASTER SISWA
# ----------------------------------------------------------------------
elif menu == "🏊 Master Siswa":
    st.title("🏊 Management Data Siswa")
    
    with st.expander("➕ Tambah Siswa Baru", expanded=False):
        with st.form("add_siswa"):
            new_s_id = f"SW-00{len(st.session_state.siswa)+1}"
            n_siswa = st.text_input("Nama Siswa")
            lvl_siswa = st.selectbox("Level", ["Pemula", "Menengah", "Lanjutan"])
            p_siswa = st.selectbox("Pelatih Utama", st.session_state.pelatih['Nama'].tolist())
            st_siswa = st.selectbox("Status", ["Aktif", "Naik Level", "Lulus", "Non-Aktif"])
            
            if st.form_submit_button("Simpan Siswa"):
                s_row = pd.DataFrame([{"ID": new_s_id, "Nama": n_siswa, "Level": lvl_siswa, "Pelatih": p_siswa, "Status": st_siswa}])
                st.session_state.siswa = pd.concat([st.session_state.siswa, s_row], ignore_index=True)
                st.success(f"Siswa {n_siswa} berhasil didaftarkan!")
                
    st.subheader("Daftar Seluruh Siswa")
    st.data_editor(st.session_state.siswa, num_rows="dynamic", use_container_width=True)

# ----------------------------------------------------------------------
# 7. EXPORT DATA
# ----------------------------------------------------------------------
elif menu == "📥 Export / Backup Data":
    st.title("📥 Backup & Download Laporan Data")
    st.write("Unduh seluruh data aplikasi ke dalam format Excel / CSV secara instant.")
    
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        st.subheader("📄 Unduh CSV Data")
        st.download_button("Download Data Pelatih (CSV)", st.session_state.pelatih.to_csv(index=False), "Data_Pelatih.csv", "text/csv")
        st.download_button("Download Data Siswa (CSV)", st.session_state.siswa.to_csv(index=False), "Data_Siswa.csv", "text/csv")
        st.download_button("Download Data Absensi (CSV)", st.session_state.absensi.to_csv(index=False), "Data_Absensi.csv", "text/csv")
        
    with col_e2:
        st.subheader("📊 Laporan Ringkas")
        st.download_button("Download Laporan Progres Siswa", st.session_state.progres.to_csv(index=False), "Progres_Siswa.csv", "text/csv")
        st.download_button("Download Laporan Evaluasi", st.session_state.evaluasi.to_csv(index=False), "Evaluasi_Pelatih.csv", "text/csv")
