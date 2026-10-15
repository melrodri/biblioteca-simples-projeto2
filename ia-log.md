# Registro de uso de IA

## Entrada 01 — Especificação inicial da Aula 1

**Ferramenta realmente utilizada:** Codex, assistente da OpenAI, nesta conversa. Os documentos desta entrega não foram gerados no GitHub Copilot. Não há evidência de revisão com Copilot até esta entrada.

### Solicitação utilizada

Resumo fiel do pedido do usuário nesta interação: preparar os arquivos da Aula 1 do Projeto 2 de Serviços em Nuvem, em português simples, para uma biblioteca com autores e livros em relação 1:N; produzir especificação com pelo menos cinco histórias e critérios de aceite, mapear RF-01 a RF-05 e restrições futuras, registrar honestamente o uso de IA, criar README e apresentação curta. Não implementar aplicação, criar AWS, antecipar arquitetura ou enviar conteúdo ao professor/Moodle. Preparar localmente sem link GitHub e incluir Melissa Bezerra como quarta integrante.

O domínio, as entidades, a simplificação de um autor por livro e as funcionalidades futuras de capa, metadados e relatório foram fornecidos pelo usuário. A lista dos três primeiros integrantes veio do projeto anterior; a quarta integrante foi informada nesta conversa.

### Saída produzida

- `specs/spec.md`: problema, público, persona ilustrativa, objetivo, escopo, seis histórias, critérios de aceite e correspondência com requisitos.
- `README.md`: integrantes, status verdadeiro, localização dos documentos, checklist e pendências do GitHub/Moodle.
- Roteiro de apresentação com fala e cinco perguntas para estudo (material de apoio, não incluído no repositório).
- Este registro de IA e um ZIP contendo os documentos do repositório.

### Simplificações e propostas

| Item | Origem e justificativa | Situação |
| --- | --- | --- |
| Apenas autores e livros, sem empréstimos ou login | Escopo solicitado pelo usuário, para facilitar entendimento e entrega incremental. | Requisito recebido; leitura final do grupo pendente |
| Um autor por livro | Simplificação explícita do usuário; permite relação 1:N simples. | Requisito recebido |
| Lambda registra somente metadados da capa | Solicitado pelo usuário; evita processamento complexo de imagens. | Planejado |
| Autor sem livros aparece com zero no relatório | Solicitado pelo usuário; evita omitir autores cadastrados. | Planejado |
| Ano inteiro entre 1 e ano corrente; repetição de nomes/títulos permitida | Proposta desta IA para critérios verificáveis sem impor identidade pelo nome. | A revisar pelo grupo |
| PNG/JPEG até 5 MB, uma capa atual por livro | Proposta desta IA para limitar e tornar o upload testável. | A revisar pelo grupo |
| Eventos repetidos não duplicam metadados | Proposta desta IA para tratar repetições de eventos sem criar funcionalidades extras. | A revisar pelo grupo |

### Aceites, rejeições e correções

Não foi registrado aceite final do grupo para o conteúdo gerado. Nenhuma rejeição técnica do grupo foi informada. A inclusão de Melissa Bezerra foi solicitada pelo usuário; não representa aprovação dos demais documentos.

Ainda falta revisar a clareza das histórias, validar os critérios propostos e conferir se cada integrante consegue explicar o escopo. Não foram realizados testes da aplicação, deploys, convites ao professor ou envios ao Moodle.

## Revisão obrigatória pendente no GitHub Copilot

O enunciado exige GitHub Copilot em todas as etapas. Esta geração no Codex, por si só, não comprova esse requisito. O grupo deve realizar e registrar uma revisão real com Copilot antes de marcar a pendência como concluída.

Prompt sugerido, para enviar ao Copilot com `specs/spec.md` e o enunciado como contexto:

> Revise esta especificação da Aula 1 para uma biblioteca simples. Confira seis histórias com critérios testáveis, o mapeamento RF-01 a RF-05 e as restrições do Learner Lab. Preserve somente autores, livros, capas, metadados e relatório. Aponte inconsistências e sugira correções simples. Não gere código, arquitetura ou recursos AWS. Diferencie requisitos do enunciado de propostas que o grupo precisa aprovar.

Depois da revisão, acrescentar uma entrada com data, ferramenta, prompt efetivamente usado, sugestões reais, o que o grupo aceitou/rejeitou/corrigiu e os motivos. Não preencher essa entrada antecipadamente nem atribuir ao Copilot os arquivos já gerados aqui.

