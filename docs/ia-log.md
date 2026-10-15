# Registro de uso de IA

## Entrada 01 — Especificação inicial da Aula 1

**Ferramenta utilizada:** Codex, assistente da OpenAI, nesta conversa.

### Solicitação utilizada

Resumo fiel do pedido do usuário nesta interação: preparar os arquivos da Aula 1 do Projeto 2 de Serviços em Nuvem, em português simples, para uma biblioteca com autores e livros em relação 1:N; produzir especificação com pelo menos cinco histórias e critérios de aceite, mapear RF-01 a RF-05 e restrições futuras, registrar honestamente o uso de IA, criar README e apresentação curta. Não implementar aplicação, criar AWS, antecipar arquitetura ou enviar conteúdo ao professor/Moodle. Preparar localmente sem link GitHub e incluir Melissa Bezerra como quarta integrante.

O domínio, as entidades, a simplificação de um autor por livro e as funcionalidades futuras de capa, metadados e relatório foram fornecidos pelo usuário. A lista dos três primeiros integrantes veio do projeto anterior; a quarta integrante foi informada nesta conversa.

### Saída produzida

- `specs/spec.md`: problema, público, persona ilustrativa, objetivo, escopo, seis histórias, critérios de aceite e correspondência com requisitos.
- `README.md`: integrantes, status verdadeiro, localização dos documentos, checklist e pendências do GitHub/Moodle.
- Roteiro de apresentação com fala e cinco perguntas para estudo (material de apoio, não incluído no repositório).
- Este registro de IA e um ZIP contendo os documentos do repositório.

### Simplificações e propostas

| Item | Origem e justificativa |
| --- | --- |
| Apenas autores e livros, sem empréstimos ou login | Escopo solicitado pelo usuário, para facilitar entendimento e entrega incremental. |
| Um autor por livro | Simplificação explícita do usuário; permite relação 1:N simples. |
| Lambda registra somente metadados da capa | Solicitado pelo usuário; evita processamento complexo de imagens. |
| Autor sem livros aparece com zero no relatório | Solicitado pelo usuário; evita omitir autores cadastrados. |
| Ano inteiro entre 1 e ano corrente; repetição de nomes/títulos permitida | Proposta desta IA para critérios verificáveis sem impor identidade pelo nome. |
| PNG/JPEG até 5 MB, uma capa atual por livro | Proposta desta IA para limitar e tornar o upload testável. |
| Eventos repetidos não duplicam metadados | Proposta desta IA para tratar repetições de eventos sem criar funcionalidades extras. |

## Entrada 02 — Revisão da especificação com GitHub Copilot

**Data:** 15/10/2026
**Ferramenta:** GitHub Copilot Chat (github.com/copilot), modo Ask, modelo Auto.

O envio ao repositório, a execução desta revisão no Copilot e a redação desta entrada foram feitos com ajuda do Claude (assistente da Anthropic), que também removeu do README um link para um arquivo não incluído.

### Prompt utilizado

Foi enviado o link de `specs/spec.md` no repositório, um resumo do enunciado (RF-01 a RF-05, RNF-01 a RNF-05 e restrições do Learner Lab) e o prompt sugerido na Entrada 01:

> Revise esta especificação da Aula 1 para uma biblioteca simples. Confira seis histórias com critérios testáveis, o mapeamento RF-01 a RF-05 e as restrições do Learner Lab. Preserve somente autores, livros, capas, metadados e relatório. Aponte inconsistências e sugira correções simples. Não gere código, arquitetura ou recursos AWS. Diferencie requisitos do enunciado de propostas que o grupo precisa aprovar.

### O que o Copilot sugeriu

- Reescrever as seis histórias no formato Dado/Quando/Então, com rotas de API e códigos HTTP (201, 204, 404).
- Personas diferentes: estudante/usuário final, administrador/bibliotecário e desenvolvedor.
- Campos extras: bio do autor; sinopse, ISBN e páginas do livro; largura/altura e flag `processed` da capa.
- Lambda do RF-03 gerando miniatura (thumbnail) além de gravar metadados.
- Relatório com média de páginas por autor e filtro por ano.
- Listar decisões pendentes: 1:N ou N:N, ação da Lambda, Lambda ou container no CRUD (ADR) e hospedagem do front-end.
- Documentar variáveis de ambiente e passos de recriação para novas sessões do Learner Lab.

### Observações

A resposta parece não ter usado o conteúdo real de `specs/spec.md`: cita campos, personas, autenticação de administrador e miniaturas que não existem na especificação e contrariam o escopo definido (sem login, sem processamento complexo de imagem). Várias sugestões já estão atendidas no arquivo atual (escolha 1:N, ação concreta da Lambda, ADR previsto para a Aula 2).


### O que o grupo aceitou, rejeitou ou corrigiu

| Sugestão do Copilot | Decisão | Motivo |
| --- | --- | --- |
| Login e perfil de administrador | Rejeitada | Fora do escopo: o sistema é usado por um funcionário, sem login. |
| Campos extras (bio, sinopse, ISBN, páginas, largura/altura) | Rejeitada | Mantemos só os dados necessários para o CRUD, a capa e o relatório. |
| Lambda gerar miniatura da capa | Rejeitada | A Lambda grava apenas chave, tamanho e tipo do arquivo, evitando processamento de imagem. |
| Relatório com média de páginas e filtro por ano | Rejeitada | O relatório fica só com a quantidade de livros por autor, que já atende ao RF-04. |
| Personas de estudante e desenvolvedor | Rejeitada | O único usuário do sistema é o funcionário da biblioteca. |
| Rotas de API e códigos HTTP nos critérios | Adiada | Serão definidas no `specs/design.md` (Aula 2). |
| Relação 1:N entre autor e livro | Aceita | Já estava na especificação; é a forma mais simples de atender ao RF-01. |
| ADR sobre Lambda ou container no CRUD | Aceita | Será feito na Aula 2, conforme o RNF-04. |
| Documentar variáveis de ambiente e passos para recriar o ambiente no Learner Lab | Aceita | Ajuda a cumprir o RNF-03; entrará no README quando houver infraestrutura. |
| Hospedagem do front-end | Adiada | Será decidida no `specs/design.md`. |

As propostas da Entrada 01 (ano entre 1 e o ano corrente, capas PNG/JPEG de até 5 MB e eventos repetidos sem duplicar metadados) foram aceitas e mantidas na especificação.
