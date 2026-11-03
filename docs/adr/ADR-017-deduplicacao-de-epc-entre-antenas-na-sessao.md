# ADR-017 — Deduplicação de EPC entre antenas na sessão

- Status: Aceita
- Data: 2026-10-29
- Requisito: RF026 e orientação explícita do solicitante
- Complementa: ADR-003, ADR-014 e ADR-016

## Contexto

O RF026 habilita todas as antenas configuradas na mesma conexão LLRP. A chave
anterior de consulta, composta por reader, antena e EPC, permitia consultar e
registrar duas passagens do mesmo EPC quando recebido por antenas diferentes.
Deduplicar apenas o resumo visual não impedia esse efeito no Backend.

Embora o documento RF026 peça preservar a chave de origem, o solicitante
explicitou que o mesmo EPC deve ser processado apenas uma vez por sessão,
mesmo quando lido por outra antena.

## Decisão

Manter a chave de origem e o AntennaID recebido no relatório do reader.
Acrescentar ao serviço de consulta um conjunto de EPCs normalizados por sessão,
reservando o EPC sob lock antes de enfileirar a consulta. O filtro de prefixos
continua sendo aplicado antes dessa reserva.

O primeiro callback aceito determina a origem do processamento. Outros callbacks
do mesmo EPC, inclusive simultâneos ou de outra antena, não iniciam novo GET ou
POST nem acrescentam linhas ou contagens. A reserva permanece após erro HTTP ou
fila cheia, evitando tentativas repetidas na mesma sessão. Iniciar uma nova
sessão limpa ambos os conjuntos e permite processar novamente o EPC.

## Alternativas consideradas

- Deduplicar somente por reader, antena e EPC: permite passagens duplicadas.
- Deduplicar somente na tabela e no resumo: não evita duplicidade no Backend.
- Usar apenas uma janela temporal: permite nova passagem na mesma sessão após
  o vencimento da janela.

## Consequências

A leitura física pode ocorrer várias vezes, mas o processamento operacional
ocorre no máximo uma vez por EPC na sessão local. Isso não constitui garantia
de execução exatamente uma vez no Backend após reinício da aplicação ou entre
sessões distintas. A origem da primeira leitura permanece disponível; não há
agregação de todas as antenas que observaram o EPC.

Testes simulados cobrem concorrência, respostas de erro, Extra Box e reinício
da sessão. A homologação com duas antenas físicas permanece necessária.
