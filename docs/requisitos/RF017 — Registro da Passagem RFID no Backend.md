# RF017 — Registro da Passagem RFID no Backend

## 1. Objetivo

Implementar no software RFID o registro efetivo da passagem de uma etiqueta no Backend RFID.

Após um EPC ser identificado pelo Zebra FX9600 e validado com sucesso através do fluxo implementado no RF016:

    GET /api/v1/rfid_records/:epc

o software deverá registrar a passagem através de:

    POST /api/v1/rfid_reads

enviando:

    {
        "epc": "E280691500005029EEA6A275"
    }

A partir deste requisito, o fluxo completo será:

    Zebra FX9600
          │
          ▼
        EPC lido
          │
          ▼
    normalização
          │
          ▼
    deduplicação da sessão
          │
          ▼
    GET /api/v1/rfid_records/:epc
          │
          ▼
    EPC encontrado?
       │        │
      NÃO      SIM
       │        │
       ▼        ▼
    ignorar   POST /api/v1/rfid_reads
                   │
                   ▼
              Backend Rails
                   │
                   ▼
              PostgreSQL
                   │
             ┌─────┼──────────────┐
             ▼     ▼              ▼
           status read_count    timestamps
                                   │
                                   ▼
                            histórico da leitura
                                   │
                                   ▼
                          resposta para software

O RF016 continua responsável por:

    consultar + validar

O RF017 será responsável por:

    registrar a passagem

---

# 2. Premissa obrigatória

Antes de implementar qualquer alteração, analisar o estado atual do projeto.

O RF016 deve estar implementado e funcional.

Não reimplementar o fluxo de consulta EPC.

Não criar um novo cliente HTTP se o RF015/RF016 já possuir um Backend Client centralizado.

Não modificar componentes que não estejam relacionados ao registro da passagem.

---

# 3. Endpoint

Utilizar:

    POST /api/v1/rfid_reads

A Base URL deve continuar vindo da configuração implementada no RF015.

Exemplo conceitual:

    https://<backend-configurado>/api/v1/rfid_reads

Não hardcodar:

- domínio;
- URL ngrok;
- IP;
- porta;
- endpoint completo.

A URL deve ser construída pelo Backend Client existente.

---

# 4. Payload

O POST deve enviar exclusivamente:

    {
        "epc": "E280691500005029EEA6A275"
    }

Não enviar novamente os dados retornados pelo GET.

Portanto, NÃO enviar:

    destinatario
    notafiscal
    volume
    pedido
    doca
    fornecedor
    tag
    status
    read_count
    first_read_at
    last_read_at
    datahora

O Backend já possui esses dados no PostgreSQL.

---

# 5. EPC utilizado no POST

Utilizar exatamente o mesmo EPC normalizado utilizado pelo RF016.

Normalização:

    strip + uppercase

Exemplo:

    "  e280691500005029eea6a275  "

torna-se:

    "E280691500005029EEA6A275"

O fluxo GET e POST deve utilizar o mesmo EPC normalizado.

Não realizar conversão hexadecimal → ASCII.

Não calcular `tag` a partir do EPC.

---

# 6. Condição obrigatória para executar POST

O POST somente poderá ser executado depois que o RF016 confirmar que o EPC existe.

Condição:

    GET /api/v1/rfid_records/:epc
        ↓
    HTTP 200
        ↓
    found = true
        ↓
    contrato válido
        ↓
    EPC retornado compatível
        ↓
    POST /api/v1/rfid_reads

Se qualquer etapa da validação falhar:

    NÃO executar POST.

---

# 7. EPC não encontrado

Quando o GET retornar:

    HTTP 404

    {
        "found": false,
        "error": "epc_not_found",
        "epc": "..."
    }

o fluxo termina.

Não executar POST.

Preservar a regra existente:

- não adicionar "EPC não encontrado";
- não criar card de não encontrados;
- não incrementar contador;
- não consultar SQLite;
- não consultar Power Automate;
- não gerar erro operacional por um simples EPC inexistente.

---

# 8. Erro técnico no GET

Se o GET falhar por:

    timeout
    connection error
    HTTP 5xx
    JSON inválido
    contrato inválido

não executar POST.

O POST só pode ocorrer após uma validação positiva e confiável do EPC.

---

# 9. Responsabilidade do Backend

O software RFID NÃO deve implementar localmente as regras de atualização da passagem.

O Backend é responsável por:

    status
    first_read_at
    last_read_at
    read_count
    rfid_read_events

O software deve apenas:

    enviar EPC
        ↓
    receber resultado
        ↓
    interpretar resultado
        ↓
    atualizar seu modelo/interface

---

# 10. Estrutura relevante do banco

O Backend utiliza:

    rfid_records

com os campos de controle da leitura:

    epc
    status
    first_read_at
    last_read_at
    read_count

Além dos campos de negócio definidos no RF016.

O histórico é armazenado através de:

    rfid_read_events

com relação conceitual:

    RfidRecord
        1
        │
        ▼
        N
    RfidReadEvent

O software desktop NÃO deve acessar essas tabelas diretamente.

Fluxo obrigatório:

    Software RFID
         ↓
    Rails API
         ↓
    PostgreSQL

---

# 11. Primeira passagem

Para um registro nunca processado anteriormente:

    status = "pendente"
    read_count = 0
    first_read_at = null
    last_read_at = null

o POST deverá fazer com que o Backend registre a primeira passagem.

Resultado esperado no servidor:

    status
        "pendente" → "lido"

    read_count
        0 → 1

    first_read_at
        null → horário da passagem

    last_read_at
        null → horário da passagem

e criação de um evento de histórico:

    duplicate = false

O horário é responsabilidade do Backend.

O software RFID não deve enviar o horário da passagem.

---

# 12. Contrato esperado — primeira passagem

Resposta de sucesso:

    HTTP 200

Estrutura:

    {
        "success": true,
        "epc": "E280691500005029EEA6A275",
        "first_read": true,
        "duplicate": false,
        "status": "lido",
        "read_count": 1,
        "first_read_at": "...",
        "last_read_at": "..."
    }

O Codex deve validar o contrato real existente no Backend/documentação antes de implementar o parser.

Não alterar o Backend para se adaptar ao software desktop.

O software desktop deve consumir o contrato atual da API.

---

# 13. Passagens posteriores

O mesmo EPC pode passar novamente em outra sessão/ciclo RFID.

Exemplo:

    Primeira passagem:

    read_count = 1
    first_read = true
    duplicate = false

Depois, em uma nova passagem física:

    read_count = 2
    first_read = false
    duplicate = true

O Backend deve:

- preservar `first_read_at`;
- atualizar `last_read_at`;
- incrementar `read_count`;
- manter `status = "lido"`;
- criar novo `rfid_read_event`.

---

# 14. Contrato esperado — passagem posterior

Exemplo:

    {
        "success": true,
        "epc": "E280691500005029EEA6A275",
        "first_read": false,
        "duplicate": true,
        "status": "lido",
        "read_count": 2,
        "first_read_at": "...",
        "last_read_at": "..."
    }

Uma resposta:

    success = true
    duplicate = true

é SUCESSO.

`duplicate = true` não representa erro.

Significa apenas que aquele registro já possuía uma passagem anterior registrada no Backend.

---

# 15. Diferença entre deduplicação do software e duplicate do Backend

Esses conceitos não podem ser misturados.

## Deduplicação do software

Evita que o Zebra registre repetidamente a mesma etiqueta durante a mesma sessão/ciclo.

Exemplo:

    Zebra:
        EPC A
        EPC A
        EPC A
        EPC A

Resultado:

    1 GET
    1 POST

## Duplicate do Backend

Indica que o EPC já teve uma passagem registrada anteriormente.

Exemplo:

    Sessão 1
        EPC A
        POST
        duplicate = false
        read_count = 1

    Sessão 2
        EPC A
        POST
        duplicate = true
        read_count = 2

Portanto:

    duplicate = true

não deve bloquear nem invalidar uma passagem legítima de uma nova sessão.

---

# 16. Deduplicação da sessão

Preservar obrigatoriamente a deduplicação já existente no software RFID.

O usuário já definiu que o software não deve processar repetidamente a mesma etiqueta dentro da mesma sessão/ciclo.

Durante uma sessão:

    EPC A
    EPC A
    EPC A

deve resultar em:

    1 consulta GET
    +
    1 registro POST

Nunca:

    3 POSTs

Cada POST representa uma passagem no Backend e incrementa o histórico.

---

# 17. EPC em processamento

Existe uma condição importante de concorrência.

O Zebra pode ler:

    EPC A

e, enquanto GET/POST ainda estão em processamento, ler:

    EPC A

novamente.

Portanto, o EPC deve ser protegido desde o início do processamento.

Fluxo conceitual:

    EPC recebido
        │
        ▼
    verificar deduplicação
        │
        ▼
    marcar IN_FLIGHT
        │
        ▼
    GET
        │
        ▼
    POST
        │
        ▼
    sucesso
        │
        ▼
    marcar PROCESSADO

Não é obrigatório utilizar exatamente os nomes:

    IN_FLIGHT
    PROCESSADO

mas deve existir mecanismo equivalente.

---

# 18. Proibição de POST concorrente

Enquanto um EPC estiver sendo processado:

    EPC A → GET/POST em andamento

uma nova leitura:

    EPC A

não pode iniciar outro:

    GET
    +
    POST

paralelo.

Isso poderia incrementar o Backend duas vezes para uma única passagem física.

---

# 19. Fluxo completo do processamento

Implementar conceitualmente:

    EPC recebido
        │
        ▼
    normalizar
        │
        ▼
    EPC válido?
      │       │
     NÃO     SIM
      │       │
      ▼       ▼
    ignorar  já processado ou IN_FLIGHT?
                │
           ┌────┴────┐
           │         │
          SIM       NÃO
           │         │
           ▼         ▼
        ignorar    marcar IN_FLIGHT
                         │
                         ▼
                        GET
                         │
                  ┌──────┴──────┐
                  │             │
              encontrado     não encontrado
                  │             │
                  ▼             ▼
                 POST        finalizar
                  │          sem POST
             ┌────┴────┐
             │         │
          sucesso     falha
             │         │
             ▼         ▼
        PROCESSADO   tratar erro
             │
             ▼
       atualizar modelo/UI

---

# 20. Modelo para resposta do POST

Criar ou adaptar uma representação interna equivalente a:

    RfidReadResult

contendo conceitualmente:

    success
    epc
    first_read
    duplicate
    status
    read_count
    first_read_at
    last_read_at

O nome real deve seguir a arquitetura atual do projeto.

Não criar dicionários soltos sendo interpretados diretamente pela UI.

---

# 21. Backend Client

Reutilizar o Backend Client criado nos RF015/RF016.

Adicionar conceitualmente:

    create_rfid_read(epc)

ou nome equivalente seguindo o padrão existente.

Arquitetura esperada:

    RFID Processing Service
             │
             ▼
      Backend RFID Client
             │
             ├── health()
             │
             ├── get_rfid_record(epc)
             │
             └── create_rfid_read(epc)

Não criar outro cliente HTTP.

---

# 22. Separação de responsabilidades

A UI não deve executar:

    requests.post(...)

O callback LLRP também não deve possuir diretamente:

    requests.post(...)

Fluxo preferido:

    Zebra / LLRP
        ↓
    EPC
        ↓
    processamento RFID
        ↓
    worker / executor
        ↓
    Backend Client
        ↓
    Rails API

---

# 23. Execução assíncrona

O POST não pode bloquear:

- thread da UI;
- callback LLRP;
- leitura do Zebra;
- monitoramento Waveshare.

Reutilizar a infraestrutura assíncrona existente no RF016.

Não criar:

    uma thread ilimitada para cada EPC

caso o projeto já utilize fila/executor controlado.

---

# 24. Combinação dos dados GET + POST

O GET continua fornecendo os dados de negócio:

    destinatario
    notafiscal
    volume
    pedido
    doca
    fornecedor
    etc.

O POST fornece o resultado da passagem:

    status
    first_read
    duplicate
    read_count
    first_read_at
    last_read_at

Após sucesso do POST, atualizar o modelo em memória com os valores retornados pelo servidor.

---

# 25. Atualização do status

Exemplo:

GET retorna:

    status = "pendente"

POST retorna:

    status = "lido"

Depois do POST bem-sucedido, o modelo deve possuir:

    status = "lido"

Não manter:

    status = "pendente"

apenas porque esse era o valor retornado pelo GET antes do registro da passagem.

---

# 26. Tabela atual

Preservar a estrutura visual existente:

    Status
    Cliente
    Nota fiscal
    Volume
    Pedido
    Doca

Mapeamento de negócio permanece:

    Cliente
        ← destinatario

    Nota fiscal
        ← notafiscal

    Volume
        ← volume

    Pedido
        ← pedido

    Doca
        ← doca

Depois do POST bem-sucedido:

    Status
        ← status retornado pelo POST

Normalmente:

    lido

Não adicionar novas colunas neste requisito.

---

# 27. Card "EPCs encontrados"

Preservar o significado atual:

    quantidade de EPCs distintos encontrados
    na sessão atual

Esse card NÃO representa:

    read_count

O `read_count` pertence ao histórico do Backend.

Exemplo:

    Backend:
        read_count = 25

O EPC apareceu uma vez na sessão atual.

Resultado:

    EPCs encontrados += 1

Não:

    EPCs encontrados += 25

---

# 28. Momento do registro

Distinguir:

    GET encontrado
        =
    EPC existe no Backend

de:

    POST success = true
        =
    passagem registrada no Backend

O software somente pode considerar a passagem registrada com sucesso depois de:

    HTTP 200
    +
    success = true

no POST.

---

# 29. Não fabricar sucesso

Se o GET funcionar, mas o POST falhar:

    NÃO considerar que a passagem foi registrada.

Não alterar localmente:

    status = "lido"

Não incrementar localmente:

    read_count

Não gerar localmente:

    first_read_at
    last_read_at

O Backend é a autoridade desses dados.

---

# 30. POST — EPC não encontrado

O Backend pode retornar:

    HTTP 404

com:

    {
        "success": false,
        "error": "epc_not_found",
        "epc": "..."
    }

Esse cenário pode ocorrer se:

    GET encontrou
        ↓
    registro foi removido/alterado
        ↓
    POST executou
        ↓
    EPC não existe mais

Nesse caso:

- não considerar passagem registrada;
- não executar fallback;
- não consultar SQLite;
- não consultar Power Automate;
- registrar a inconsistência.

---

# 31. POST — EPC ausente

O Backend pode retornar:

    HTTP 422

quando o EPC estiver ausente/vazio.

Contrato:

    {
        "success": false,
        "error": "epc_required"
    }

Esse erro não deveria ocorrer no fluxo normal porque o EPC já passou pela validação do RF016.

Se ocorrer:

    tratar como erro de integração/cliente.

Não tratar como:

    EPC não encontrado.

---

# 32. Falhas técnicas

Tratar como falha técnica:

    timeout
    connection refused
    DNS failure
    TLS error
    HTTP 500
    HTTP 502
    HTTP 503
    HTTP 504
    JSON inválido
    contrato inesperado

Nenhuma dessas situações pode ser considerada sucesso.

---

# 33. Regra crítica — NÃO fazer retry automático cego

Não realizar retry automático do:

    POST /api/v1/rfid_reads

após uma falha ambígua.

Principalmente:

    timeout
    conexão interrompida
    resposta perdida

Motivo:

o servidor pode ter processado o POST mesmo que o software não tenha recebido a resposta.

---

# 34. Exemplo do problema de retry

Cenário:

    Software
       │
       │ POST EPC A
       ▼
    Backend
       │
       ├── read_count 5 → 6
       ├── atualiza last_read_at
       └── cria histórico
       │
       ▼
    resposta HTTP
       X
       │
       └── conexão perdida

Software recebe:

    timeout

Se o software executar automaticamente:

    POST novamente

o Backend poderá fazer:

    read_count 6 → 7

e criar outro histórico.

Uma única passagem física teria sido registrada duas vezes.

Isso é proibido.

---

# 35. Resultado ambíguo

Quando o software não consegue determinar se o POST chegou a ser processado:

- não repetir automaticamente o POST;
- não afirmar que a passagem foi registrada;
- registrar erro técnico;
- impedir novas leituras repetidas do Zebra de dispararem outro POST para aquele EPC na mesma sessão;
- permitir que o health/status central avalie a disponibilidade da API.

---

# 36. Estado do EPC após timeout do POST

Em caso de timeout ambíguo:

NÃO remover imediatamente o EPC da proteção de deduplicação.

Caso contrário:

    Zebra lê EPC novamente
        ↓
    novo POST
        ↓
    possível duplicidade

Portanto, durante a mesma sessão/ciclo, o EPC deve permanecer protegido contra novo POST automático.

Uma nova sessão física legítima poderá processar novamente o EPC.

---

# 37. Idempotência

O contrato atual não possui:

    idempotency_key

ou:

    passage_id

enviado pelo software.

Não inventar esses campos neste requisito.

Caso o Codex identifique necessidade de retry confiável, documentar como melhoria futura.

Não alterar o Backend neste RF.

---

# 38. first_read

`first_read` deve ser interpretado exclusivamente a partir da resposta do POST.

Não calcular localmente.

Semântica:

    true
        =
    primeira passagem registrada no Backend

    false
        =
    já existia passagem anterior

Não significa:

    primeira leitura da sessão atual.

---

# 39. duplicate

Semântica:

    duplicate = false
        =
    primeira passagem histórica

    duplicate = true
        =
    registro já possuía passagem anterior

`duplicate = true` com:

    success = true

é uma operação bem-sucedida.

Não exibir erro apenas porque:

    duplicate = true.

---

# 40. read_count

O valor oficial é o retornado pelo Backend.

Não fazer:

    read_count += 1

no software.

Usar:

    response.read_count

Isso evita divergência entre cliente e servidor.

---

# 41. first_read_at e last_read_at

O software não deve gerar esses horários.

O Backend é a fonte oficial.

Primeira passagem:

    first_read_at = horário da primeira passagem
    last_read_at  = horário da primeira passagem

Passagens posteriores:

    first_read_at = preservado
    last_read_at  = atualizado

---

# 42. Horário da passagem

Não adicionar ao payload:

    timestamp
    read_at
    datahora

O Backend determina o horário oficial da passagem.

O campo:

    datahora

do `rfid_record` possui outro significado e não deve ser confundido com:

    first_read_at
    last_read_at
    rfid_read_events.read_at

---

# 43. Validação da resposta

Para considerar a passagem confirmada, validar minimamente:

    HTTP 200
    success = true
    epc presente
    epc compatível com o enviado
    status presente
    first_read presente
    duplicate presente
    read_count válido

Interpretar também:

    first_read_at
    last_read_at

conforme contrato.

---

# 44. EPC divergente

Se enviar:

    EPC A

e receber:

    success = true
    epc = EPC B

não considerar a resposta válida silenciosamente.

Não atualizar EPC A com dados de EPC B.

Registrar:

    inconsistência de resposta/contrato.

---

# 45. Integração com status do sistema

Preservar os indicadores implementados anteriormente:

    RFID
    Comandos
    Sistema
    Base de dados

e:

    Internet

caso continue existente.

Não recriar:

    Sincronização.

---

# 46. Falha do POST e health

Uma falha técnica de comunicação com o POST pode ser utilizada como sinal para o mecanismo central solicitar/reutilizar uma verificação:

    GET /api/v1/health

Não criar outro monitor independente.

Não criar nova thread infinita apenas para o POST.

Reutilizar o mecanismo do RF015.

---

# 47. HTTP 404 e HTTP 422 não significam necessariamente Sistema NOK

Uma resposta:

    HTTP 404

ou:

    HTTP 422

demonstra que a API respondeu.

Portanto, não marcar automaticamente:

    Sistema = NOK
    Base de dados = NOK

somente por causa desses códigos.

Erros de infraestrutura devem ser tratados separadamente.

---

# 48. Relés

Preservar:

    CH1 = sistema apto
    CH2 = leitura RFID em andamento
    CH3 = erro/indisponibilidade

O Backend Client NÃO deve controlar relés diretamente.

Não fazer:

    POST falhou
        ↓
    BackendClient.set_relay(CH3)

A cadeia deve continuar:

    Backend Client
         ↓
    resultado
         ↓
    estado central
         ↓
    lógica operacional
         ↓
    Waveshare

---

# 49. CH2

CH2 representa:

    sessão de leitura RFID ativa

Não:

    requisição HTTP em andamento.

Portanto:

    GET concluído

ou:

    POST concluído

não deve individualmente ligar/desligar CH2.

Preservar o comportamento definido no RF012.

---

# 50. RF012

Não alterar:

- DI1;
- DI2;
- sensor de entrada;
- sensor de saída;
- timer de 60 segundos;
- Start;
- Stop;
- CH1;
- CH2;
- CH3;
- CH4–CH8.

Fluxo físico continua:

    DI1 interrompido
        ↓
    leitura RFID inicia
        ↓
    CH2 ON
        ↓
    Zebra lê EPC
        ↓
    RF016 GET
        ↓
    RF017 POST

DI2 ou timeout continuam encerrando a sessão conforme RF012.

---

# 51. Resposta tardia

Pode ocorrer:

    POST iniciado
        ↓
    DI2 encerra leitura
        ↓
    sessão finalizada
        ↓
    resposta POST chega depois

A aplicação deve tratar esse cenário sem:

- crash;
- alterar sessão errada;
- duplicar registro;
- iniciar nova leitura;
- alterar relés incorretamente.

Reutilizar o conceito de:

    session_id
    cycle_id
    generation

caso já exista no projeto.

---

# 52. Não cancelar POST de maneira insegura

Depois que um POST foi enviado, não existe garantia de que cancelar a espera local impeça o Backend de processar a requisição.

Portanto, não implementar:

    cancelar POST
        ↓
    enviar novamente

Isso pode gerar duplicidade.

---

# 53. SQLite

O RF016 removeu o SQLite da validação operacional.

O RF017 não deve reintroduzi-lo.

Não armazenar passagem localmente no SQLite como substituto do Backend.

Não implementar fila offline neste requisito.

---

# 54. Power Automate

Power Automate não participa mais do fluxo operacional.

Não utilizar:

    POST falhou
        ↓
    Power Automate

Não existe fallback.

---

# 55. Fonte de verdade

Após RF017:

    PostgreSQL
        ↓
    Rails API
        ↓
    Software RFID

é a arquitetura oficial.

O software não deve manter contadores de passagem independentes do Backend.

---

# 56. Análise obrigatória antes da implementação

Antes de alterar qualquer arquivo, analisar:

1. `AGENTS.md`;
2. RF012;
3. RF015;
4. RF016;
5. fluxo atual do EPC;
6. Backend Client;
7. método GET do RF016;
8. modelo `RfidRecord`/equivalente do cliente;
9. tabela da tela Start;
10. card EPCs encontrados;
11. deduplicação atual;
12. EPCs em processamento;
13. worker/executor;
14. callback LLRP;
15. session/cycle ID;
16. tratamento de respostas tardias;
17. health check;
18. Sistema;
19. Base de dados;
20. `system_ready`;
21. CH1/CH2/CH3;
22. logging;
23. testes existentes.

Não implementar antes dessa análise.

---

# 57. Relatório obrigatório antes da implementação

Antes de modificar o código, apresentar um relatório curto contendo:

- fluxo atual implementado pelo RF016;
- ponto onde o GET é executado;
- ponto onde um EPC passa a ser considerado encontrado;
- funcionamento atual da deduplicação;
- existência ou não de estado IN_FLIGHT;
- worker/executor utilizado;
- modelo atual de dados;
- momento atual de atualização da tabela;
- momento atual de atualização do contador;
- Backend Client existente;
- estratégia proposta para adicionar o POST;
- estratégia para impedir POST concorrente;
- estratégia para timeout ambíguo;
- tratamento proposto para respostas tardias;
- arquivos que serão alterados;
- testes que serão criados/alterados.

Somente depois iniciar a implementação.

---

# 58. Teste — primeira passagem

Preparar registro:

    status = "pendente"
    read_count = 0
    first_read_at = null
    last_read_at = null

Executar passagem.

Esperado:

    GET
        HTTP 200
        found = true

seguido de:

    POST
    {
        "epc": "<EPC>"
    }

Resposta esperada:

    success = true
    first_read = true
    duplicate = false
    status = "lido"
    read_count = 1
    first_read_at != null
    last_read_at != null

Confirmar no Backend:

    status = lido
    read_count = 1
    histórico criado

---

# 59. Teste — nova passagem em outra sessão

Encerrar a sessão.

Iniciar nova sessão.

Ler novamente o mesmo EPC.

Esperado:

    1 GET
    1 POST

Resposta:

    success = true
    first_read = false
    duplicate = true
    status = "lido"
    read_count = 2

Confirmar:

    first_read_at preservado
    last_read_at atualizado
    novo histórico criado

---

# 60. Teste — várias leituras na mesma sessão

Zebra produz:

    EPC A
    EPC A
    EPC A
    EPC A

Esperado:

    GET = 1
    POST = 1

Confirmar no Backend:

    read_count incrementou somente 1 vez

e:

    somente um evento correspondente foi criado.

---

# 61. Teste — concorrência

Simular:

    EPC A
        ↓
    GET/POST ainda em andamento

e receber novamente:

    EPC A

Esperado:

    segunda leitura ignorada pelo mecanismo IN_FLIGHT/deduplicação.

Não criar segundo POST.

---

# 62. Teste — GET 404

GET retorna:

    HTTP 404
    epc_not_found

Esperado:

    POST = 0

---

# 63. Teste — POST 404

GET retorna encontrado.

POST retorna:

    HTTP 404
    epc_not_found

Esperado:

- não considerar passagem registrada;
- não alterar status local para lido;
- não executar fallback;
- registrar inconsistência.

---

# 64. Teste — POST 422

POST retorna:

    HTTP 422
    epc_required

Esperado:

- erro de integração;
- passagem não registrada;
- nenhum retry automático;
- nenhuma consulta SQLite.

---

# 65. Teste — timeout

Simular timeout após envio do POST.

Esperado:

- não repetir automaticamente;
- não afirmar sucesso;
- EPC continuar protegido contra novos POSTs na mesma sessão;
- UI continuar responsiva;
- erro ser registrado.

---

# 66. Teste — 5xx

Simular:

    HTTP 500

Esperado:

- passagem não confirmada;
- sem retry automático cego;
- sem fallback;
- health pode ser reavaliado;
- aplicação permanece funcional.

---

# 67. Teste — duplicate true

Resposta:

    HTTP 200
    success = true
    first_read = false
    duplicate = true
    read_count = 10

Esperado:

    operação considerada sucesso.

Não gerar erro de duplicidade.

---

# 68. Teste — atualização da tabela

GET:

    status = "pendente"
    destinatario = "CLIENTE A"
    notafiscal = "123456"
    volume = "1/2"
    pedido = "000012345"
    doca = "DOCA 10"

POST:

    success = true
    status = "lido"
    read_count = 1

Resultado final:

    Status       lido
    Cliente      CLIENTE A
    Nota fiscal  123456
    Volume       1/2
    Pedido       000012345
    Doca         DOCA 10

Preservar zeros à esquerda.

---

# 69. Teste — read_count

Backend retorna:

    read_count = 17

Confirmar:

- software aceita 17;
- software não executa `+1`;
- card EPCs encontrados não passa para 17.

---

# 70. Teste — EPC divergente

POST enviado:

    EPC A

Resposta:

    success = true
    epc = EPC B

Esperado:

- detectar inconsistência;
- não atualizar EPC A com dados de EPC B;
- registrar erro.

---

# 71. Teste de regressão

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
- health funciona;
- Sistema funciona;
- Base de dados funciona;
- RF016 GET funciona;
- EPC inexistente continua ignorado;
- tabela funciona;
- contador funciona;
- deduplicação funciona;
- UI permanece responsiva.

---

# 72. Ambiente oficial

Executar desenvolvimento e testes do software RFID exclusivamente em:

    Windows

Não utilizar WSL como ambiente oficial.

O Backend Rails/PostgreSQL pode continuar executando em Docker.

---

# 73. Fora do escopo

Não implementar neste RF:

- alteração do Backend Rails;
- alteração do PostgreSQL;
- migration;
- autenticação;
- idempotency key;
- retry automático do POST;
- fila offline;
- SQLite;
- Power Automate;
- sincronização;
- novas colunas na UI;
- dashboard de histórico;
- consulta de histórico;
- alteração do RF012;
- alteração do LLRP;
- alteração do Zebra;
- alteração da lógica dos sensores;
- alteração do timer;
- alteração CH4–CH8;
- escrita RFID.

---

# 74. Critérios de aceite

- [ ] POST `/api/v1/rfid_reads` implementado;
- [ ] Backend Client existente reutilizado;
- [ ] payload contém somente `epc`;
- [ ] EPC normalizado;
- [ ] POST ocorre somente após GET válido;
- [ ] GET 404 não gera POST;
- [ ] erro no GET não gera POST;
- [ ] primeira passagem retorna `first_read = true`;
- [ ] primeira passagem retorna `duplicate = false`;
- [ ] primeira passagem resulta em `read_count = 1`;
- [ ] status passa para `lido`;
- [ ] nova passagem legítima incrementa `read_count`;
- [ ] nova passagem retorna `first_read = false`;
- [ ] nova passagem retorna `duplicate = true`;
- [ ] `duplicate = true` é tratado como sucesso;
- [ ] `first_read_at` vem do Backend;
- [ ] `last_read_at` vem do Backend;
- [ ] software não gera timestamps;
- [ ] software não incrementa `read_count` localmente;
- [ ] mesma etiqueta gera somente um POST por sessão/ciclo;
- [ ] EPC em processamento não gera POST concorrente;
- [ ] timeout não gera retry automático;
- [ ] 5xx não gera retry automático cego;
- [ ] POST 404 não é considerado sucesso;
- [ ] POST 422 é tratado como erro de integração;
- [ ] EPC divergente é detectado;
- [ ] SQLite não participa;
- [ ] Power Automate não participa;
- [ ] UI não executa HTTP diretamente;
- [ ] callback LLRP não executa POST diretamente;
- [ ] UI permanece responsiva;
- [ ] RF012 permanece funcional;
- [ ] RF015 permanece funcional;
- [ ] RF016 permanece funcional;
- [ ] aplicação validada no Windows.

---

# 75. Ordem de implementação

Executar nesta ordem:

    1. analisar implementação atual

    2. apresentar relatório pré-implementação

    3. revisar contrato real do POST

    4. criar/adaptar modelo RfidReadResult

    5. adicionar POST ao Backend Client

    6. criar testes do Backend Client

    7. integrar POST ao fluxo após GET

    8. implementar proteção IN_FLIGHT

    9. integrar resultado ao modelo

    10. atualizar status da tabela após sucesso

    11. testar primeira passagem

    12. testar nova passagem

    13. testar deduplicação

    14. testar concorrência

    15. testar 404

    16. testar 422

    17. testar timeout

    18. testar 5xx

    19. testar resposta inválida

    20. revisar diff

    21. executar regressão completa

    22. validar no Windows

---

# 76. Definição de pronto

O RF017 somente pode ser considerado concluído quando:

1. um EPC válido for consultado pelo RF016;
2. o software executar exatamente um POST para a passagem;
3. o Backend atualizar `status`;
4. o Backend atualizar `read_count`;
5. o Backend controlar `first_read_at`;
6. o Backend controlar `last_read_at`;
7. o Backend criar o histórico;
8. o software interpretar `first_read`;
9. o software interpretar `duplicate`;
10. a tabela refletir o status retornado;
11. múltiplas leituras do Zebra na mesma sessão não gerarem múltiplos POSTs;
12. uma nova sessão permitir uma nova passagem legítima;
13. timeout não causar retry automático;
14. SQLite não participar do fluxo;
15. Power Automate não participar do fluxo;
16. testes passarem;
17. regressões RF012/RF015/RF016 passarem;
18. funcionamento ser validado no Windows.

---

# 77. Relatório final obrigatório

Ao concluir, o Codex deve apresentar:

- arquivos alterados;
- fluxo anterior;
- fluxo implementado;
- método criado no Backend Client;
- payload utilizado;
- contrato de resposta utilizado;
- modelo interno criado/adaptado;
- funcionamento da primeira passagem;
- funcionamento das passagens posteriores;
- funcionamento de `first_read`;
- funcionamento de `duplicate`;
- funcionamento de `status`;
- funcionamento de `read_count`;
- funcionamento de `first_read_at`;
- funcionamento de `last_read_at`;
- funcionamento da deduplicação;
- proteção contra POST concorrente;
- comportamento em timeout;
- confirmação de ausência de retry automático;
- tratamento de 404;
- tratamento de 422;
- tratamento de 5xx;
- tratamento de EPC divergente;
- comportamento de resposta tardia;
- confirmação de ausência de SQLite;
- confirmação de ausência de Power Automate;
- testes executados;
- resultado dos testes;
- limitações encontradas;
- confirmação de funcionamento no Windows.

---

# 78. Resultado final esperado

Ao final do RF017:

    ┌─────────────────────────────────────────────┐
    │               SOFTWARE RFID                 │
    │                                             │
    │ Zebra FX9600                                │
    │      │                                      │
    │      ▼                                      │
    │     EPC                                     │
    │      │                                      │
    │      ▼                                      │
    │ Normalização                                │
    │      │                                      │
    │      ▼                                      │
    │ Deduplicação / IN_FLIGHT                    │
    └──────┬──────────────────────────────────────┘
           │
           ▼
    GET /api/v1/rfid_records/:epc
           │
           ▼
       found = true
           │
           ▼
    POST /api/v1/rfid_reads
           │
           │
           ▼
    {
        "epc": "E280691500005029EEA6A275"
    }
           │
           ▼
    ┌───────────────────────┐
    │      Rails API        │
    └───────────┬───────────┘
                │
                ▼
    ┌───────────────────────┐
    │      PostgreSQL       │
    │                       │
    │ rfid_records          │
    │   status              │
    │   first_read_at       │
    │   last_read_at        │
    │   read_count          │
    │                       │
    │ rfid_read_events      │
    │   read_at             │
    │   duplicate           │
    └───────────┬───────────┘
                │
                ▼
    {
        "success": true,
        "epc": "...",
        "first_read": true/false,
        "duplicate": true/false,
        "status": "lido",
        "read_count": N,
        "first_read_at": "...",
        "last_read_at": "..."
    }
                │
                ▼
    ┌─────────────────────────────────────────────┐
    │               SOFTWARE RFID                 │
    │                                             │
    │ atualiza modelo                             │
    │ atualiza Status                             │
    │ mantém dados do GET                         │
    │ preserva deduplicação                       │
    └─────────────────────────────────────────────┘

Com o RF017 concluído, a integração operacional com o Backend estará dividida claramente em:

    RF015
        Configuração do Backend
        Health
        Sistema
        Base de dados

                ↓

    RF016
        GET /api/v1/rfid_records/:epc
        Consulta
        Validação
        Dados do registro

                ↓

    RF017
        POST /api/v1/rfid_reads
        Registro da passagem
        Status
        Contador
        Timestamps
        Histórico

A partir desse ponto, o PostgreSQL através da API Rails passa a ser a fonte oficial do estado e do histórico das passagens RFID.