import os
import google.generativeai as genai

# Konfigurasi API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Inisialisasi model
model = genai.GenerativeModel("gemini-1.5-pro")


def check_nutrition_safety_gemini(text, health_data):
    prompt = f"""
Kamu adalah ahli gizi digital. Tugasmu adalah menilai apakah suatu makanan aman untuk dikonsumsi berdasarkan data kesehatan pengguna dan informasi nilai gizinya.

Data kesehatan pengguna:
{health_data}

Informasi nilai gizi makanan:
{text}

Berikan jawaban dengan format berikut:

Status: [Aman / Tidak Aman]  
Alasan: [Penjelasan singkat mengapa makanan tersebut aman atau tidak, maksimal 2 kalimat]

Sekarang, berikan penilaianmu:
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Error saat memanggil Gemini: {str(e)}"


def recommend_foods_gemini(text, health_data):
    prompt = f"""
Kamu adalah ahli gizi digital. Berdasarkan informasi gizi suatu makanan dan data kesehatan pengguna, tugasmu adalah:

1. Menentukan apakah makanan tersebut aman atau tidak.
2. Jika tidak aman, jelaskan alasannya secara singkat.
3. Berikan 2-3 rekomendasi makanan alternatif yang lebih aman dan sehat untuk pengguna.

Data kesehatan pengguna:
{health_data}

Informasi nilai gizi makanan:
{text}

Berikan jawaban dengan format berikut:

Status: [Aman / Tidak Aman]  
Alasan: [Jika Tidak Aman, berikan penjelasan singkat. Jika Aman, cukup tulis "Tidak perlu rekomendasi."]
Rekomendasi: 
- [Makanan alternatif 1]
- [Makanan alternatif 2]
- [Makanan alternatif 3] (opsional)

Contoh output:
Status: Tidak Aman  
Alasan: Kandungan gula terlalu tinggi untuk penderita diabetes.  
Rekomendasi:
- Oatmeal tanpa pemanis
- Salad sayuran dengan minyak zaitun
- Sup ayam rendah garam

Sekarang, berikan hasil rekomendasimu:
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Error saat memanggil Gemini: {str(e)}"
