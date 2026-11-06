# Tarefas — Biblioteca Simples

Estado da entrega final. As tarefas da Aula 3 registram a validação feita na etapa correspondente.

| ID | Requisito | Tarefa | Responsável | Estado |
|---|---|---|---|---|
| T-01 | RF-01 | Versionar o esquema MySQL de autor e livro | Grupo | Concluído; tabelas criadas no RDS |
| T-02 | RNF-01 | Criar duas subnets privadas, grupo de subnets e RDS sem acesso público | Grupo | Concluído; RDS disponível e privado |
| T-03 | RNF-01 | Criar `biblioteca-lambda` e `biblioteca-rds` com acesso MySQL restrito | Grupo | Concluído; entrada do RDS só da Lambda |
| T-04 | RF-01 | Publicar Lambda CRUD e executar evento `init_db` | Grupo | Concluído; resposta 200 |
| T-05 | RF-01 | Criar rotas HTTP API e demonstrar CRUD de autores e livros | Grupo | Concluído; dez rotas e testes HTTP realizados |
| T-06 | RNF-03/RNF-05 | Registrar IDs, endpoint sem segredos e passos de retomada | Grupo | Concluído em `docs/parte3.md` |
| T-07 | RF-02 | URL pré-assinada e bucket privado para capas | Grupo | Concluído; upload PNG testado no S3 |
| T-08 | RF-03 | Evento S3 processa capa na Lambda e grava no RDS | Grupo | Validado na configuração original da Aula 4. Para as duas funções, consulte T-12. |
| T-09 | RF-04 | Relatório de livros por autor via API | Grupo | Concluído; consulta testada |
| T-10 | RF-05 | Front-end com CRUD e relatório publicado na EC2 | Grupo | Concluído; HTTP 200 verificado |
| T-11 | RNF-01 | Mostrar VPC, EC2, Lambda e RDS privado | Grupo | Concluído; detalhes em `docs/parte4.md` |
| T-12 | RF-03 | Separar a função de processamento do S3 da função da API | Grupo | Implantado. Upload real pela API acionou a Lambda automaticamente. Registro no CloudWatch e leitura da capa conferidos. |
| T-13 | RF-02/RF-05 | Confirmar a exibição de capa e o relatório no site publicado | Grupo | Concluído. Captura em `docs/evidencias/` |
| T-14 | Final | Revisar a documentação e reunir fontes, SQL e evidências | Grupo | Concluído no pacote final |
