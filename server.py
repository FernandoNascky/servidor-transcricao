from flask import Flask, request, jsonify
import requests
import openai
import os

app = Flask(__name__)

# Substitua por sua chave real da OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

# 🔊 Transcrição de áudio
@app.route("/transcrever", methods=["POST"])
def transcrever_audio():
    audio_url = request.json.get("audio_url")
    audio_data = requests.get(audio_url)

    with open("audio.ogg", "wb") as f:
        f.write(audio_data.content)

    with open("audio.ogg", "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

    texto = transcript["text"]

    return jsonify({"texto": texto})


# 💬 Entendimento de texto
@app.route("/mensagem", methods=["POST"])
def responder_texto():
    texto = request.json.get("texto")

    resposta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um atendente simpático de WhatsApp que ajuda a vender produtos."},
            {"role": "user", "content": texto}
        ]
    )

    conteudo = resposta["choices"][0]["message"]["content"]
    return jsonify({"resposta": conteudo})


# 🖼️ Entendimento de imagem
@app.route("/imagem", methods=["POST"])
def responder_imagem():
    image_url = request.json.get("imagem_url")
    prompt = request.json.get("pergunta", "Descreva a imagem.")

    resposta = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        max_tokens=1000
    )

    conteudo = resposta["choices"][0]["message"]["content"]
    return jsonify({"resposta": conteudo})


# 🚀 Executar servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
