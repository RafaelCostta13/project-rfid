# RF016 — Consulta e Validação Remota do EPC via Backend RFID

## 1. Objetivo

Alterar o fluxo operacional do software RFID para que a consulta e validação de cada EPC identificado pelo Zebra FX9600 deixe de utilizar a base SQLite local e passe a utilizar exclusivamente o Backend RFID através do endpoint:

    GET /api/v1/rfid_records/:epc

A partir deste requisito, a fonte operacional para validação de EPC passa a ser:

    Zebra FX9600
         │
         ▼
        EPC
         │
         ▼
    Software RFID
         │
         ▼
    Backend RFID
         │
         ▼
    Rails API
         │
         ▼
    PostgreSQL

Este requisito também deve corrigir uma incompatibilidade importante existente atualmente:

    O software RFID ainda espera o antigo JSON
    utilizado com SharePoint / Power Automate / SQLite.

Porém:

    O novo Backend Rails possui outro contrato JSON
    e outra estrutura de dados.

Portanto, NÃO basta trocar a URL da consulta.

É necessário adaptar corretamente:

- contrato da resposta;
- nomes dos campos;
- estrutura aninhada `data`;
- indicador de registro encontrado;
- modelo utilizado pelo software;
- preenchimento da tabela;
- tratamento de EPC não encontrado;
- tratamento de erros;
- deduplicação;
- retirada da dependência operacional do SQLite.

---

# 2. Contexto da alteração

Anteriormente o software trabalhava conceitualmente com dados vindos do SharePoint.

O JSON utilizado pelo software possuía estrutura semelhante a:

    {
        "sucesso": true,
        "epc": "484C44303130313237353835",
        "cliente": "HARLEY DAVIDSON",
        "notaFiscal": "127585",
        "pedido": "100066805",
        "volume": "1/2",
        "doca": ""
    }

Essa estrutura NÃO representa o contrato atual do Backend RFID.

O novo Backend utiliza PostgreSQL e possui uma estrutura de dados diferente.

---

# 3. Problema atual

O software RFID ainda possui código preparado para campos como:

    sucesso
    cliente
    notaFiscal
    volume
    pedido
    doca
    epc

Entretanto, o Backend atual retorna:

    found
    data

e dentro de:

    data

existem os campos:

    datahora
    volume
    pedido
    notafiscal
    destinatario
    endereco
    numero
    cidade
    uf
    doca
    epc
    tag
    fornecedor
    status
    first_read_at
    last_read_at
    read_count

Portanto, existem pelo menos três incompatibilidades:

    1. estrutura do JSON;

    2. nomes dos campos;

    3. quantidade e significado dos dados disponíveis.

O Codex deve corrigir essa incompatibilidade de forma estrutural.

Não criar apenas vários `.get()` espalhados pela UI para tentar suportar os dois formatos.

---

# 4. Arquitetura após o RF016

Após este requisito:

    Zebra FX9600
         │
         ▼
    EPC recebido
         │
         ▼
    normalização
         │
         ▼
    deduplicação
         │
         ▼
    Backend RFID Client
         │
         ▼
    GET /api/v1/rfid_records/:epc
         │
         ▼
    PostgreSQL
         │
         ├── encontrado
         │       ↓
         │    dados do registro
         │       ↓
         │    software RFID
         │
         └── não encontrado
                 ↓
              ignorar

O SQLite deixa de participar da consulta operacional do EPC.

---

# 5. Endpoint utilizado

Utilizar:

    GET /api/v1/rfid_records/:epc

Exemplo conceitual:

    GET /api/v1/rfid_records/E280691500005029EEA6A275

A Base URL deve vir exclusivamente da configuração implementada no RF015.

Não hardcodar a Base URL novamente.

---

# 6. Cliente Backend

Reutilizar obrigatoriamente o cliente/serviço Backend criado no RF015.

Conceitualmente:

    BackendRfidClient
        │
        ├── health()
        │
        └── get_rfid_record(epc)

Os nomes reais devem seguir o padrão do projeto.

Não criar um segundo cliente HTTP exclusivamente para consulta EPC.

---

# 7. Estrutura atual do banco PostgreSQL

A tabela operacional principal do Backend é:

    rfid_records

Model Rails:

    RfidRecord

A estrutura atual possui os seguintes campos de negócio:

    datahora
    volume
    pedido
    notafiscal
    destinatario
    endereco
    numero
    cidade
    uf
    doca
    epc
    tag
    fornecedor
    status

Posteriormente foram adicionados os campos de controle de leitura:

    first_read_at
    last_read_at
    read_count

O Rails também possui os campos internos:

    id
    created_at
    updated_at

Esses campos internos não fazem parte do contrato do GET de consulta RFID.

---

# 8. Tipos conceituais atuais

A estrutura definida para `rfid_records` utiliza conceitualmente:

    datahora          datetime

    volume            string
    pedido            string
    notafiscal        string
    destinatario      string
    endereco          string
    numero            string
    cidade            string
    uf                string
    doca              string
    epc               string
    tag               string / nullable
    fornecedor        string
    status            string

    first_read_at     datetime / nullable
    last_read_at      datetime / nullable
    read_count        integer

    created_at        datetime
    updated_at        datetime

`read_count` possui valor inicial:

    0

`first_read_at` e `last_read_at` podem inicialmente ser:

    null

O Codex deve conferir o schema/migrations atuais do Backend caso estejam disponíveis no repositório/documentação, mas NÃO deve modificar o Backend neste requisito.

---

# 9. Campos que devem permanecer string

Campos como:

    pedido
    notafiscal
    numero

devem ser tratados como texto.

Não converter automaticamente para inteiro.

Exemplo:

    pedido = "0007819215"

deve permanecer:

    "0007819215"

e NÃO:

    "7819215"

Isso evita perda de zeros à esquerda.

---

# 10. EPC no PostgreSQL

O campo:

    epc

é a chave de negócio utilizada para consulta.

A estrutura atual do Backend define EPC como obrigatório e único.

A normalização definida no Backend é:

    strip
    +
    upcase

Exemplo:

    "  e280691500005029eea6a275  "

deve ser consultado como:

    "E280691500005029EEA6A275"

---

# 11. Não converter EPC para ASCII

Preservar a decisão anterior do projeto.

Não reintroduzir:

    EPC hexadecimal → ASCII

Não recriar o antigo conceito de:

    Tag derivada do EPC

O campo:

    tag

que existe no PostgreSQL é um campo próprio da base.

Ele NÃO deve ser calculado pelo software a partir do EPC.

---

# 12. Status do registro

O campo:

    status

possui atualmente os valores de negócio:

    pendente
    lido

Semântica:

    pendente
        =
    registro cadastrado,
    ainda não processado como leitura RFID

    lido
        =
    registro já processado/lido pelo sistema RFID

O GET deste requisito é somente consulta.

Portanto:

    GET /api/v1/rfid_records/:epc

NÃO deve alterar:

- status;
- read_count;
- first_read_at;
- last_read_at;
- histórico.

Essa alteração será responsabilidade do RF017 através do POST de leitura.

---

# 13. Estrutura de histórico existente no Backend

O Backend também possui uma estrutura para histórico de leituras:

    rfid_read_events

Conceitualmente contém:

    rfid_record_id
    epc
    read_at
    duplicate
    created_at
    updated_at

Existe relação:

    RfidRecord
        1
        │
        ▼
        N
    RfidReadEvent

O RF016 NÃO deve criar eventos nessa tabela.

O endpoint GET é estritamente somente leitura.

---

# 14. Campos de controle de leitura

Os campos:

    first_read_at
    last_read_at
    read_count

já fazem parte do registro retornado pela API.

Neste RF eles são apenas informações recebidas.

Não incrementar:

    read_count

Não alterar:

    first_read_at
    last_read_at

Não utilizar GET como se fosse registro de passagem.

---

# 15. Contrato atual do GET — registro encontrado

Quando o EPC existir, o Backend retorna:

    HTTP 200

com estrutura:

    {
        "found": true,
        "data": {
            "datahora": "...",
            "volume": "...",
            "pedido": "...",
            "notafiscal": "...",
            "destinatario": "...",
            "endereco": "...",
            "numero": "...",
            "cidade": "...",
            "uf": "...",
            "doca": "...",
            "epc": "...",
            "tag": "...",
            "fornecedor": "...",
            "status": "...",
            "first_read_at": null,
            "last_read_at": null,
            "read_count": 0
        }
    }

A aplicação deve passar a entender esse contrato diretamente.

---

# 16. Exemplo de registro atual

Utilizando o registro de referência definido para a nova base:

    {
        "found": true,
        "data": {
            "datahora": "2026-10-06T14:41:25.000Z",
            "volume": "2/4",
            "pedido": "0007819215",
            "notafiscal": "1198780",
            "destinatario": "EURO IMPORT COMERCIO E SERVICOS LTDA",
            "endereco": "AV DAS NACOES UNIDAS",
            "numero": "17381",
            "cidade": "SAO PAULO",
            "uf": "SP",
            "doca": "DOCA 35",
            "epc": "E280691500005029EEA6A275",
            "tag": "TAG000123",
            "fornecedor": "BMW",
            "status": "pendente",
            "first_read_at": null,
            "last_read_at": null,
            "read_count": 0
        }
    }

O Codex deve utilizar os nomes dos campos exatamente como definidos pelo contrato do Backend.

---

# 17. Campos não retornados pelo GET

Não depender de:

    id
    created_at
    updated_at

Esses campos são internos do Backend e não fazem parte do contrato operacional de consulta.

O software RFID não precisa conhecer o ID interno PostgreSQL/Rails para consultar um EPC.

---

# 18. Contrato — EPC não encontrado

Quando o EPC não existir:

    HTTP 404

Resposta:

    {
        "found": false,
        "error": "epc_not_found",
        "epc": "E280691500005029EEA6A275"
    }

Isso representa:

    consulta executada corretamente
    +
    Backend disponível
    +
    EPC inexistente

Portanto:

    HTTP 404 neste endpoint NÃO significa falha do Sistema.

---

# 19. Diferença fundamental entre 404 e erro técnico

Distinguir obrigatoriamente:

    404 epc_not_found
        =
    consulta válida
    EPC não cadastrado

de:

    timeout
    connection refused
    HTTP 500
    HTTP 502
    HTTP 503
    JSON inválido
        =
    problema técnico de comunicação/Backend

Não tratar todos como:

    EPC não encontrado

---

# 20. Incompatibilidade com o JSON antigo

O código atual pode estar esperando algo semelhante a:

    response["sucesso"]

Isso não existe mais.

Agora deve utilizar:

    response["found"]

O código atual pode estar esperando:

    response["cliente"]

Isso não existe mais.

Agora o dado está em:

    response["data"]["destinatario"]

O código atual pode estar esperando:

    response["notaFiscal"]

Agora o campo é:

    response["data"]["notafiscal"]

Além disso, os dados agora estão dentro de:

    data

e não diretamente na raiz da resposta.

---

# 21. Mapeamento oficial para compatibilidade da interface

A partir deste RF fica definido o seguinte mapeamento para a interface atual do software:

| Interface / conceito antigo | Backend atual |
|---|---|
| `sucesso` | `found` |
| `cliente` | `data.destinatario` |
| `notaFiscal` | `data.notafiscal` |
| `volume` | `data.volume` |
| `pedido` | `data.pedido` |
| `doca` | `data.doca` |
| `epc` | `data.epc` |
| Status exibido do registro | `data.status` |

Portanto, para fins da interface atual:

    Cliente
        =
    destinatario

e:

    Nota fiscal
        =
    notafiscal

Essa passa a ser a regra de integração do software RFID com o novo Backend.

---

# 22. Não renomear o Backend para imitar o SharePoint

Não solicitar nem implementar alteração no Backend para retornar:

    cliente
    notaFiscal
    sucesso

apenas porque o software antigo utilizava esses nomes.

O software RFID deve ser adaptado ao novo contrato.

A nova API passa a ser a referência oficial.

---

# 23. Não criar um JSON falso intermediário desnecessário

Evitar uma solução como:

    Backend JSON
        ↓
    criar artificialmente antigo JSON SharePoint
        ↓
    UI antiga

Exemplo a evitar:

    {
        "sucesso": true,
        "cliente": data["destinatario"],
        "notaFiscal": data["notafiscal"]
    }

Preferir criar/adaptar um modelo interno apropriado para o registro RFID atual.

---

# 24. Modelo interno

Criar ou adaptar uma representação interna equivalente a:

    RfidRecordData

contendo conceitualmente:

    datahora
    volume
    pedido
    notafiscal
    destinatario
    endereco
    numero
    cidade
    uf
    doca
    epc
    tag
    fornecedor
    status
    first_read_at
    last_read_at
    read_count

O nome real deve seguir a arquitetura existente.

Não é obrigatório usar `dataclass` caso o projeto utilize outro padrão.

---

# 25. Separar modelo de API da UI

A UI não deve conhecer detalhes como:

    response["data"]["destinatario"]

diretamente.

Fluxo preferido:

    Backend JSON
         │
         ▼
    Backend Service
         │
         ▼
    modelo interno
         │
         ▼
    processamento RFID
         │
         ▼
    UI

Isso evita espalhar o contrato HTTP pela aplicação.

---

# 26. Tabela atual

Preservar inicialmente a tabela visual existente:

    Status
    Cliente
    Nota fiscal
    Volume
    Pedido
    Doca

Neste RF não é necessário adicionar todas as novas colunas do PostgreSQL à interface.

---

# 27. Preenchimento da tabela

A tabela deverá utilizar:

    Status
        ← data.status

    Cliente
        ← data.destinatario

    Nota fiscal
        ← data.notafiscal

    Volume
        ← data.volume

    Pedido
        ← data.pedido

    Doca
        ← data.doca

Os demais campos recebidos devem permanecer disponíveis no modelo interno, mesmo que não sejam exibidos nessa tabela neste momento.

---

# 28. Campos adicionais do Backend

Os seguintes campos são novos em relação ao JSON antigo utilizado pela interface:

    datahora
    endereco
    numero
    cidade
    uf
    tag
    fornecedor
    status
    first_read_at
    last_read_at
    read_count

Não descartá-los prematuramente na camada de integração.

Eles podem ser necessários nos próximos requisitos.

Porém não alterar a interface para exibi-los sem requisito específico.

---

# 29. Campo status não significa "Encontrado"

Importante:

    found

e:

    status

possuem significados diferentes.

`found` significa:

    o EPC existe ou não na base

`status` significa:

    estado de leitura do registro

com valores:

    pendente
    lido

Portanto, não fazer:

    status = "Encontrado"

apenas porque:

    found = true

A coluna Status deve utilizar o estado de negócio retornado pelo Backend quando essa coluna representar o status do registro.

---

# 30. Fluxo completo da consulta

Fluxo esperado:

    Zebra FX9600
          │
          ▼
      EPC recebido
          │
          ▼
    strip + uppercase
          │
          ▼
      EPC válido?
          │
          ├── NÃO
          │     ↓
          │   ignorar
          │
          └── SIM
                │
                ▼
          já processado
          nesta sessão?
                │
          ┌─────┴─────┐
          │           │
         SIM         NÃO
          │           │
          ▼           ▼
       ignorar      GET API
                      │
                      ▼
               HTTP response
                      │
            ┌─────────┼─────────┐
            │         │         │
           200       404      ERRO
            │         │         │
            ▼         ▼         ▼
         validar    ignorar   erro técnico
          JSON
            │
            ▼
       found = true
            │
            ▼
       criar modelo
            │
            ▼
       adicionar UI

---

# 31. Normalização do EPC

Antes da consulta:

    epc = epc.strip().upper()

ou equivalente já existente no projeto.

Não duplicar normalização caso ela já ocorra em uma camada central.

---

# 32. EPC na URL

O EPC deve ser utilizado como parâmetro de path.

Conceitualmente:

    /api/v1/rfid_records/{epc}

A montagem deve ser realizada pelo cliente Backend.

A UI não deve concatenar URL.

Utilizar encoding apropriado do parâmetro de path.

---

# 33. Deduplicação da sessão

Preservar a regra existente do software:

    a mesma etiqueta não deve ser enviada repetidamente
    durante a mesma sessão/ciclo de leitura.

Portanto, o mesmo EPC normalizado não deve gerar múltiplos GETs desnecessários durante a mesma sessão.

Não remover a deduplicação existente.

---

# 34. Deduplicação continua sendo responsabilidade do software

O Backend não deve ser utilizado para resolver repetição causada pelo reader durante a mesma sessão.

Exemplo:

    Zebra lê EPC A
    Zebra lê EPC A
    Zebra lê EPC A
    Zebra lê EPC A

Resultado esperado no software:

    1 consulta operacional para EPC A

e não:

    4 consultas HTTP

Reutilizar a infraestrutura atual de deduplicação.

---

# 35. EPC encontrado

Condição:

    HTTP 200
    +
    found = true
    +
    data válido

Resultado:

- considerar EPC encontrado;
- criar/adaptar modelo interno;
- preencher tabela;
- incrementar contador de EPCs encontrados conforme regra atual;
- preservar deduplicação;
- manter EPC internamente;
- NÃO registrar passagem ainda.

---

# 36. EPC não encontrado

Condição:

    HTTP 404
    +
    found = false
    +
    error = "epc_not_found"

Resultado:

- ignorar EPC;
- não adicionar linha;
- não incrementar contador;
- não exibir "Não encontrado";
- não criar erro visual;
- não consultar SQLite;
- não executar fallback;
- não executar POST;
- pode registrar informação de diagnóstico em log.

Preservar o comportamento visual definido anteriormente.

---

# 37. Não restaurar card "EPCs não encontrados"

Não recriar:

    EPCs não encontrados

O card removido anteriormente deve continuar removido.

O usuário operacional deve continuar vendo apenas registros encontrados.

---

# 38. Não adicionar coluna EPC

Não adicionar novamente coluna EPC visível na tabela se ela atualmente não existir.

O EPC continua sendo utilizado internamente para:

- identidade;
- deduplicação;
- consulta;
- futura chamada POST do RF017.

---

# 39. Sem fallback SQLite

Após o cutover deste RF:

    GET remoto não encontrou EPC
        ↓
    ignorar

NÃO:

    GET remoto não encontrou
        ↓
    consultar SQLite

Também NÃO:

    Backend indisponível
        ↓
    consultar SQLite

O SQLite deixa de ser fonte operacional.

---

# 40. Sem fallback Power Automate

Também é proibido:

    Backend Rails falhou
        ↓
    consultar Power Automate antigo

Não manter duas arquiteturas operacionais.

A fonte oficial passa a ser:

    Rails API
        ↓
    PostgreSQL

---

# 41. Doca

O endpoint atual consulta:

    /api/v1/rfid_records/:epc

Ele NÃO recebe Doca como parâmetro.

Portanto, neste RF não inventar:

    ?doca=D01

nem:

    {
        "doca": "D01"
    }

na consulta GET.

---

# 42. Doca retornada pelo Backend

O campo:

    data.doca

deve ser tratado como dado do registro e exibido normalmente.

Não foi definida até este momento uma regra no novo Backend determinando que:

    doca retornada
        =
    doca configurada na estação

seja condição obrigatória para aceitar o EPC.

Portanto, NÃO rejeitar um EPC encontrado apenas porque sua Doca é diferente da Doca configurada no software sem um requisito específico.

A antiga regra SQLite `EPC + Doca` pertencia à arquitetura anterior e não deve ser transportada automaticamente para a nova API.

---

# 43. Configuração de Doca

Preservar a configuração de Doca existente no software.

Não removê-la.

Porém ela não deve ser enviada ao:

    GET /api/v1/rfid_records/:epc

neste requisito.

---

# 44. HTTP 200 com contrato inválido

Exemplo:

    HTTP 200

    {
        "foo": "bar"
    }

Isso NÃO deve ser considerado EPC encontrado.

Tratar como:

    resposta inválida do Backend

Não adicionar linha.

Não incrementar contador.

Registrar erro técnico.

---

# 45. HTTP 200 com found false

O contrato normal para EPC inexistente utiliza:

    HTTP 404

Portanto, se ocorrer uma combinação inesperada:

    HTTP 200
    found = false

não inventar dados.

Tratar de forma defensiva e registrar inconsistência de contrato.

---

# 46. HTTP 404

O 404 documentado:

    error = epc_not_found

é condição de negócio.

Não deve:

- marcar Sistema NOK;
- marcar Base de dados NOK;
- acionar CH3;
- interromper a leitura RFID;
- gerar popup de erro.

O Backend funcionou corretamente e apenas informou que o EPC não existe.

---

# 47. Timeout

Se a consulta sofrer timeout:

- não considerar EPC não encontrado;
- não adicionar linha;
- não incrementar contador;
- registrar erro técnico;
- reportar falha através da infraestrutura central criada no RF015;
- não manipular relés diretamente no cliente HTTP.

---

# 48. HTTP 5xx

Se ocorrer:

    500
    502
    503
    504

ou equivalente:

tratar como falha técnica do Backend.

Não transformar em:

    EPC não encontrado

Utilizar o mecanismo central de disponibilidade.

---

# 49. Falha de conexão

Casos:

    connection refused
    DNS failure
    TLS error
    timeout
    network unavailable

devem ser tratados como falha de comunicação.

Nenhum desses casos deve causar crash da aplicação.

---

# 50. Integração com status RF015

O RF015 já possui:

    Sistema
    Base de dados

através do:

    GET /api/v1/health

O RF016 não deve criar novos indicadores.

Falhas técnicas durante uma consulta EPC podem ser reportadas ao mecanismo central de disponibilidade, mas a UI não deve possuir uma segunda lógica independente para Sistema/Base de dados.

---

# 51. Não manipular relés no Backend Client

O serviço responsável por:

    GET /api/v1/rfid_records/:epc

não deve executar:

    CH1
    CH2
    CH3

diretamente.

A cadeia correta é:

    Backend Client
         │
         ▼
    resultado/erro
         │
         ▼
    estado central
         │
         ▼
    lógica operacional
         │
         ▼
    Waveshare

Preservar separação de responsabilidades.

---

# 52. Execução não bloqueante

A consulta HTTP não deve bloquear a interface gráfica.

Também deve ser analisado cuidadosamente o callback do LLRP.

Não executar uma chamada HTTP lenta diretamente de forma que:

- bloqueie a UI;
- bloqueie o reader;
- impeça processamento de novas tags;
- provoque perda de eventos.

Reutilizar workers/filas/executores existentes.

---

# 53. Ordem das respostas

Como consultas podem ser executadas em background, garantir que respostas assíncronas não corrompam:

- tabela;
- contador;
- deduplicação;
- estado da sessão.

Não assumir que respostas HTTP obrigatoriamente retornarão na mesma ordem das leituras.

---

# 54. Sessão/ciclo

Preservar o conceito atual de sessão/ciclo RFID.

Se uma resposta HTTP de uma sessão antiga chegar depois que aquela sessão já foi encerrada, analisar a arquitetura atual e impedir que callbacks obsoletos alterem incorretamente o estado da sessão atual.

Reutilizar mecanismos de generation/session ID caso já existam.

Não criar race conditions.

---

# 55. Timeout HTTP

Utilizar o timeout central definido no RF015.

Não criar outro timeout hardcoded apenas para consulta EPC.

Se futuramente houver necessidade de timeout específico por endpoint, centralizar em configuração apropriada.

---

# 56. Não realizar POST neste RF

Mesmo quando:

    GET retorna 200
    found = true

NÃO executar ainda:

    POST /api/v1/rfid_reads

Isso será implementado no:

    RF017

O RF016 é exclusivamente:

    consulta
    +
    validação
    +
    apresentação

---

# 57. Consequência temporária do RF016

Até o RF017 ser executado:

    GET encontrou EPC

não significa que o Backend registrará a passagem.

Portanto:

    status
    first_read_at
    last_read_at
    read_count
    rfid_read_events

não serão modificados pelo RF016.

Isso é esperado.

---

# 58. Retirada da consulta SQLite

Depois que a consulta remota estiver implementada e validada:

remover/desativar do caminho operacional:

    lookup SQLite por EPC

Nenhuma leitura nova deve consultar o banco local.

---

# 59. Retirada da sincronização antiga

O RF015 permitia preservar temporariamente partes da sincronização caso fossem necessárias para manter o lookup local até o RF016.

Agora essa dependência deixa de existir.

Depois do cutover e dos testes:

- desativar sincronização automática antiga;
- remover timers exclusivos da sincronização;
- remover chamadas Power Automate de sincronização;
- remover serviços exclusivamente obsoletos;
- remover participação do SQLite na operação RFID.

---

# 60. Não apagar arquivo SQLite do computador automaticamente

Mesmo deixando de utilizar SQLite operacionalmente, não apagar automaticamente o arquivo físico existente no computador do usuário.

A limpeza de dados locais não deve ser destrutiva sem necessidade.

O arquivo pode permanecer no disco até uma política específica de migração/limpeza ser definida.

---

# 61. Remoção segura de código legado

Antes de apagar qualquer classe ou serviço relacionado ao SQLite, verificar se também é utilizado por outra funcionalidade.

Remover apenas componentes comprovadamente obsoletos.

Não remover:

- configuração geral;
- logging;
- HTTP client;
- componentes compartilhados;
- estruturas utilizadas por outras telas.

---

# 62. Nova fonte de verdade operacional

Após o RF016:

    PostgreSQL
        │
        ▼
    Rails API
        │
        ▼
    Software RFID

é a fonte oficial para validação operacional.

O software não deve tentar reconciliar respostas da API com dados antigos do SQLite.

---

# 63. Não comparar API com SQLite

Não implementar:

    resultado API
        VS
    resultado SQLite

para decidir qual é correto.

A resposta válida do Backend é a referência.

---

# 64. Compatibilidade de campos

O Codex deve procurar no projeto qualquer referência aos campos antigos:

    sucesso
    cliente
    notaFiscal

e analisar onde são utilizados.

Também procurar:

    volume
    pedido
    doca
    epc
    status

O objetivo é identificar todos os locais afetados pela mudança do contrato.

---

# 65. Busca obrigatória no código

Antes de implementar, pesquisar no repositório por:

    "sucesso"
    "cliente"
    "notaFiscal"
    "notafiscal"
    "destinatario"
    "found"
    "epc"
    "sqlite"
    "sync"
    "Power Automate"

Não realizar substituição global automática.

Analisar cada ocorrência.

---

# 66. Não manter dois contratos indefinidamente

Após o cutover não manter código como:

    if "sucesso" in response:
        usar_json_antigo
    elif "found" in response:
        usar_json_novo

salvo se existir uma necessidade real documentada.

O objetivo é migrar o software para o novo contrato, não manter permanentemente compatibilidade com a arquitetura antiga.

---

# 67. Contrato oficial após RF016

O contrato oficial passa a ser:

    {
        "found": true,
        "data": {
            ...
        }
    }

ou:

    {
        "found": false,
        "error": "epc_not_found",
        "epc": "..."
    }

Não utilizar mais `sucesso` como indicador da consulta RFID.

---

# 68. DataHora

O Backend retorna:

    datahora

em formato serializado pela API Rails.

O software deve tratá-lo como dado recebido.

Não realizar conversões desnecessárias se o campo ainda não for exibido.

Caso seja convertido para datetime internamente, utilizar parsing seguro e timezone-aware.

Não utilizar `datahora` como horário da leitura física atual.

Ele pertence ao registro de negócio.

---

# 69. first_read_at e last_read_at

Esses campos possuem significado diferente de:

    datahora

`datahora` pertence aos dados originais do registro.

`first_read_at` representa a primeira passagem RFID registrada.

`last_read_at` representa a passagem RFID mais recente registrada.

Não misturar esses conceitos.

---

# 70. read_count

`read_count` representa a quantidade de passagens registradas pelo Backend.

Neste RF:

    somente leitura

Não incrementar localmente.

O RF017 será responsável por chamar o endpoint que efetivamente incrementa esse contador no servidor.

---

# 71. fornecedor

O novo banco possui:

    fornecedor

Esse campo não existia no JSON antigo utilizado pela interface RFID.

Preservá-lo no modelo interno.

Não substituir:

    Cliente

por:

    fornecedor

A coluna Cliente utiliza:

    destinatario

---

# 72. destinatario

A partir deste RF, para integração com a interface existente:

    destinatario

é o campo utilizado para preencher:

    Cliente

Exemplo:

    destinatario =
    "EURO IMPORT COMERCIO E SERVICOS LTDA"

Interface:

    Cliente
    EURO IMPORT COMERCIO E SERVICOS LTDA

---

# 73. notafiscal

O novo Backend utiliza exatamente:

    notafiscal

Não:

    notaFiscal

Não:

    nota_fiscal

O parser deve respeitar o contrato atual.

Na UI o título pode continuar:

    Nota fiscal

---

# 74. tag

O campo:

    tag

pode ser:

    null

Isso é válido.

Um registro NÃO deve ser rejeitado apenas porque:

    tag = null

Não tentar calcular automaticamente `tag` a partir do EPC.

---

# 75. Campos obrigatórios para considerar resposta válida

O Codex deve validar minimamente a estrutura necessária para o fluxo operacional.

Para um `found = true`, devem existir dados suficientes para identificar o registro e alimentar o fluxo atual.

No mínimo, o EPC retornado deve ser coerente com a consulta.

Não exigir artificialmente campos opcionais como `tag`.

Não rejeitar uma resposta válida apenas porque um campo opcional está `null`.

---

# 76. EPC retornado

Para:

    GET /rfid_records/E280...

a resposta deve conter:

    data.epc

O software pode validar que o EPC retornado, após normalização, corresponde ao EPC consultado.

Se houver divergência:

- não adicionar resultado silenciosamente;
- registrar inconsistência de contrato/dados;
- tratar como erro técnico de resposta.

---

# 77. Contador

Preservar o card atual:

    EPCs encontrados

Ele continua contando EPCs distintos encontrados na sessão atual.

Não utilizar:

    read_count

do PostgreSQL para preencher esse card.

São métricas diferentes.

---

# 78. Diferença entre os dois contadores

O software possui:

    EPCs encontrados
        =
    quantidade de EPCs distintos encontrados
    na sessão/ciclo atual

O Backend possui:

    read_count
        =
    quantidade histórica de passagens registradas
    para aquele registro

Não misturar os dois valores.

---

# 79. Status visual do sistema

Preservar os indicadores implementados no RF015:

    RFID
    Comandos
    Sistema
    Base de dados

e:

    Internet

caso continue presente.

Não recriar:

    Sincronização

---

# 80. System Ready

Como a consulta EPC agora depende obrigatoriamente da API, preservar a regra do RF015 de que o Backend precisa estar operacional para iniciar uma nova operação.

Conceitualmente:

    system_ready =
        RFID OK
        AND
        Comandos OK
        AND
        Sistema OK
        AND
        Base de dados OK
        AND
        demais condições obrigatórias existentes

Não duplicar essa regra na UI.

---

# 81. CH1 / CH2 / CH3

Preservar:

    CH1
        =
    sistema apto

    CH2
        =
    leitura RFID em andamento

    CH3
        =
    sistema indisponível/erro

O RF016 não altera o significado dos relés.

---

# 82. Consulta HTTP durante CH2

Durante uma sessão de leitura:

    CH2 ON

os EPCs recebidos podem gerar consultas HTTP ao Backend.

Não desligar CH2 a cada resposta individual.

CH2 representa a sessão RFID, não a requisição HTTP.

---

# 83. RF012 preservado

Preservar integralmente:

    DI1
    DI2
    timer de 60 segundos
    Start
    Stop
    CH1
    CH2
    CH3

Fluxo físico permanece:

    DI1 interrompido
        ↓
    inicia leitura
        ↓
    CH2 ON
        ↓
    Zebra lê EPCs
        ↓
    RF016 consulta Backend

DI2 ou timeout continuam encerrando a leitura conforme regras existentes.

---

# 84. Análise obrigatória antes da implementação

Antes de alterar qualquer arquivo, o Codex deve analisar:

1. `AGENTS.md`;
2. RF012;
3. RF014;
4. RF015;
5. tela Start;
6. processamento atual dos EPCs;
7. callback LLRP;
8. fila/worker de processamento;
9. deduplicação;
10. consulta SQLite atual;
11. repository SQLite;
12. serviço de sincronização;
13. Power Automate antigo;
14. cliente Backend criado no RF015;
15. configuração da Base URL;
16. health check;
17. status Sistema;
18. status Base de dados;
19. `system_ready`;
20. CH1/CH2/CH3;
21. tabela de resultados;
22. card EPCs encontrados;
23. modelo atual de resultado;
24. parser do JSON antigo;
25. testes existentes.

Não implementar antes dessa análise.

---

# 85. Relatório obrigatório antes da implementação

Antes de modificar o código, apresentar um relatório curto contendo:

- fluxo atual desde o EPC até a tabela;
- onde o SQLite é consultado;
- onde a resposta antiga é convertida;
- onde existem referências a `sucesso`;
- onde existem referências a `cliente`;
- onde existem referências a `notaFiscal`;
- modelo atual utilizado pela UI;
- como será introduzido o novo contrato;
- como `destinatario` será mapeado para Cliente;
- como `notafiscal` será mapeado para Nota fiscal;
- como `status` será tratado;
- como os campos adicionais serão preservados;
- onde será realizada a chamada GET;
- como a chamada ficará fora da thread da UI;
- como será preservada a deduplicação;
- como será tratado 404;
- como serão tratados erros técnicos;
- quais componentes SQLite poderão ser removidos;
- quais componentes de sincronização poderão ser removidos;
- arquivos previstos para alteração.

Somente depois iniciar a implementação.

---

# 86. Teste unitário — resposta 200

Mock:

    HTTP 200

    {
        "found": true,
        "data": {
            "datahora": "2026-10-06T14:41:25.000Z",
            "volume": "2/4",
            "pedido": "0007819215",
            "notafiscal": "1198780",
            "destinatario": "EURO IMPORT COMERCIO E SERVICOS LTDA",
            "endereco": "AV DAS NACOES UNIDAS",
            "numero": "17381",
            "cidade": "SAO PAULO",
            "uf": "SP",
            "doca": "DOCA 35",
            "epc": "E280691500005029EEA6A275",
            "tag": "TAG000123",
            "fornecedor": "BMW",
            "status": "pendente",
            "first_read_at": null,
            "last_read_at": null,
            "read_count": 0
        }
    }

Esperado:

    registro encontrado

e modelo interno preenchido corretamente.

---

# 87. Teste — mapeamento da interface

Para a resposta anterior, confirmar:

    Status
        =
    pendente

    Cliente
        =
    EURO IMPORT COMERCIO E SERVICOS LTDA

    Nota fiscal
        =
    1198780

    Volume
        =
    2/4

    Pedido
        =
    0007819215

    Doca
        =
    DOCA 35

Confirmar que:

    pedido

mantém os zeros à esquerda.

---

# 88. Teste — 404

Mock:

    HTTP 404

    {
        "found": false,
        "error": "epc_not_found",
        "epc": "E280691500005029EEA6A275"
    }

Esperado:

- nenhuma linha;
- nenhum incremento;
- nenhum popup;
- Sistema continua OK;
- Base de dados continua OK;
- nenhum SQLite;
- nenhum Power Automate;
- nenhum POST.

---

# 89. Teste — tag null

Mock:

    "tag": null

Esperado:

    registro continua válido

Não rejeitar.

---

# 90. Teste — status lido

Mock:

    "status": "lido"

Esperado:

    consulta continua válida

Apenas apresentar o estado recebido.

O GET não deve alterar o status.

---

# 91. Teste — read_count

Mock:

    "read_count": 15

Esperado:

- preservar valor no modelo;
- não utilizar como card EPCs encontrados;
- não incrementar localmente.

---

# 92. Teste — normalização

Entrada:

    "  e280691500005029eea6a275  "

Esperado:

    GET /api/v1/rfid_records/E280691500005029EEA6A275

---

# 93. Teste — EPC duplicado na sessão

Reader produz:

    EPC A
    EPC A
    EPC A

Esperado:

    uma única consulta operacional

conforme mecanismo de deduplicação da sessão.

---

# 94. Teste — timeout

Mock:

    timeout

Esperado:

- nenhum resultado falso;
- nenhum "não encontrado";
- nenhuma consulta SQLite;
- erro técnico controlado;
- UI responsiva.

---

# 95. Teste — HTTP 500

Mock:

    HTTP 500

Esperado:

- tratar como falha técnica;
- não tratar como EPC inexistente;
- não adicionar linha;
- não executar fallback.

---

# 96. Teste — JSON antigo não deve ser necessário

Depois da migração, testar que o fluxo principal NÃO depende de:

    sucesso
    cliente
    notaFiscal

A aplicação deve operar com:

    found
    data.destinatario
    data.notafiscal

---

# 97. Teste — ausência de SQLite

Executar teste com o banco SQLite antigo indisponível/removido do ambiente de teste.

Com Backend disponível:

    consulta EPC deve funcionar normalmente.

Isso comprova que o lookup remoto não possui dependência oculta do SQLite.

---

# 98. Teste — ausência de Power Automate

Executar sem o antigo Power Automate.

Com Backend Rails disponível:

    consulta EPC deve funcionar normalmente.

---

# 99. Teste — GET não altera Backend

Consultar um registro conhecido.

Antes:

    status = pendente
    read_count = 0
    first_read_at = null
    last_read_at = null

Executar:

    GET /api/v1/rfid_records/:epc

Depois:

    status = pendente
    read_count = 0
    first_read_at = null
    last_read_at = null

O GET não deve registrar passagem.

---

# 100. Teste de regressão

Confirmar:

- Zebra FX9600 conecta;
- Start funciona;
- Stop funciona;
- DI1 funciona;
- DI2 funciona;
- timer 60 segundos funciona;
- CH1 funciona;
- CH2 funciona;
- CH3 funciona;
- Waveshare funciona;
- diagnóstico Waveshare funciona;
- deduplicação funciona;
- tabela funciona;
- contador funciona;
- Sistema funciona;
- Base de dados funciona;
- Sincronização continua removida;
- UI permanece responsiva.

---

# 101. Teste manual no Windows

Executar nativamente no Windows:

1. iniciar Backend Rails;
2. confirmar `/api/v1/health`;
3. iniciar software RFID;
4. confirmar Sistema OK;
5. confirmar Base de dados OK;
6. iniciar leitura;
7. ler EPC existente;
8. confirmar GET remoto;
9. confirmar `found = true`;
10. confirmar dados exibidos;
11. confirmar Cliente vindo de `destinatario`;
12. confirmar Nota fiscal vindo de `notafiscal`;
13. confirmar ausência de consulta SQLite;
14. ler EPC inexistente;
15. confirmar 404;
16. confirmar que EPC inexistente foi ignorado;
17. confirmar que Sistema não ficou NOK devido ao 404;
18. desligar Backend;
19. confirmar tratamento de falha;
20. restaurar Backend;
21. confirmar recuperação do status.

---

# 102. Ambiente oficial

O software RFID continua sendo desenvolvido e validado em:

    Windows

Não utilizar WSL como ambiente oficial.

O Backend pode estar executando em Docker, mas isso não altera o ambiente oficial do software desktop RFID.

---

# 103. Fora do escopo

Não implementar neste RF:

- POST `/api/v1/rfid_reads`;
- atualização de `status`;
- incremento de `read_count`;
- atualização de `first_read_at`;
- atualização de `last_read_at`;
- criação de `rfid_read_events`;
- autenticação;
- alteração do Backend Rails;
- alteração do PostgreSQL;
- alteração do schema;
- alteração da Doca no Backend;
- validação Doca configurada versus Doca retornada;
- novas colunas visuais;
- dashboard de histórico;
- consulta de histórico;
- escrita RFID;
- alteração LLRP;
- alteração da lógica DI1/DI2;
- alteração do timer;
- alteração CH4–CH8.

---

# 104. Preservar obrigatoriamente

Preservar:

- Zebra FX9600;
- LLRP;
- normalização EPC;
- EPC hexadecimal;
- deduplicação;
- Start/Stop;
- RF012;
- RF015;
- DI1;
- DI2;
- timer 60 segundos;
- CH1;
- CH2;
- CH3;
- CH4–CH8;
- Waveshare;
- diagnóstico Waveshare;
- configuração Backend;
- configuração Doca;
- status RFID;
- status Comandos;
- status Sistema;
- status Base de dados;
- Internet, caso exista;
- tabela atual;
- card EPCs encontrados;
- comportamento de ignorar EPC não encontrado.

---

# 105. Critérios de aceite — Backend

- [ ] consulta utilizar GET `/api/v1/rfid_records/:epc`;
- [ ] Base URL vir do RF015;
- [ ] cliente Backend do RF015 ser reutilizado;
- [ ] EPC ser normalizado;
- [ ] EPC ser enviado no path;
- [ ] HTTP possuir timeout;
- [ ] consulta não bloquear UI;
- [ ] HTTP 200 ser interpretado corretamente;
- [ ] HTTP 404 ser interpretado como EPC inexistente;
- [ ] HTTP 404 não marcar Sistema NOK;
- [ ] erros técnicos não serem tratados como EPC inexistente.

---

# 106. Critérios de aceite — contrato JSON

- [ ] software não depender mais de `sucesso`;
- [ ] software utilizar `found`;
- [ ] software interpretar `data`;
- [ ] `destinatario` alimentar Cliente;
- [ ] `notafiscal` alimentar Nota fiscal;
- [ ] `volume` ser preservado;
- [ ] `pedido` ser preservado como string;
- [ ] `doca` ser preservada;
- [ ] `epc` ser preservado;
- [ ] `status` ser preservado;
- [ ] `tag = null` ser aceito;
- [ ] campos adicionais serem representáveis pelo modelo interno;
- [ ] `read_count` não ser confundido com contador da sessão.

---

# 107. Critérios de aceite — arquitetura

- [ ] SQLite não participar mais da consulta EPC;
- [ ] não existir fallback SQLite;
- [ ] não existir fallback Power Automate;
- [ ] PostgreSQL através da API ser a fonte operacional;
- [ ] software não acessar PostgreSQL diretamente;
- [ ] UI não interpretar HTTP diretamente;
- [ ] callback LLRP não possuir lógica HTTP espalhada;
- [ ] deduplicação impedir consultas repetidas na mesma sessão;
- [ ] Sincronização continuar removida;
- [ ] componentes antigos de sincronização serem desativados/removidos quando seguros.

---

# 108. Critérios de aceite — RF016 não registra leitura

- [ ] GET não alterar `status`;
- [ ] GET não alterar `read_count`;
- [ ] GET não alterar `first_read_at`;
- [ ] GET não alterar `last_read_at`;
- [ ] GET não criar `rfid_read_events`;
- [ ] software não chamar POST neste requisito.

---

# 109. Ordem obrigatória de implementação

Executar a migração nesta ordem:

    1. analisar fluxo atual

    2. localizar contrato antigo

    3. localizar lookup SQLite

    4. revisar cliente Backend RF015

    5. implementar modelo do novo contrato

    6. implementar get_rfid_record(epc)

    7. implementar parsing/validação

    8. criar testes do cliente

    9. integrar ao processamento RFID

    10. testar EPC encontrado

    11. testar EPC não encontrado

    12. testar deduplicação

    13. testar falhas técnicas

    14. validar tabela e contador

    15. confirmar ausência de POST

    16. remover lookup SQLite do caminho operacional

    17. desativar sincronização antiga quando não houver mais dependência

    18. revisar diff

    19. executar regressão completa

Não remover primeiro o fluxo atual para depois tentar implementar a API.

---

# 110. Regra definitiva após RF016

Após a conclusão:

    EPC
     │
     ▼
    GET /api/v1/rfid_records/:epc
     │
     ├── 200 + found true
     │       │
     │       ▼
     │    Registro válido
     │       │
     │       ▼
     │    Mostrar na tabela
     │
     ├── 404 + epc_not_found
     │       │
     │       ▼
     │     Ignorar
     │
     └── erro técnico
             │
             ▼
        tratar como falha

Nunca:

    EPC
     ↓
    SQLite

Nunca:

    EPC
     ↓
    Power Automate

---

# 111. Preparação para RF017

O resultado deste RF deve permitir que o próximo requisito implemente:

    EPC validado
         │
         ▼
    POST /api/v1/rfid_reads
         │
         ▼
    Backend
         │
         ├── status = lido
         ├── first_read_at
         ├── last_read_at
         ├── read_count
         └── rfid_read_events

Porém essa operação NÃO deve ser antecipada neste requisito.

---

# 112. Definição de pronto

Antes de declarar RF016 concluído, o Codex deve:

1. revisar o diff completo;
2. confirmar alterações apenas no escopo;
3. executar testes unitários;
4. executar testes de qualidade configurados;
5. testar contrato 200;
6. testar contrato 404;
7. testar timeout;
8. testar 5xx;
9. testar JSON inválido;
10. testar EPC normalizado;
11. testar EPC duplicado;
12. testar `tag = null`;
13. testar `status = pendente`;
14. testar `status = lido`;
15. testar `read_count`;
16. testar mapeamento `destinatario → Cliente`;
17. testar mapeamento `notafiscal → Nota fiscal`;
18. confirmar preservação de zeros em `pedido`;
19. confirmar ausência de consulta SQLite;
20. confirmar ausência de Power Automate;
21. confirmar ausência de POST;
22. confirmar que GET não modifica o registro;
23. testar tabela;
24. testar contador;
25. testar status Sistema/Base de dados;
26. executar regressão RF012;
27. validar em Windows;
28. confirmar que o software opera com o novo contrato sem depender do JSON antigo.

---

# 113. Relatório final obrigatório

Ao concluir, apresentar:

- fluxo anterior de consulta;
- fluxo novo;
- arquivos alterados;
- cliente Backend utilizado;
- método criado para consulta EPC;
- modelo interno criado/adaptado;
- campos do novo contrato;
- locais onde `sucesso` foi removido;
- locais onde `cliente` foi substituído;
- locais onde `notaFiscal` foi substituído;
- mapeamento final da tabela;
- tratamento de `found`;
- tratamento de 404;
- tratamento de timeout;
- tratamento de 5xx;
- tratamento de resposta inválida;
- funcionamento da deduplicação;
- confirmação de uma consulta por EPC por sessão;
- confirmação de que SQLite não participa mais do lookup;
- componentes SQLite removidos/desativados;
- componentes de sincronização removidos/desativados;
- código legado mantido e motivo;
- confirmação de ausência de fallback;
- confirmação de ausência de POST;
- testes executados;
- resultado dos testes;
- testes manuais realizados;
- limitações encontradas;
- confirmação de funcionamento no Windows.

---

# 114. Resultado final esperado

Ao final do RF016:

    ┌─────────────────────────────────────────────┐
    │               SOFTWARE RFID                 │
    │                                             │
    │ Zebra FX9600                                │
    │      │                                      │
    │      ▼                                      │
    │     EPC                                     │
    │      │                                      │
    │      ▼                                      │
    │ Normalização + Deduplicação                 │
    │      │                                      │
    │      ▼                                      │
    │ Backend RFID Client                         │
    └──────┬──────────────────────────────────────┘
           │
           │ GET /api/v1/rfid_records/:epc
           ▼
    ┌──────────────────┐
    │    Rails API     │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │    PostgreSQL    │
    │   rfid_records   │
    └────────┬─────────┘
             │
             ▼
    {
        "found": true,
        "data": {
            "destinatario": "...",
            "notafiscal": "...",
            "volume": "...",
            "pedido": "...",
            "doca": "...",
            "epc": "...",
            "status": "...",
            ...
        }
    }
             │
             ▼
    ┌─────────────────────────────────────────────┐
    │               SOFTWARE RFID                 │
    │                                             │
    │ Status       ← status                       │
    │ Cliente      ← destinatario                 │
    │ Nota fiscal  ← notafiscal                   │
    │ Volume       ← volume                       │
    │ Pedido       ← pedido                       │
    │ Doca         ← doca                         │
    └─────────────────────────────────────────────┘

A partir deste requisito, o software RFID deixa definitivamente de validar EPC utilizando a base sincronizada local e passa a utilizar o Backend Rails/PostgreSQL como fonte operacional da consulta.

O RF017 será responsável exclusivamente pelo próximo passo:

    EPC encontrado e validado
            ↓
    POST /api/v1/rfid_reads
            ↓
    registrar passagem/
            ↓
    atualizar status
            ↓
    atualizar contador
            ↓
    criar histórico