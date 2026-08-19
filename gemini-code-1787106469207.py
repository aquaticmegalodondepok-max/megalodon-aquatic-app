import streamlit as st
import pandas as pd
import numpy as np
import io
import re
from datetime import datetime

# --- REPORTLAB IMPORTS FOR PDF GENERATION ---
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
# 2. HELPER FUNCTIONS: EXPORT CSV, EXCEL, PDF
# ==========================================
@st.cache_data
def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Konversi DataFrame ke CSV"""
    return df.to_csv(index=False).encode('utf-8')

def convert_df_to_excel(df: pd.DataFrame) -> bytes:
    """Konversi single DataFrame ke Excel"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Data_Laporan")
    output.seek(0)
    return output.getvalue()

def generate_pdf_report(title: str, df: pd.DataFrame) -> io.BytesIO:
    """Membuat laporan PDF dari DataFrame secara dinamis"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#0F7B5F'),
        alignment=1,
        spaceAfter=12
    )
    
    story = []
    story.append(Paragraph("MEGALODON AQUATIC SWIMMING ACADEMY", title_style))
    story.append(Paragraph(f"<b>LAPORAN: {title.upper()}</b>", styles['Heading2']))
    story.append(Paragraph(f"Tanggal Cetak: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    if not df.empty:
        # Batasi kolom jika terlalu banyak
        disp_df = df.iloc[:, :6].copy()
        table_data = [disp_df.columns.tolist()] + disp_df.astype(str).values.tolist()
        
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F7B5F')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("Tidak ada data untuk ditampilkan.", styles['Normal']))
        
    doc.build(story)
    buffer.seek(0)
    return buffer

def render_export_toolbar(df: pd.DataFrame, report_name: str, key_prefix: str):
    """Menampilkan 3 opsi cetak/download universal dalam 1 baris"""
    st.markdown("##### 🖨️ Cetak / Unduh Laporan")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.download_button(
            label="📥 Download CSV",
            data=convert_df_to_csv(df),
            file_name=f"{report_name}.csv",
            mime="text/csv",
            key=f"{key_prefix}_csv",
            use_container_width=True
        )
    with c2:
        st.download_button(
            label="🟢 Download Excel (.xlsx)",
            data=convert_df_to_excel(df),
            file_name=f"{report_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"{key_prefix}_xlsx",
            use_container_width=True
        )
    with c3:
        pdf_file = generate_pdf_report(report_name, df)
        st.download_button(
            label="📄 Cetak PDF Laporan",
            data=pdf_file,
            file_name=f"{report_name}.pdf",
            mime="application/pdf",
            key=f"{key_prefix}_pdf",
            use_container_width=True
        )

def generate_multi_sheet_excel(data_dict):
    """Membuat file .xlsx multi-sheet"""
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

# Master Data Siswa
if 'data_siswa' not in st.session_state:
    st.session_state.data_siswa = pd.DataFrame([
        {"ID Siswa": "SSW-001", "Nama Siswa": "Budi Santoso", "No HP": "628123456789", "Lokasi Kolam": "Kolam Cilandak", "Sisa Kuota": 4, "Status": "Aktif"},
        {"ID Siswa": "SSW-002", "Nama Siswa": "Siti Aminah", "No HP": "628987654321", "Lokasi Kolam": "Kolam GBK", "Sisa Kuota": 2, "Status": "Aktif"},
        {"ID Siswa": "SSW-003", "Nama Siswa": "Ahmad Dani", "No HP": "628111222333", "Lokasi Kolam": "Kolam Cilandak", "Sisa Kuota": 0, "Status": "Non-Aktif"},
    ])

# Master Data Pelatih
if 'data_pelatih' not in st.session_state:
    st.session_state.data_pelatih = pd.DataFrame([
        {"ID Pelatih": "PLT-001", "Nama Pelatih": "Coach Anton", "No HP": "628555666777", "Tarif/Sesi": 100000, "Status": "Aktif"},
        {"ID Pelatih": "PLT-002", "Nama Pelatih": "Coach Bella", "No HP": "628444333222", "Tarif/Sesi": 120000, "Status": "Aktif"},
    ])

# Absensi Pelatih
if 'absensi_pelatih' not in st.session_state:
    st.session_state.absensi_pelatih = pd.DataFrame([
        {"Tanggal": "2026-08-01", "ID Pelatih": "PLT-001", "Nama Pelatih": "Coach Anton", "Kolam": "Kolam Cilandak", "Jumlah Sesi": 2, "Keterangan": "Hadir"},
        {"Tanggal": "2026-08-02", "ID Pelatih": "PLT-002", "Nama Pelatih": "Coach Bella", "Kolam": "Kolam GBK", "Jumlah Sesi": 1, "Keterangan": "Hadir"},
    ])

# Absensi Siswa
if 'absensi_siswa' not in st.session_state:
    st.session_state.absensi_siswa = pd.DataFrame([
        {"Tanggal": "2026-08-01", "ID Siswa": "SSW-001", "Nama Siswa": "Budi Santoso", "Kolam": "Kolam Cilandak", "Pelatih": "Coach Anton", "Materi": "Gaya Bebas"},
    ])

# Pembayaran SPP
if 'pembayaran_spp' not in st.session_state:
    st.session_state.pembayaran_spp = pd.DataFrame([
        {"Tanggal": "2026-08-01", "ID Siswa": "SSW-001", "Nama Siswa": "Budi Santoso", "Jumlah Bayar": 500000, "Tambahan Kuota": 4, "Metode": "Transfer"},
    ])

# Pengeluaran Operasional
if 'pengeluaran_ops' not in st.session_state:
    st.session_state.pengeluaran_ops = pd.DataFrame([
        {"Tanggal": "2026-08-01", "Kategori": "Sewa Kolam", "Nominal": 200000, "Keterangan": "Sewa jalur Cilandak"},
    ])

# Progres Siswa
if 'progres_siswa' not in st.session_state:
    st.session_state.progres_siswa = pd.DataFrame([
        {"ID Siswa": "SSW-001", "Nama Siswa": "Budi Santoso", "Meluncur": 85, "Gaya Bebas": 80, "Gaya Dada": 75, "Gaya Punggung": 70, "Gaya Kupu": 60},
    ])

# Account Management
if 'users' not in st.session_state:
    st.session_state.users = pd.DataFrame([
        {"Username": "admin", "Password": "123", "Role": "ADMIN"},
        {"Username": "pelatih", "Password": "123", "Role": "PELATIH"},
    ])

# Custom Dynamic Menus (Integrasi Menu Baru oleh Admin)
if 'custom_menus' not in st.session_state:
    st.session_state.custom_menus = {
        # Contoh Menu Kustom Bawaan Admin
        "📌 Catatan Khusus Lomba": {
            "role_access": ["ADMIN", "PELATIH"],
            "type": "Table & Notes",
            "data": pd.DataFrame([
                {"Tanggal": "2026-08-10", "Siswa": "Budi Santoso", "Target Lomba": "Kejurda 50m Gaya Bebas", "Status Readiness": "80%"},
            ])
        }
    }

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
# 5. SIDEBAR NAVIGATION & INTEGRATED RBAC
# ==========================================
st.sidebar.title("🏊 Megalodon System")
st.sidebar.write(f"Logged in: **{st.session_state.username}** (`{st.session_state.user_role}`)")

# Standard Menus
if st.session_state.user_role == "ADMIN":
    standard_menus = [
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
        "⚙️ Kelola Menu Kustom (Admin Only)",
        "🔑 Pengaturan Akun System"
    ]
else:
    standard_menus = [
        "📝 Absensi Pelatih",
        "📈 Progres Siswa"
    ]

# Menggabungkan Standard Menu + Custom Dynamic Menus sesuai Izin Access
accessible_custom_menus = [
    menu_name for menu_name, meta in st.session_state.custom_menus.items()
    if st.session_state.user_role in meta["role_access"]
]

all_menu_options = standard_menus + accessible_custom_menus
selected_menu = st.sidebar.radio("Pilih Menu:", all_menu_options)

if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.rerun()

# ==========================================
# 6. MODULE IMPLEMENTATIONS
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
        render_export_toolbar(st.session_state.absensi_pelatih, "Dashboard_Absensi_Pelatih", "dash_abs")
        
    with tab2:
        st.dataframe(st.session_state.pembayaran_spp, use_container_width=True)
        render_export_toolbar(st.session_state.pembayaran_spp, "Dashboard_Pembayaran_SPP", "dash_spp")

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
        
    c1, c2, c3 = st.columns(3)
    c1.metric("Jumlah Siswa Aktif", len(filtered_df[filtered_df['Status'] == 'Aktif']))
    sessions_cnt = len(st.session_state.absensi_siswa[st.session_state.absensi_siswa['Kolam'] == selected_pool]) if selected_pool != "Semua Kolam" else len(st.session_state.absensi_siswa)
    c2.metric("Total Sesi Latihan", f"{sessions_cnt} Sesi")
    c3.metric("Pelatih Bertugas", f"{st.session_state.data_pelatih['Nama Pelatih'].nunique()} Orang")
    
    st.subheader(f"Tabel Siswa - {selected_pool}")
    st.dataframe(filtered_df, use_container_width=True)
    render_export_toolbar(filtered_df, f"Siswa_Kolam_{selected_pool}", "klasifikasi_kolam")

# ------------------------------------------
# MENU: Download Spreadsheet Rekapan (Multi-Sheet)
# ------------------------------------------
elif selected_menu == "📊 Download Spreadsheet Rekapan (Multi-Sheet)":
    st.title("📊 Download Spreadsheet Rekapan (Multi-Sheet)")
    st.write("Unduh seluruh database sistem dalam 1 file Microsoft Excel (.xlsx) berisi 8+ sheet terpisah.")
    
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
    
    # Tambahkan custom dynamic menus jika ada
    for c_name, c_meta in st.session_state.custom_menus.items():
        if isinstance(c_meta["data"], pd.DataFrame):
            clean_sheet_name = re.sub(r'[^\w\s]', '', c_name)[:30]
            all_sheets[clean_sheet_name] = c_meta["data"]

    excel_file = generate_multi_sheet_excel(all_sheets)
    st.download_button(
        label="🟢 Download Full Database Excel Multi-Sheet (.XLSX)",
        data=excel_file,
        file_name=f"Megalodon_Full_Database_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
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
        render_export_toolbar(st.session_state.pembayaran_spp, "Cash_Inflow_SPP", "inflow_spp")
        
        st.subheader("Rincian Cash Outflow (Pengeluaran Ops)")
        st.dataframe(st.session_state.pengeluaran_ops, use_container_width=True)
        render_export_toolbar(st.session_state.pengeluaran_ops, "Cash_Outflow_Ops", "outflow_ops")
        
    with tab2:
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
                idx = st.session_state.data_siswa[st.session_state.data_siswa['Nama Siswa'] == selected_siswa].index
                st.session_state.data_siswa.loc[idx, 'Sisa Kuota'] += kuota
                st.session_state.data_siswa.loc[idx, 'Status'] = 'Aktif'
                
                siswa_id = st.session_state.data_siswa.loc[idx[0], 'ID Siswa']
                new_pay = {"Tanggal": str(tgl), "ID Siswa": siswa_id, "Nama Siswa": selected_siswa, "Jumlah Bayar": jml, "Tambahan Kuota": kuota, "Metode": metode}
                st.session_state.pembayaran_spp = pd.concat([st.session_state.pembayaran_spp, pd.DataFrame([new_pay])], ignore_index=True)
                st.success(f"Pembayaran berhasil! Kuota {selected_siswa} bertambah {kuota} sesi.")
                st.rerun()
                
        st.dataframe(st.session_state.pembayaran_spp, use_container_width=True)
        render_export_toolbar(st.session_state.pembayaran_spp, "Laporan_Pembayaran_SPP", "pembayaran_spp")

    with tab2:
        st.subheader("Input Kehadiran Latihan Siswa")
        pool_options = st.session_state.data_siswa['Lokasi Kolam'].unique().tolist()
        filter_kolam_lat = st.selectbox("Filter Siswa Berdasarkan Kolam:", ["Semua"] + pool_options)
        
        filtered_siswa_list = st.session_state.data_siswa[st.session_state.data_siswa['Lokasi Kolam'] == filter_kolam_lat]['Nama Siswa'].tolist() if filter_kolam_lat != "Semua" else st.session_state.data_siswa['Nama Siswa'].tolist()
            
        with st.form("form_latihan"):
            tgl_lat = st.date_input("Tanggal Latihan", datetime.now())
            nama_s = st.selectbox("Pilih Siswa", filtered_siswa_list)
            
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
                    st.error("Kuota siswa ini sudah habis!")

        st.dataframe(st.session_state.absensi_siswa, use_container_width=True)
        render_export_toolbar(st.session_state.absensi_siswa, "Laporan_Absensi_Siswa", "abs_siswa")

    with tab3:
        st.subheader("Generate Raport PDF & Template WhatsApp Editable")
        selected_s = st.selectbox("Pilih Siswa:", st.session_state.data_siswa['Nama Siswa'].tolist(), key="wa_siswa")
        s_data = st.session_state.data_siswa[st.session_state.data_siswa['Nama Siswa'] == selected_s].iloc[0]
        
        default_wa_text = f"Halo Orang Tua dari *{selected_s}*,\n\nSisa Kuota Latihan: {s_data['Sisa Kuota']} Sesi.\nLokasi Kolam: {s_data['Lokasi Kolam']}."
        edited_wa_text = st.text_area("Template Pesan WhatsApp (Editable):", value=default_wa_text, height=120)
        
        phone_number = re.sub(r'\D', '', str(s_data['No HP']))
        encoded_text = pd.Series([edited_wa_text]).astype(str).str.replace('\n', '%0A').iloc[0]
        st.markdown(f'<a href="https://wa.me/{phone_number}?text={encoded_text}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; font-weight:bold;">📱 Kirim Laporan via WhatsApp</button></a>', unsafe_allow_html=True)

# ------------------------------------------
# MENU: Absensi Pelatih (ADMIN & PELATIH)
# ------------------------------------------
elif selected_menu == "📝 Absensi Pelatih":
    st.title("📝 Absensi Pelatih")
    
    with st.form("form_abs_pelatih"):
        tgl_p = st.date_input("Tanggal", datetime.now())
        nama_p = st.text_input("Nama Pelatih", value=st.session_state.username, disabled=True) if st.session_state.user_role == "PELATIH" else st.selectbox("Nama Pelatih", st.session_state.data_pelatih['Nama Pelatih'].tolist())
        kolam_p = st.text_input("Nama / Lokasi Kolam (Manual Input)", "Kolam Cilandak")
        sesi_p = st.number_input("Jumlah Sesi Mengajar", min_value=1, max_value=10, value=1)
        ket_p = st.text_input("Keterangan", "Latihan Reguler")
        
        if st.form_submit_button("Simpan Absensi Pelatih"):
            plt_id = st.session_state.data_pelatih[st.session_state.data_pelatih['Nama Pelatih'] == nama_p]
            id_val = plt_id.iloc[0]['ID Pelatih'] if not plt_id.empty else "PLT-000"
            
            new_abs_p = {"Tanggal": str(tgl_p), "ID Pelatih": id_val, "Nama Pelatih": nama_p, "Kolam": kolam_p, "Jumlah Sesi": sesi_p, "Keterangan": ket_p}
            st.session_state.absensi_pelatih = pd.concat([st.session_state.absensi_pelatih, pd.DataFrame([new_abs_p])], ignore_index=True)
            st.success("Absensi pelatih berhasil dicatat!")
            st.rerun()

    st.subheader("Riwayat Absensi Pelatih")
    st.dataframe(st.session_state.absensi_pelatih, use_container_width=True)
    render_export_toolbar(st.session_state.absensi_pelatih, "Laporan_Absensi_Pelatih", "abs_plt_menu")

# ------------------------------------------
# MENU: Progres Siswa (ADMIN & PELATIH)
# ------------------------------------------
elif selected_menu == "📈 Progres Siswa":
    st.title("📈 Evaluation & Progres Teknik Renang Siswa")
    
    edited_progres = st.data_editor(st.session_state.progres_siswa, num_rows="dynamic", use_container_width=True, key="prog_editor")
    st.session_state.progres_siswa = edited_progres
    
    render_export_toolbar(st.session_state.progres_siswa, "Laporan_Progres_Siswa", "prog_siswa")

# ------------------------------------------
# MENU: Penggajian & WA Laporan (ADMIN)
# ------------------------------------------
elif selected_menu == "💰 Penggajian & WA Laporan":
    st.title("💰 Penggajian Pelatih & Slip Gaji WA")
    
    payroll_df = st.session_state.data_pelatih.copy()
    sesi_rekap = st.session_state.absensi_pelatih.groupby("Nama Pelatih")["Jumlah Sesi"].sum().reset_index()
    payroll_df = payroll_df.merge(sesi_rekap, on="Nama Pelatih", how="left").fillna({"Jumlah Sesi": 0})
    payroll_df["Total Gaji"] = payroll_df["Jumlah Sesi"] * payroll_df["Tarif/Sesi"]
    
    st.dataframe(payroll_df, use_container_width=True)
    render_export_toolbar(payroll_df, "Rekap_Payroll_Gaji_Pelatih", "payroll_gaji")

# ------------------------------------------
# MENU: Kelola Data Pelatih (ADMIN)
# ------------------------------------------
elif selected_menu == "👥 Kelola & Hapus Data Pelatih":
    st.title("👥 Kelola Master Data Pelatih")
    
    tab1, tab2 = st.tabs(["Daftar & Edit Pelatih", "Tambah Pelatih Baru"])
    with tab1:
        edited_plt = st.data_editor(st.session_state.data_pelatih, num_rows="dynamic", use_container_width=True, key="plt_editor")
        st.session_state.data_pelatih = edited_plt
        render_export_toolbar(st.session_state.data_pelatih, "Master_Data_Pelatih", "master_plt")
    with tab2:
        with st.form("form_add_plt"):
            new_id = f"PLT-00{len(st.session_state.data_pelatih)+1}"
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
# MENU: Kelola Data Siswa (ADMIN)
# ------------------------------------------
elif selected_menu == "🏊 Kelola & Hapus Data Siswa":
    st.title("🏊 Kelola Master Data Siswa")
    
    tab1, tab2 = st.tabs(["Daftar & Edit Siswa", "Tambah Siswa Baru"])
    with tab1:
        edited_siswa = st.data_editor(st.session_state.data_siswa, num_rows="dynamic", use_container_width=True, key="siswa_editor")
        st.session_state.data_siswa = edited_siswa
        render_export_toolbar(st.session_state.data_siswa, "Master_Data_Siswa", "master_siswa")
    with tab2:
        with st.form("form_add_siswa"):
            new_id_s = f"SSW-00{len(st.session_state.data_siswa)+1}"
            nama_s = st.text_input("Nama Lengkap Siswa")
            hp_s = st.text_input("No HP (WhatsApp)", "628")
            kolam_s = st.text_input("Lokasi Kolam Utama", "Kolam Cilandak")
            kuota_s = st.number_input("Kuota Initial Latihan", value=4, step=1)
            status_s = st.selectbox("Status Siswa", ["Aktif", "Non-Aktif"])
            
            if st.form_submit_button("Tambah Siswa"):
                new_row_s = {"ID Siswa": new_id_s, "Nama Siswa": nama_s, "No HP": hp_s, "Lokasi Kolam": kolam_s, "Sisa Kuota": kuota_s, "Status": status_s}
                st.session_state.data_siswa = pd.concat([st.session_state.data_siswa, pd.DataFrame([new_row_s])], ignore_index=True)
                st.success("Siswa baru berhasil ditambahkan!")
                st.rerun()

# ------------------------------------------
# MENU BARU: Kelola Menu Kustom (ADMIN ONLY)
# ------------------------------------------
elif selected_menu == "⚙️ Kelola Menu Kustom (Admin Only)":
    st.title("⚙️ Kelola & Tambah Menu Kustom Baru")
    st.write("Admin dapat menambahkan menu baru dengan pilihan komponen data yang langsung terintegrasi dengan fitur cetak/download.")
    
    tab1, tab2 = st.tabs(["Tambah Menu Baru", "Daftar Menu Kustom Saat Ini"])
    
    with tab1:
        with st.form("form_add_menu"):
            menu_title = st.text_input("Nama Menu Baru (misal: 🏆 Turnamen & Lomba)", "")
            role_access = st.multiselect("Izin Akses Role:", ["ADMIN", "PELATIH"], default=["ADMIN"])
            menu_type = st.selectbox("Tipe Komponen Menu:", ["Table & Notes", "Simple Record Table"])
            initial_columns = st.text_input("Nama Kolom Tabel (pisahkan dengan koma):", "Tanggal, Nama Kegiatan, Lokasi, Catatan")
            
            if st.form_submit_button("🚀 Buat & Integrasikan Menu Baru"):
                if menu_title and initial_columns:
                    cols = [c.strip() for c in initial_columns.split(",")]
                    empty_df = pd.DataFrame(columns=cols)
                    
                    st.session_state.custom_menus[menu_title] = {
                        "role_access": role_access,
                        "type": menu_type,
                        "data": empty_df
                    }
                    st.success(f"Menu '{menu_title}' berhasil dibuat dan langsung terintegrasi di Sidebar!")
                    st.rerun()
                else:
                    st.error("Nama Menu dan Kolom wajib diisi!")
                    
    with tab2:
        st.subheader("Daftar Menu Kustom Terdaftar")
        for m_name, m_meta in list(st.session_state.custom_menus.items()):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"**{m_name}** | Access: `{m_meta['role_access']}` | Type: `{m_meta['type']}`")
            with col_b:
                if st.button(f"🗑️ Hapus Menu", key=f"del_{m_name}"):
                    del st.session_state.custom_menus[m_name]
                    st.success(f"Menu '{m_name}' berhasil dihapus.")
                    st.rerun()

# ------------------------------------------
# MENU: Pengaturan Akun System (ADMIN)
# ------------------------------------------
elif selected_menu == "🔑 Pengaturan Akun System":
    st.title("🔑 Kelola Akun Login System")
    edited_users = st.data_editor(st.session_state.users, num_rows="dynamic", use_container_width=True, key="users_editor")
    st.session_state.users = edited_users
    render_export_toolbar(st.session_state.users, "Data_Pengguna_Sistem", "users_acc")

# ------------------------------------------
# DYNAMIC RENDERER UNTUK CUSTOM MENUS BUATAN ADMIN
# ------------------------------------------
elif selected_menu in st.session_state.custom_menus:
    c_meta = st.session_state.custom_menus[selected_menu]
    st.title(f"{selected_menu}")
    st.info(f"Menu Kustom | Izin Akses: {', '.join(c_meta['role_access'])}")
    
    st.subheader("Direct Table Editor")
    edited_custom_df = st.data_editor(
        c_meta["data"],
        num_rows="dynamic",
        use_container_width=True,
        key=f"custom_editor_{selected_menu}"
    )
    st.session_state.custom_menus[selected_menu]["data"] = edited_custom_df
    
    st.markdown("---")
    clean_filename = re.sub(r'[^\w\s]', '', selected_menu).strip().replace(" ", "_")
    render_export_toolbar(edited_custom_df, clean_filename, f"export_custom_{clean_filename}")