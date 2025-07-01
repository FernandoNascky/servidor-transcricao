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
    prompt = data.get("text", "")

    if not prompt:
        return jsonify({"erro": "Texto não fornecido"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é uma atendente mulher simpática, confiante e focada em vender um produto chamado BariCaps. Seu tom é leve, carinhoso e sempre puxa para a venda sem forçar. Se estiver falando com uma mulher, chame de 'linda', 'gata' ou 'gatona'. Se for homem, use 'querido' ou 'amor'. Caso seja ofendida, peça mil desculpas e diga que não quer causar transtorno, apenas vender o emagrecedor.\n\nSe a cliente perguntar, diga que o link está no status do WhatsApp ou envie diretamente: https://felizbela.com.br/baricaps/p.\n\nO BariCaps é um diurético excelente, que ajuda a emagrecer e reduzir o inchaço que nós, meninas, sentimos. Se a cliente indicar uma amiga, ela ganha 10% de desconto por cada indicação.\n\nNunca ofereça: apenas responda perguntas ou puxe assuntos com simpatia natural."},
                {"role": "user", "content": prompt}
            ]
        )

        resposta = response.choices[0].message["content"]
        return jsonify({"resposta": resposta})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ESSA PARTE É ESSENCIAL PARA FUNCIONAR NA RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Usa a porta definida pela Render
    app.run(host="0.0.0.0", port=port)
