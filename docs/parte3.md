# Implantação da Aula 3 — Biblioteca Simples

Esta etapa acrescenta o CRUD de autores e livros ao [projeto existente](https://github.com/melrodri/biblioteca-simples-projeto2). Foi preparada a partir de `specs/spec.md` e `specs/design.md` do repositório. O front-end `site/index.html` da Aula 2 já existe e foi preservado: é uma página de apresentação, sem formulários ou chamadas à API. O CRUD da Aula 3 é demonstrado pela API.

Os recursos da Aula 2 foram criados em outra conta AWS. Isso não impede a Aula 3: a API e o banco abaixo foram criados nesta conta do Learner Lab. O código do site continua no mesmo repositório.

## Recursos criados no Learner Lab

Região: `us-east-1`. Conta do laboratório: `245273424999`. Estes recursos podem ser temporários; confira os IDs antes da apresentação.

| Recurso | Identificador / configuração |
|---|---|
| VPC padrão | `vpc-0b634a93cd9f5fff2`, CIDR `172.31.0.0/16` |
| Subnet pública existente | `subnet-04bb6962f2ee002e2` (`us-east-1a`), rota para Internet Gateway |
| Subnets privadas novas | `subnet-0a910930095876a8a` (`172.31.96.0/24`, `us-east-1a`) e `subnet-0567b14bc7595a09e` (`172.31.97.0/24`, `us-east-1b`) |
| Tabela das subnets privadas | `rtb-0601e30058df2b19b`, somente rota local; sem NAT nem Internet Gateway |
| Grupos de segurança | Lambda: `sg-01400ab7cdd6654a7`; RDS: `sg-07731711a0a6d5d22` |
| Grupo de subnets do banco | `biblioteca-db-subnets` |
| RDS MySQL | `biblioteca-simples-db`, classe `db.t3.micro`, 20 GiB, acesso público desativado; endpoint `biblioteca-simples-db.c4lkpxpnwhdg.us-east-1.rds.amazonaws.com` |
| Lambda | `biblioteca-crud`, Python 3.12, `LabRole`, nas duas subnets privadas |
| HTTP API | `ml1m8ddi5j`, [URL da API](https://ml1m8ddi5j.execute-api.us-east-1.amazonaws.com) |

O RDS aceita TCP 3306 apenas do grupo da Lambda. A Lambda não recebe conexões de entrada e sua saída é restrita a TCP 3306 para o grupo do RDS. A senha foi gerada no CloudShell e guardada fora do repositório. Não publique `DB_PASSWORD` nem capturas das variáveis de ambiente.

## Verificação feita na AWS

- Evento direto `{"action":"init_db"}` na Lambda: resposta 200, tabelas prontas.
- `GET` e `POST` em `/autores` e `/livros`; `GET`, `PUT` e `DELETE` por ID: respostas esperadas. A API contém as dez rotas do design.
- Nome vazio e ano futuro: 400; autor inexistente no cadastro de livro: 400; livro inexistente: 404; exclusão de autor com livro: 409.
- CORS: `OPTIONS /autores` respondeu 204 e liberou a origem HTTP do site S3.
- Exemplo deixado no banco: autor `Machado de Assis` (ID 1) e livro `Dom Casmurro` (ID 1). Os registros temporários usados para testar exclusão foram removidos.
- O roteiro `docs/teste-aula3.ps1` foi executado novamente em 22/10/2026: consultou 1 autor e 1 livro, criou e editou registros temporários, recebeu 409 no bloqueio e apagou os temporários. O exemplo principal continuou no banco.

Esses resultados pertencem à sessão do Learner Lab em 22/10/2026. Confira a API novamente antes da demonstração: [autores](https://ml1m8ddi5j.execute-api.us-east-1.amazonaws.com/autores) e [livros](https://ml1m8ddi5j.execute-api.us-east-1.amazonaws.com/livros).

## Arquivos para acrescentar ao repositório

- `sql/schema.sql`: tabelas `autor` e `livro`, com relação 1:N e exclusão de autor restrita.
- `lambda_crud/lambda_function.py`: uma Lambda para as dez operações CRUD descritas em `specs/design.md`.
- `lambda_crud/requirements.txt`: única dependência externa, PyMySQL.
- `specs/tasks.md`: tarefas e estado real da entrega. Ajustar responsáveis e estado com o grupo.
- `.gitignore`: impede o envio do pacote gerado ao repositório.
- `README.md`: registra a Aula 3 e aponta para este roteiro.
- `docs/ia-log-aula3.md`: registro curto do apoio de IA nesta etapa; preserve também `docs/ia-log.md` das Aulas 1 e 2.
- `docs/teste-aula3.ps1`: teste curto para repetir o CRUD na apresentação sem apagar o exemplo principal.

Copie estes arquivos para as mesmas pastas no repositório, sem substituir `site/index.html`, `specs/spec.md`, `specs/design.md` ou `docs/ia-log.md`. Antes da apresentação, o grupo deve atribuir nomes reais às tarefas em `specs/tasks.md` e revisar o código para conseguir explicá-lo.

## Preparar a Lambda no computador

Na pasta `lambda_crud`, com Python e `pip` instalados, execute no PowerShell:

```powershell
New-Item -ItemType Directory -Force pacote | Out-Null
python -m pip install -r requirements.txt -t pacote
Copy-Item lambda_function.py pacote/
Copy-Item ../sql/schema.sql pacote/
Compress-Archive -Path pacote/* -DestinationPath biblioteca-crud.zip -Force
```

O arquivo ZIP contém `lambda_function.py` e `schema.sql` na raiz, junto com `pymysql`. Não inclua senhas nem o diretório `pacote` no GitHub.

## Criar a infraestrutura no Learner Lab

Use uma única região para todos os recursos. Anote no seu ambiente os IDs dos recursos, sem registrar senhas no repositório.

1. Inicie a sessão do Learner Lab e abra o console AWS. Escolha uma VPC existente apropriada ou crie uma VPC com uma subnet pública e duas subnets privadas em zonas de disponibilidade diferentes. A subnet pública tem rota para Internet Gateway. As tabelas de rotas das subnets privadas não devem ter rota para Internet Gateway ou NAT Gateway. A subnet pública não precisa hospedar o CRUD.
2. Crie o grupo `biblioteca-lambda` com **nenhuma entrada** e saída TCP 3306 para `biblioteca-rds`. Crie `biblioteca-rds` com entrada TCP 3306 **somente de `biblioteca-lambda`**. Mantenha a saída padrão do RDS. Não abra 3306 para `0.0.0.0/0`.
3. No RDS, crie um MySQL pequeno e de instância única dentro de um DB subnet group com as duas subnets privadas. Desative `Public access`. Associe `biblioteca-rds`. Defina o nome inicial do banco como `biblioteca` (ou registre o nome escolhido). Guarde usuário e senha fora do repositório.
4. Crie a função Lambda `biblioteca-crud` a partir de `biblioteca-crud.zip`, com handler `lambda_function.lambda_handler` e a `LabRole` permitida pelo laboratório. Associe-a à mesma VPC, às subnets privadas e a `biblioteca-lambda`. Configure as variáveis `DB_HOST` (endpoint DNS do RDS), `DB_PORT` (`3306`), `DB_NAME`, `DB_USER` e `DB_PASSWORD` no console. O endpoint DNS evita IP fixo no código. Comece com timeout de 15 segundos e aumente apenas se um teste concreto exigir.
5. No console da Lambda, invoque **diretamente** um evento de teste com `{"action":"init_db"}`. Confirme a resposta `Tabelas autor e livro prontas.`. Esse evento não é uma rota HTTP. Se falhar, veja CloudWatch Logs, VPC, grupos de segurança, nome do banco e credenciais.
6. Crie uma HTTP API no API Gateway, com integração Lambda no formato de payload `2.0`. Use o estágio `$default` com implantação automática. Aponte as rotas abaixo para `biblioteca-crud`. A integração pelo console deve configurar a permissão de invocação da Lambda; se não configurar, ajuste-a no API Gateway/Lambda.

| Método | Rota |
|---|---|
| GET, POST | `/autores` |
| GET, PUT, DELETE | `/autores/{id}` |
| GET, POST | `/livros` |
| GET, PUT, DELETE | `/livros/{id}` |

Configure CORS na HTTP API para a origem exata do site S3 já publicado. Use métodos `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS` e cabeçalho `Content-Type`. Na Aula 3 é suficiente demonstrar as chamadas pela URL da API; o site ainda é apenas um protótipo.

## Demonstração mínima

Antes da aula, inicie o Learner Lab e confirme que o RDS está como **Available** e a Lambda como **Active**. Abra os links de [autores](https://ml1m8ddi5j.execute-api.us-east-1.amazonaws.com/autores) e [livros](https://ml1m8ddi5j.execute-api.us-east-1.amazonaws.com/livros) no navegador. Eles devem mostrar Machado de Assis e Dom Casmurro em JSON.

Para mostrar o CRUD completo sem apagar esse exemplo, abra o PowerShell na pasta `docs` do repositório e execute `.\teste-aula3.ps1 -Apresentacao`. O roteiro cria um autor e um livro temporários e **pausa** para vocês atualizarem as páginas de autores e livros no navegador. Depois edita o livro e pausa novamente; confirma o erro **409** ao tentar excluir o autor antes do livro; por fim, apaga os dois registros temporários. Pressione Enter a cada pausa. Se quiser apenas conferir rapidamente, execute `.\teste-aula3.ps1` sem a opção de apresentação. Se falhar no meio, o roteiro imprime os IDs que podem precisar de limpeza.

Se o PowerShell bloquear scripts, cole o conteúdo do arquivo no terminal ou use as chamadas pelo Postman. Para testar manualmente, use os IDs retornados pelo cadastro, sem presumir que serão 1 e 2. Na apresentação, mostre a API respondendo, o RDS com acesso público desativado, o DB subnet group e as regras dos dois grupos de segurança.

## Retomada do Learner Lab

Ao iniciar nova sessão, confira se o RDS está disponível e se a Lambda, API e VPC ainda existem. Se o banco ou a API foram recriados, atualize `DB_HOST`/demais variáveis e a URL usada nos testes. Reexecute `init_db` apenas para criar tabelas ausentes; `CREATE TABLE IF NOT EXISTS` não apaga dados existentes. Nenhum IP público é usado no código. Se a sessão apagar os recursos, repita os passos acima e atualize a documentação com os IDs novos. Ao encerrar os testes, desligue recursos cobrados por hora conforme as regras do laboratório.

## Próxima etapa

Upload de capas (RF-02), evento S3 → Lambda → RDS (RF-03), relatório (RF-04) e front-end consumindo a API (RF-05) pertencem à Aula 4. Eles continuam como planejados no design, sem afirmação de implementação nesta entrega.
