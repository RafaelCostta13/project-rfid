# RF015 — Configuração e Comunicação com Backend RFID

## 1. Objetivo

Integrar o software RFID ao novo Backend RFID desenvolvido em Rails, criando a infraestrutura de comunicação HTTP que será utilizada pelos próximos requisitos para:

- consultar EPCs no servidor;
- validar registros RFID;
- registrar passagens RFID;
- consultar a disponibilidade da API;
- consultar a disponibilidade do PostgreSQL através da própria API.

Neste RF015 ainda NÃO deve ser alterado o fluxo operacional de consulta do EPC.

A substituição da consulta local pelo endpoint:

    GET /api/v1/rfid_records/:epc

será realizada no RF016.

O registro das passagens através de:

    POST /api/v1/rfid_reads

será realizado no RF017.

O objetivo deste requisito é preparar e validar toda a infraestrutura necessária para que essas próximas alterações possam ser realizadas de forma segura.

---

# 2. Mudança arquitetural

A arquitetura do sistema está sendo alterada.

A arquitetura anterior utilizava:

    SharePoint
        │
        ▼
    Power Automate
        │
        ▼
    Sincronização
        │
        ▼
    SQLite local
        │
        ▼
    Consulta por EPC

Essa arquitetura será descontinuada.

A nova arquitetura será:

    Software RFID
         │
         ▼
    Backend RFID Rails
         │
         ▼
    PostgreSQL

Posteriormente:

    Zebra FX9600
         │
         ▼
        EPC
         │
         ▼
    Backend RFID
         │
         ▼
    PostgreSQL

O software RFID deixará de possuir responsabilidade pela sincronização da base.

---

# 3. Backend como nova fonte operacional

O Backend RFID passa a ser a camada responsável pelo acesso aos dados operacionais.

Arquitetura:

    Software RFID
         │
         │ HTTP
         ▼
    API Rails
         │
         ▼
    PostgreSQL

O software desktop não deve acessar diretamente o PostgreSQL.

Toda comunicação deve acontecer através da API Rails.

---

# 4. Base URL

A aplicação deve possuir uma configuração centralizada para:

    Backend Base URL

Utilizar como valor inicial/configurável a Base URL do ambiente Backend RFID/ngrok atualmente informada para o projeto.

Não espalhar a Base URL pelo código.

Não hardcodar a URL diretamente:

- no serviço de RFID;
- na tela Start;
- no serviço de status;
- no processamento de EPC;
- em múltiplos arquivos.

Deve existir uma única fonte de configuração.

---

# 5. Configuração do Backend RFID

Adicionar na tela de Configurações existente uma seção:

    Backend RFID

Contendo:

    URL do Backend
    [________________________________]

    [ Testar conexão ]

Exemplo conceitual:

    Backend RFID
    ─────────────────────────────────

    URL do Backend
    [ endereço configurado do servidor ]

    [ Testar conexão ]

Adaptar ao layout real da aplicação.

Não criar uma nova tela exclusivamente para o Backend.

---

# 6. Persistência da URL

A URL do Backend deve utilizar o mesmo mecanismo de persistência das configurações existentes.

Antes de implementar, analisar:

- arquivo atual de configuração;
- serviço de configuração;
- configuração do Zebra;
- configuração da Waveshare;
- configuração da Doca;
- configuração dos endpoints atualmente existentes.

Não criar um segundo sistema de configuração sem necessidade.

---

# 7. Alteração futura da URL

A Base URL poderá mudar.

O ambiente atual utiliza ngrok, mas futuramente poderá utilizar:

- outro endereço ngrok;
- IP interno;
- DNS interno;
- domínio corporativo;
- servidor definitivo.

Portanto, a aplicação não pode depender de uma URL fixa no código.

Exemplo conceitual:

    hoje:

    Backend Base URL
        ↓
    ambiente ngrok

    futuro:

    Backend Base URL
        ↓
    ambiente definitivo

Nenhuma alteração de código deve ser necessária para essa troca.

---

# 8. Normalização da Base URL

O serviço deve tratar corretamente a montagem das URLs.

Exemplo:

    Base URL configurada

            +

    /api/v1/health

Não criar problemas como:

    //api/v1/health

ou:

    api/v1api/v1/health

Centralizar a montagem dos endpoints.

---

# 9. Endpoints conhecidos

O Backend RFID atualmente disponibiliza:

    GET /api/v1/health

Finalidade:

    verificar servidor Rails
    +
    conexão com PostgreSQL


    GET /api/v1/rfid_records/:epc

Finalidade:

    consultar registro RFID pelo EPC
    sem registrar leitura


    POST /api/v1/rfid_reads

Finalidade:

    registrar passagem RFID
    atualizar contador
    atualizar estado
    registrar histórico

Neste RF015 implementar somente a infraestrutura comum e a integração operacional com:

    GET /api/v1/health

Não integrar ainda a leitura RFID com os outros dois endpoints.

---

# 10. Responsabilidade do GET /health

Utilizar:

    GET /api/v1/health

como fonte oficial do estado do Backend RFID.

Esse endpoint verifica:

    Rails
      +
    PostgreSQL

Portanto, ele substituirá as verificações relacionadas ao antigo mecanismo de sincronização.

---

# 11. Resposta saudável

O Backend pode responder conceitualmente:

    HTTP 200

    {
        "status": "ok",
        "database": "ok"
    }

Interpretar:

    status = ok

como:

    Backend Rails/API operacional

e:

    database = ok

como:

    PostgreSQL operacional

---

# 12. Resposta com banco indisponível

O Backend pode responder conceitualmente:

    HTTP 503

    {
        "status": "error",
        "database": "unavailable"
    }

Interpretar:

    Sistema/API = NOK

e:

    Base de dados = NOK

Não considerar HTTP 503 como uma resposta saudável apenas porque o servidor respondeu HTTP.

---

# 13. Estados atuais da interface

Atualmente existem indicadores relacionados a:

    RFID

    Comandos

    Base de dados

    Sincronização

Também devem ser preservados outros indicadores já existentes no projeto, como Internet, caso estejam atualmente presentes na interface.

Não remover indicadores não relacionados sem necessidade.

---

# 14. Remover status Sincronização

O indicador:

    Sincronização

deve ser removido.

Motivo:

A aplicação não realizará mais sincronização da base SharePoint/Power Automate para SQLite.

Portanto, esse conceito deixou de representar uma função da arquitetura atual.

Remover da interface:

    Sincronização

Também remover sua atualização automática caso ela tenha sido implementada especificamente para o fluxo antigo.

---

# 15. Não remover código indiscriminadamente

A remoção do indicador Sincronização não autoriza apagar indiscriminadamente serviços compartilhados.

Antes de remover código, verificar se ele é utilizado por:

- cliente HTTP;
- configurações;
- status gerais;
- tratamento de erros;
- workers;
- outros componentes.

Remover somente código comprovadamente obsoleto e exclusivo da sincronização antiga.

---

# 16. Novo status Sistema

No lugar do antigo conceito de Sincronização, adicionar/utilizar o status:

    Sistema

Esse indicador representará o estado da API Rails.

A informação deve vir diretamente do:

    GET /api/v1/health

Campo:

    status

Exemplo:

    {
        "status": "ok",
        "database": "ok"
    }

Resultado:

    Sistema = OK

---

# 17. Status Base de dados

Preservar o indicador:

    Base de dados

Porém seu significado deve mudar.

Ele não representa mais:

    SQLite local

nem:

    sincronização SharePoint

A partir deste requisito ele representa:

    PostgreSQL do Backend RFID

A informação deve vir do campo:

    database

retornado pelo:

    GET /api/v1/health

---

# 18. Mapeamento do health

Mapeamento principal:

    GET /api/v1/health

Resposta:

    {
        "status": "ok",
        "database": "ok"
    }

Interface:

    Sistema         ● OK
    Base de dados   ● OK

---

# 19. Exemplo de erro

Resposta:

    {
        "status": "error",
        "database": "unavailable"
    }

Interface:

    Sistema         ● NOK
    Base de dados   ● NOK

---

# 20. Estados visuais finais

Após esta alteração, os indicadores relacionados à nova arquitetura devem incluir:

    RFID
    Comandos
    Sistema
    Base de dados

Se o indicador:

    Internet

já existir atualmente na aplicação, preservá-lo.

Portanto, não remover Internet apenas porque não foi explicitamente citado neste requisito.

O indicador removido especificamente é:

    Sincronização

---

# 21. Responsabilidade dos indicadores

Definir claramente:

    RFID
        ↓
    conexão/disponibilidade do Zebra FX9600


    Comandos
        ↓
    comunicação com Waveshare


    Sistema
        ↓
    disponibilidade do Backend Rails/API


    Base de dados
        ↓
    disponibilidade do PostgreSQL
    informada pelo Backend


    Internet
        ↓
    conectividade geral
    caso esse indicador já exista

Não misturar essas responsabilidades.

---

# 22. Uma única chamada para Sistema e Base de dados

Não realizar duas requisições separadas para obter:

    Sistema

e:

    Base de dados

Uma única chamada:

    GET /api/v1/health

deve fornecer as duas informações.

Exemplo:

    GET /api/v1/health
            │
            ▼
    {
        status,
        database
    }
       │       │
       │       └──────────► Base de dados
       │
       └──────────────────► Sistema

---

# 23. Cliente HTTP centralizado

Criar ou adaptar um cliente centralizado para comunicação com o Backend RFID.

Não espalhar chamadas HTTP diretamente pelas telas.

Arquitetura conceitual:

    UI
     │
     ▼
    Status Controller
     │
     ▼
    Backend RFID Service
     │
     ▼
    HTTP Client
     │
     ▼
    Rails API

Adaptar aos padrões reais encontrados no projeto.

---

# 24. Preparação para RF016 e RF017

O cliente criado neste requisito deve ser estruturado para futuramente suportar:

    health()

    get_rfid_record(epc)

    create_rfid_read(epc)

Os nomes são apenas conceituais.

Não implementar prematuramente regras de negócio dos RF016/RF017.

Porém evitar criar uma implementação exclusiva de health que depois precise ser completamente reescrita.

---

# 25. Não acessar PostgreSQL diretamente

É proibido implementar:

    Software Python
          │
          ▼
    conexão PostgreSQL direta

O software desktop não deve possuir:

- usuário PostgreSQL;
- senha PostgreSQL;
- string de conexão PostgreSQL;
- driver PostgreSQL apenas para essa integração.

A arquitetura correta é:

    Python
      ↓
    HTTP
      ↓
    Rails
      ↓
    PostgreSQL

---

# 26. Botão Testar conexão

Na configuração Backend RFID, o botão:

    Testar conexão

deve utilizar:

    GET /api/v1/health

O teste deve utilizar o valor atualmente preenchido no campo da tela.

Isso permite testar uma nova URL antes de salvar.

---

# 27. Testar sem salvar

Exemplo:

URL salva:

    servidor A

Usuário digita:

    servidor B

e clica:

    Testar conexão

O teste deve utilizar:

    servidor B

sem obrigatoriamente salvar a configuração.

Isso segue o mesmo conceito utilizado nas demais telas de configuração do projeto.

---

# 28. Resultado do teste

Se receber:

    HTTP 200

e:

    status = ok
    database = ok

apresentar resultado positivo.

Exemplo conceitual:

    Backend conectado com sucesso.
    Sistema: OK
    Base de dados: OK

Adaptar ao padrão visual existente.

---

# 29. Teste com PostgreSQL indisponível

Se receber:

    HTTP 503

com:

    status = error
    database = unavailable

apresentar claramente:

    Sistema: NOK
    Base de dados: NOK

Não apresentar:

    Conexão realizada com sucesso

apenas porque houve resposta HTTP.

---

# 30. Timeout

Todas as requisições ao Backend RFID devem possuir timeout.

O timeout deve ser centralizado.

Reutilizar configuração/padrão existente caso já exista.

Não permitir que uma indisponibilidade do Backend congele a aplicação.

---

# 31. Execução em background

O health check não deve bloquear a thread principal da interface.

Não realizar chamada HTTP bloqueante diretamente no evento da UI.

Reutilizar:

- worker;
- thread;
- executor;
- mecanismo assíncrono;

já utilizado pela aplicação.

---

# 32. Monitoramento periódico

O status do Backend deve ser atualizado periodicamente utilizando:

    GET /api/v1/health

Não realizar polling agressivo.

Antes de definir o intervalo, verificar como os outros status são atualizados.

Preferir integrar o health check ao monitor central existente.

Não criar outro loop infinito independente sem necessidade.

---

# 33. Uma requisição por ciclo de health

Cada ciclo de monitoramento deve executar apenas uma chamada ao endpoint health.

Não fazer:

    GET health para Sistema
    +
    GET health para Base de dados

Usar uma chamada e distribuir o resultado.

---

# 34. Estado inicial

Antes da primeira resposta do Backend, os indicadores não devem apresentar falsamente:

    OK

Utilizar o estado visual já adotado pelo software para:

    Verificando

ou:

    Desconhecido

Exemplo:

    Sistema         ● Verificando
    Base de dados   ● Verificando

---

# 35. Erro de rede

Se ocorrer:

- timeout;
- DNS failure;
- conexão recusada;
- servidor inacessível;
- erro TLS;
- erro HTTP inesperado;

considerar:

    Sistema = NOK

Como não foi possível obter uma resposta confiável sobre o PostgreSQL:

    Base de dados = NOK

ou o equivalente visual de indisponível utilizado pela aplicação.

Não manter um `OK` antigo indefinidamente.

---

# 36. Resposta inválida

Exemplo:

    HTTP 200

mas:

    {
        "foo": "bar"
    }

Isso NÃO é um health válido.

Resultado:

    Sistema = NOK
    Base de dados = NOK

Registrar tecnicamente:

    resposta health inválida

sem gerar crash.

---

# 37. Campo status inválido

Se:

    status != "ok"

não considerar o Sistema operacional.

Não utilizar apenas o HTTP status como critério.

Validar o contrato da resposta.

---

# 38. Campo database inválido

Se:

    database != "ok"

não considerar a Base de dados operacional.

Exemplo:

    database = unavailable

Resultado:

    Base de dados = NOK

---

# 39. Disponibilidade geral

A nova arquitetura depende do Backend para as futuras consultas por EPC.

Portanto, o estado do Backend deve participar da disponibilidade operacional do sistema.

Depois do RF015, conceitualmente:

    system_ready =
        rfid_ok
        AND waveshare_ok
        AND backend_system_ok
        AND backend_database_ok

Se o projeto ainda utilizar `internet_ok` como requisito independente, preservar também essa condição.

Adaptar aos nomes reais encontrados no código.

---

# 40. Não duplicar system_ready

Não implementar uma nova regra diretamente na UI se já existir uma avaliação centralizada.

Atualizar a fonte central de disponibilidade.

Evitar:

    Tela Start calcula status

e:

    serviço calcula outro status

com regras diferentes.

Deve existir uma única regra de disponibilidade.

---

# 41. Sistema OK

Exemplo:

    RFID            OK
    Comandos        OK
    Sistema         OK
    Base de dados   OK

e Internet OK, caso seja requisito existente.

Resultado:

    sistema apto

Preservar a lógica existente do RF012:

    CH1 ON
    CH2 OFF
    CH3 OFF

quando estiver aguardando leitura.

---

# 42. Sistema/API NOK

Exemplo:

    RFID            OK
    Comandos        OK
    Sistema         NOK
    Base de dados   NOK

Resultado:

    sistema não apto

Se Waveshare estiver disponível:

    CH1 OFF
    CH2 OFF
    CH3 ON

Não iniciar novo ciclo automático de RFID.

---

# 43. PostgreSQL NOK

Se:

    Sistema         OK
    Base de dados   NOK

caso o Backend futuramente consiga retornar essa combinação, considerar o sistema operacionalmente não apto.

Motivo:

A futura validação dos EPCs dependerá dos dados do PostgreSQL.

---

# 44. Falha durante operação

Se o Backend se tornar indisponível durante a execução, utilizar a infraestrutura central de status já existente.

Não implementar lógica duplicada diretamente na tela.

Preservar a política de segurança operacional do RF012.

---

# 45. CH1

CH1 continua significando:

    sistema apto

Portanto, para ficar verde, todos os componentes obrigatórios devem estar operacionais.

Após esta migração, isso inclui o Backend/API e sua base PostgreSQL.

---

# 46. CH2

CH2 continua significando exclusivamente:

    leitura RFID em andamento

Não utilizar CH2 para indicar:

- chamada HTTP;
- health check;
- comunicação com API;
- consulta PostgreSQL.

---

# 47. CH3

CH3 continua significando:

    sistema indisponível/erro

Se Backend ou PostgreSQL forem obrigatórios e estiverem NOK:

    CH3 ON

quando a Waveshare estiver disponível para receber o comando.

---

# 48. CH4–CH8

Não alterar:

    CH4
    CH5
    CH6
    CH7
    CH8

neste requisito.

---

# 49. Remoção do conceito de sincronização

O software não deve mais depender operacionalmente de:

    SharePoint → Power Automate → SQLite

Portanto, o RF015 deve preparar a remoção desse conceito.

Entretanto, não apagar indiscriminadamente toda a implementação SQLite neste requisito.

O cutover operacional será realizado nos requisitos seguintes.

---

# 50. SQLite neste RF

O RF015 NÃO deve alterar ainda a forma como o EPC é consultado.

Portanto, neste requisito:

- não substituir consulta por EPC;
- não implementar GET de EPC no fluxo RFID;
- não implementar POST de passagem;
- não remover o lookup atual antes do RF016;
- não realizar mudanças grandes no processamento RFID.

O objetivo é primeiro estabelecer:

    Backend configurado
        +
    comunicação funcionando
        +
    health funcionando
        +
    status funcionando

---

# 51. Sincronização automática antiga

Se atualmente existir um worker/timer responsável exclusivamente por sincronizar a base local, NÃO permitir que ele continue realizando novas sincronizações após a migração arquitetural, desde que sua remoção/desativação possa ser feita com segurança neste RF.

O Codex deve primeiro analisar a implementação.

Se desativá-lo neste RF puder quebrar a consulta operacional ainda utilizada antes do RF016, não fazer uma remoção prematura.

Nesse caso:

- documentar a dependência;
- manter temporariamente o mínimo necessário;
- remover definitivamente no RF016 após o cutover da consulta.

A prioridade é não deixar o software sem base funcional entre RF015 e RF016.

---

# 52. Regra de migração segura

A sequência oficial será:

    RF015
      │
      ├── Backend configurável
      ├── HTTP client
      ├── GET /health
      ├── Sistema
      ├── Base de dados
      └── retirar conceito visual de Sincronização
              │
              ▼
    RF016
      │
      └── GET /rfid_records/:epc
          substitui consulta local
              │
              ▼
    RF017
      │
      └── POST /rfid_reads
          registra passagem
              │
              ▼
    limpeza final
      │
      └── remover componentes SQLite/sync
          comprovadamente obsoletos

Não antecipar etapas sem necessidade.

---

# 53. Preparação do cliente para consulta EPC

O cliente Backend criado no RF015 deve permitir que no RF016 seja adicionada a operação:

    GET /api/v1/rfid_records/:epc

Mas não integrar essa chamada ao Zebra ainda.

O objetivo é evitar retrabalho arquitetural.

---

# 54. Preparação do cliente para registro de passagem

Da mesma forma, o cliente deve permitir que no RF017 seja adicionada:

    POST /api/v1/rfid_reads

Não registrar passagens neste requisito.

---

# 55. Não enviar EPC para /health

O endpoint:

    GET /api/v1/health

não recebe EPC.

Não enviar:

    epc

como query parameter, body ou header sem necessidade.

---

# 56. Health não registra leitura

O health check não deve:

- alterar registro RFID;
- incrementar contador;
- criar histórico;
- alterar status de etiqueta;
- executar qualquer operação de negócio.

Ele serve exclusivamente para monitorar:

    Rails
    +
    PostgreSQL

---

# 57. Doca

Preservar a configuração de Doca existente.

Não remover a Doca neste RF.

Ela continuará fazendo parte da identificação/configuração da estação e poderá ser utilizada nos próximos fluxos conforme contrato do Backend.

Não inventar seu uso no endpoint `/health`, pois esse endpoint não necessita de Doca.

---

# 58. Segurança da URL

A Base URL não deve ser registrada repetidamente em logs completos caso futuramente possua componentes sensíveis.

Para o health:

registrar preferencialmente:

    backend health OK

ou:

    backend health failed: timeout

Não registrar desnecessariamente URLs completas, tokens ou segredos.

---

# 59. Autenticação

Neste momento, os endpoints informados não exigem autenticação adicional.

Portanto, não inventar:

- API Key;
- Bearer Token;
- Basic Auth;
- OAuth;

sem que isso esteja definido no Backend.

Estruturar o cliente de forma organizada para permitir autenticação futura sem reescrever toda a integração.

---

# 60. ngrok

O ambiente atual utiliza ngrok.

O software deve tratar o endereço apenas como uma Base URL HTTP/HTTPS.

Não implementar lógica específica para ngrok dentro das regras de negócio.

Para a aplicação:

    Backend Base URL
        ↓
    HTTP/HTTPS

A aplicação não deve depender de saber se o servidor está:

- local;
- Docker;
- ngrok;
- cloud;
- domínio definitivo.

---

# 61. Tratamento de exceções

O serviço Backend deve tratar de forma controlada:

- timeout;
- connection error;
- DNS error;
- TLS/SSL error;
- HTTP error;
- JSON inválido;
- campos ausentes;
- valores inesperados.

Nenhuma dessas condições deve causar crash da aplicação.

---

# 62. Logging

Registrar eventos úteis como:

    Backend health check OK

    Backend health check failed: timeout

    Backend health invalid response

    Backend database unavailable

Não registrar dados sensíveis.

Evitar gerar log excessivo a cada ciclo saudável caso o monitor execute frequentemente.

Preferir registrar:

- mudança de estado;
- erros;
- recuperação;

conforme padrão existente.

---

# 63. Mudança de estado

Idealmente, evitar logs repetitivos:

    OK
    OK
    OK
    OK
    OK

Preferir:

    Sistema Backend: UNKNOWN → OK

    Sistema Backend: OK → NOK

    Sistema Backend: NOK → OK

Aplicar apenas se compatível com o padrão atual de logging.

---

# 64. Configuração inválida

Se nenhuma Base URL estiver configurada:

    Sistema = NOK
    Base de dados = NOK

Não tentar montar URL inválida.

Na tela de Configurações, apresentar mensagem clara:

    Configure a URL do Backend RFID.

Não assumir silenciosamente endereço padrão em runtime.

---

# 65. Salvar configuração

Ao clicar em Salvar:

1. validar valor;
2. normalizar quando necessário;
3. persistir usando mecanismo existente;
4. atualizar configuração em memória;
5. utilizar nova URL nas próximas verificações.

Não exigir reinicialização da aplicação se a arquitetura atual permitir atualização segura em runtime.

---

# 66. Alteração da URL em runtime

Exemplo:

    URL A
      ↓
    Sistema NOK

Usuário altera para:

    URL B

e salva.

As próximas verificações devem utilizar:

    URL B

Não continuar utilizando URL A armazenada em cache.

---

# 67. Botão Testar conexão e monitor automático

O teste manual e o monitor automático podem utilizar o mesmo serviço:

    BackendHealthService

ou equivalente.

Não duplicar lógica de interpretação da resposta.

Deve existir uma única regra para converter:

    HTTP + JSON

em:

    Sistema
    Base de dados

---

# 68. Estrutura conceitual do resultado health

O serviço pode retornar conceitualmente:

    BackendHealthResult

contendo:

    api_ok
    database_ok
    http_status
    error_type

Não obrigatoriamente utilizar esse nome ou essa estrutura.

Adaptar ao padrão real do projeto.

O importante é não passar lógica HTTP bruta para a UI.

---

# 69. UI

A UI deve receber estados já interpretados.

Evitar:

    if response.status_code == 200
        ...
    if json["database"] == ...

diretamente na tela.

Essa interpretação pertence ao serviço Backend.

---

# 70. Internet

Caso exista atualmente um indicador:

    Internet

preservá-lo.

O status Internet e o status Sistema são diferentes.

Exemplo possível:

    Internet        OK
    Sistema         NOK

Isso significa que o computador possui conectividade, mas o Backend RFID está indisponível.

---

# 71. Base de dados e Sistema são diferentes

Também deve ser possível representar, se o Backend fornecer essa condição:

    Sistema         OK
    Base de dados   NOK

Isso significa:

    Rails responde
        │
        ▼
    PostgreSQL indisponível

Não transformar os dois indicadores em um único booleano internamente se o contrato permite distingui-los.

---

# 72. Fluxo esperado do health

Fluxo:

    Monitor de status
          │
          ▼
    Backend Service
          │
          ▼
    GET /api/v1/health
          │
          ▼
    HTTP + JSON
          │
          ▼
    Validar contrato
          │
          ├──────── status
          │            │
          │            ▼
          │         Sistema
          │
          └──────── database
                       │
                       ▼
                  Base de dados

---

# 73. Fluxo de disponibilidade

Conceitualmente:

    RFID OK?
       │
       ▼
    Comandos OK?
       │
       ▼
    Sistema API OK?
       │
       ▼
    PostgreSQL OK?
       │
       ▼
    demais condições existentes OK?
       │
       ▼
    SISTEMA APTO
       │
       ▼
    CH1 ON

Qualquer dependência operacional obrigatória NOK:

    SISTEMA NÃO APTO
        │
        ▼
    CH3 ON

quando Waveshare estiver disponível.

---

# 74. Não alterar leitura RFID ainda

Neste RF, ao receber um EPC, preservar temporariamente o fluxo operacional existente.

Não implementar ainda:

    EPC
     ↓
    GET /api/v1/rfid_records/:epc

Isso será responsabilidade do RF016.

---

# 75. Não registrar passagem ainda

Também não implementar:

    POST /api/v1/rfid_reads

neste RF.

Isso será responsabilidade do RF017.

---

# 76. Análise obrigatória antes da implementação

Antes de alterar qualquer código, o Codex deve analisar:

1. `AGENTS.md`;
2. estrutura atual do projeto;
3. tela Configurações;
4. mecanismo de persistência das configurações;
5. configuração da Doca;
6. configuração do RFID;
7. configuração Waveshare;
8. tela Start;
9. todos os indicadores de status atuais;
10. indicador RFID;
11. indicador Comandos;
12. indicador Base de dados;
13. indicador Sincronização;
14. indicador Internet, caso exista;
15. serviço central de status;
16. regra atual de `system_ready`;
17. integração CH1/CH2/CH3;
18. cliente HTTP existente;
19. integração Power Automate antiga;
20. sincronização SQLite existente;
21. workers/timers da sincronização;
22. acesso SQLite;
23. processamento atual do EPC;
24. mecanismo de execução em background;
25. tratamento de timeout;
26. logging;
27. testes existentes.

Não implementar antes dessa análise.

---

# 77. Relatório obrigatório antes da implementação

Antes de modificar arquivos, apresentar:

- fluxo atual dos status;
- quais status existem realmente no código;
- onde o status Sincronização está implementado;
- onde Base de dados está implementado;
- significado atual de Base de dados;
- serviço atual de health/status;
- regra atual de `system_ready`;
- como CH1/CH2/CH3 dependem desses estados;
- onde a Base URL será persistida;
- cliente HTTP que será reutilizado/criado;
- arquivos que precisarão ser alterados;
- arquivos que não precisarão ser alterados;
- código de sincronização que pode ser removido agora;
- código de sincronização que precisa permanecer temporariamente até RF016;
- estratégia de timeout;
- estratégia de execução em background;
- intervalo atual/proposto do health;
- impacto esperado nos testes.

Somente depois iniciar a implementação.

---

# 78. Alteração mínima

Este RF deve alterar apenas o necessário para:

- configurar Backend;
- testar Backend;
- monitorar health;
- apresentar Sistema;
- atualizar Base de dados;
- remover o status visual Sincronização;
- atualizar disponibilidade geral.

Não realizar ainda a migração completa da consulta EPC.

---

# 79. Testes unitários — Health OK

Mock:

    HTTP 200

    {
        "status": "ok",
        "database": "ok"
    }

Esperado:

    Sistema = OK
    Base de dados = OK

---

# 80. Teste — Banco indisponível

Mock:

    HTTP 503

    {
        "status": "error",
        "database": "unavailable"
    }

Esperado:

    Sistema = NOK
    Base de dados = NOK

---

# 81. Teste — Timeout

Mock:

    timeout

Esperado:

    Sistema = NOK
    Base de dados = NOK

A UI deve continuar responsiva.

---

# 82. Teste — Connection refused

Mock:

    connection refused

Esperado:

    Sistema = NOK
    Base de dados = NOK

Sem crash.

---

# 83. Teste — JSON inválido

Mock:

    HTTP 200

    resposta não JSON

Esperado:

    Sistema = NOK
    Base de dados = NOK

---

# 84. Teste — contrato inválido

Mock:

    HTTP 200

    {
        "foo": "bar"
    }

Esperado:

    Sistema = NOK
    Base de dados = NOK

---

# 85. Teste — URL não configurada

Configuração:

    Backend URL = vazio

Esperado:

    Sistema = NOK
    Base de dados = NOK

Nenhuma requisição inválida deve ser realizada.

---

# 86. Teste — alteração de URL

Configuração inicial:

    URL A

Alterar para:

    URL B

Esperado:

    próximas verificações utilizam URL B

sem necessidade de reiniciar a aplicação, quando tecnicamente suportado pela arquitetura existente.

---

# 87. Teste — Testar conexão sem salvar

URL persistida:

    URL A

Campo da tela:

    URL B

Clicar:

    Testar conexão

Esperado:

    health check utiliza URL B

sem substituir automaticamente URL A persistida.

---

# 88. Teste — uma chamada por ciclo

Confirmar que um ciclo de monitoramento realiza:

    1 × GET /api/v1/health

e não:

    2 × GET /api/v1/health

para obter Sistema e Base de dados separadamente.

---

# 89. Teste — Sincronização removida

Confirmar que:

    Sincronização

não aparece mais na interface.

Confirmar que a remoção não quebrou:

- RFID;
- Comandos;
- Base de dados;
- Sistema;
- Internet, se existir;
- CH1;
- CH2;
- CH3.

---

# 90. Teste — disponibilidade geral

Estado:

    RFID            OK
    Comandos        OK
    Sistema         OK
    Base de dados   OK

e demais condições existentes OK.

Esperado:

    system_ready = true

    CH1 ON
    CH2 OFF
    CH3 OFF

quando aguardando operação.

---

# 91. Teste — API indisponível

Estado:

    RFID            OK
    Comandos        OK
    Sistema         NOK
    Base de dados   NOK

Esperado:

    system_ready = false

Se Waveshare estiver disponível:

    CH1 OFF
    CH2 OFF
    CH3 ON

---

# 92. Teste de regressão

Confirmar que continuam funcionando:

- Zebra FX9600;
- LLRP;
- Start/Stop;
- DI1;
- DI2;
- timer de 60 segundos;
- CH1;
- CH2;
- CH3;
- Waveshare;
- diagnóstico Waveshare;
- leitura de EPC;
- deduplicação;
- tabela;
- contador;
- configuração da Doca;
- fluxo operacional atualmente utilizado para consulta de EPC até a execução do RF016.

---

# 93. Teste manual no Windows

Executar nativamente no Windows.

Procedimento:

1. iniciar Backend RFID;
2. iniciar túnel/endpoint atual;
3. iniciar software RFID;
4. acessar Configurações;
5. configurar Base URL;
6. clicar Testar conexão;
7. confirmar Sistema OK;
8. confirmar Base de dados OK;
9. salvar;
10. fechar aplicação;
11. abrir novamente;
12. confirmar persistência da URL;
13. confirmar monitor automático;
14. desligar Backend;
15. confirmar Sistema NOK;
16. confirmar Base de dados NOK;
17. iniciar Backend novamente;
18. confirmar recuperação automática;
19. validar CH1/CH3 conforme disponibilidade.

---

# 94. Ambiente oficial

Todo desenvolvimento e validação do software RFID deve continuar sendo realizado em:

    Windows

Não utilizar WSL como ambiente oficial deste projeto.

O fato de o Backend poder estar em Docker não altera o ambiente oficial do software desktop RFID.

---

# 95. Critérios de aceite

O RF015 será considerado aprovado quando:

- [ ] existir configuração para Backend Base URL;
- [ ] URL for persistida;
- [ ] URL for carregada ao iniciar;
- [ ] alteração da URL for aplicada corretamente;
- [ ] existir botão Testar conexão;
- [ ] teste utilizar GET /api/v1/health;
- [ ] teste utilizar valor digitado mesmo antes de salvar;
- [ ] existir cliente HTTP centralizado para Backend RFID;
- [ ] health check possuir timeout;
- [ ] health check não bloquear UI;
- [ ] Sistema utilizar `status` retornado pela API;
- [ ] Base de dados utilizar `database` retornado pela API;
- [ ] uma única chamada health atualizar os dois indicadores;
- [ ] Sincronização for removida da interface;
- [ ] status antigo de sincronização deixar de participar do `system_ready`;
- [ ] Base de dados deixar de representar SQLite;
- [ ] Base de dados passar a representar PostgreSQL;
- [ ] Sistema representar Backend Rails/API;
- [ ] HTTP 200 + status ok + database ok resultar em estados OK;
- [ ] HTTP 503 resultar em estado NOK;
- [ ] timeout resultar em NOK;
- [ ] resposta inválida resultar em NOK;
- [ ] URL vazia resultar em NOK sem crash;
- [ ] disponibilidade geral considerar Backend e PostgreSQL;
- [ ] CH1/CH2/CH3 continuarem respeitando RF012;
- [ ] leitura RFID atual continuar funcionando até RF016;
- [ ] GET de EPC ainda não estiver integrado ao fluxo RFID;
- [ ] POST de passagem ainda não estiver integrado;
- [ ] aplicação continuar funcionando nativamente no Windows;
- [ ] testes existentes continuarem passando.

---

# 96. Fora do escopo

Não implementar neste RF:

- GET operacional de EPC no Backend;
- substituição definitiva do SQLite pelo GET remoto;
- POST de passagem RFID;
- incremento de contador remoto;
- criação de histórico remoto;
- alteração de status RFID no Backend;
- autenticação da API;
- acesso PostgreSQL direto;
- alteração de schema PostgreSQL;
- alteração do Backend Rails;
- alteração dos endpoints;
- alteração da lógica DI1/DI2;
- alteração do timer de 60 segundos;
- alteração do protocolo LLRP;
- alteração da Waveshare;
- alteração de CH4–CH8;
- escrita RFID;
- remoção prematura do mecanismo necessário para manter a consulta EPC funcionando antes do RF016.

---

# 97. Preservar obrigatoriamente

Preservar:

- Zebra FX9600;
- LLRP;
- EPC;
- deduplicação;
- Start/Stop;
- RF012;
- DI1;
- DI2;
- timer de 60 segundos;
- CH1 verde;
- CH2 amarelo;
- CH3 vermelho;
- CH4–CH8;
- Waveshare;
- tela de diagnóstico;
- configuração da Doca;
- configuração RFID;
- configuração Waveshare;
- tabela de resultados;
- contador;
- logs;
- Internet, caso o status já exista;
- fluxo atual de consulta EPC até RF016.

---

# 98. Regra definitiva após RF015

Após este requisito, o monitoramento deve ser:

    Zebra FX9600
         │
         ▼
       RFID


    Waveshare
         │
         ▼
      Comandos


    GET /api/v1/health
         │
         ├──────── status
         │            │
         │            ▼
         │          Sistema
         │
         └──────── database
                      │
                      ▼
                 Base de dados


    Sincronização
         │
         ▼
       REMOVIDO

O conceito de sincronização deixa de fazer parte dos status operacionais do software.

---

# 99. Arquitetura preparada para RF016

Após concluir o RF015:

    Zebra
      │
      ▼
     EPC
      │
      ▼
    fluxo atual temporário

e:

    Backend Service
       │
       ▼
    GET /health
       │
       ▼
    Sistema + Base de dados

No RF016 será realizada a mudança:

    Zebra
      │
      ▼
     EPC
      │
      ▼
    Backend Service
      │
      ▼
    GET /api/v1/rfid_records/:epc
      │
      ▼
    PostgreSQL
      │
      ▼
    Resultado

---

# 100. Arquitetura preparada para RF017

Depois do RF016, o RF017 adicionará:

    EPC válido
       │
       ▼
    POST /api/v1/rfid_reads
       │
       ▼
    Backend
       │
       ├── contador
       ├── status
       └── histórico

Não antecipar essa lógica neste requisito.

---

# 101. Definição de pronto

Antes de declarar o RF015 concluído, o Codex deve:

1. revisar todo o diff;
2. remover alterações fora do escopo;
3. executar testes unitários;
4. executar testes de qualidade configurados pelo projeto;
5. testar configuração da URL;
6. testar persistência;
7. testar alteração em runtime;
8. testar botão Testar conexão;
9. testar health 200;
10. testar health 503;
11. testar timeout;
12. testar conexão recusada;
13. testar JSON inválido;
14. testar contrato inválido;
15. confirmar uma única chamada por ciclo;
16. confirmar Sistema;
17. confirmar Base de dados;
18. confirmar remoção de Sincronização;
19. confirmar `system_ready`;
20. confirmar CH1/CH2/CH3;
21. confirmar que o RFID continua funcionando;
22. confirmar que Waveshare continua funcionando;
23. confirmar que a consulta atual de EPC não foi quebrada antes do RF016;
24. confirmar que GET de EPC não foi antecipado;
25. confirmar que POST de passagem não foi antecipado;
26. confirmar que não existem credenciais PostgreSQL no software;
27. confirmar funcionamento no Windows.

---

# 102. Relatório final obrigatório

Ao finalizar, apresentar:

- arquivos alterados;
- arquivos criados;
- componentes removidos;
- localização da configuração Backend Base URL;
- forma de persistência;
- serviço HTTP criado/reutilizado;
- timeout utilizado;
- frequência do health check;
- interpretação de `status`;
- interpretação de `database`;
- funcionamento do indicador Sistema;
- funcionamento do indicador Base de dados;
- confirmação da remoção de Sincronização;
- alterações realizadas em `system_ready`;
- impacto em CH1/CH2/CH3;
- comportamento com Backend indisponível;
- comportamento com PostgreSQL indisponível;
- comportamento com resposta inválida;
- código antigo de sincronização removido;
- código antigo temporariamente preservado e motivo;
- testes executados;
- resultados;
- limitações encontradas;
- confirmação de que RF016 não foi antecipado;
- confirmação de que RF017 não foi antecipado;
- confirmação de que o fluxo RFID atual permaneceu funcional durante esta etapa.

---

# 103. Resultado esperado do RF015

Ao final deste requisito, o software deve possuir a seguinte infraestrutura:

    ┌────────────────────────────────────────────┐
    │              SOFTWARE RFID                 │
    │                                            │
    │ RFID             ● OK                     │
    │ Comandos         ● OK                     │
    │ Sistema          ● OK                     │
    │ Base de dados    ● OK                     │
    │                                            │
    │ Sincronização → REMOVIDO                   │
    └────────────────────────────────────────────┘
                         │
                         │ GET /api/v1/health
                         ▼
                  ┌───────────────┐
                  │ Backend Rails │
                  │ status = ok   │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │  PostgreSQL   │
                  │ database = ok │
                  └───────────────┘

Essa será a infraestrutura oficial de comunicação entre o software desktop RFID e o novo Backend RFID.

A consulta operacional dos EPCs será migrada para o Backend no RF016 e o registro das passagens será integrado no RF017.