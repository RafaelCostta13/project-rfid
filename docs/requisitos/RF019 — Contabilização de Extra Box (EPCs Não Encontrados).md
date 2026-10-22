# RF019 — Contabilização de Extra Box (EPCs Não Encontrados)

**Projeto:** RFID
**Requisito:** RF019
**Categoria:** Nova funcionalidade / Contabilização RFID
**Prioridade:** Alta
**Ambiente:** Windows
**Interface:** PySide6 + Qt Quick/QML
**Equipamento:** Zebra FX9600
**Backend:** Rails / PostgreSQL
**Status:** A implementar

---

## 1. Objetivo

Implementar uma nova funcionalidade para contabilizar os EPCs lidos
pelo Zebra FX9600 que não forem encontrados no Backend RFID.

Esses EPCs serão classificados visualmente como:

    Extra box

A tela Start deverá apresentar um novo card contendo exclusivamente
a quantidade total de EPCs distintos não encontrados.

O novo card deverá ficar ao lado do card existente:

    EPCs encontrados

A funcionalidade deverá preservar integralmente o fluxo operacional
atual, incluindo a leitura RFID, a consulta ao Backend e o registro
das passagens dos EPCs encontrados.

---

## 2. Contexto atual

Atualmente, o sistema executa o seguinte fluxo:

    Zebra FX9600
          |
          v
    EPC identificado
          |
          v
    GET /api/v1/rfid_records/:epc
          |
          v
    EPC encontrado?
          |
          +---- SIM
          |      |
          |      v
          |   Registrar passagem
          |      |
          |      v
          |   Atualizar tabela
          |      |
          |      v
          |   Incrementar contador
          |
          +---- NÃO
                 |
                 v
              Ignorar EPC

A regra atual foi estabelecida anteriormente para apresentar
somente EPCs encontrados na base.

O RF019 altera exclusivamente o tratamento estatístico dos EPCs
não encontrados.

A partir deste requisito, os EPCs não encontrados continuarão
fora da tabela, mas serão contabilizados no novo card Extra box.

---

## 3. Novo fluxo esperado

    Zebra FX9600
          |
          v
    EPC recebido
          |
          v
    Normalização e deduplicação
          |
          v
    GET /api/v1/rfid_records/:epc
          |
          v
    Resultado da consulta
          |
          +----------------------------+
          |                            |
          v                            v
    EPC ENCONTRADO               EPC NÃO ENCONTRADO
          |                            |
          v                            v
    Fluxo atual RF016/RF017      Classificar Extra box
          |                            |
          v                            v
    Registrar passagem           Incrementar contador
          |                            |
          v                            v
    Atualizar tabela             Atualizar card Extra box
          |                            |
          v                            |
    Atualizar contador                 |
    EPCs encontrados                   |
          |                            |
          +----------------------------+
                       |
                       v
                 Interface QML

A classificação deverá ser realizada pela camada operacional Python.

O QML será responsável exclusivamente por apresentar os totais.

---

## 4. Requisito funcional RF019.01 — Identificação de Extra box

Um EPC será classificado como Extra box quando:

1. For recebido validamente pelo Zebra FX9600.
2. Passar pelas validações existentes de EPC.
3. For consultado no Backend RFID.
4. O Backend confirmar que o EPC não existe na base.

O endpoint continuará sendo:

    GET /api/v1/rfid_records/:epc

Condição principal:

    HTTP 404
        |
        v
    EPC não encontrado
        |
        v
    Extra box

Caso o contrato atual do Backend possua outra representação
explícita e documentada para EPC inexistente, respeitar esse
contrato após inspecionar a implementação real.

Não interpretar erros técnicos como EPC não encontrado.

---

## 5. Requisito funcional RF019.02 — Contabilização

O sistema deverá manter um contador específico:

    extra_box_count

Esse nome é apenas uma sugestão.

Utilizar a nomenclatura compatível com a arquitetura existente.

### Regra de contagem

Cada EPC distinto não encontrado deverá ser contabilizado
uma única vez durante a mesma sessão de leitura.

Exemplo:

    EPC A -> Não encontrado
    EPC B -> Não encontrado
    EPC A -> Não encontrado
    EPC C -> Não encontrado
    EPC B -> Não encontrado

Resultado esperado:

    Extra box = 3

Os EPCs A, B e C representam três etiquetas distintas.

As leituras repetidas de A e B não devem aumentar o contador.

### Regra crítica

Não contabilizar a quantidade de callbacks recebidos do Zebra.

Contabilizar a quantidade de EPCs distintos cuja ausência
tenha sido confirmada pelo Backend durante a sessão.

---

## 6. Requisito funcional RF019.03 — Deduplicação

O Zebra FX9600 pode identificar a mesma etiqueta várias vezes
durante o inventário RFID.

Portanto, o sistema deverá preservar a deduplicação existente.

Implementar ou reutilizar uma estrutura de controle equivalente a:

    extra_box_epcs = set()

Quando o Backend confirmar que um EPC não foi encontrado:

    Se EPC não estiver em extra_box_epcs:
        Adicionar EPC ao conjunto
        Incrementar extra_box_count

    Caso contrário:
        Não incrementar

A estrutura deverá permanecer interna à aplicação.

Não expor a lista de EPCs Extra box na interface.

Não criar mecanismos paralelos de deduplicação caso o
controller atual já forneça essa funcionalidade.

---

## 7. Requisito funcional RF019.04 — Contador por sessão

O contador Extra box deverá seguir o mesmo ciclo de vida
do contador existente EPCs encontrados.

### Início de nova sessão

Ao iniciar uma nova sessão de leitura, conforme a definição
já implementada no sistema:

    EPCs encontrados = 0
    Extra box = 0

Preservar a política atual de início e reinicialização
de sessão.

Não redefinir o conceito de sessão neste requisito.

### Durante a sessão

Atualizar os dois contadores conforme os resultados das
consultas ao Backend.

### Finalização da sessão

Aplicar a mesma política de retenção ou limpeza visual
já utilizada pelo contador EPCs encontrados.

Não limpar Extra box em um momento diferente do contador
existente.

### Atenção

Não reiniciar os contadores a cada leitura de EPC.

Não reiniciar os contadores a cada atualização visual.

Não reiniciar os contadores devido a uma reconexão QML.

Não reiniciar os contadores devido a um novo callback do Zebra.

---

## 8. Requisito funcional RF019.05 — Novo card Extra box

Adicionar um card na tela Start com o título:

    Extra box

O card deverá apresentar:

    Título: Extra box

    Valor: quantidade de EPCs distintos não encontrados

Exemplo:

    ┌──────────────────────────┐
    │                          │
    │        Extra box         │
    │                          │
    │            7             │
    │                          │
    └──────────────────────────┘

Não apresentar os códigos EPC.

Não apresentar cliente.

Não apresentar nota fiscal.

Não apresentar pedido.

Não apresentar detalhes das etiquetas.

O objetivo é exclusivamente a contabilização.

---

## 9. Requisito funcional RF019.06 — Posicionamento visual

O novo card Extra box deverá ficar imediatamente ao lado
do card existente EPCs encontrados.

Layout conceitual:

    ┌──────────────────────────┐  ┌──────────────────────────┐
    │                          │  │                          │
    │     EPCs encontrados     │  │        Extra box         │
    │                          │  │                          │
    │            15            │  │            4             │
    │                          │  │                          │
    └──────────────────────────┘  └──────────────────────────┘

### Regras de design

- Utilizar o mesmo componente visual de card existente.
- Preservar o tema QML aprovado no RF018.
- Preservar tipografia.
- Preservar bordas.
- Preservar espaçamentos.
- Preservar altura dos cards.
- Preservar alinhamento.
- Manter os dois cards visualmente equilibrados.

O novo card deverá utilizar a mesma hierarquia visual
do card EPCs encontrados.

### Cores

O card EPCs encontrados deverá manter o estilo atual.

O card Extra box poderá utilizar uma cor de atenção
já existente no tema, como amarelo/âmbar.

Não utilizar vermelho de erro apenas porque o EPC não
foi encontrado.

Um EPC não encontrado representa uma classificação
de negócio, não necessariamente uma falha técnica.

Não alterar a paleta global da aplicação.

---

## 10. Requisito funcional RF019.07 — Preservação da tabela

A tabela atual deverá continuar apresentando somente
EPCs encontrados no Backend.

Preservar as colunas existentes:

    Status
    Cliente
    Nota fiscal
    Volume
    Pedido
    Doca

### Regra obrigatória

EPCs classificados como Extra box NÃO deverão ser
adicionados à tabela.

Não criar:

- Nova coluna Extra box.
- Nova linha para EPC não encontrado.
- Nova tabela de EPCs não encontrados.
- Tela adicional para Extra box.

O RF019 exige somente um novo contador visual.

---

## 11. Requisito funcional RF019.08 — Tratamento de respostas HTTP

A classificação deverá respeitar o resultado real da
consulta ao Backend.

### Cenário A — HTTP 200

O EPC foi encontrado e a resposta contém um registro válido.

Resultado:

    Fluxo atual de EPC encontrado

    Extra box não incrementa

Preservar GET/POST e as demais regras atuais.

### Cenário B — HTTP 404

O EPC não existe na base.

Resultado:

    Extra box incrementa uma vez por EPC distinto

    Não executar POST

    Não adicionar à tabela

### Cenário C — HTTP 500

Ocorreu erro no Backend.

Resultado:

    Não incrementar Extra box

    Não classificar EPC como inexistente

    Preservar tratamento de erro atual

### Cenário D — Timeout

A consulta não foi concluída.

Resultado:

    Não incrementar Extra box

    Não classificar EPC como inexistente

    Preservar tratamento atual de timeout

### Cenário E — Falha de conexão

O Backend está indisponível.

Resultado:

    Não incrementar Extra box

    Preservar o monitoramento do Sistema

### Cenário F — EPC inválido

O EPC não atende às validações existentes.

Resultado:

    Não consultar ou contabilizar indevidamente

    Preservar as regras atuais de validação

### Cenário G — HTTP 200 com resposta inválida

Não classificar automaticamente como Extra box.

Preservar o tratamento de erro de contrato existente.

### Regra crítica

    Não encontrado != Erro de comunicação

Somente uma confirmação válida de inexistência deverá
aumentar o contador Extra box.

---

## 12. Requisito funcional RF019.09 — Atualização em tempo real

Quando um novo EPC não encontrado for confirmado,
o contador Extra box deverá ser atualizado automaticamente.

Fluxo:

    Backend retorna 404
          |
          v
    Controller classifica EPC
          |
          v
    Atualiza contador da sessão
          |
          v
    Emite evento de atualização
          |
          v
    Qt Bridge
          |
          v
    QML atualiza card Extra box

Não utilizar polling adicional para atualizar o card.

Não executar consultas HTTP dentro do QML.

Não manipular diretamente objetos QML a partir
das threads de LLRP ou HTTP.

Utilizar o mecanismo de signals/slots e propriedades
já adotado no RF018.

---

## 13. Requisito funcional RF019.10 — Concorrência

O sistema deverá suportar múltiplas leituras RFID
em um curto intervalo.

Exemplo:

    Zebra recebe EPC A
    Zebra recebe EPC A novamente
    Primeira consulta ainda está em andamento

Resultado esperado:

    Apenas uma classificação Extra box para EPC A
    durante a sessão.

Preservar o controle de requisições em andamento
existente no controller.

Evitar condições de corrida entre:

- Callback RFID.
- Consulta HTTP.
- Deduplicação.
- Atualização do contador.
- Atualização do modelo Qt.

Se duas respostas referentes ao mesmo EPC chegarem
simultaneamente, o contador deverá incrementar
no máximo uma vez.

---

## 14. Requisito funcional RF019.11 — Respostas tardias

Considerar o cenário:

    Sessão A inicia
        |
        v
    EPC não encontrado é consultado
        |
        v
    Sessão A termina
        |
        v
    Sessão B inicia
        |
        v
    Resposta HTTP 404 da sessão A chega

A resposta antiga não poderá incrementar o contador
da sessão B.

Utilizar o identificador de sessão ou geração
já existente no fluxo operacional.

Não permitir que respostas antigas alterem os
contadores da sessão atual.

Não modificar o controle físico dos relés em
consequência de uma resposta tardia.

---

## 15. Requisito funcional RF019.12 — Preservação do fluxo operacional

O RF019 não poderá modificar o fluxo validado
de leitura automática.

Preservar:

    DI1 interrompido
          |
          v
    Iniciar inventário RFID
          |
          v
    CH2 ON
          |
          v
    Leitura EPC
          |
          v
    GET Backend
          |
          v
    Classificação encontrado / Extra box
          |
          v
    DI2 interrompido ou timeout
          |
          v
    Finalizar leitura
          |
          v
    CH1 ON, se sistema apto

Não alterar:

- Timer de 60 segundos.
- DI1.
- DI2.
- CH1.
- CH2.
- CH3.
- Start/Stop.
- Máquina de estados.
- Critérios de disponibilidade.
- Gerenciamento de sessões físicas.

O contador Extra box deverá ser passivo.

Ele não poderá iniciar, interromper ou prolongar
um ciclo de leitura RFID.

---

## 16. Requisito funcional RF019.13 — Preservação do Backend

O RF019 não exige alterações no Backend Rails.

Continuar utilizando:

    GET /api/v1/rfid_records/:epc

Para EPCs encontrados, preservar:

    POST /api/v1/rfid_reads

Para EPCs não encontrados:

    Não executar POST

Não criar novos endpoints.

Não alterar o contrato JSON.

Não criar tabelas no PostgreSQL.

Não criar armazenamento local para Extra box.

Não implementar sincronização SQLite.

Não utilizar Power Automate.

A contabilização Extra box será realizada
na memória da sessão da aplicação Python.

---

## 17. Arquitetura esperada

A implementação deverá seguir a arquitetura
PySide6 + QML estabelecida no RF018.

    ┌──────────────────────────────────┐
    │          Zebra FX9600            │
    └────────────────┬─────────────────┘
                     |
                     v
    ┌──────────────────────────────────┐
    │          RFID Service            │
    └────────────────┬─────────────────┘
                     |
                     v
    ┌──────────────────────────────────┐
    │       Application Controller     │
    │                                  │
    │ - Deduplicação                   │
    │ - Controle de sessão             │
    │ - Consulta EPC                   │
    │ - Classificação Extra box        │
    │ - Contadores                     │
    └────────────────┬─────────────────┘
                     |
                     v
    ┌──────────────────────────────────┐
    │             Qt Bridge            │
    │                                  │
    │ - foundCount                     │
    │ - extraBoxCount                  │
    └────────────────┬─────────────────┘
                     |
                     v
    ┌──────────────────────────────────┐
    │               QML                │
    │                                  │
    │ EPCs encontrados | Extra box     │
    └──────────────────────────────────┘

Os nomes das propriedades são sugestões.

Reutilizar a arquitetura existente.

Não criar controllers duplicados.

Não criar um novo serviço HTTP.

Não duplicar o estado da sessão.

---

## 18. Análise obrigatória antes da implementação

Antes de modificar qualquer arquivo, o Codex deverá:

1. Ler AGENTS.md e as instruções do projeto.
2. Confirmar a branch atual.
3. Verificar o estado do Git.
4. Localizar o controller de leitura RFID.
5. Localizar a implementação do GET de EPC.
6. Localizar o tratamento atual de HTTP 404.
7. Localizar a deduplicação de EPCs.
8. Localizar o contador EPCs encontrados.
9. Identificar a política atual de sessão.
10. Localizar o componente QML do card.
11. Localizar a Qt Bridge.
12. Identificar os testes existentes.

Verificar se o retorno 404 atualmente é simplesmente
ignorado ou se existe um evento de resultado de consulta
que possa ser reutilizado.

Preferir adicionar a contabilização nesse ponto.

Não refatorar amplamente o fluxo RFID.

---

## 19. Estratégia de implementação

Executar a implementação na seguinte sequência:

### Etapa 1 — Identificar resultado não encontrado

Localizar o ponto onde o Backend confirma que o EPC
não foi encontrado.

Garantir que a classificação não confunda 404
com falhas técnicas.

### Etapa 2 — Contador de sessão

Adicionar o controle de EPCs Extra box distintos
ao estado da sessão existente.

Garantir inicialização, deduplicação e limpeza corretas.

### Etapa 3 — Evento de atualização

Expor a alteração do contador através do mecanismo
de eventos existente.

### Etapa 4 — Qt Bridge

Adicionar propriedade ou signal para disponibilizar
o total Extra box ao QML.

### Etapa 5 — Card QML

Adicionar o card Extra box ao lado do card
EPCs encontrados.

Preservar o design aprovado.

### Etapa 6 — Testes

Implementar testes unitários e de integração simulada.

### Etapa 7 — Revisão

Revisar o diff para confirmar que somente os
componentes necessários foram modificados.

---

## 20. Cenários de teste

### Teste 01 — Nenhum EPC

Entrada:

    Nenhuma leitura RFID

Resultado:

    EPCs encontrados = 0
    Extra box = 0

### Teste 02 — Um EPC encontrado

Entrada:

    EPC A -> HTTP 200

Resultado:

    EPCs encontrados = 1
    Extra box = 0

### Teste 03 — Um EPC não encontrado

Entrada:

    EPC A -> HTTP 404

Resultado:

    EPCs encontrados = 0
    Extra box = 1

### Teste 04 — Múltiplos EPCs não encontrados

Entrada:

    EPC A -> 404
    EPC B -> 404
    EPC C -> 404

Resultado:

    EPCs encontrados = 0
    Extra box = 3

### Teste 05 — EPC não encontrado repetido

Entrada:

    EPC A -> 404
    EPC A -> 404
    EPC A -> 404

Resultado:

    Extra box = 1

### Teste 06 — Leitura mista

Entrada:

    EPC A -> 200
    EPC B -> 404
    EPC C -> 200
    EPC D -> 404
    EPC E -> 404

Resultado:

    EPCs encontrados = 2
    Extra box = 3

### Teste 07 — Backend indisponível

Entrada:

    EPC A -> HTTP 500
    EPC B -> Timeout

Resultado:

    Extra box = 0

### Teste 08 — Nova sessão

Sessão A:

    Extra box = 5

Nova sessão B:

    Extra box = 0

Aplicar a mesma política de reinicialização
utilizada pelo contador EPCs encontrados.

### Teste 09 — Resposta tardia

Entrada:

    EPC A consultado na sessão A
    Sessão A encerrada
    Sessão B iniciada
    Resposta 404 da sessão A recebida

Resultado:

    Extra box da sessão B não incrementa

### Teste 10 — POST

Entrada:

    EPC A -> HTTP 404

Resultado:

    Extra box = 1
    Nenhum POST de passagem executado

### Teste 11 — Tabela

Entrada:

    EPC A -> 200
    EPC B -> 404

Resultado:

    Tabela apresenta somente EPC A

    Extra box = 1

### Teste 12 — Concorrência

Entrada:

    Múltiplos callbacks simultâneos do mesmo EPC

Resultado:

    Extra box incrementa no máximo uma vez

### Teste 13 — Atualização visual

Entrada:

    Re-renderização do componente QML

Resultado:

    Nenhum incremento adicional

### Teste 14 — Regressão operacional

Validar que:

- Zebra continua lendo.
- Backend continua respondendo.
- GET continua funcionando.
- POST continua funcionando.
- DI1 continua iniciando a leitura.
- DI2 continua encerrando a leitura.
- Timer de 60 segundos continua funcionando.
- CH1/CH2/CH3 continuam funcionando.
- Start/Stop permanece funcional.

---

## 21. Critérios de aceite

- [ ] Card Extra box implementado.
- [ ] Card posicionado ao lado de EPCs encontrados.
- [ ] Design QML preservado.
- [ ] Total iniciado em zero.
- [ ] HTTP 404 classifica EPC como Extra box.
- [ ] EPC distinto incrementa apenas uma vez por sessão.
- [ ] Leitura repetida não incrementa novamente.
- [ ] HTTP 500 não incrementa.
- [ ] Timeout não incrementa.
- [ ] Falha de conexão não incrementa.
- [ ] EPC inválido não incrementa.
- [ ] EPC encontrado não incrementa Extra box.
- [ ] EPC não encontrado não aparece na tabela.
- [ ] EPC não encontrado não gera POST.
- [ ] Contador acompanha o ciclo de vida da sessão.
- [ ] Respostas tardias não alteram nova sessão.
- [ ] Atualização QML ocorre em tempo real.
- [ ] Não existem chamadas HTTP no QML.
- [ ] Não existem novos serviços duplicados.
- [ ] Fluxo RF012 preservado.
- [ ] Integração RF016 preservada.
- [ ] Integração RF017 preservada.
- [ ] Indicadores RFID, Internet, Comandos e Sistema preservados.
- [ ] Testes automatizados aprovados.

---

## 22. Fora do escopo

Não implementar neste requisito:

- Listagem de EPCs Extra box.
- Exportação de EPCs Extra box.
- Armazenamento de Extra box no Backend.
- Registro de passagem de EPC inexistente.
- Alterações no PostgreSQL.
- Alterações no Rails.
- Novos endpoints.
- Novas colunas na tabela.
- Novas telas.
- Alterações na comunicação Modbus.
- Alterações na comunicação LLRP.
- Alterações no controle dos relés.
- Alterações no timer operacional.
- Redesenho da interface.
- Modificação dos quatro indicadores de conexão.

---

## 23. Relatório final obrigatório

Ao concluir, apresentar:

1. Branch utilizada.
2. Arquivos criados.
3. Arquivos modificados.
4. Local onde o HTTP 404 passou a ser contabilizado.
5. Estrutura de deduplicação utilizada.
6. Local de armazenamento do contador na sessão.
7. Integração com a Qt Bridge.
8. Componente QML utilizado.
9. Testes implementados.
10. Testes executados.
11. Testes aprovados.
12. Testes reprovados.
13. Resultado da regressão.
14. Confirmação de ausência de alterações no Backend.
15. Confirmação de preservação do fluxo operacional.

---

## 24. Definição de pronto

O RF019 estará concluído quando a tela Start apresentar
os dois contadores:

    EPCs encontrados | Extra box

O primeiro deverá continuar contabilizando os EPCs
encontrados conforme as regras atuais.

O segundo deverá contabilizar os EPCs distintos cuja
inexistência foi confirmada pelo Backend durante a sessão.

Os EPCs Extra box não deverão aparecer na tabela e não
deverão gerar registros de passagem.

A implementação deverá reutilizar os serviços Python
existentes e preservar integralmente a arquitetura
PySide6 + QML.

**Implementar o RF019 completo, incluindo lógica de
contabilização, integração Qt, componente visual e testes
automatizados, sem alterar as regras operacionais existentes.** 