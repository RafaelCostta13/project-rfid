# RF013 — Configuração da Doca e Status da Base de Dados

## 1. Objetivo

Adicionar ao software RFID duas novas funcionalidades de configuração e monitoramento:

1. permitir configurar na tela de **Configurações** qual **Doca** está associada à estação/computador RFID;
2. adicionar ao **Status do sistema** um novo indicador chamado **Base de dados**, responsável por verificar se a fonte remota utilizada pelo sistema está disponível e respondendo corretamente.

A Doca configurada será posteriormente utilizada pelo processo de sincronização da base local.

Este requisito deve preparar a aplicação para essa próxima etapa, porém **não deve implementar ainda SQLite, sincronização incremental ou alteração da consulta operacional dos EPCs**.

---

# 2. Contexto atual

O software atualmente possui:

- Zebra FX9600;
- comunicação RFID via LLRP;
- leitura automática controlada pelos sensores;
- Waveshare Modbus RTU Relay D;
- status de Internet;
- status de RFID;
- status de Comandos/Waveshare;
- tela Start;
- tela de Configurações;
- consulta remota para verificar se um EPC existe;
- integração com Power Automate/SharePoint;
- tabela com os EPCs encontrados;
- contador de EPCs encontrados.

A base utilizada atualmente para verificar se um EPC existe é a mesma fonte de dados que será utilizada posteriormente para atualizar a base SQLite local.

A sincronização será realizada por Doca.

Exemplo conceitual de uma futura requisição de sincronização:

    {
        "doca": "D01",
        "modifiedSince": "2026-10-03T22:10:35Z"
    }

Por esse motivo, cada instalação do software precisa possuir uma **Doca configurada**.

---

# 3. Ambiente oficial do projeto

O ambiente oficial do projeto é:

**Windows**

Todo desenvolvimento, instalação de dependências, criação de ambiente virtual, execução da aplicação, testes automatizados e testes de hardware devem ser realizados nativamente no Windows.

Não utilizar WSL para executar, testar ou validar o projeto.

---

# 4. Escopo do RF013

Implementar neste requisito:

- configuração da Doca;
- persistência da Doca;
- carregamento da Doca ao iniciar a aplicação;
- disponibilização da Doca para os serviços da aplicação;
- novo status `Base de dados`;
- verificação real de disponibilidade da base remota;
- integração do novo status ao Status do sistema;
- integração do novo status à regra de disponibilidade operacional existente.

Não implementar ainda:

- SQLite;
- sincronização completa;
- sincronização incremental;
- UPSERT;
- armazenamento local;
- atualização automática da base;
- alteração da consulta operacional de EPC para SQLite.

Esses itens serão tratados no próximo requisito.

---

# 5. Configuração da Doca

## 5.1 Local

Adicionar a configuração da Doca na **tela de Configurações existente**.

Não criar uma nova tela exclusivamente para essa configuração.

Manter o padrão visual e arquitetural já utilizado pelas configurações atuais.

Exemplo conceitual:

    Configurações

    Reader RFID
    --------------------------------
    [...]

    Waveshare
    --------------------------------
    [...]

    Estação
    --------------------------------
    Doca
    [ D01 ▼ ]

    [ Salvar ]

O desenho acima é apenas conceitual.

Adaptar a implementação ao layout atual do projeto.

Não redesenhar a tela de Configurações sem necessidade.

---

# 6. Campo Doca

Adicionar o campo:

**Doca**

A Doca representa a localização física em que aquela instalação do software RFID está operando.

Exemplos:

    D01
    D02
    D03
    D04
    D05

Preferencialmente utilizar um componente de seleção compatível com o padrão atual da interface.

Exemplo:

    Doca
    [ D01 ▼ ]

Antes de implementar, analisar como as opções configuráveis existentes são armazenadas.

Não espalhar uma lista fixa de Docas por diferentes partes do código.

Caso seja necessário manter uma lista de Docas permitidas, centralizar essa configuração.

---

# 7. Doca como configuração da estação

A Doca deve ser tratada como uma configuração da instalação.

Exemplo:

    ESTAÇÃO RFID 01
          │
          ▼
    Configuração
          │
          ▼
       Doca D01

Outro computador poderá possuir:

    ESTAÇÃO RFID 02
          │
          ▼
    Configuração
          │
          ▼
       Doca D05

Portanto, não utilizar valores fixos como:

    doca = "D01"

espalhados pelo código.

Deve existir uma única fonte de verdade para a Doca configurada.

---

# 8. Persistência da Doca

A Doca selecionada deve ser persistida utilizando o **mesmo mecanismo de configuração já utilizado pelo software**.

Antes da implementação, identificar:

- arquivo atual de configuração;
- formato atual da configuração;
- serviço responsável pelo carregamento;
- serviço responsável pelo salvamento;
- comportamento utilizado pela configuração RFID;
- comportamento utilizado pela configuração Waveshare.

Não criar:

- banco de dados apenas para a configuração da Doca;
- segundo arquivo de configuração sem necessidade;
- segunda fonte de verdade para configurações.

Reutilizar a infraestrutura existente.

---

# 9. Carregamento da Doca

Quando a aplicação iniciar:

1. carregar as configurações existentes;
2. obter a Doca configurada;
3. manter a Doca disponível em memória;
4. apresentar a Doca atual na tela de Configurações;
5. disponibilizar o valor aos serviços que futuramente necessitarem realizar consultas por Doca.

A configuração deve permanecer após:

- fechar o software;
- abrir novamente;
- reiniciar o computador.

Exemplo:

    Doca configurada: D01

---

# 10. Salvamento da Doca

Quando o usuário salvar uma nova Doca:

1. validar o valor;
2. persistir utilizando o mecanismo atual de configuração;
3. atualizar a configuração em memória;
4. disponibilizar imediatamente o novo valor para futuras consultas;
5. manter logs apropriados.

Exemplo:

    Valor anterior:
    D01

    Novo valor:
    D05

As próximas operações dependentes da Doca deverão utilizar:

    D05

Não continuar utilizando `D01` em cache após a alteração.

---

# 11. Doca não configurada

Caso nenhuma Doca tenha sido configurada:

- não assumir automaticamente `D01`;
- não utilizar uma Doca padrão silenciosamente;
- não realizar consultas dependentes de Doca com um valor inventado.

Apresentar informação adequada ao usuário.

Exemplo:

    Configure a Doca desta estação.

A ausência de uma Doca válida deve impedir que a base remota seja considerada completamente operacional quando a consulta utilizada para validação depender da Doca.

---

# 12. Uso futuro da configuração

O próximo requisito utilizará a Doca para sincronizar a base local.

Exemplo futuro:

    {
        "doca": "D01",
        "modifiedSince": "2026-10-03T22:10:35Z"
    }

O valor:

    "doca": "D01"

deverá vir diretamente da configuração implementada neste RF.

Fluxo futuro:

    Configuração
         │
         ▼
      Doca D01
         │
         ▼
    Serviço de sincronização
         │
         ▼
    Power Automate
         │
         ▼
      SharePoint

Não implementar esse processo de sincronização neste RF.

---

# 13. Fonte de dados remota

A fonte utilizada atualmente para validar se um EPC existe deve continuar sendo considerada a fonte oficial dos dados.

A mesma fonte será posteriormente utilizada para alimentar a base SQLite local.

Conceitualmente:

                       SHAREPOINT
                     Fonte oficial
                          │
               ┌──────────┴──────────┐
               │                     │
               ▼                     ▼
        Consulta atual        Sincronização futura
          dos EPCs                da base
               │                     │
               ▼                     ▼
         Software RFID          SQLite local

Neste requisito, não alterar ainda a consulta operacional dos EPCs.

---

# 14. Novo Status — Base de dados

Atualmente o sistema apresenta os seguintes status:

    Internet
    RFID
    Comandos

Adicionar:

    Base de dados

A apresentação conceitual passa a ser:

    Internet        ● OK
    RFID            ● OK
    Comandos        ● OK
    Base de dados   ● OK

Manter o mesmo padrão visual utilizado atualmente pelos demais indicadores.

---

# 15. Significado do status Base de dados

O indicador deve responder à seguinte pergunta:

**A aplicação consegue acessar a fonte remota utilizada para obter os dados dos EPCs e receber uma resposta válida?**

Não considerar:

    Internet = OK

como equivalente a:

    Base de dados = OK

É possível existir:

    Internet        ● OK
    Base de dados   ● NOK

Por exemplo:

- computador possui Internet;
- Power Automate está indisponível;
- endpoint está incorreto;
- endpoint não responde;
- SharePoint está indisponível;
- autenticação falhou;
- ocorreu timeout;
- serviço retornou erro;
- resposta recebida é inválida.

---

# 16. Verificação da Base de dados

O status da base deve ser determinado por uma **requisição real e simples** ao serviço remoto.

Não marcar a base como OK apenas porque:

- existe Internet;
- o DNS responde;
- existe uma URL configurada;
- a requisição foi iniciada;
- uma conexão TCP foi aberta.

Deve existir uma resposta válida do serviço.

Fluxo conceitual:

    Verificar base
         │
         ▼
    Realizar requisição
         │
         ▼
    Serviço respondeu?
         │
       SIM
         │
         ▼
    Resposta válida?
       │       │
      SIM     NÃO
       │       │
       ▼       ▼
      OK      NOK

---

# 17. Reutilização da integração existente

Antes de criar qualquer novo cliente HTTP, analisar a implementação atual.

O projeto já realiza consultas remotas para verificar EPCs.

O Codex deve identificar:

- serviço atual responsável pela consulta;
- cliente HTTP utilizado;
- tratamento de timeout;
- tratamento de erros;
- configuração de URL;
- gerenciamento de credenciais;
- execução em background;
- logs existentes.

Reutilizar a infraestrutura existente sempre que possível.

Não criar uma segunda implementação HTTP sem necessidade.

---

# 18. Endpoint de sincronização

Existe um novo fluxo Power Automate criado para a futura sincronização da base.

Esse fluxo recebe conceitualmente:

    {
        "doca": "D01",
        "modifiedSince": ""
    }

e retorna estrutura semelhante a:

    {
        "success": true,
        "syncUntil": "2026-10-03T22:10:35Z",
        "count": 3,
        "items": [
            ...
        ]
    }

Esse endpoint poderá ser utilizado para verificar a disponibilidade da base caso seja tecnicamente adequado.

Entretanto, neste requisito:

- não salvar `items`;
- não criar SQLite;
- não realizar UPSERT;
- não persistir `syncUntil`;
- não utilizar a resposta para sincronização.

O objetivo neste RF é somente determinar se a fonte remota está disponível.

---

# 19. Doca utilizada na verificação

Se o endpoint utilizado para verificar a base exigir uma Doca, utilizar obrigatoriamente a Doca configurada na aplicação.

Exemplo:

    Configuração

    doca = D01

          │
          ▼

    Teste da base

          │
          ▼

    {
        "doca": "D01",
        "modifiedSince": ""
    }

Não utilizar uma Doca fixa no código.

---

# 20. Evitar requisição pesada para Health Check

O Codex deve analisar se utilizar:

    modifiedSince = ""

provocará uma carga completa de todos os registros da Doca.

Caso provoque, **não utilizar uma carga completa como health check periódico**, pois isso geraria tráfego e processamento desnecessários.

O objetivo do status é somente confirmar que a base está acessível.

Antes da implementação, analisar a forma mais leve de validar:

- endpoint;
- Power Automate;
- acesso à fonte remota;
- resposta válida.

Caso o endpoint atual não possua uma operação leve de health check, documentar essa limitação antes de criar comportamento adicional.

Não realizar repetidamente o download completo da Doca apenas para atualizar o indicador de status.

---

# 21. Base de dados OK

Considerar:

    Base de dados = OK

quando houver evidência real de que o serviço remoto está disponível.

Exemplo conceitual:

    requisição enviada
           │
           ▼
    resposta HTTP válida
           │
           ▼
    estrutura esperada válida
           │
           ▼
    Base de dados = OK

---

# 22. Base de dados NOK

Considerar:

    Base de dados = NOK

em situações como:

- timeout;
- falha de conexão;
- HTTP de erro;
- endpoint indisponível;
- resposta inválida;
- falha de autenticação;
- Power Automate indisponível;
- SharePoint/fonte remota indisponível.

Registrar detalhes técnicos no log.

Na interface, apresentar somente informação operacional.

Exemplo:

    Base de dados   ● NOK

Não exibir:

- stack trace;
- tokens;
- assinatura da URL;
- credenciais;
- detalhes sensíveis do endpoint.

---

# 23. Estado inicial

Enquanto a primeira verificação da base ainda não tiver sido concluída, não apresentar falsamente:

    Base de dados = OK

Utilizar o estado visual já existente no projeto para:

    Verificando

ou:

    Desconhecido

conforme o padrão utilizado pelos demais serviços.

---

# 24. Timeout

A requisição de verificação deve possuir timeout.

Não permitir que:

- Power Automate indisponível;
- SharePoint indisponível;
- falha de Internet;
- problema de DNS;

congelem a aplicação.

Reutilizar o padrão de timeout já existente no cliente HTTP do projeto.

Não introduzir arbitrariamente outro padrão caso já exista uma configuração apropriada.

---

# 25. Execução em background

A verificação da base não deve bloquear a thread principal da interface.

Não executar uma requisição HTTP bloqueante diretamente na UI.

Reutilizar, conforme a arquitetura atual:

- worker;
- thread;
- executor;
- serviço assíncrono;
- mecanismo existente de monitoramento.

A interface deve permanecer responsiva durante:

- teste da base;
- timeout;
- recuperação de conexão;
- falhas remotas.

---

# 26. Atualização periódica

O status da base deve seguir o padrão utilizado atualmente pelos demais indicadores.

Antes de implementar, analisar como são atualizados:

- Internet;
- RFID;
- Comandos.

Se já existir um monitor central de status, integrar a Base de dados a ele.

Não criar outro mecanismo paralelo sem necessidade.

A frequência deve evitar chamadas excessivas ao Power Automate e SharePoint.

Não implementar polling agressivo.

---

# 27. Relação entre Internet e Base de dados

Os dois indicadores devem permanecer independentes.

Exemplo:

    Internet        ● OK
    Base de dados   ● OK

Também deve ser possível:

    Internet        ● OK
    Base de dados   ● NOK

Se:

    Internet = NOK

não realizar chamadas remotas repetitivas sem necessidade.

Quando a Internet recuperar, o sistema poderá realizar novamente a verificação da base.

---

# 28. Status geral do sistema

O RF012 atualmente utiliza:

- Internet;
- RFID;
- Comandos/Waveshare;

para determinar se o sistema está apto.

Após o RF013, adicionar:

- Base de dados.

Portanto:

    system_ready =
        internet_ok
        AND rfid_ok
        AND waveshare_ok
        AND database_ok

Adaptar aos nomes e à arquitetura reais encontrados no projeto.

Não duplicar essa regra diretamente em diferentes telas.

Preferir uma avaliação centralizada de disponibilidade.

---

# 29. Sistema apto

O sistema somente será considerado completamente apto quando:

    Internet        OK
    RFID            OK
    Comandos        OK
    Base de dados   OK

Nesse cenário, preservar o comportamento do RF012:

    Estado = AGUARDANDO / READY

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

CH1 representa a luz verde indicando que o sistema está apto.

---

# 30. Base indisponível

Caso:

    Base de dados = NOK

e a Waveshare continue disponível, o sistema não deve ser considerado apto.

Aplicar a regra operacional existente:

    CH1 = OFF
    CH2 = OFF
    CH3 = ON

O sistema não deve iniciar um novo ciclo automático de leitura enquanto um serviço obrigatório estiver indisponível.

---

# 31. Prioridade da disponibilidade

Preservar a regra estabelecida no RF012:

**Disponibilidade do sistema possui prioridade sobre o estado de leitura.**

A Base de dados passa a fazer parte dessa disponibilidade.

Não criar regras concorrentes diretamente na interface.

---

# 32. CH1, CH2 e CH3

Preservar a semântica atual:

    CH1 = Verde
    Sistema apto

    CH2 = Amarelo
    Leitura RFID em andamento

    CH3 = Vermelho
    Sistema indisponível/erro

Os canais devem continuar mutuamente exclusivos.

Quando um deles estiver ativo, os outros dois devem estar desativados.

Não alterar CH4–CH8 neste requisito.

---

# 33. Comportamento da leitura RFID

Este requisito não deve alterar:

- lógica de DI1;
- lógica de DI2;
- temporizador de 60 segundos;
- Start Inventory;
- Stop Inventory;
- leitura de EPC;
- deduplicação;
- processamento dos EPCs encontrados.

O novo status apenas passa a participar da determinação de disponibilidade do sistema.

---

# 34. Consulta atual de EPC

A consulta operacional atual deve continuar funcionando exatamente como hoje.

Fluxo atual:

    Zebra FX9600
          │
          ▼
         EPC
          │
          ▼
    Consulta remota atual
          │
          ▼
       Encontrado?
          │
          ▼
    Exibir resultado

Não substituir essa consulta por SQLite neste RF.

Essa alteração será feita somente depois que o mecanismo de sincronização e banco local estiver implementado e validado.

---

# 35. Segurança

A URL do Power Automate pode conter informações sensíveis.

Portanto:

- não registrar a URL completa nos logs;
- não exibir URL completa na interface;
- não imprimir assinatura/token no console;
- não incluir credenciais em mensagens de erro;
- preservar o mecanismo atual utilizado para configuração de endpoints e segredos.

A Doca pode ser apresentada normalmente na interface.

---

# 36. Arquitetura esperada

Evitar:

    UI
     │
     ▼
    Requisição HTTP direta

Preferir reutilizar a arquitetura existente:

    UI
     │
     ▼
    Controller / ViewModel
     │
     ▼
    Serviço de Status
     │
     ▼
    Serviço HTTP existente
     │
     ▼
    Power Automate
     │
     ▼
    SharePoint

O desenho é conceitual.

Adaptar à arquitetura real do projeto.

Não criar camadas artificiais caso já exista uma estrutura equivalente.

---

# 37. Análise obrigatória antes da implementação

Antes de alterar qualquer arquivo, o Codex deve analisar:

1. `AGENTS.md`, caso exista;
2. tela de Configurações atual;
3. mecanismo atual de persistência;
4. arquivo/formato atual das configurações;
5. configuração do Zebra;
6. configuração da Waveshare;
7. tela Start;
8. status de Internet;
9. status de RFID;
10. status de Comandos/Waveshare;
11. serviço responsável pelo status geral;
12. regra atual de `system_ready`;
13. integração atual com CH1/CH2/CH3;
14. serviço atual de consulta de EPC;
15. endpoint atualmente utilizado;
16. cliente HTTP existente;
17. tratamento atual de timeout;
18. tratamento atual de erros HTTP;
19. mecanismo atual de execução em background;
20. armazenamento atual de URLs/segredos;
21. workers existentes;
22. cleanup realizado ao fechar a aplicação;
23. testes existentes;
24. novo endpoint de sincronização;
25. possibilidade de utilizar esse endpoint para health check sem realizar download desnecessário de todos os registros da Doca.

Não implementar antes dessa análise.

---

# 38. Relatório obrigatório antes das alterações

Antes da implementação, informar:

- arquivos que precisarão ser alterados;
- arquivos que não precisam ser alterados;
- onde a Doca será persistida;
- como a Doca será carregada;
- como a Doca ficará disponível aos serviços;
- como a lista/opções de Doca será estruturada;
- serviço utilizado para verificar a base;
- endpoint utilizado;
- requisição proposta para health check;
- como evitar download completo da base apenas para health check;
- como será determinado `Base de dados = OK`;
- como será determinado `Base de dados = NOK`;
- frequência prevista da verificação;
- timeout utilizado;
- impacto no status geral;
- impacto em CH1/CH2/CH3;
- estratégia para não bloquear a UI.

Somente depois realizar as alterações mínimas necessárias.

---

# 39. Requisitos não funcionais

A implementação deve:

- preservar a arquitetura existente;
- evitar duplicação;
- manter a UI responsiva;
- não bloquear a thread principal;
- utilizar timeout;
- tratar exceções;
- preservar logs;
- não expor segredos;
- funcionar nativamente no Windows;
- manter compatibilidade com Zebra FX9600;
- manter compatibilidade com Waveshare;
- não alterar o protocolo LLRP;
- não alterar o processamento atual dos EPCs;
- não implementar SQLite neste RF;
- não realizar refatorações amplas sem necessidade.

---

# 40. Testes automatizados — Configuração

Adicionar ou atualizar testes para validar:

### 40.1 Salvar Doca

    Doca selecionada = D01

    Salvar

    Resultado:
    D01 persistida

### 40.2 Carregar Doca

    Configuração persistida = D01

    Reinicializar aplicação

    Resultado:
    Doca apresentada = D01

### 40.3 Alterar Doca

    Doca anterior = D01
    Nova Doca = D05

    Resultado:
    configuração persistida = D05
    configuração em memória = D05

### 40.4 Doca vazia

Validar que o sistema:

- não assume `D01`;
- não realiza consulta dependente de Doca com valor inventado;
- apresenta estado apropriado.

---

# 41. Testes automatizados — Base de dados

Utilizar mock/fake para a camada HTTP.

### Cenário 1

    Requisição válida
    Resposta válida

    Resultado:
    Base de dados = OK

### Cenário 2

    Timeout

    Resultado:
    Base de dados = NOK

### Cenário 3

    HTTP erro

    Resultado:
    Base de dados = NOK

### Cenário 4

    Resposta inválida

    Resultado:
    Base de dados = NOK

### Cenário 5

    Internet = NOK

    Resultado:
    evitar chamadas remotas repetitivas desnecessárias

### Cenário 6

    Internet recuperada

    Resultado:
    nova verificação da base pode ser realizada

---

# 42. Testes automatizados — Status geral

Validar:

    Internet       OK
    RFID           OK
    Comandos       OK
    Base de dados  OK

Resultado:

    Sistema apto
    CH1 ON
    CH2 OFF
    CH3 OFF

Validar:

    Internet       OK
    RFID           OK
    Comandos       OK
    Base de dados  NOK

Resultado:

    Sistema não apto
    CH1 OFF
    CH2 OFF
    CH3 ON

Validar também que CH1/CH2/CH3 permanecem mutuamente exclusivos.

---

# 43. Teste manual — Configuração

No Windows:

1. iniciar aplicação;
2. acessar Configurações;
3. selecionar `D01`;
4. salvar;
5. fechar aplicação;
6. abrir novamente;
7. confirmar que `D01` permanece selecionada;
8. alterar para `D05`;
9. salvar;
10. confirmar que a nova configuração é aplicada.

---

# 44. Teste manual — Base disponível

Condições:

    Internet = OK
    Endpoint = disponível
    Power Automate = disponível
    Fonte remota = disponível

Esperado:

    Base de dados = OK

---

# 45. Teste manual — Base indisponível

Simular indisponibilidade do serviço remoto mantendo Internet disponível.

Esperado:

    Internet        = OK
    Base de dados   = NOK

Isso deve comprovar que os dois indicadores são independentes.

---

# 46. Teste manual — Sistema apto

Com:

    Internet        OK
    RFID            OK
    Comandos        OK
    Base de dados   OK

Esperado:

    Sistema apto

    CH1 ON
    CH2 OFF
    CH3 OFF

---

# 47. Teste manual — Base NOK

Com Waveshare disponível:

    Internet        OK
    RFID            OK
    Comandos        OK
    Base de dados   NOK

Esperado:

    Sistema não apto

    CH1 OFF
    CH2 OFF
    CH3 ON

---

# 48. Critérios de aceite

O RF013 será considerado aprovado quando:

- [ ] existir configuração de Doca na tela de Configurações;
- [ ] a Doca puder ser selecionada/configurada;
- [ ] a Doca for persistida;
- [ ] a Doca for carregada ao iniciar a aplicação;
- [ ] a Doca permanecer após reiniciar o software;
- [ ] alterar a Doca atualizar o valor em memória;
- [ ] não existir Doca fixa espalhada pelo código;
- [ ] o sistema não assumir `D01` quando nenhuma Doca estiver configurada;
- [ ] a Doca configurada estiver disponível para futuras consultas;
- [ ] existir o indicador `Base de dados`;
- [ ] o indicador seguir o padrão visual dos status existentes;
- [ ] uma requisição real for utilizada para determinar disponibilidade;
- [ ] uma resposta válida resultar em `Base de dados = OK`;
- [ ] timeout resultar em `Base de dados = NOK`;
- [ ] erro HTTP resultar em `Base de dados = NOK`;
- [ ] resposta inválida resultar em `Base de dados = NOK`;
- [ ] Internet OK não implicar automaticamente Base de dados OK;
- [ ] a verificação não bloquear a interface;
- [ ] existir timeout;
- [ ] não houver polling agressivo;
- [ ] o health check não baixar desnecessariamente toda a base da Doca;
- [ ] URLs/tokens sensíveis não aparecerem nos logs;
- [ ] Base de dados participar da disponibilidade geral do sistema;
- [ ] Base NOK impedir o sistema de ser considerado apto;
- [ ] CH1/CH2/CH3 permanecerem mutuamente exclusivos;
- [ ] CH4–CH8 não forem alterados;
- [ ] RFID continuar funcionando;
- [ ] Waveshare continuar funcionando;
- [ ] tela de diagnóstico Waveshare continuar funcionando;
- [ ] consulta atual de EPC continuar funcionando;
- [ ] temporizador de 60 segundos continuar funcionando;
- [ ] aplicação continuar funcionando nativamente no Windows;
- [ ] testes existentes continuarem passando.

---

# 49. Fora do escopo

Não implementar neste RF:

- SQLite;
- arquivo `.db`;
- criação de tabelas SQLite;
- tabela de controle de sincronização;
- `last_sync`;
- persistência de `syncUntil`;
- sincronização completa;
- sincronização incremental;
- UPSERT;
- atualização automática da base local;
- atualização manual da base local;
- consulta de EPC no SQLite;
- cache local dos EPCs;
- fallback SQLite/SharePoint;
- remoção da consulta remota atual;
- tratamento de exclusões do SharePoint;
- reconciliação completa;
- histórico de sincronização;
- dashboard de sincronização;
- exportação da base;
- alteração da lista SharePoint;
- alteração do Power Automate sem necessidade;
- alteração do protocolo RFID;
- alteração da lógica DI1/DI2;
- alteração do temporizador de 60 segundos;
- alteração da tela de diagnóstico Waveshare.

Essas funcionalidades serão tratadas no próximo requisito:

**Sincronização da Base e Banco de Dados Local SQLite.**

---

# 50. Preservar obrigatoriamente

Preservar:

- Zebra FX9600;
- LLRP;
- Start/Stop RFID;
- fluxo operacional do RF012;
- DI1;
- DI2;
- temporizador de 60 segundos;
- CH1 verde;
- CH2 amarelo;
- CH3 vermelho;
- CH4–CH8;
- Waveshare;
- tela de diagnóstico;
- consulta remota atual de EPC;
- comportamento atual dos EPCs encontrados;
- tabela atual;
- contador atual;
- integração atual com Power Automate;
- configurações RFID;
- configurações Waveshare;
- logs existentes.

Não realizar refatorações amplas sem necessidade.

---

# 51. Definição de pronto

Após implementar, o Codex deve:

1. revisar o diff completo;
2. remover alterações fora do escopo;
3. executar os testes existentes;
4. executar os testes específicos do RF013;
5. confirmar que não houve regressão no RF012;
6. confirmar que RFID continua funcionando;
7. confirmar que Waveshare continua funcionando;
8. confirmar que a consulta atual de EPC continua funcionando;
9. confirmar que a Doca é persistida;
10. confirmar que a Doca é carregada corretamente;
11. confirmar que a alteração da Doca é aplicada;
12. confirmar que o status da base representa uma verificação real;
13. confirmar que o health check não realiza uma carga completa desnecessária da Doca;
14. confirmar que o novo status participa da disponibilidade geral;
15. confirmar que CH1/CH2/CH3 continuam funcionando conforme RF012;
16. confirmar que nenhuma credencial foi adicionada ao código ou aos logs;
17. confirmar que SQLite e sincronização incremental não foram implementados neste RF.

---

# 52. Relatório final obrigatório

Ao finalizar, apresentar:

- arquivos alterados;
- resumo das alterações;
- configuração de Doca adicionada;
- local onde a Doca é persistida;
- forma como a Doca é carregada;
- forma como a Doca é disponibilizada aos serviços;
- serviço utilizado para verificar a base;
- endpoint utilizado;
- estratégia utilizada para health check;
- estratégia utilizada para evitar download completo da base no health check;
- timeout utilizado;
- frequência de verificação;
- comportamento em caso de timeout;
- comportamento em caso de erro HTTP;
- integração com o Status do sistema;
- integração com `system_ready`;
- impacto em CH1/CH2/CH3;
- testes executados;
- resultados dos testes;
- eventuais limitações encontradas;
- confirmação de que a consulta operacional atual dos EPCs foi preservada;
- confirmação de que SQLite e sincronização incremental ficaram fora deste requisito.