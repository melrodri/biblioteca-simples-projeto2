# Design — Biblioteca Simples

Este documento descreve como o sistema será construído na AWS (Learner Lab): arquitetura, modelo de dados, rotas da API, regras de rede e decisões de arquitetura (ADRs). Ele parte da especificação em [`specs/spec.md`](spec.md).

## 1. Diagrama de arquitetura
Arquitetura implantada na Aula 4:

```text
Navegador → EC2 (nginx, HTML/JS) → API Gateway → Lambda biblioteca-crud → RDS MySQL
                         │                                 │
                         └── URL pré-assinada → S3 capas ──┘
                                                  evento de upload
```

A EC2 está na subnet pública da VPC. A Lambda e o RDS estão nas subnets privadas; a Lambda acessa o S3 por um VPC Gateway Endpoint. A imagem abaixo é o desenho inicial da Aula 2, antes da decisão de publicar o site na EC2.
<img width="1600" height="783" alt="WhatsApp Image 2026-10-16 at 09 34 34" src="https://github.com/user-attachments/assets/2aedd9a0-aa17-443b-b259-c11b85c6cde8" />

### Componentes

| Componente | Função no sistema | Requisito |
| --- | --- | --- |
| EC2 (nginx) | Hospeda o front-end simples (HTML, CSS e JavaScript) na subnet pública. | RF-05 |
| API Gateway (HTTP API) | Recebe as chamadas do front-end e encaminha para a Lambda correta. CORS configurado para a origem do site. | RF-01, RF-02, RF-04 |
| Lambda `crud` | Cadastro, consulta, edição e exclusão de autores e livros. | RF-01 |
| Lambda `biblioteca-crud` | Além do CRUD, confere o livro e gera a URL pré-assinada para envio da capa. | RF-02 |
| S3 (bucket de capas) | Guarda as imagens das capas. Privado; o acesso é feito só por URLs pré-assinadas. CORS liberado para o site. | RF-02 |
| Lambda `biblioteca-crud` | Também recebe o evento do S3, registra a capa no RDS e executa o relatório com JOIN e GROUP BY. Uma função mantém o projeto pequeno. | RF-03, RF-04 |
| Amazon RDS (MySQL, db.t3.micro) | Banco relacional com autores, livros e capas. Em subnet privada, sem acesso público. | RF-01, RNF-01 |
| VPC Gateway Endpoint (S3) | Rota associada às tabelas de rota das subnets privadas. Permite que a Lambda `processa-capa`, dentro da VPC, acesse o S3 sem internet e sem NAT Gateway. Não é um servidor nem aparece em regras de Security Group. | Learner Lab |

A Lambda usa a **LabRole**. Nenhuma role IAM é criada.

### Fluxo de envio da capa

1. O funcionário escolhe a imagem no site.
2. O site chama `POST /livros/{id}/capa/url-upload` informando o tipo do arquivo.
3. A Lambda `biblioteca-crud` confere se o livro existe e se o tipo é PNG ou JPEG, e devolve uma URL pré-assinada válida por 5 minutos, com a chave `capas/{livro_id}/{uuid}.{extensao}`.
4. O navegador envia a imagem direto ao bucket de capas usando essa URL.
5. O S3 dispara a mesma Lambda `biblioteca-crud`, que tira o `livro_id` da chave e faz um `HeadObject` no S3 para obter tamanho e tipo reais do arquivo. Se o arquivo for válido (PNG/JPEG até 5 MB), grava os dados na tabela `capa`; caso contrário, registra o erro no CloudWatch e não associa a capa.

A imagem anterior de um livro continua no bucket, mas deixa de ser a capa atual. A remoção de arquivos antigos é feita manualmente, se necessário.

## 2. Modelo de dados (ER)

<img width="605" height="1600" alt="WhatsApp Image 2026-10-16 at 09 34 34 (1)" src="https://github.com/user-attachments/assets/f774b3ef-a2d3-45b0-8fa5-1524a965f60d" />

| Tabela | Campos | Regras |
| --- | --- | --- |
| `autor` | `id` (PK, auto incremento), `nome` (varchar 150, obrigatório) | Não pode ser excluído enquanto tiver livros. |
| `livro` | `id` (PK, auto incremento), `titulo` (varchar 200, obrigatório), `ano_publicacao` (int, obrigatório), `autor_id` (FK → `autor.id`, obrigatório) | Relação **1:N**: um autor tem zero ou vários livros; cada livro tem um autor. A FK usa `ON DELETE RESTRICT`. |
| `capa` | `livro_id` (PK e FK → `livro.id`), `s3_chave` (único), `tamanho_bytes`, `tipo_conteudo`, `atualizado_em` | Relação **1:1** com livro: cada livro tem no máximo uma capa atual. Um novo envio substitui a linha. Ao excluir o livro, a capa é excluída junto (`ON DELETE CASCADE`). |

Como `livro_id` é a chave da tabela `capa`, um evento repetido do S3 apenas atualiza a mesma linha e não duplica metadados.

## 3. Rotas da API

Base: endereço do API Gateway. Corpo e respostas em JSON.

| Método | Rota | O que faz | Lambda |
| --- | --- | --- | --- |
| GET | `/autores` | Lista os autores | `crud` |
| GET | `/autores/{id}` | Consulta um autor | `crud` |
| POST | `/autores` | Cadastra um autor | `crud` |
| PUT | `/autores/{id}` | Edita o nome do autor | `crud` |
| DELETE | `/autores/{id}` | Exclui o autor (só se não tiver livros) | `crud` |
| GET | `/livros` | Lista os livros com o nome do autor | `crud` |
| GET | `/livros/{id}` | Consulta um livro | `crud` |
| POST | `/livros` | Cadastra um livro | `crud` |
| PUT | `/livros/{id}` | Edita título, ano e autor | `crud` |
| DELETE | `/livros/{id}` | Exclui o livro | `crud` |
| POST | `/livros/{id}/capa/url-upload` | Gera a URL pré-assinada para enviar a capa | `biblioteca-crud` |
| GET | `/livros/{id}/capa` | Retorna os metadados da capa e uma URL pré-assinada de leitura (GET), válida por 5 minutos, para exibi-la | `crud` |
| GET | `/relatorios/livros-por-autor` | Quantidade de livros por autor | `biblioteca-crud` |

### Respostas de erro

| Código | Quando acontece |
| --- | --- |
| 400 | Dados inválidos (nome ou título vazio, ano fora do intervalo, tipo de arquivo não aceito) |
| 404 | Autor, livro ou capa não encontrado |
| 409 | Tentativa de excluir autor que ainda tem livros |

### Exemplos

`POST /livros`

```json
{ "titulo": "Dom Casmurro", "ano_publicacao": 1899, "autor_id": 1 }
```

`GET /relatorios/livros-por-autor`

```json
[
  { "autor_id": 1, "nome": "Machado de Assis", "quantidade_livros": 2 },
  { "autor_id": 2, "nome": "Clarice Lispector", "quantidade_livros": 0 }
]
```

Consulta usada no relatório:

```sql
SELECT a.id AS autor_id, a.nome, COUNT(l.id) AS quantidade_livros
FROM autor a
LEFT JOIN livro l ON l.autor_id = a.id
GROUP BY a.id, a.nome
ORDER BY a.nome;
```

O `LEFT JOIN` mantém autores sem livros, e `COUNT(l.id)` conta zero para eles.

## 4. Rede e Security Groups

| Recurso | Configuração |
| --- | --- |
| VPC | VPC padrão do Learner Lab |
| EC2 | Subnet pública, nginx na porta HTTP 80 |
| Subnets privadas | Duas subnets em zonas diferentes (exigência do RDS), sem rota para a internet |
| RDS | Nessas subnets, com **acesso público desativado** |
| Endpoint | VPC Gateway Endpoint do S3 associado à tabela de rotas das subnets privadas |
| NAT Gateway | Não utilizado |

| Security Group | Entrada | Saída |
| --- | --- | --- |
| `sg-lambda` | Nenhuma | MySQL (3306) com destino `sg-rds`; HTTPS (443) para o prefixo do S3 pelo endpoint |
| `sg-rds` | MySQL (3306) somente a partir de `sg-lambda` | Padrão |
| `biblioteca-web` | HTTP (80) da internet | Saída padrão para instalar o nginx |

A regra do RDS aponta para outro Security Group, não para um IP. Assim, nada depende de endereço fixo.

O acesso ao S3 a partir da VPC passa pelo Gateway Endpoint por meio da tabela de rotas; o endpoint não é referenciado nos Security Groups.

### CORS

| Onde | Configuração |
| --- | --- |
| Bucket de capas | Origem: endereço do site. Métodos: `PUT` e `GET`. Cabeçalho permitido: `Content-Type`. |
| API Gateway | Origem: endereço do site. Métodos: `GET`, `POST`, `PUT`, `DELETE` e `OPTIONS`. Cabeçalho permitido: `Content-Type`. |

## 5. Configuração e segredos

- Host, usuário, senha e nome do banco ficam em **variáveis de ambiente** das Lambdas, preenchidas no console.
- O nome do bucket de capas também fica em variável de ambiente.
- Nenhuma senha ou chave é salva no repositório (RNF-02).
- O endereço da API usado pelo front-end fica no início de `site/app.js`, atualizado se a API for recriada.
- O passo a passo para recriar os recursos numa nova sessão do Learner Lab ficará no README (RNF-03, RNF-05).

## 6. ADRs

### ADR-001 — CRUD em Lambda

**Contexto.** O RNF-04 pede para decidir se o CRUD de autores e livros roda em Lambda ou em container (EC2/ECS). O sistema tem pouco acesso, roda no Learner Lab (orçamento limitado e sessão que expira) e já usa Lambda nos RF-03 e RF-04.

**Opções consideradas.**

| | Lambda | Container em EC2/ECS |
| --- | --- | --- |
| Custo | Cobra só pelas execuções | Cobra enquanto a instância estiver ligada |
| Learner Lab | Continua funcionando após reiniciar a sessão; não depende de IP | A instância para com a sessão e o IP público muda |
| Manutenção | Sem servidor para administrar | Sistema operacional, Docker e porta para configurar |
| Integração | Direta com API Gateway, já usado no RF-04 | Exige integração do API Gateway com a instância ou um balanceador |
| Desvantagens | Atraso na primeira chamada (cold start) e limite de 15 minutos por execução | Mais configuração e risco de esquecer a instância ligada |

**Decisão.** O CRUD roda em **Lambda**, atrás do API Gateway, dentro da VPC para acessar o RDS.

**Consequências.**

- Toda a API segue o mesmo padrão (API Gateway + Lambda), o que simplifica o projeto.
- A EC2 serve somente os arquivos estáticos; o CRUD não depende dela para processar requisições.
- A primeira chamada após um tempo parado pode demorar alguns segundos, um pouco mais por a Lambda estar dentro da VPC. É aceitável para o uso previsto.
- Cada execução abre conexão com o banco. Com pouco uso, isso não é um problema.

### ADR-002 — Front-end estático na EC2

**Contexto.** O RF-05 exige um front-end publicado consumindo a API.

**Decisão.** Publicar o front-end simples (HTML, CSS e JavaScript) com nginx numa EC2, conforme pedido do professor. O bucket S3 continua reservado às capas privadas.

**Consequências.** A turma pode mostrar a EC2 e a VPC no console. O site chama a API Gateway e o navegador envia a capa diretamente ao S3; por isso a origem HTTP da EC2 precisa estar no CORS de ambos. Ao reiniciar a EC2, o IP público pode mudar e essas origens devem ser atualizadas. O site usa HTTP, adequado apenas à demonstração no Learner Lab.
