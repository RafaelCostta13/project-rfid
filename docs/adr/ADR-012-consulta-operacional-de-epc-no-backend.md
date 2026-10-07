# ADR-012 — Consulta operacional de EPC no Backend RFID

- Status: Aceita
- Data: 2026-10-07
- Requisito: RF016
- Complementa: ADR-010 e ADR-011

## Contexto

Até o RF015, o fluxo de leitura consultava o SQLite local, alimentado pela
sincronização Power Automate/SharePoint. O RF015 estabeleceu o Backend Rails
como fonte de disponibilidade e preparou o cliente HTTP, mas preservou o
lookup local temporariamente.

O contrato operacional do Backend é diferente do contrato antigo: a resposta
usa `found` e dados aninhados em `data`, com `destinatario` e `notafiscal` no
lugar de `cliente` e `notaFiscal`.

## Decisão

O `TagLookupService` passa a consultar exclusivamente
`GET /api/v1/rfid_records/{epc}` através do `BackendRFIDClient` criado no
RF015. O EPC é normalizado com `strip` e `upper` antes da deduplicação e da
montagem do path.

O cliente valida e converte o contrato Rails para `RfidRecordData`, preservando
os campos operacionais e de controle recebidos:

- `datahora`, `volume`, `pedido`, `notafiscal`;
- `destinatario`, `endereco`, `numero`, `cidade`, `uf`, `doca`;
- `epc`, `tag`, `fornecedor`, `status`;
- `first_read_at`, `last_read_at`, `read_count`.

O modelo visual continua usando as colunas existentes:

```text
Status       <- data.status
Cliente      <- data.destinatario
Nota fiscal  <- data.notafiscal
Volume       <- data.volume
Pedido       <- data.pedido
Doca         <- data.doca
```

`TagLookupResult.status` continua representando o estado técnico da consulta,
enquanto `record_status` representa o status de negócio (`pendente` ou `lido`).
`read_count` não é usado no card de EPCs encontrados e não é incrementado.

O retorno documentado `404` com `found=false` e `error=epc_not_found` é uma
condição de negócio: o EPC é ignorado sem erro visual, sem alterar os
indicadores e sem fallback. Timeout, rede, 5xx, JSON inválido, contrato
inconsistente ou EPC divergente são falhas técnicas controladas.

A fila/worker existente continua executando as chamadas fora da UI e do
callback de leitura. A deduplicação por sessão permanece ativa; uma nova
sessão pode consultar novamente o mesmo EPC. Nenhuma chamada POST é feita no
RF016.

O bootstrap da aplicação deixa de inicializar o SQLite e de executar a
sincronização automática Power Automate. O arquivo SQLite e os módulos legados
não são apagados automaticamente nem removidos enquanto puderem ser usados
por componentes históricos/testes; eles deixam de participar do caminho
operacional do EPC.

## Alternativas consideradas

- Manter o lookup SQLite como fallback: rejeitado porque preservaria duas fontes
  operacionais e poderia retornar dados obsoletos.
- Consultar Power Automate quando o Backend falhar: rejeitado pela mesma razão
  e pela migração definitiva para Rails/PostgreSQL.
- Adaptar o JSON novo para o JSON antigo: rejeitado porque perpetuaria o
  contrato legado; a conversão passa a ocorrer em um modelo interno explícito.
- Fazer o GET no callback LLRP ou na thread da UI: rejeitado porque uma rede
  lenta bloquearia leitura ou interface.

## Consequências

O PostgreSQL via Rails passa a ser a fonte operacional única para validar EPCs.
EPCs inexistentes deixam de gerar linhas e contagens, enquanto registros
encontrados continuam alimentando a tabela existente sem alterar o Backend.

O software não valida Doca localmente nem envia Doca no GET; a Doca retornada
pela API é apenas apresentada como dado do registro. A configuração da Doca
permanece disponível para os demais fluxos ainda existentes.

O RF017 continua responsável pelo POST de passagem, mudança de status,
incremento de `read_count`, timestamps e histórico de leituras.

Testes sem hardware cobrem contrato 200, mapeamento, zeros à esquerda, `tag`
nulo, status `lido`, 404, timeout/erros técnicos, normalização, deduplicação e
ausência de fallback operacional. A validação com Backend, Zebra e Waveshare
reais permanece manual no Windows.
