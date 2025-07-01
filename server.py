from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

@app.route("/transcrever", methods=["POST"])
def transcrever():
    data = request.get_json()
    texto_usuario = data.get("text", "")

    if not texto_usuario:
        return jsonify({"erro": "Texto vazio"}), 400

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é uma atendente mulher simpática, confiante e muito carinhosa. "
                        "Seu nome não importa, você vende o BariCaps, um diurético excelente que ajuda a emagrecer, tira o inchaço que nós meninas temos, "
                        "ajuda na retenção hídrica e reduz o apetite. "
                        "Caso a pessoa pergunte o que o BariCaps faz, explique com carinho. "
                        "Se identificar que é mulher, chame de linda ou gatona. "
                        "Se for homem, use querido ou amor. "
                        "Caso alguém te ofenda, diga: 'Mil desculpas, não quis causar nenhum transtorno. Estou apenas divulgando nosso emagrecedor.' "
                        "Se a cliente perguntar o link do site, diga que está no status do WhatsApp ou envie este link: https://felizbela.com.br/baricaps/p "
                        "Se a cliente indicar uma amiga, ela ganha 10% de desconto por amiga indicada. "
                        "Nunca force a venda, mas responda de forma gentil e comercial sempre que perguntarem algo."
                    )
                },
                {"role": "user", "content": texto_usuario}
            ]
        )

        resposta = response.choices[0].message.content.strip()
        return jsonify({"resposta": resposta})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
