# RF014 — Sincronização da Base Local SQLite e Consulta Local por EPC
## Correção arquitetural do RF013 — Base de Dados, Sincronização e remoção da consulta remota por EPC

---

# 1. Objetivo

Implementar uma mudança arquitetural crítica no software RFID.

A aplicação deixará de consultar o Power Automate/SharePoint individualmente para cada EPC lido pelo Zebra FX9600.

A nova arquitetura deverá funcionar da seguinte forma:

    SharePoint
        │
        ▼
    Power Automate
    Endpoint de sincronização
        │
        │ doca + modifiedSince
        ▼
    Software RFID
        │
        ▼
    SQLite local
        │
        ▼
    Consulta local por EPC

O Power Automate será utilizado exclusivamente para:

- verificar a disponibilidade da fonte remota;
- realizar a carga inicial da base;
- realizar atualizações incrementais;
- alimentar o SQLite local.

A consulta operacional das etiquetas RFID deverá ser realizada exclusivamente no SQLite local utilizando o EPC.

O endpoint antigo que recebe:

    {
        "epc": "..."
    }

não fará mais parte da arquitetura operacional final.

---

# 2. Esta correção substitui a correção anterior do RF013

A correção anterior:

**"CORREÇÃO DO RF013 — Separação entre Consulta por EPC e Endpoint de Sincronização"**

ainda NÃO foi executada.

Portanto, NÃO implementar a correção anterior.

Ela considerava temporariamente a seguinte arquitetura:

    EPC
     ↓
    endpoint antigo
     ↓
    SharePoint

Essa premissa não é mais válida para a arquitetura final.

A arquitetura definitiva passa a ser:

    EPC
     ↓
    SQLite local

e:

    Doca + modifiedSince
             ↓
        Power Automate
             ↓
         SharePoint
             ↓
        SQLite local

---

# 3. Regra arquitetural principal

Existem duas responsabilidades completamente diferentes.

## 3.1 Sincronização

Utiliza:

    Doca
    +
    modifiedSince

Objetivo:

    SharePoint
        ↓
    Power Automate
        ↓
    Software
        ↓
    SQLite

---

## 3.2 Consulta operacional RFID

Utiliza:

    EPC

Objetivo:

    Zebra FX9600
        ↓
       EPC
        ↓
    SQLite local
        ↓
    Dados da etiqueta

---

# 4. Regra obrigatória

O novo endpoint Power Automate NUNCA deve receber EPC.

ERRADO:

    {
        "epc": "484C44303130313237353835"
    }

ERRADO:

    {
        "epc": "484C44303130313237353835",
        "doca": "D01",
        "modifiedSince": "2026-10-05T10:00:00Z"
    }

CORRETO:

    {
        "doca": "D01",
        "modifiedSince": "2026-10-05T10:00:00Z"
    }

O EPC deverá existir somente na lógica de consulta da base local.

---

# 5. Contrato do novo endpoint

O novo Power Automate possui o seguinte contrato:

    {
        "type": "object",
        "properties": {
            "doca": {
                "type": "string"
            },
            "modifiedSince": {
                "type": "string"
            }
        }
    }

Exemplo de carga inicial:

    {
        "doca": "D01",
        "modifiedSince": ""
    }

Exemplo de atualização incremental:

    {
        "doca": "D01",
        "modifiedSince": "2026-10-05T10:00:00Z"
    }

Não modificar esse contrato para adicionar EPC.

---

# 6. Resposta esperada do endpoint

A resposta esperada possui conceitualmente:

    {
        "success": true,
        "syncUntil": "2026-10-05T10:15:00Z",
        "count": 2,
        "items": [
            {
                "sharepointId": 10,
                "status": "Ativo",
                "cliente": "CLIENTE ALFA",
                "notaFiscal": "100001",
                "volume": "1/3",
                "pedido": "500001",
                "doca": "D01",
                "epc": "484C443030303030303031",
                "modified": "2026-10-05T10:10:00Z"
            }
        ]
    }

Antes de gravar qualquer informação no SQLite, validar a resposta.

---

# 7. Campos esperados

A sincronização deverá trabalhar com os campos:

    sharepointId
    status
    cliente
    notaFiscal
    volume
    pedido
    doca
    epc
    modified

O Codex deve verificar os nomes reais utilizados pelo código e pelo JSON retornado.

Não criar conversões ou renomeações desnecessárias se já existir modelo equivalente.

---

# 8. Fonte oficial dos dados

O SharePoint continua sendo a fonte oficial dos dados.

O SQLite será uma réplica/cache operacional local.

Portanto:

    SHAREPOINT
       │
       │ fonte oficial
       ▼
    POWER AUTOMATE
       │
       ▼
    SQLITE
       │
       │ base operacional
       ▼
    SOFTWARE RFID

Alterações de negócio continuam ocorrendo no SharePoint.

O SQLite não deve se tornar uma segunda fonte de verdade.

---

# 9. Configuração da Doca

Preservar a configuração criada no RF013.

A estação deve possuir uma Doca configurada.

Exemplo:

    Doca = D01

Essa configuração será utilizada pelo serviço de sincronização.

Exemplo:

    Configuração
         │
         ▼
      Doca D01
         │
         ▼
    {
        "doca": "D01",
        "modifiedSince": "..."
    }

Não utilizar Doca fixa no código.

---

# 10. Banco de dados local

Utilizar SQLite como banco de dados local.

Preferir a biblioteca `sqlite3` da biblioteca padrão do Python, salvo se o projeto já possuir uma abstração de banco de dados que justifique outra abordagem.

Não adicionar ORM ou dependência externa apenas para esta funcionalidade sem necessidade.

O arquivo SQLite deve ficar em local persistente apropriado para a aplicação Windows.

Antes de definir o caminho, analisar como o projeto atualmente armazena:

- configurações;
- arquivos persistentes;
- logs;
- dados da aplicação.

Não salvar o banco em diretório temporário.

Não depender do diretório atual de execução.

---

# 11. Estrutura conceitual da tabela de etiquetas

Criar uma tabela equivalente a:

    etiquetas

Campos conceituais:

    id
    sharepoint_id
    epc
    status
    cliente
    nota_fiscal
    volume
    pedido
    doca
    sharepoint_modified
    synced_at

O nome real da tabela e das colunas pode seguir o padrão do projeto.

---

# 12. Identificadores

`sharepoint_id` deve preservar o ID original do registro no SharePoint.

`epc` deve preservar o EPC utilizado pela aplicação RFID.

Não utilizar o ID interno autoincremental do SQLite como identificador de negócio do registro.

---

# 13. Índice do EPC

A consulta por EPC será uma operação crítica e frequente.

Criar índice apropriado para:

    epc

A consulta operacional não deve realizar varredura completa da tabela.

A estrutura deve permitir busca eficiente pelo EPC.

---

# 14. Doca na base local

Os registros devem preservar a Doca.

Exemplo:

    epc = 484C443030303030303031
    doca = D01

A consulta operacional deve considerar a Doca configurada na estação.

Conceitualmente:

    SELECT ...
    FROM etiquetas
    WHERE epc = ?
      AND doca = ?
    LIMIT 1;

Adaptar ao schema real.

Isso evita que uma estação configurada como D01 utilize acidentalmente registros pertencentes a outra Doca.

---

# 15. Status dos registros

Preservar o campo:

    status

A base atualmente possui estados como:

    Ativo
    Inativo

A sincronização deve atualizar esse campo normalmente.

Registros alterados para `Inativo` devem continuar chegando pelo incremental, pois a alteração modifica o registro no SharePoint.

A consulta operacional não deve considerar uma etiqueta inativa como uma etiqueta válida caso essa seja a semântica atual da base.

Antes de implementar essa filtragem, confirmar no código/dados atuais a semântica utilizada para `status`.

Não apagar automaticamente o histórico local apenas porque um registro ficou inativo.

---

# 16. Tabela de controle de sincronização

Criar uma estrutura de controle separada.

Exemplo conceitual:

    sync_control

Campos mínimos conceituais:

    doca
    last_sync
    last_full_sync
    last_success_at
    initialized

A Doca deve ser a chave lógica desse controle.

---

# 17. Cursor separado por Doca

O cursor de sincronização deve ser armazenado separadamente para cada Doca.

Exemplo:

    D01
    last_sync = 2026-10-05T10:00:00Z

    D05
    last_sync = 2026-10-05T09:30:00Z

Nunca utilizar o `last_sync` de D01 para sincronizar D05.

---

# 18. Primeira sincronização

Quando não existir uma sincronização inicial válida para a Doca configurada:

    modifiedSince = ""

Exemplo:

    {
        "doca": "D01",
        "modifiedSince": ""
    }

Isso representa a carga inicial.

O Power Automate deverá retornar todos os registros aplicáveis à Doca.

---

# 19. Fluxo da primeira sincronização

Fluxo esperado:

    Aplicação inicia
          │
          ▼
    Carrega Doca
          │
          ▼
        D01
          │
          ▼
    Existe base inicial válida
    para D01?
       │       │
      NÃO     SIM
       │       │
       ▼       ▼
    Carga     Incremental
    inicial
       │
       ▼
    modifiedSince = ""

---

# 20. Validação antes da gravação

Antes de alterar o SQLite, validar:

- resposta HTTP;
- JSON;
- `success`;
- `syncUntil`;
- `count`;
- `items`;
- estrutura dos itens;
- campos necessários;
- tipos mínimos esperados.

Uma resposta HTTP 200 isoladamente não significa que a sincronização foi válida.

---

# 21. Transação obrigatória

A atualização do SQLite deve ocorrer dentro de uma transação.

Fluxo:

    Receber resposta
          │
          ▼
    Validar resposta
          │
          ▼
    BEGIN TRANSACTION
          │
          ▼
    UPSERT registros
          │
          ▼
    Atualizar sync_control
          │
          ▼
    COMMIT

Se qualquer etapa crítica falhar:

    ROLLBACK

A base anterior deve permanecer utilizável.

---

# 22. Regra crítica do syncUntil

O valor:

    syncUntil

NUNCA deve ser salvo antes que todos os registros retornados tenham sido gravados com sucesso.

ERRADO:

    receber syncUntil
        ↓
    salvar last_sync
        ↓
    começar UPSERT
        ↓
    falhar

Esse comportamento poderia perder registros na próxima sincronização.

---

# 23. Comportamento correto do syncUntil

Fluxo obrigatório:

    Power Automate
          │
          ▼
      resposta
          │
          ▼
    syncUntil = X
          │
          ▼
    validar items
          │
          ▼
    iniciar transação
          │
          ▼
    gravar todos os items
          │
          ▼
    tudo OK?
       │       │
      NÃO     SIM
       │       │
       ▼       ▼
    ROLLBACK  salvar last_sync = X
                 │
                 ▼
               COMMIT

Somente depois do COMMIT considerar a sincronização concluída.

---

# 24. UPSERT

A sincronização deve suportar:

- registros novos;
- registros existentes alterados;
- repetição segura da mesma janela de sincronização.

Utilizar UPSERT ou estratégia equivalente.

Não criar registros duplicados quando o mesmo item for recebido novamente.

---

# 25. Chave do UPSERT

Antes de implementar, analisar qual chave deve ser utilizada como referência principal.

Preferencialmente utilizar o identificador estável originado no SharePoint:

    sharepointId

O EPC também deve possuir proteção apropriada contra duplicidade incompatível com a regra de negócio.

Não assumir silenciosamente que EPC e SharePoint ID possuem a mesma semântica.

---

# 26. Sincronização incremental

Depois da carga inicial:

    last_sync = último syncUntil confirmado

A próxima chamada deverá utilizar:

    {
        "doca": "D01",
        "modifiedSince": "<last_sync>"
    }

Exemplo:

    last_sync =
    2026-10-05T10:15:00Z

Requisição:

    {
        "doca": "D01",
        "modifiedSince": "2026-10-05T10:15:00Z"
    }

---

# 27. Resposta incremental vazia

Uma resposta:

    {
        "success": true,
        "syncUntil": "2026-10-05T10:30:00Z",
        "count": 0,
        "items": []
    }

é uma resposta válida.

`count = 0` NÃO significa erro.

Significa apenas que não existem registros novos ou alterados naquela janela.

Nesse caso, após validar a resposta, o cursor pode avançar normalmente para o novo `syncUntil`.

---

# 28. Janela de sincronização

O software deve utilizar `syncUntil` retornado pelo servidor como cursor.

Não gerar arbitrariamente o próximo cursor baseado apenas no relógio local do Windows.

O Codex deve verificar se o Power Automate garante uma janela consistente entre:

    modifiedSince

e:

    syncUntil

Caso o fluxo Power Automate atualmente não utilize `syncUntil` como limite superior da consulta, reportar isso como dependência externa da sincronização.

Não alterar o Power Automate automaticamente sem solicitação.

---

# 29. Consulta operacional por EPC

Depois da migração, quando o Zebra FX9600 identificar uma etiqueta:

    Zebra
      │
      ▼
     EPC
      │
      ▼
    Normalização existente
      │
      ▼
    Deduplicação existente
      │
      ▼
    Consulta SQLite
      │
      ▼
    Registro encontrado?
      │
      ├── SIM → processamento atual
      │
      └── NÃO → ignorar conforme regra atual

Nenhuma chamada HTTP deve acontecer nesse caminho.

---

# 30. Consulta local obrigatória

O processamento operacional do EPC deve utilizar exclusivamente o repositório local.

Conceitualmente:

    find_by_epc(epc, doca)

A UI não deve executar SQL diretamente.

O callback do RFID também não deve conter SQL espalhado.

Criar/reutilizar uma camada responsável pelo acesso à base local.

---

# 31. Resultado encontrado

Quando o EPC for encontrado localmente, preservar o comportamento atual da aplicação.

Utilizar os dados:

    status
    cliente
    notaFiscal
    volume
    pedido
    doca
    epc

para alimentar o processamento existente.

Preservar a tabela atual:

    Status
    Cliente
    Nota fiscal
    Volume
    Pedido
    Doca

Não adicionar novamente uma coluna EPC visível se ela não existir atualmente.

O EPC continua sendo mantido internamente.

---

# 32. EPC não encontrado

Quando um EPC não existir na base local:

- não chamar Power Automate;
- não chamar SharePoint;
- não tentar endpoint antigo;
- não realizar fallback remoto;
- não exibir linha de erro;
- não incrementar contador de encontrados.

Preservar a regra atual de ignorar EPCs não encontrados.

Pode registrar informação apropriada em log de diagnóstico.

---

# 33. Proibido fallback para endpoint antigo

Não implementar:

    SQLite não encontrou
          │
          ▼
    consultar Power Automate por EPC

Esse fallback recriaria a dependência que estamos removendo.

Depois do cutover:

    SQLite não encontrou
          │
          ▼
    EPC não encontrado

A atualização da base deve acontecer pelo mecanismo de sincronização.

---

# 34. Endpoint antigo por EPC

O endpoint antigo:

    {
        "epc": "..."
    }

não deve mais ser utilizado pelo fluxo operacional final.

Entretanto, a remoção deve seguir uma ordem segura.

Não quebrar o sistema no meio da implementação.

---

# 35. Ordem obrigatória da migração

Executar a alteração nesta ordem:

    1. criar camada SQLite

    2. criar schema

    3. criar controle de sincronização

    4. implementar carga inicial

    5. implementar sincronização incremental

    6. validar gravação local

    7. implementar consulta local por EPC

    8. testar consulta local

    9. integrar consulta local ao processamento RFID

    10. validar fluxo RFID completo

    11. remover/desativar o lookup remoto por EPC do caminho operacional

    12. revisar código morto/configurações obsoletas

Não remover primeiro o mecanismo atual e depois tentar construir o SQLite.

---

# 36. Resultado arquitetural após o cutover

Depois da implementação:

    Zebra FX9600
          │
          ▼
         EPC
          │
          ▼
    SQLite local
          │
          ▼
    Resultado

e paralelamente:

    SharePoint
         │
         ▼
    Power Automate
         │
         ▼
    Doca + modifiedSince
         │
         ▼
    Sincronização
         │
         ▼
    SQLite local

---

# 37. Correção do significado de "Base de dados" no RF013

O RF013 deve ser ajustado.

Anteriormente, o status `Base de dados` estava diretamente associado à resposta do endpoint remoto.

Com a nova arquitetura, isso precisa ser separado.

Existem agora dois estados diferentes:

    Base de dados
        =
    SQLite local operacional

e:

    Sincronização
        =
    serviço remoto Power Automate/SharePoint disponível

Não misturar esses conceitos.

---

# 38. Status Base de dados

O indicador:

    Base de dados

deve representar a disponibilidade da base LOCAL utilizada pela operação RFID.

Exemplo:

    Base de dados   ● OK

significa:

- SQLite pode ser aberto;
- schema está válido;
- Doca atual possui uma inicialização válida;
- consultas podem ser realizadas;
- a base local está operacional.

---

# 39. Novo status Sincronização

Adicionar um indicador separado:

    Sincronização

Ele representa a disponibilidade do novo endpoint Power Automate/SharePoint.

Exemplo:

    Internet        ● OK
    RFID            ● OK
    Comandos        ● OK
    Base de dados   ● OK
    Sincronização   ● OK

Manter o mesmo padrão visual dos status existentes.

---

# 40. Teste do endpoint remoto

Para determinar:

    Sincronização = OK

realizar uma requisição válida utilizando exclusivamente o novo contrato:

    {
        "doca": "<DOCA_CONFIGURADA>",
        "modifiedSince": "<TIMESTAMP_APROPRIADO>"
    }

Nunca enviar EPC.

---

# 41. Health check não deve baixar a base completa

Não utilizar periodicamente:

    {
        "doca": "D01",
        "modifiedSince": ""
    }

apenas para testar disponibilidade.

Isso representa uma carga inicial e pode retornar toda a base da Doca.

O health check deve ser leve.

---

# 42. Estratégia de verificação remota

Sempre que uma sincronização real for executada, o próprio resultado da sincronização deve atualizar o status remoto.

Exemplo:

    sincronização válida
        ↓
    Sincronização = OK

    timeout
        ↓
    Sincronização = NOK

    erro HTTP
        ↓
    Sincronização = NOK

    resposta inválida
        ↓
    Sincronização = NOK

Se o monitor de status precisar realizar uma verificação independente entre sincronizações, utilizar uma chamada leve com o mesmo contrato `doca + modifiedSince`, sem EPC e sem avançar o cursor real de sincronização.

---

# 43. Health check não altera last_sync

Uma chamada utilizada somente para verificar disponibilidade NÃO pode alterar:

    last_sync

Também não deve:

- executar UPSERT;
- modificar registros;
- marcar carga inicial como concluída;
- alterar `last_full_sync`.

Health check e sincronização são operações diferentes, embora utilizem o mesmo endpoint.

---

# 44. Resposta válida do health check

Uma resposta como:

    {
        "success": true,
        "syncUntil": "...",
        "count": 0,
        "items": []
    }

deve ser suficiente para confirmar que o serviço remoto respondeu corretamente.

`count = 0` é válido.

---

# 45. Sincronização remota indisponível

Se:

    Sincronização = NOK

mas:

    Base de dados local = OK

a aplicação NÃO deve apagar ou invalidar a base local.

A última base sincronizada permanece disponível.

Exemplo:

    Internet        ● OK
    RFID            ● OK
    Comandos        ● OK
    Base de dados   ● OK
    Sincronização   ● NOK

A consulta local de EPC continua tecnicamente disponível.

---

# 46. Correção da regra de system_ready do RF013

Esta regra substitui a parte do RF013 que fazia a disponibilidade operacional depender diretamente da resposta do endpoint remoto.

O estado operacional deve considerar principalmente a base utilizada pelo processo RFID:

    local_database_ready

e NÃO:

    remote_sync_available

Portanto, a falha temporária da sincronização não deve invalidar automaticamente uma base local já válida.

---

# 47. Internet

Preservar neste RF a regra existente do RF012 referente ao status de Internet.

Não alterar a política de Internet sem requisito específico.

A mudança deste RF refere-se à separação entre:

    base local

e:

    sincronização remota.

---

# 48. Sistema operacionalmente apto

Preservando as regras existentes, o sistema deve considerar:

    Internet
    RFID
    Comandos/Waveshare
    Base local

para determinar disponibilidade operacional.

Conceitualmente:

    system_ready =
        internet_ok
        AND rfid_ok
        AND waveshare_ok
        AND local_database_ready

O status:

    remote_sync_available

deve ser monitorado separadamente.

---

# 49. Base local inexistente

Se a aplicação nunca realizou uma carga inicial válida para a Doca configurada:

    Base de dados = NOK

Nesse cenário, não existe base operacional para consultar EPC.

Portanto:

    Sistema não apto

e, se Waveshare estiver disponível:

    CH1 OFF
    CH2 OFF
    CH3 ON

---

# 50. Falha na primeira sincronização

Exemplo:

    Doca = D01

    SQLite criado

    nenhuma sincronização válida realizada

    Power Automate indisponível

Resultado:

    Base de dados   NOK
    Sincronização   NOK

O sistema não deve iniciar leitura RFID automática porque não possui uma base operacional válida.

---

# 51. Falha incremental com base local válida

Exemplo:

    Doca = D01

    última sincronização válida:
    08:45

    nova sincronização às 09:00:
    FALHOU

Resultado:

    Base de dados   OK
    Sincronização   NOK

A base local anterior deve permanecer intacta.

Não apagar dados.

Não avançar `last_sync`.

---

# 52. Falha durante UPSERT

Se a resposta remota for válida, mas ocorrer erro durante a gravação:

    ROLLBACK

Resultado:

- manter base anterior;
- manter `last_sync` anterior;
- não aceitar `syncUntil`;
- registrar erro;
- marcar a tentativa de sincronização como falha.

Não deixar a base parcialmente atualizada.

---

# 53. Consulta durante sincronização

A leitura RFID pode ocorrer enquanto uma atualização da base estiver sendo processada.

A aplicação deve evitar expor dados parcialmente atualizados.

As alterações da sincronização devem se tornar visíveis somente após COMMIT.

A consulta RFID deve enxergar:

- estado anterior completo;

ou:

- estado novo completo.

Nunca um estado intermediário parcialmente atualizado.

---

# 54. Concorrência

Analisar a arquitetura de threads existente.

Evitar:

- múltiplos writers simultâneos;
- conexões SQLite compartilhadas de forma insegura entre threads;
- bloqueios longos;
- SQL direto na thread da UI;
- SQL pesado dentro do callback LLRP.

Centralizar o acesso ao SQLite em serviço/repositório apropriado.

---

# 55. Callback RFID

Preservar a regra arquitetural do projeto:

O callback do reader não deve executar operações demoradas.

O fluxo deve continuar utilizando a arquitetura/fila existente para processar as leituras.

A consulta SQLite deve ocorrer na camada apropriada.

Não mover regras de negócio para dentro do driver LLRP.

---

# 56. Mudança de Doca

Quando o usuário alterar:

    D01

para:

    D05

a aplicação deve atualizar imediatamente a Doca configurada.

A partir desse momento:

    D05

é a Doca operacional.

---

# 57. Controle por Doca

Ao mudar para D05:

    procurar sync_control de D05

Se D05 nunca foi sincronizada:

    modifiedSince = ""

Se D05 já possui histórico:

    utilizar cursor de D05

Nunca utilizar:

    last_sync de D01

para sincronizar D05.

---

# 58. Segurança ao mudar de Doca

Após mudança de Doca, não continuar consultando silenciosamente a base da Doca anterior.

A consulta deve obrigatoriamente utilizar:

    epc
    +
    doca configurada

Se a nova Doca ainda não possuir base válida, o sistema deve ficar não apto até que a condição necessária seja satisfeita.

---

# 59. Mudança de Doca e sincronização

Ao alterar a Doca, iniciar o processo apropriado de validação/sincronização para a nova Doca.

Não assumir que a base antiga representa a nova estação.

Se existir base previamente sincronizada para a nova Doca, verificar seu estado e executar a estratégia de atualização prevista antes de utilizar dados incorretos.

---

# 60. Frequência de sincronização

Até o momento não foi definida uma frequência oficial para sincronização automática.

Portanto:

- não espalhar intervalos fixos pelo código;
- não inventar polling agressivo;
- centralizar a frequência em configuração/constante apropriada;
- analisar o mecanismo de timers existente;
- informar no relatório prévio qual frequência está sendo proposta.

A carga inicial e a sincronização necessária na inicialização devem ser implementadas.

Caso seja necessária uma cadência recorrente adicional, o Codex deve apresentar a proposta antes de fixar um intervalo de negócio arbitrário.

---

# 61. Inicialização da aplicação

Fluxo conceitual:

    Iniciar software
          │
          ▼
    Carregar configurações
          │
          ▼
    Obter Doca
          │
          ▼
    Inicializar SQLite
          │
          ▼
    Validar schema
          │
          ▼
    Verificar sync_control
          │
          ├── nunca sincronizada
          │       ↓
          │   carga inicial
          │
          └── já sincronizada
                  ↓
             base local disponível
                  ↓
             tentar atualização

A UI não deve congelar durante esse processo.

---

# 62. Base local durante atualização no startup

Se já existir uma base válida para a Doca, uma tentativa de atualização remota não deve destruir essa disponibilidade.

Exemplo:

    SQLite D01 válido
          │
          ▼
    aplicação inicia
          │
          ▼
    sincronização falha
          │
          ▼
    manter SQLite anterior

A falha remota deve ser sinalizada separadamente.

---

# 63. Reconciliação completa

Existe uma limitação importante no modelo incremental:

    Doca + Modified

Se um registro for fisicamente excluído do SharePoint, ele não aparecerá naturalmente em uma consulta incremental posterior.

Existe problema semelhante se um registro for movido de:

    D01

para:

    D05

pois uma estação que consulta somente D01 pode não receber o registro informando que ele deixou de pertencer à D01.

O Codex NÃO deve ignorar essa condição.

---

# 64. Exclusões físicas

O fluxo incremental não deve presumir que consegue detectar exclusões físicas.

Por enquanto, preservar o uso do campo:

    status

para representar registros que deixaram de ser operacionalmente válidos, sempre que esse for o processo de negócio adotado.

Exemplo:

    Ativo
      ↓
    Inativo

Essa alteração será recebida pelo incremental.

---

# 65. Alteração de Doca de um registro

Não assumir silenciosamente que uma alteração:

    D01 → D05

será detectada corretamente pela estação D01 usando somente:

    Doca = D01
    AND
    Modified >= last_sync

O Codex deve documentar essa limitação.

---

# 66. Capacidade de reconciliação

A camada de sincronização deve ser estruturada para permitir uma sincronização completa/reconciliação futura por Doca.

Conceitualmente:

    full_sync(D01)

deve permitir comparar:

    registros remotos atuais de D01

com:

    registros locais de D01

e identificar registros locais que não existem mais no conjunto remoto.

Não criar automaticamente uma política destrutiva sem definição do negócio.

---

# 67. Não apagar registros automaticamente por ausência no incremental

Uma resposta incremental contendo:

    count = 0

NUNCA significa:

    apagar registros locais

Significa somente:

    nenhum registro foi modificado na janela.

---

# 68. Política de exclusão/reconciliação

Como a regra definitiva para:

- exclusão física no SharePoint;
- transferência de registro entre Docas;
- frequência de full reconciliation;

ainda não foi definida, não inventar comportamento destrutivo.

Implementar a arquitetura de forma que uma reconciliação possa ser adicionada com segurança.

Registrar essa limitação no relatório final.

---

# 69. Integridade da base local

O status:

    Base de dados = OK

não deve depender da quantidade de registros.

Uma Doca pode legitimamente retornar:

    count = 0

e ainda possuir uma sincronização válida.

A validade deve depender de:

- SQLite acessível;
- schema válido;
- Doca inicializada;
- sincronização inicial concluída corretamente.

---

# 70. Status da última sincronização

Manter internamente informação suficiente para identificar:

    última sincronização bem-sucedida

Exemplo:

    last_success_at

Esse valor deve ser UTC na persistência.

A UI pode converter para horário local quando necessário.

Não utilizar string de horário local como cursor do Power Automate.

---

# 71. UTC

Utilizar UTC para:

    modifiedSince
    syncUntil
    sharepoint_modified
    synced_at
    last_sync
    last_success_at

Não realizar comparação incremental usando timestamps locais sem timezone.

---

# 72. Normalização do EPC

Preservar a normalização atual do EPC.

Não reintroduzir conversão ASCII/Tag removida anteriormente.

O EPC deve permanecer no formato interno já utilizado pelo software.

O valor armazenado no SQLite deve ser compatível com o EPC produzido pela leitura RFID.

---

# 73. Não alterar o driver RFID

Não colocar lógica SQLite dentro do driver do Zebra.

A responsabilidade deve continuar separada:

    Reader
      ↓
    leitura EPC
      ↓
    serviço de processamento
      ↓
    repositório local
      ↓
    SQLite

O driver LLRP continua responsável somente pela comunicação RFID.

---

# 74. Não alterar deduplicação

Preservar a lógica atual de deduplicação.

A mudança de SharePoint para SQLite não deve provocar:

- duplicação de EPCs na tabela;
- incremento repetido do contador;
- processamento repetido de uma mesma leitura dentro da janela existente.

---

# 75. Contador de EPCs encontrados

Preservar a regra atual:

    EPC encontrado localmente
          ↓
    adiciona resultado
          ↓
    incrementa contador

EPC repetido:

    não duplica

EPC não encontrado:

    não incrementa

---

# 76. Status Inativo

Caso a regra de negócio confirme que:

    status = Inativo

significa etiqueta não válida para operação, o registro pode permanecer no SQLite para consistência/histórico, mas não deve ser retornado como válido pela consulta operacional.

Não excluir fisicamente apenas por estar inativo.

---

# 77. Performance

O caminho crítico de leitura deve ser completamente local.

Esperado:

    Zebra
      ↓
    EPC
      ↓
    SQLite indexado
      ↓
    resultado

Não deve existir:

- HTTP;
- Power Automate;
- SharePoint;
- espera de rede;

no caminho de consulta individual da etiqueta.

---

# 78. UI responsiva

Nenhuma destas operações deve congelar a interface:

- abertura do SQLite;
- carga inicial;
- sincronização incremental;
- health check;
- UPSERT;
- timeout HTTP;
- consulta RFID.

Utilizar os mecanismos de background já existentes no projeto.

---

# 79. Timeout remoto

Todas as chamadas ao novo Power Automate devem possuir timeout.

Reutilizar o padrão HTTP já existente no projeto.

Não permitir que falha de rede bloqueie indefinidamente a aplicação.

---

# 80. Segurança

A URL do Power Automate pode conter informações sensíveis.

Não:

- imprimir URL completa;
- registrar token;
- exibir assinatura na UI;
- colocar credenciais em mensagens de erro;
- hardcodar segredo no código.

Reutilizar o mecanismo de configuração/segredos existente.

---

# 81. Arquitetura sugerida

Adaptar aos nomes reais do projeto.

Conceitualmente:

    RFID Reader Service
            │
            ▼
    EPC Processing Service
            │
            ▼
    Local Tag Repository
            │
            ▼
          SQLite

Paralelamente:

    Sync Service
        │
        ├── Config/Doca
        │
        ├── HTTP Client
        │
        ├── Power Automate
        │
        └── Local Tag Repository
                    │
                    ▼
                  SQLite

Não duplicar acesso ao SQLite em múltiplas camadas.

---

# 82. Não criar SQL na UI

A tela Start não deve executar:

    SELECT
    INSERT
    UPDATE

diretamente.

A tela de Configurações também não deve manipular SQL diretamente.

A UI deve utilizar serviços/repositórios.

---

# 83. Não criar HTTP na UI

Da mesma forma, a UI não deve montar diretamente o payload do Power Automate.

Centralizar no serviço de sincronização.

Exemplo conceitual:

    sync_service.sync(doca)

e não:

    botão/UI
       ↓
    requests.post(...)

---

# 84. Análise obrigatória antes da implementação

Antes de alterar qualquer arquivo, o Codex deve analisar integralmente:

1. `AGENTS.md`;
2. documentos de requisitos relacionados;
3. RF012;
4. RF013;
5. tela Start;
6. tela Configurações;
7. configuração da Doca;
8. serviço de status;
9. status Internet;
10. status RFID;
11. status Comandos/Waveshare;
12. lógica CH1/CH2/CH3;
13. serviço atual de consulta por EPC;
14. local onde o payload `{epc}` é criado;
15. endpoint antigo;
16. novo endpoint de sincronização;
17. cliente HTTP;
18. processamento de EPC;
19. deduplicação;
20. tabela de resultados;
21. contador;
22. modelos existentes;
23. workers/threads;
24. mecanismo de persistência;
25. diretórios de dados;
26. logging;
27. cleanup da aplicação;
28. testes existentes.

Não implementar antes dessa análise.

---

# 85. Diagnóstico obrigatório antes da alteração

Antes de modificar código, apresentar um relatório curto contendo:

- fluxo atual completo do EPC;
- arquivos envolvidos;
- onde ocorre a chamada remota atual;
- onde o EPC é enviado ao Power Automate;
- onde será inserido o repositório SQLite;
- onde será inserido o serviço de sincronização;
- como a Doca será obtida;
- caminho proposto do arquivo SQLite;
- schema proposto;
- estratégia de UPSERT;
- estratégia de transação;
- estratégia de cursor;
- estratégia de concorrência;
- impacto nos status;
- impacto em `system_ready`;
- impacto em CH1/CH2/CH3;
- como será realizado o cutover;
- código/configuração que ficará obsoleto.

Somente depois iniciar as alterações.

---

# 86. Alterações mínimas

Apesar de ser uma mudança arquitetural importante, evitar refatorações não relacionadas.

Não alterar:

- design geral da aplicação;
- protocolo LLRP;
- comunicação Modbus;
- telas não relacionadas;
- lógica de sensores sem necessidade;
- nomes/estruturas não relacionadas apenas por preferência estética.

---

# 87. Fluxo RF012 preservado

Preservar:

    DI1 ativo → desativado
          ↓
    iniciar ciclo
          ↓
    iniciar RFID
          ↓
    CH2 ON
          ↓
    timer 60 segundos

e:

    DI2 ativo → desativado
          ↓
    parar RFID
          ↓
    finalizar ciclo

A alteração deste requisito está no processamento do EPC e na disponibilidade da base.

---

# 88. Falha da base local durante operação

Se o SQLite ficar indisponível/corrompido de forma que não seja possível realizar consultas confiáveis:

    Base de dados = NOK

O sistema não deve iniciar novos ciclos.

Se Waveshare estiver disponível:

    CH1 OFF
    CH2 OFF
    CH3 ON

Registrar erro técnico.

---

# 89. Falha da sincronização durante leitura

Se:

    Base local = OK

e ocorrer:

    Sincronização = NOK

durante uma leitura RFID:

não interromper a leitura apenas por esse motivo.

A consulta operacional está utilizando a base local já válida.

Registrar a indisponibilidade remota e preservar a base local.

---

# 90. Sincronização não deve controlar CH2

CH2 continua significando exclusivamente:

    leitura RFID em andamento

Não utilizar CH2 para indicar:

- sincronização;
- download;
- atualização SQLite;
- health check.

---

# 91. CH3

CH3 continua representando indisponibilidade operacional.

Uma falha de sincronização remota isolada, com base local válida, não deve obrigatoriamente acionar CH3.

Uma falha da base LOCAL necessária para consultar EPC deve tornar o sistema não apto.

---

# 92. CH1

CH1 continua representando sistema apto para operação.

A disponibilidade operacional deve utilizar a base local.

Não utilizar diretamente o estado do Power Automate como substituto do estado da base local.

---

# 93. Testes unitários — SQLite

Criar testes para:

- criação do banco;
- criação do schema;
- abertura do banco;
- inserção;
- UPSERT;
- atualização;
- consulta por EPC;
- consulta por EPC + Doca;
- registro inexistente;
- status;
- controle de sincronização;
- cursor por Doca;
- rollback.

Não utilizar rede nos testes unitários.

---

# 94. Testes — carga inicial

Simular:

    Doca = D01
    sem sync_control

Resposta:

    success = true
    count > 0
    items = [...]

Esperado:

- registros gravados;
- transação concluída;
- `initialized = true`;
- `last_sync = syncUntil`;
- base local OK.

---

# 95. Teste — carga inicial vazia

Resposta:

    success = true
    count = 0
    items = []

Esperado:

- sincronização considerada válida;
- Doca considerada inicializada;
- `last_sync` atualizado;
- não tratar como erro apenas por não existirem registros.

---

# 96. Teste — incremental

Estado:

    last_sync = T1

Requisição:

    {
        "doca": "D01",
        "modifiedSince": "T1"
    }

Resposta:

    syncUntil = T2

Esperado:

- novos registros inseridos;
- existentes atualizados;
- `last_sync = T2` somente após COMMIT.

---

# 97. Teste — falha no meio do UPSERT

Simular erro durante gravação.

Esperado:

    ROLLBACK

Confirmar:

- nenhum estado parcial;
- `last_sync` continua T1;
- dados anteriores continuam válidos.

---

# 98. Teste — Docas independentes

Estado:

    D01 → last_sync = T1
    D05 → last_sync = T5

Configurar D05.

Esperado:

    modifiedSince = T5

Nunca:

    modifiedSince = T1

---

# 99. Teste — EPC encontrado

SQLite:

    Doca = D01
    EPC = ABC123

Reader:

    ABC123

Esperado:

- consulta local;
- nenhuma requisição HTTP;
- dados apresentados;
- contador atualizado.

---

# 100. Teste — EPC não encontrado

Reader:

    XYZ999

SQLite:

    inexistente

Esperado:

- nenhuma chamada Power Automate;
- nenhuma chamada SharePoint;
- nenhuma linha adicionada;
- nenhum incremento;
- nenhum fallback remoto.

---

# 101. Teste — EPC existente em outra Doca

SQLite:

    EPC = ABC123
    Doca = D05

Configuração:

    Doca = D01

Esperado:

    não considerar o registro como válido para D01.

---

# 102. Teste — endpoint remoto indisponível com base local válida

Estado:

    Base local = OK
    Power Automate = NOK

Esperado:

    Base de dados = OK
    Sincronização = NOK

A consulta local por EPC deve continuar funcionando.

---

# 103. Teste — primeira sincronização indisponível

Estado:

    Doca = D01
    nenhuma base inicial
    Power Automate = NOK

Esperado:

    Base de dados = NOK
    Sincronização = NOK
    sistema não apto

Não iniciar operação RFID automática.

---

# 104. Teste — health check

Enviar somente:

    {
        "doca": "D01",
        "modifiedSince": "..."
    }

Confirmar:

- nenhum EPC no payload;
- resposta válida detectada;
- `last_sync` não alterado;
- SQLite não alterado;
- `syncUntil` do health check não substitui cursor operacional.

---

# 105. Teste — nenhuma chamada HTTP por etiqueta

Criar teste específico garantindo que o processamento:

    on_epc_read(...)

ou equivalente:

não execute cliente HTTP.

Essa é uma regra arquitetural crítica.

---

# 106. Teste de regressão RFID

Validar:

- conexão FX9600;
- início do inventário;
- parada;
- recebimento de EPC;
- deduplicação;
- timer de 60 segundos;
- DI1;
- DI2;
- CH1;
- CH2;
- CH3;
- tabela;
- contador.

---

# 107. Testes de qualidade Python

Executar os comandos configurados pelo projeto.

Quando aplicável:

    ruff check .
    ruff format --check .
    mypy src
    pytest

Não declarar que passaram sem executá-los.

Testes que dependem de hardware devem permanecer separados/marcados adequadamente.

---

# 108. Testes em Windows

A validação final deve ser realizada nativamente no Windows.

Não utilizar WSL como ambiente oficial.

Validar:

- criação do arquivo SQLite;
- permissões;
- persistência;
- fechamento;
- reinicialização;
- consulta;
- sincronização;
- threads;
- encerramento da aplicação.

---

# 109. Teste manual — primeira execução

1. iniciar aplicação;
2. configurar Doca D01;
3. confirmar ausência de base inicial;
4. executar carga inicial;
5. confirmar retorno do Power Automate;
6. confirmar registros no SQLite;
7. confirmar `last_sync`;
8. confirmar Base de dados OK;
9. ler EPC real;
10. confirmar consulta local;
11. confirmar que nenhuma consulta individual foi enviada ao Power Automate.

---

# 110. Teste manual — atualização

1. obter `last_sync`;
2. alterar um registro D01 no SharePoint;
3. criar outro registro D01;
4. executar incremental;
5. confirmar envio de D01 + `last_sync`;
6. confirmar retorno dos registros;
7. confirmar UPSERT;
8. confirmar novo `last_sync`;
9. ler EPC atualizado;
10. confirmar novos dados localmente.

---

# 111. Teste manual — indisponibilidade remota

1. possuir base D01 válida;
2. tornar endpoint indisponível;
3. confirmar Sincronização NOK;
4. confirmar Base de dados local OK;
5. ler EPC;
6. confirmar consulta SQLite funcionando;
7. confirmar ausência de fallback remoto.

---

# 112. Teste manual — mudança de Doca

1. Doca atual D01;
2. confirmar base D01;
3. alterar configuração para D05;
4. confirmar uso do controle D05;
5. confirmar que D01 não é consultada como se fosse D05;
6. realizar carga/sincronização necessária de D05;
7. consultar EPC de D05;
8. confirmar resultado.

---

# 113. Critérios de aceite — arquitetura

O requisito será aprovado quando:

- [ ] Power Automate não receber EPC durante leitura RFID;
- [ ] endpoint antigo por EPC não fizer parte do caminho operacional final;
- [ ] novo endpoint receber somente Doca + modifiedSince;
- [ ] Doca vier da configuração;
- [ ] SQLite estiver implementado;
- [ ] SharePoint permanecer fonte oficial;
- [ ] SQLite funcionar como base operacional local;
- [ ] consulta RFID ocorrer exclusivamente no SQLite;
- [ ] nenhuma chamada HTTP ocorrer por EPC lido;
- [ ] não existir fallback remoto por EPC.

---

# 114. Critérios de aceite — sincronização

- [ ] existir carga inicial;
- [ ] `modifiedSince = ""` ser utilizado somente quando apropriado;
- [ ] existir sincronização incremental;
- [ ] `last_sync` ser separado por Doca;
- [ ] `syncUntil` ser utilizado como cursor;
- [ ] `syncUntil` só ser salvo após COMMIT;
- [ ] UPSERT evitar duplicidade;
- [ ] falha provocar rollback;
- [ ] base anterior permanecer válida após falha;
- [ ] `count = 0` ser tratado como resposta válida;
- [ ] status Ativo/Inativo ser sincronizado;
- [ ] timestamps persistidos para sincronização utilizarem UTC.

---

# 115. Critérios de aceite — status

- [ ] Base de dados representar SQLite local;
- [ ] Sincronização representar endpoint remoto;
- [ ] Base local válida continuar disponível quando sincronização remota falhar;
- [ ] primeira sincronização inexistente resultar em Base de dados NOK;
- [ ] falha remota não apagar base local;
- [ ] health check não alterar cursor;
- [ ] health check não baixar desnecessariamente toda a Doca;
- [ ] health check nunca enviar EPC.

---

# 116. Critérios de aceite — RFID

- [ ] EPC continuar sendo identificador da etiqueta;
- [ ] normalização atual ser preservada;
- [ ] deduplicação ser preservada;
- [ ] EPC encontrado gerar resultado;
- [ ] EPC não encontrado ser ignorado;
- [ ] EPC não encontrado não chamar Power Automate;
- [ ] contador permanecer correto;
- [ ] tabela permanecer correta;
- [ ] Start/Stop permanecer funcionando;
- [ ] timer de 60 segundos permanecer funcionando;
- [ ] RF012 permanecer funcional.

---

# 117. Fora do escopo

Não implementar sem requisito específico:

- edição manual dos dados SQLite;
- cadastro manual de etiquetas;
- alteração de dados do SharePoint pelo SQLite;
- envio de alterações locais para SharePoint;
- escrita RFID;
- alteração do EPC da etiqueta;
- dashboard complexo de banco;
- exportação SQLite;
- alteração do Power Automate além do contrato existente;
- política destrutiva para exclusões físicas;
- exclusão automática de registros ausentes;
- política definitiva de full reconciliation sem regra de negócio;
- alteração da lógica dos sensores;
- alteração de CH4–CH8;
- alteração do protocolo LLRP;
- alteração persistente no FX9600.

---

# 118. Preservar obrigatoriamente

Preservar:

- Zebra FX9600;
- LLRP;
- leitura EPC;
- EPC hexadecimal interno;
- deduplicação;
- RF012;
- DI1;
- DI2;
- timer de 60 segundos;
- CH1 verde;
- CH2 amarelo;
- CH3 vermelho;
- CH4–CH8;
- Waveshare;
- tela de diagnóstico Waveshare;
- configuração RFID;
- configuração Waveshare;
- configuração da Doca;
- tabela de resultados;
- contador;
- logs;
- comportamento de EPCs não encontrados;
- execução nativa Windows.

---

# 119. Código legado do endpoint por EPC

Após o novo fluxo estar implementado e testado:

- localizar código exclusivo do lookup remoto por EPC;
- remover/desativar somente o que ficou realmente obsoleto;
- não remover cliente HTTP caso continue sendo utilizado pela sincronização;
- não remover configuração compartilhada por outras funcionalidades;
- não deixar caminhos mortos que possam voltar a enviar EPC por engano.

Revisar cuidadosamente o diff.

---

# 120. Regra definitiva do projeto

A partir deste requisito:

    ┌──────────────────────────────────────────┐
    │              SINCRONIZAÇÃO               │
    │                                          │
    │ Configuração                             │
    │      │                                   │
    │      ▼                                   │
    │     Doca                                 │
    │      +                                   │
    │ modifiedSince                            │
    │      │                                   │
    │      ▼                                   │
    │ Power Automate                           │
    │      │                                   │
    │      ▼                                   │
    │ SharePoint                               │
    │      │                                   │
    │      ▼                                   │
    │ SQLite local                             │
    └──────────────────────────────────────────┘


    ┌──────────────────────────────────────────┐
    │             OPERAÇÃO RFID                │
    │                                          │
    │ Zebra FX9600                             │
    │      │                                   │
    │      ▼                                   │
    │     EPC                                  │
    │      │                                   │
    │      ▼                                   │
    │ SQLite local                             │
    │      │                                   │
    │      ▼                                   │
    │ Cliente / NF / Volume / Pedido / Doca    │
    └──────────────────────────────────────────┘

Não misturar os dois fluxos.

---

# 121. Regra simples para o Codex

Sempre que estiver trabalhando com:

    Doca + modifiedSince

está trabalhando com:

    SINCRONIZAÇÃO

Sempre que estiver trabalhando com:

    EPC

está trabalhando com:

    CONSULTA LOCAL SQLITE

Nunca:

    EPC → Power Automate

na arquitetura final.

---

# 122. Definição de pronto

Antes de declarar conclusão, o Codex deve:

1. revisar o diff completo;
2. confirmar que não existem alterações fora do escopo;
3. executar testes unitários;
4. executar Ruff;
5. executar Mypy, quando configurado;
6. executar Pytest;
7. testar criação do SQLite;
8. testar carga inicial;
9. testar incremental;
10. testar rollback;
11. testar cursor por Doca;
12. testar consulta por EPC;
13. testar EPC inexistente;
14. testar ausência de fallback remoto;
15. testar status Base de dados;
16. testar status Sincronização;
17. testar falha remota com base local válida;
18. testar primeira sincronização indisponível;
19. testar mudança de Doca;
20. testar regressão do RF012;
21. testar Zebra quando hardware estiver disponível;
22. testar Waveshare quando hardware estiver disponível;
23. confirmar que o endpoint novo nunca recebe EPC;
24. confirmar que o caminho operacional RFID não depende mais do Power Automate;
25. confirmar que nenhuma credencial foi exposta.

---

# 123. Relatório final obrigatório

Ao finalizar, apresentar:

- causa da incompatibilidade anterior;
- arquitetura anterior;
- arquitetura nova;
- arquivos alterados;
- arquivos criados;
- localização do SQLite;
- schema implementado;
- índices criados;
- estratégia de UPSERT;
- estratégia de transação;
- estrutura do `sync_control`;
- funcionamento da carga inicial;
- funcionamento do incremental;
- funcionamento do `syncUntil`;
- tratamento de rollback;
- comportamento por Doca;
- comportamento ao mudar Doca;
- funcionamento da consulta local por EPC;
- comportamento de EPC não encontrado;
- confirmação de ausência de fallback remoto;
- funcionamento do status Base de dados;
- funcionamento do status Sincronização;
- comportamento quando Power Automate estiver indisponível;
- comportamento quando SQLite estiver indisponível;
- código legado removido/desativado;
- testes executados;
- comandos executados;
- resultado dos testes;
- testes de hardware executados;
- testes de hardware pendentes;
- limitações conhecidas;
- limitação referente a exclusões físicas;
- limitação referente à alteração de Doca de registros;
- necessidade futura de definir política/frequência de full reconciliation;
- confirmação explícita de que nenhuma leitura individual de EPC utiliza Power Automate/SharePoint.

---

# 124. Resultado final esperado

A implementação estará correta quando o caminho operacional de uma etiqueta for:

    Sensor DI1
        ↓
    inicia RFID
        ↓
    Zebra FX9600
        ↓
       EPC
        ↓
    processamento
        ↓
    SQLite local
        ↓
    EPC encontrado
        ↓
    dados exibidos
        ↓
    Cliente
    Nota Fiscal
    Volume
    Pedido
    Doca

Enquanto a atualização dos dados ocorrer de forma independente:

    SharePoint
        ↓
    Power Automate
        ↓
    Doca + modifiedSince
        ↓
    sincronização
        ↓
    transação
        ↓
    UPSERT
        ↓
    SQLite
        ↓
    COMMIT
        ↓
    salvar syncUntil

Essa passa a ser a arquitetura oficial para consulta e atualização da base do software RFID.    