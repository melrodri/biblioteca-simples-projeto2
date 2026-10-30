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


