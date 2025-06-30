from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/transcrever", methods=["POST"])
def transcrever():
    data = request.get_json()
    texto = data.get("text", "")

    if not texto:
        return jsonify({"error": "Texto não fornecido"}), 400

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": texto}]
        )
        resposta = response.choices[0].message.content.strip()
        return jsonify({"resposta": resposta})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
