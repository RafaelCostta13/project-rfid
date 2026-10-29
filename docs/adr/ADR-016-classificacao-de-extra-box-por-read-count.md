# ADR-016 — Classificação de Extra Box por `read_count`

- Status: Aceita
- Data: 2026-10-23
- Requisito: RF020
- Complementa: ADR-014 e o requisito de contabilização de Extra Box

## Contexto

O fluxo de consulta RFID executa um `GET /api/v1/rfid_records/{epc}` antes de
registrar a passagem no `POST /api/v1/rfid_reads`. O registro retornado pelo
GET informa `read_count`, que representa quantas passagens anteriores foram
registradas pelo Backend.

Antes desta decisão, um EPC encontrado na base era classificado como encontrado
independentemente de já ter passado pelo portal. Isso fazia com que etiquetas
que deveriam representar Extra Box aumentassem o contador de EPCs encontrados.

O POST continua sendo necessário para que o Backend incremente seu contador e
mantenha o histórico de passagens. Portanto, a classificação local não pode
impedir o POST.

## Decisão

Após um GET válido e encontrado:

- `read_count == 0` classifica o EPC como `FOUND`;
- `read_count > 0` classifica o EPC como `EXTRA_BOX`;
- o POST de registro da passagem é executado nos dois casos;
- o resultado do POST continua sendo validado e usado para os dados da
  passagem atual;
- a decisão de classificação usa o `read_count` recebido pelo GET, antes do
  POST, e não o contador retornado pelo POST.

Um EPC não encontrado permanece classificado como `NOT_FOUND` e continua sendo
contabilizado como Extra Box conforme a regra existente. `EXTRA_BOX` é um
estado explícito para diferenciar um EPC existente, mas já lido, de um EPC
ausente na base.

O resumo da sessão mantém conjuntos distintos por EPC:

- estados `FOUND` alteram somente o total de encontrados;
- estados `EXTRA_BOX` e `NOT_FOUND` alteram somente o total de Extra Box;
- estados `CONSULTING` e `ERROR` não alteram nenhum contador;
- repetir o mesmo EPC não cria nova contagem;
- iniciar uma nova sessão limpa os dois conjuntos.

## Alternativas consideradas

- **Não executar o POST para `read_count > 0`:** rejeitada, pois o Backend
  precisa registrar a nova passagem e incrementar o contador histórico.
- **Usar `NOT_FOUND` para todos os Extra Box:** rejeitada, pois mistura EPC
  ausente com EPC existente e previamente lido.
- **Classificar pelo `read_count` retornado no POST:** rejeitada, pois esse
  valor representa o estado após o registro atual e não a situação anterior
  que determina a classificação.
- **Incrementar os contadores localmente sem conjuntos por EPC:** rejeitada,
  pois leituras repetidas do reader não podem inflar os totais da sessão.

## Consequências

- O contador de encontrados representa somente EPCs existentes que nunca
  haviam passado pelo portal.
- O contador de Extra Box representa EPCs ausentes e EPCs existentes já lidos.
- Cada EPC existente gera no máximo um POST por sessão, conforme a
  deduplicação vigente.
- O Backend continua sendo a fonte de verdade para contador, timestamps e
  histórico de passagens.
- A validação de integração com Backend e Zebra FX9600 permanece necessária;
  os testes unitários não substituem o teste físico.

