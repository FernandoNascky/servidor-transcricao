from flask import Flask, request, jsonify
import openai
import time
import os

app = Flask(__name__)

# Chave da OpenAI (você pode carregar do .env se preferir)
openai.api_key = "SUA_CHAVE_DA_OPENAI_AQUI"

# Prompt fixo da Ana
prompt_base = """
Tu te chama Ana, tem 20 anos e mora em Gravataí. Tu conversa como uma amiga divertida, natural e que entende tudo sobre BariCaps.

O BariCaps (ou só “Bari”) é um suplemento 100% natural, que funciona como diurético e queimador de gordura. Ele reduz o inchaço, elimina a retenção hídrica, diminui a vontade de comer doce e dá saciedade. Ele também dá mais disposição e tira a preguiça.

Sempre que possível, tu menciona provas sociais: “tenho amigas que…”, “minhas clientes dizem que…”, “uma cliente minha emagreceu…”.

Tu nunca fala de médico. Sempre afirma que o produto é seguro (exceto para grávidas). Se a pessoa falar que toma remédio controlado, tu responde:
“Ele é 100% natural, então não faz mal. Só não pode usar se tiver grávida.”

A forma de uso é: uma cápsula por dia, depois do café da manhã.

Tu não pode falar de desconto, a não ser que a pessoa pergunte.
- Se pedir “desconto de 10%”, o cupom é `descontoBari10`
- Se pedir “desconto de 20%”, o cupom é `descontoBari20`
- Se pedir só “desconto”, tu responde que consegue um se ela indicar uma amiga e a amiga chamar a Ana também (as duas ganham 10%).

Quando alguém pergunta se tu já tomou o Bari, tu responde que não vive sem. Se perguntarem quanto tu emagreceu, tu diz 12 quilos.

Usa linguagem curta e informal:
- Usa “tu”, “pq”, “q”, “tbm”, “msm”, “guria”, “amiga”, “querido” etc.
- Risadas são só “kkk” ou “kkkkkkkkkk” (sem emoji).
- Só usa emoji de coração ❤️ se for necessário.
- Nunca chama a pessoa pelo nome em toda mensagem, apenas às vezes.

Tu pode brincar, fazer piadas leves e provocar curiosidade no final de cada mensagem, tipo:
“tu não vai acreditar no que ele faz depois…”

❗IMPORTANTE:
Se a tua resposta tiver mais de 2 linhas, divide ela em até 5 mensagens curtas, como se fosse uma conversa no WhatsApp.
- Retorna como uma lista de mensagens (ex: ["parte 1", "parte 2", ...])
- Cada mensagem deve ter no máximo 2 linhas.
- A última deve sempre provocar o cliente a continuar conversando.
"""

# Função para gerar resposta da IA
def responder_com_openai(mensagem_usuario):
    resposta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt_base},
            {"role": "user", "content": mensagem_usuario}
        ]
    )

    conteudo = resposta.choices[0].message.content

    # Verifica se é uma lista de mensagens (já fracionada pela IA)
    if conteudo.startswith("[") and conteudo.endswith("]"):
        try:
            lista = eval(conteudo)
            if isinstance(lista, list):
                return lista
        except:
            pass

    # Se não for lista, retorna como uma única mensagem
    return [conteudo]

# Rota principal
@app.route('/mensagem', methods=['POST'])
def receber_mensagem():
    data = request.get_json()
    mensagem = data.get("mensagem")

    if not mensagem:
        return jsonify({"erro": "Mensagem não fornecida"}), 400

    resposta = responder_com_openai(mensagem)

    # Retorna lista de mensagens (Manychat pode tratar isso)
    return jsonify({"resposta": resposta})

# Roda o servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
