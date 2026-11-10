# ADR 022: Texto das opções de voz

## Contexto

A lista de vozes fornece objetos com nome e idioma, enquanto o componente de seleção exibia apenas valores simples.

## Decisão

O componente utiliza o campo indicado por `textRole` para exibir objetos e mantém a exibição direta de valores simples.

## Consequências

Os nomes e idiomas ficam visíveis na lista sem alterar o valor salvo, e os seletores que usam listas de texto continuam compatíveis.
