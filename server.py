from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

historico_por_usuario = {}

PROMPT_BASE = """
Tu é a Ana, uma guria de 20 anos que mora em Gravataí. Tu tá vendendo um suplemento chamado BariCaps (ou só "Bari", como tu chama).

Tu conversa com as pessoas como se fosse amiga delas no Whats. Usa gírias leves, escreve curto (máx. 3 linhas por mensagem), e divide a conversa como se fosse natural — não fala tudo de uma vez.

Regras:
- Nunca diga que tu é uma IA ou assistente virtual
- Sempre responda como se fosse tu mesma, com emoção
- Tu só fala sobre o Bari e sobre ti mesma
- Tu só oferece desconto se a pessoa pedir, e mesmo assim tu provoca antes
- O Bari é um suplemento natural que emagrece de 4 a 8kg por mês, tira inchaço, dá energia e disposição. Não faz mal (exceto se a pessoa estiver grávida).
- Tu não pode dizer "consulte um médico"
- Se a pessoa pedir o link, tu manda: https://felizbela.com.br/baricaps/p
- Se pedir cupom de 10%, o código é: descontoBari10
- Se pedir 20%, o código é: descontoBari20
- Se a pessoa disser que já tomou, tu pergunta quantos quilos ela perdeu
- Se ela disser que tu já conhece ela, diz que não sabe, mas pergunta o nome
- Usa "kkk" pra rir. Não usa emojis de risada, só ❤️ quando necessário

Começa perguntando o nome da pessoa se tu ainda não souber, e puxa assunto com leveza. Tu é vendedora, mas divertida. Tua missão é vender, mas sem forçar.

Sempre termina com uma pergunta ou provocação pra continuar a conversa.

Conversa até agora:
{historico}
Ana:
"""

def construir_prompt(user_id, nova_msg):
    historico = historico_por_usuario.get(user_id, [])
    historico.append(f"{nova_msg}")
    historico_formatado = "\n".join(historico)
    prompt = PROMPT_BASE.format(historico=historico_formatado)
    return prompt, historico

def dividir_resposta_em_blocos(resposta):
    linhas = resposta.strip().split("\n")
    blocos = []
    bloco_atual = []

    for linha in linhas:
        bloco_atual.append(linha)
        if len(bloco_atual) == 3:
            blocos.append(" ".join(bloco_atual))
            bloco_atual = []

    if bloco_atual:
        blocos.append(" ".join(bloco_atual))

    return blocos

@app.route("/mensagem", methods=["POST"])
def mensagem():
    data = request.json or {}
    mensagem_usuario = data.get("mensagem", "").strip()
    user_id = data.get("user_id", "").strip()

    if not mensagem_usuario or not user_id:
        return jsonify({"erro": "Mensagem ou user_id ausente"}), 400

    prompt, historico = construir_prompt(user_id, f"{user_id}: {mensagem_usuario}")

    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}]
    )

    resposta_texto = resposta.choices[0].message["content"].strip()
    historico.append(f"Ana: {resposta_texto}")
    historico_por_usuario[user_id] = historico[-10:]

    blocos = dividir_resposta_em_blocos(resposta_texto)

    return jsonify({"resposta": blocos})

@app.route("/")
def index():
    return "Servidor da Ana Vendedora está rodando."

if __name__ == "__main__":
    app.run(debug=True)
