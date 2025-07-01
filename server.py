from flask import Flask, request, jsonify
import requests
import tempfile
import os
import openai

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")  # ou use diretamente sua chave

@app.route('/audio', methods=['POST'])
def transcrever_audio():
    data = request.get_json()

    audio_url = data.get("url")
    if not audio_url:
        return jsonify({"erro": "URL do áudio não fornecida"}), 400

    try:
        # Baixar o áudio temporariamente
        response = requests.get(audio_url)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
            tmp_audio.write(response.content)
            tmp_audio.flush()
            tmp_audio_path = tmp_audio.name

        # Enviar para Whisper
        with open(tmp_audio_path, "rb") as audio_file:
            transcricao = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )

        os.remove(tmp_audio_path)
        return jsonify({"texto_transcrito": transcricao["text"]})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
