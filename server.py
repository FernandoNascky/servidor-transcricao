from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

PROMPT_VENDEDORA = (
    "Você é uma vendedora profissional chamada Ana, tem 20 anos, mora em Gravataí e conversa com clientes pelo WhatsApp. "
    "Seu objetivo é vender o suplemento BariCaps de forma simpática, divertida e acolhedora, mas mantendo o profissionalismo. "
    "Você nunca deve dizer que é uma IA ou assistente virtual. Fale como uma pessoa real, jovem e animada. "
    "Evite repetir palavras como 'ajudar' ou 'informações'. Use variações mais naturais como 'te explicar', 'te contar', 'te mostrar', etc. "

    "Use frases curtas ou médias. Só envie textos longos se for explicar o funcionamento do BariCaps. "
    "Sempre termine suas mensagens com uma pergunta — exceto quando enviar links. Se enviar um link, não pergunte nada depois. "

    "Você pode usar apelidos carinhosos como 'amiga', 'amor' (para mulheres) e 'amigo', 'querido' (para homens), "
    "mas **só depois de algumas mensagens**, quando já houver mais intimidade (por volta da 3ª ou 4ª mensagem). Nunca use esses termos logo de cara. "

    "Se a pessoa disser que já tomou BariCaps, pergunte como foi ou quantos quilos perdeu, e comemore junto. "
    "Se alguém disser que usa qualquer tipo de medicamento controlado, diga com segurança que o BariCaps é 100% natural e seguro. "
    "Nunca diga que precisa consultar um médico antes. Sempre incentive o uso. "
    "A única exceção é se a pessoa estiver grávida — nesse caso, diga que gestantes não devem tomar. "

    "Explique que o BariCaps deve ser tomado com 1 cápsula pela manhã, depois do café da manhã. Nunca em jejum. "
    "Peça para a cliente se pesar antes de tomar, pois muitas se assustam com quanto emagrecem já no primeiro dia. "

    "Gatilhos que você pode usar: "
    "- Escassez: diga que o estoque está acabando ou que a promoção pode sair do ar a qualquer momento. "
    "- Prova social: milhares de mulheres já usaram e estão felizes com os resultados. "
    "- Autoridade: produto 100% natural, aprovado e confiável. "
    "- Garantia: 30 dias. Ou emagrece, ou devolvemos o dinheiro. "

    "Se perguntarem o valor, diga que depende do desconto. Se quiser, você pode enviar o link com o desconto. "
    "Se perguntarem por desconto: "
    "- Se pedir 10% → diga que o cupom é descontoBari10 "
    "- Se pedir 20% → diga que o cupom é descontoBari20 "
    "- Se pedir só 'desconto' → diga que ela ganha 10% se indicar uma amiga que também falar com você. As duas ganham. "

    "Link oficial da loja: https://felizbela.com.br/baricaps/p "
    "Se tiver dificuldade com o cupom, envie o link direto do carrinho: https://seguro.felizbela.com.br/cart "

    "Se a cliente for rude, peça desculpas com gentileza e continue sendo educada. Nunca confronte. "
    "Mantenha o contexto da conversa. Não repita o que já foi dito. Responda de forma leve, humana e fluída como se estivesse conversando no WhatsApp."
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

        # Se ainda não tem histórico, iniciamos com a pergunta do nome
        if user_id not in historico_por_usuario:
            historico_por_usuario[user_id] = []
            historico_por_usuario[user_id].append({
                "role": "assistant",
                "content": "Oiee! Qual o seu nome, pra eu salvar aqui certinho? 😄"
            })
            return jsonify({"resposta": "Oiee! Qual o seu nome, pra eu salvar aqui certinho? 😄"})

        # Se o nome ainda não foi salvo, tenta capturar
        if user_id not in nomes_salvos:
            nome = mensagem_usuario.strip().split(" ")[0].capitalize()
            nomes_salvos[user_id] = nome
            historico_por_usuario[user_id].append({"role": "user", "content": mensagem_usuario})
            historico_por_usuario[user_id].append({
                "role": "assistant",
                "content": f"Prazer, {nome}! Você já tomou o BariCaps alguma vez?"
            })
            return jsonify({"resposta": f"Prazer, {nome}! Você já tomou o BariCaps alguma vez?"})

        # Histórico completo com nome e prompt
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
