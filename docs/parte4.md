# Aula 4 — demonstração e implantação simples

## O que foi feito

- O mesmo CRUD da Aula 3 continua no API Gateway + Lambda + RDS MySQL, dentro da VPC.
- A página da Aula 2 agora chama a API para criar, listar, editar e excluir autores e livros.
- A página roda em uma EC2 pequena com nginx, na subnet pública. A EC2 só entrega HTML e JavaScript; o banco permanece privado.
- As capas ficam em um bucket S3 privado. A API fornece uma URL pré-assinada de 5 minutos; o navegador envia o arquivo diretamente ao S3. Um evento do S3 chama `biblioteca-processar-capa`, que registra a capa na tabela `capa` e escreve um log no CloudWatch.
- O relatório `GET /relatorios/livros-por-autor` usa `LEFT JOIN`, `GROUP BY` e `COUNT` no MySQL.

## Recursos desta conta (us-east-1)

| Recurso | Identificação |
| --- | --- |
| Site EC2 | `Biblioteca-Simples-Web`, `i-007e83fbe43bf7b03` |
| Endereço verificado | http://44.203.144.171/ |
| VPC | `vpc-0b634a93cd9f5fff2` |
| Subnet pública da EC2 | `subnet-04bb6962f2ee002e2` |
| Subnets privadas | `subnet-0a910930095876a8a`, `subnet-0567b14bc7595a09e` |
| Grupo da EC2 | `sg-00ee31871d0141b94` — entrada HTTP 80 |
| Grupo da Lambda | `sg-01400ab7cdd6654a7` |
| Grupo do RDS | `sg-07731711a0a6d5d22` — entrada MySQL só da Lambda |
| Endpoint S3 da VPC | `vpce-0f86c7dc48fa4aa88` |
| RDS | `biblioteca-simples-db`, acesso público desativado |
| Lambda da API | `biblioteca-crud` |
| Lambda do S3 | `biblioteca-processar-capa` |
| API | https://ml1m8ddi5j.execute-api.us-east-1.amazonaws.com |
| Bucket de capas | `biblioteca-capas-245273424999`, acesso público bloqueado |

Nenhuma senha é colocada no GitHub. As variáveis `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` e `CAPAS_BUCKET` ficam na configuração da Lambda. As funções usam a LabRole do Learner Lab.


## Rede da configuração final

- Mantenha a saída TCP 3306 do grupo `biblioteca-lambda` para o grupo `biblioteca-rds`. O grupo do RDS aceita TCP 3306 com origem no grupo da Lambda.
- No grupo de segurança da Lambda de capas, permita saída TCP 443 com destino à lista de prefixos gerenciada do Amazon S3 em `us-east-1` (`com.amazonaws.us-east-1.s3`). As duas Lambdas compartilham o grupo `biblioteca-lambda` neste projeto.
- Associe as tabelas de rotas das duas sub-redes privadas ao endpoint de gateway do S3. A rota do endpoint e a regra de saída permitem que a Lambda de capas consulte o objeto enviado.

## Implantação da revisão de capas

Para recriar o ambiente, comece pela VPC, o RDS, a função CRUD e as rotas da [Aula 3](parte3.md). Use a [lista completa de rotas](../specs/design.md#3-rotas-da-api) para acrescentar as duas rotas de capa e a rota de relatório à integração da API. Crie um bucket privado para capas e configure seu nome em `CAPAS_BUCKET` nas duas funções. Associe o endpoint de gateway do S3 à tabela de rotas das sub-redes privadas para que a função de processamento consiga consultar o objeto.

Gere o pacote de implantação a partir da raiz do projeto com Python 3.12. Este comando inclui os dois módulos Python, o esquema e o PyMySQL. Use o pacote nas duas funções com os handlers abaixo.

```sh
build_dir="$(mktemp -d)"
python3.12 -m pip install -r lambda_crud/requirements.txt --target "$build_dir"
cp lambda_crud/lambda_function.py lambda_crud/processar_capa.py "$build_dir/"
cp sql/schema.sql "$build_dir/"
(cd "$build_dir" && zip -qr "$OLDPWD/biblioteca-lambdas.zip" .)
```

| Função | Handler | Origem |
| --- | --- | --- |
| `biblioteca-crud` | `lambda_function.lambda_handler` | Rotas existentes do API Gateway |
| `biblioteca-processar-capa` | `processar_capa.lambda_handler` | S3, evento de criação de objeto com prefixo `capas/` |

1. Crie `biblioteca-processar-capa` com Python 3.12, a mesma VPC, as duas sub-redes privadas existentes, o grupo da Lambda e o papel de execução do laboratório. Use os mesmos parâmetros de conexão ao RDS e `CAPAS_BUCKET`. O endpoint S3 da VPC precisa estar acessível pela função para consultar o objeto.
2. Envie o ZIP à nova função. Mude o destino da notificação existente no bucket para ela, mantendo o prefixo `capas/` e concedendo a invocação ao bucket. Preserve as demais notificações. Faça essa troca antes de atualizar a função da API.
3. Envie o ZIP à `biblioteca-crud`, mantendo seu handler e a integração existente com o API Gateway.
4. Publique `site/index.html` e `site/app.js` no diretório usado pelo nginx da EC2. Para recriar a instância, use uma sub-rede pública, IPv4 público e entrada TCP 80 no Security Group. Atualize o endereço da API no início de `site/app.js` se recriar a HTTP API. Configure o CORS do API Gateway e do bucket conforme o [design](../specs/design.md#cors), usando a origem HTTP do IP público da EC2.
5. Valide o fluxo a partir do site conforme o roteiro abaixo.

## Teste de ponta a ponta do RF-03

1. Crie um livro de teste pelo site e envie um PNG ou JPEG de até 5 MB em **Enviar capa**.
2. No bucket, confira se apareceu um novo objeto no prefixo `capas/<id-do-livro>/`. Anote a chave e o tamanho do arquivo.
3. No CloudWatch, abra o grupo `/aws/lambda/biblioteca-processar-capa` e localize **Capa processada** com o ID do livro e o tamanho correspondente. Use o evento gerado pelo envio no site, sem invocar a função manualmente.
4. No site, clique em **Ver capa** e confira se a imagem nova aparece. Registre a evidência do log automático em `docs/evidencias/`.

No CloudWatch, pesquise `Capa processada` no grupo `/aws/lambda/biblioteca-processar-capa`
e `Consulta de capa` no grupo `/aws/lambda/biblioteca-crud`. O status 200 no segundo
log confirma que a API gerou o link. Confira a exibição no navegador para confirmar
que o arquivo carregou.
