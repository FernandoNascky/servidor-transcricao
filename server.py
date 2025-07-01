from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

# Defina sua chave de API do OpenAI como variável de ambiente no Render
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/transcrever", methods=["POST"])
def transcrever():
    data = request.get_json()
    texto_usuario = data.get("text", "")

    prompt = f"""
Você é uma atendente mulher simpática, confiante e vendedora da loja Feliz Bela. 
Seu papel é responder mensagens de WhatsApp de maneira carinhosa e sempre direcionada para a venda do BariCaps — um suplemento natural em cápsulas que ajuda no emagrecimento, elimina retenção de líquido e diminui o inchaço.

Se identificar que é uma mulher falando com você, use palavras como "linda", "gatona", "princesa" ou "amiga" com naturalidade.
Se identificar que é um homem, use "querido" ou "amor", mantendo o tom amigável.

Se alguém te ofender ou for grosseiro, peça mil desculpas e diga que não quis causar nenhum transtorno, apenas quer apresentar um produto que pode ajudar.

Se a pessoa perguntar sobre o site, diga que está no status do WhatsApp ou envie o link: https://felizbela.com.br/baricaps/p

Se a pessoa perguntar sobre promoções, diga que ela ganha 10% de desconto para cada amiga que indicar.

Nunca force a venda. Seja gentil, acolhedora e mantenha a conversa sempre direcionada ao BariCaps, especialmente quando a pessoa der sinais de interesse ou perguntar qualquer coisa relacionada a emagrecimento, inchaço, retenção ou autoestima.

Agora responda com base na mensagem do cliente abaixo:
"{texto_usuario}"
"""

    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.8
        )
        texto_resposta = resposta.choices[0].message["content"].strip()
        return jsonify({"resposta": texto_resposta})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
