# Tarefas — Biblioteca Simples

Estado em 22/10/2026. Os recursos da Aula 3 foram verificados no Learner Lab.

| ID | Requisito | Tarefa | Responsável | Estado |
|---|---|---|---|---|
| T-01 | RF-01 | Versionar o esquema MySQL de autor e livro | Grupo | Concluído; tabelas criadas no RDS |
| T-02 | RNF-01 | Criar duas subnets privadas, grupo de subnets e RDS sem acesso público | Grupo | Concluído; RDS disponível e privado |
| T-03 | RNF-01 | Criar `biblioteca-lambda` e `biblioteca-rds` com acesso MySQL restrito | Grupo | Concluído; entrada do RDS só da Lambda |
| T-04 | RF-01 | Publicar Lambda CRUD e executar evento `init_db` | Grupo | Concluído; resposta 200 |
| T-05 | RF-01 | Criar rotas HTTP API e demonstrar CRUD de autores e livros | Grupo | Concluído; dez rotas e testes HTTP realizados |
| T-06 | RNF-03/RNF-05 | Registrar IDs, endpoint sem segredos e passos de retomada | Grupo | Concluído em `docs/parte3.md` |
| T-07 | RF-02 | URL pré-assinada e bucket privado para capas | Grupo | Concluído; upload PNG testado no S3 |
| T-08 | RF-03 | Evento S3 processa capa na Lambda e grava no RDS | Grupo | Concluído; metadados e log CloudWatch verificados |
| T-09 | RF-04 | Relatório de livros por autor via API | Grupo | Concluído; consulta testada |
| T-10 | RF-05 | Front-end com CRUD e relatório publicado na EC2 | Grupo | Concluído; HTTP 200 verificado |
| T-11 | RNF-01 | Mostrar VPC, EC2, Lambda e RDS privado | Grupo | Concluído; detalhes em `docs/parte4.md` |
