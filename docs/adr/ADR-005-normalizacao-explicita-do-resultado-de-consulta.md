# ADR-005 — Normalização explícita do resultado de consulta

- Status: Aceita
- Data: 2026-07-27
- Funcionalidade relacionada: Correção 001 do RF007
- Substituição parcial: a ADR-006 preserva a normalização, mas deixa de
  apresentar e contabilizar resultados `NOT_FOUND` na interface.

## Contexto

A correção do RF007 exige distinguir um resultado de negócio negativo de uma
falha técnica:

- `sucesso = true` significa etiqueta encontrada;
- `sucesso = false` significa etiqueta não encontrada;
- ausência ou valor inválido em `sucesso` significa que não foi possível
  classificar a consulta e deve resultar em erro.

A análise do fluxo local encontrou a seguinte sequência:

1. `SharePointLookupClient` seleciona o objeto `body`, valida os campos e cria um
   `TagLookupResult`;
2. `TagLookupService` encaminha esse mesmo resultado ou converte exceções do
   cliente em `TagLookupStatus.ERROR`;
3. `MainWindow` usa o status do resultado tanto para atualizar a tabela quanto
   para atualizar `TagLookupSessionSummary`;
4. a tabela exibe diretamente `TagLookupStatus.value`, e o resumo conta os
   conjuntos de EPCs em `FOUND` e `NOT_FOUND`.

No estado analisado, o booleano `false` já era convertido para
`TagLookupStatus.NOT_FOUND` e o resumo já contava esse estado. Portanto, não foi
reproduzida localmente a cadeia relatada de `false` virar `Erro` e deixar de ser
contado. Foram identificadas duas causas concretas de não conformidade:

- o valor visual de `NOT_FOUND` era `Não encontrada`, diferente do texto único
  `Não encontrado` exigido pela correção;
- o normalizador considerava qualquer valor desconhecido de `sucesso` como
  `false`, fazendo respostas como `null` ou `"other"` parecerem resultados
  válidos de não encontrado em vez de falhas de contrato.

## Decisão

`TagLookupStatus` permanece como a única fonte dos estados compartilhados entre
cliente HTTP, serviço, tabela e cards. O valor visual de `NOT_FOUND` passa a ser
exatamente `Não encontrado`.

O cliente HTTP normalizará `sucesso` por comparação explícita:

- `true`, `"true"`, `"True"`, `1` e `"1"` produzem `FOUND`;
- `false`, `"false"`, `"False"`, `0` e `"0"` produzem `NOT_FOUND`;
- espaços e diferenças entre maiúsculas e minúsculas continuam normalizados nas
  representações textuais;
- qualquer outro valor lança `TagLookupResponseError`.

Os formatos numéricos `1`, `"1"`, `0` e `"0"` são preservados por
compatibilidade com o contrato registrado anteriormente na ADR-002. A aceitação
aberta de todo valor restante é encerrada: compatibilidade não deve mascarar
respostas inválidas.

O `TagLookupService` continua sendo a fronteira que converte
`TagLookupResponseError`, timeout, falha HTTP ou falha de rede no estado
`ERROR`. Assim, somente uma resposta válida e explicitamente negativa pode
produzir `NOT_FOUND`.

Não haverá nova interpretação do JSON na interface. `MainWindow` continuará
entregando o mesmo `TagLookupResult` normalizado à linha da tabela e ao resumo da
sessão, que mantém a contagem idempotente por EPC hexadecimal.

## Alternativas consideradas

### Usar truthiness para classificar `sucesso`

Rejeitada porque confunde valores negativos válidos com ausência ou valores
inválidos e não expressa o contrato aceito.

### Considerar todo valor diferente de sucesso como não encontrado

Rejeitada porque classifica falhas de contrato como resultado de negócio e
incrementa indevidamente o card de EPCs não encontrados.

### Interpretar novamente a resposta na tabela ou nos cards

Rejeitada porque criaria múltiplas fontes de classificação e permitiria
divergência entre o texto da linha e os totais da sessão.

### Tratar todo HTTP 404 como não encontrado

Rejeitada porque não há contrato local que associe indiscriminadamente esse
status HTTP à ausência de EPC. Respostas HTTP fora da faixa 2xx permanecem erros
técnicos.

## Consequências

### Positivas

- `false` é um resultado válido e distinto de erro;
- o texto da tabela é padronizado como `Não encontrado`;
- valores ausentes ou inválidos não incrementam nenhum card;
- tabela e cards continuam derivados do mesmo estado interno;
- formatos legados explicitamente documentados permanecem compatíveis.

### Limitações aceitas

- o formato de payload sem o envelope `body` continua aceito por compatibilidade
  definida na ADR-002;
- um HTTP 404 com eventual JSON de negócio continua classificado como erro até
  que o contrato oficial do endpoint determine uma normalização específica;
- a validação automatizada usa transporte falso e não comprova o comportamento
  do endpoint real do Power Automate.
