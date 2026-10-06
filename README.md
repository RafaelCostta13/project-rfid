# RFID Reader

Aplicação Python para comunicação com leitores RFID, inicialmente o Zebra FX9600.
A tela principal apresenta o estado da sessão LLRP e do acesso à internet, além
de permitir iniciar e parar um inventário manual para visualizar os EPCs
confirmados pela base consultada.

## Requisitos

- Python 3.12 ou superior;
- `pip`;
- suporte Tkinter do Python (normalmente incluído no Windows; no Linux pode exigir
  o pacote `python3-tk`);
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

Para consultar os EPCs pelo fluxo do Power Automate, configure também:

```dotenv
SHAREPOINT_LOOKUP_URL=https://endpoint-do-fluxo
SHAREPOINT_LOOKUP_TIMEOUT_SECONDS=10
SHAREPOINT_LOOKUP_QUEUE_SIZE=100
```

`SHAREPOINT_LOOKUP_URL` é obrigatória e pode conter uma assinatura de acesso.
Mantenha seu valor somente no `.env`; a aplicação não exibe nem registra essa URL
nos logs.

A Waveshare Modbus RTU Relay é opcional nesta etapa. A porta serial começa
vazia; os demais parâmetros usam os valores validados no protótipo:

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
rfid-reader show
```

A aplicação mantém uma única sessão LLRP com o FX9600 e a reutiliza tanto para o
status quanto para o inventário manual. Na página **Start**, use **Iniciar
leitura** e **Parar leitura** para controlar o inventário. A tabela apresenta
somente EPCs confirmados pela base, com status, cliente, nota fiscal, volume,
pedido e doca quando disponibilizados pelo Power Automate. EPCs não encontrados,
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
o arquivo. O salvamento preserva as demais chaves e prepara os novos dados para a
próxima conexão, sem interromper ou reconectar automaticamente a sessão atual.

Na mesma área de **Configurações**, a seção **Waveshare** permite testar e salvar
os parâmetros Modbus RTU. O teste usa somente uma leitura pontual de DI1/DI2,
fecha a porta em seguida e não aciona relés. Salvar não conecta automaticamente à
placa, e a ausência de porta configurada não impede o funcionamento do RFID.

O botão **Testar Waveshare**, dentro da mesma seção, abre o diagnóstico manual.
Use **Conectar** para acompanhar D1–D5 e consultar o estado de CH1–CH8; cada
relé pode ser ligado ou desligado separadamente. **Voltar** encerra o teste e
devolve a sessão COM ao controle operacional. A tela usa a configuração salva,
não aciona relés por conta própria e não inicia o inventário RFID.

## Operação automática por sensores (RF012 — Windows)

O worker operacional da Waveshare utiliza uma única sessão serial. Quando
Internet, RFID, Waveshare e Base de dados estão conectados, CH1 indica que o
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
| Internet, RFID ou Base de dados indisponível, com Waveshare acessível | OFF | OFF | OFF | ON |
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
Zebra ou da Base de dados cancela o ciclo e aciona CH3 quando a Waveshare está
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

O indicador **Base de dados** usa o mesmo padrão visual dos demais: inicia em
**Verificando** e só mostra **Conectado** após resposta HTTP/JSON válida da fonte
remota. **Erro** ou **Desconectado** significam base não operacional.

A verificação reutiliza `SharePointLookupClient` e `SHAREPOINT_LOOKUP_URL`, com
POST `{"epc": "<DATABASE_CHECK_EPC>"}`. O EPC padrão de sondagem contém 24 zeros;
ele não representa uma leitura física e seu resultado não entra na tabela,
fila de leituras ou contador. O contrato existente considera tanto etiqueta
encontrada quanto não encontrada como consultas válidas. Não há download completo
da Doca, chamada de sincronização, SQLite ou persistência de itens/timestamps.
Essa consulta não depende de Doca; a ausência de Doca não impede este teste.

`DATABASE_CHECK_INTERVAL_SECONDS` tem padrão 60 e mínimo 30 segundos. O
`ConnectionMonitor` executa o verificador em background; as chamadas remotas
respeitam esse intervalo após a conclusão da anterior, com resolução do intervalo
geral `RFID_STATUS_CHECK_INTERVAL_SECONDS` (padrão 5 segundos). O timeout é o
existente `SHAREPOINT_LOOKUP_TIMEOUT_SECONDS` (padrão 10 segundos). Timeout, erro
HTTP, autenticação, rede ou resposta inválida deixam a base indisponível. Logs
informam a categoria da falha e o código HTTP, sem URL, resposta ou credenciais.
Sem Internet, novas sondagens ficam suspensas; após recuperação observada, a
próxima passagem pelo monitor pode consultar novamente. Ao fechar, não são
iniciadas novas chamadas e a aplicação aguarda a requisição em andamento.

Todos os quatro serviços precisam estar conectados para habilitar novos ciclos.
Base indisponível também cancela um ciclo ativo pela regra já existente do RF012:
CH1 OFF, CH2 OFF, CH3 ON quando a Waveshare responde. A recuperação permite
voltar a CH1 sem iniciar automaticamente um ciclo. CH4–CH8, sensores, timer de
60 segundos e consultas operacionais dos EPCs permanecem com o fluxo existente.

Limitação: o repositório não contém contrato executável de uma operação leve do
novo fluxo de sincronização. Não se usa `modifiedSince=""`, pois pode provocar
carga completa. Validar no Power Automate real que uma falha do SharePoint gera
erro HTTP/contrato, e não uma resposta normal de “não encontrado”. O cliente não
consegue distinguir falhas que o servidor disfarça como resposta válida.
Consulte [ADR-009](docs/adr/ADR-009-doca-e-status-da-base-remota.md).

Validação manual pendente no Windows: salvar D01, reabrir, trocar por D05;
observar o indicador com o fluxo disponível e indisponível mantendo Internet;
confirmar CH1/CH3 e bloqueio dos ciclos no FX9600/Waveshare reais. Os testes
automatizados usam transporte HTTP falso e não comprovam a integração física.

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
