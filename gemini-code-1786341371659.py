import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import urllib.parse
import io
try:
    import xlsxwriter
except ImportError:
    pass

def convert_df_to_excel(df_dict):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

def generate_pdf_report(title, header_info, tables_dict):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor("#0F7B5F"),
            spaceAfter=10
        )
        elements.append(Paragraph(f"<b>{title}</b>", title_style))
        elements.append(Paragraph("<b>Megalodon Aquatic - Swimming Academy</b>", styles['Normal']))
        elements.append(Paragraph(f"Tanggal Cetak: {datetime.now().strftime('%d %B %Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 15))

        if header_info:
            for k, v in header_info.items():
                elements.append(Paragraph(f"<b>{k}:</b> {v}", styles['Normal']))
            elements.append(Spacer(1, 15))

        for table_name, df in tables_dict.items():
            if not df.empty:
                elements.append(Paragraph(f"<b>{table_name}</b>", styles['Heading2']))
                elements.append(Spacer(1, 5))
                
                data = [df.columns.tolist()] + df.values.tolist()
                formatted_data = []
                for row_idx, row in enumerate(data):
                    formatted_row = []
                    for col in row:
                        val = str(col)
                        if row_idx == 0:
                            formatted_row.append(Paragraph(f"<b>{val}</b>", styles['Normal']))
                        else:
                            formatted_row.append(Paragraph(val, styles['Normal']))
                    formatted_data.append(formatted_row)

                t = Table(formatted_data, hAlign='LEFT')
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E0F2FE")),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0,0), (-1,0), 6),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 15))

        doc.build(elements)
        return buffer.getvalue()
    except Exception as e:
        return f"Error Generating PDF: {str(e)}".encode('utf-8')


# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Megalodon Aquatic - Sistem Manajemen",
    page_icon="🦈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING (EMERALD & OCEAN THEME) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #0F7B5F;
    }
    h1, h2, h3 { color: #0F7B5F; }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE USERS DATABASE ---
if 'users' not in st.session_state:
    st.session_state.users = pd.DataFrame([
        {"Username": "admin", "Password": "123", "Role": "Admin", "Nama": "Manajemen Utama", "No HP": "081299998888"},
        {"Username": "budi", "Password": "123", "Role": "Pelatih", "Nama": "Budi Santoso", "No HP": "081234567890"},
        {"Username": "siti", "Password": "123", "Role": "Pelatih", "Nama": "Siti Aminah", "No HP": "082198765432"},
        {"Username": "rian", "Password": "123", "Role": "Pelatih", "Nama": "Rian Hidayat", "No HP": "083811223344"},
    ])

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

# --- INITIALIZE DATA TABLES ---
if 'pelatih' not in st.session_state:
    st.session_state.pelatih = pd.DataFrame([
        {"ID": "PLT-001", "Nama": "Budi Santoso", "No HP": "081234567890", "Tarif/Sesi": 75000, "Status": "Aktif"},
        {"ID": "PLT-002", "Nama": "Siti Aminah", "No HP": "082198765432", "Tarif/Sesi": 85000, "Status": "Aktif"},
        {"ID": "PLT-003", "Nama": "Rian Hidayat", "No HP": "083811223344", "Tarif/Sesi": 75000, "Status": "Aktif"},
    ])

if 'siswa' not in st.session_state:
    st.session_state.siswa = pd.DataFrame([
        {"ID": "SW-001", "Nama": "Andi Pratama", "No HP Ortu": "081211112222", "Level": "Pemula", "Pelatih": "Budi Santoso", "Status": "Aktif", "Kuota Sesi": 8},
        {"ID": "SW-002", "Nama": "Citra Kirana", "No HP Ortu": "081333334444", "Level": "Menengah", "Pelatih": "Siti Aminah", "Status": "Naik Level", "Kuota Sesi": 8},
        {"ID": "SW-003", "Nama": "Dimas Anggara", "No HP Ortu": "081555556666", "Level": "Pemula", "Pelatih": "Rian Hidayat", "Status": "Aktif", "Kuota Sesi": 4},
    ])

if 'absensi' not in st.session_state:
    st.session_state.absensi = pd.DataFrame([
        {"Tanggal": "2026-08-01", "Nama Pelatih": "Budi Santoso", "Kolam": "Kolam Utama (Olympic)", "Status": "Hadir", "Sesi": 1, "Catatan": "Latihan meluncur"},
        {"Tanggal": "2026-08-01", "Nama Pelatih": "Siti Aminah", "Kolam": "Kolam Anak / Pemula", "Status": "Hadir", "Sesi": 2, "Catatan": "Gaya dada"},
        {"Tanggal": "2026-08-02", "Nama Pelatih": "Rian Hidayat", "Kolam": "Kolam Utama (Olympic)", "Status": "Hadir", "Sesi": 1, "Catatan": "Latihan pernapasan"},
    ])

if 'absensi_siswa' not in st.session_state:
    st.session_state.absensi_siswa = pd.DataFrame([
        {"Tanggal": "2026-08-01", "Nama Siswa": "Andi Pratama", "Pelatih": "Budi Santoso", "Status": "Hadir", "Jumlah Sesi": 1},
        {"Tanggal": "2026-08-01", "Nama Siswa": "Citra Kirana", "Pelatih": "Siti Aminah", "Status": "Hadir", "Jumlah Sesi": 1},
        {"Tanggal": "2026-08-02", "Nama Siswa": "Andi Pratama", "Pelatih": "Budi Santoso", "Status": "Hadir", "Jumlah Sesi": 1},
        {"Tanggal": "2026-08-03", "Nama Siswa": "Dimas Anggara", "Pelatih": "Rian Hidayat", "Status": "Hadir", "Jumlah Sesi": 1},
    ])

if 'progres' not in st.session_state:
    st.session_state.progres = pd.DataFrame([
        {"Tanggal": "2026-08-01", "Nama Siswa": "Andi Pratama", "Keberanian": 8, "Napas": 7, "Floating": 7, "Teknik": 6, "Rata-rata": 7.0, "Rekomendasi": "Tetap"},
        {"Tanggal": "2026-08-01", "Nama Siswa": "Citra Kirana", "Keberanian": 9, "Napas": 9, "Floating": 8, "Teknik": 9, "Rata-rata": 8.75, "Rekomendasi": "Naik Level"},
    ])

if 'pembayaran_siswa' not in st.session_state:
    st.session_state.pembayaran_siswa = pd.DataFrame([
        {"Tanggal": "2026-08-01", "Nama Siswa": "Andi Pratama", "Bulan/Paket": "Agustus (8 Sesi)", "Jumlah Bayar": 500000, "Metode": "Transfer Bank", "Status": "Lunas"},
        {"Tanggal": "2026-08-01", "Nama Siswa": "Citra Kirana", "Bulan/Paket": "Agustus (8 Sesi)", "Jumlah Bayar": 500000, "Metode": "Tunai", "Status": "Lunas"},
        {"Tanggal": "2026-08-02", "Nama Siswa": "Dimas Anggara", "Bulan/Paket": "Agustus (4 Sesi)", "Jumlah Bayar": 300000, "Metode": "Transfer Bank", "Status": "Lunas"},
    ])

if 'pengeluaran_lain' not in st.session_state:
    st.session_state.pengeluaran_lain = pd.DataFrame([
        {"Tanggal": "2026-08-01", "Kategori": "Sewa Kolam", "Keterangan": "Sewa Jalur Kolam Renang Agustus", "Jumlah": 400000},
        {"Tanggal": "2026-08-02", "Kategori": "Peralatan", "Keterangan": "Beli Pelampung & Kacamata Renang", "Jumlah": 150000},
    ])

if 'evaluasi' not in st.session_state:
    st.session_state.evaluasi = pd.DataFrame([
        {"Nama Pelatih": "Budi Santoso", "Bulan": "Agustus", "Total Nilai": 93.3},
        {"Nama Pelatih": "Siti Aminah", "Bulan": "Agustus", "Total Nilai": 88.3},
    ])

# ----------------------------------------------------------------------
# FITUR LOGIN
# ----------------------------------------------------------------------
def login_screen():
    st.markdown("<h2 style='text-align: center;'>🦈 Login Megalodon Aquatic</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            uname = st.text_input("Username").lower().strip()
            pwd = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            if submit:
                users_df = st.session_state.users
                match = users_df[(users_df['Username'] == uname) & (users_df['Password'] == pwd)]
                if not match.empty:
                    user_data = match.iloc[0].to_dict()
                    st.session_state.logged_in = True
                    st.session_state.user_info = user_data
                    st.success(f"Berhasil Login sebagai {user_data['Nama']} ({user_data['Role']})")
                    st.rerun()
                else:
                    st.error("Username atau Password salah! (Default login: admin / 123)")

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# ----------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ----------------------------------------------------------------------
user_role = st.session_state.user_info["Role"]
user_nama = st.session_state.user_info["Nama"]

st.sidebar.title("🦈 Megalodon Aquatic")
st.sidebar.write(f"👤 **{user_nama}**")
st.sidebar.caption(f"Role: **{user_role}**")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.rerun()

st.sidebar.markdown("---")

if user_role == "Admin":
    menu_options = [
        "📊 Dashboard Management",
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
    menu_options = [
        "📝 Absensi Pelatih",
        "📈 Progres Siswa"
    ]

menu = st.sidebar.radio("MENU UTAMA", menu_options)

# ----------------------------------------------------------------------
# 1. DASHBOARD MANAGEMENT (ADMIN ONLY)
# ----------------------------------------------------------------------
if menu == "📊 Dashboard Management":
    st.title("📊 Executive Dashboard - Megalodon Aquatic")
    tot_pemasukan_siswa = st.session_state.pembayaran_siswa['Jumlah Bayar'].sum()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Siswa Aktif", len(st.session_state.siswa[st.session_state.siswa['Status'] == 'Aktif']))
    c2.metric("Total Pemasukan Siswa", f"Rp {tot_pemasukan_siswa:,.0f}")
    tot_sesi = st.session_state.absensi[st.session_state.absensi['Status'] == 'Hadir']['Sesi'].sum()
    c3.metric("Total Sesi Terlaksana", int(tot_sesi))
    c4.metric("Siswa Naik Level", len(st.session_state.siswa[st.session_state.siswa['Status'] == 'Naik Level']))

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📊 Rekapitulasi Sesi Pelatih")
        df_gaji = st.session_state.absensi[st.session_state.absensi['Status'] == 'Hadir'].groupby('Nama Pelatih')['Sesi'].sum().reset_index()
        st.bar_chart(df_gaji, x='Nama Pelatih', y='Sesi')
    with col_b:
        st.subheader("💳 Riwayat Pembayaran Terbaru Siswa")
        st.dataframe(st.session_state.pembayaran_siswa, use_container_width=True)

# ----------------------------------------------------------------------
# 2. DOWNLOAD SPREADSHEET REKAPAN (MULTI-SHEET) - ADMIN ONLY
# ----------------------------------------------------------------------
elif menu == "📊 Download Spreadsheet Rekapan (Multi-Sheet)":
    st.title("📊 Download Rekapan Lengkap Spreadsheet (Excel Multi-Sheet)")
    st.info("💡 **Fitur khusus Admin:** Mengunduh seluruh data aplikasi ke dalam **1 File Excel (Spreadsheet)** dengan sheet terpisah untuk setiap kategori laporan.")
    
    df_abs_hadir = st.session_state.absensi[st.session_state.absensi['Status'] == 'Hadir']
    rekap_sesi = df_abs_hadir.groupby('Nama Pelatih')['Sesi'].sum().reset_index()
    df_payroll = pd.merge(st.session_state.pelatih, rekap_sesi, left_on='Nama', right_on='Nama Pelatih', how='left').fillna(0)
    df_payroll['Gaji Pokok'] = df_payroll['Sesi'] * df_payroll['Tarif/Sesi']
    df_payroll['Bonus Kehadiran'] = df_payroll['Sesi'].apply(lambda x: 200000 if x >= 2 else 0)
    df_payroll['TOTAL GAJI'] = df_payroll['Gaji Pokok'] + df_payroll['Bonus Kehadiran']

    all_sheets_dict = {
        'Master Siswa': st.session_state.siswa,
        'Master Pelatih': st.session_state.pelatih,
        'Absensi Siswa': st.session_state.absensi_siswa,
        'Absensi Pelatih': st.session_state.absensi,
        'Pembayaran SPP': st.session_state.pembayaran_siswa,
        'Pengeluaran Ops': st.session_state.pengeluaran_lain,
        'Progres Siswa': st.session_state.progres,
        'Rekap Gaji Payroll': df_payroll
    }

    excel_full_data = convert_df_to_excel(all_sheets_dict)

    col_sh1, col_sh2 = st.columns([2, 1])
    with col_sh1:
        st.subheader("📁 Isi Tab Sheet dalam File Spreadsheet:")
        st.markdown("""
        1. 🏊 **Master Siswa**: Data profil seluruh siswa & kuota latihan.
        2. 👥 **Master Pelatih**: Data pelatih & tarif nominal gaji per sesi.
        3. 📝 **Absensi Siswa**: Catatan riwayat kehadiran & tanggal latihan siswa.
        4. 📋 **Absensi Pelatih**: Catatan kehadiran mengajar coach.
        5. 💳 **Pembayaran SPP**: Riwayat transaksi pendaftaran & SPP siswa.
        6. 📤 **Pengeluaran Ops**: Catatan operasional (sewa kolam, alat, dll).
        7. 📈 **Progres Siswa**: Nilai evaluasi perkembangan teknik renang.
        8. 💰 **Rekap Gaji Payroll**: Perhitungan total gaji & bonus pelatih.
        """)

    with col_sh2:
        st.markdown("### 📥 Unduh Sekarang")
        st.download_button(
            label="📊 Download File Spreadsheet (.xlsx)",
            data=excel_full_data,
            file_name=f"Rekapan_Lengkap_Megalodon_Aquatic_{datetime.now().strftime('%Y%m%d_%H%m')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ----------------------------------------------------------------------
# 3. LAPORAN ARUS KAS KHUSUS (ADMIN ONLY)
# ----------------------------------------------------------------------
elif menu == "💵 Laporan Arus Kas Khusus":
    st.title("💵 Laporan Arus Kas (Cash Flow Report)")
    st.write("Laporan rekapitulasi Arus Kas Masuk (Pemasukan SPP) dan Arus Kas Keluar (Gaji Pelatih & Operasional).")
    
    total_inflow = st.session_state.pembayaran_siswa['Jumlah Bayar'].sum()
    
    df_abs_hadir = st.session_state.absensi[st.session_state.absensi['Status'] == 'Hadir']
    rekap_sesi = df_abs_hadir.groupby('Nama Pelatih')['Sesi'].sum().reset_index()
    df_payroll = pd.merge(st.session_state.pelatih, rekap_sesi, left_on='Nama', right_on='Nama Pelatih', how='left').fillna(0)
    df_payroll['Gaji Pokok'] = df_payroll['Sesi'] * df_payroll['Tarif/Sesi']
    df_payroll['Bonus Kehadiran'] = df_payroll['Sesi'].apply(lambda x: 200000 if x >= 2 else 0)
    total_gaji_outflow = (df_payroll['Gaji Pokok'] + df_payroll['Bonus Kehadiran']).sum()
    
    total_operasional_outflow = st.session_state.pengeluaran_lain['Jumlah'].sum()
    total_outflow = total_gaji_outflow + total_operasional_outflow
    net_cash_flow = total_inflow - total_outflow
    
    col_cf1, col_cf2, col_cf3 = st.columns(3)
    col_cf1.metric("📥 Total Arus Kas Masuk (Inflow)", f"Rp {total_inflow:,.0f}")
    col_cf2.metric("📤 Total Arus Kas Keluar (Outflow)", f"Rp {total_outflow:,.0f}")
    col_cf3.metric("💰 Arus Kas Bersih (Net Cash Flow)", f"Rp {net_cash_flow:,.0f}", delta=f"Rp {net_cash_flow:,.0f}")
    
    st.markdown("---")
    st.subheader("📥 Export Laporan Arus Kas (PDF / Excel Sheet)")
    
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        excel_data = convert_df_to_excel({
            'Pemasukan SPP': st.session_state.pembayaran_siswa,
            'Pengeluaran Gaji': df_payroll[['Nama', 'Sesi', 'Tarif/Sesi', 'Gaji Pokok', 'Bonus Kehadiran']],
            'Pengeluaran Operasional': st.session_state.pengeluaran_lain
        })
        st.download_button(
            label="📊 Download Laporan Arus Kas (.xlsx / Excel Sheet)",
            data=excel_data,
            file_name=f"Laporan_Arus_Kas_Megalodon_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    with col_exp2:
        pdf_bytes = generate_pdf_report(
            title="LAPORAN ARUS KAS (CASH FLOW REPORT)",
            header_info={
                "Total Arus Masuk (Inflow)": f"Rp {total_inflow:,.0f}",
                "Total Arus Keluar (Outflow)": f"Rp {total_outflow:,.0f}",
                "Arus Kas Bersih (Net Cash Flow)": f"Rp {net_cash_flow:,.0f}"
            },
            tables_dict={
                "1. Penerimaan Kas SPP Siswa": st.session_state.pembayaran_siswa,
                "2. Pengeluaran Operasional": st.session_state.pengeluaran_lain
            }
        )
        st.download_button(
            label="📄 Download Laporan Arus Kas (.pdf / PDF Document)",
            data=pdf_bytes,
            file_name=f"Laporan_Arus_Kas_Megalodon_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.markdown("---")
    tab_cf1, tab_cf2, tab_cf3 = st.tabs(["📥 Detail Pemasukan (SPP Siswa)", "📤 Detail Pengeluaran (Gaji & Ops)", "➕ Tambah Pengeluaran Ops"])
    
    with tab_cf1:
        st.subheader("📥 Daftar Penerimaan Kas SPP Siswa")
        st.dataframe(st.session_state.pembayaran_siswa.style.format({'Jumlah Bayar': 'Rp {:,.0f}'}), use_container_width=True)
        st.info(f"**Total Arus Masuk:** Rp {total_inflow:,.0f}")
        
    with tab_cf2:
        st.subheader("📤 Rincian Pengeluaran Gaji Pelatih & Operasional")
        st.write("1. **Pengeluaran Gaji Coach / Pelatih:**")
        st.dataframe(df_payroll[['Nama', 'Sesi', 'Tarif/Sesi', 'Gaji Pokok', 'Bonus Kehadiran']].style.format({'Tarif/Sesi': 'Rp {:,.0f}', 'Gaji Pokok': 'Rp {:,.0f}', 'Bonus Kehadiran': 'Rp {:,.0f}'}), use_container_width=True)
        
        st.write("2. **Pengeluaran Operasional Lain (Sewa Kolam, Alat, dll):**")
        st.dataframe(st.session_state.pengeluaran_lain.style.format({'Jumlah': 'Rp {:,.0f}'}), use_container_width=True)
        
    with tab_cf3:
        st.subheader("➕ Catat Pengeluaran Operasional Baru")
        with st.form("form_ops_baru"):
            col_o1, col_o2 = st.columns(2)
            with col_o1:
                tgl_ops = st.date_input("Tanggal Transaksi", datetime.now())
                kat_ops = st.selectbox("Kategori Pengeluaran", ["Sewa Kolam", "Peralatan Renang", "Konsumsi / Snack", "Lain-lain"])
            with col_o2:
                ket_ops = st.text_input("Keterangan", "Pembelian / Pembayaran...")
                jml_ops = st.number_input("Nominal Pengeluaran (Rp)", value=100000, step=25000)
                
            if st.form_submit_button("Simpan Pengeluaran"):
                row_ops = pd.DataFrame([{"Tanggal": str(tgl_ops), "Kategori": kat_ops, "Keterangan": ket_ops, "Jumlah": jml_ops}])
                st.session_state.pengeluaran_lain = pd.concat([st.session_state.pengeluaran_lain, row_ops], ignore_index=True)
                st.success(f"Pengeluaran {kat_ops} sebesar Rp {jml_ops:,.0f} berhasil dicatat!")

# ----------------------------------------------------------------------
# 4. KEUANGAN SISWA, DETAIL LATIHAN & RAPORT WA EDITABLE (ADMIN ONLY)
# ----------------------------------------------------------------------
elif menu == "💳 Keuangan & Latihan Siswa":
    st.title("💳 Laporan Keuangan Pembayaran & Total Latihan Siswa")
    
    tab1, tab2, tab3 = st.tabs(["📊 Rekap Latihan & Laporan WA", "➕ Input Pembayaran SPP/Paket", "📝 Input Kehadiran Latihan Siswa"])
    
    with tab1:
        st.subheader("📋 Ringkasan Total Latihan & Status Pembayaran Per Siswa")
        
        df_latihan = st.session_state.absensi_siswa[st.session_state.absensi_siswa['Status'] == 'Hadir'].groupby('Nama Siswa')['Jumlah Sesi'].sum().reset_index()
        df_latihan.rename(columns={'Jumlah Sesi': 'Total Latihan (Sesi)'}, inplace=True)
        
        df_bayar = st.session_state.pembayaran_siswa.groupby('Nama Siswa')['Jumlah Bayar'].sum().reset_index()
        df_bayar.rename(columns={'Jumlah Bayar': 'Total SPP Dibayar'}, inplace=True)
        
        rekap_siswa = pd.merge(st.session_state.siswa, df_latihan, left_on='Nama', right_on='Nama Siswa', how='left').fillna({'Total Latihan (Sesi)': 0})
        if 'Nama Siswa' in rekap_siswa.columns:
            rekap_siswa.drop(columns=['Nama Siswa'], inplace=True)
            
        rekap_siswa = pd.merge(rekap_siswa, df_bayar, left_on='Nama', right_on='Nama Siswa', how='left').fillna({'Total SPP Dibayar': 0})
        if 'Nama Siswa' in rekap_siswa.columns:
            rekap_siswa.drop(columns=['Nama Siswa'], inplace=True)
            
        rekap_siswa['Sisa Kuota Sesi'] = rekap_siswa['Kuota Sesi'] - rekap_siswa['Total Latihan (Sesi)']
        
        st.dataframe(
            rekap_siswa[['ID', 'Nama', 'No HP Ortu', 'Level', 'Pelatih', 'Kuota Sesi', 'Total Latihan (Sesi)', 'Sisa Kuota Sesi', 'Total SPP Dibayar', 'Status']].style.format({
                'Total SPP Dibayar': 'Rp {:,.0f}',
                'Total Latihan (Sesi)': '{:.0f}',
                'Sisa Kuota Sesi': '{:.0f}'
            }),
            use_container_width=True
        )
        
        st.markdown("---")
        st.subheader("📲 Kirim Raport / Laporan Per Siswa (PDF + WA Editable)")
        
        col_wa1, col_wa2 = st.columns([1, 2])
        
        with col_wa1:
            pilihan_s = st.selectbox("Pilih Nama Siswa:", rekap_siswa['Nama'].tolist())
            s_data = rekap_siswa[rekap_siswa['Nama'] == pilihan_s].iloc[0]
            
            df_p = st.session_state.progres[st.session_state.progres['Nama Siswa'] == pilihan_s]
            if not df_p.empty:
                last_p = df_p.iloc[-1]
                keb = last_p['Keberanian']
                nap = last_p['Napas']
                flo = last_p['Floating']
                tek = last_p['Teknik']
                rata = last_p['Rata-rata']
                rekom = last_p['Rekomendasi']
            else:
                keb = nap = flo = tek = "-"
                rata = 0.0
                rekom = "Belum Di-evaluasi"

            # Individual Student PDF Raport
            df_eval_indiv = pd.DataFrame([{
                "Keberanian Air": f"{keb} / 10",
                "Pernapasan": f"{nap} / 10",
                "Floating / Meluncur": f"{flo} / 10",
                "Teknik Gaya": f"{tek} / 10",
                "Rata-rata": f"{rata:.2f}",
                "Status Level": rekom
            }])
            
            # Extract list of training dates
            df_tgl_s = st.session_state.absensi_siswa[(st.session_state.absensi_siswa['Nama Siswa'] == pilihan_s) & (st.session_state.absensi_siswa['Status'] == 'Hadir')]
            if not df_tgl_s.empty:
                tgl_list = df_tgl_s['Tanggal'].tolist()
                tgl_str = ", ".join(tgl_list)
            else:
                tgl_str = "Belum ada riwayat tanggal latihan"

            pdf_indiv = generate_pdf_report(
                title=f"RAPORT PERKEMBANGAN RENANG - {s_data['Nama'].upper()}",
                header_info={
                    "Nama Siswa": s_data['Nama'],
                    "Level Kelas": s_data['Level'],
                    "Pelatih Utama": s_data['Pelatih'],
                    "Kuota Sesi Total": f"{int(s_data['Kuota Sesi'])} Sesi",
                    "Sesi Terpakai": f"{int(s_data['Total Latihan (Sesi)'])} Sesi",
                    "Sisa Kuota": f"{int(s_data['Sisa Kuota Sesi'])} Sesi",
                    "Tanggal Hadir Latihan": tgl_str,
                    "Total SPP Dibayar": f"Rp {s_data['Total SPP Dibayar']:,.0f}"
                },
                tables_dict={"Evaluasi Teknik Renang": df_eval_indiv}
            )
            
            st.download_button(
                label=f"📄 Download Raport PDF ({s_data['Nama']})",
                data=pdf_indiv,
                file_name=f"Raport_{s_data['Nama'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            no_wa = str(s_data['No HP Ortu']).replace("-", "").replace(" ", "")
            if no_wa.startswith("0"):
                no_wa = "62" + no_wa[1:]
                
            pesan_lengkap = (
                "🦈 *MEGALODON AQUATIC - LAPORAN PERKEMBANGAN & KEUANGAN* 🌊\n"
                "--------------------------------------------------\n"
                f"Halo Bapak/Ibu Orang Tua dari *{s_data['Nama']}*, 👋\n\n"
                "Berikut rekapitulasi latihan, evaluasi teknik, dan status keuangan ananda di Megalodon Aquatic:\n\n"
                "👤 *DATA SISWA*\n"
                f"• Nama Siswa    : {s_data['Nama']}\n"
                f"• Level Kelas   : {s_data['Level']}\n"
                f"• Pelatih Utama : {s_data['Pelatih']}\n\n"
                "🏊 *DETAIL & KUOTA LATIHAN*\n"
                f"• Total Kuota Sesi : {int(s_data['Kuota Sesi'])} Sesi\n"
                f"• Sesi Terpakai    : {int(s_data['Total Latihan (Sesi)'])} Sesi\n"
                f"• *SISA KUOTA*     : *{int(s_data['Sisa Kuota Sesi'])} Sesi*\n"
                f"• *TANGGAL LATIHAN*: {tgl_str}\n\n"
                "📈 *EVALUASI PERKEMBANGAN TEKNIK*\n"
                f"• Keberanian Air    : {keb} / 10 ⭐️\n"
                f"• Pernapasan        : {nap} / 10 ⭐️\n"
                f"• Floating/Meluncur : {flo} / 10 ⭐️\n"
                f"• Teknik Gaya       : {tek} / 10 ⭐️\n"
                f"• *Nilai Rata-Rata* : *{rata:.2f}*\n"
                f"• Status Level      : {rekom}\n\n"
                "💳 *STATUS KEUANGAN & PEMBAYARAN*\n"
                f"• Total SPP Dibayar : Rp {s_data['Total SPP Dibayar']:,.0f}\n"
                "• Status Pembayaran : LUNAS ✅\n"
                "--------------------------------------------------\n"
                "Terima kasih atas kepercayaannya pada Megalodon Aquatic! Mari bersama tingkatkan kemampuan renang ananda. 🦈✨\n\n"
                "_- Manajemen Megalodon Aquatic_"
            )

        with col_wa2:
            st.write("✏️ **Edit Pesan WA Sebelum Dikirim:**")
            edited_pesan_wa_s = st.text_area("Template Pesan WhatsApp Siswa", value=pesan_lengkap, height=350, key="txt_edit_wa_siswa")
            
            url_wa_lengkap = f"https://wa.me/{no_wa}?text={urllib.parse.quote(edited_pesan_wa_s)}"
            st.markdown(f'<a href="{url_wa_lengkap}" target="_blank"><button style="background-color:#25D366; color:white; padding:12px 20px; border:none; border-radius:8px; font-weight:bold; cursor:pointer; width:100%;">📲 Buka WhatsApp & Kirim Pesan ke {s_data["Nama"]}</button></a>', unsafe_allow_html=True)

    with tab2:
        st.subheader("Input Pembayaran SPP / Paket Sesi Baru")
        with st.form("form_bayar_spp"):
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                tgl_b = st.date_input("Tanggal Pembayaran", datetime.now())
                s_nama_b = st.selectbox("Nama Siswa", st.session_state.siswa['Nama'].tolist())
                pkt_b = st.selectbox("Paket / Bulan", ["Bulan Ini (4 Sesi)", "Bulan Ini (8 Sesi)", "Bulan Ini (12 Sesi)", "Pendaftaran Baru"])
            with col_b2:
                nominal_b = st.number_input("Nominal Pembayaran (Rp)", value=500000, step=50000)
                metode_b = st.selectbox("Metode Pembayaran", ["Transfer Bank", "Tunai", "QRIS"])
                st_b = st.selectbox("Status", ["Lunas", "Pending / DP"])
                
            if st.form_submit_button("Simpan Pembayaran"):
                row_bayar = pd.DataFrame([{
                    "Tanggal": str(tgl_b), "Nama Siswa": s_nama_b, "Bulan/Paket": pkt_b,
                    "Jumlah Bayar": nominal_b, "Metode": metode_b, "Status": st_b
                }])
                st.session_state.pembayaran_siswa = pd.concat([st.session_state.pembayaran_siswa, row_bayar], ignore_index=True)
                
                tambah_sesi = 8 if "8 Sesi" in pkt_b else (4 if "4 Sesi" in pkt_b else (12 if "12 Sesi" in pkt_b else 0))
                if tambah_sesi > 0:
                    st.session_state.siswa.loc[st.session_state.siswa['Nama'] == s_nama_b, 'Kuota Sesi'] += tambah_sesi
                    
                st.success(f"Pembayaran Rp {nominal_b:,.0f} untuk {s_nama_b} berhasil dicatat!")

        st.markdown("---")
        st.subheader("Edit Riwayat Pembayaran Siswa")
        edited_pembayaran = st.data_editor(st.session_state.pembayaran_siswa, num_rows="dynamic", use_container_width=True)
        if st.button("Simpan Perubahan Pembayaran"):
            st.session_state.pembayaran_siswa = edited_pembayaran
            st.success("Riwayat pembayaran berhasil diperbarui!")

    with tab3:
        st.subheader("Input Kehadiran Latihan Siswa")
        with st.form("form_abs_siswa"):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                tgl_ls = st.date_input("Tanggal Latihan", datetime.now(), key="tgl_ls")
                s_nama_ls = st.selectbox("Nama Siswa", st.session_state.siswa['Nama'].tolist(), key="s_nama_ls")
            with col_s2:
                p_nama_ls = st.selectbox("Pelatih Mengajar", st.session_state.pelatih['Nama'].tolist(), key="p_nama_ls")
                st_ls = st.selectbox("Status Kehadiran", ["Hadir", "Izin", "Sakit", "Alpha"], key="st_ls")
                sesi_ls = st.number_input("Jumlah Sesi Terpakai", min_value=1, max_value=3, value=1, key="sesi_ls")
                
            if st.form_submit_button("Catat Kehadiran Siswa"):
                row_ls = pd.DataFrame([{
                    "Tanggal": str(tgl_ls), "Nama Siswa": s_nama_ls, "Pelatih": p_nama_ls,
                    "Status": st_ls, "Jumlah Sesi": sesi_ls
                }])
                st.session_state.absensi_siswa = pd.concat([st.session_state.absensi_siswa, row_ls], ignore_index=True)
                st.success(f"Latihan {s_nama_ls} berhasil dicatat!")

        st.markdown("---")
        st.subheader("Edit Riwayat Latihan Siswa")
        edited_abs_s = st.data_editor(st.session_state.absensi_siswa, num_rows="dynamic", use_container_width=True)
        if st.button("Simpan Perubahan Riwayat Latihan"):
            st.session_state.absensi_siswa = edited_abs_s
            st.success("Riwayat latihan berhasil diperbarui!")

# ----------------------------------------------------------------------
# 5. ABSENSI PELATIH (KOLAM menggantikan KELAS)
# ----------------------------------------------------------------------
elif menu == "📝 Absensi Pelatih":
    st.title("📝 Data Absensi Kehadiran Pelatih")
    
    col_in, col_tb = st.columns([1, 2])
    with col_in:
        st.subheader("Form Absensi Baru Pelatih")
        with st.form("form_abs"):
            tgl = st.date_input("Tanggal Latihan", datetime.now())
            if user_role == "Pelatih":
                nama_p = user_nama
                st.info(f"Pelatih: **{nama_p}**")
            else:
                nama_p = st.selectbox("Nama Pelatih", st.session_state.pelatih['Nama'].tolist())
            
            # KELAS DIGANTI DENGAN KOLAM
            kolam = st.selectbox("Lokasi Kolam", ["Kolam Utama (Olympic)", "Kolam Anak / Pemula", "Kolam Dalam / Menengah", "Kolam Privat"])
            status = st.selectbox("Status Kehadiran", ["Hadir", "Izin", "Sakit", "Alpha"])
            sesi = st.number_input("Jumlah Sesi Mengajar", min_value=0, max_value=5, value=1)
            catatan = st.text_area("Catatan Latihan / Evaluasi Kolam", "-")
            
            if st.form_submit_button("Simpan Absensi Pelatih"):
                row = pd.DataFrame([{"Tanggal": str(tgl), "Nama Pelatih": nama_p, "Kolam": kolam, "Status": status, "Sesi": sesi, "Catatan": catatan}])
                st.session_state.absensi = pd.concat([st.session_state.absensi, row], ignore_index=True)
                st.success("Absensi pelatih berhasil disimpan!")

    with col_tb:
        st.subheader("Daftar Absensi Pelatih (Dapat Di-edit)")
        if user_role == "Admin":
            edited_abs = st.data_editor(st.session_state.absensi, num_rows="dynamic", use_container_width=True)
            if st.button("Simpan Perubahan Absensi"):
                st.session_state.absensi = edited_abs
                st.success("Data absensi berhasil di-update!")
        else:
            df_pelatih_abs = st.session_state.absensi[st.session_state.absensi['Nama Pelatih'] == user_nama]
            edited_abs_p = st.data_editor(df_pelatih_abs, num_rows="dynamic", use_container_width=True)
            if st.button("Update Absensi Saya"):
                st.session_state.absensi.update(edited_abs_p)
                st.success("Absensi Anda berhasil di-update!")

# ----------------------------------------------------------------------
# 6. PROGRES SISWA
# ----------------------------------------------------------------------
elif menu == "📈 Progres Siswa":
    st.title("📈 Laporan Progres Siswa")
    
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        st.subheader("Form Input Progres Siswa")
        with st.form("form_prog"):
            tgl_p = st.date_input("Tanggal Evaluasi", datetime.now())
            nama_s = st.selectbox("Pilih Siswa", st.session_state.siswa['Nama'].tolist())
            k1 = st.slider("Keberanian Air", 1, 10, 8)
            k2 = st.slider("Pernapasan", 1, 10, 7)
            k3 = st.slider("Floating / Meluncur", 1, 10, 7)
            k4 = st.slider("Teknik Gaya", 1, 10, 7)
            rekom = st.selectbox("Rekomendasi", ["Tetap", "Naik Level", "Remedial"])
            
            if st.form_submit_button("Simpan Progres"):
                rata = (k1 + k2 + k3 + k4) / 4.0
                row_p = pd.DataFrame([{"Tanggal": str(tgl_p), "Nama Siswa": nama_s, "Keberanian": k1, "Napas": k2, "Floating": k3, "Teknik": k4, "Rata-rata": rata, "Rekomendasi": rekom}])
                st.session_state.progres = pd.concat([st.session_state.progres, row_p], ignore_index=True)
                if rekom == "Naik Level":
                    st.session_state.siswa.loc[st.session_state.siswa['Nama'] == nama_s, 'Status'] = "Naik Level"
                st.success(f"Progres tersimpan! Rata-rata: {rata:.2f}")

    with col_p2:
        st.subheader("Edit Data Progres Siswa")
        edited_prog = st.data_editor(st.session_state.progres, num_rows="dynamic", use_container_width=True)
        if st.button("Simpan Perubahan Progres"):
            st.session_state.progres = edited_prog
            st.success("Data progres siswa berhasil diperbarui!")

# ----------------------------------------------------------------------
# 7. PENGGAJIAN & INTEGRASI WHATSAPP (ADMIN ONLY)
# ----------------------------------------------------------------------
elif menu == "💰 Penggajian & WA Laporan":
    st.title("💰 Perhitungan Gaji & Kirim Laporan via WhatsApp")
    
    df_abs_hadir = st.session_state.absensi[st.session_state.absensi['Status'] == 'Hadir']
    rekap_sesi = df_abs_hadir.groupby('Nama Pelatih')['Sesi'].sum().reset_index()
    
    df_payroll = pd.merge(st.session_state.pelatih, rekap_sesi, left_on='Nama', right_on='Nama Pelatih', how='left').fillna(0)
    df_payroll = pd.merge(df_payroll, st.session_state.evaluasi[['Nama Pelatih', 'Total Nilai']], left_on='Nama', right_on='Nama Pelatih', how='left').fillna(0)
    
    df_payroll['Gaji Pokok'] = df_payroll['Sesi'] * df_payroll['Tarif/Sesi']
    df_payroll['Bonus Kehadiran'] = df_payroll['Sesi'].apply(lambda x: 200000 if x >= 2 else 0)
    df_payroll['Bonus Evaluasi'] = df_payroll['Total Nilai'].apply(lambda x: 300000 if x >= 90 else 0)
    df_payroll['TOTAL GAJI'] = df_payroll['Gaji Pokok'] + df_payroll['Bonus Kehadiran'] + df_payroll['Bonus Evaluasi']
    
    st.subheader("📋 Rekapitulasi Gaji Pelatih Bulan Ini")
    st.dataframe(
        df_payroll[['Nama', 'No HP', 'Sesi', 'Tarif/Sesi', 'Gaji Pokok', 'Bonus Kehadiran', 'TOTAL GAJI']].style.format({
            'Tarif/Sesi': 'Rp {:,.0f}', 'Gaji Pokok': 'Rp {:,.0f}',
            'Bonus Kehadiran': 'Rp {:,.0f}', 'TOTAL GAJI': 'Rp {:,.0f}'
        }),
        use_container_width=True
    )
    
    st.markdown("---")
    st.subheader("📲 Kirim Rincian Gaji ke WhatsApp Pelatih")
    
    pilihan_pelatih = st.selectbox("Pilih Pelatih untuk Dikirimkan WA:", df_payroll['Nama'].tolist())
    p_data = df_payroll[df_payroll['Nama'] == pilihan_pelatih].iloc[0]
    
    no_hp = str(p_data['No HP']).replace("-", "").replace(" ", "")
    if no_hp.startswith("0"):
        no_hp = "62" + no_hp[1:]
        
    pesan_wa = (
        f"Hallo Coach *{p_data['Nama']}*,\n\n"
        "Berikut adalah rincian rekapan gaji & bonus Anda bulan ini di Megalodon Aquatic:\n"
        "-----------------------------------------\n"
        f"• Total Sesi Hadir : {int(p_data['Sesi'])} Sesi\n"
        f"• Tarif per Sesi   : Rp {p_data['Tarif/Sesi']:,.0f}\n"
        f"• Gaji Pokok Sesi  : Rp {p_data['Gaji Pokok']:,.0f}\n"
        f"• Bonus Kehadiran  : Rp {p_data['Bonus Kehadiran']:,.0f}\n"
        f"• Bonus Evaluasi   : Rp {p_data['Bonus Evaluasi']:,.0f}\n"
        "-----------------------------------------\n"
        f"💰 *TOTAL DITERIMA : Rp {p_data['TOTAL GAJI']:,.0f}*\n\n"
        "Terima kasih atas kerja keras Anda mengajar! 🦈✨\n"
        "_- Manajemen Megalodon Aquatic_"
    )
    
    st.write("✏️ **Edit Pesan WA Slip Gaji Sebelum Dikirim:**")
    edited_pesan_wa_p = st.text_area("Template Pesan WA Pelatih", value=pesan_wa, height=220, key="txt_edit_wa_p")
    
    encoded_pesan = urllib.parse.quote(edited_pesan_wa_p)
    wa_url = f"https://wa.me/{no_hp}?text={encoded_pesan}"
    
    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; padding:12px 20px; border:none; border-radius:8px; font-weight:bold; cursor:pointer; width:100%;">📲 Buka WhatsApp & Kirim Slip Gaji ke {p_data["Nama"]}</button></a>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# 8. KELOLA, EDIT & HAPUS DATA PELATIH (ADMIN KHUSUS)
# ----------------------------------------------------------------------
elif menu == "👥 Kelola & Hapus Data Pelatih":
    st.title("👥 Kelola, Edit, Tambah & Hapus Data Pelatih (Khusus Admin)")
    
    tab_p1, tab_p2, tab_p3 = st.tabs(["✏️ Edit Master & Tarif Pelatih", "➕ Tambah Pelatih Baru (Sinkron ID & No HP)", "🗑️ Hapus Pelatih Tertentu"])
    
    with tab_p1:
        st.subheader("📋 Tabel Master Pelatih (Sinkron ID, Nama, No HP, Tarif & Status)")
        st.info("💡 **Petunjuk:** Anda dapat mengubah Tarif/Sesi, Status, atau No HP secara langsung di tabel bawah.")
        
        edited_p = st.data_editor(st.session_state.pelatih, num_rows="dynamic", use_container_width=True, key="data_editor_pelatih")
        if st.button("💾 Simpan Perubahan Master Pelatih"):
            st.session_state.pelatih = edited_p
            st.success("Master data pelatih berhasil diperbarui!")
            
    with tab_p2:
        st.subheader("➕ Form Input & Sinkronisasi Pelatih Baru")
        st.caption("Pilih nama pelatih terdaftar atau masukkan nama baru untuk otomatis mensinkronkan ID dan No HP.")
        
        with st.form("form_tambah_pelatih_sync"):
            col_tp1, col_tp2 = st.columns(2)
            
            with col_tp1:
                auto_id = f"PLT-{len(st.session_state.pelatih) + 1:03d}"
                st.text_input("ID Pelatih Otomatis", value=auto_id, disabled=True)
                nama_pelatih_input = st.text_input("Nama Lengkap Pelatih", placeholder="misal: Hendra Wijaya")
                no_hp_input = st.text_input("No HP / WhatsApp", placeholder="081234567890")
                
            with col_tp2:
                tarif_input = st.number_input("Input Tarif / Sesi (Rp)", value=75000, step=5000)
                status_input = st.selectbox("Status Pelatih", ["Aktif", "Cuti / Non-Aktif"])
                
            if st.form_submit_button("➕ Simpan Data Pelatih"):
                if nama_pelatih_input.strip() != "":
                    row_new_p = pd.DataFrame([{
                        "ID": auto_id,
                        "Nama": nama_pelatih_input.strip(),
                        "No HP": no_hp_input.strip(),
                        "Tarif/Sesi": tarif_input,
                        "Status": status_input
                    }])
                    st.session_state.pelatih = pd.concat([st.session_state.pelatih, row_new_p], ignore_index=True)
                    st.success(f"Pelatih **{nama_pelatih_input}** ({auto_id}) berhasil ditambahkan dan disinkronkan!")
                    st.rerun()
                else:
                    st.error("Nama Pelatih wajib diisi!")

    with tab_p3:
        st.subheader("🗑️ Hapus Pelatih dari Sistem")
        st.warning("⚠️ **Perhatian:** Menghapus pelatih akan menghapus data pelatih dari daftar master.")
        
        pilihan_hapus_plt = st.selectbox("Pilih Pelatih yang Ingin Dihapus:", st.session_state.pelatih['Nama'].tolist())
        
        selected_p_info = st.session_state.pelatih[st.session_state.pelatih['Nama'] == pilihan_hapus_plt].iloc[0]
        st.write(f"📌 **Detail Sinkron Pelatih:** ID: `{selected_p_info['ID']}` | No HP: `{selected_p_info['No HP']}` | Tarif: `Rp {selected_p_info['Tarif/Sesi']:,.0f}`")
        
        if st.button(f"❌ Hapus Pelatih: {pilihan_hapus_plt}", type="primary"):
            st.session_state.pelatih = st.session_state.pelatih[st.session_state.pelatih['Nama'] != pilihan_hapus_plt].reset_index(drop=True)
            st.success(f"Data pelatih **{pilihan_hapus_plt}** berhasil dihapus dari sistem!")
            st.rerun()

# ----------------------------------------------------------------------
# 9. KELOLA & HAPUS DATA SISWA (ADMIN ONLY)
# ----------------------------------------------------------------------
elif menu == "🏊 Kelola & Hapus Data Siswa":
    st.title("🏊 Kelola, Edit & Hapus Data Siswa (Khusus Admin)")
    
    tab_s1, tab_s2, tab_s3 = st.tabs(["✏️ Edit & Hapus Master Siswa", "➕ Tambah Siswa Baru", "🗑️ Hapus Siswa Tertentu"])
    
    with tab_s1:
        st.subheader("📋 Tabel Master Siswa (Bisa Langsung Edit & Tambah Baris)")
        st.info("💡 **Petunjuk:** Anda bisa mengedit teks langsung di tabel, atau mencentang baris lalu tekan tombol **Delete** pada keyboard untuk menghapus.")
        
        edited_s = st.data_editor(st.session_state.siswa, num_rows="dynamic", use_container_width=True, key="data_editor_siswa")
        if st.button("💾 Simpan Perubahan Master Siswa"):
            st.session_state.siswa = edited_s
            st.success("Master data siswa berhasil diperbarui!")
            
    with tab_s2:
        st.subheader("➕ Tambah Data Siswa Baru")
        with st.form("form_tambah_siswa"):
            col_ts1, col_ts2 = st.columns(2)
            with col_ts1:
                new_id = f"SW-{len(st.session_state.siswa) + 1:03d}"
                st.text_input("ID Siswa", value=new_id, disabled=True)
                new_nama = st.text_input("Nama Siswa Lengkap")
                new_hp = st.text_input("No HP Ortu (WA)", "08123456789")
            with col_ts2:
                new_level = st.selectbox("Level Kelas", ["Pemula", "Menengah", "Lanjutan", "Prestasi"])
                new_pelatih = st.selectbox("Pelatih Utama", st.session_state.pelatih['Nama'].tolist())
                new_kuota = st.number_input("Kuota Sesi Awal", min_value=1, max_value=48, value=8)
                
            if st.form_submit_button("Simpan Siswa Baru"):
                if new_nama.strip() != "":
                    row_s_baru = pd.DataFrame([{
                        "ID": new_id,
                        "Nama": new_nama.strip(),
                        "No HP Ortu": new_hp,
                        "Level": new_level,
                        "Pelatih": new_pelatih,
                        "Status": "Aktif",
                        "Kuota Sesi": new_kuota
                    }])
                    st.session_state.siswa = pd.concat([st.session_state.siswa, row_s_baru], ignore_index=True)
                    st.success(f"Siswa baru **{new_nama}** berhasil ditambahkan!")
                    st.rerun()
                else:
                    st.error("Nama Siswa tidak boleh kosong!")

    with tab_s3:
        st.subheader("🗑️ Hapus Siswa dari Sistem")
        st.warning("⚠️ **Perhatian:** Menghapus siswa akan menghapus data master siswa dari daftar.")
        
        pilihan_hapus_siswa = st.selectbox("Pilih Siswa yang Ingin Dihapus:", st.session_state.siswa['Nama'].tolist())
        
        if st.button(f"❌ Hapus Siswa: {pilihan_hapus_siswa}", type="primary"):
            st.session_state.siswa = st.session_state.siswa[st.session_state.siswa['Nama'] != pilihan_hapus_siswa].reset_index(drop=True)
            st.success(f"Data siswa **{pilihan_hapus_siswa}** berhasil dihapus dari sistem!")
            st.rerun()

# ----------------------------------------------------------------------
# 10. MANAJEMEN AKUN SYSTEM (ADMIN ONLY)
# ----------------------------------------------------------------------
elif menu == "🔑 Pengaturan Akun System":
    st.title("🔑 Kelola Akun Admin & Pelatih")
    
    col_u1, col_u2 = st.columns([1, 2])
    with col_u1:
        st.subheader("➕ Tambah Akun Baru")
        with st.form("form_add_user"):
            u_name = st.text_input("Username").lower().strip()
            u_pass = st.text_input("Password", type="password")
            u_role = st.selectbox("Role Akun", ["Pelatih", "Admin"])
            u_fullname = st.text_input("Nama Lengkap")
            u_hp = st.text_input("No HP (WhatsApp)", "08123456789")
            
            if st.form_submit_button("Buat Akun"):
                new_u = pd.DataFrame([{"Username": u_name, "Password": u_pass, "Role": u_role, "Nama": u_fullname, "No HP": u_hp}])
                st.session_state.users = pd.concat([st.session_state.users, new_u], ignore_index=True)
                st.success(f"Akun {u_name} ({u_role}) berhasil dibuat!")

    with col_u2:
        st.subheader("Daftar & Edit Akun Terdaftar")
        edited_users = st.data_editor(st.session_state.users, num_rows="dynamic", use_container_width=True)
        if st.button("Simpan Perubahan Akun"):
            st.session_state.users = edited_users
            st.success("Data akun berhasil diperbarui!")