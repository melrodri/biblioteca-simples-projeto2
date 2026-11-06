# Etapa final — Biblioteca Simples

## Alterações

- O site continua hospedado na EC2. O API Gateway aciona `biblioteca-crud` para o cadastro de autores e livros, o relatório e a geração de URLs pré-assinadas para as capas.
- O S3 aciona `biblioteca-processar-capa` quando um objeto é criado em `capas/`. A função valida o tipo e o tamanho do arquivo, grava os metadados no RDS e registra o processamento no CloudWatch.
- As funções usam as duas sub-redes privadas existentes. O RDS tem acesso público desativado. Para consultar o objeto no S3, a Lambda usa o endpoint de gateway da VPC e a saída HTTPS na porta 443.
- A capa de *Dom Casmurro* foi substituída por uma imagem visível no site.

## Validação do RF-03

Um upload real pela API, com URL pré-assinada, criou um PNG de 32.693 bytes no S3 para o livro de teste 12. A notificação do S3 acionou a Lambda automaticamente. O grupo `/aws/lambda/biblioteca-processar-capa` registrou `Capa processada: livro 12, 32693 bytes.`. A API devolveu os metadados e o link para a mesma imagem.

## Entrega

O ZIP para o Moodle reúne código-fonte, SQL, README, especificações, registro de uso de IA com reflexão final e sete evidências em [`docs/evidencias/`](evidencias/README.md). Entre elas estão as capturas do objeto novo no S3 e do processamento automático no CloudWatch.
