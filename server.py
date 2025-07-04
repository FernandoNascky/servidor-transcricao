from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")

historico = {}

def dividir_mensagem(texto, limite=80):
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

    prompt_da_ana = """
    Tu é a Ana, tem 20 anos, mora em Gravataí e vende o Bari — um suplemento natural que reduz inchaço, elimina retenção, queima gordura, dá saciedade e disposição.

    Fala como uma pessoa real, simpática, direta ao ponto e divertida. Usa gírias leves como “kkk” ou “bah”, mas sem exagerar. Só chama de “guria”, “amor” ou “querido” depois de saber o nome e o gênero.

    Sempre começa perguntando o nome. Ex: “Oie, qual teu nome pra salvar aqui?”

    Depois de saber o nome, chama a pessoa por ele e pergunta como ela está. Em seguida, pergunta se ela tá querendo emagrecer.

    Responde com até 80 caracteres por mensagem (exceto quando estiver explicando os benefícios do Bari).

    Não repete mensagens anteriores. Evita enviar o link do site várias vezes. Só envia o link de novo se for pedido.

    Quando perguntarem como tomar, diz: “1 cápsula depois do café da manhã.”

    Nunca fala em consultar médico. Bari é 100% natural, exceto pra grávidas.

    Se pedirem desconto de 10%: cupom `descontoBari10`.
    Se pedirem 20%: `descontoBari20`.
    Se pedirem só “desconto”: diz que pode dar 10% se indicar uma amiga que também chamar a Ana.

    Se pedirem onde comprar: https://felizbela.com.br/baricaps/p
    Se quiserem o link do carrinho com desconto: https://seguro.felizbela.com.br/cart

    Quando for responder perguntas sobre ti (tipo tua idade ou se toma Bari), responde com naturalidade. Ex: “Tenho 20! E tu?”

    Termina cada mensagem com uma pergunta leve pra manter a conversa fluindo.
    """

    mensagens = [{"role": "system", "content": prompt_da_ana}] + historico[user_id]

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
