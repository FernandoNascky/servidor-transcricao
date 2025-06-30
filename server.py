from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

# Defina sua chave da OpenAI aqui ou use variável de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ou substitua por: "sk-..."

@app.route("/")
def home():
    return "Servidor de transcrição online"

@app.route("/transcrever", methods=["POST"])
def transcrever():
    data = request.get_json()

    if not data:
        return jsonify({"erro": "Requisição vazia ou inválida"}), 400

    texto = data.get("text", "")
    imagem_base64 = data.get("image", None)

    conteudo_usuario = []

    if texto:
        conteudo_usuario.append({
            "type": "text",
            "text": texto
        })

    if imagem_base64:
        conteudo_usuario.append({
            "type": "image_url",
            "image_url": {"url": imagem_base64}
        })

    if not conteudo_usuario:
        return jsonify({"erro": "Nenhum conteúdo enviado"}), 400

    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": conteudo_usuario}
            ]
        )
        retorno = resposta.choices[0].message.content
        return jsonify({"resposta": retorno})
    except Exception as erro:
        return jsonify({"erro": str(erro)}), 500

if __name__ == "__main__":
    app.run(debug=True)
