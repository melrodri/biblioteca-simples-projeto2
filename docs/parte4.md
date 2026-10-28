# Aula 4 — demonstração e implantação simples

## O que foi feito

- O mesmo CRUD da Aula 3 continua no API Gateway + Lambda + RDS MySQL, dentro da VPC.
- A página da Aula 2 agora chama a API para criar, listar, editar e excluir autores e livros.
- A página roda em uma EC2 pequena com nginx, na subnet pública. A EC2 só entrega HTML e JavaScript; o banco permanece privado.
- As capas ficam em um bucket S3 privado. A API fornece uma URL pré-assinada de 5 minutos; o navegador envia o arquivo diretamente ao S3. Um evento do S3 chama a Lambda, que registra a capa na tabela `capa` e escreve um log no CloudWatch.
- O relatório `GET /relatorios/livros-por-autor` usa `LEFT JOIN`, `GROUP BY` e `COUNT` no MySQL.

## Recursos desta conta (us-east-1)

| Recurso | Identificação |
| --- | --- |
| Site EC2 | `Biblioteca-Simples-Web`, `i-007e83fbe43bf7b03` |
| Endereço atual | http://3.90.6.87/ |
| VPC | `vpc-0b634a93cd9f5fff2` |
| Subnet pública da EC2 | `subnet-04bb6962f2ee002e2` |
| Subnets privadas | `subnet-0a910930095876a8a`, `subnet-0567b14bc7595a09e` |
| Grupo da EC2 | `sg-00ee31871d0141b94` — entrada HTTP 80 |
| Grupo da Lambda | `sg-01400ab7cdd6654a7` |
| Grupo do RDS | `sg-07731711a0a6d5d22` — entrada MySQL só da Lambda |
| Endpoint S3 da VPC | `vpce-0f86c7dc48fa4aa88` |
| RDS | `biblioteca-simples-db`, acesso público desativado |
| Lambda | `biblioteca-crud` |
| API | https://ml1m8ddi5j.execute-api.us-east-1.amazonaws.com |
| Bucket de capas | `biblioteca-capas-245273424999`, acesso público bloqueado |

Nenhuma senha é colocada no GitHub. As variáveis `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` e `CAPAS_BUCKET` ficam na configuração da Lambda. A função usa a LabRole do Learner Lab.

## Teste para mostrar ao professor (5 minutos)

1. Inicie o Learner Lab e confira se a EC2 `Biblioteca-Simples-Web` e o RDS `biblioteca-simples-db` estão em execução. Abra o [site da biblioteca](http://3.90.6.87/).
2. No site, cadastre um autor e um livro. Mostre os registros nas tabelas da página. Use **Editar** e **Excluir** em um registro de teste para demonstrar o CRUD. Exclua primeiro o livro, depois o autor.
3. Para um livro existente, clique em **Enviar capa** e escolha PNG ou JPEG de até 5 MB. Aguarde alguns segundos e clique em **Ver capa**. A imagem mostra que o S3 e o evento da Lambda funcionaram.
4. Clique em **Atualizar relatório**. A contagem de livros por autor vem da consulta SQL via API.
5. No console AWS, mostre a EC2 na subnet pública, o RDS com **Public access: No**, o bucket privado, a notificação de evento do bucket e o log `Capa processada` em `/aws/lambda/biblioteca-crud` no CloudWatch. Abra a VPC e mostre a subnet pública, as privadas e o endpoint S3.

Fala curta: “A EC2 hospeda somente o site. O API Gateway recebe as requisições, a Lambda executa o CRUD e consulta o RDS privado. Para a capa, a Lambda gera uma URL temporária, o navegador envia ao S3 e o evento do S3 registra a imagem no banco. O relatório conta livros por autor com JOIN e GROUP BY.”

## Retomada após reiniciar o Learner Lab

O IP público da EC2 pode mudar. Se mudar, abra a instância no console e copie o novo IP. Atualize a origem `http://NOVO_IP` no CORS da HTTP API e no CORS do bucket de capas (retire a origem antiga). O endereço da API em `site/app.js` só precisa mudar se a API for recriada. Se a EC2 tiver sido apagada, crie uma Amazon Linux 2023 `t3.micro` na subnet pública, associe `biblioteca-web`, instale nginx e copie `site/index.html` e `site/app.js` para `/usr/share/nginx/html/`. A Lambda é empacotada com `lambda_crud/lambda_function.py`, `sql/schema.sql` (como `schema.sql` na raiz do ZIP) e `pymysql` de `lambda_crud/requirements.txt`.

Na AWS Academy, pare a EC2 ao terminar a demonstração para poupar o orçamento do laboratório. Ao religá-la, confira o IP e o CORS novamente.

## Verificação realizada em 28/10/2026

- Página na EC2 respondeu HTTP 200.
- Relatório retornou a contagem de livros por autor.
- Upload de PNG por URL pré-assinada retornou HTTP 200 do S3.
- Consulta da capa retornou os metadados gravados no RDS e o CloudWatch registrou `Capa processada`.
