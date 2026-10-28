// URL estável da API. O IP da EC2 não fica no código.
const API = 'https://ml1m8ddi5j.execute-api.us-east-1.amazonaws.com';
const campo = id => document.getElementById(id);
let capaLivro = null;

function aviso(texto) { campo('status').textContent = texto; }
async function api(rota, metodo = 'GET', dados) {
  const opcoes = { method: metodo, headers: {} };
  if (dados !== undefined) {
    opcoes.headers['Content-Type'] = 'application/json';
    opcoes.body = JSON.stringify(dados);
  }
  const resposta = await fetch(API + rota, opcoes);
  const corpo = await resposta.json();
  if (!resposta.ok) throw new Error(corpo.erro || 'Erro na API.');
  return corpo;
}
function botao(texto, acao) {
  const b = document.createElement('button');
  b.textContent = texto; b.className = 'small'; b.onclick = acao;
  return b;
}
function celula(linha, texto) {
  const c = linha.insertCell(); c.textContent = texto; return c;
}
async function carregar() {
  const [autores, livros] = await Promise.all([api('/autores'), api('/livros')]);
  const escolha = campo('autor-id');
  escolha.replaceChildren(new Option('Escolha o autor', ''));
  autores.forEach(a => escolha.add(new Option(a.nome, a.id)));
  campo('autores').replaceChildren();
  autores.forEach(a => {
    const linha = campo('autores').insertRow(); celula(linha, a.nome);
    linha.insertCell().append(
      botao('Editar', () => {
        const nome = prompt('Nome do autor:', a.nome);
        if (nome !== null) executar(() => api('/autores/' + a.id, 'PUT', {nome}));
      }),
      botao('Excluir', () => excluir('/autores/' + a.id))
    );
  });
  campo('livros').replaceChildren();
  livros.forEach(l => {
    const linha = campo('livros').insertRow();
    celula(linha, l.titulo); celula(linha, l.ano_publicacao); celula(linha, l.autor_nome);
    const capa = linha.insertCell();
    capa.append(botao('Ver capa', () => verCapa(l.id, capa)));
    linha.insertCell().append(
      botao('Editar', () => editarLivro(l)),
      botao('Excluir', () => excluir('/livros/' + l.id)),
      botao('Enviar capa', () => { capaLivro = l.id; campo('arquivo').click(); })
    );
  });
}
async function executar(acao) {
  try { await acao(); await carregar(); aviso('Operação concluída.'); }
  catch (erro) { aviso(erro.message); }
}
campo('form-autor').onsubmit = evento => {
  evento.preventDefault();
  executar(async () => { await api('/autores', 'POST', {nome: campo('nome').value}); campo('nome').value = ''; });
};
campo('form-livro').onsubmit = evento => {
  evento.preventDefault();
  executar(async () => {
    await api('/livros', 'POST', {
      titulo: campo('titulo').value, ano_publicacao: Number(campo('ano').value),
      autor_id: Number(campo('autor-id').value)
    });
    campo('titulo').value = ''; campo('ano').value = '';
  });
};
function editarLivro(l) {
  const titulo = prompt('Título:', l.titulo);
  if (titulo === null) return;
  const ano = prompt('Ano:', l.ano_publicacao);
  if (ano === null) return;
  const autor = prompt('ID do autor:', l.autor_id);
  if (autor !== null) executar(() => api('/livros/' + l.id, 'PUT', {
    titulo, ano_publicacao: Number(ano), autor_id: Number(autor)
  }));
}
function excluir(rota) {
  if (confirm('Excluir este registro?')) executar(() => api(rota, 'DELETE'));
}
async function verCapa(id, cel) {
  try {
    const capa = await api('/livros/' + id + '/capa');
    const imagem = document.createElement('img');
    imagem.className = 'capa'; imagem.alt = 'Capa do livro'; imagem.src = capa.url;
    cel.replaceChildren(imagem);
  } catch (erro) { aviso(erro.message); }
}
campo('arquivo').onchange = async () => {
  const arquivo = campo('arquivo').files[0];
  if (!arquivo || !capaLivro) return;
  if (!['image/png', 'image/jpeg'].includes(arquivo.type) || arquivo.size > 5 * 1024 * 1024) {
    aviso('Use PNG ou JPEG de até 5 MB.'); return;
  }
  try {
    const dados = await api('/livros/' + capaLivro + '/capa/url-upload', 'POST', {tipo_conteudo: arquivo.type});
    const resposta = await fetch(dados.url, {method: 'PUT', headers: {'Content-Type': arquivo.type}, body: arquivo});
    if (!resposta.ok) throw new Error('Falha no envio ao S3.');
    aviso('Capa enviada. Aguarde alguns segundos e clique em Ver capa.');
  } catch (erro) { aviso(erro.message); }
  campo('arquivo').value = '';
};
campo('ver-relatorio').onclick = async () => {
  try {
    const itens = await api('/relatorios/livros-por-autor');
    campo('relatorio').replaceChildren();
    itens.forEach(item => {
      const linha = campo('relatorio').insertRow();
      celula(linha, item.nome); celula(linha, item.quantidade_livros);
    });
    aviso('Relatório atualizado.');
  } catch (erro) { aviso(erro.message); }
};
carregar().catch(erro => aviso('API indisponível: ' + erro.message));
