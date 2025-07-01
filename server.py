from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/midia", methods=["POST"])
def transcrever_midia():
    data = request.get_json()

    from_user = data.get("from")
    mensagem = data.get("mensagem")
    midia_url = data.get("midia_url")
    midia_tipo = data.get("midia_tipo")

    if not midia_url or not midia_tipo:
        return jsonify({"error": "midia_url e midia_tipo são obrigatórios"}), 400

    try:
        # Baixar o arquivo de mídia
        resposta = requests.get(midia_url)
        nome_arquivo = f"temp_{from_user}.{midia_tipo}"
        with open(nome_arquivo, "wb") as f:
            f.write(resposta.content)

        # Enviar para transcrição
        with open(nome_arquivo, "rb") as audio_file:
            transcricao = openai.Audio.transcribe("whisper-1", audio_file)

        texto = transcricao["text"]

        os.remove(nome_arquivo)

        return jsonify({"texto": texto})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "Servidor ativo e aguardando mídia"}), 200

if __name__ == "__main__":
    from os import environ
    app.run(host="0.0.0.0", port=int(environ.get("PORT", 5000)))
