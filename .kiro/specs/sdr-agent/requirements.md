# Documento de Requisitos

## Introdução

O SDR Agent é um agente conversacional autônomo construído com LangChain/LangGraph que atua como Sales Development Representative (SDR). O agente opera em dois contextos: plataforma principal e leilões. Em ambos os contextos, o objetivo é qualificar leads e agendar reuniões ou ligações com vendedores humanos.

O agente utiliza uma arquitetura de grafo com nós especializados, carrega o perfil do lead a partir de um banco de dados PostgreSQL (RDS) e adapta seu comportamento dinamicamente conforme a origem da conversa.

## Glossário

- **SDR_Agent**: O agente conversacional principal responsável por conduzir a qualificação de leads
- **Router_Node**: Nó do grafo responsável por identificar a origem da conversa (plataforma ou leilão)
- **Context_Loader**: Nó responsável por buscar o perfil do lead no RDS e montar o system prompt dinâmico
- **Qualification_Check**: Nó responsável por avaliar se o lead está qualificado para avançar no funil
- **Schedule_Node**: Nó responsável por registrar o agendamento de reunião ou ligação no banco de dados
- **Notify_Seller**: Nó responsável por notificar o vendedor sobre o lead qualificado e o agendamento
- **Lead**: Potencial cliente identificado por um ID único no banco de dados
- **Contexto de Leilão**: Bloco adicional de informações carregado no system prompt quando a origem da conversa for leilão
- **RDS**: Banco de dados PostgreSQL hospedado na AWS RDS
- **Qualificação**: Processo de determinar se o lead possui perfil adequado para avançar para uma reunião com o vendedor
- **System Prompt Dinâmico**: Prompt de sistema montado em tempo de execução com base na origem e no perfil do lead

---

## Requisitos

### Requisito 1: Roteamento por Origem

**User Story:** Como sistema, quero identificar a origem de cada conversa, para que o agente carregue o contexto correto e adapte seu comportamento.

#### Critérios de Aceitação

1. WHEN uma nova conversa é iniciada, THE Router_Node SHALL identificar a origem como "plataforma" ou "leilão" com base nos metadados da requisição
2. WHEN a origem identificada for "leilão", THE Router_Node SHALL sinalizar ao Context_Loader para incluir o bloco de contexto de leilão no system prompt
3. WHEN a origem identificada for "plataforma", THE Router_Node SHALL sinalizar ao Context_Loader para usar apenas o contexto padrão da plataforma
4. IF a origem não puder ser determinada, THEN THE Router_Node SHALL assumir a origem como "plataforma" e registrar um aviso no log

---

### Requisito 2: Carregamento de Contexto e Perfil do Lead

**User Story:** Como SDR Agent, quero ter acesso ao perfil completo do lead e ao contexto correto antes de iniciar a conversa, para que eu possa personalizar a abordagem.

#### Critérios de Aceitação

1. WHEN o Router_Node sinaliza a origem, THE Context_Loader SHALL buscar o perfil do lead no RDS PostgreSQL usando o identificador do lead fornecido na requisição
2. WHEN o perfil do lead é recuperado com sucesso, THE Context_Loader SHALL montar o system prompt dinâmico incluindo nome, histórico e dados relevantes do lead
3. WHEN a origem for "leilão", THE Context_Loader SHALL acrescentar o bloco de contexto de leilão ao system prompt dinâmico
4. IF o lead não for encontrado no RDS, THEN THE Context_Loader SHALL interromper o fluxo e retornar uma resposta de erro indicando que o lead não foi localizado
5. IF a conexão com o RDS falhar, THEN THE Context_Loader SHALL retornar uma resposta de erro e registrar o erro no log sem expor detalhes técnicos ao usuário

---

### Requisito 3: Condução da Conversa de Qualificação

**User Story:** Como lead, quero ser atendido por um agente que entenda meu contexto e me faça perguntas relevantes, para que eu possa avançar no processo de forma natural.

#### Critérios de Aceitação

1. WHEN o Context_Loader conclui o carregamento, THE SDR_Agent SHALL iniciar a conversa com uma saudação personalizada usando o nome do lead
2. WHILE a conversa estiver em andamento, THE SDR_Agent SHALL manter o histórico completo da conversa no estado do grafo LangGraph
3. WHILE a conversa estiver em andamento, THE SDR_Agent SHALL responder perguntas do lead sobre a plataforma ou sobre leilões conforme o contexto ativo
4. WHEN o lead fizer uma pergunta fora do escopo de qualificação e vendas, THE SDR_Agent SHALL redirecionar a conversa de volta ao objetivo de qualificação
5. THE SDR_Agent SHALL coletar as seguintes informações de qualificação: necessidade do lead, orçamento disponível, prazo de decisão e autoridade de compra
6. WHEN todas as informações de qualificação forem coletadas, THE SDR_Agent SHALL encaminhar o estado para o Qualification_Check

---

### Requisito 4: Verificação de Qualificação

**User Story:** Como vendedor, quero receber apenas leads qualificados, para que eu possa focar meu tempo em oportunidades reais.

#### Critérios de Aceitação

1. WHEN o SDR_Agent encaminha o estado para o Qualification_Check, THE Qualification_Check SHALL avaliar as informações coletadas com base nos critérios de qualificação definidos
2. WHEN o lead for considerado qualificado, THE Qualification_Check SHALL encaminhar o fluxo para o Schedule_Node
3. WHEN o lead não for considerado qualificado, THE Qualification_Check SHALL encaminhar o fluxo de volta ao SDR_Agent com uma instrução para continuar a conversa ou encerrar educadamente
4. THE Qualification_Check SHALL registrar o resultado da avaliação (qualificado ou não qualificado) no estado do grafo

---

### Requisito 5: Agendamento de Reunião ou Ligação

**User Story:** Como lead qualificado, quero agendar uma reunião ou ligação com o vendedor diretamente durante a conversa, para que eu não precise passar por etapas adicionais.

#### Critérios de Aceitação

1. WHEN o Qualification_Check encaminha o fluxo para o Schedule_Node, THE Schedule_Node SHALL apresentar ao lead as opções de horário disponíveis para reunião ou ligação
2. WHEN o lead confirmar um horário, THE Schedule_Node SHALL registrar o agendamento no banco de dados RDS PostgreSQL via a plataforma
3. WHEN o agendamento for registrado com sucesso, THE Schedule_Node SHALL confirmar o agendamento ao lead com data, hora e formato (reunião ou ligação)
4. IF o horário escolhido pelo lead não estiver mais disponível no momento do registro, THEN THE Schedule_Node SHALL apresentar novas opções de horário ao lead
5. IF o registro do agendamento no RDS falhar, THEN THE Schedule_Node SHALL informar ao lead que houve um problema e solicitar que tente novamente

---

### Requisito 6: Notificação do Vendedor

**User Story:** Como vendedor, quero ser notificado imediatamente após um lead ser qualificado e agendado, para que eu possa me preparar para o atendimento.

#### Critérios de Aceitação

1. WHEN o Schedule_Node registra o agendamento com sucesso, THE Notify_Seller SHALL enviar uma notificação ao vendedor responsável pelo lead
2. THE Notify_Seller SHALL incluir na notificação: nome do lead, dados de contato, resumo da qualificação, data e hora do agendamento e formato do atendimento
3. WHEN a notificação for enviada com sucesso, THE Notify_Seller SHALL registrar o evento no estado do grafo e encerrar o fluxo
4. IF o envio da notificação falhar, THEN THE Notify_Seller SHALL registrar o erro no log e encerrar o fluxo sem impactar a experiência do lead

---

### Requisito 7: Gerenciamento de Estado do Grafo

**User Story:** Como sistema, quero que o estado da conversa seja mantido de forma consistente ao longo de todos os nós do grafo, para que nenhuma informação seja perdida entre as transições.

#### Critérios de Aceitação

1. THE SDR_Agent SHALL manter um objeto de estado LangGraph que inclui: origem da conversa, perfil do lead, histórico de mensagens, informações de qualificação coletadas e status do agendamento
2. WHEN qualquer nó do grafo atualiza o estado, THE SDR_Agent SHALL preservar todos os campos anteriores do estado não modificados pelo nó atual
3. IF o estado do grafo for corrompido ou inválido em qualquer nó, THEN THE SDR_Agent SHALL encerrar o fluxo com uma mensagem de erro genérica ao usuário e registrar o erro completo no log

---

### Requisito 8: Observabilidade e Rastreabilidade

**User Story:** Como desenvolvedor, quero que todas as transições de nó e decisões do agente sejam registradas, para que eu possa depurar e auditar o comportamento do agente.

#### Critérios de Aceitação

1. WHEN qualquer nó do grafo é executado, THE SDR_Agent SHALL registrar no log: nome do nó, timestamp de início, timestamp de fim e resultado da execução
2. WHEN o SDR_Agent gera uma resposta via LLM, THE SDR_Agent SHALL registrar o número de tokens utilizados na chamada
3. IF uma exceção não tratada ocorrer em qualquer nó, THEN THE SDR_Agent SHALL registrar o stack trace completo no log sem expor informações sensíveis do lead
