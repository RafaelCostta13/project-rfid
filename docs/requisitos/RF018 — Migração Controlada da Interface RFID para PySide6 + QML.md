# RF018 — Migração Controlada da Interface RFID para PySide6 + QML

**Versão:** 2.0 — Revisão arquitetural
**Categoria:** Arquitetura Desktop / UX/UI
**Prioridade:** Alta
**Sistema operacional:** Windows
**Framework obrigatório:** PySide6 + Qt Quick/QML
**Status:** Planejamento — implementação condicionada à auditoria
**Substitui:** RF018 anterior baseado em Tkinter/CustomTkinter

---

## 1. Objetivo

Substituir a interface gráfica atual do software RFID, desenvolvida em Tkinter/CustomTkinter, por uma nova interface utilizando:

- Python
- PySide6
- Qt Quick
- QML
- Qt Quick Controls
- Qt Quick Layouts

A migração deve resultar em uma aplicação desktop moderna, profissional, responsiva e alinhada à identidade visual da DSV.

A nova interface deve preservar integralmente o funcionamento operacional existente.

### Princípio fundamental

A mudança é da camada de apresentação, não do sistema RFID.

O objetivo NÃO é reescrever o software inteiro.

Arquitetura desejada:

    ┌───────────────────────────────────────────────┐
    │                INTERFACE QML                  │
    │                                               │
    │  Header | Sidebar | Cards | Tabelas | Forms   │
    └───────────────────────┬───────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────────┐
    │             PySide6 — UI Bridge               │
    │                                               │
    │  Signals | Slots | Properties | Models        │
    └───────────────────────┬───────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────────┐
    │          CONTROLLERS / APPLICATION            │
    │                                               │
    │  Estado operacional | Eventos | Coordenação   │
    └───────────────────────┬───────────────────────┘
                            │
              ┌─────────────┼──────────────┐
              │             │              │
              ▼             ▼              ▼
         Zebra FX9600    Waveshare     Backend RFID
              │             │              │
              ▼             ▼              ▼
             LLRP       Modbus RTU      Rails API
                                           │
                                           ▼
                                       PostgreSQL

A interface QML deverá consumir o estado da aplicação e enviar comandos através de uma camada de integração.

A interface NÃO deverá executar diretamente operações de hardware ou HTTP.

---

# 2. Decisão tecnológica

A tecnologia oficial da nova interface será:

    PySide6 + Qt Quick/QML

Não utilizar para a nova interface:

- Tkinter
- CustomTkinter
- PyQt Widgets
- Interfaces HTML embutidas
- Electron
- Flet

### 2.1 Responsabilidades do PySide6

O PySide6 será responsável por:

- Inicialização da aplicação Qt.
- Gerenciamento do event loop.
- Integração entre Python e QML.
- Comunicação entre threads e UI.
- Modelos de dados.
- Eventos e comandos.
- Gerenciamento do ciclo de vida da interface.

### 2.2 Responsabilidades do QML

O QML será responsável por:

- Estrutura visual.
- Layout.
- Componentes gráficos.
- Cores.
- Tipografia.
- Ícones.
- Estados visuais.
- Animações discretas.
- Navegação visual.
- Renderização de tabelas e indicadores.

### 2.3 Responsabilidades do Python existente

Continuarão sob responsabilidade do Python:

- Comunicação LLRP.
- Comunicação Modbus.
- Comunicação HTTP.
- Regras de negócio.
- Validação de EPC.
- Deduplicação.
- Registro de passagens.
- Monitoramento operacional.
- Configurações persistidas.
- Gerenciamento de sessões.
- Controle de sensores e relés.

Não transferir regras operacionais para JavaScript/QML.

---

# 3. Regra crítica — Não migrar tudo de uma vez

A migração deverá ser incremental e reversível.

É proibido:

1. Excluir a interface antiga no início.
2. Substituir todos os arquivos de interface de uma vez.
3. Reescrever os serviços RFID sem necessidade.
4. Alterar a lógica operacional para acomodar a nova interface.
5. Introduzir novas regras de negócio durante a migração.
6. Conectar o protótipo visual diretamente aos equipamentos.
7. Misturar dois event loops gráficos na mesma execução.

### Estratégia obrigatória

    Interface atual
         │
         │ permanece preservada
         │
         ▼
    Nova interface QML
         │
         │ inicialmente simulada
         │
         ▼
    Aprovação visual
         │
         ▼
    Integração com serviços existentes
         │
         ▼
    Testes de regressão
         │
         ▼
    Homologação
         │
         ▼
    Substituição definitiva

A interface anterior somente poderá ser removida depois da homologação da nova.

---

# 4. Fase 0 — Auditoria obrigatória do projeto

**Esta é a primeira atividade que o Codex deve executar.**

Antes de modificar qualquer arquivo, analisar o repositório existente.

## 4.1 Arquitetura atual

Identificar:

- Arquivo de inicialização da aplicação.
- Classe principal da interface.
- Arquivos Tkinter/CustomTkinter.
- Estrutura de telas.
- Estrutura de componentes.
- Gerenciamento de navegação.
- Gerenciamento de estados.
- Configurações.
- Serviços de hardware.
- Serviços HTTP.
- Workers e threads.
- Timers.
- Sistema de logging.
- Testes.
- Empacotamento Windows.

## 4.2 Dependências entre UI e lógica operacional

Identificar especificamente se existem chamadas como:

    root.after(...)
    widget.configure(...)
    widget.insert(...)
    messagebox.showinfo(...)
    mainloop(...)

ou equivalentes.

Verificar quais serviços dependem diretamente desses recursos.

### Problema que devemos evitar

Um serviço operacional não pode depender de um widget Tkinter para continuar funcionando.

Exemplo de acoplamento inadequado:

    RFID Service
        ↓
    Tkinter Widget
        ↓
    Atualização de estado

Arquitetura desejada:

    RFID Service
        ↓
    Evento / Estado
        ↓
    UI Bridge
        ↓
    QML

Se houver dependências diretas, propor uma estratégia para desacoplá-las sem alterar o comportamento funcional.

## 4.3 Inventário das telas

Catalogar todas as telas existentes.

Para cada tela, identificar:

- Nome.
- Finalidade.
- Arquivo de implementação.
- Componentes.
- Eventos.
- Dados consumidos.
- Comandos executados.
- Serviços envolvidos.
- Dependências com Tkinter.
- Riscos de migração.

## 4.4 Inventário dos estados

Mapear os estados utilizados pela aplicação.

Exemplos:

    RFID conectado
    RFID desconectado

    Waveshare conectada
    Waveshare desconectada

    Sistema disponível
    Sistema indisponível

    Banco conectado
    Banco indisponível

    Aguardando leitura
    Leitura em andamento
    Erro operacional

Identificar a fonte real de cada estado.

Não criar estados paralelos apenas para a nova interface.

## 4.5 Relatório da Fase 0

O Codex deverá apresentar:

1. Arquitetura encontrada.
2. Mapa das telas.
3. Mapa das dependências Tkinter.
4. Componentes que podem ser preservados.
5. Componentes que precisam ser substituídos.
6. Riscos de migração.
7. Estratégia de desacoplamento.
8. Estrutura de arquivos proposta.
9. Dependências necessárias.
10. Plano de testes.
11. Estratégia de rollback.
12. Estimativa de complexidade por etapa.

**PONTO DE CONTROLE 1**

Após apresentar esse relatório, interromper a implementação e aguardar aprovação.

Não modificar arquivos durante a Fase 0.

---

# 5. Preservação da interface atual

A composição do layout existente foi aprovada.

Preservar:

- Header superior.
- Sidebar.
- Área principal.
- Cards.
- Indicadores.
- Botões operacionais.
- Tabela de EPCs.
- Tela de configurações.
- Tela de testes Waveshare.

Não reorganizar os componentes.

Não criar uma interface completamente diferente.

A migração deve alterar principalmente:

    Tecnologia
    Aparência
    Componentes
    Tipografia
    Cores
    Interações visuais

e não:

    Fluxos
    Regras
    Funcionalidades
    Estrutura de navegação

Pequenos ajustes de alinhamento, espaçamento e dimensão são permitidos quando melhorarem o acabamento visual.

---

# 6. Fase 1 — Protótipo QML independente

Após aprovação da auditoria, desenvolver um protótipo visual utilizando PySide6 + QML.

### Regra obrigatória

O protótipo NÃO deverá acessar:

- Zebra FX9600.
- Porta serial Waveshare.
- Backend RFID real.
- PostgreSQL.
- Relés.
- Sensores.

Todos os dados serão simulados.

## 6.1 Objetivo do protótipo

Validar:

- Qualidade visual.
- Composição.
- Cores.
- Identidade DSV.
- Tipografia.
- Cards.
- Botões.
- Tabela.
- Indicadores.
- Responsividade.
- Navegação.

Antes de integrar qualquer serviço real.

## 6.2 Tela inicial

Desenvolver primeiro somente a tela Start.

Essa tela deve conter os componentes existentes na aplicação atual.

Utilizar dados simulados para representar:

    RFID: Conectado
    Comandos: Conectado
    Sistema: Disponível
    Base de dados: Conectada

    Estado operacional: Aguardando

    EPCs encontrados: 5

    Tabela: 5 registros simulados

Os dados simulados devem estar claramente separados dos serviços reais.

## 6.3 Estados simulados

O protótipo deve permitir visualizar os seguintes cenários:

### Cenário A — Sistema apto

    RFID: OK
    Comandos: OK
    Sistema: OK
    Base de dados: OK

    Estado: Aguardando

### Cenário B — Leitura em andamento

    RFID: OK
    Comandos: OK

    Estado: Lendo

### Cenário C — Falha

    Sistema: NOK

    Estado: Indisponível

### Cenário D — Verificando

    Sistema: Verificando

    Base de dados: Verificando

### Cenário E — Sem registros

    Tabela vazia

    EPCs encontrados: 0

Esses cenários devem servir exclusivamente para validação visual.

Não executar comandos operacionais.

---

# 7. Direção de design

A nova interface deverá utilizar uma linguagem visual corporativa moderna.

Referência principal:

    imagem.png

Identidade corporativa:

    DSV_Logo.svg

A imagem de referência deve orientar a estética, não a composição das telas.

## 7.1 Características desejadas

- Tema escuro sofisticado.
- Superfícies em grafite e azul-acinzentado.
- Hierarquia visual clara.
- Cards discretos.
- Tabelas modernas.
- Ícones lineares.
- Tipografia limpa.
- Botões bem definidos.
- Bordas suaves.
- Estados de interação consistentes.
- Ausência de efeitos exagerados.

Evitar aparência de:

- Interface Tkinter tradicional.
- Painel industrial antigo.
- Aplicação Windows legada.
- Dashboard excessivamente colorido.
- Página web genérica sem identidade.

## 7.2 Propostas visuais

Antes de implementar o tema definitivo, apresentar duas variações visuais da mesma tela:

### Proposta A — Corporate Dark

- Grafite predominante.
- Azul corporativo nos elementos de navegação.
- Cards escuros.
- Alto contraste.
- Aparência discreta.

### Proposta B — Navy Dark

- Azul-marinho predominante.
- Superfícies em diferentes profundidades.
- Cards em azul-acinzentado.
- Elementos de ação com maior destaque.

Ambas devem preservar exatamente a mesma estrutura funcional.

O Codex deverá recomendar uma das opções e justificar a escolha.

A paleta definitiva dependerá da aprovação visual.

Não considerar as cores do RF018 anterior como obrigatoriamente aprovadas.

---

# 8. Identidade DSV

Utilizar o arquivo oficial:

    DSV_Logo.svg

O logotipo deverá ser exibido no header.

Preservar:

- Proporção.
- Geometria.
- Cores institucionais.
- Área de respiro.
- Legibilidade.

Não recriar a marca manualmente.

Não substituir pelo logotipo da aplicação utilizada como referência visual.

Caso o arquivo SVG possua problemas de estrutura, criar uma cópia corrigida e validar sua renderização.

Utilizar recursos locais ou o sistema de recursos do Qt.

Não depender de URLs externas para carregar o logotipo.

---

# 9. Sistema de design centralizado

Criar uma estrutura de design tokens em QML.

Estrutura conceitual:

    Theme.qml
        │
        ├── Background
        ├── Surface
        ├── Primary
        ├── Success
        ├── Error
        ├── Warning
        ├── Text
        ├── Border
        ├── Spacing
        └── Radius

Utilizar um singleton QML ou mecanismo equivalente adequado à versão do Qt.

Não espalhar códigos hexadecimais por todos os componentes.

Não duplicar definições de fonte.

Não criar estilos independentes para componentes equivalentes.

## 9.1 Cores semânticas

A semântica das cores é obrigatória:

| Estado | Cor |
|---|---|
| Conectado | Verde |
| Disponível | Verde |
| Sucesso | Verde |
| Leitura em andamento | Amarelo |
| Verificando | Amarelo |
| Atenção | Amarelo |
| Desconectado | Vermelho |
| Falha | Vermelho |
| Indisponível | Vermelho |
| Desconhecido | Cinza |
| Ações neutras | Azul |

As cores devem ser acompanhadas de texto ou ícones.

Não depender exclusivamente da cor para comunicar o estado.

## 9.2 Tipografia

Priorizar uma tipografia moderna e compatível com Windows.

Exemplo:

    Segoe UI

Definir estilos para:

    PageTitle
    SectionTitle
    CardTitle
    Body
    Caption
    KPIValue
    TableHeader
    TableCell

Garantir contraste e legibilidade.

---

# 10. Componentes QML reutilizáveis

Criar componentes reutilizáveis para evitar inconsistência visual.

Estrutura sugerida:

    ui/
      qml/
        Main.qml

        theme/
          Theme.qml

        components/
          AppHeader.qml
          AppSidebar.qml
          StatusIndicator.qml
          StatusCard.qml
          MetricCard.qml
          PrimaryButton.qml
          SecondaryButton.qml
          DangerButton.qml
          StyledTextField.qml
          StyledComboBox.qml
          StyledTable.qml
          EmptyState.qml
          LoadingIndicator.qml

        pages/
          StartPage.qml
          SettingsPage.qml
          WaveshareTestPage.qml

        assets/
          branding/
          icons/

A estrutura deve ser adaptada ao repositório real.

Não criar diretórios duplicados caso já exista uma organização apropriada.

## 10.1 Componente StatusIndicator

Propriedades conceituais:

    label
    state
    description

Estados:

    ok
    error
    warning
    checking
    unknown

O componente será responsável somente pela representação visual.

Não deverá executar health check.

## 10.2 Componente StyledTable

Responsável por:

- Cabeçalho.
- Linhas.
- Seleção.
- Scroll.
- Estados vazios.
- Cores de status.
- Apresentação de dados.

Não deverá consultar o Backend.

## 10.3 Botões

Criar estilos para:

    Primary
    Secondary
    Success
    Danger

Preservar os comandos associados aos botões existentes.

---

# 11. Arquitetura de integração Python ↔ QML

Esta seção é obrigatória.

Não conectar diretamente a lógica operacional aos elementos visuais QML.

Criar uma camada de integração equivalente a:

    UI Bridge

Utilizar os recursos do PySide6:

    QObject
    Signal
    Slot
    Property

A nomenclatura final deve seguir o padrão real do projeto.

## 11.1 Comunicação de dados

Fluxo:

    Serviço Python
          │
          ▼
    Estado da aplicação
          │
          ▼
    UI Bridge
          │
          ▼
    Signal / Property
          │
          ▼
    QML

## 11.2 Comunicação de comandos

Fluxo:

    Botão QML
          │
          ▼
    Slot Python
          │
          ▼
    Controller
          │
          ▼
    Serviço existente

Exemplo conceitual:

    Botão "Iniciar Leitura"
          │
          ▼
    uiBridge.requestStart()
          │
          ▼
    Application Controller
          │
          ▼
    Fluxo operacional RF012

O QML não deve decidir diretamente quando iniciar o inventário Zebra.

## 11.3 Estado central

Reutilizar o estado operacional existente.

Se não existir uma estrutura central adequada, propor uma camada mínima de adaptação.

Não criar uma segunda máquina de estados concorrente.

---

# 12. Atualização segura da interface

O Qt possui seu próprio event loop.

As atualizações de objetos QML e modelos visuais devem ocorrer de forma segura na thread apropriada da interface.

### Regras

- Utilizar signals/slots para comunicar eventos entre threads.
- Não modificar objetos QML diretamente a partir de workers.
- Não bloquear o event loop com operações HTTP.
- Não bloquear o event loop com Modbus.
- Não bloquear o event loop com LLRP.
- Não criar uma thread para cada atualização visual.
- Não criar um worker por EPC sem controle de concorrência.

Verificar se os serviços existentes utilizam:

    threading
    queue
    concurrent.futures
    asyncio
    callbacks

Adaptar a integração sem reescrever os serviços desnecessariamente.

---

# 13. Tabela RFID — Modelo de dados Qt

A tabela deverá consumir um modelo Python adequado ao Qt.

Avaliar:

    QAbstractTableModel

ou:

    QAbstractListModel

conforme o componente QML escolhido.

Preferir um modelo apropriado para atualização incremental de registros.

### Estrutura visual preservada

    Status
    Cliente
    Nota fiscal
    Volume
    Pedido
    Doca

Não adicionar colunas.

### Dados do Backend

O modelo deverá continuar utilizando o contrato estabelecido no RF016.

Mapeamento conceitual:

    Cliente       ← destinatario
    Nota fiscal   ← notafiscal
    Volume        ← volume
    Pedido        ← pedido
    Doca          ← doca

O status final deverá respeitar o retorno do registro de passagem do RF017.

### Regras

- Preservar zeros à esquerda.
- Preservar strings.
- Não transformar pedido em número.
- Não alterar EPC.
- Não converter EPC hexadecimal para ASCII.
- Não adicionar EPCs não encontrados.
- Não duplicar linhas.
- Não reconstruir toda a tabela desnecessariamente.
- Preservar responsividade durante atualizações.

O Codex deverá confirmar o contrato JSON real implementado no projeto antes de definir o modelo definitivo.

---

# 14. Preservação do RF012 — Fluxo operacional

A migração visual não poderá alterar a lógica dos sensores e relés.

## 14.1 Sensores

Preservar:

    DI1 = Sensor de entrada
    DI2 = Sensor de saída

Estado normal:

    Feixe livre
        → entrada digital ativa

Passagem de objeto:

    Feixe interrompido
        → entrada digital desativada

## 14.2 Sistema apto

Quando os requisitos operacionais estiverem atendidos:

    CH1 ON
    CH2 OFF
    CH3 OFF

Representação visual:

    Verde
    Sistema apto

## 14.3 Início da leitura

Quando DI1 identificar a interrupção válida do feixe:

    Iniciar leitura RFID
    CH1 OFF
    CH2 ON
    CH3 OFF
    Timer de 60 segundos

Representação visual:

    Amarelo
    Leitura em andamento

## 14.4 Finalização

Quando DI2 identificar a interrupção válida dentro do ciclo:

    Parar leitura RFID
    Cancelar timer
    CH2 OFF
    CH1 ON, se sistema apto

## 14.5 Timeout

Após 60 segundos:

    Parar leitura RFID
    Finalizar ciclo
    Retornar ao estado apto, se possível

## 14.6 Erro

Em indisponibilidade operacional:

    CH3 ON, quando o controlador permitir
    CH1 OFF
    CH2 OFF

Preservar o tratamento existente para perda de comunicação com a Waveshare.

### Regra crítica

O timer operacional de 60 segundos NÃO deve ser transferido para QML.

O QML pode exibir uma contagem regressiva, caso já exista essa funcionalidade.

Mas o controle real do tempo deverá permanecer na camada operacional Python.

A UI não poderá ser a autoridade para iniciar ou encerrar ciclos físicos.

---

# 15. Preservação do RF015 — Backend Health

Preservar:

    GET /api/v1/health

E os indicadores existentes:

    RFID
    Comandos
    Sistema
    Base de dados

Preservar também Internet, caso esteja presente no sistema atual.

Não recriar:

    Sincronização

### Regras

- O QML não executa HTTP.
- O QML não interpreta diretamente JSON do health.
- O serviço Python continua responsável pelo monitoramento.
- A UI Bridge recebe os estados.
- Os indicadores são atualizados visualmente.

Não criar um segundo monitor de health exclusivamente para a interface.

---

# 16. Preservação do RF016 — Consulta EPC

Preservar:

    GET /api/v1/rfid_records/:epc

Fluxo:

    Zebra
      ↓
    EPC
      ↓
    Validação
      ↓
    GET Backend
      ↓
    Registro encontrado

### Regras

- Não alterar normalização.
- Não alterar deduplicação.
- Não alterar tratamento de 404.
- Não consultar SQLite.
- Não utilizar Power Automate.
- Não criar consulta HTTP diretamente em QML.
- Não apresentar EPC inexistente na tabela.

---

# 17. Preservação do RF017 — Registro da passagem

Preservar:

    POST /api/v1/rfid_reads

Payload:

    {
        "epc": "E280691500005029EEA6A275"
    }

### Regras

- POST somente após validação positiva.
- Um POST por EPC aceito no ciclo/sessão.
- Não criar POST adicional por atualização visual.
- Não repetir POST em resposta a re-renderização da tabela.
- Não executar retry automático cego.
- Preservar tratamento de timeout ambíguo.
- Preservar estado IN_FLIGHT ou equivalente.
- Preservar tratamento de respostas tardias.

### Regra crítica

Um evento de atualização visual NÃO pode provocar um novo registro de passagem.

O fluxo correto é:

    RFID
      ↓
    Serviço
      ↓
    Backend
      ↓
    Resultado
      ↓
    Modelo Qt
      ↓
    QML

Nunca:

    QML renderiza linha
      ↓
    POST

---

# 18. Preservação da Waveshare

A nova interface deverá preservar:

    DI1 a DI5
    CH1 a CH8

Na tela de testes:

- Estados reais das entradas.
- Controles manuais dos relés.
- Teste de conexão.
- Conectar/desconectar.
- Mensagens de erro.
- Estados desconhecidos.

### Proibições

- Não alterar endereços Modbus.
- Não alterar baudrate.
- Não alterar configuração serial.
- Não alterar polling sem justificativa.
- Não abrir a mesma COM por dois serviços concorrentes.
- Não criar outra instância independente do controlador.
- Não acionar relés automaticamente ao abrir a tela.
- Não executar testes de hardware durante a inicialização do protótipo.

A UI deve reutilizar o serviço Waveshare existente.

---

# 19. Fase 2 — Integração progressiva

Após aprovação visual do protótipo, integrar os serviços reais.

A integração deverá ocorrer na seguinte ordem.

## Etapa 2.1 — Configurações

Integrar:

- Leitura de configurações.
- Exibição de configurações.
- Salvamento.
- Validação de campos.

Não alterar o formato persistido sem necessidade.

Testar reinicialização da aplicação.

## Etapa 2.2 — Indicadores

Integrar somente a leitura de estados:

    RFID
    Comandos
    Sistema
    Base de dados

Nenhum comando operacional nesta etapa.

## Etapa 2.3 — Tabela RFID

Integrar o modelo de registros existente.

Validar com dados simulados e eventos de teste.

Não iniciar leitura física ainda.

## Etapa 2.4 — Backend

Integrar os serviços existentes:

    health
    get_rfid_record
    create_rfid_read

Não reimplementar os endpoints.

## Etapa 2.5 — Zebra

Integrar:

- Estado de conexão.
- Eventos de EPC.
- Atualização do modelo.
- Start/Stop através do controller existente.

## Etapa 2.6 — Waveshare

Integrar:

- Estado de conexão.
- Estados DI1–DI5.
- Estados CH1–CH8.
- Tela de diagnóstico.

## Etapa 2.7 — Fluxo operacional completo

Validar:

    DI1
      ↓
    Leitura Zebra
      ↓
    GET
      ↓
    POST
      ↓
    Atualização UI
      ↓
    DI2 ou timeout
      ↓
    Finalização

**PONTO DE CONTROLE 2**

Não avançar para a integração com hardware real antes da aprovação do protótipo visual e dos testes com mocks.

---

# 20. Ciclo de vida da aplicação

O Codex deverá revisar cuidadosamente:

- Inicialização.
- Carregamento de configurações.
- Inicialização de serviços.
- Conexão de sinais.
- Inicialização da UI.
- Fechamento da janela.
- Parada de workers.
- Cancelamento de timers.
- Desconexão RFID.
- Liberação da porta COM.
- Encerramento de serviços HTTP.

### Regra crítica

Fechar a janela não pode deixar:

- Inventário RFID executando indevidamente.
- Thread órfã.
- Porta COM bloqueada.
- Timer operacional ativo.
- Processo Python em background sem necessidade.

O encerramento deverá reutilizar o procedimento seguro existente.

Não inventar um estado físico seguro para os relés sem consultar as regras atuais.

---

# 21. Execução paralela durante a migração

A versão antiga deverá continuar disponível durante o desenvolvimento.

Entretanto:

**Não executar simultaneamente as duas interfaces controlando os mesmos equipamentos.**

Isso poderia gerar:

- Duas conexões ao Zebra.
- Disputa pela porta COM.
- Duplicação de eventos.
- Dois comandos sobre o mesmo relé.
- Dois POSTs para a mesma passagem.

### Estratégia

Criar um ponto de entrada separado para o protótipo Qt.

Exemplo conceitual:

    app/
      main.py
      main_qt.py

Os nomes reais devem respeitar a estrutura do projeto.

Durante a fase de protótipo:

    main.py
        → interface atual

    main_qt.py
        → interface QML simulada

Não iniciar simultaneamente Tkinter e Qt dentro do mesmo processo.

Não permitir que o protótipo QML inicialize hardware automaticamente.

Após homologação, definir um único ponto de entrada oficial.

---

# 22. Estrutura proposta do projeto

A estrutura abaixo é conceitual.

O Codex deverá adaptá-la à arquitetura encontrada.

    project-rfid/
    │
    ├── app/
    │   │
    │   ├── core/
    │   │   ├── application_state.py
    │   │   └── ...
    │   │
    │   ├── services/
    │   │   ├── rfid/
    │   │   ├── waveshare/
    │   │   ├── backend/
    │   │   └── ...
    │   │
    │   ├── controllers/
    │   │   └── ...
    │   │
    │   ├── ui/
    │   │   │
    │   │   ├── legacy/
    │   │   │   └── interface atual
    │   │   │
    │   │   ├── qt/
    │   │   │   ├── bridge/
    │   │   │   ├── models/
    │   │   │   └── ...
    │   │   │
    │   │   └── qml/
    │   │       ├── Main.qml
    │   │       ├── pages/
    │   │       ├── components/
    │   │       ├── theme/
    │   │       └── assets/
    │   │
    │   └── ...
    │
    ├── tests/
    │   ├── unit/
    │   ├── integration/
    │   └── ui/
    │
    └── ...

Não mover indiscriminadamente os serviços existentes.

A separação entre `legacy` e `qt` é uma estratégia de migração, não uma obrigação de renomear toda a árvore atual.

---

# 23. Gerenciamento de dependências

Adicionar PySide6 conforme o mecanismo de dependências já utilizado pelo projeto.

Não atualizar bibliotecas não relacionadas.

Não alterar versões de:

- sllurp;
- bibliotecas Modbus;
- cliente HTTP;
- demais dependências operacionais;

sem necessidade comprovada.

Fixar uma versão compatível do PySide6 conforme a política de dependências do projeto.

Documentar a versão de Python suportada.

Não instalar pacotes globalmente como requisito da aplicação.

---

# 24. Empacotamento Windows

A aplicação deverá continuar funcionando nativamente no Windows.

Verificar compatibilidade com o empacotamento atual.

Caso utilize PyInstaller, avaliar a inclusão de:

- Módulos PySide6.
- Plugins Qt.
- QML modules.
- Qt Quick Controls.
- Recursos SVG.
- Imagens.
- Ícones.
- Fontes utilizadas.
- Assets da marca.

### Regras

- Não depender de caminhos absolutos.
- Não depender de arquivos existentes somente na máquina de desenvolvimento.
- Não depender de internet para renderizar a interface.
- Não exigir instalação separada do Qt pelo operador.
- Não incluir dependências gráficas desnecessárias.

Testar a aplicação empacotada em um ambiente Windows limpo ou equivalente.

---

# 25. Desempenho

A interface deverá permanecer responsiva durante:

- Leitura contínua de EPCs.
- Atualizações da tabela.
- Health checks.
- Leitura de sensores.
- Atualização de relés.
- Chamadas GET.
- Chamadas POST.

### Requisitos

- Não bloquear a UI.
- Não reconstruir a página inteira por cada EPC.
- Não executar polling visual excessivo.
- Não criar animações contínuas desnecessárias.
- Não atualizar propriedades sem mudança real de estado.
- Não criar threads ilimitadas.

Preferir atualização orientada a eventos.

---

# 26. Responsividade e DPI

Validar no Windows:

    1366 × 768
    1600 × 900
    1920 × 1080

Escalas:

    100%
    125%
    150%

### Critérios

- Textos não cortados.
- Cards alinhados.
- Botões acessíveis.
- Sidebar funcional.
- Tabela com scroll.
- Logotipo proporcional.
- Sem sobreposição.
- Sem distorção.

Preservar o comportamento atual de abertura maximizada.

---

# 27. Testes automatizados

Criar testes adequados à nova camada de interface.

## 27.1 Testes de UI Bridge

Validar:

- Recebimento de eventos.
- Emissão de signals.
- Atualização de properties.
- Execução de slots.
- Comunicação segura entre threads.
- Tratamento de erros.
- Estados desconhecidos.

## 27.2 Testes de modelos

Validar:

- Inclusão de EPC.
- Atualização de registro.
- Deduplicação visual.
- Limpeza da sessão.
- Preservação de strings.
- Status correto.
- Contagem correta.
- Atualização incremental.

## 27.3 Testes QML

Validar:

- Carregamento de Main.qml.
- Disponibilidade de componentes.
- Carregamento de assets.
- Navegação.
- Binding de propriedades.
- Exibição de estados.
- Ausência de erros críticos de QML.

## 27.4 Testes com mocks

Simular:

    RFID conectado
    RFID desconectado

    Waveshare conectada
    Waveshare desconectada

    Backend OK
    Backend NOK

    EPC encontrado
    EPC não encontrado

    POST sucesso
    POST falha

    DI1 interrompido
    DI2 interrompido

    Timer finalizado

Esses testes não devem acionar equipamentos físicos.

---

# 28. Testes de regressão operacional

Antes de substituir a interface anterior, validar:

- [ ] Zebra FX9600 conecta.
- [ ] Inventário RFID inicia corretamente.
- [ ] Inventário RFID encerra corretamente.
- [ ] EPCs são recebidos.
- [ ] Deduplicação permanece funcional.
- [ ] Waveshare conecta.
- [ ] DI1–DI5 são lidos corretamente.
- [ ] CH1–CH8 continuam funcionando na tela de teste.
- [ ] DI1 inicia o ciclo corretamente.
- [ ] Timer de 60 segundos funciona.
- [ ] DI2 finaliza o ciclo corretamente.
- [ ] CH1 representa sistema apto.
- [ ] CH2 representa leitura em andamento.
- [ ] CH3 representa erro.
- [ ] Health do Backend funciona.
- [ ] Sistema apresenta estado correto.
- [ ] Base de dados apresenta estado correto.
- [ ] GET de EPC funciona.
- [ ] POST de passagem funciona.
- [ ] Não ocorrem POSTs duplicados por atualização visual.
- [ ] EPC inexistente permanece ignorado.
- [ ] Tabela apresenta os campos corretamente.
- [ ] Contador de EPCs funciona.
- [ ] Configurações persistem.
- [ ] Aplicação encerra corretamente.
- [ ] Porta COM é liberada.
- [ ] Threads são encerradas corretamente.

Os testes com hardware devem ser realizados somente após os testes simulados e em condições controladas.

---

# 29. Critérios de aprovação visual

O protótipo QML deverá ser apresentado antes da integração operacional.

A aprovação deverá considerar:

### Identidade

- [ ] Logotipo DSV correto.
- [ ] Tema corporativo moderno.
- [ ] Paleta consistente.
- [ ] Tipografia profissional.

### Layout

- [ ] Composição atual preservada.
- [ ] Header adequado.
- [ ] Sidebar adequada.
- [ ] Cards bem dimensionados.
- [ ] Tabela legível.
- [ ] Botões consistentes.

### Estados

- [ ] Verde para sucesso.
- [ ] Vermelho para falha.
- [ ] Amarelo para leitura/processamento.
- [ ] Cinza para desconhecido.
- [ ] Texto acompanha a cor.

### Qualidade

- [ ] Sem aparência de Tkinter legado.
- [ ] Sem excesso de efeitos.
- [ ] Sem componentes visualmente incompatíveis.
- [ ] Sem textos cortados.
- [ ] Sem sobreposição.
- [ ] Sem problemas de contraste.

**PONTO DE CONTROLE 3**

O Codex deverá apresentar capturas de tela reais do protótipo executado no Windows.

Não considerar o protótipo aprovado apenas porque o código QML compila.

A aprovação visual deverá ser explícita antes da integração operacional.

---

# 30. Estratégia de rollback

A migração deverá permitir retorno à interface anterior até a homologação final.

### Requisitos

- Preservar a implementação atual.
- Trabalhar em branch específica.
- Criar commits por etapa.
- Evitar mudanças irreversíveis em configurações.
- Não alterar o formato do banco.
- Não excluir assets existentes prematuramente.
- Não remover dependências Tkinter antes da homologação.

Branch sugerida:

    feature/pyside6-qml-migration

Commits sugeridos:

    refactor(ui): prepara arquitetura para migração Qt

    feat(ui): adiciona protótipo PySide6 QML

    feat(ui): integra modelos e estados da aplicação

    feat(ui): integra telas de configuração

    feat(ui): integra controles RFID e Waveshare

    test(ui): valida regressão da interface Qt

A remoção da interface antiga deverá ocorrer somente em uma etapa final aprovada.

---

# 31. Fora do escopo

Não implementar neste requisito:

- Alterações no Backend Rails.
- Alterações no PostgreSQL.
- Novos endpoints.
- Alterações de contrato JSON.
- Alterações no protocolo LLRP.
- Alterações no protocolo Modbus.
- Alterações na lógica dos sensores.
- Alterações nos tempos operacionais.
- Alterações na deduplicação.
- Alterações no registro de passagens.
- Novos KPIs.
- Novas funcionalidades.
- Novas colunas.
- Novo fluxo operacional.
- Novas regras de validação EPC.
- Sincronização SQLite.
- Integração Power Automate.

O foco é exclusivamente a substituição segura da camada gráfica.

---

# 32. Entregas por fase

| Fase | Entrega | Exige aprovação? |
|---|---|---|
| 0 | Auditoria da arquitetura | Sim |
| 1 | Protótipo visual QML com mocks | Sim |
| 2.1 | Configurações e estados | Testes |
| 2.2 | Modelos e tabela | Testes |
| 2.3 | Backend e Zebra | Testes |
| 2.4 | Waveshare e fluxo completo | Homologação |
| 3 | Empacotamento Windows | Validação |
| 4 | Remoção da interface antiga | Sim |

Cada fase deverá produzir um diff revisável.

Não executar todas as fases em uma única alteração massiva.

---

# 33. Definição de pronto

O RF018 estará concluído somente quando:

1. A interface oficial utilizar PySide6 + QML.
2. O layout original estiver preservado.
3. A identidade DSV estiver corretamente aplicada.
4. O protótipo visual tiver sido aprovado.
5. A UI Bridge estiver implementada.
6. Os modelos Qt estiverem funcionais.
7. Os serviços Python existentes forem reutilizados.
8. A leitura RFID funcionar.
9. A Waveshare funcionar.
10. O Backend funcionar.
11. O fluxo RF012 estiver preservado.
12. Os requisitos RF015, RF016 e RF017 continuarem funcionais.
13. Não houver operações de hardware diretamente no QML.
14. Não houver chamadas HTTP diretamente no QML.
15. Não houver bloqueios do event loop.
16. O encerramento liberar os recursos corretamente.
17. Os testes automatizados passarem.
18. Os testes operacionais passarem.
19. O empacotamento Windows funcionar.
20. A nova interface for homologada.

---

# 34. Relatório final obrigatório

Ao finalizar a migração, apresentar:

- Arquitetura anterior.
- Arquitetura nova.
- Arquivos criados.
- Arquivos alterados.
- Componentes QML implementados.
- UI Bridge implementada.
- Modelos Qt utilizados.
- Serviços preservados.
- Dependências adicionadas.
- Estratégia de threads.
- Estratégia de gerenciamento de estado.
- Estratégia de encerramento.
- Resultados dos testes.
- Evidências visuais.
- Resultados dos testes com hardware.
- Pendências.
- Limitações.
- Confirmação de compatibilidade com Windows.

---

# 35. Instrução de execução inicial para o Codex

ATENÇÃO:

Este requisito descreve o projeto completo de migração, mas NÃO autoriza executar todas as fases imediatamente.

**Neste primeiro momento, executar SOMENTE a Fase 0.**

Sua tarefa inicial é:

1. Ler `AGENTS.md` e as instruções do repositório.
2. Inspecionar a arquitetura atual.
3. Mapear os arquivos Tkinter.
4. Mapear as dependências com a lógica operacional.
5. Identificar riscos de migração.
6. Propor a arquitetura PySide6 + QML.
7. Propor a estrutura de arquivos.
8. Identificar os serviços que poderão ser reutilizados sem alterações.
9. Elaborar um plano de migração incremental.
10. Apresentar o relatório técnico.

Não alterar código.

Não instalar dependências.

Não excluir arquivos.

Não migrar widgets.

Não iniciar a Fase 1 sem autorização.

**A prioridade absoluta é preservar a estabilidade operacional do software RFID enquanto construímos uma interface nova, moderna e profissional.**