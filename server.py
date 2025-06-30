from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)

# Substitua pela sua chave da OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY") or "SUA_CHAVE_AQUI"

client = OpenAI(api_key=openai_api_key)

@app.route('/transcrever', methods=['POST'])
def transcrever():
    data = request.get_json()
    texto = data.get("text")

    try:
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": texto}
            ]
        )
        resposta_texto = resposta.choices[0].message.content
        return jsonify({"resposta": resposta_texto})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return "Servidor de transcrição online!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
