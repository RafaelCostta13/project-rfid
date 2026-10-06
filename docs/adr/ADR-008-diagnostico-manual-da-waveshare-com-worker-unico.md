# ADR-008 — Diagnóstico manual da Waveshare com worker único

- Status: Aceita
- Data: 2026-09-24
- Funcionalidade relacionada: RF011
- Complementa: ADR-007

## Contexto

A ADR-007 definiu a configuração da Waveshare e um teste pontual que lê DI1/DI2
e fecha a porta COM. O RF011 acrescenta uma tela de diagnóstico que precisa
manter a comunicação aberta para observar cinco entradas digitais e controlar
manualmente oito relés. Polling e comandos compartilham a mesma conexão Modbus
RTU; acessos simultâneos à serial podem misturar requisições e respostas.

A interface Tkinter deve continuar responsiva durante abertura, timeout,
leitura, escrita e fechamento. O diagnóstico usa a configuração Waveshare já
salva em memória e não participa da sessão RFID.

O código físico anterior validou a leitura de DI1/DI2 e a escrita de CH1–CH3.
Para os demais canais, o [manual da Waveshare Modbus RTU Relay (D)][manual]
documenta entradas e coils nos endereços 0–7. A correspondência de D3–D5 e
CH4–CH8 ainda precisa de confirmação na placa utilizada pelo projeto.

## Decisão

### Sessão e concorrência

`WaveshareDiagnosticService` possuirá uma única thread de comunicação por
sessão. Ela abrirá um cliente `WaveshareDiagnosticPort`, fará polling das
entradas a cada 500 ms e processará comandos manuais de relé em uma fila. Só
essa thread acessará o cliente Modbus, serializando leitura e escrita sem um
segundo lock para a porta.

O indicador global de Waveshare seguirá o monitor periódico já usado por RFID
e Internet. Fora do diagnóstico, ele fará uma leitura Modbus temporária para
confirmar a resposta da placa, usando a configuração atual. O teste da tela de
configurações, a verificação periódica e a sessão de diagnóstico compartilharão
uma proteção da porta serial. Quando o diagnóstico ocupar a COM, o monitor
consultará o estado dessa sessão sem abrir outro cliente. A ausência de COM
configurada será mostrada como **Desconectado**.

O botão **Conectar** obterá `WaveshareConfigurationService.current()`. Uma porta
COM vazia será rejeitada antes de criar o cliente. A abertura da COM só será
considerada conexão depois de uma leitura Modbus válida das entradas. A
interface receberá eventos por uma fila própria, consumida na thread do
Tkinter; o worker não modificará widgets.

### Endereços e confirmação

O adaptador Modbus, e não a interface, mapeará D1–D5 para `read_discrete_inputs`
com endereço inicial 0 e quantidade 5. Ele consultará CH1–CH8 por `read_coils`
com endereço inicial 0 e quantidade 8. Cada botão de relé usará `write_coil`
no endereço `canal - 1`, com o `device_id` configurado, e lerá o coil novamente.
O estado visual só será atualizado quando a leitura de retorno confirmar o
valor solicitado.

Antes da primeira leitura e após desconexão, entradas e relés serão exibidos
como **Desconhecido**. Se a consulta inicial dos coils falhar, os relés
permanecerão desconhecidos; seu estado não será presumido. Uma falha de comando
também deixará o canal afetado como desconhecido e produzirá mensagem e log.

### Ciclo de vida

Uma falha no polling encerrará a sessão, fechará o cliente e emitirá evento de
desconexão. **Desconectar** e **Voltar** solicitarão a parada do worker; o
fechamento da aplicação aguardará a finalização da thread e a liberação da COM.
Nenhum estado de entrada acionará relé ou inventário RFID automaticamente.

## Alternativas consideradas

### Uma thread para polling e outra para comandos, protegidas por lock

Permite implementar as duas rotinas separadamente, mas exige coordenar lock,
parada e ordem das operações na mesma serial. Um worker com fila atende ao
diagnóstico com menos estados concorrentes.

### Abrir uma conexão por leitura ou comando

Rejeitada porque criaria disputas pela COM, repetiria o custo de abertura e
impediria uma sessão de diagnóstico com estado de conexão claro.

### Executar Modbus nos handlers do Tkinter

Rejeitada porque os dois segundos de timeout configurados poderiam congelar a
interface em cada operação.

### Mostrar o estado solicitado assim que o usuário clica

Rejeitada porque uma resposta de escrita com erro, timeout ou falha de leitura
posterior não comprova o estado físico do relé.

## Consequências

- A porta COM é usada por uma sessão de diagnóstico de cada vez, com leitura e
  escrita serializadas.
- A tela usa a configuração existente; abrir a tela não conecta nem aciona
  relés.
- O estado dos relés depende de leitura de coils. Se ela não for confiável no
  hardware instalado, a tela mostra **Desconhecido**.
- O intervalo de 500 ms é fixo nesta versão e pode ser revisto após medir a
  resposta da placa real.
- A sessão de diagnóstico é independente do teste pontual da ADR-007 e do
  inventário RFID. Se outra aplicação ocupar a COM, a conexão poderá falhar.
- O indicador global representa a disponibilidade Modbus: uma leitura temporária
  pode mostrar **Conectado** mesmo quando a tela de diagnóstico está fechada.
- Testes com fakes verificam regras e limpeza sem equipamento. Ruff, Mypy,
  Pytest e a validação física no Windows permanecem pendentes; esta ADR não
  afirma que D3–D5 ou CH4–CH8 já foram testados na placa real.

[manual]: https://www.waveshare.com/wiki/Modbus_RTU_Relay_%28D%29
