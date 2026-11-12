# ADR-029 — Preservação da saída armada quando DI5 se repete

## Contexto

Uma passagem pode ter DI5 reconhecido antes de uma nova amostra apresentar bordas simultâneas de DI5 e DI2. A lógica descartava o encerramento mesmo com DI5 anterior comprovado.

## Decisão

Quando DI5 já tiver armado a saída, aceitar a borda posterior de DI2 mesmo que DI5 apresente uma nova borda na mesma amostra. Sem DI5 anterior, continuar rejeitando bordas simultâneas. O encerramento válido mantém prioridade sobre o pedal e funciona durante a leitura e após o timeout.

## Consequências

Uma repetição de DI5 não cancela uma saída já armada. A ordem de dois primeiros acionamentos observados na mesma amostra continua indeterminada. A validação da operação exige testes no portal físico.
