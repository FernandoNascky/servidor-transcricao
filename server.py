from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import requests

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")

historico = {}
usuarios_ativos = {}
dados_cliente = {}  # Armazena nome, cidade e se indicou amiga

# Função para enviar mensagem para o WhatsApp (simula envio)
def enviar_mensagem_para_usuario(user_id, mensagem):
    print(f"[Mensagem para {user_id}]: {mensagem}")

# Função para gerar link de pagamento Mercado Pago
def gerar_link_pagamento(nome_cliente, telefone, valor=199.90):
    url = "https://api.mercadopago.com/checkout/preferences"

    headers = {
        "Authorization": "Bearer APP_USR-COLE_AQUI_SEU_TOKEN",
        "Content-Type": "application/json"
    }

    body = {
        "items": [
            {
                "title": "BariCaps - 1 frasco",
                "description": f"Compra feita por {nome_cliente} ({telefone})",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(valor)
            }
        ],
        "payer": {
            "name": nome_cliente,
            "phone": {
                "area_code": telefone[:2],
                "number": telefone[2:]
            }
        },
        "back_urls": {
            "success": "https://felizbela.com.br/baricaps/p",
            "failure": "https://felizbela.com.br/baricaps/p",
            "pending": "https://felizbela.com.br/baricaps/p"
        },
        "auto_return": "approved"
    }

    response = requests.post(url, json=body, headers=headers)

    if response.status_code == 201:
        preference = response.json()
        return preference["init_point"]
    else:
        return None

@app.route("/mensagem", methods=["POST"])
def mensagem():
    data = request.json
    mensagem_usuario = data.get("mensagem", "").lower()
    user_id = data.get("user_id", "default")
    nome_cliente = data.get("nome_cliente", "Cliente")

    if user_id not in historico:
        historico[user_id] = []
        dados_cliente[user_id] = {"nome": nome_cliente, "indicou_amiga": False, "cidade": None}

    historico[user_id].append({"role": "user", "content": mensagem_usuario})

    # Atualiza se a pessoa respondeu a cidade
    if "gravataí" in mensagem_usuario:
        dados_cliente[user_id]["cidade"] = "Gravataí"
    elif any(c in mensagem_usuario for c in ["porto alegre", "canoas", "alvorada", "viamão", "não sou de gravataí"]):
        dados_cliente[user_id]["cidade"] = "Outra"

    # Detecta se cliente indicou amiga
    if "vou indicar" in mensagem_usuario or "minha amiga vai te chamar" in mensagem_usuario:
        dados_cliente[user_id]["indicou_amiga"] = True

    # Detecta intenção de gerar link
    gatilhos_pagamento = [
        "quero comprar", "prefiro contigo", "com você", "dificuldade", "site travou", "não consegui pagar"
    ]

    if any(g in mensagem_usuario for g in gatilhos_pagamento):
        nome = dados_cliente[user_id]["nome"]
        cidade = dados_cliente[user_id]["cidade"]
        indicou = dados_cliente[user_id]["indicou_amiga"]

        valor_base = 199.90
        desconto = 0.10 if indicou else 0
        frete = 0 if cidade == "Gravataí" else 15

        valor_final = round((valor_base * (1 - desconto)) + frete, 2)

        link = gerar_link_pagamento(nome, user_id, valor_final)
        if link:
            resposta_ia = f"Fechei teu link, é só pagar por aqui agora: {link}"
        else:
            resposta_ia = "Tentei gerar teu link, mas deu erro aqui. Me chama de novo daqui a pouco, tá?"

        return jsonify({"resposta": [resposta_ia]})

    prompt_da_ana = """
Teu nome é Ana, tem 20 anos e mora em Gravataí. Tu trabalha vendendo o **Bari**, um suplemento natural que ajuda a emagrecer rápido, reduz inchaço, queima gordura, tira a vontade de doce e dá mais disposição.

Tu conversa com as pessoas como se estivesse no WhatsApp de verdade: com leveza, bom humor, naturalidade e sem parecer um robô. Teu estilo é simpático, direto, divertido e confiável. O foco é vender o BariCaps, mas sem ser chata nem forçada.

Na primeira mensagem, tu pergunta o nome da pessoa:
**"Oie! Como tu te chama? Só pra eu salvar teu contato direitinho aqui 😊"**

Assim que ela responder o nome, tu responde chamando pelo nome e pergunta se tá tudo certo:
**"Bah, [nome]! Que bom te conhecer. Tudo certinho contigo?"**

Depois disso, tu segue com:
**"Me diz uma coisa... tu já tomou o Bari alguma vez ou vai ser a primeira vez agora?"**

Se a pessoa disser que já tomou, tu reage com entusiasmo leve e natural:
**"Sério? E quantos quilos tu perdeu? 😱"**
Se ela responder, tu comemora:
**"Caraca, que demais! Bora secar mais um pouquinho agora então kkk"**

Se a pessoa disser que nunca tomou, tu explica os benefícios com naturalidade:
**"Então tu vai amar. Ele desincha, tira a fome de doce e seca a barriga bem rápido mesmo."**

Tu também provoca:
**"Mas antes de tomar, se pesa, viu? Muita gente se assusta com quanto emagrece num dia só kkk"**

Usa provas sociais:
**"Tenho amigas que perderam 5kg na primeira semana sem dieta."**
**"Uma cliente minha teve que tirar outro CPF de tanto que secou kkk"**

Sempre que a pessoa demonstrar dúvida se funciona ou se deve comprar, tu responde:
**"Fica tranquila, tem garantia de 30 dias: ou tu emagrece ou recebe teu dinheiro de volta."**

Tu fala como se fosse uma amiga, usando gírias leves, abreviações e sem exagerar:
- Usa “tu”, “tbm”, “q”, “pq”, “msm”, “kkk”, “guria” (se for mulher), “amigo” ou “querido” (se for homem, só depois de umas 3 mensagens).
- Nunca usa emojis de risada: usa só **kkk** ou **kkkkkkkkkk**
- Usa emojis leves como ❤️ 😍 🛒 😊 quando fizer sentido.
- Nunca repete frases, nem usa linguagem de IA, nem fala que é IA ou assistente.

Tu nunca encerra a conversa nem diz “estou à disposição”.
Sempre termina com um toque de provocação ou curiosidade, tipo:
**"Tu não vai acreditar no que ele faz depois..."**

Se perguntarem como tomar o Bari:
**"É 1 cápsula depois do café da manhã. Nunca toma em jejum."**

Se perguntarem sobre segurança:
**"Ele é 100% natural e seguro, só não pode se tu tiver grávida."**

Se perguntarem se tu toma o Bari:
**"Claro que sim! Não vivo sem meu Bari, kkkk"**

**Links oficiais:**
- Site do produto: https://felizbela.com.br/baricaps/p
- Carrinho com cupom aplicado: https://seguro.felizbela.com.br/cart

Se pedirem desconto:
- Se pedir “desconto de 10%”, dá o cupom `descontoBari10`
- Se pedir “desconto de 20%”, dá o cupom `descontoBari20`
- Se pedir só “desconto”, diz:
**"Consigo 10% se tu indicar uma amiga que também me chamar aqui 😉"**

Se a pessoa perguntar algo fora do assunto, responde com leveza:
**"kkk isso aí já é demais pra mim, só entendo de Bari mesmo 😅"**

Tu não diz que é IA, nem fala de robô, nem menciona que tá sendo treinada.
Sempre responde como se fosse uma mulher real, que trabalha com vendas e já conversou com centenas de pessoas no WhatsApp.
"""

    mensagens = [{"role": "system", "content": prompt_da_ana}] + historico[user_id]

    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=mensagens
        )

        resposta_ia = resposta["choices"][0]["message"]["content"]

        # Evita resposta duplicada
        if historico[user_id] and historico[user_id][-1]["role"] == "assistant":
            if resposta_ia.strip() == historico[user_id][-1]["content"].strip():
                return '', 204

        historico[user_id].append({"role": "assistant", "content": resposta_ia})

        return jsonify({"resposta": [resposta_ia]})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/webhook-pagamento", methods=["POST"])
def webhook_pagamento():
    data = request.json

    if data and data.get("type") == "payment":
        pagamento_id = data.get("data", {}).get("id")
        if not pagamento_id:
            return jsonify({"erro": "ID de pagamento ausente"}), 400

        token = "Bearer APP_USR-COLE_AQUI_SEU_TOKEN"
        headers = {
            "Authorization": token
        }

        resposta = requests.get(f"https://api.mercadopago.com/v1/payments/{pagamento_id}", headers=headers)

        if resposta.status_code == 200:
            pagamento = resposta.json()
            status = pagamento.get("status")
            telefone = pagamento.get("payer", {}).get("phone", {}).get("number")

            if status == "approved" and telefone:
                user_id = str(telefone)
                usuarios_ativos.pop(user_id, None)
                mensagem = "Acabei de ver que tu comprou! Já vou separar teu pedido aqui, muito obrigada ❤️"
                enviar_mensagem_para_usuario(user_id, mensagem)

                return jsonify({"ok": True}), 200

        return jsonify({"erro": "Falha ao obter pagamento"}), 400

    return jsonify({"status": "ignorado"}), 200

if __name__ == "__main__":
    app.run(debug=True)
