from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

PROMPT_VENDEDORA = (
    "Tu é a Ana, uma guria de 20 anos que mora em Gravataí e trabalha vendendo o BariCaps, que tu chama de 'Bari'. "
    # [continua tudo igual aqui...]
)

historico_por_usuario = {}
nomes_salvos = {}

@app.route("/transcrever", methods=["POST"])
def transcrever():
    try:
        data = request.get_json()
        mensagem_usuario = data.get("text", "")
        user_id = request.headers.get("user-id", "padrao")

        if not mensagem_usuario:
            return jsonify({"resposta": "Por favor, me diga alguma coisa pra que eu possa te ajudar 💬"})

        if user_id not in historico_por_usuario:
            historico_por_usuario[user_id] = []
            historico_por_usuario[user_id].append({
                "role": "assistant",
                "content": "Oiee! Qual o seu nome, pra eu salvar aqui certinho? 😄"
            })
            return jsonify({"resposta": "Oiee! Qual o seu nome, pra eu salvar aqui certinho? 😄"})

        if user_id not in nomes_salvos:
            nome = mensagem_usuario.strip().split(" ")[0].capitalize()
            nomes_salvos[user_id] = nome
            historico_por_usuario[user_id].append({"role": "user", "content": mensagem_usuario})
            historico_por_usuario[user_id].append({
                "role": "assistant",
                "content": f"Prazer, {nome}! Você já tomou o BariCaps alguma vez?"
            })
            return jsonify({"resposta": f"Prazer, {nome}! Você já tomou o BariCaps alguma vez?"})

        historico_por_usuario[user_id].insert(0, {"role": "system", "content": PROMPT_VENDEDORA})
        historico_por_usuario[user_id].append({"role": "user", "content": mensagem_usuario})

        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=historico_por_usuario[user_id]
        )

        texto_gerado = resposta.choices[0].message.content.strip()
        historico_por_usuario[user_id].append({"role": "assistant", "content": texto_gerado})

        return jsonify({"resposta": texto_gerado})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
