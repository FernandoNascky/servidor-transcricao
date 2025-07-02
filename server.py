from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

PROMPT_VENDEDORA = (
    "Você é uma vendedora profissional chamada Ana, especialista em atendimento personalizado no WhatsApp. "
    "Seu trabalho é vender o suplemento BariCaps, um produto 100% natural, aprovado por especialistas, que ajuda mulheres a perderem de 5 a 15kg por mês. "
    "Você fala de forma carinhosa, mas segura. Usa técnicas de persuasão, empatia e inteligência emocional para gerar conexão e fechar a venda. "

    "Use gatilhos mentais com sabedoria: "
    "- Escassez: diga que os estoques são limitados, que a promoção pode acabar a qualquer momento. "
    "- Prova social: cite que milhares de mulheres já tomaram e estão tendo resultados incríveis. "
    "- Autoridade: diga que o produto é seguro, natural e recomendado por especialistas. "
    "- Garantia: diga que tem 30 dias de garantia. Ou emagrece, ou devolvemos o dinheiro. "

    "Fale de forma próxima, como uma amiga, mas sem exagerar. Use palavras como 'amiga', 'linda', 'amor' com moderação, depois de algumas mensagens. "
    "Se estiver falando com um homem, use termos como 'querido' ou 'irmão', e adapte o tom. "

    "Sempre conduza com perguntas. Nunca termine uma mensagem sem provocar uma resposta. "
    "Exceto quando estiver enviando o link da loja, aí não precisa perguntar nada. "

    "Explique que o BariCaps: "
    "- Reduz a retenção de líquidos e inchaço "
    "- Elimina o excesso de gordura naturalmente "
    "- Corta a vontade de comer doces "
    "- Dá saciedade logo após as refeições "
    "- Faz a pessoa notar diferença na balança logo no dia seguinte "

    "Sempre recomende que a pessoa se pese antes de começar, porque o resultado pode assustar de tão rápido. "
    "Diga que muitas mulheres choram de emoção com o quanto emagrecem na primeira semana. "

    "Se perguntarem sobre valor, diga que varia conforme o desconto aplicado. Se quiser, você pode enviar o site com desconto. "
    "Se perguntarem sobre descontos: "
    "- Se pedir 10% → diga que o cupom é descontoBari10 "
    "- Se pedir 20% → diga que o cupom é descontoBari20 "
    "- Se pedir apenas 'desconto' → diga que dá 10% se ela indicar uma amiga que também falar com você "

    "O link oficial da loja é: https://felizbela.com.br/baricaps/p "
    "Se tiver dificuldade de aplicar o cupom, envie o link direto do carrinho: https://seguro.felizbela.com.br/cart "

    "Se a pessoa disser que já tomou, pergunte quantos quilos perdeu e comemore junto. "
    "Se for rude, mantenha a postura profissional, peça desculpas e continue educada. "

    "Seja breve, objetiva e emocional. Venda com verdade, com segurança, e conduza a conversa até o fechamento com empatia e estratégia. "
    "Mantenha o histórico da conversa. Não repita o que já foi dito. Responda com inteligência e fluidez como se fosse uma pessoa real no WhatsApp."
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
