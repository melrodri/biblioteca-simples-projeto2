# Especificação inicial — Biblioteca Simples

**Estado:** funcionalidades planejadas, não implementadas. Documento preparado em 15/10/2026 para revisão do grupo na Aula 1.

## Problema e público

Um funcionário precisa manter um catálogo simples de autores e livros. Anotações separadas dificultam localizar um título, corrigir dados e contar quantos livros estão associados a cada autor. O sistema reunirá essas informações em uma aplicação web.

Público-alvo: funcionários responsáveis pelo cadastro do catálogo de uma pequena biblioteca.

Persona ilustrativa, sem representar uma pessoa real: um funcionário que usa o computador para cadastrar e consultar livros, mas não tem conhecimentos técnicos de nuvem. Ele precisa de campos claros e mensagens simples quando um cadastro não puder ser salvo.

## Objetivo e limites

Permitir o cadastro, a consulta, a edição e a exclusão de autores e livros relacionados. Futuramente, permitir uma capa por livro, registrar informações dessa imagem e mostrar a quantidade de livros por autor.

Ficam fora: empréstimos, reservas, multas, pagamentos, login, perfis de acesso, pesquisa avançada e outras funcionalidades extras. Não haverá processamento complexo de imagens. O cadastro não representa exemplares físicos nem controla empréstimos ou estoque.

## Entidades e relacionamento

| Entidade | Dados iniciais previstos |
| --- | --- |
| Autor | ID e nome |
| Livro | ID, título, ano de publicação e ID do autor |

ID é um identificador único gerado pelo sistema. Um autor pode ter zero ou vários livros; cada livro deve pertencer a exatamente um autor existente. Esse relacionamento é chamado **1:N (um para muitos)**. Livros com vários autores não fazem parte desta simplificação.

Para a etapa de capas, também será necessário associar ao livro a chave do objeto no S3, o tamanho em bytes e o tipo de conteúdo. A organização desses dados no banco será definida na Aula 2; não foi definida uma entidade adicional nesta entrega.

Regras propostas para revisão: nomes e títulos devem conter ao menos um caractere que não seja espaço; ano de publicação deve ser um número inteiro entre 1 e o ano corrente; nomes de autores e títulos repetidos serão permitidos, pois a identificação será feita pelo ID. O nome sozinho não identifica necessariamente uma pessoa única.

## Histórias de usuário e critérios de aceite

Todos os critérios abaixo são condições para testes futuros, não resultados de testes já realizados.

### HU-01 — Manter autores

Como funcionário, quero cadastrar, consultar, editar e excluir autores para manter o catálogo atualizado.

- Ao salvar um nome válido, o autor recebe um ID e aparece na consulta.
- Nome vazio ou composto somente por espaços impede o cadastro ou a atualização e apresenta uma mensagem.
- A consulta permite ver o ID e o nome dos autores cadastrados.
- A edição de um autor existente altera seu nome e conserva seu ID.
- A exclusão de um autor sem livros remove-o da consulta.
- A exclusão de um autor com livros é impedida, informa o motivo e preserva autor e livros.
- Uma operação sobre um ID inexistente informa que o autor não foi encontrado e não altera dados.

### HU-02 — Manter livros

Como funcionário, quero cadastrar, consultar, editar e excluir livros para manter os dados do catálogo corretos.

- O cadastro válido recebe um ID e apresenta título, ano e autor na consulta.
- Título vazio ou composto somente por espaços impede salvar e apresenta uma mensagem.
- Ano ausente, não inteiro ou fora do intervalo de 1 ao ano corrente impede salvar e informa a regra.
- A edição permite alterar título, ano e autor, conserva o ID e mostra os dados atualizados na consulta.
- A exclusão de um livro existente retira esse livro da consulta e preserva o autor.
- Uma operação sobre um ID inexistente informa que o livro não foi encontrado e não altera dados.
- Depois de recarregar a página, cadastros e alterações continuam disponíveis no banco; exclusões continuam efetivadas.

### HU-03 — Associar livro e autor

Como funcionário, quero escolher um autor existente ao cadastrar ou editar um livro para relacionar corretamente o catálogo.

- O formulário permite selecionar entre os autores cadastrados.
- Sem autor selecionado, o livro não é salvo.
- Um ID de autor inexistente é rejeitado pelo backend, mesmo que seja enviado fora do formulário.
- Alterar o autor de um livro associa-o ao novo autor e preserva os demais dados.
- A consulta de livros mostra o nome correspondente ao autor associado.

### HU-04 — Enviar capa de um livro

Como funcionário, quero enviar uma imagem de capa para um livro existente para identificá-lo visualmente.

- A aplicação solicita ao backend uma URL pré-assinada, isto é, uma autorização temporária para enviar um arquivo específico ao Amazon S3.
- O navegador envia a imagem diretamente ao S3, sem que o backend receba o conteúdo do arquivo para retransmiti-lo.
- A autorização é vinculada a um livro existente; livro inexistente é rejeitado.
- A proposta inicial aceita PNG e JPEG de até 5 MB; formato ou tamanho inválido gera mensagem e não fica associado como capa válida.
- Após envio e processamento bem-sucedidos, a capa fica vinculada ao livro correspondente e pode ser visualizada na aplicação.
- Uma falha de envio é informada, sem apresentar a capa como concluída.
- Cada livro exibe uma capa atual; um novo envio válido substitui a associação da capa anterior. A política de retenção dos objetos antigos será definida na arquitetura.

### HU-05 — Registrar informações da capa automaticamente

Como funcionário, quero que o sistema registre informações da imagem enviada sem digitá-las manualmente, para conferir sua associação e características.

- A criação da imagem no S3 dispara uma função Lambda, código executado pela AWS em resposta a um evento.
- A função identifica o livro destinatário e grava no RDS a chave do objeto, o tamanho em bytes e o tipo de conteúdo obtidos do arquivo no S3.
- Após processamento bem-sucedido, os três dados correspondem ao objeto enviado e ao livro correto.
- Um evento repetido do mesmo objeto não cria outra associação de capa nem duplica os metadados.
- Um objeto sem associação válida a livro não altera outro cadastro e gera um registro de erro para investigação.

Utilidade: a **chave do objeto** localiza o arquivo e o associa ao livro; o **tamanho em bytes** permite conferir o volume armazenado; o **tipo de conteúdo** identifica como tratar e exibir o arquivo. Não será necessário redimensionar ou analisar visualmente a imagem.

### HU-06 — Consultar quantidade de livros por autor

Como funcionário, quero consultar a quantidade de livros por autor para conhecer a distribuição do catálogo.

- O relatório mostra ID, nome do autor e quantidade de livros associados, uma linha por autor.
- Um autor sem livros aparece com quantidade zero.
- Autores de mesmo nome aparecem separadamente por ID.
- Após cadastrar, mudar de autor ou excluir um livro, uma nova consulta reflete a alteração.
- Se não houver autores, a resposta contém uma lista vazia, sem inventar registros.
- A implementação prevista usa consulta com JOIN (junção de dados de tabelas relacionadas) e GROUP BY (agrupamento para calcular contagens), executada em Lambda e exposta pelo API Gateway. Será necessário preservar autores sem livros na junção e contar IDs de livros, não linhas vazias.

## Aplicação futura dos requisitos funcionais

| Requisito | Aplicação na biblioteca | Histórias | Estado |
| --- | --- | --- | --- |
| RF-01 | CRUD completo (criar, consultar, atualizar e excluir) de autores e livros, relacionados e persistidos no Amazon RDS, serviço gerenciado de banco de dados relacional. | HU-01, HU-02, HU-03 | Planejado |
| RF-02 | Envio direto da capa ao S3, serviço de armazenamento de objetos, por URL pré-assinada gerada pelo backend. | HU-04 | Planejado |
| RF-03 | Evento de criação no S3 dispara Lambda para gravar chave, tamanho e tipo de conteúdo da capa no RDS. | HU-05 | Planejado |
| RF-04 | Relatório de livros por autor com JOIN e GROUP BY, incluindo quantidade zero, em Lambda e exposto pelo API Gateway, serviço que recebe e encaminha chamadas de API. | HU-06 | Planejado |
| RF-05 | Front-end web publicado na AWS e consumindo a API (interface de comunicação entre a página e os serviços). O funcionário usará a página para executar as funcionalidades. | HU-01 a HU-06 | Planejado |

## Restrições para as próximas etapas

- **RNF-01:** RDS em subnet privada, sem acesso público; documentar Security Groups (regras de tráfego de rede).
- **RNF-02:** nenhuma senha ou chave no repositório, nos exemplos ou nas evidências.
- **RNF-03:** documentar a retomada após reiniciar o Learner Lab, sem IP fixo no código.
- **RNF-04:** na Aula 2, justificar a decisão entre Lambda e container para o CRUD em um ADR (registro de decisão de arquitetura). Decisão ainda não tomada.
- **RNF-05:** criar infraestrutura pelo console ou CLI (interface de linha de comando), sem Terraform, CloudFormation ou SAM.
- Usar LabRole nas Lambdas e LabInstanceProfile na EC2 quando necessário; não prever criação de roles IAM próprias no Learner Lab.
- Evitar NAT Gateway; prever um endpoint Gateway do S3 quando necessário para acesso ao S3 a partir da VPC (rede virtual privada).
- Configurar CORS no API Gateway e no S3, permitindo as origens necessárias ao front-end. CORS são regras do navegador para chamadas entre origens diferentes.
- Manter recursos pequenos e custos baixos, respeitando as limitações do laboratório.

## Pendências de validação

O grupo ainda precisa revisar e aceitar estas propostas, inclusive os limites de arquivo e a regra de ano. A revisão com GitHub Copilot está pendente. Não há código, implantação, testes executados ou arquitetura aprovada nesta etapa.
