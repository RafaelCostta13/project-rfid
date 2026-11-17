# ADR 030 — Reestruturação do controle dos sensores

## Contexto

A proximidade dos sensores pode fazer as duas bordas aparecerem na mesma
amostra. O requisito solicitado também simplifica a saída e acrescenta início
de passagem pelo pedal. O arquivo do requisito é identificado como RF041 no
nome e RF042 no conteúdo.

## Decisão

Reutilizar o controlador existente: iniciar por DI1 seguido de DI4 ou ambos
interrompidos, encerrar por DI2 e retirar DI5 das decisões operacionais.
DI3 inicia passagem nova ou retoma a passagem após timeout, conforme o estado.
Manter o debounce do pedal, o rearme dos sensores e os controles dos relés.
Reduzir o timeout para 30 segundos e a espera operacional de polling para 20 ms,
mantendo a sessão Modbus serializada e o diagnóstico físico de DI5.

## Consequências

A condição simultânea não determina a ordem física e pode aceitar acionamentos
em ordem inversa. O intervalo efetivo inclui comunicação e processamento e
deve ser medido no equipamento; pulsos curtos ainda podem ser perdidos.
Os resultados e a estabilidade dependem de homologação física no Windows.
