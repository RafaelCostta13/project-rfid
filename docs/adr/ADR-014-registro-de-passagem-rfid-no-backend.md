# ADR-014 — Registro de passagem RFID no Backend

- Status: Aceita
- Data: 2026-10-07
- Requisito: RF017
- Complementa: ADR-012

## Contexto

O RF016 passou a validar EPCs pelo Backend, mas ainda não registrava a
passagem. O novo registro altera estado, contador, timestamps e histórico no
servidor, portanto não pode ser reproduzido nem calculado localmente pelo
desktop.

O leitor pode enviar o mesmo EPC várias vezes durante uma sessão e uma chamada
POST pode terminar com resultado ambíguo quando a conexão cai depois que o
servidor processou a requisição.

## Decisão

Após um `GET /api/v1/rfid_records/{epc}` válido e encontrado, o mesmo worker de
lookup executará:

```text
POST /api/v1/rfid_reads
{"epc": "<EPC_NORMALIZADO>"}
```

O payload contém somente o EPC normalizado. O cliente valida a resposta
`success`, EPC, `first_read`, `duplicate`, `status`, `read_count` e timestamps,
convertendo-a para `RfidReadResult`.

O resultado do POST substitui o status de negócio vindo do GET no modelo em
memória. `duplicate=true` com `success=true` é sucesso; `read_count`,
`first_read_at` e `last_read_at` são apenas valores retornados pelo Backend.

A deduplicação existente marca a chave antes do processamento e permanece
ativa até o fim da sessão. Isso funciona como proteção `IN_FLIGHT` e
`PROCESSADO`: leituras repetidas não iniciam novo GET/POST, inclusive quando o
POST falha ou termina em timeout ambíguo. Não há retry automático.

O POST roda fora da UI e do callback LLRP. Respostas de sessões antigas são
descartadas antes de atualizar a interface pelo `session_id`; o POST já enviado
não é cancelado nem repetido.

404/422 e falhas técnicas não produzem sucesso local. Não há fallback para
SQLite ou Power Automate, e o cliente não controla relés.

## Alternativas consideradas

- Incrementar `read_count` localmente: rejeitado porque o Backend é a fonte de
  verdade e também controla timestamps/histórico.
- Repetir POST em timeout: rejeitado porque a requisição pode ter sido
  processada antes da perda da resposta.
- Fazer POST no callback RFID ou na UI: rejeitado porque rede lenta bloquearia
  leitura ou interface.
- Enviar o registro completo retornado pelo GET: rejeitado porque o endpoint
  recebe exclusivamente o EPC.

## Consequências

Cada EPC encontrado gera no máximo um POST por sessão. Uma nova sessão pode
registrar uma nova passagem legítima, e o Backend decide se ela é primeira ou
duplicada historicamente.

O status exibido após sucesso representa o resultado real do registro remoto.
Em caso de falha, nenhuma passagem é fabricada localmente e o EPC permanece
protegido na sessão atual.

Testes unitários cobrem payload mínimo, resposta de primeira passagem,
passagem duplicada, EPC divergente, 404/422, erro técnico, ausência de retry,
deduplicação e ausência de POST quando o GET não encontra o EPC. A validação
com Backend e leitor físicos permanece manual no Windows.
