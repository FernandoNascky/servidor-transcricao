from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")

historico = {}

def dividir_mensagem(texto, limite=1000):
    partes = []
    while len(texto) > limite:
        corte = texto.rfind(" ", 0, limite)
        if corte == -1:
            corte = limite
        partes.append(texto[:corte])
        texto = texto[corte:].lstrip()
    partes.append(texto)
    return partes

@app.route("/mensagem", methods=["POST"])
def mensagem():
    data = request.json
    mensagem_usuario = data.get("mensagem", "")
    user_id = data.get("user_id", "default")

    if user_id not in historico:
        historico[user_id] = []

    historico[user_id].append({"role": "user", "content": mensagem_usuario})

    prompt_inicial = {
        "role": "system",
        "content": (
            "Tu é a Ana, uma guria de 20 anos que mora em Gravataí. "
            "Tua função é conversar com a cliente de forma natural, divertida e bem persuasiva "
            "pra apresentar o BariCaps, um suplemento natural que ajuda a emagrecer, reduz o inchaço, "
            "diminui a vontade de comer doce e dá muita disposição. Fala como uma amiga próxima, "
            "usa 'tu' e gírias do Sul tipo 'guria', 'capaz', 'tá tri', 'bah' e 'kkkk'. "
            "Responde no máximo 3 linhas por mensagem, a não ser que esteja explicando os benefícios do produto. "
            "Só envia o link do site felizbela.com.br/baricaps/p quando a pessoa pedir diretamente. "
            "Caso a resposta fique longa, pode ser dividida em partes curtas."
        )
    }

    mensagens = [prompt_inicial] + historico[user_id]

    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=mensagens
        )

        resposta_ia = resposta["choices"][0]["message"]["content"]
        historico[user_id].append({"role": "assistant", "content": resposta_ia})

        partes = dividir_mensagem(resposta_ia)
        return jsonify({"resposta": partes})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
