# Requisitos: Integração Google Sheets com Agente SDR Agno

## Visão Geral

Integração que permite ao agente SDR Agno gerenciar leads automaticamente através do Google Sheets, realizando prospecção via WhatsApp com conversas bidirecionais e sincronização de status em tempo real.

## Requirement 1

**User Story:** Como um SDR, quero que o agente leia automaticamente leads de uma planilha Google Sheets, para que eu possa gerenciar minha base de prospecção de forma centralizada.

### Acceptance Criteria

1. WHEN o sistema inicia THEN ele SHALL autenticar com Google Sheets API usando OAuth2
2. WHEN o scheduler executa THEN ele SHALL ler todos os leads com status "pendente" da planilha
3. WHEN um lead é lido THEN ele SHALL ser validado (telefone obrigatório no formato internacional)
4. WHEN leads são lidos THEN eles SHALL ser armazenados no banco de dados local
5. WHEN ocorre erro de leitura THEN o sistema SHALL registrar o erro e tentar novamente no próximo ciclo

## Requirement 2

**User Story:** Como um SDR, quero que o agente envie mensagens iniciais automaticamente via WhatsApp para novos leads, para que eu possa escalar minha prospecção.

### Acceptance Criteria

1. WHEN um lead tem status "pendente" THEN o sistema SHALL enviar uma mensagem inicial personalizada via WhatsApp
2. WHEN uma mensagem é enviada com sucesso THEN o status do lead SHALL ser atualizado para "contatado"
3. WHEN uma mensagem é enviada THEN o timestamp SHALL ser registrado no campo last_contact
4. WHEN o envio falha THEN o status SHALL ser atualizado para "erro" com detalhes nas notas
5. WHEN uma mensagem é enviada THEN uma sessão de conversa SHALL ser criada no banco de dados



## Requirement 3

**User Story:** Como um SDR, quero que o agente processe respostas recebidas via WhatsApp, para que as conversas sejam gerenciadas automaticamente.

### Acceptance Criteria

1. WHEN uma mensagem é recebida via WhatsApp THEN o sistema SHALL identificar a sessão pelo número de telefone
2. WHEN uma resposta é recebida THEN o agente SHALL processar com contexto completo da conversa
3. WHEN uma resposta é processada THEN o status do lead SHALL ser atualizado para "respondeu"
4. WHEN o agente detecta interesse THEN o status SHALL ser atualizado para "qualificado"
5. WHEN o agente detecta desinteresse THEN o status SHALL ser atualizado para "desqualificado"
6. WHEN uma resposta é processada THEN o histórico SHALL ser armazenado no banco de dados

## Requirement 4

**User Story:** Como um SDR, quero que o status dos leads seja sincronizado automaticamente com o Google Sheets, para que eu tenha visibilidade em tempo real.

### Acceptance Criteria

1. WHEN o status de um lead muda THEN a atualização SHALL ser adicionada à fila de sincronização
2. WHEN a fila tem atualizações pendentes THEN elas SHALL ser sincronizadas em lote com o Google Sheets
3. WHEN uma atualização é sincronizada THEN o campo synced SHALL ser marcado como true
4. WHEN ocorre erro na sincronização THEN a atualização SHALL permanecer na fila para retry
5. WHEN uma sincronização é bem-sucedida THEN o timestamp synced_at SHALL ser registrado

## Requirement 5

**User Story:** Como um SDR, quero que o sistema evite duplicação de contatos, para que leads não sejam contatados múltiplas vezes.

### Acceptance Criteria

1. WHEN um lead é processado THEN o sistema SHALL verificar se já existe sessão ativa para o telefone
2. WHEN já existe sessão ativa THEN o sistema SHALL reutilizar a sessão existente
3. WHEN um lead com status "contatado" é lido THEN ele SHALL ser ignorado pelo scheduler
4. WHEN um lead com status "respondeu" é lido THEN ele SHALL ser ignorado pelo scheduler
5. WHEN um telefone duplicado é encontrado na planilha THEN apenas o primeiro SHALL ser processado

## Requirement 6

**User Story:** Como um SDR, quero que o sistema mantenha histórico completo de interações, para que eu possa revisar conversas passadas.

### Acceptance Criteria

1. WHEN uma mensagem é enviada ou recebida THEN ela SHALL ser armazenada na tabela de mensagens
2. WHEN uma sessão é acessada THEN o histórico completo SHALL estar disponível
3. WHEN o agente processa uma mensagem THEN ele SHALL ter acesso às últimas 10 mensagens da sessão
4. WHEN uma sessão é atualizada THEN os campos updated_at e message_count SHALL ser atualizados
5. WHEN o histórico é consultado THEN as mensagens SHALL ser ordenadas por timestamp

## Requirement 7

**User Story:** Como um desenvolvedor, quero que o sistema tenha tratamento robusto de erros, para que falhas não interrompam o serviço.

### Acceptance Criteria

1. WHEN ocorre erro de autenticação com Google Sheets THEN o sistema SHALL registrar e tentar reautenticar
2. WHEN ocorre erro no envio de WhatsApp THEN o sistema SHALL registrar e marcar o lead com status "erro"
3. WHEN ocorre erro de sincronização THEN a atualização SHALL permanecer na fila para retry
4. WHEN ocorre erro de validação de dados THEN o lead SHALL ser ignorado com log detalhado
5. WHEN ocorre erro crítico THEN o sistema SHALL continuar operando para outros leads

## Requirement 8

**User Story:** Como um SDR, quero que mensagens iniciais sejam personalizadas com dados do lead, para aumentar taxa de resposta.

### Acceptance Criteria

1. WHEN uma mensagem inicial é criada THEN ela SHALL incluir o nome do lead
2. WHEN o lead tem empresa THEN a mensagem SHALL mencionar a empresa
3. WHEN o lead tem source THEN o contexto SHALL ser adaptado à origem
4. WHEN a mensagem é formatada THEN ela SHALL seguir o tom e estilo do agente SDR
5. WHEN dados obrigatórios estão faltando THEN uma mensagem genérica SHALL ser usada

## Non-Functional Requirements

### Performance
- O scheduler deve processar até 100 leads por minuto
- Sincronização em lote deve processar até 50 atualizações por operação
- Tempo de resposta para mensagens inbound deve ser < 2 segundos

### Reliability
- Taxa de sucesso de sincronização > 99%
- Sistema deve se recuperar automaticamente de falhas temporárias
- Retry automático com backoff exponencial para operações falhadas

### Security
- Credenciais OAuth2 devem ser armazenadas de forma segura
- Dados de leads devem ser criptografados em repouso
- Logs não devem conter informações sensíveis (telefones, emails)

### Scalability
- Sistema deve suportar até 10.000 leads ativos
- Banco de dados deve suportar até 100.000 mensagens
- Fila de sincronização deve suportar até 1.000 atualizações pendentes
