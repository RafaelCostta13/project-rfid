---
name: feature-implementation
description: Implementar uma funcionalidade numerada descrita em docs, mantendo escopo, critérios de aceite, testes e revisão. Usar quando o pedido mencionar um arquivo de funcionalidade como "000 - Criar ambiente.md".
---

# Feature Implementation

## Entrada esperada

Um documento em `docs/` contendo:

- objetivo;
- contexto;
- escopo;
- fora do escopo;
- requisitos;
- critérios de aceite.

## Processo

1. Leia o `AGENTS.md`.
2. Leia integralmente o documento da funcionalidade.
3. Inspecione o repositório.
4. Compare o estado atual com os critérios de aceite.
5. Crie um plano curto por etapas.
6. Implemente somente o necessário.
7. Marque mentalmente cada critério atendido.
8. Execute verificações.
9. Revise o diff.
10. Apresente um resumo final objetivo.

## Controle de escopo

- Não antecipar funcionalidades futuras.
- Não realizar refatoração ampla sem necessidade.
- Não introduzir banco, API, UI ou infraestrutura porque “poderá ser útil”.
- Não alterar decisões descritas sem explicar o conflito.
- Quando houver ambiguidade pequena, adotar a solução mais simples e registrar a suposição.
- Quando faltar informação que impeça implementação correta, apresentar o bloqueio de forma concreta.

## Documentação

Atualize o documento da funcionalidade apenas quando solicitado ou quando o repositório adotar explicitamente marcação de status.

Não transformar o documento em diário de implementação.

Criar ADR apenas para decisões:

- com impacto arquitetural;
- difíceis de reverter;
- com alternativas relevantes;
- que afetem funcionalidades futuras.

## Finalização

O resumo final deve conter:

- arquivos principais alterados;
- comportamento entregue;
- testes adicionados;
- comandos executados;
- critérios não atendidos;
- limitações ou validações manuais pendentes.

Não declarar conclusão total quando testes obrigatórios estiverem falhando.
