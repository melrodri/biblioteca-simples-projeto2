# Registro de IA — Aula 3

**Ferramenta:** Codex (OpenAI), em 22/10/2026.

**Pedido principal:** implementar a parte 3 da Biblioteca Simples a partir de `specs/spec.md` e `specs/design.md`, mantendo a solução pequena e usando o Learner Lab.

**Resultado:** sugestão do esquema SQL, de uma Lambda CRUD para autores e livros e dos passos de implantação. O código foi colocado no RDS/Lambda/API Gateway e as dez rotas foram testadas ao vivo. A página `site/index.html` da Aula 2 foi preservada.

**Decisões e correções:** usamos uma única Lambda e PyMySQL; mantivemos o RDS sem acesso público, em duas subnets privadas, e restringimos o MySQL ao grupo da Lambda. A senha ficou fora do repositório. Reduzimos o tamanho da senha gerada para respeitar o limite aceito pelo RDS. RF-02 a RF-05 ficaram para a Aula 4, conforme o enunciado.

O grupo deve revisar estes arquivos e conseguir explicar o fluxo antes da apresentação.
