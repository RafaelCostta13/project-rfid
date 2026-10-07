# ADR-009 — Doca da estação e disponibilidade da base remota

- Status: Aceita
- Data: 2026-10-03
- Requisito: RF013
- Complementa: ADR-002, ADR-004 e ADR-007

## Contexto

A futura sincronização por Doca precisa conhecer a localização configurada na
instalação. O RF013 também exige disponibilidade real da fonte remota como
pré-condição operacional, preservando consultas atuais, sensores e sinalizadores
do RF012. SQLite e sincronização estão fora deste requisito.

A aplicação carrega `.env` por `python-dotenv` na CLI e valida valores em
`load_config`. RFID/Waveshare salvam apenas suas chaves por substituição atômica
do mesmo arquivo. `ConnectionMonitor` já executa um verificador por thread e
publica estados por uma fila consumida pelo Tkinter. O controlador automático
centraliza disponibilidade e CH1–CH3 considerando todos os `ConnectionKind`.

O cliente HTTP atual usa `urllib`, timeout configurável e validação de JSON,
campos e correspondência do EPC. Pelo contrato vigente, `sucesso=false`
significa etiqueta não encontrada, não uma falha técnica.

O novo fluxo de sincronização é descrito conceitualmente no RF013, mas não há
contrato implementado de health check leve nem garantia de limite de resultados.
Enviar `modifiedSince=""` pode solicitar todos os registros. Usar uma data
inventada também não garante uma operação barata ou válida no servidor.

## Decisão

### Doca

Persistir `RFID_STATION_DOCK` no `.env` existente, reutilizando a escrita atômica
do store de configuração. `Settings.station_dock` fornece o valor inicial a
`StationConfigurationService`; seu getter `current()` é a fonte de verdade em
execução para a UI e futuros serviços. Não capturar o valor inicial em futuras
consultas: obter pelo getter a cada operação. Falha ao salvar preserva o arquivo
e o valor em memória.

A UI existente recebe uma seleção editável. D01–D05 são sugestões centralizadas
em `config.py`, não um catálogo de Docas comprovado nem uma restrição às cinco
opções. Aceitar códigos com até 32 letras/números/hífen/sublinhado, normalizados
para maiúsculas. Permitir vazio para instalações ainda não configuradas ou para
limpar a associação, exibindo orientação; nunca escolher D01 automaticamente.

### Verificação remota

Reutilizar a instância sem estado de `SharePointLookupClient` e a configuração
`SHAREPOINT_LOOKUP_URL`. Fazer uma consulta pontual POST por EPC de sondagem
(`DATABASE_CHECK_EPC`, padrão de 24 zeros), validada pelo cliente existente.
Uma resposta FOUND ou NOT_FOUND para o EPC solicitado comprova disponibilidade
segundo o contrato. Não submeter a sondagem ao `TagLookupService`, não alterar
sessões, tabela ou contador e não persistir o resultado.

Essa estratégia verifica a fonte oficial atual sem chamar o fluxo de
sincronização e sem baixar todos os itens de uma Doca. Não exige Doca; portanto,
Doca vazia não impede esse indicador de conectar. Quando uma futura operação
exigir Doca, ela deverá rejeitar vazio e usar `current()` obrigatoriamente.

`DatabaseConnectionChecker` participa do monitor central. O intervalo remoto
configurável tem padrão 60 segundos e mínimo 30 para evitar polling agressivo;
é contado com relógio monotônico após o término de cada tentativa, inclusive
falhas. A resolução segue o polling geral, padrão 5 segundos. Reutilizar
`SHAREPOINT_LOOKUP_TIMEOUT_SECONDS`, padrão 10 segundos. O transporte existente
limita operações de rede por timeout; ele não oferece um deadline global
separado para toda a resolução DNS/leitura da resposta.

Enquanto Internet é desconhecida, a base permanece Verificando. Sem Internet,
fica Desconectado sem novas chamadas. Ao observar recuperação, uma nova sondagem
pode ocorrer na próxima passagem. Internet conectada não implica base conectada.
Erros HTTP, rede, timeout e resposta inválida produzem Erro. Registrar apenas
tipo de exceção e status HTTP; nunca conteúdo remoto, mensagem arbitrária da
exceção, URL assinada ou traceback com credenciais.

O encerramento impede novas consultas e aguarda a chamada corrente antes de
liberar o worker. Nenhuma requisição HTTP executa na thread gráfica.

### Disponibilidade e relés

Adicionar DATABASE a `ConnectionKind`, mantendo a avaliação única do controlador
automático: Internet, RFID, Waveshare e Base de dados precisam estar conectados.
Estado inicial/erro da base bloqueia habilitação e novos ciclos; a perda durante
um ciclo usa a interrupção existente de dependência indisponível. Com Waveshare
acessível, CH1/CH2 desligam antes de CH3 ligar. Recuperação volta a sinalizar
disponibilidade sem iniciar inventário. Preservar CH4–CH8, DI1/DI2 e timer.

## Alternativas consideradas

- Fluxo de sincronização com `modifiedSince` vazio: rejeitado por possível carga
  completa periódica e ausência de contrato leve validado.
- Inventar `health=true`, `top=1` ou timestamp de corte: rejeitado porque não há
  evidência de suporte do servidor.
- Endpoint dedicado de saúde: adequado futuramente, mas exige contrato e mudança
  externa desnecessária para esta etapa, que já possui consulta pontual.
- Usar Internet/DNS/TCP como status da base: não comprova resposta da fonte.
- Criar novo cliente HTTP, arquivo de configuração ou banco: duplicação sem
  necessidade para este requisito.

## Consequências e validação

Não há novas dependências de produção, banco local ou sincronização. As consultas
operacionais existentes mantêm seu contrato e processamento. A sondagem gera uma
execução adicional do fluxo a cada intervalo quando a Internet está disponível;
o custo interno da consulta SharePoint depende da implementação do fluxo.

O status comprova o contrato remoto, não consegue detectar um servidor que
converta indisponibilidade do SharePoint em uma resposta normal NOT_FOUND.
Esse comportamento e a aceitação do EPC de sondagem precisam ser conferidos no
Power Automate real. Se necessário, configurar um EPC de teste aceito pelo fluxo.

Testes sem hardware cobrem persistência, recarga, troca, vazio, validação, falha
de gravação, preservação das outras configurações, HTTP, timeout, JSON inválido,
sigilo de logs, polling, suspensão offline, recuperação, shutdown e os relés
com a nova dependência. A aceitação física continua exigindo Windows, fluxo
Power Automate/SharePoint, Zebra FX9600 e Waveshare reais; testes com fakes não
constituem essa validação.
