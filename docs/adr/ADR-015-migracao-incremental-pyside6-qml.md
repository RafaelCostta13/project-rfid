# ADR-015 — Migração incremental da interface para PySide6 + QML

- Status: Aceita; Qt oficial e Tkinter removido por autorização do usuário; homologação física pendente
- Data: 2026-10-08
- Requisito: RF018 — Migração Controlada da Interface RFID para PySide6 + QML, v2
- Complementa: ADR-001, ADR-003, ADR-006, ADR-008, ADR-013 e ADR-014
- Autorização: após o relatório da Fase 0, o usuário aprovou iniciar a Fase 1
  e solicitou o registro das decisões em ADR.
- Continuidade: após a entrega visual, o usuário respondeu “sim”; a resposta
  foi interpretada e comunicada como aprovação do Corporate Dark recomendado
  e início do recorte incremental de configurações/indicadores, sem hardware.

## Contexto e auditoria da Fase 0

A migração é exclusivamente da apresentação. Não autoriza reescrever regras
RFID, Backend, sensores, relés, configuração ou persistência. A Fase 0 foi
realizada sem editar código ou instalar dependências, com 291 testes aprovados.

### Arquitetura encontrada

`pyproject.toml` define `rfid-reader = rfid_reader.cli:run`. `cli.py` carrega
e valida as configurações; `application.py:run_application` compõe os serviços
e a `ui/main_window.py:MainWindow`. A UI atual é Tkinter/ttk, não CustomTkinter.

A composição compartilha um reader Zebra, um serviço de consulta com worker
único e fila limitada, um controlador automático, um gate serial e o serviço
de diagnóstico Waveshare. Os callbacks publicam eventos em oito filas. A janela
consome as filas com `after(100, ...)`; não há chamadas de widgets nos serviços.

O monitor executa workers por conexão. Start/Stop são serializados por
`ThreadPoolExecutor(max_workers=1)`. Configurações RFID/Waveshare têm workers
de teste. O inventário automático usa `threading.Timer`, com cancelamento e
identificação do ciclo. Logging é configurado na aplicação e os módulos usam
loggers próprios. Configurações são validadas em `config.py` e os serviços
persistem o `.env`, preservando as demais chaves.

Não há configuração de PySide6, QML, PyInstaller ou recursos Qt no estado
auditado. Os assets existentes ficam em `assets/branding`. O README contém
descrições históricas de SharePoint/SQLite que não representam o bootstrap atual.

### Telas e dependências Tkinter

| Tela/arquivo | Componentes e finalidade | Dados/eventos/comandos | Serviços e riscos |
|---|---|---|---|
| Start — `ui/pages.py:SystemStatusPage` | Título, resumo, contador, controles e tabela | Eventos de sessão, estado e lookup; iniciar/parar modo automático | Inventário e lookup; preservar deduplicação, contador e resultados tardios |
| Configs — `ui/pages.py:RFIDSettingsPage` e `WaveshareSettingsPanel` | Nome/IP/porta RFID, doca, parâmetros seriais e URL Backend | Recarregar campos, testar, salvar e exibir feedback | Configuração reader/Waveshare/station/Backend; evitar UI bloqueada e gravações concorrentes |
| Diagnóstico — `ui/waveshare_diagnostic_page.py` | DI1–DI5, CH1–CH8, conexão e comandos manuais | Eventos de conexão, entradas, relés e erro; conectar/desconectar/ligar/desligar | Diagnóstico e controle automático; exclusividade COM e bloqueio de CH1–CH3 no automático |
| Shell — `ui/main_window.py`, `components.py`, `styles.py` | Header, indicadores, sidebar Start/Configs e área de conteúdo | Navegação, consumo de filas e fechamento | Adaptação de apresentação; diagnóstico depende da navegação e do modo automático |

Dependências a substituir: `Tk`, `Frame`, `Label`, `Button`, variáveis Tk,
bindings, `configure`, `Treeview.insert/item`, Canvas, geometria, `after` e
`mainloop`. A lógica operacional não depende diretamente dessas APIs. Há
mapeadores de apresentação dentro de módulos Tk: o Qt não deve importar esses
módulos apenas para reutilizar funções ou constantes.

### Estados e suas fontes reais

| Estado | Fonte/contrato existente |
|---|---|
| RFID, Internet, Comandos e Sistema | `ConnectionMonitor` e respectivos checkers; CHECKING, CONNECTED, DISCONNECTED, ERROR |
| Inventário parado/lendo/erro | `ManualInventoryService`, após confirmação ou falha do reader |
| Modo automático habilitado e disponibilidade | `AutomaticInventoryController`; Start habilita o modo, não inventário imediato |
| DI1–DI5 e CH1–CH8 | Eventos confirmados de `WaveshareDiagnosticService`; ausência de informação é desconhecido |
| Timer de 60 segundos | Controller Python; permanece fora da UI |
| Linha e contador da sessão | `TagLookupService`, `session_id` e resumo por EPC; somente FOUND |
| Status de negócio da passagem | Resposta do POST validada pelo cliente Backend; não calcular sucesso/contador remotamente em QML |

## Decisões aprovadas

1. Utilizar PySide6 + Qt Quick/QML, preservando a interface Tkinter e sua entrada.
2. Construir primeiro somente Start, com dados fictícios separados dos serviços.
3. Manter somente **Sistema**, além de RFID, Internet e Comandos, conforme a
   ADR-013. As menções a Base de dados no RF018 não reintroduzem indicador,
   checker, dependência de disponibilidade ou acesso ao PostgreSQL. Essa
   divergência foi apresentada na auditoria e a recomendação foi aprovada.
4. Não iniciar Fase 2 sem aprovação visual explícita e testes com mocks.
5. Manter os seis campos visuais: Status, Cliente, Nota fiscal, Volume, Pedido
   e Doca. EPC é chave interna. Preservar strings e zeros à esquerda.
6. Não modificar contratos, deduplicação, tempos, protocolos ou configurações
   persistidas para atender à nova UI.

### Componentes preservados e substituídos

Preservar domínio, configuração/validação, cliente HTTP, driver LLRP, inventário,
lookup, gate serial, diagnóstico, callbacks, logs e regras operacionais. Não
mover ou refatorar serviços durante a Fase 1.

Substituir gradualmente widgets, estilos ttk, tabela e consumo de eventos pela
janela. O Qt utilizará QObject/Signal/Slot/Property e QAbstractTableModel.
O modelo é uma projeção: atualizar uma célula não executa GET ou POST.

### Estrutura implementada na Fase 1

```text
src/rfid_reader/
├── cli_qt.py
└── ui/
    ├── qt/
    │   ├── application.py
    │   ├── bridge.py
    │   ├── models.py
    │   └── mock_data.py
    └── qml/
        ├── Main.qml
        ├── theme/Theme.qml + qmldir
        ├── components/
        ├── pages/StartPage.qml
        └── assets/branding/dsv_logo.svg
```

`rfid-reader-qt`, sem `--configure`, é uma entrada separada de protótipo.
Não importa a composição operacional,
não carrega `.env`, não cria serviços e não abre HTTP/LLRP/COM. Configurações
aparece desabilitada, explicitamente reservada à Fase 2. Start/Stop alteram
somente a apresentação fictícia; Start representa a espera por DI1. Os cinco
cenários são apto, lendo, falha, verificando e vazio.

Corporate Dark e Navy Dark compartilham composição e componentes. Recomenda-se
Corporate Dark pelo grafite discreto e destaque moderado da navegação. A
paleta foi posteriormente aprovada pelo usuário para continuidade. Tokens semânticos
e tipográficos são centralizados em singleton QML: verde sucesso, amarelo
leitura/verificação, vermelho falha, cinza desconhecido e azul neutro.

O asset SVG já existente no projeto é copiado sem alteração para os recursos da UI Qt,
com geometria e cor institucional preservadas, superfície branca e área de
respiro. Os arquivos QML, qmldir e SVG são incluídos em package-data. Caminhos
são relativos ao pacote, não ao cwd. `imagem.png` não foi encontrada; a
aprovação visual deve considerar essa ausência de referência.

PySide6 6.10.3 fica fixado no extra opcional `qt`, isolando a dependência gráfica
da instalação operacional atual. A validação inicial utiliza Python 3.12 no
Windows. Nenhuma versão de sllurp, pymodbus ou cliente HTTP é alterada.

## Integração futura e riscos

Eventos de workers devem chegar por sinais enfileirados a slots da thread Qt.
Somente essa thread atualiza objetos QML e o modelo; não haverá worker por EPC.
Atualizações incrementais usarão inserções e dataChanged, sem reconstruir a
tela. O adaptador futuro refletirá o controller existente, não uma máquina de
estados operacional concorrente. `PrototypeBridge` permanece explicitamente
simulado; os adaptadores novos ficam separados dele.

Na Fase 2, extrair minimamente a composição/ciclo de vida de `application.py`,
injetando a UI e reutilizando serviços. Riscos a resolver/testar nessa etapa:

- `run_application` conecta Waveshare e inicia monitoramento: não reutilizá-lo
  no protótipo.
- Teste Backend cria thread daemon não acompanhada por shutdown; o monitor
  pode esgotar o tempo de join antes de um worker acabar. Não tratar fechar a
  janela como prova de encerramento operacional correto.
- Consumo ilimitado de filas em cada tick e salvamentos síncronos podem travar
  a UI. Serializar comandos e persistência, sem mudar o formato `.env`.
- Deduplicação da consulta é por reader/antena/EPC, mas tabela/resumo são por
  EPC. Não modificar silenciosamente essa diferença.
- Disponibilidade tem compatibilidade que ignora Sistema até a primeira
  observação de health; testar início e recuperação antes de alterar regras.
- Resultados antigos não podem atualizar a sessão atual. POST já enviado não
  deve ser cancelado/repetido pela UI, inclusive em timeout ambíguo.
- Abrir telas não deve abrir outra COM, outro controller ou acionar relés.
- Empacotamento Windows exige validação futura de plugins Qt/QML/SVG e execução
  offline em ambiente limpo; package-data não é homologação de um executável.

Preservar DI1/DI2 invertidos, CH1 apto, CH2 leitura confirmada, CH3 falha e
CH4–CH8 com regras atuais. Timer e encerramento físico continuam em Python.

## Plano de testes e checkpoints

Fase 1: testar propriedades/sinais/slots, entrega enfileirada entre threads,
cenários, estados, modelo incremental, deduplicação visual, strings, sessão,
carregamento QML, SVG, bindings, controles e ausência de inicialização real.
Executar Ruff, formatação, Mypy e Pytest, mantendo os testes legados.

Capturas devem vir da renderização real do QML no Windows, não de mockups.
Validar 1366×768, 1600×900 e 1920×1080 e escalas 100/125/150%. Testes offscreen
não substituem inspeção interativa, maximização ou aprovação visual do usuário.
O modo `--screenshot` existe somente para produzir evidência visual e encerrar.

Fases futuras: configuração/salvar/reabrir, eventos Backend/Zebra falsos,
GET/POST/404/erro/timeout sem retry, DI1/DI2 e timer simulados, sessão antiga,
liberação COM/reader/workers e, após autorização, regressão física controlada.

## Sequência, complexidade e rollback

| Etapa | Complexidade | Condição |
|---|---|---|
| 0 — auditoria | Média | Concluída e aprovada |
| 1 — Start simulado, temas e evidências | Média | Entregue; Corporate Dark aprovado |
| 2.1 — configuração local e adaptador de estados | Média | Implementada; monitor ativo e testes físicos não integrados |
| 2 — modelo, Backend e Zebra | Alta | Mocks antes de integração física |
| 2 — Waveshare e fluxo completo | Muito alta | Mocks + homologação controlada |
| 3 — empacotamento Windows | Alta | Ambiente limpo/offline |
| 4 — troca definitiva e remoção Tk | Alta | Homologação e aprovação explícitas |

Rollback: executar `rfid-reader show` para retornar à UI atual. A entrada Qt
não substitui a oficial. O protótipo não altera `.env`; o modo `--configure`
persiste somente configurações locais mediante Salvar. Essas gravações também
serão lidas pelo legado; trocar a interface não desfaz configurações salvas.
Nenhum dos modos Qt acessa banco ou hardware neste recorte. Usar branch
dedicada e commits por etapa quando Git estiver disponível. Nesta máquina Git
não foi localizado no PATH; nenhuma branch ou commit foi criado pelo agente.
O HEAD encontrado pertence a `integracao-backend`. Não remover Tkinter ou
assets existentes antes da homologação.

## Alternativas consideradas

- Trocar toda a UI de uma vez: rejeitado pelo risco operacional e rollback.
- Reescrever serviços com QThread/Qt: rejeitado; adaptar eventos é suficiente.
- Reutilizar a inicialização real no protótipo: rejeitado por abrir hardware/rede.
- Fazer HTTP/Modbus em QML: rejeitado por acoplamento, bloqueios e efeitos de renderização.
- Reintroduzir Base de dados: rejeitado conforme decisão aprovada da ADR-013.
- Tornar Qt obrigatório na entrada legada: rejeitado durante a migração.

## Consequências e pendências

A Fase 1 é uma prévia isolada, não a conclusão do RF018. A aprovação visual
permite a integração incremental, não autoriza testes no equipamento real.
O recorte 2.1 abaixo não substitui o fluxo operacional. Restante da Fase 2,
testes físicos e Fases 3–4 permanecem pendentes.

## Verificação da entrega da Fase 1

- Ambiente: Windows, Python 3.12.10, PySide6 6.10.3 instalado somente na `.venv`.
- Ruff check e format check aprovados; Mypy strict aprovado nos 55 arquivos
  de fonte; suíte Pytest aprovada: **338 testes**.
- 47 testes adicionados à camada de protótipo; os 291 testes anteriores permanecem.
- Matriz automatizada: três resoluções físicas × escalas 100/125/150%, offscreen,
  verificando renderização/captura e ausência de erros QML.
- Testes incluem popup/teclado, desconhecido cinza, entrega entre threads,
  falha ao gravar captura com saída controlada e proibição de importar a
  composição operacional ou acessar rede.
- SVG Qt idêntico ao asset local original, confirmado por SHA-256.
- Wheel construído, instalado em diretório de validação separado e executado
  com recursos QML/SVG desse diretório. Isso valida a distribuição Python,
  não um executável autônomo ou uma máquina Windows limpa.
- Capturas reais em [docs/evidencias/rf018](../evidencias/rf018/README.md).
- Inspeção de processos após as capturas não encontrou prévia Qt remanescente.
- Revisão dos arquivos novos e das alterações de README/pyproject realizada.
  Diff pelo Git indisponível porque o executável não foi localizado; nenhuma
  mudança nos serviços operacionais foi feita pelo agente na Fase 1.

## Entrega incremental 2.1 — configurações e indicadores

### Escopo e decisões

- `--configure` habilita um modo explícito, sem composição operacional.
  `--env-file` define o destino e `--page settings` abre o formulário diretamente.
  A entrada padrão continua simulada; opções de configuração não se misturam
  com cenários fictícios. Leitura `.env` e prioridade do ambiente seguem o legado.
- `ConfigurationBridge` reutiliza ReaderConfigurationService,
  WaveshareConfigurationService, StationConfigurationService e
  BackendConfigurationService. Não replica validadores ou o formato persistido.
  A URL mantém a regra atual de trim, sem introduzir validação mais restrita.
- Ajustes mínimos de composição: reader/configurer/factory e tester podem ser
  `None` nos serviços de configuração RFID/Waveshare. Nesse caso, Salvar não
  configura driver e Testar falha explicitamente sem criar worker. Dependências
  fornecidas pelo bootstrap legado continuam com o comportamento anterior.
- Um executor Python com um worker serializa todas as gravações no mesmo `.env`.
  Enquanto ocupado, novos comandos são recusados e campos/Salvar desabilitados.
  Stores existentes preservam outras chaves, comentários e CRLF por substituição
  atômica. A proteção é por instância, não entre processos; evitar duas UIs
  editando simultaneamente. Nenhuma nova dependência foi adicionada.
- Feedback atravessa `Signal` com `QueuedConnection` e slot decorado. A UI não
  é atualizada pelo worker. Sucesso recarrega só a seção salva; falha preserva
  rascunhos. Doca mantém texto livre/sugestões e normalização existentes.
- Fechamento recusa novos comandos, ignora callbacks tardios e aguarda a
  gravação em curso após sair do event loop, sem deixar executor órfão.
  Falha inesperada vira feedback; o log da fronteira não inclui valores do formulário.
- `ConnectionBridge` projeta somente eventos/snapshot do ConnectionMonitor:
  RFID, Internet, Comandos e Sistema. Entrega enfileirada, sem nova sondagem
  ou máquina de estados. Estados ausentes são cinza/Desconhecido; DATABASE e
  SYNC legados não reintroduzem Base de dados. Nenhum monitor é iniciado neste modo.
- QML acrescenta SettingsPage, campos, cards e feedback reutilizáveis, com
  grid responsivo e scroll. O shell navega entre Start/Configurações sem abrir
  COM, iniciar serviços ou executar consultas. Start mostra tabela vazia e
  controles operacionais desabilitados, sem apresentar dados fictícios como reais.
- Testes de conexão/diagnóstico continuam desabilitados: Backend/Zebra/Waveshare
  serão conectados nas próximas etapas. Não reutilizar o bootstrap legado,
  que já inicia monitoramento e conexão Waveshare, apenas para preencher indicadores.
- `None` do Python pode chegar como `undefined` a propriedades QML `var`.
  No protótipo, a propriedade opcional não é injetada; mantém o `null` declarado
  no QML. O teste de regressão confirma o menu desabilitado e ausência de warnings.
- Branding preservado: Qt usa cópia byte-idêntica de `assets/branding/dsv_logo.svg`.
  O arquivo indicado no Desktop contém trechos não gráficos após `</svg>`;
  por isso seu checksum completo difere. O conteúdo até o fechamento de SVG
  foi comparado e é idêntico ao asset local, incluindo viewBox, path e fill.
  Não sobrescrever o asset existente nem distribuir os trechos externos ao logo.

### Checkpoint e limites

Configurações podem ser lidas, validadas, salvas e reabertas; a projeção de
estados está coberta por callbacks do monitor com fakes. Monitoramento real,
teste RFID/HTTP/COM, tabela alimentada pelo Backend, inventário, diagnóstico,
timer/relés e fluxo completo continuam pendentes. Não declarar a etapa inteira
de integração operacional ou o RF018 concluídos por esta entrega.

O agente usou somente `.env` temporários nos testes e Settings fictícios nas
capturas. O `.env` real não foi lido, alterado ou exposto pelo agente.
Os `__init__.py` existentes reexportam definições de serviços e drivers;
isso não instancia hardware. O teste isolado proíbe criar reader/cliente HTTP/
monitor, abrir socket/serial e iniciar threads Python ao abrir a tela.

### Verificação da entrega 2.1

- Ruff check aprovado; format check aprovado nos 139 arquivos; Mypy strict
  aprovado nos 57 arquivos de fonte. Pytest final: **383 testes aprovados**,
  incluindo 45 adicionados neste recorte e os 338 da entrega anterior;
  testes hardware não executados.
- Testes cobrem salvamento das quatro seções, reabertura, CRLF/chaves preservadas,
  falha atômica sem alterar memória/arquivo, validação existente, URL trim-only,
  executor fora da thread Qt, recusa de comandos concorrentes, callbacks tardios,
  encerramento sem worker, erro inesperado sem valores do formulário nos logs,
  estados/cores, snapshot/callback do monitor com fake, teclado de Doca,
  navegação, scroll até Backend e preservação de rascunhos entre seções.
- Matriz offscreen de Configurações: 1366×768, 1600×900 e 1920×1080 físicos,
  com escala 100/125/150%, sem warnings QML ou acesso ao arquivo real.
- Capturas Windows nativas em `configuracoes.png`, `configuracoes-backend.png`
  e `wheel-configuracoes.png`, usando valores fictícios. O desktop pode limitar
  as dimensões efetivas, como já registrado para a Fase 1.
- Wheel atualizado construído e instalado em `build/rf018-config-installed`;
  execução isolada confirma SettingsPage, componentes e SVG distribuídos.
  Isso não homologa executável autônomo, instalação limpa ou hardware.
- Nenhum processo da prévia Qt permaneceu após testes e capturas.
- Revisão direta dos arquivos alterados realizada. Git não encontrado no PATH
  nem nos caminhos usuais de Program Files; diff, branch e commit indisponíveis.

Referências técnicas: [thread safety dos modelos Qt](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QAbstractTableModel.html)
e [signals/slots entre threads](https://doc.qt.io/qtforpython-6/tutorials/basictutorial/signals_and_slots.html).

## Integração operacional — 2026-10-09

O RF018 “Implementação Operacional Definitiva PySide6 + QML” autoriza a
integração dos serviços existentes e preserva a condição de homologação antes
da remoção definitiva do Tkinter. Este checkpoint substitui as pendências
operacionais descritas na entrega 2.1; o histórico anterior permanece registrado.

### Composição e entrega de eventos

`runtime.py:ApplicationRuntime` concentra reader, inventário, lookup,
controlador automático, diagnóstico Waveshare, gate serial, monitor e serviços
de configuração. Sua construção não inicia workers nem abre equipamentos.
`start()` inicializa os workers; `close()` invalida sessões, bloqueia novos ciclos,
cancela timers, encerra conexões e aguarda I/O em andamento. Falhas de limpeza
são registradas por componente; as demais limpezas continuam e a falha é propagada.
O runtime não importa Tkinter, Qt ou widgets e não depende de `after()`.

A janela antiga consome filas opcionais desse runtime. A execução Qt utiliza
assinaturas de `RuntimeEvent` e sinais com `QueuedConnection`; filas legadas
não acumulam eventos no modo Qt. `OperationalBridge` projeta estado, comandos,
diagnóstico e sessões em `TagTableModel`. Propriedades e slots da ponte utilizam
estado local entregue por eventos; não aguardam locks de controller que possam
estar ocupados com LLRP. Modelo e UI são atualizados na thread Qt.

Há uma sessão Zebra compartilhada entre monitor, inventário e teste RFID.
O teste serializa acesso ao mesmo reader e restaura a configuração salva;
nenhum reader temporário adicional é criado. A Waveshare mantém seu worker
único e o gate já existente. Iniciar devolve o diagnóstico manual ao controller.
CH1–CH3 manuais são bloqueados enquanto o automático está habilitado, inclusive
para comandos que já estavam na fila. CH4–CH8 permanecem disponíveis.

### Regras preservadas e ajustes de integração

- Start habilita automático e aguarda a transição DI1 ATIVA → DESATIVADA.
  Stop desabilita o modo e cancela o ciclo. DI2, geração dos timers e limite
  de 60 segundos continuam no controller existente.
- GET/POST continuam no worker de lookup, com o contrato Rails e deduplicação
  por sessão. A tabela não realiza POST. GET de sessão invalidada/fechada não
  inicia POST; POST já enviado não é repetido e seu resultado antigo é ignorado.
- A sessão é publicada antes de aceitar callbacks RFID, evitando resultado
  chegar ao Qt antes da abertura do modelo. Uma sessão LLRP recuperada libera
  o estado de erro do inventário para um novo ciclo controlado.
- Configuração operacional reutiliza as mesmas instâncias de serviço; gravações
  e testes Qt usam o executor serializado do runtime. `--configure` preserva
  seu isolamento e os testes físicos continuam desabilitados nesse modo.
- O RF018 pede Base de dados além de Sistema. O cliente preserva `database`
  na mesma resposta health e o checker o publica somente quando solicitado
  pelo runtime. Base de dados é observacional; a aptidão continua usando
  `status`/Sistema conforme ADR-013. Não há segunda sondagem nem consulta SQL.
- O layout Corporate Dark, Start, Configurações, tabela e branding aprovados
  foram preservados. DiagnosticPage utiliza os componentes existentes.

O arquivo histórico RF012 descreve timer de 30 segundos e CH3 para ambos os
feixes interrompidos, enquanto o controller operacional atual e o RF018 usam
60 segundos e CH3 para indisponibilidade das dependências. A migração mantém
o comportamento implementado, sem reescrever a regra física. A divergência
está explicitada no checklist para conferência na homologação.

### Entrada, distribuição e conclusão

`rfid-reader-qt --operate --env-file <arquivo>` inicia a operação real.
A entrada sem opções continua sendo a prévia, `--configure` permanece isolado
e `rfid-reader show` mantém a execução anterior. O entrypoint oficial não foi
substituído e nenhum widget Tkinter foi removido antes da homologação.

O build Windows usa PyInstaller, recursos QML/SVG empacotados e os hooks Qt.
Recursos são resolvidos por `__file__`; o `.env` real fica externo. O verificador
executa prévia/configuração em cwd separado, sem Python no PATH, com dados
fictícios e Qt offscreen. Isso valida o carregamento do bundle na máquina atual;
não substitui uma instalação em Windows limpo nem a homologação dos transportes.
Ver [documentação de recursos do PyInstaller](https://pyinstaller.org/en/stable/spec-files.html#adding-data-files).

Resultados finais, arquivos e comandos estão no
[relatório operacional](../validacao/RF018-relatorio-operacional.md).
Verificação final: 410 testes aprovados, nenhum reprovado; Ruff check,
format check e Mypy aprovados. Bundle Windows reconstruído e aprovado no
smoke test de prévia/configuração sem Python no PATH, na máquina atual.
O [checklist físico](../validacao/RF018-homologacao-fisica.md) permanece pendente.
RF018 não está declarado concluído enquanto persistirem essas condições.

## Substituição final autorizada — 2026-10-09

Após a entrega operacional, o usuário autorizou expressamente executar a
migração completa. Essa instrução substitui a condição documental que adiava
a retirada do Tkinter até a homologação física. Os checkpoints anteriores
descrevem o histórico; este é o estado atual da interface.

`rfid-reader`, `rfid-reader show`, `rfid-reader-qt` e o executável Windows abrem
a operação Qt por padrão. `--preview` torna a prévia explicitamente simulada;
`--configure` preserva a configuração local sem conexões. `--operate` continua
aceito. `check-config --env-file <arquivo>` permanece disponível sem importar
Qt nem iniciar serviços. PySide6 passa a ser dependência de produção.

A antiga composição `application.py`, os widgets, a navegação e o tema Tkinter
foram removidos. O runtime utiliza somente assinaturas de eventos; filas e
wrappers destinados à janela antiga foram retirados. Protocolos, endereços,
regras de sensores/relés, timer e serviços operacionais permanecem existentes.
Testes exclusivos dos widgets antigos são retirados; cobertura equivalente
de tabela, contador, configuração, navegação e diagnóstico está nos testes Qt.

O executável usa a mesma CLI oficial e exclui Tkinter do bundle. Seu verificador
usa `--preview`, configuração fictícia e `check-config`, sem abrir equipamentos.
Git continua indisponível neste ambiente; um snapshot pré-substituição foi
guardado em `build/rf018-before-final`, e o diff desta etapa é registrado em
`build/rf018-final-review.diff`. Nenhuma referência Git foi alterada.

A migração do código é finalizada por autorização do usuário. Homologação
física e implantação em outro Windows com equipamentos continuam pendentes;
esta autorização não é evidência de funcionamento físico.

Validação final da substituição: 377 testes aprovados, nenhum reprovado,
Ruff check/format check aprovados nos 135 arquivos e Mypy nos 49 arquivos
de fonte. Foram retirados 41 casos exclusivos do Tkinter e adicionados 8
casos de lançadores Qt. Build e smoke test Windows aprovados; o verificador
confirma ausência de Tkinter, preservação dos recursos e funcionamento de
`check-config` sem Python no PATH. O relatório contém os arquivos e evidências.

## RF018 — Ajuste 01: indicadores da Start

A lista visual operacional reutiliza os quatro itens de `CONNECTION_LABELS`,
na ordem RFID, Internet, Comandos e Sistema. A inclusão visual separada de
Base de dados foi retirada, e o container QML distribui os quatro itens sem
espaço reservado ao quinto indicador. Os estados internos DATABASE/SYNC,
health, monitor e prontidão permanecem intactos. Ver o
[relatório do ajuste](../validacao/RF018-ajuste01-relatorio.md).
