import streamlit as st
import pandas as pd
import numpy as np
import io
import re
from datetime import datetime

# --- REPORTLAB IMPORTS ---
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ==========================================
# 1. PAGE CONFIG & THEME SETUP
# ==========================================
st.set_page_config(
    page_title="Megalodon Aquatic - System Management",
    page_icon="🏊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Emerald Green #0F7B5F & Ocean Soft Blue #E0F2FE)
st.markdown("""
    <style>
    .stApp {
        background-color: #F8FAFC;
    }
    .css-1d3av2a, [data-testid="stSidebar"] {
        background-color: #0F7B5F !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    .metric-card {
        background-color: #E0F2FE;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #0F7B5F;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button {
        background-color: #0F7B5F;
        color: white;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0B5C47;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER FUNCTIONS & CACHING
# ==========================================
@st.cache_data
def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Helper universal untuk ekspor dataframe ke CSV"""
    return df.to_csv(index=False).encode('utf-8')

def download_csv_button(df: pd.DataFrame, filename: str, key: str):
    """Menampilkan tombol download CSV universal"""
    csv_data = convert_df_to_csv(df)
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        key=key
    )

def generate_pdf_raport(student_name, coach_name, pool, stats_dict):
    """Membuat Raport PDF menggunakan ReportLab"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#0F7B5F'),
        alignment=1,
        spaceAfter=12
    )
    
    story = []
    story.append(Paragraph("MEGALODON AQUATIC SWIMMING ACADEMY", title_style))
    story.append(Paragraph("<b>RAPORT EVALUASI PROGRES SISWA</b>", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    info_data = [
        ["Nama Siswa:", student_name, "Lokasi Kolam:", pool],
        ["Pelatih:", coach_name, "Tanggal Cetak:", datetime.now().strftime("%Y-%m-%d")]
    ]
    t_info = Table(info_data, colWidths=[100, 150, 100, 150])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#E0F2FE')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 18))
    
    eval_data = [["Teknik Renang", "Nilai Evaluasi (1-100)"]]
    for skill, val in stats_dict.items():
        eval_data.append([skill, str(val)])
        
    t_eval = Table(eval_data, colWidths=[250, 250])
    t_eval.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F7B5F')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    story.append(t_eval)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_multi_sheet_excel(data_dict):
    """Membuat file .xlsx multi-sheet menggunakan pandas & xlsxwriter"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in data_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return output

# ==========================================
# 3. INITIALIZATION OF STATE & DUMMY DATA
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = ""

if 'data_siswa' not in st.session_state:
    st.session_state.data_siswa = pd.DataFrame([
        {"ID Siswa": "SSW-001", "Nama Siswa": "Budi Santoso", "No HP": "628123456789", "Lokasi Kolam": "Kolam Cilandak", "Sisa Kuota": 4, "Status": "Aktif"},
        {"ID Siswa": "SSW-002", "Nama Siswa": "Siti Aminah", "No HP": "628987654321", "Lokasi Kolam": "Kolam GBK", "Sisa Kuota": 2, "Status": "Aktif"},
        {"ID Siswa": "SSW-003", "Nama Siswa": "Ahmad Dani", "No HP": "628111222333", "Lokasi Kolam": "Kolam Cilandak", "Sisa Kuota": 0, "Status": "Non-Aktif"},
    ])

if 'data_pelatih' not in st.session_state:
    st.session_state.data_pelatih = pd.DataFrame([
        {"ID Pelatih": "PLT-001", "Nama Pelatih": "Coach Anton", "No HP": "628555666777", "Tarif/Sesi": 100000, "Status": "Aktif"},
        {"ID Pelatih": "PLT-002", "Nama Pelatih": "Coach Bella", "No HP": "628444333222", "Tarif/Sesi": 120000, "Status": "Aktif"},
    ])

if 'absensi_pelatih' not in st.session_state:
    st.session_state.absensi_pelatih = pd.DataFrame([
        {"Tanggal": "2026-08-01", "ID Pelatih": "PLT-001", "Nama Pelatih": "Coach Anton", "Kolam": "Kolam Cilandak", "Jumlah Sesi": 2, "Keterangan": "Hadir"},
        {"Tanggal": "2026-08-02", "ID Pelatih": "PLT-002", "Nama Pelatih": "Coach Bella", "Kolam": "Kolam GBK", "Jumlah Sesi": 1, "Keterangan": "Hadir"},
    ])

if 'absensi_siswa' not in st.session_state:
    st.session_state.absensi_siswa = pd.DataFrame([
        {"Tanggal": "2026-08-01", "ID Siswa": "SSW-001", "Nama Siswa": "Budi Santoso", "Kolam": "Kolam Cilandak", "Pelatih": "Coach Anton", "Materi": "Gaya Bebas"},
    ])

if 'pembayaran_spp' not in st.session_state:
    st.session_state.pembayaran_spp = pd.DataFrame([
        {"Tanggal": "2026-08-01", "ID Siswa": "SSW-001", "Nama Siswa": "Budi Santoso", "Jumlah Bayar": 500000, "Tambahan Kuota": 4, "Metode": "Transfer"},
    ])

if 'pengeluaran_ops' not in st.session_state:
    st.session_state.pengeluaran_ops = pd.DataFrame([
        {"Tanggal": "2026-08-01", "Kategori": "Sewa Kolam", "Nominal": 200000, "Keterangan": "Sewa jalur Cilandak"},
    ])

if 'progres_siswa' not in st.session_state:
    st.session_state.progres_siswa = pd.DataFrame([
        {"ID Siswa": "SSW-001", "Nama Siswa": "Budi Santoso", "Meluncur": 85, "Gaya Bebas": 80, "Gaya Dada": 75, "Gaya Punggung": 70, "Gaya Kupu": 60},
    ])

if 'users' not in st.session_state:
    st.session_state.users = pd.DataFrame([
        {"Username": "admin", "Password": "123", "Role": "ADMIN"},
        {"Username": "pelatih", "Password": "123", "Role": "PELATIH"},
    ])

# ==========================================
# 4. LOGIN SYSTEM
# ==========================================
def login_screen():
    st.markdown("<h2 style='text-align: center; color: #0F7B5F;'>🏊 MEGALODON AQUATIC MANAGEMENT SYSTEM</h2>", unsafe_allow_html=True)
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.subheader("🔑 Silakan Login")
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            user_match = st.session_state.users[
                (st.session_state.users['Username'] == username_input) & 
                (st.session_state.users['Password'] == password_input)
            ]
            if not user_match.empty:
                st.session_state.logged_in = True
                st.session_state.user_role = user_match.iloc[0]['Role']
                st.session_state.username = user_match.iloc[0]['Username']
                st.success(f"Login Berhasil sebagai {st.session_state.user_role}")
                st.rerun()
            else:
                st.error("Username atau Password salah!")

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# ==========================================
# 5. SIDEBAR NAVIGATION & RBAC
# ==========================================
st.sidebar.title("🏊 Megalodon System")
st.sidebar.write(f"Logged in: **{st.session_state.username}** (`{st.session_state.user_role}`)")

if st.session_state.user_role == "ADMIN":
    menu_options = [
        "📊 Dashboard Management",
        "🏊 Klasifikasi Data Siswa per Kolam",
        "📊 Download Spreadsheet Rekapan (Multi-Sheet)",
        "💵 Laporan Arus Kas Khusus",
        "💳 Keuangan & Latihan Siswa",
        "📝 Absensi Pelatih",
        "📈 Progres Siswa",
        "💰 Penggajian & WA Laporan",
        "👥 Kelola & Hapus Data Pelatih",
        "🏊 Kelola & Hapus Data Siswa",
        "🔑 Pengaturan Akun System"
    ]
else:
    # Akses PELATIH (Ringkas & Terfokus)
    menu_options = [
        "📝 Absensi Pelatih",
        "📈 Progres Siswa"
    ]

selected_menu = st.sidebar.radio("Pilih Menu:", menu_options)

if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.rerun()

# ==========================================
# 6. MODULE IMPLEMENTATION
# ==========================================

# ------------------------------------------
# MENU: Dashboard Management (ADMIN)
# ------------------------------------------
if selected_menu == "📊 Dashboard Management":
    st.title("📊 Dashboard Management")
    
    col1, col2, col3, col4 = st.columns(4)
    active_students = len(st.session_state.data_siswa[st.session_state.data_siswa['Status'] == 'Aktif'])
    total_income = st.session_state.pembayaran_spp['Jumlah Bayar'].sum()
    total_sessions = st.session_state.absensi_pelatih['Jumlah Sesi'].sum()
    total_expense = st.session_state.pengeluaran_ops['Nominal'].sum()
    
    col1.metric("Siswa Aktif", f"{active_students} Orang")
    col2.metric("Total Pemasukan SPP", f"Rp {total_income:,.0f}")
    col3.metric("Total Sesi Pelatih", f"{total_sessions} Sesi")
    col4.metric("Total Pengeluaran Ops", f"Rp {total_expense:,.0f}")
    
    st.markdown("---")
    st.subheader("📈 Aktivitas & Transaksi Terbaru")
    
    tab1, tab2 = st.tabs(["Rekap Absensi Pelatih", "Pembayaran SPP Terbaru"])
    
    with tab1:
        st.dataframe(st.session_state.absensi_pelatih, use_container_width=True)
        download_csv_button(st.session_state.absensi_pelatih, "dashboard_absensi_pelatih.csv", "dash_abs_plt")
        
    with tab2:
        st.dataframe(st.session_state.pembayaran_spp, use_container_width=True)
        download_csv_button(st.session_state.pembayaran_spp, "dashboard_pembayaran_spp.csv", "dash_spp")

# ------------------------------------------
# MENU: Klasifikasi Data Siswa per Kolam
# ------------------------------------------
elif selected_menu == "🏊 Klasifikasi Data Siswa per Kolam":
    st.title("🏊 Klasifikasi Data Siswa per Lokasi Kolam")
    
    df_siswa = st.session_state.data_siswa
    available_pools = list(df_siswa['Lokasi Kolam'].unique())
    
    selected_pool = st.selectbox("🔍 Pilih Lokasi Kolam:", ["Semua Kolam"] + available_pools)
    
    if selected_pool != "Semua Kolam":
        filtered_df = df_siswa[df_siswa['Lokasi Kolam'] == selected_pool]
    else:
        filtered_df = df_siswa.copy()
        
    st.markdown("### 📊 Ringkasan Statistik Kolam")
    c1, c2, c3 = st.columns(3)
    c1.metric("Jumlah Siswa Aktif", len(filtered_df[filtered_df['Status'] == 'Aktif']))
    
    # Sesi latihan di kolam ini
    if selected_pool != "Semua Kolam":
        sessions_cnt = st.session_state.absensi_siswa[st.session_state.absensi_siswa['Kolam'] == selected_pool].shape[0]
        coaches = st.session_state.absensi_pelatih[st.session_state.absensi_pelatih['Kolam'] == selected_pool]['Nama Pelatih'].nunique()
    else:
        sessions_cnt = len(st.session_state.absensi_siswa)
        coaches = st.session_state.data_pelatih['Nama Pelatih'].nunique()
        
    c2.metric("Total Sesi Latihan", f"{sessions_cnt} Sesi")
    c3.metric("Pelatih Bertugas", f"{coaches} Orang")
    
    st.subheader(f"Tabel Siswa - {selected_pool}")
    st.dataframe(filtered_df, use_container_width=True)
    download_csv_button(filtered_df, f"siswa_kolam_{selected_pool}.csv", "dl_csv_kolam")

# ------------------------------------------
# MENU: Download Spreadsheet Rekapan (Multi-Sheet)
# ------------------------------------------
elif selected_menu == "📊 Download Spreadsheet Rekapan (Multi-Sheet)":
    st.title("📊 Download Spreadsheet Rekapan (Multi-Sheet)")
    st.write("Unduh seluruh database sistem manajemen Megalodon Aquatic dalam 1 file Microsoft Excel (.xlsx) dengan sheet terpisah.")
    
    # Kalkulasi rekap gaji untuk sheet ke-8
    payroll_df = st.session_state.data_pelatih.copy()
    payroll_df = payroll_df.merge(
        st.session_state.absensi_pelatih.groupby("Nama Pelatih")["Jumlah Sesi"].sum().reset_index(),
        on="Nama Pelatih", how="left"
    ).fillna(0)
    payroll_df["Total Gaji"] = payroll_df["Jumlah Sesi"] * payroll_df["Tarif/Sesi"]

    all_sheets = {
        "Master Siswa": st.session_state.data_siswa,
        "Master Pelatih": st.session_state.data_pelatih,
        "Absensi Siswa": st.session_state.absensi_siswa,
        "Absensi Pelatih": st.session_state.absensi_pelatih,
        "Pembayaran SPP": st.session_state.pembayaran_spp,
        "Pengeluaran Ops": st.session_state.pengeluaran_ops,
        "Progres Siswa": st.session_state.progres_siswa,
        "Rekap Gaji Payroll": payroll_df
    }
    
    excel_file = generate_multi_sheet_excel(all_sheets)
    st.download_button(
        label="🟢 Download Full Database Excel (.XLSX)",
        data=excel_file,
        file_name=f"Megalodon_Full_Database_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ------------------------------------------
# MENU: Laporan Arus Kas Khusus
# ------------------------------------------
elif selected_menu == "💵 Laporan Arus Kas Khusus":
    st.title("💵 Laporan Arus Kas (Cashflow)")
    
    tab1, tab2 = st.tabs(["Ringkasan Arus Kas", "Input Pengeluaran Ops"])
    
    with tab1:
        inflow = st.session_state.pembayaran_spp['Jumlah Bayar'].sum()
        outflow_ops = st.session_state.pengeluaran_ops['Nominal'].sum()
        
        # Outflow gaji
        payroll_merged = st.session_state.absensi_pelatih.merge(st.session_state.data_pelatih, on="Nama Pelatih")
        outflow_gaji = (payroll_merged['Jumlah Sesi'] * payroll_merged['Tarif/Sesi']).sum()
        
        total_outflow = outflow_ops + outflow_gaji
        net_cashflow = inflow - total_outflow
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Cash Inflow (SPP)", f"Rp {inflow:,.0f}")
        c2.metric("Cash Outflow (Ops + Gaji)", f"Rp {total_outflow:,.0f}")
        c3.metric("Net Cashflow", f"Rp {net_cashflow:,.0f}")
        
        st.subheader("Rincian Cash Inflow (Penerimaan SPP)")
        st.dataframe(st.session_state.pembayaran_spp, use_container_width=True)
        download_csv_button(st.session_state.pembayaran_spp, "cash_inflow.csv", "dl_inflow")
        
        st.subheader("Rincian Cash Outflow (Pengeluaran Ops)")
        st.dataframe(st.session_state.pengeluaran_ops, use_container_width=True)
        download_csv_button(st.session_state.pengeluaran_ops, "cash_outflow_ops.csv", "dl_outflow")
        
    with tab2:
        st.subheader("Form Input Pengeluaran Operational")
        with st.form("form_ops"):
            tgl = st.date_input("Tanggal", datetime.now())
            kat = st.selectbox("Kategori", ["Sewa Kolam", "Alat & Perlengkapan", "Gaji Staff", "Lain-lain"])
            nom = st.number_input("Nominal (Rp)", min_value=0, step=10000)
            ket = st.text_input("Keterangan")
            
            if st.form_submit_button("Simpan Pengeluaran"):
                new_row = {"Tanggal": str(tgl), "Kategori": kat, "Nominal": nom, "Keterangan": ket}
                st.session_state.pengeluaran_ops = pd.concat([st.session_state.pengeluaran_ops, pd.DataFrame([new_row])], ignore_index=True)
                st.success("Data pengeluaran berhasil disimpan!")
                st.rerun()

# ------------------------------------------
# MENU: Keuangan & Latihan Siswa
# ------------------------------------------
elif selected_menu == "💳 Keuangan & Latihan Siswa":
    st.title("💳 Keuangan & Latihan Siswa")
    
    tab1, tab2, tab3 = st.tabs(["Input Pembayaran SPP", "Input Latihan Siswa", "Kirim Raport & WA"])
    
    with tab1:
        st.subheader("Input Pembayaran SPP (Tambah Kuota)")
        siswa_list = st.session_state.data_siswa['Nama Siswa'].tolist()
        selected_siswa = st.selectbox("Pilih Siswa:", siswa_list, key="spp_siswa")
        
        with st.form("form_spp"):
            tgl = st.date_input("Tanggal Pembayaran", datetime.now())
            jml = st.number_input("Jumlah Bayar (Rp)", min_value=0, value=500000, step=50000)
            kuota = st.number_input("Tambahan Kuota Sesi", min_value=1, value=4, step=1)
            metode = st.selectbox("Metode Pembayaran", ["Transfer", "Tunai"])
            
            if st.form_submit_button("Proses Pembayaran"):
                # Update Kuota
                idx = st.session_state.data_siswa[st.session_state.data_siswa['Nama Siswa'] == selected_siswa].index
                st.session_state.data_siswa.loc[idx, 'Sisa Kuota'] += kuota
                st.session_state.data_siswa.loc[idx, 'Status'] = 'Aktif'
                
                # Record Pembayaran
                siswa_id = st.session_state.data_siswa.loc[idx[0], 'ID Siswa']
                new_pay = {"Tanggal": str(tgl), "ID Siswa": siswa_id, "Nama Siswa": selected_siswa, "Jumlah Bayar": jml, "Tambahan Kuota": kuota, "Metode": metode}
                st.session_state.pembayaran_spp = pd.concat([st.session_state.pembayaran_spp, pd.DataFrame([new_pay])], ignore_index=True)
                
                st.success(f"Pembayaran berhasil! Kuota {selected_siswa} bertambah {kuota} sesi.")
                st.rerun()
                
        st.dataframe(st.session_state.pembayaran_spp, use_container_width=True)
        download_csv_button(st.session_state.pembayaran_spp, "pembayaran_spp.csv", "dl_spp_menu")

    with tab2:
        st.subheader("Input Kehadiran Latihan Siswa")
        pool_options = st.session_state.data_siswa['Lokasi Kolam'].unique().tolist()
        filter_kolam_lat = st.selectbox("Filter Siswa Berdasarkan Kolam:", ["Semua"] + pool_options)
        
        if filter_kolam_lat != "Semua":
            filtered_siswa_list = st.session_state.data_siswa[st.session_state.data_siswa['Lokasi Kolam'] == filter_kolam_lat]['Nama Siswa'].tolist()
        else:
            filtered_siswa_list = st.session_state.data_siswa['Nama Siswa'].tolist()
            
        with st.form("form_latihan"):
            tgl_lat = st.date_input("Tanggal Latihan", datetime.now())
            nama_s = st.selectbox("Pilih Siswa", filtered_siswa_list)
            
            # Ambil lokasi default siswa
            siswa_row = st.session_state.data_siswa[st.session_state.data_siswa['Nama Siswa'] == nama_s]
            default_pool = siswa_row.iloc[0]['Lokasi Kolam'] if not siswa_row.empty else ""
            
            kolam_lat = st.text_input("Lokasi Kolam", value=default_pool)
            pelatih_lat = st.selectbox("Pelatih Bertugas", st.session_state.data_pelatih['Nama Pelatih'].tolist())
            materi_lat = st.text_input("Materi Latihan", "Latihan Gaya Bebas & Water Trappen")
            
            if st.form_submit_button("Simpan Latihan & Potong Kuota"):
                idx = st.session_state.data_siswa[st.session_state.data_siswa['Nama Siswa'] == nama_s].index
                current_kuota = st.session_state.data_siswa.loc[idx[0], 'Sisa Kuota']
                
                if current_kuota > 0:
                    st.session_state.data_siswa.loc[idx[0], 'Sisa Kuota'] -= 1
                    s_id = st.session_state.data_siswa.loc[idx[0], 'ID Siswa']
                    
                    new_abs = {"Tanggal": str(tgl_lat), "ID Siswa": s_id, "Nama Siswa": nama_s, "Kolam": kolam_lat, "Pelatih": pelatih_lat, "Materi": materi_lat}
                    st.session_state.absensi_siswa = pd.concat([st.session_state.absensi_siswa, pd.DataFrame([new_abs])], ignore_index=True)
                    st.success("Absensi latihan berhasil dicatat. Sisa kuota berkurang 1.")
                    st.rerun()
                else:
                    st.error("Kuota siswa ini sudah habis! Silakan lakukan pembayaran SPP terlebih dahulu.")

        st.dataframe(st.session_state.absensi_siswa, use_container_width=True)
        download_csv_button(st.session_state.absensi_siswa, "absensi_siswa.csv", "dl_abs_siswa")

    with tab3:
        st.subheader("Generate Raport PDF & Template WhatsApp Editable")
        selected_s = st.selectbox("Pilih Siswa untuk Raport/WA:", st.session_state.data_siswa['Nama Siswa'].tolist(), key="wa_siswa")
        
        s_data = st.session_state.data_siswa[st.session_state.data_siswa['Nama Siswa'] == selected_s].iloc[0]
        s_prog = st.session_state.progres_siswa[st.session_state.progres_siswa['Nama Siswa'] == selected_s]
        
        last_lat = st.session_state.absensi_siswa[st.session_state.absensi_siswa['Nama Siswa'] == selected_s]
        tgl_terakhir = last_lat.iloc[-1]['Tanggal'] if not last_lat.empty else "Belum Ada"
        
        default_wa_text = f"""Halo Orang Tua dari *{selected_s}*,

Berikut ringkasan progres latihan renang di Megalodon Aquatic:
- **Lokasi Kolam:** {s_data['Lokasi Kolam']}
- **Sisa Kuota Latihan:** {s_data['Sisa Kuota']} Sesi
- **Latihan Terakhir:** {tgl_terakhir}

Terima kasih atas kepercayaannya! 🏊✨"""
        
        edited_wa_text = st.text_area("Template Pesan WhatsApp (Editable):", value=default_wa_text, height=180)
        
        phone_number = re.sub(r'\D', '', str(s_data['No HP']))
        encoded_text = pd.Series([edited_wa_text]).astype(str).str.replace('\n', '%0A').iloc[0]
        wa_url = f"https://wa.me/{phone_number}?text={encoded_text}"
        
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; font-weight:bold;">📱 Kirim Laporan via WhatsApp</button></a>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Download Raport PDF")
        if not s_prog.empty:
            stats = {
                "Meluncur": s_prog.iloc[0]['Meluncur'],
                "Gaya Bebas": s_prog.iloc[0]['Gaya Bebas'],
                "Gaya Dada": s_prog.iloc[0]['Gaya Dada'],
                "Gaya Punggung": s_prog.iloc[0]['Gaya Punggung'],
                "Gaya Kupu": s_prog.iloc[0]['Gaya Kupu'],
            }
            pdf_bytes = generate_pdf_raport(selected_s, "Coach Megalodon", s_data['Lokasi Kolam'], stats)
            st.download_button(
                label="📄 Download Raport PDF Siswa",
                data=pdf_bytes,
                file_name=f"Raport_{selected_s}.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("Data nilai progres untuk siswa ini belum diisi!")

# ------------------------------------------
# MENU: Absensi Pelatih (ADMIN & PELATIH)
# ------------------------------------------
elif selected_menu == "📝 Absensi Pelatih":
    st.title("📝 Absensi Pelatih")
    
    st.subheader("Form Input Absensi Latihan Pelatih")
    with st.form("form_abs_pelatih"):
        tgl_p = st.date_input("Tanggal", datetime.now())
        
        if st.session_state.user_role == "PELATIH":
            nama_p = st.text_input("Nama Pelatih", value=st.session_state.username, disabled=True)
        else:
            nama_p = st.selectbox("Nama Pelatih", st.session_state.data_pelatih['Nama Pelatih'].tolist())
            
        # Field Kolam menggunakan INPUT TEXT MANUAL
        kolam_p = st.text_input("Nama / Lokasi Kolam (Manual Input)", "Kolam Cilandak")
        sesi_p = st.number_input("Jumlah Sesi Mengajar", min_value=1, max_value=10, value=1)
        ket_p = st.text_input("Keterangan", "Latihan Reguler")
        
        if st.form_submit_button("Simpan Absensi Pelatih"):
            plt_id = st.session_state.data_pelatih[st.session_state.data_pelatih['Nama Pelatih'] == nama_p]
            id_val = plt_id.iloc[0]['ID Pelatih'] if not plt_id.empty else "PLT-UNKNOWN"
            
            new_abs_p = {
                "Tanggal": str(tgl_p),
                "ID Pelatih": id_val,
                "Nama Pelatih": nama_p,
                "Kolam": kolam_p,
                "Jumlah Sesi": sesi_p,
                "Keterangan": ket_p
            }
            st.session_state.absensi_pelatih = pd.concat([st.session_state.absensi_pelatih, pd.DataFrame([new_abs_p])], ignore_index=True)
            st.success("Absensi pelatih berhasil dicatat!")
            st.rerun()

    st.markdown("---")
    st.subheader("Riwayat Absensi Pelatih")
    st.dataframe(st.session_state.absensi_pelatih, use_container_width=True)
    download_csv_button(st.session_state.absensi_pelatih, "absensi_pelatih.csv", "dl_abs_plt_menu")

# ------------------------------------------
# MENU: Progres Siswa (ADMIN & PELATIH)
# ------------------------------------------
elif selected_menu == "📈 Progres Siswa":
    st.title("📈 Evaluation & Progres Teknik Renang Siswa")
    
    st.subheader("Edit Data Nilai Progres (Direct Table Editor)")
    edited_progres = st.data_editor(
        st.session_state.progres_siswa,
        num_rows="dynamic",
        use_container_width=True,
        key="prog_editor"
    )
    st.session_state.progres_siswa = edited_progres
    
    download_csv_button(st.session_state.progres_siswa, "progres_siswa.csv", "dl_prog_siswa")
    
    st.markdown("---")
    st.subheader("Rata-Rata Nilai Evaluasi Siswa")
    df_calc = st.session_state.progres_siswa.copy()
    skill_cols = ["Meluncur", "Gaya Bebas", "Gaya Dada", "Gaya Punggung", "Gaya Kupu"]
    
    if not df_calc.empty:
        df_calc['Rata-Rata'] = df_calc[skill_cols].mean(axis=1)
        st.dataframe(df_calc[['ID Siswa', 'Nama Siswa', 'Rata-Rata']], use_container_width=True)

# ------------------------------------------
# MENU: Penggajian & WA Laporan (ADMIN)
# ------------------------------------------
elif selected_menu == "💰 Penggajian & WA Laporan":
    st.title("💰 Penggajian Pelatih & Slip Gaji WA")
    
    # Hitung Payroll
    payroll_df = st.session_state.data_pelatih.copy()
    sesi_rekap = st.session_state.absensi_pelatih.groupby("Nama Pelatih")["Jumlah Sesi"].sum().reset_index()
    payroll_df = payroll_df.merge(sesi_rekap, on="Nama Pelatih", how="left").fillna({"Jumlah Sesi": 0})
    payroll_df["Total Gaji"] = payroll_df["Jumlah Sesi"] * payroll_df["Tarif/Sesi"]
    
    st.subheader("Tabel Rekapitulasi Payroll Gaji Pelatih")
    st.dataframe(payroll_df, use_container_width=True)
    download_csv_button(payroll_df, "rekap_payroll_gaji.csv", "dl_payroll")
    
    st.markdown("---")
    st.subheader("Kirim Slip Gaji via WhatsApp")
    selected_plt = st.selectbox("Pilih Pelatih:", payroll_df['Nama Pelatih'].tolist())
    p_data = payroll_df[payroll_df['Nama Pelatih'] == selected_plt].iloc[0]
    
    default_slip = f"""Yth. *{p_data['Nama Pelatih']}*,

Berikut adalah Rincian Slip Gaji Mengajar Anda:
- **Total Sesi Mengajar:** {p_data['Jumlah Sesi']} Sesi
- **Tarif Per Sesi:** Rp {p_data['Tarif/Sesi']:,.0f}
- **Total Take Home Pay:** Rp {p_data['Total Gaji']:,.0f}

Terima kasih atas dedikasi Anda di Megalodon Aquatic! 🏊‍♂️"""
    
    edited_slip = st.text_area("Template Slip Gaji WA (Editable):", value=default_slip, height=180)
    
    p_phone = re.sub(r'\D', '', str(p_data['No HP']))
    encoded_slip = pd.Series([edited_slip]).astype(str).str.replace('\n', '%0A').iloc[0]
    wa_slip_url = f"https://wa.me/{p_phone}?text={encoded_slip}"
    
    st.markdown(f'<a href="{wa_slip_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; font-weight:bold;">📱 Kirim Slip Gaji via WA</button></a>', unsafe_allow_html=True)

# ------------------------------------------
# MENU: Kelola & Hapus Data Pelatih (ADMIN)
# ------------------------------------------
elif selected_menu == "👥 Kelola & Hapus Data Pelatih":
    st.title("👥 Kelola Master Data Pelatih")
    
    tab1, tab2 = st.tabs(["Daftar & Edit Pelatih", "Tambah Pelatih Baru"])
    
    with tab1:
        edited_plt = st.data_editor(
            st.session_state.data_pelatih,
            num_rows="dynamic",
            use_container_width=True,
            key="plt_editor"
        )
        st.session_state.data_pelatih = edited_plt
        download_csv_button(st.session_state.data_pelatih, "master_data_pelatih.csv", "dl_master_plt")
        
    with tab2:
        with st.form("form_add_plt"):
            new_id = f"PLT-00{len(st.session_state.data_pelatih)+1}"
            st.text_input("ID Pelatih (Auto)", value=new_id, disabled=True)
            nama = st.text_input("Nama Lengkap Pelatih")
            hp = st.text_input("No HP (WhatsApp)", "628")
            tarif = st.number_input("Tarif per Sesi (Rp)", value=100000, step=10000)
            status = st.selectbox("Status", ["Aktif", "Cuti"])
            
            if st.form_submit_button("Tambah Pelatih"):
                new_row = {"ID Pelatih": new_id, "Nama Pelatih": nama, "No HP": hp, "Tarif/Sesi": tarif, "Status": status}
                st.session_state.data_pelatih = pd.concat([st.session_state.data_pelatih, pd.DataFrame([new_row])], ignore_index=True)
                st.success("Pelatih baru berhasil ditambahkan!")
                st.rerun()

# ------------------------------------------
# MENU: Kelola & Hapus Data Siswa (ADMIN)
# ------------------------------------------
elif selected_menu == "🏊 Kelola & Hapus Data Siswa":
    st.title("🏊 Kelola Master Data Siswa")
    
    tab1, tab2 = st.tabs(["Daftar & Edit Siswa", "Tambah Siswa Baru"])
    
    with tab1:
        edited_siswa = st.data_editor(
            st.session_state.data_siswa,
            num_rows="dynamic",
            use_container_width=True,
            key="siswa_editor"
        )
        st.session_state.data_siswa = edited_siswa
        download_csv_button(st.session_state.data_siswa, "master_data_siswa.csv", "dl_master_siswa")
        
    with tab2:
        with st.form("form_add_siswa"):
            new_id_s = f"SSW-00{len(st.session_state.data_siswa)+1}"
            st.text_input("ID Siswa (Auto)", value=new_id_s, disabled=True)
            nama_s = st.text_input("Nama Lengkap Siswa")
            hp_s = st.text_input("No HP (WhatsApp Orang Tua)", "628")
            kolam_s = st.text_input("Lokasi Kolam Utama", "Kolam Cilandak")
            kuota_s = st.number_input("Kuota Initial Latihan", value=4, step=1)
            status_s = st.selectbox("Status Siswa", ["Aktif", "Non-Aktif"])
            
            if st.form_submit_button("Tambah Siswa"):
                new_row_s = {
                    "ID Siswa": new_id_s, 
                    "Nama Siswa": nama_s, 
                    "No HP": hp_s, 
                    "Lokasi Kolam": kolam_s, 
                    "Sisa Kuota": kuota_s, 
                    "Status": status_s
                }
                st.session_state.data_siswa = pd.concat([st.session_state.data_siswa, pd.DataFrame([new_row_s])], ignore_index=True)
                
                # Inisialisasi tabel progres siswa
                new_prog = {"ID Siswa": new_id_s, "Nama Siswa": nama_s, "Meluncur": 0, "Gaya Bebas": 0, "Gaya Dada": 0, "Gaya Punggung": 0, "Gaya Kupu": 0}
                st.session_state.progres_siswa = pd.concat([st.session_state.progres_siswa, pd.DataFrame([new_prog])], ignore_index=True)
                
                st.success("Siswa baru berhasil ditambahkan!")
                st.rerun()

# ------------------------------------------
# MENU: Pengaturan Akun System (ADMIN)
# ------------------------------------------
elif selected_menu == "🔑 Pengaturan Akun System":
    st.title("🔑 Kelola Akun Login Sistem")
    
    st.subheader("Daftar User & Role System")
    edited_users = st.data_editor(
        st.session_state.users,
        num_rows="dynamic",
        use_container_width=True,
        key="users_editor"
    )
    st.session_state.users = edited_users
    download_csv_button(st.session_state.users, "accounts_system.csv", "dl_users")