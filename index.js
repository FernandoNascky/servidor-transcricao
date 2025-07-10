const venom = require('venom-bot');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

const caminhoArquivo = path.join(__dirname, 'clientes.json');
let dadosClientes = {};

if (fs.existsSync(caminhoArquivo)) {
  try {
    dadosClientes = JSON.parse(fs.readFileSync(caminhoArquivo));
  } catch (e) {
    console.error('Erro ao ler clientes.json:', e);
  }
}

function salvarDados() {
  fs.writeFileSync(caminhoArquivo, JSON.stringify(dadosClientes, null, 2));
}

venom
  .create({
    session: 'botzap',
    multidevice: true,
    headless: true,
    useChrome: true,
    disableWelcome: true,
    disableSpins: true,
  })
  .then((client) => start(client))
  .catch((erro) => console.error('Erro ao iniciar VenomBot:', erro));

async function start(client) {
  const historico = {};
  const ultimoContato = {};
  const sugestoes = [
    'Skol', 'Brahma', 'Antarctica', 'Itaipava',
    'Amstel', 'Heineken', 'Budweiser', 'Original',
    'Schin', 'Cristal', 'Polar Export'
  ];

  setInterval(async () => {
    const numeroFernando = '5551989518151@c.us';
    const mensagem = 'Oi! Chegou bebida nova no Depósito Espuma 🍻. Quer experimentar umas novidades top?';
    try {
      await client.sendText(numeroFernando, mensagem);
    } catch (err) {
      console.error('Erro ao enviar mensagem automática:', err);
    }
  }, 60 * 60 * 1000);

  setInterval(async () => {
    const agora = Date.now();
    for (const numero in ultimoContato) {
      if (agora - ultimoContato[numero] > 15 * 60 * 1000) {
        const proxima = sugestoes[Math.floor(Math.random() * sugestoes.length)];
        await client.sendText(numero, `Tava aqui pensando... já provou a ${proxima}?`);
        ultimoContato[numero] = agora;
      }
    }
  }, 60 * 1000);

  client.onMessage(async (message) => {
    if (message.isGroupMsg || !message.body) return;

    const from = message.from;
    const texto = message.body.trim();
    ultimoContato[from] = Date.now();

    if (!(from in dadosClientes)) {
      dadosClientes[from] = { nome: null, endereco: null, telefone: from, ultimosPedidos: [], historico: [] };
      salvarDados();
      await client.sendText(from, 'Oi! Eu sou a Ana do Depósito Espuma 🍻. Qual é o teu nome?');
      return;
    }

    if (dadosClientes[from].nome === null) {
      const nome = texto.split(' ')[0];
      dadosClientes[from].nome = nome;
      salvarDados();
      console.log(`Nome salvo para ${from}: ${nome}`);
      await client.sendText(from, `Prazer, ${nome}! Como posso te ajudar hoje?`);
      return;
    }

    if (!historico[from]) historico[from] = [];
    historico[from].push({ role: 'user', content: texto });
    if (historico[from].length > 30) historico[from] = historico[from].slice(-30);

    dadosClientes[from].historico = historico[from];
    salvarDados();

    const memoriaPedido = dadosClientes[from].ultimosPedidos.length > 0 ? `
Se esse número já pediu antes, lembra que o último pedido foi: ${dadosClientes[from].ultimosPedidos.join(', ')}.` : '';

    const prompt = [
      {
        role: 'system',
        content: `
Tu é a Ana, atendente do Depósito de Bebidas Espuma, em Gravataí.
Fala como uma guria simpática e leve.
Nunca corta frases no meio entre mensagens. Cada mensagem deve terminar a frase antes de começar outra.
Evita gírias pesadas, mas pode usar "chefe" com cliente recorrente.
Sempre que o cliente mandar mensagem, vê se já tem um pedido anterior e pergunta se vai querer o mesmo.
${memoriaPedido}
Sugestões:
- Skol (lata 350 ml – R$ 3,99 ou combo com 10 por R$ 36)
- Brahma (lata 350 ml – R$ 2,99 ou combo com 10 por R$ 27)
- Antarctica (lata 350 ml – R$ 3,29 ou combo com 10 por R$ 30)
- Itaipava (lata 350 ml – R$ 2,99 ou combo com 10 por R$ 27)
- Amstel (lata 350 ml – R$ 4,49 ou combo com 10 por R$ 42)
- Heineken (long neck 330 ml – R$ 6,89 ou combo com 10 por R$ 65)
- Budweiser (lata 350 ml – R$ 3,60 ou combo com 10 por R$ 34)
- Original (lata 350 ml – R$ 4,29 ou combo com 10 por R$ 40)
- Schin (lata 350 ml – R$ 3,19 ou combo com 10 por R$ 30)
- Cristal (long neck 355 ml – R$ 3,99 ou combo com 10 por R$ 36)
- Polar Export (garrafa 600 ml – R$ 5,90 ou litrão 1 L por R$ 8,50 – combo 10 por R$ 79)
Nunca diga que é uma IA nem robô.
Respostas com no máximo 50 caracteres por mensagem, mas sempre terminando a frase antes de quebrar.`
      },
      ...historico[from]
    ];

    try {
      const resp = await axios.post(
        'https://api.openai.com/v1/chat/completions',
        {
          model: 'gpt-3.5-turbo',
          messages: prompt,
          temperature: 0.75,
        },
        {
          headers: {
         Authorization: `Bearer ${process.env.OPENAI_KEY}`
            'Content-Type': 'application/json'
          }
        }
      );

      const iaResposta = resp.data.choices[0].message.content.trim();
      const ultimaResposta = historico[from].slice().reverse().find(m => m.role === 'assistant');

      if (!ultimaResposta || ultimaResposta.content !== iaResposta) {
        const frases = iaResposta.match(/[^.!?]+[.!?]/g) || [iaResposta];

        for (const frase of frases) {
          const partes = frase.match(/.{1,50}/g);
          for (const parte of partes) {
            await client.sendText(from, parte.trim());
          }
        }

        historico[from].push({ role: 'assistant', content: iaResposta });
      }

      const cervejas = sugestoes.filter(c => texto.toLowerCase().includes(c.toLowerCase()));
      if (cervejas.length > 0) {
        dadosClientes[from].ultimosPedidos = cervejas;
        salvarDados();
      }

    } catch (e) {
      console.error('Erro IA:', e.response?.data || e.message);
      await client.sendText(from, 'Opa, deu um errinho aqui… tenta de novo mais tarde, tá bom?');
    }
  });
}
