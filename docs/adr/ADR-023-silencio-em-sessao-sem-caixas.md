# ADR-023 — Silêncio em sessão sem caixas

## Contexto

O anúncio de zero caixas ao encerrar uma leitura não é necessário para a operação.

## Decisão

Anunciar o total de caixas encontradas apenas quando for maior que zero, tanto na leitura operacional quanto no simulador.

## Consequências

Sessões sem caixas encontradas terminam sem anúncio de voz; contagens positivas continuam sendo anunciadas.
