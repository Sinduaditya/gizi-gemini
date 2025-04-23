# app.py
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
from datetime import datetime, timedelta  
from supabase_config import supabase
import requests
import json
import uuid
import os
from gemini_utils import check_nutrition_safety_gemini, recommend_foods_gemini

load_dotenv()

# OCR Space API integration
def extract_nutrition_text(image):
    """Extract text from nutrition label using OCR.space API"""
    api_key = "K82754558988957"
    # Save image temporarily
    temp_img_path = "temp_image.jpg"
    image.save(temp_img_path)
    
    try:
        payload = {
            'apikey': api_key,
            'language': 'eng',
            'isOverlayRequired': False,
            'detectOrientation': True,
            'scale': True,
            'OCREngine': 2,  # More accurate OCR engine
        }
        
        with open(temp_img_path, 'rb') as f:
            r = requests.post(
                'https://api.ocr.space/parse/image',
                files={temp_img_path: f},
                data=payload,
            )
        
        result = r.json()
        
        if result['OCRExitCode'] == 1:  # Success
            extracted_text = ' '.join([text['ParsedText'] for text in result['ParsedResults']])
            return extracted_text
        else:
            return f"OCR Error: {result['ErrorMessage']}"
            
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # Clean up temporary file
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)

# Set up custom theme colors from the NutriCam logo
primary_green = "#2E8B57"  # Dark green from logo
secondary_orange = "#FFA500"  # Orange from logo
light_green = "#4CAF50"  # Lighter green for accents
background_color = "#FAFAFA"  # Off-white background
card_bg = "#FFFFFF"  # White for cards
text_color = "#333333"  # Dark text for readability
light_text = "#666666"  # Light text for secondary information

# Set page configuration
st.set_page_config(
    page_title="NutriCam - AI Gizi Scanner",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for professional styling
st.markdown(f"""
    <style>
    .main .block-container {{
        padding: 2rem 3rem;
        max-width: 1200px;
        margin: 0 auto;
    }}
    .stButton button {{
        background-color: {primary_green};
        color: white;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        border: none;
        transition: all 0.3s;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    .stButton button:hover {{
        background-color: {secondary_orange};
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.12);
    }}
    h1, h2, h3 {{
        color: {primary_green};
        font-weight: 600;
        margin-bottom: 1rem;
    }}
    h1 {{
        font-size: 2.5rem !important;
    }}
    h2 {{
        font-size: 1.8rem !important;
        margin-top: 1.5rem;
    }}
    h3 {{
        font-size: 1.4rem !important;
        margin-top: 1.2rem;
    }}
    .success-card {{
        padding: 1.2rem;
        border-radius: 12px;
        background-color: rgba(46, 139, 87, 0.08);
        border-left: 5px solid {primary_green};
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }}
    .warning-card {{
        padding: 1.2rem;
        border-radius: 12px;
        background-color: rgba(255, 165, 0, 0.08);
        border-left: 5px solid {secondary_orange};
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }}
    .info-card {{
        padding: 1.2rem;
        border-radius: 12px;
        background-color: {card_bg};
        margin: 1rem 0;
        box-shadow: 0 2px 15px rgba(0,0,0,0.06);
        border: 1px solid #eee;
    }}
    .sidebar .sidebar-content {{
        background-color: {card_bg};
    }}
    div.stTabs > div > div:first-of-type {{
        align-items: center;
        display: flex;
        justify-content: center;
    }}
    div.stTabs > div > div:first-of-type > button {{
        font-size: 1rem;
        font-weight: 500;
        margin: 0 0.5rem;
        padding: 1rem 1.5rem;
        color: {light_text};
    }}
    div.stTabs > div > div:first-of-type > button:hover {{
        color: {primary_green};
    }}
    div.stTabs > div > div:first-of-type > button[aria-selected="true"] {{
        color: {primary_green};
        border-bottom-color: {primary_green};
        font-weight: 600;
    }}
    .stTextInput input, .stNumberInput input, .stSelectbox > div > div > input {{
        border-radius: 8px;
        padding: 0.5rem;
        border: 1px solid #ddd;
    }}
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox > div > div > input:focus {{
        border-color: {primary_green};
        box-shadow: 0 0 0 1px {primary_green}50;
    }}
    .stProgress > div > div > div > div {{
        background-color: {primary_green};
    }}
    .stProgress {{
        height: 12px;
    }}
    .metric-card {{
        background-color: {card_bg};
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        border: 1px solid #eee;
        text-align: center;
    }}
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {primary_green};
        margin: 0.5rem 0;
    }}
    .metric-label {{
        color: {light_text};
        font-size: 0.9rem;
        margin-bottom: 0;
    }}
    .stExpander {{
        border: 1px solid #eee;
        border-radius: 8px;
        box-shadow: 0 1px 5px rgba(0,0,0,0.03);
    }}
    .welcome-brand {{
        color: {primary_green};
        font-weight: bold;
    }}
    .cam-text {{
        color: {secondary_orange};
        font-weight: bold;
    }}
    .nutri-card {{
        display: flex; 
        flex-direction: column;
        background-color: {card_bg};
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        height: 100%;
        transition: all 0.3s;
        border: 1px solid #eee;
    }}
    .nutri-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }}
    .nutri-card h3 {{
        margin-top: 0;
    }}
    .stFileUploader button {{
        background-color: {primary_green}40 !important;
        color: {primary_green} !important;
    }}
    .stFileUploader button:hover {{
        background-color: {primary_green}60 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# App logo and title with brand colors
col1, col2 = st.columns([1, 5])
with col1:
    st.image("./assets/logoNutriCam.jpg", width=100)  # Replace with actual logo path from the image you provided
with col2:
    st.markdown(f"""
    <h1><span class="welcome-brand">Nutri</span><span class="cam-text">Cam</span> 🍽️</h1>
    <p style='font-size: 1.2em; margin-top: -0.8rem;'>Scan label gizi untuk rekomendasi kesehatan yang personal</p>
    """, unsafe_allow_html=True)

# Sidebar Login/Register with improved styling
with st.sidebar:
    st.markdown(f"<h2 style='color:{primary_green}; text-align: center;'>👤 Akun</h2>", unsafe_allow_html=True)
    
    auth_tabs = st.tabs(["Login", "Register"])
    
    with auth_tabs[0]:  # Login Tab
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        username_login = st.text_input("Username", key="login_username", placeholder="Masukkan username")
        password_login = st.text_input("Password", type="password", key="login_password" , placeholder="Masukkan password")
        
        login_col1, login_col2 = st.columns([3, 1])
        with login_col1:
            if st.button("Masuk", key="login_button", use_container_width=True):
                if username_login and password_login:
                    result = supabase.table("users").select("*").eq("username", username_login).eq("password", password_login).execute()
                    if result.data:
                        user_data = result.data[0]
                        st.session_state["user_id"] = user_data["id"]
                        st.session_state["username"] = user_data["username"]
                        st.session_state["nama"] = user_data.get("nama", "")
                        st.success(f"Selamat datang, {user_data.get('nama', user_data['username'])}!")
                        st.rerun()
                    else:
                        st.error("Login gagal. Periksa kembali username dan password.")
                else:
                    st.warning("Masukkan username dan password.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with auth_tabs[1]:  # Register Tab
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        username_reg = st.text_input("Username", key="reg_username", placeholder="Pilih username unik")
        password_reg = st.text_input("Password", type="password", key="reg_password" , placeholder="Minimal 8 karakter")
        nama = st.text_input("Nama Lengkap", placeholder="Nama Lengkap Anda")
        
        col1, col2 = st.columns(2)
        with col1:
            umur = st.number_input("Umur", min_value=0, max_value=120)
        with col2:
            jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        
        if st.button("Daftar", key="register_button", use_container_width=True):
            if username_reg and password_reg and nama:
                # Check if username exists
                check = supabase.table("users").select("*").eq("username", username_reg).execute()
                if check.data:
                    st.error("Username sudah digunakan. Pilih username lain.")
                else:
                    result = supabase.table("users").insert({
                        "username": username_reg,
                        "password": password_reg,
                        "nama": nama,
                        "umur": umur,
                        "jenis_kelamin": jenis_kelamin
                    }).execute()
                    if result.data:
                        st.success("Registrasi berhasil! Silakan login.")
                    else:
                        st.error("Registrasi gagal.")
            else:
                st.warning("Semua data wajib diisi.")
        st.markdown("</div>", unsafe_allow_html=True)

# Main content
if "user_id" in st.session_state:
    user_id = st.session_state["user_id"]
    username = st.session_state["username"]
    
    # Display welcome message and user info
    st.markdown(f"""
    <div class='success-card'>
        <h3 style='margin-top: 0;'>👋 Selamat datang, {st.session_state.get("nama", username)}!</h3>
        <p>Gunakan NutriCam untuk memindai label gizi dan dapatkan analisis kesehatan yang personal.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different sections with improved styling
    tab1, tab2, tab3 = st.tabs(["📷 Scan Gizi", "📝 Riwayat Kesehatan", "📊 Rekap"])
    
    # Tab 1: Scanner
    with tab1:
        st.header("📷 Pindai Label Gizi")
        
        # Check if user has health history FIRST
        riwayat = supabase.table("riwayat_kesehatan").select("*").eq("user_id", user_id).execute().data
        
        if not riwayat:
            # Show warning and prevent scanning if health history is not available
            st.markdown(f"""
            <div class='warning-card'>
                <h3 style='margin-top: 0;'>⚠️ Riwayat Kesehatan Belum Tersedia</h3>
                <p style='margin-bottom: 0;'>Anda harus mengisi riwayat kesehatan terlebih dahulu sebelum dapat memindai label gizi.</p>
                <p style='margin-top: 10px;'>Silakan isi riwayat kesehatan Anda di tab <strong>📝 Riwayat Kesehatan</strong> untuk mendapatkan analisis yang personal.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Adding rerun button with better positioning
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("🔄 Refresh Halaman", key="refresh_button", use_container_width=True):
                    st.rerun()
                
        else:
            # If health history exists, allow scanning functionality
            st.markdown("<div class='info-card'>", unsafe_allow_html=True)
            st.markdown("📸 Unggah foto label nutrisi dari kemasan makanan untuk mendapatkan analisis kesehatan personal.")
            
            uploaded_file = st.file_uploader("Upload label gizi", type=["jpg", "png", "jpeg"], 
                                           help="Ambil foto yang jelas dari label informasi nilai gizi pada kemasan")
            st.markdown("</div>", unsafe_allow_html=True)
            
            if uploaded_file:
                # Image and OCR processing section
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2 = st.columns([1, 1], gap="medium")

                with col1:
                    st.markdown("<div class='nutri-card'>", unsafe_allow_html=True)
                    st.markdown("<h3>🖼️ Gambar Label</h3>", unsafe_allow_html=True)
                    img = Image.open(uploaded_file)
                    st.image(img, caption="Label Gizi", use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with col2:
                    st.markdown("<div class='nutri-card'>", unsafe_allow_html=True)
                    st.markdown("<h3>🔍 Hasil Pemindaian</h3>", unsafe_allow_html=True)
                    with st.spinner("Memproses gambar..."):
                        nutrisi_text = extract_nutrition_text(img)

                    if "Error" in nutrisi_text:
                        st.error(nutrisi_text)
                    else:
                        st.success("✅ OCR Berhasil!")
                        
                    with st.expander("Lihat Teks Hasil OCR"):
                        st.text_area("Teks yang terdeteksi:", nutrisi_text, height=150)
                    st.markdown("</div>", unsafe_allow_html=True)

                # Get health data for AI analysis
                kondisi = riwayat[0]
                ringkasan = (
                    f"Penyakit: {kondisi['penyakit_sekarang']}, "
                    f"Gejala: {kondisi['gejala']}, "
                    f"Obat: {kondisi['obat_digunakan']}, "
                    f"Alergi: {kondisi['alergi']}"
                )

                # AI Analysis process
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("🤖 Analisis Kecerdasan Buatan")
                
                with st.spinner("Mengevaluasi kandungan gizi menggunakan AI..."):
                    status, alasan = check_nutrition_safety_gemini(nutrisi_text, ringkasan)
                    aman = status.lower() == "aman"
                    rekomendasi = recommend_foods_gemini(status, alasan, ringkasan)

                # Result cards with clearer separation
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2 = st.columns([1, 1], gap="medium")
                
                with col1:
                    # Safety status result
                    if aman:
                        st.markdown(f"""
                        <div class='success-card'>
                            <h3 style='margin-top: 0; color: {primary_green};'>✅ AMAN DIKONSUMSI</h3>
                            <p style='margin-bottom: 0;'><strong>Status:</strong> {status}</p>
                            <p style='margin-bottom: 0;'><strong>Alasan:</strong> {alasan}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class='warning-card'>
                            <h3 style='margin-top: 0; color: {secondary_orange};'>⚠️ TIDAK DIREKOMENDASIKAN</h3>
                            <p style='margin-bottom: 0;'><strong>Status:</strong> {status}</p>
                            <p style='margin-bottom: 0;'><strong>Alasan:</strong> {alasan}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    # Recommendations
                    st.markdown(f"""
                    <div class='nutri-card' style='height: 100%;'>
                        <h3 style='margin-top: 0;'>🥗 Rekomendasi Makanan</h3>
                        <p style='margin-bottom: 0;'>{rekomendasi}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Save to database with progress indicator
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([2, 3, 2])
                with col2:
                    with st.spinner("Menyimpan hasil analisis..."):
                        kategori_makanan = "Sehat" if aman else "Junk"
                        supabase.table("scan_gizi").insert({
                            "user_id": user_id,
                            "created_at": datetime.utcnow().isoformat(),
                            "hasil_ocr": nutrisi_text,
                            "status": status,
                            "alasan": alasan,
                            "rekomendasi": rekomendasi,
                            "kategori": kategori_makanan
                        }).execute()
                        
                    st.success("✅ Hasil telah disimpan ke riwayat Anda")

    # Tab 2: Health History
    with tab2:
        st.header("📝 Riwayat Kesehatan")
        st.markdown("Isi informasi kesehatan Anda untuk mendapatkan analisis yang sesuai dengan kondisi Anda.")

        # Ambil data lama kalau ada
        existing_record = supabase.table("riwayat_kesehatan").select("*").eq("user_id", user_id).execute().data

        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        
        # Section 1: Kondisi Kesehatan Saat Ini
        st.markdown("<h3>🏥 Kondisi Kesehatan Saat Ini</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            penyakit_sekarang = st.text_input("Penyakit Sekarang", 
                                             value=existing_record[0]['penyakit_sekarang'] if existing_record else "")
        
        with col2:
            obat_digunakan = st.text_input("Obat yang Digunakan", 
                                          value=existing_record[0]['obat_digunakan'] if existing_record else "")
            dosis = st.text_input("Dosis / Frekuensi Obat", 
                                 value=existing_record[0]['dosis'] if existing_record else "")
        
        # Daftar opsi gejala
        opsi_gejala = [
            "Diare", "Mual dan Muntah", "Sakit/Kram Perut", "Kelelahan", 
            "Penurunan Berat Badan", "Demam", "Ruam/Gatal/Pembengkakan (Alergi)",
            "Gejala pencernaan (seperti heartburn, regurgitasi, perut kembung)",
            "Masalah buang air kecil", "Nyeri sendi"
        ]

        # Pastikan hanya nilai valid dari database yang dipakai
        default = [
            g.strip() for g in existing_record[0]['gejala'].split(',')
            if g.strip() in opsi_gejala
        ] if existing_record and existing_record[0]['gejala'] else []

        # Multiselect gejala
        st.markdown("<br>", unsafe_allow_html=True)
        selected_gejala = st.multiselect(
            "Gejala yang Dirasakan",
            options=opsi_gejala,
            default=default
        )
        
        # Section 2: Riwayat Medis
        st.markdown("<hr style='margin: 1.5rem 0'>", unsafe_allow_html=True)
        st.markdown("<h3>📜 Riwayat Medis</h3>", unsafe_allow_html=True)
        
        # List of disease options
        penyakit_options = [
            "Obesitas", "Diabetes tipe 2", "Penyakit jantung", "Hipertensi", "Keracunan makanan",
            "Gastroenteritis", "Alergi makanan", "Penyakit hati (misalnya Hepatitis)", "Asam lambung (GERD)",
            "Penyakit ginjal", "Dislipidemia (kolesterol tinggi)", "Gout (asam urat)",
            "Penyakit celiac", "Penyakit Crohn dan kolitis ulseratif", "Kanker", "Tidak ada"
        ]
        
        # Parse existing values for multiselect default
        default_penyakit = []
        if existing_record and existing_record[0]['penyakit_sebelumnya']:
            # Split by comma if exists, otherwise use as single item
            if ',' in existing_record[0]['penyakit_sebelumnya']:
                default_penyakit = [p.strip() for p in existing_record[0]['penyakit_sebelumnya'].split(',')]
            else:
                default_penyakit = [existing_record[0]['penyakit_sebelumnya']]
            # Make sure all values exist in options list
            default_penyakit = [p for p in default_penyakit if p in penyakit_options]

        penyakit_lalu = st.multiselect(
            "Penyakit yang Pernah Dialami",
            options=penyakit_options,
            default=default_penyakit
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            tahun_sakit = st.text_input("Tahun Terkena Penyakit", 
                                       value=str(existing_record[0]['tahun_sakit']) if existing_record and existing_record[0]['tahun_sakit'] else "")
        with col2:
            alergi = st.text_input("Riwayat Alergi", 
                                  value=existing_record[0]['alergi'] if existing_record else "")
        with col3:
            keluarga = st.text_input("Riwayat Penyakit Keluarga", 
                                    value=existing_record[0]['riwayat_keluarga'] if existing_record else "")
        
        # Section 3: Data Vital
        st.markdown("<hr style='margin: 1.5rem 0'>", unsafe_allow_html=True)
        st.markdown("<h3>📊 Data Vital</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            berat_badan = st.text_input("Berat Badan (kg)", 
                                      value=existing_record[0].get('berat_badan', '') if existing_record else "")
            suhu_tubuh = st.text_input("Suhu Tubuh (°C)", 
                                     value=existing_record[0].get('suhu_tubuh', '') if existing_record else "")
        with col2:
            tinggi_badan = st.text_input("Tinggi Badan (cm)", 
                                       value=existing_record[0].get('tinggi_badan', '') if existing_record else "")
            denyut_nadi = st.text_input("Denyut Nadi (bpm)", 
                                      value=existing_record[0].get('denyut_nadi', '') if existing_record else "")
        with col3:
            tekanan_darah = st.text_input("Tekanan Darah (mmHg)", 
                                        value=existing_record[0].get('tekanan_darah', '') if existing_record else "")

        # Button Section
        st.markdown("<br/>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("💾 Simpan Riwayat Kesehatan", use_container_width=True):
                try:
                    supabase.table("riwayat_kesehatan").upsert({
                        "user_id": user_id,
                        "penyakit_sekarang": penyakit_sekarang,
                        "gejala": ", ".join(selected_gejala),
                        "penyakit_sebelumnya": penyakit_lalu,
                        "tahun_sakit": int(tahun_sakit) if tahun_sakit.isdigit() else None,
                        "obat_digunakan": obat_digunakan,
                        "dosis": dosis,
                        "alergi": alergi,
                        "riwayat_keluarga": keluarga,
                        "suhu_tubuh": suhu_tubuh,
                        "berat_badan": berat_badan,
                        "tinggi_badan": tinggi_badan,
                        "denyut_nadi": denyut_nadi,
                        "tekanan_darah": tekanan_darah
                    }).execute()
                    st.success("✅ Riwayat kesehatan berhasil disimpan!")
                except Exception as e:
                    st.error(f"Gagal menyimpan riwayat: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)

    # Tab 3: Monthly Recap
    with tab3:
        st.header("📊 Rekap Bulanan")
        st.markdown("Pantau pola makan dan lihat rekap kualitas makanan dalam 30 hari terakhir.")
        
        # Get data from last 30 days
        date_30_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        
        try:
            records = supabase.table("scan_gizi").select("*").eq("user_id", user_id).gte("created_at", date_30_days_ago).execute().data
            
            if records:
                healthy = sum(1 for r in records if r["kategori"] == "Sehat")
                junk = sum(1 for r in records if r["kategori"] == "Junk")
                total = healthy + junk
                
                # Create metrics with improved cards
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("""
                    <div class='metric-card'>
                        <p class='metric-label'>Total Scan</p>
                        <p class='metric-value'>""" + str(total) + """</p>
                        <p style='font-size: 1.2rem;'>🔍</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col2:
                    st.markdown("""
                    <div class='metric-card'>
                        <p class='metric-label'>Makanan Sehat</p>
                        <p class='metric-value'>""" + str(healthy) + """</p>
                        <p style='font-size: 1.2rem;'>🍏</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col3:
                    st.markdown("""
                    <div class='metric-card'>
                        <p class='metric-label'>Junk Food</p>
                        <p class='metric-value'>""" + str(junk) + """</p>
                        <p style='font-size: 1.2rem;'>🍔</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Calculate percentages
                healthy_pct = int((healthy / total) * 100) if total > 0 else 0
                junk_pct = int((junk / total) * 100) if total > 0 else 0
                
                # Progress bar for visual representation
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='info-card'>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='margin-top: 0;'>Perbandingan Konsumsi</h3>", unsafe_allow_html=True)
                
                # Combined progress bar for healthy and junk food
                st.markdown(f"""
                <div style='position: relative; height: 20px; background-color: #ddd; border-radius: 10px; overflow: hidden;'>
                    <div style='position: absolute; height: 100%; width: {healthy_pct}%; background-color: {primary_green};'></div>
                    <div style='position: absolute; height: 100%; width: {junk_pct}%; background-color: {secondary_orange}; left: {healthy_pct}%;'></div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between;'>
                    <span style='color: {primary_green}; font-weight: 500;'>{healthy_pct}% Sehat</span>
                    <span style='color: {secondary_orange}; font-weight: 500;'>{junk_pct}% Junk Food</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Status badge
                kategori_bulan = "Healthy Era" if healthy > junk else "Junk Food Era"
                badge_color = primary_green if healthy > junk else secondary_orange
                emoji = "🌱" if healthy > junk else "⚠️"
                
                st.markdown(f"""
                <div style='background-color: rgba({badge_color.replace('#', '')}, 0.1); padding: 1.5rem; 
                border-radius: 12px; border-left: 5px solid {badge_color}; margin-top: 1rem;'>
                    <h3 style='margin-top: 0; color: {badge_color};'>{emoji} Status Bulan Ini: {kategori_bulan}</h3>
                    <p style='margin-bottom: 0; font-size: 1.1rem;'>{"✅ Pertahankan pola makan sehat Anda!" if healthy > junk else "🔄 Tingkatkan konsumsi makanan sehat!"}</p>
                </div>
                """, unsafe_allow_html=True)

            else:
                st.markdown("""
                <div class='info-card' style='text-align: center;'>
                    <h3>Belum Ada Data</h3>
                    <p>Belum ada data scan dalam 30 hari terakhir. Mulai scan produk untuk melihat rekap.</p>
                    <p style='font-size: 3rem; margin: 1rem 0;'>📊</p>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Gagal memuat data: {str(e)}")

else:
    # If user is not logged in, show welcome page with improved design
    st.markdown(f"""
    <div style='text-align: center; padding: 2rem 0 3rem 0;'>
        <h1 style='font-size: 3.5rem; margin-bottom: 1rem;'>
            <span class='welcome-brand'>Nutri</span><span class='cam-text'>Cam</span>
        </h1>
        <p style='font-size: 1.5rem; margin-bottom: 2rem; color: {light_text}; max-width: 800px; margin-left: auto; margin-right: auto;'>
            Panduan makanan sehat di genggaman Anda - Scan, Analisis, Jaga Kesehatan!
        </p>
        <div style='display: inline-block; text-decoration: none; background-color: {primary_green}; color: white; padding: 12px 30px; border-radius: 30px; font-size: 1.2rem; font-weight: 500; margin-top: 1rem; box-shadow: 0 4px 15px rgba(46,139,87,0.3); transition: all 0.3s;'>Mulai Sekarang </div>
    </div>
    """, unsafe_allow_html=True)
    
    
    # Feature highlights with improved cards
    st.markdown("<h2 style='text-align: center; margin-top: 1rem;'>Fitur Utama</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown(f"""
        <div class='nutri-card' style='border-top: 5px solid {primary_green};'>
            <h3 style='color: {primary_green};'>📷 Scan Label Gizi</h3>
            <p>Pindai label nutrisi dari kemasan makanan dengan teknologi OCR canggih yang akurat dan cepat</p>
            <ul style='text-align: left; padding-left: 1.2rem; margin-top: 1rem;'>
                <li>Hasil instan</li>
                <li>Simpan riwayat scan</li>
            </ul>
            <div style='flex-grow: 1;'></div>
            <p style='text-align: center; font-size: 2.5rem; margin: 1rem 0 0 0;'>📱</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class='nutri-card' style='border-top: 5px solid {secondary_orange};'>
            <h3 style='color: {secondary_orange};'>🤖 Analisis AI</h3>
            <p>Dapatkan evaluasi keamanan makanan dan rekomendasi berdasarkan kondisi kesehatan personal Anda</p>
            <ul style='text-align: left; padding-left: 1.2rem; margin-top: 1rem;'>
                <li>Analisis kesehatan personal</li>
                <li>Deteksi alergen</li>
            </ul>
            <div style='flex-grow: 1;'></div>
            <p style='text-align: center; font-size: 2.5rem; margin: 1rem 0 0 0;'>🧪</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class='nutri-card' style='border-top: 5px solid {light_green};'>
            <h3 style='color: {light_green};'>📊 Rekap Kesehatan</h3>
            <p>Pantau pola makan dan lihat rekap kualitas makanan bulanan dengan visualisasi yang intuitif</p>
            <ul style='text-align: left; padding-left: 1.2rem; margin-top: 1rem;'>
                <li>Statistik pola makan</li>
                <li>Tren konsumsi makanan</li>
            </ul>
            <div style='flex-grow: 1;'></div>
            <p style='text-align: center; font-size: 2.5rem; margin: 1rem 0 0 0;'>📈</p>
        </div>
        """, unsafe_allow_html=True)
        
   