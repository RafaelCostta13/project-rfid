# ADR-028 — Preservação da entrada armada quando DI1 se repete

## Contexto

Após observar DI1, o polling pode encontrar novas bordas de DI1 e DI4 na mesma amostra. A regra anterior descartava a sequência mesmo quando já existia uma borda de DI1 comprovadamente anterior.

## Decisão

Quando uma entrada válida já estiver armada por DI1, aceitar a borda posterior de DI4 mesmo que DI1 também apresente uma nova borda na mesma amostra. Sem DI1 previamente observado, manter a rejeição das bordas simultâneas. As demais condições e cancelamentos permanecem em vigor.

## Consequências

Uma repetição de DI1 não anula uma sequência de entrada já comprovada. O polling continua incapaz de determinar a ordem de acionamentos que ocorram pela primeira vez entre as mesmas amostras; a validação física permanece necessária.
