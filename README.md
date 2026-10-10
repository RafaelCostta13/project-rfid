# RFID Reader

Aplicação Python para comunicação com leitores RFID, inicialmente o Zebra FX9600.
A interface oficial usa PySide6 + QML, com indicadores de disponibilidade,
inventário automático por DI1/DI2, diagnóstico Waveshare e EPCs confirmados e
registrados pelo Backend Rails. O runtime e os serviços independem da interface.

## Requisitos

- Python 3.12 ou superior;
- `pip`;
- PySide6, instalado com as dependências do projeto;
- um terminal Bash, PowerShell ou Prompt de Comando.

## Preparação do ambiente

No Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

No Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

No Windows Prompt de Comando, use `.venv\Scripts\activate.bat` para ativar o
ambiente.

## Configuração

Copie o arquivo de exemplo e ajuste os valores para o seu ambiente:

No Linux:

```bash
cp .env.example .env
```

No Windows:

```powershell
Copy-Item .env.example .env
```

O arquivo `.env` é local e ignorado pelo Git. Na ausência de valores explícitos,
o reader usa `192.168.0.214`, porta `5084` e nome `fx9600-01`. Valores informados
são sempre validados. `RFID_CONNECTION_TIMEOUT_SECONDS` controla o timeout das
sondagens e `RFID_STATUS_CHECK_INTERVAL_SECONDS` define o intervalo entre
atualizações.

Para consultar EPCs e registrar passagens no Backend Rails, configure também:

```dotenv
RFID_BACKEND_BASE_URL=http://backend-de-testes:3000
```

Health, GET EPC e POST de passagem usam o cliente HTTP existente. URLs e
segredos do ambiente devem permanecer no `.env` externo ao pacote.

A porta Waveshare começa vazia; configure-a para habilitar o inventário
automático por sensores. Os demais parâmetros usam os valores validados:

```dotenv
WAVESHARE_SERIAL_PORT=
WAVESHARE_BAUD_RATE=9600
WAVESHARE_DATA_BITS=8
WAVESHARE_PARITY=None
WAVESHARE_STOP_BITS=1
WAVESHARE_DEVICE_ID=1
```

## Abrir a tela principal

Com o ambiente virtual ativado:

```bash
rfid-reader --env-file .env
```

A aplicação mantém uma única sessão LLRP com o FX9600 e a reutiliza tanto para o
status quanto para o inventário. Na página **Start**, **Iniciar leitura** habilita
o automático e aguarda DI1; **Parar leitura** cancela o ciclo. A tabela apresenta
somente EPCs confirmados pela base, com status, cliente, nota fiscal, volume,
pedido e doca quando disponibilizados pelo Backend. EPCs não encontrados,
inválidos ou afetados por erro técnico não criam linhas. Campos ausentes ou nulos
permanecem vazios.

O card **EPCs encontrados** mostra a quantidade de EPCs distintos confirmados na
sessão atual. A lista, o card e a deduplicação são reiniciados a cada novo
início. O EPC hexadecimal original permanece usado internamente na consulta,
deduplicação e associação da resposta, mas não é apresentado como coluna.

As consultas HTTP são processadas por uma fila limitada e por um único worker,
sem bloquear o callback LLRP. Durante a mesma sessão, a combinação de reader,
antena e EPC é consultada apenas uma vez. Ao parar e iniciar uma nova sessão, o
ROSpec é recriado, a deduplicação é limpa e o mesmo EPC pode ser lido e
consultado novamente.

Nesta etapa, o inventário utiliza somente a primeira antena de `RFID_ANTENNAS`.
São criadas apenas configurações transitórias da sessão e um ROSpec temporário,
removido ao parar a leitura ou fechar a aplicação. Nenhuma configuração
persistente do reader é alterada.

O acesso à internet é verificado por HTTPS, evitando depender da liberação da
porta DNS 53. Os estados de RFID, Internet e Waveshare são verificados de forma
independente. O indicador **Comandos** na barra superior representa uma resposta
Modbus válida; sem COM configurada, mostra **Desconectado**. Durante o
diagnóstico, a verificação usa o estado da sessão aberta, sem acessar a COM em
paralelo.

Na página **Configurações RFID**, nome, IP/hostname e porta podem ser testados e
salvos no mesmo `.env`. O teste é temporário, não inicia inventário e não altera
o arquivo; utiliza o mesmo reader e restaura a conexão salva ao terminar.
O salvamento preserva as demais chaves e prepara os novos dados para a
próxima conexão, sem interromper ou reconectar automaticamente a sessão atual.

Na mesma área de **Configurações**, a seção **Waveshare** permite testar e salvar
os parâmetros Modbus RTU. O teste usa a sessão serial existente quando os
parâmetros coincidem, ou uma sondagem exclusiva pelo gate serial; não aciona
relés. Salvar não troca os parâmetros de uma sessão serial já aberta.

O botão **Testar Waveshare**, dentro da mesma seção, abre o diagnóstico manual.
Use **Conectar** para acompanhar D1–D5 e consultar o estado de CH1–CH8; cada
relé pode ser ligado ou desligado separadamente. **Voltar** encerra o teste e
devolve a sessão COM ao controle operacional. A tela usa a configuração salva,
não aciona relés por conta própria e não inicia o inventário RFID.

## Operação automática por sensores (RF012 — Windows)

O worker operacional da Waveshare utiliza uma única sessão serial. Quando
Internet, RFID, Waveshare e Sistema estão conectados, CH1 indica que o
sistema está apto.
Na página **Start**, **Iniciar leitura** habilita o modo automático, mas não
inicia imediatamente o inventário.
DI1/DI2 `True` significa **DI ATIVA / FEIXE LIVRE**; `False` significa
**DI DESATIVADA / FEIXE INTERROMPIDO**, conforme o código físico validado.
A primeira amostra apenas estabelece o estado inicial. Após ambos os feixes
estarem livres, a borda de DI1 `True → False` inicia o serviço de inventário
existente. CH2 só liga após confirmação do início pelo Zebra.

O modo automático consulta as entradas a cada 50 ms, além do tempo das operações
Modbus, sem debounce artificial. Ao detectar DI2 interrompida, solicita Stop
imediatamente; um timer independente limita cada ciclo a 60 segundos e é cancelado
na parada. Cada timer tem uma geração, impedindo interferência em ciclos novos.
As latências físicas incluem polling, comunicação serial e confirmação LLRP.

| Condição | RFID | CH1 | CH2 | CH3 |
|---|---|---|---|---|
| Sistema apto, aguardando DI1 | OFF | ON | OFF | OFF |
| Ciclo iniciado por DI1 | ON | OFF | ON | OFF |
| Internet, RFID ou Sistema indisponível, com Waveshare acessível | OFF | OFF | OFF | ON |
| Waveshare indisponível | OFF | estado desconhecido | estado desconhecido | estado desconhecido |

Somente a borda de DI2 `True → False` ou o timeout encerra o ciclo. Depois da
parada, uma nova borda de DI1 é obrigatória; manter DI1 interrompida não reinicia
o RFID. Os relés são desligados antes de ligar o próximo indicador, e seus estados
só são apresentados após confirmação. CH4–CH8 não são escritos pela automação;
DI3–DI5 continuam disponíveis apenas para diagnóstico.

Enquanto o modo automático estiver habilitado, comandos manuais de CH1–CH3 ficam
bloqueados e CH4–CH8 continuam disponíveis. **Parar leitura** cancela o timer,
para o RFID ativo e impede novos ciclos. Com o automático desligado, a tela de
diagnóstico pode assumir temporariamente o controle manual pela mesma sessão COM;
ao sair, o controle operacional é retomado.

Falha Waveshare encerra o modo automático, cancela o timer e solicita Stop RFID;
sem comunicação, os relés ficam com estado desconhecido. Falha de Internet ou do
Zebra ou do Sistema cancela o ciclo e aciona CH3 quando a Waveshare está
acessível. Após a recuperação, CH1 volta a indicar disponibilidade sem iniciar
uma leitura por si só.

O processamento de EPCs, consultas, deduplicação, tabela e contador reutilizam
a sessão existente. Validação física ainda necessária no Windows: reproduzir
feixes livres → DI1 interrompida → ambos interrompidos → feixes livres, verificar
timeout e desconexões com Waveshare/FX9600 reais. Testes automatizados usam fakes
e não comprovam funcionamento no equipamento.

## Doca e disponibilidade da base (RF013 — Windows)

Em **Configurações**, o campo **Doca** permite selecionar uma sugestão
D01–D05 ou digitar outro código. **Salvar Doca** valida e grava
`RFID_STATION_DOCK` no mesmo `.env` das configurações RFID/Waveshare, preservando
as demais chaves. Códigos aceitam até 32 letras, números, hífen ou sublinhado,
são normalizados para maiúsculas e ficam imediatamente disponíveis por
`StationConfigurationService.current()`. Ao iniciar, `load_config` carrega o valor
e a tela o apresenta; vazio significa **Configure a Doca desta estação**, sem
assumir D01. Como nas demais configurações, variáveis do ambiente do processo
têm precedência sobre o `.env`; evite definir a mesma chave nos dois lugares.
Os formulários possuem rolagem para manter campos e botões acessíveis em janelas
menores.

A barra da tela Start apresenta **RFID**, **Internet**, **Comandos** e
**Sistema**, nessa ordem. A avaliação de Base de dados continua interna, sem
indicador separado, conforme RF018 — Ajuste 01.

A operação atual usa `status` e `database` da mesma resposta health do Backend,
sem sondagem de EPC artificial, consulta SQLite ou Power Automate. A aptidão
segue Sistema/`status`, conforme ADR-013; Base de dados é um indicador
observacional. O contrato histórico do RF013/ADR-009 permanece documentado
para referência, mas não integra a composição operacional atual.

O único `ConnectionMonitor` verifica os serviços em background, no intervalo
`RFID_STATUS_CHECK_INTERVAL_SECONDS`, usando os timeouts existentes. Ao fechar,
a aplicação invalida as sessões e aguarda as requisições em andamento.
Validação física de doca, disponibilidade, relés e leitura permanece pendente.

## Verificar a configuração

Com o ambiente virtual ativado:

```bash
rfid-reader check-config
```

Também é possível executar:

```bash
python -m rfid_reader.cli check-config
```

Esse comando somente valida e apresenta a configuração; ele não acessa a rede nem
tenta se conectar ao FX9600.

## Protótipo Qt/QML — RF018, Fase 1

A prévia exige `--preview`: usa somente dados fictícios, não lê `.env`,
não acessa Backend, Zebra ou porta serial e não registra passagens.

No ambiente virtual com Python 3.12+:

```powershell
python -m pip install -e ".[dev]"
python -m rfid_reader.cli --preview
```

Também é possível executar `rfid-reader-qt --preview`. A prévia abre maximizada;
`--windowed` abre em janela. A sidebar permite comparar Corporate Dark/Navy Dark
e os cenários apto, lendo, falha, verificando e vazio. Configurações permanece
desabilitada nesse modo. Iniciar/Parar são controles apenas simulados.

Para gerar uma captura da renderização QML e encerrar:

```powershell
python -m rfid_reader.cli --preview --theme corporate --screenshot docs/evidencias/rf018/corporate-dark.png
python -m rfid_reader.cli --preview --theme navy --scenario reading --screenshot docs/evidencias/rf018/navy-dark.png
```

`--size 1600 900` altera a dimensão da captura em pixels lógicos. Os recursos
QML/SVG são locais e incluídos na distribuição Python e no bundle Windows.
Corporate Dark foi aprovado para a
integração incremental. Auditoria, decisões e rollback estão na
[ADR-015](docs/adr/ADR-015-migracao-incremental-pyside6-qml.md).

PySide6 é uma dependência de produção; instale as dependências completas para
executar os testes Qt. Hardware não é acessado pelo conjunto padrão de testes.

### Configurações locais Qt — RF018, etapa 2.1

```powershell
python -m rfid_reader.cli_qt --configure --page settings --env-file .env
```

Esse modo lê a configuração validada e permite salvar nome/IP/porta RFID,
parâmetros Waveshare, doca e URL do Backend pelos serviços existentes. As
gravações são executadas fora da thread da interface, uma por vez, preservando
as demais chaves do arquivo. Após salvar, os valores normalizados aparecem no
formulário; erros mantêm o rascunho para correção. Doca admite sugestões e texto
livre conforme a validação já existente. A tela adapta as colunas e oferece scroll.

Sem `--env-file`, utiliza o `.env` encontrado a partir do diretório atual, ou
o `.env` desse diretório se não houver arquivo. Variáveis de ambiente mantêm
prioridade sobre o arquivo, como no legado; uma variável já exportada também
prevalecerá ao reabrir depois de salvar. Não execute duas interfaces salvando
simultaneamente no mesmo arquivo: a serialização cobre esta instância, não
processos diferentes.

Start/Stop, testes de conexão e diagnóstico permanecem desabilitados. Não há
inventário, consultas, POST, monitoramento ativo, conexão COM ou comandos de relé.
Os indicadores ficam **Desconhecido** porque esse modo não inicia o monitor.
A tabela começa vazia, sem dados simulados.

Ver [captura de Configurações](docs/evidencias/rf018/configuracoes.png).

## Operação Qt — RF018

A integração operacional utiliza `ApplicationRuntime` e os serviços existentes
de Zebra, Waveshare e Backend. A composição e os widgets Tkinter foram removidos.
Para abrir a interface QML com as conexões reais em um ambiente preparado:

```powershell
python -m rfid_reader.cli --env-file .env
```

`rfid-reader`, `rfid-reader show` e `rfid-reader-qt` abrem a operação Qt.
`--operate` continua aceito como opção explícita. Iniciar Leitura habilita o modo
automático e aguarda DI1 ATIVA → DESATIVADA; o inventário termina por DI2,
Stop ou timeout de 60 segundos. A tabela e o contador recebem somente EPCs
encontrados e registrados pelo Backend, com deduplicação por sessão. POSTs
não são repetidos automaticamente em timeout. As configurações e o diagnóstico
DI1–DI5/CH1–CH8 usam os mesmos serviços e a mesma porta serial da operação.
CH1–CH3 ficam protegidos contra comandos manuais durante o modo automático.

Sistema e o estado interno de Base de dados vêm da mesma chamada health.
O monitor continua observando `database`; a interface apresenta somente
Sistema, e a aptidão preserva a regra de Sistema do ADR-013.
Configurações de conexão salvas são usadas nas próximas conexões; uma sessão
serial já aberta mantém os parâmetros com que foi iniciada.

Sem opções, os pontos de entrada e o executável Windows iniciam a operação Qt.
`--preview` e `--configure` abrem sem hardware. A substituição final foi
autorizada pelo usuário antes da homologação física, que continua pendente.
Veja o [checklist](docs/validacao/RF018-homologacao-fisica.md) e o
[relatório](docs/validacao/RF018-relatorio-operacional.md).

### Distribuição Windows

```powershell
python -m pip install -e ".[build-windows]"
python tools/build_windows.py
python tools/verify_windows.py
```

O bundle fica em `dist/DSV-RFID`; distribua a pasta inteira. QML, SVG, DLLs
e plugins Qt acompanham o executável. O `.env` real não é incorporado.
O verificador executa somente prévia/configuração com dados fictícios em uma
pasta separada, sem Python no PATH, e grava capturas em
`build/rf018-distribution-smoke`. Para operação com equipamentos preparados:

```powershell
.\dist\DSV-RFID\DSV-RFID.exe --env-file C:\RFID\estacao.env
```

## Qualidade e testes

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Testes automatizados não dependem do equipamento. A confirmação de leitura,
interrupção e desconexão no FX9600 deve ser executada manualmente no ambiente do
reader.
# project-rfid
# project-rfid
