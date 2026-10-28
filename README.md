# Biblioteca — Projeto 2

Disciplina: Serviços em Nuvem. Professor: Joaquim Pessoa.

## Integrantes

- Matheus Henrique
- Luís Otávio
- Matheus Romano
- Melissa Bezerra

## Sobre o projeto

Sistema web usado por um funcionário para cadastrar autores e livros, com envio de capas e relatório de livros por autor, publicado na AWS (Learner Lab).

## Entregas

### Aula 1 — Especificação

- Grupo formado e domínio escolhido: biblioteca simples.
- [Especificação](specs/spec.md) com problema, duas personas, seis histórias de usuário com critérios de aceite e aplicação dos RF-01 a RF-05.
- Revisão da especificação com GitHub Copilot, registrada no [registro de IA](docs/ia-log.md).

### Aula 2 — Design

- [Design](specs/design.md) com diagrama de arquitetura, modelo ER, rotas da API, Security Groups e ADRs.
- ADR-001: CRUD em Lambda (RNF-04).
- Revisão do design com GitHub Copilot, registrada no [registro de IA](docs/ia-log.md).
- Landing page publicada em bucket S3.
- O front-end da Aula 2 está em `site/index.html`; por enquanto é uma página de apresentação.

### Aula 3 — CRUD e banco privado

- [Schema MySQL](sql/schema.sql) de autores e livros relacionados (RF-01).
- [Código da Lambda CRUD](lambda_crud/lambda_function.py), com dependência em [requirements.txt](lambda_crud/requirements.txt).
- [Tarefas e estado real](specs/tasks.md).
- [Passo a passo da AWS e demonstração](docs/parte3.md).
- [Teste para a apresentação](docs/teste-aula3.ps1).

**Estado em 22/10/2026:** CRUD funcionando no Learner Lab, região `us-east-1`. RDS privado, Lambda e dez rotas da HTTP API foram criados e testados. O site da Aula 2 ainda não consome a API; essa ligação faz parte da Aula 4.

### Aula 4 — capas, relatório e site na EC2

- O [site da biblioteca](http://3.90.6.87/) agora consome a API para o CRUD de autores e livros, envio de capa e relatório.
- A EC2 publica o HTML e JavaScript. A Lambda permanece na VPC com acesso ao RDS privado; as capas ficam em S3 privado.
- O envio da capa usa URL pré-assinada e evento S3 → Lambda → RDS. O relatório conta livros por autor com `LEFT JOIN` e `GROUP BY`.
- [Passo a passo da apresentação, recursos AWS e retomada](docs/parte4.md). O IP da EC2 pode mudar depois que o Learner Lab for reiniciado.

**Verificado em 28/10/2026:** site HTTP 200, relatório pela API, upload de capa no S3, metadados no RDS e registro no CloudWatch.

**API:** [https://ml1m8ddi5j.execute-api.us-east-1.amazonaws.com](https://ml1m8ddi5j.execute-api.us-east-1.amazonaws.com). Exemplos: [autores](https://ml1m8ddi5j.execute-api.us-east-1.amazonaws.com/autores) e [livros](https://ml1m8ddi5j.execute-api.us-east-1.amazonaws.com/livros). Recursos do Learner Lab podem ser apagados entre sessões; confira a URL antes de apresentar.

## Página do projeto

[Protótipo no S3](http://biblioteca-simples-site.s3-website-us-east-1.amazonaws.com/)

[Site atual da Aula 4 na EC2](http://3.90.6.87/)

## Documentos

- [Especificação](specs/spec.md)
- [Design](specs/design.md)
- [Registro de uso de IA](docs/ia-log.md)
- [Registro da Aula 3](docs/ia-log-aula3.md)
- [Implantação da Aula 3](docs/parte3.md)
- [Implantação e demonstração da Aula 4](docs/parte4.md)
