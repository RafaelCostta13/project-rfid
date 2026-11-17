# ADR-031 — Sensores diretos e EPCs identificados

## Contexto

Os testes do portal indicaram a necessidade de voltar a dois sensores e um pedal,
com visibilidade dos EPCs aceitos antes da classificação pelo backend.

## Decisão

DI1 inicia uma passagem, DI2 a encerra e DI3 inicia ou retoma após timeout de
20 segundos. DI4 e DI5 continuam no diagnóstico, sem decisões operacionais.
O contador visual usa os eventos de consulta emitidos após validação, filtro e
deduplicação por sessão. A tabela utiliza linhas compactas.

## Consequências

A reabertura preserva a sessão e seus EPCs; uma nova passagem reinicia a contagem.
O diagnóstico físico e o polling permanecem inalterados. A validação dos sensores,
relés e legibilidade no ambiente operacional requer homologação com o hardware.
