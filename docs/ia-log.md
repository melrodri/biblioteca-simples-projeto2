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

## Entrada 03 — Design da Aula 2

**Data:** 15/10/2026
**Ferramenta:** Claude (assistente da Anthropic).

### Pedido

Gerar o `specs/design.md` a partir do `specs/spec.md` e do enunciado: diagrama de arquitetura, modelo ER, rotas da API, Security Groups e ADR do RNF-04, respeitando as restrições do Learner Lab. Gerar também uma landing page simples para o bucket S3.

### O que a IA gerou

- Diagrama de arquitetura com S3 (site e capas), API Gateway, quatro Lambdas, RDS em subnets privadas e VPC Gateway Endpoint para o S3.
- Modelo ER com as tabelas `autor`, `livro` (1:N) e `capa` (1:1 com livro).
- Rotas da API, códigos de erro e a consulta SQL do relatório com `LEFT JOIN` e `GROUP BY`.
- Security Groups `sg-lambda` e `sg-rds`.
- ADR-001 (CRUD em Lambda) e ADR-002 (front-end estático no S3).
- Página `site/index.html` para o bucket S3.

### O que o grupo aceitou, rejeitou ou corrigiu

| Item | Decisão | Motivo |
| --- | --- | --- |
| CRUD em Lambda | Aceito | Mais simples e barato no Learner Lab; não depende de IP nem de instância ligada. |
| Tabela `capa` separada, uma capa por livro | Aceito | Evita metadados duplicados em eventos repetidos e mantém a tabela `livro` simples. |
| `LEFT JOIN` no relatório | Aceito | Garante que autores sem livros apareçam com zero, como pede a HU-06. |
| Front-end estático no S3 | Aceito | Sem servidor e com endereço fixo entre sessões. |
| Credenciais em variáveis de ambiente | Aceito | Cumpre o RNF-02 sem custo extra; Secrets Manager fica como possível bônus. |

## Entrada 04 — Revisão do design com GitHub Copilot

**Data:** 15/10/2026
**Ferramenta:** GitHub Copilot Chat (github.com/copilot), modo Ask, modelo Auto, com o repositório anexado como contexto. O Copilot abriu `specs/design.md` e `specs/spec.md`.

### Prompt utilizado

> Revise o arquivo specs/design.md do repositório melrodri/biblioteca-simples-projeto2, usando specs/spec.md como referência. [Resumo dos RF-01 a RF-05, RNF-01 a RNF-05 e restrições do Learner Lab.] Confira o diagrama de arquitetura, o modelo ER, as rotas da API, os Security Groups e os ADRs. Aponte erros, inconsistências com a especificação ou com as restrições do Learner Lab e sugira correções simples. Não gere código.

### O que o grupo aceitou, rejeitou ou corrigiu

| Sugestão do Copilot | Decisão | Motivo |
| --- | --- | --- |
| O diagrama mostrava o VPC Gateway Endpoint como um componente no caminho até o S3 | Aceita | O endpoint é uma rota da VPC, não um servidor. O diagrama passou a mostrar a Lambda acessando o S3 "via VPC Gateway Endpoint". |
| A tabela de Security Groups citava o endpoint como destino de regra | Aceita | Security Groups não referenciam Gateway Endpoints. A regra passou a ser HTTPS (443) liberado, e foi incluída uma nota explicando. |
| A Lambda `processa-capa` deve fazer `HeadObject` para obter tamanho e tipo reais | Aceita | Evita depender só dos dados do evento. Também passou a rejeitar arquivos fora de PNG/JPEG ou acima de 5 MB. |
| Detalhar o CORS do bucket e do API Gateway | Aceita | Foi incluída uma tabela com origens, métodos e cabeçalhos. |
| Informar que o site estático do S3 só tem HTTP | Aceita | Registrado no ADR-002; CloudFront fica como possível melhoria. |
| Deixar claro que `GET /livros/{id}/capa` devolve URL pré-assinada de leitura | Aceita | A rota passou a informar o tipo de URL, quem a gera e a validade. |
| Mencionar o atraso extra de Lambda dentro da VPC | Aceita | Incluído nas consequências do ADR-001. |
| Política de retenção das capas antigas | Corrigida | A imagem anterior fica no bucket e deixa de ser a capa atual; remoção manual se necessário, sem regra de ciclo de vida. |
| Política no endpoint restringindo o acesso ao bucket de capas | Rejeitada | O bucket já é privado e o acesso passa pela LabRole; mantemos a configuração padrão para simplificar no Learner Lab. |
| Secrets Manager para a senha do banco | Rejeitada por agora | Variáveis de ambiente já cumprem o RNF-02; Secrets Manager fica como possível bônus. |
| Provisioned Concurrency para reduzir cold start | Rejeitada | Gera custo contínuo e o atraso é aceitável para o uso previsto. |
| Corrigir "trechos truncados e acentuação" | Rejeitada | Conferimos o arquivo e não há trechos truncados; foi uma leitura incorreta da ferramenta. |

## Entrada 05 — Personas da especificação com GitHub Copilot

**Data:** 15/10/2026
**Ferramenta:** GitHub Copilot Chat (github.com/copilot), modo Ask, modelo Auto, com o repositório anexado como contexto.

### Prompt utilizado

> Com base no arquivo specs/spec.md do repositório melrodri/biblioteca-simples-projeto2, gere a seção de personas da especificação. O enunciado da Aula 1 pede 'personas' (no plural). Restrições: o sistema não tem login nem perfis de acesso; todas as personas são funcionários de uma pequena biblioteca que usam o mesmo sistema; não adicione funcionalidades novas além de autores, livros, capas, metadados da capa e relatório de livros por autor. Para cada persona (2 ou 3), traga: nome fictício, idade, função, familiaridade com tecnologia, objetivos, dificuldades atuais e quais histórias (HU-01 a HU-06) ela mais usa. Responda em português, em formato pronto para colar em Markdown. Não gere código.

### O que o Copilot gerou

Três personas: Ana Souza (bibliotecária chefe), João Pereira (assistente de acervo) e Marta Lima (atendimento ao público), cada uma com idade, função, familiaridade com tecnologia, objetivos, dificuldades e histórias mais usadas.

### O que o grupo aceitou, rejeitou ou corrigiu

| Sugestão do Copilot | Decisão | Motivo |
| --- | --- | --- |
| Personas com nome, idade, objetivos e dificuldades | Aceita | Deixa claro para quem o sistema é feito. |
| Três personas | Corrigida | Reduzimos para duas: a bibliotecária, que cadastra, e a atendente, que só consulta. O João fazia o mesmo que a Ana. |
| Ligação das personas às histórias | Corrigida | O Copilot trocou as histórias (por exemplo, citou a HU-03 como envio de capa e a HU-05 como consulta). Ajustamos conforme o spec. |
| Preenchimento manual dos metadados da capa | Rejeitada | Os metadados são registrados automaticamente pela Lambda (HU-05). |
| Busca de títulos, impressão e controle de duplicatas | Rejeitada | Fora do escopo; nomes e títulos repetidos são permitidos e diferenciados pelo ID. |
