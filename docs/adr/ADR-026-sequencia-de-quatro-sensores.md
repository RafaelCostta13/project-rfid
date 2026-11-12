# ADR-026 — Sequência de quatro sensores para a passagem RFID

## Contexto

A instalação usa DI1 e DI4 na entrada e DI5 e DI2 na saída. Uma amostra de estados simultâneos não comprova a direção de passagem. A regra anterior encerrava a passagem em DI2 isolado.

## Decisão

O controlador operacional reconhece bordas `True → False` na ordem DI1 → DI4 para abrir e DI5 → DI2 para encerrar normalmente. Ele exige DI2 livre para iniciar, preservando a proteção anterior. Pares de bordas detectados na mesma amostra não são ordenados; acionamentos de saída durante entrada pendente invalidam essa entrada. Uma amostra inicial com feixes interrompidos não inicia uma passagem.

Timeout preserva a passagem e uma eventual saída pendente. A reabertura por DI3 invalida a saída pendente; uma saída completa tem prioridade sobre o pedal. Stop e falhas invalidam sequências pendentes. O tratamento de relés, desconexões e timer permanece no controlador existente.

## Consequências

DI2 isolado deixa de encerrar normalmente, conforme RF040. O polling pode não observar eventos rápidos ou simultâneos, que não serão presumidos em ordem. A polaridade, a temporização e a posição dos quatro sensores e do pedal precisam de homologação com o equipamento físico.
