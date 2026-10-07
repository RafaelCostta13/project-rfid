# ADR-011 — Backend RFID como fonte de status operacional

- Status: Aceita
- Data: 2026-10-07
- Requisito: RF015
- Complementa: ADR-009 e ADR-010

## Contexto

O RF015 inicia a migração da aplicação desktop para o Backend RFID Rails como
camada de acesso à operação. O software não deve acessar o PostgreSQL
diretamente, e a consulta operacional dos EPCs ainda permanece no SQLite local
até o RF016.

A aplicação já possui configuração persistida em `.env`, um monitor central de
conectividade executado fora da thread da interface e um controlador único para
disponibilidade e os relés CH1–CH3.

## Decisão

### Backend e cliente HTTP

Adicionar `RFID_BACKEND_BASE_URL` à configuração existente e persistir a chave
usando o mesmo store atômico das demais configurações. A URL não será
hardcodada nem duplicada nas telas ou nos serviços.

Criar um cliente HTTP centralizado para o Backend RFID. A montagem do endpoint
é feita a partir da URL configurada:

```text
<base-url>/api/v1/health
```

As barras finais da URL são normalizadas. Toda requisição usa o timeout central
`RFID_CONNECTION_TIMEOUT_SECONDS`.

### Health e indicadores

Uma única chamada `GET /api/v1/health` fornece os dois indicadores:

- `status = "ok"` representa `Sistema` conectado;
- `database = "ok"` representa `Base de dados` conectada.

HTTP 503, timeout, falha de rede, URL vazia ou resposta inválida produzem
estado indisponível. O cliente não acessa PostgreSQL e não armazena credenciais
de banco.

O health é integrado ao `ConnectionMonitor`, que executa a chamada em worker e
distribui o resultado para `Sistema` e `Base de dados` sem duplicar a
requisição. O estado inicial permanece `Verificando`.

### Disponibilidade e relés

`system_ready` continua centralizado no `AutomaticInventoryController` e passa
a exigir, além de Internet, RFID e Waveshare:

- `Sistema` conectado;
- `Base de dados` conectada.

CH1 continua representando sistema apto, CH2 continua reservado à leitura RFID
e CH3 continua representando indisponibilidade. CH4–CH8, DI1/DI2 e o timer de
60 segundos não são alterados.

O indicador visual `Sincronização` é removido. A enumeração e os serviços
legados podem permanecer temporariamente enquanto forem necessários ao fluxo de
consulta SQLite existente, mas deixam de participar da disponibilidade
operacional.

### Configuração na interface

A tela de Configurações recebe uma seção `Backend RFID` com URL, botão para
salvar e botão `Testar conexão`. O teste utiliza o valor atualmente digitado,
sem exigir salvamento prévio, e seu resultado é encaminhado à UI por fila para
evitar atualização de Tkinter fora da thread principal.

## Alternativas consideradas

- Acessar PostgreSQL diretamente: rejeitado porque viola a nova arquitetura e
  acopla o desktop a credenciais e detalhes do banco.
- Fazer uma chamada health para cada indicador: rejeitado porque duplica carga e
  pode produzir estados inconsistentes.
- Criar um loop independente para o Backend: rejeitado porque duplica o
  monitoramento e dificulta o encerramento coordenado.
- Remover imediatamente SQLite e sincronização: rejeitado porque quebraria o
  fluxo operacional antes da migração prevista no RF016.
- Manter `Sincronização` como status operacional: rejeitado porque a nova
  arquitetura não usa esse conceito para indicar prontidão do sistema.

## Consequências

O Backend Rails e o PostgreSQL passam a ser a referência dos indicadores
`Sistema` e `Base de dados`, preparando os próximos requisitos sem antecipar a
consulta remota de EPC nem o registro de passagens.

O SQLite local e a sincronização Power Automate/SharePoint continuam
temporariamente disponíveis para preservar a operação entre RF015 e RF016. O
cutover definitivo da consulta por EPC e a remoção segura da sincronização
legada permanecem responsabilidades dos requisitos seguintes.

Testes unitários cobrem URL vazia, normalização de endpoint, health saudável,
HTTP 503, timeout, resposta inválida, persistência e a distribuição dos dois
indicadores a partir de uma única chamada. A validação contra Backend real,
Zebra FX9600 e Waveshare continua sendo manual e dependente do ambiente Windows.
