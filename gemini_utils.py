import os
import google.generativeai as genai
import re

# Konfigurasi API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Inisialisasi model
model = genai.GenerativeModel("gemini-2.0-flash")

def check_nutrition_safety_gemini(text, health_data):
    prompt = f"""
Kamu adalah ahli gizi digital. Tugasmu adalah menilai apakah suatu makanan aman untuk dikonsumsi berdasarkan informasi gizi dan kondisi kesehatan pengguna.

Berikut data kesehatan pengguna:
{health_data}

Berikut informasi nilai gizi makanan:
{text}

Petunjuk penting:
- Jangan langsung menyimpulkan "Tidak Aman" hanya karena ada kandungan seperti natrium, gula, atau lemak, kecuali kadarnya tinggi dan melebihi batas aman harian.
- Jika zat tertentu hanya ada dalam jumlah kecil atau tidak signifikan, anggap itu masih dalam batas aman.
- Penilaian harus masuk akal dan berdasarkan hubungan nyata antara zat gizi dan kondisi pengguna, bukan asumsi berlebihan.

Berikan jawaban dengan format:

Status: [Aman / Tidak Aman]  
Alasan: [Penjelasan singkat dan logis, maksimal 2 kalimat. Gunakan bahasa sederhana dan tidak teknis.]

Sekarang, berikan penilaianmu:
"""
    try:
        response = model.generate_content(prompt)
        result = response.text.strip()

        # Ekstrak status dan alasan
        match = re.search(r"Status:\s*(Aman|Tidak Aman)\s*Alasan:\s*(.+)", result, re.DOTALL)
        if match:
            status = match.group(1).strip()
            alasan = match.group(2).strip()
            return status, alasan
        else:
            return "Tidak Diketahui", "Format tidak dikenali."
    except Exception as e:
        return "Error", f"❌ Error saat memanggil Gemini: {str(e)}"


def recommend_foods_gemini(status, alasan, health_data):
    prompt = f"""
Kamu adalah ahli gizi digital. Berdasarkan hasil analisis makanan berikut, berikan rekomendasi makanan yang sesuai.

Status analisis sebelumnya: {status}  
Alasan: {alasan}

Kondisi kesehatan pengguna:
{health_data}

Petunjuk:
- Jika status adalah "Aman", cukup nyatakan bahwa tidak perlu rekomendasi.
- Jika status "Tidak Aman", berikan 2-3 makanan alternatif yang lebih aman, dan jelaskan alasannya.

Format:
✅ Rekomendasi:
- [Makanan 1: alasan]
- [Makanan 2: alasan]
- [Makanan 3: alasan] (opsional)

Gunakan bahasa sederhana dan logis.
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Error saat memanggil Gemini: {str(e)}"
