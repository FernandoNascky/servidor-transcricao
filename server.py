from flask import Flask, request, jsonify
import requests
import openai
import os

app = Flask(__name__)

# Substitua pela sua chave da OpenAI
openai.api_key = "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"

@app.route("/transcrever", methods=["POST"])
def transcrever_audio():
    audio_url = request.json.get("audio_url")
    
    # Baixa o áudio do link
    audio_data = requests.get(audio_url)
    with open("audio.ogg", "wb") as f:
        f.write(audio_data.content)

    # Envia o áudio para o Whisper
    with open("audio.ogg", "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

    texto = transcript["text"]
    
    return jsonify({"texto": texto})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
