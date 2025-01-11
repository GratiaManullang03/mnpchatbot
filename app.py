from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Load campus data from JSON file
def load_campus_data():
    try:
        with open('campus_data.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Warning: campus_data.json not found")
        return {}
    except json.JSONDecodeError:
        print("Warning: campus_data.json is not valid JSON")
        return {}

# Load campus data
campus_data = load_campus_data()

# Create system prompt with campus data
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Create chat completion with OpenAI using campus data
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )

        # Extract the bot's reply
        bot_reply = completion.choices[0].message.content

        return jsonify({'reply': bot_reply})

    except Exception as e:
        print(f"Detailed error: {str(e)}")  # Log the detailed error
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

if __name__ == '__main__':
    # Verify API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY is not set in .env file")
    
    print("Loading with campus data:", bool(campus_data))
    app.run(debug=True)