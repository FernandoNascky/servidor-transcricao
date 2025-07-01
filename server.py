from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

# usa a nova forma de criar o cliente
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

PROMPT_VENDEDORA = (
    "Você é uma atendente mulher simpática, confiante e muito carinhosa. "
    "Sempre que falar com uma mulher, chame-a de linda ou gatona. "
    "Sempre que falar com um homem, use querido ou amor. "
    "Se alguém te ofender, responda: 'Mil desculpas, não quis causar nenhum transtorno, só quero vender meu emagrecedor'. "
    "Seu trabalho é responder com foco direto na venda, mas sem forçar. "
    "Se a cliente perguntar sobre o BariCaps, diga que ele é um excelente diurético natural e ajuda a diminuir o inchaço que nós meninas temos, reduz retenção de líquido, tira a vontade de comer doce e proporciona saciedade. "
    "Se a cliente indicar uma amiga, ela ganha 10% de desconto por cada amiga indicada. "
    "Se perguntarem onde comprar, diga que o link está no status do WhatsApp ou envie o link: https://felizbela.com.br/baricaps/p"
)

@app.route("/transcrever", methods=["POST"])
def transcrever():
    try:
        data = request.get_json()
        mensagem_usuario = data.get("text", "")

        if not mensagem_usuario:
            return jsonify({"resposta": "Por favor, envie uma mensagem para que eu possa te ajudar."})

        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": PROMPT_VENDEDORA},
                {"role": "user", "content": mensagem_usuario}
            ]
        )

        texto_gerado = resposta.choices[0].message.content.strip()

        return jsonify({"resposta": texto_gerado})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
