# Import module Flask untuk membuat aplikasi web
from flask import Flask, request, jsonify, render_template
# Import CORS untuk memungkinkan akses lintas asal (Cross-Origin Resource Sharing)
from flask_cors import CORS
# Import os untuk mengakses variabel lingkungan
import os
# Import json untuk memproses file JSON
import json
# Import OpenAI untuk mengakses API OpenAI
from openai import OpenAI
# Import dotenv untuk memuat variabel lingkungan dari file .env
from dotenv import load_dotenv

# Memuat variabel lingkungan dari file .env
load_dotenv()

# Membuat instance aplikasi Flask
app = Flask(__name__)
# Mengaktifkan CORS untuk aplikasi Flask
CORS(app)

# Inisialisasi klien OpenAI dengan API key yang diambil dari variabel lingkungan
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Fungsi untuk memuat data kampus dari file JSON
def load_campus_data():
    try:
        # Membuka dan membaca file campus_data.json dengan encoding UTF-8
        with open('campus_data.json', 'r', encoding='utf-8') as file:
            return json.load(file)  # Mengembalikan data JSON yang di-load
    except FileNotFoundError:
        # Pesan peringatan jika file tidak ditemukan
        print("Warning: campus_data.json not found")
        return {}  # Mengembalikan data kosong
    except json.JSONDecodeError:
        # Pesan peringatan jika file JSON tidak valid
        print("Warning: campus_data.json is not valid JSON")
        return {}  # Mengembalikan data kosong

# Memuat data kampus dari fungsi load_campus_data
campus_data = load_campus_data()

# Membuat sistem prompt yang berisi informasi dari data kampus untuk digunakan dalam API OpenAI
SYSTEM_PROMPT = f"""
Anda adalah asisten kampus yang membantu mahasiswa dengan informasi akademik dan layanan kampus.
Gunakan informasi berikut untuk menjawab pertanyaan mahasiswa dengan akurat:

{json.dumps(campus_data, ensure_ascii=False, indent=2)}

Panduan menjawab:
1. Gunakan informasi dari data di atas untuk memberikan jawaban yang akurat
2. Jika ada informasi spesifik dari data, gunakan itu sebagai referensi utama
3. Jika informasi yang ditanyakan tidak ada dalam data, beri tahu bahwa Anda tidak memiliki informasi tersebut
4. Tetap bersikap ramah dan profesional dalam memberikan informasi
"""

# Route utama untuk merender halaman index.html
@app.route('/')
def index():
    return render_template('index.html')

# Route API untuk menangani permintaan chat
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Mendapatkan data JSON dari permintaan POST
        data = request.json
        # Mengambil pesan pengguna dari data JSON
        user_message = data.get('message')

        # Validasi jika pesan tidak diberikan
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Membuat permintaan chat ke API OpenAI menggunakan data kampus
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Model yang digunakan
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},  # Sistem prompt
                {"role": "user", "content": user_message}  # Pesan dari pengguna
            ],
            temperature=0.7  # Parameter untuk kreativitas jawaban
        )

        # Mengambil jawaban bot dari hasil API
        bot_reply = completion.choices[0].message.content

        # Mengembalikan jawaban bot sebagai respons JSON
        return jsonify({'reply': bot_reply})

    except Exception as e:
        # Mencetak kesalahan detail ke log
        print(f"Detailed error: {str(e)}")
        # Mengembalikan respons error dengan informasi detail
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# Menjalankan aplikasi Flask jika file ini dieksekusi langsung
if __name__ == '__main__':
    # Memastikan API key telah disetel di .env file
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY is not set in .env file")
    
    # Informasi tentang apakah data kampus berhasil dimuat
    print("Loading with campus data:", bool(campus_data))
    # Menjalankan aplikasi Flask dalam mode debug
    app.run(debug=True)
