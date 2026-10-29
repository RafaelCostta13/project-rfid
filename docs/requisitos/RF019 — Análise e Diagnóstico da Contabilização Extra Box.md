# RF019 — Análise e Diagnóstico da Contabilização Extra Box

## 1. Objetivo

Realizar uma análise técnica completa da funcionalidade Extra box,
implementada no RF019 do projeto RFID.

Identificamos dois pontos que precisam ser investigados:

1. EPCs não encontrados no Backend não estão sendo contabilizados
   corretamente no card Extra box.

2. A regra Extra box precisa ser ampliada para também contabilizar
   EPCs encontrados no Backend que já possuem status "lido".

IMPORTANTE:

Nesta etapa, realizar somente análise, diagnóstico e planejamento.

Não modificar o código da aplicação antes de apresentar os resultados.

---

## 2. Contexto do projeto

Aplicação desktop desenvolvida em:

- Python.
- PySide6 + QML.
- Windows.

Integrações:

- Zebra FX9600 via LLRP.
- Waveshare Modbus RTU Relay.
- Backend Rails.
- PostgreSQL.

Requisitos relacionados:

- RF016 — Consulta e validação remota do EPC.
- RF017 — Registro de passagem RFID.
- RF018 — Interface PySide6 + QML.
- RF019 — Contabilização Extra box.

A tela Start possui dois cards:

    EPCs encontrados
    Extra box

Atualmente, o card Extra box não está apresentando corretamente
a quantidade de etiquetas não encontradas.

Precisamos identificar a causa desse comportamento.

---

## 3. Nova regra de negócio desejada

O card Extra box deverá contabilizar duas situações distintas:

### Situação A — EPC não encontrado

O Zebra FX9600 identifica um EPC.

O sistema consulta:

    GET /api/v1/rfid_records/:epc

O Backend retorna:

    HTTP 404

Resultado esperado:

    Classificar como Extra box.
    Incrementar o contador Extra box.

### Situação B — EPC já lido

O Zebra FX9600 identifica um EPC.

O sistema consulta:

    GET /api/v1/rfid_records/:epc

O Backend retorna:

    HTTP 200

O registro encontrado possui:

    status = "lido"

Resultado esperado:

    Classificar como Extra box.
    Incrementar o contador Extra box.

### Situação C — EPC pendente

O Backend retorna:

    HTTP 200

O registro possui:

    status = "pendente"

Resultado esperado:

    Manter o fluxo normal de EPC encontrado.
    Não incrementar Extra box.

### Regra consolidada

    EPC recebido
         |
         v
    Consulta Backend
         |
         v
    Resultado?
         |
         +--- HTTP 404
         |       |
         |       v
         |    EXTRA BOX
         |
         +--- HTTP 200
         |       |
         |       v
         |    Verificar status
         |       |
         |       +--- "pendente"
         |       |       |
         |       |       v
         |       |    EPC ENCONTRADO
         |       |
         |       +--- "lido"
         |               |
         |               v
         |            EXTRA BOX
         |
         +--- Erro técnico
                 |
                 v
             NÃO CONTABILIZAR

Não confundir HTTP 404 com erro de comunicação.

Não confundir status "lido" com uma nova leitura válida
que acabou de ser registrada durante a sessão atual.

---

## 4. Análise obrigatória — Tratamento HTTP 404

Localizar o código responsável por consultar o Backend.

Identificar exatamente o comportamento quando o endpoint retorna:

    HTTP 404

Verificar:

1. Se o Backend Client recebe corretamente o status 404.
2. Se a resposta 404 é convertida em exceção.
3. Se o controller trata essa exceção.
4. Se o EPC é descartado antes da contabilização.
5. Se existe algum return antecipado.
6. Se o evento de EPC não encontrado é emitido.
7. Se o contador Extra box é atualizado.
8. Se o novo valor chega à Qt Bridge.
9. Se o QML recebe a notificação de alteração.
10. Se o card apresenta o valor atualizado.

Investigar especialmente se a regra anterior,
que ignorava EPCs não encontrados, continua ativa.

Essa regra foi utilizada antes da criação do RF019
e pode estar impedindo a contabilização.

Não assumir que essa é a causa sem verificar o código.

---

## 5. Análise obrigatória — Status "lido"

Localizar como o sistema interpreta o campo:

    status

Investigar os valores:

    pendente
    lido

Verificar:

1. Onde o status é extraído do JSON.
2. Se existe normalização do valor.
3. Se o status "lido" é identificado corretamente.
4. Se registros com status "lido" entram na tabela.
5. Se esses registros incrementam EPCs encontrados.
6. Se esses registros executam POST de passagem.
7. Se existe alguma lógica de bloqueio para EPC já processado.
8. Se a regra RF017 trata de maneira diferente uma leitura
   anteriormente registrada.

Analisar também o comportamento do endpoint:

    POST /api/v1/rfid_reads

O Backend pode retornar informações como:

    duplicate: true

Investigar a diferença entre:

- EPC que já estava com status "lido" antes da consulta.
- EPC que estava "pendente" e foi marcado como "lido"
  pelo POST da sessão atual.
- EPC que gerou um evento de passagem duplicado.

Essas situações não devem ser confundidas.

IMPORTANTE:

Não modificar o comportamento do POST nesta análise.

Documentar se a classificação de um EPC previamente "lido"
como Extra box exige alguma alteração futura na chamada POST.

---

## 6. Análise obrigatória — Deduplicação

O Zebra FX9600 pode identificar a mesma etiqueta
várias vezes durante uma sessão de inventário.

O contador Extra box deve representar EPCs distintos
classificados como Extra box durante a sessão.

Exemplo:

    EPC A -> HTTP 404
    EPC A -> HTTP 404
    EPC B -> status "lido"
    EPC B -> status "lido"
    EPC C -> HTTP 404

Resultado esperado:

    Extra box = 3

Investigar:

1. Como a deduplicação está implementada.
2. Se o RF019 possui um conjunto próprio de EPCs Extra box.
3. Se o sistema descarta EPCs repetidos antes da classificação.
4. Se a deduplicação está impedindo atualizações legítimas.
5. Se múltiplas consultas simultâneas podem duplicar a contagem.
6. Se existe separação entre EPCs encontrados e Extra box.
7. Se o estado de uma sessão anterior interfere na atual.

A mesma etiqueta não deverá aumentar repetidamente
o contador Extra box dentro da mesma sessão.

---

## 7. Análise obrigatória — Ciclo de vida da sessão

Identificar como os contadores são inicializados,
atualizados e reiniciados.

Verificar:

- Início de uma nova sessão.
- Início do inventário RFID.
- Interrupção de DI1.
- Interrupção de DI2.
- Timeout de 60 segundos.
- Encerramento da leitura.
- Acionamento de Stop.
- Reinício do modo automático.
- Reconexão com o Backend.
- Reconexão com o Zebra.

Comparar o ciclo de vida de:

    EPCs encontrados

com:

    Extra box

Identificar se o contador Extra box está sendo
reiniciado indevidamente durante a leitura.

Verificar também se respostas HTTP tardias podem
atualizar o contador de uma sessão diferente.

---

## 8. Análise obrigatória — Qt Bridge e QML

Localizar o componente QML responsável pelo card:

    Extra box

Identificar:

1. Qual propriedade fornece o valor.
2. Qual objeto Python mantém o contador.
3. Como a propriedade é exposta à Qt Bridge.
4. Qual signal informa alterações.
5. Se existe NOTIFY associado à propriedade.
6. Se o QML está utilizando o binding correto.
7. Se o componente recebe atualizações em tempo real.
8. Se o card utiliza algum valor fixo ou mock.
9. Se existem duas fontes de estado concorrentes.
10. Se o valor é reiniciado durante uma atualização da interface.

Verificar se o problema está:

- Na classificação do EPC.
- Na contabilização.
- Na comunicação Python/Qt.
- No binding QML.
- Ou em uma combinação desses pontos.

---

## 9. Análise obrigatória — Classificações exclusivas

Avaliar como implementar as seguintes classificações:

| Resultado Backend | Classificação desejada |
|---|---|
| HTTP 200 + status pendente | EPC encontrado |
| HTTP 200 + status lido previamente | Extra box |
| HTTP 404 | Extra box |
| HTTP 500 | Erro técnico |
| Timeout | Erro técnico |
| Falha de conexão | Erro técnico |
| Resposta inválida | Erro técnico |

Investigar se um mesmo EPC pode aparecer simultaneamente
nas contagens:

    EPCs encontrados
    Extra box

Propor uma política consistente para evitar dupla
contabilização na mesma sessão.

Considerar especialmente o cenário:

1. EPC A é consultado como "pendente".
2. EPC A é registrado via POST.
3. O Backend altera seu status para "lido".
4. O Zebra identifica EPC A novamente.

Não classificar automaticamente essa repetição
como uma nova Extra box sem avaliar a deduplicação
e as regras de sessão existentes.

A análise deve distinguir EPC já lido anteriormente
de EPC processado na sessão atual.

---

## 10. Testes que deverão ser avaliados

Analisar a cobertura atual e identificar testes
ausentes para os seguintes cenários.

### Teste A — EPC não encontrado

    GET -> HTTP 404

Esperado:

    Extra box = 1

### Teste B — EPC já lido

    GET -> HTTP 200
    status = "lido"

Esperado:

    Extra box = 1

### Teste C — EPC pendente

    GET -> HTTP 200
    status = "pendente"

Esperado:

    EPCs encontrados = 1
    Extra box = 0

### Teste D — Leitura mista

    EPC A -> pendente
    EPC B -> lido
    EPC C -> HTTP 404
    EPC D -> lido
    EPC E -> pendente

Esperado:

    EPCs encontrados = 2
    Extra box = 3

### Teste E — Leituras repetidas

    EPC A -> HTTP 404
    EPC A -> HTTP 404
    EPC A -> HTTP 404

Esperado:

    Extra box = 1

### Teste F — Erro técnico

    EPC A -> HTTP 500
    EPC B -> Timeout

Esperado:

    Extra box = 0

### Teste G — EPC processado na sessão atual

    EPC A -> pendente
    POST EPC A -> sucesso
    EPC A é identificado novamente

Esperado:

    Não gerar contagem dupla indevida.
    Preservar a deduplicação da sessão.

### Teste H — Resposta tardia

    Sessão A consulta EPC
    Sessão A encerra
    Sessão B inicia
    Resposta da sessão A chega

Esperado:

    A resposta antiga não altera a sessão B.

---

## 11. Restrições

Esta análise não autoriza alterações nos seguintes componentes:

- Controle dos relés Waveshare.
- Comunicação Modbus.
- Comunicação LLRP.
- Configuração do Zebra FX9600.
- Máquina de estados operacional.
- Timer de 60 segundos.
- Fluxo DI1/DI2.
- Regras CH1/CH2/CH3.
- Monitoramento dos quatro indicadores.
- Endpoints Rails.
- Banco PostgreSQL.
- Contratos JSON existentes.

Não realizar refatorações amplas.

Não alterar o comportamento do RF017 sem apresentar
uma justificativa e solicitar aprovação.

Não implementar novos endpoints.

Não criar persistência adicional.

---

## 12. Verificação do repositório

Antes da análise, executar:

    git branch --show-current
    git status -sb
    git log --oneline --decorate -10

Ler:

    AGENTS.md

Consultar os documentos disponíveis:

    RF016
    RF017
    RF018
    RF019

Identificar a implementação real de cada requisito.

Não assumir que o código está correto apenas porque
o documento do requisito foi criado.

Comparar o comportamento esperado com o código atual.

---

## 13. Relatório obrigatório

Ao finalizar, apresentar um diagnóstico técnico contendo:

### 13.1 — Estado atual do RF019

Informar:

- O que foi implementado.
- O que não foi implementado.
- O que está parcialmente implementado.
- O que está funcionando.
- O que está apresentando falhas.

### 13.2 — Causa do problema HTTP 404

Identificar por que os EPCs não encontrados
não estão aumentando o contador Extra box.

Apresentar:

- Arquivo.
- Classe.
- Método.
- Trecho relevante.
- Causa identificada.
- Evidência no código.

Se a causa não puder ser confirmada,
indicar claramente o que ainda precisa ser testado.

### 13.3 — Tratamento do status "lido"

Explicar como o sistema trata atualmente
um EPC encontrado com status "lido".

Informar se esse EPC:

- Entra na tabela.
- Incrementa EPCs encontrados.
- Executa POST.
- É ignorado.
- Pode ser contabilizado como Extra box.

### 13.4 — Diagnóstico da interface

Informar se a Qt Bridge e o QML estão recebendo
e apresentando corretamente o contador Extra box.

### 13.5 — Proposta de correção

Apresentar um plano objetivo para corrigir:

1. Contabilização de HTTP 404.
2. Contabilização de EPC previamente "lido".
3. Deduplicação por sessão.
4. Atualização do card Extra box.
5. Prevenção de dupla contabilização.
6. Testes automatizados.

Para cada alteração proposta, informar:

- Arquivo a modificar.
- Responsabilidade da alteração.
- Impacto esperado.
- Risco de regressão.

### 13.6 — Testes

Informar:

- Testes existentes.
- Testes executados durante a análise.
- Resultados observados.
- Testes ausentes.
- Cenários que exigem hardware físico.

---

## 14. Instrução final

Realizar uma análise técnica completa do RF019.

O comportamento desejado é:

    Extra box =
        EPCs distintos não encontrados no Backend
        +
        EPCs distintos previamente classificados como "lido"

Respeitar o ciclo de vida e a deduplicação da sessão.

Identificar por que a contabilização HTTP 404
não está funcionando atualmente.

Analisar a implementação necessária para incluir
o status "lido" na classificação Extra box.

Não modificar arquivos nesta etapa.

Não realizar commits.

Não realizar merges.

Não modificar o Backend.

Não alterar as regras operacionais RFID.

Apresentar o diagnóstico e o plano de correção
para aprovação antes de iniciar a implementação.