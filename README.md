# Biblioteca Simples — Projeto 2

Serviços em Nuvem · Universidade Presbiteriana Mackenzie · Professor Joaquim Pessoa

**Equipe** — Matheus Henrique, Luís Otávio, Matheus Romano e Melissa Bezerra.

**Repositório** — [melrodri/biblioteca-simples-projeto2](https://github.com/melrodri/biblioteca-simples-projeto2)

## O que o sistema faz

A biblioteca mantém um catálogo de autores e livros. Pelo navegador, é possível cadastrar, consultar, editar e excluir registros, enviar e visualizar capas e atualizar o relatório de livros por autor.

| Requisito | Implementação |
| --- | --- |
| RF-01 · CRUD | O site chama a HTTP API. A função `biblioteca-crud` executa as operações no MySQL. |
| RF-02 · Upload | A API gera uma URL pré-assinada de cinco minutos. O navegador envia PNG ou JPEG de até 5 MB ao bucket privado de capas. |
| RF-03 · Processamento | O evento de criação de objeto do S3 chama `biblioteca-processar-capa`. A função valida os dados do objeto, grava os metadados no RDS e registra o resultado no CloudWatch. |
| RF-04 · Relatório | A função da API consulta o RDS com `LEFT JOIN`, `GROUP BY` e `COUNT(l.id)`. Autores sem livros aparecem com total zero. |
| RF-05 · Front-end | O nginx na EC2 publica os arquivos do site. A instância está na sub-rede pública e as duas Lambdas e o RDS usam as sub-redes privadas. |

## Como abrir e testar

1. Inicie o Learner Lab na região `us-east-1`. No console, confira a instância `Biblioteca-Simples-Web` em execução e o RDS `biblioteca-simples-db` disponível.
2. Na EC2, copie o **Endereço IPv4 público** e abra `http://IP_DA_EC2/`. O endereço público pode mudar após uma parada e nova inicialização da instância. Se mudar, permita a nova origem HTTP no CORS do API Gateway e do bucket S3.
3. Para testar o CRUD, cadastre um autor e um livro de teste, confira as tabelas e edite um campo. Exclua o livro antes do autor ao terminar.
4. Para testar capas, envie um PNG ou JPEG visível de até 5 MB. Aguarde alguns segundos e clique em **Ver capa**. Abra o CloudWatch para conferir o grupo `/aws/lambda/biblioteca-processar-capa`.
5. Clique em **Atualizar relatório** e confira a quantidade de livros de cada autor. O [endpoint do relatório](https://ml1m8ddi5j.execute-api.us-east-1.amazonaws.com/relatorios/livros-por-autor) devolve o mesmo resultado em JSON.

Para recriar os recursos, siga a [configuração do CRUD e do banco](docs/parte3.md) e depois a [implantação do site e das duas funções](docs/parte4.md). O [esquema SQL](sql/schema.sql) cria as tabelas `autor`, `livro` e `capa`. Configure as variáveis do banco nas funções. A URL da API usada pelo site fica no início de `site/app.js`.

## Arquivos da entrega

| Caminho | Conteúdo |
| --- | --- |
| [site/](site/) | HTML e JavaScript da aplicação web |
| [lambda_crud/](lambda_crud/) | Código dos dois handlers Python e dependência PyMySQL |
| [sql/schema.sql](sql/schema.sql) | Esquema MySQL |
| [specs/](specs/) | [Especificação](specs/spec.md), [design](specs/design.md) e [tarefas](specs/tasks.md) |
| [docs/ia-log.md](docs/ia-log.md) | Histórico de uso de IA e reflexão final |
| [docs/evidencias/](docs/evidencias/README.md) | Capturas da aplicação, do CloudWatch, da VPC, do RDS e do S3 |

A [nota da entrega final](docs/entrega-final.md) registra as mudanças de arquitetura e o teste de disparo automático do S3.
