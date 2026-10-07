# ADR-007 — Configuração e teste isolado da Waveshare

- Status: Aceita
- Data: 2026-09-23
- Funcionalidade relacionada: RF010

## Contexto

A aplicação já persistia a configuração do Zebra FX9600 no arquivo `.env` e
executava testes temporários em uma thread, publicando o resultado para o
Tkinter por uma fila. A Waveshare Modbus RTU Relay (D), validada fisicamente em
um protótipo separado, precisava ser configurável pela mesma interface sem se
tornar obrigatória para o fluxo RFID.

O requisito limita esta etapa à configuração e a um teste básico de comunicação.
Leitura contínua de sensores, escrita de coils, acionamento de relés e integração
operacional com o inventário permanecem fora do escopo. Abrir a porta serial não
é evidência suficiente de que a placa respondeu, portanto o teste precisa
executar uma operação Modbus real e segura.

## Decisão

### Modelo e configuração

`WaveshareConnectionSettings` representará exclusivamente:

- porta serial;
- baud rate;
- data bits;
- paridade;
- stop bits;
- device ID.

Os valores serão carregados e validados centralmente em `config.py` pelas
variáveis:

```dotenv
WAVESHARE_SERIAL_PORT=
WAVESHARE_BAUD_RATE=9600
WAVESHARE_DATA_BITS=8
WAVESHARE_PARITY=None
WAVESHARE_STOP_BITS=1
WAVESHARE_DEVICE_ID=1
```

A porta vazia é uma configuração válida para carregar e salvar, permitindo que
a aplicação funcione sem a Waveshare. Ela passa a ser obrigatória somente na
ação explícita de teste. Os campos numéricos e a paridade são normalizados antes
de serem entregues à persistência ou à integração Modbus.

### Persistência

`DotEnvWaveshareConfigurationStore` usará o mesmo padrão já adotado para o
reader: atualizar somente as chaves sob sua responsabilidade, preservar chaves,
comentários e segredos não relacionados e substituir o `.env` atomicamente por
meio de arquivo temporário e `os.replace`.

Salvar atualizará a configuração em memória somente depois da persistência bem-
sucedida. A ação não abrirá a porta serial, não iniciará monitoramento e não
alterará a sessão LLRP.

### Integração Modbus

A integração ficará em `integrations/waveshare_modbus.py`, sem chamadas
PyModbus nos widgets ou no serviço de configuração. Será usada a série 3.15 do
`pymodbus` com o extra `serial`, limitada a `<3.16` porque o projeto da biblioteca
admite mudanças de API entre versões menores.

O adaptador mapeará a representação amigável da paridade para `N`, `E`, `O`,
`M` ou `S`. O teste usará timeout de dois segundos e nenhuma repetição interna.
Depois de abrir a porta, executará somente:

```python
client.read_discrete_inputs(
    address=0,
    count=2,
    device_id=settings.device_id,
)
```

Essa é a leitura de DI1/DI2 já validada no protótipo físico. Nenhum método de
escrita, incluindo `write_coil`, será chamado. O cliente será fechado em um
bloco `finally`, independentemente de sucesso, timeout, resposta Modbus com erro
ou falha de abertura.

### Concorrência e interface

`WaveshareConfigurationService` executará o teste em uma única thread daemon e
impedirá testes simultâneos. Eventos de início e resultado serão enviados por
uma fila dedicada, consumida pela thread do Tkinter. Dessa forma, os widgets não
são atualizados pela thread Modbus e a interface não fica bloqueada durante o
timeout.

A seção Waveshare ficará na área existente de configurações, ao lado da seção
do reader. Ela mostrará os seis parâmetros, com ações independentes de testar e
salvar. O teste usará os valores atuais do formulário e não acessará o store,
permitindo testar uma porta antes de salvá-la.

## Alternativas consideradas

### Considerar a abertura da porta como teste suficiente

Rejeitada porque confirma somente o acesso à interface serial e não a resposta
do device ID configurado.

### Escrever em um relay para validar a comunicação

Rejeitada porque altera o estado físico do processo e viola o escopo e a
segurança operacional. A leitura pontual das entradas oferece uma confirmação
Modbus sem efeitos persistentes.

### Executar o PyModbus diretamente no callback do botão

Rejeitada porque bloquearia a thread do Tkinter durante abertura, timeout e
fechamento, além de acoplar a interface à biblioteca externa.

### Conectar automaticamente ao iniciar ou salvar

Rejeitada porque a Waveshare é opcional nesta etapa e ainda não existe um ciclo
operacional ou uma política de reconexão definidos.

### Criar um arquivo de configuração separado

Rejeitada porque o `.env` já é a fonte persistente adotada pela aplicação e sua
atualização seletiva preserva as configurações existentes.

### Aceitar qualquer versão 3.x do PyModbus

Rejeitada porque a própria biblioteca documenta que versões menores podem mudar
a API. A série 3.15 contém a assinatura `device_id` usada e validada neste
projeto.

## Consequências

### Positivas

- a primeira execução mantém a porta vazia e não impede o uso do RFID;
- configuração, formulário e persistência compartilham a mesma validação;
- testar não salva e salvar não conecta;
- o teste confirma resposta Modbus real sem acionar relés;
- timeout e execução em thread preservam a responsividade da interface;
- a conexão temporária é sempre encerrada;
- detalhes PyModbus e endereços DI permanecem fora da UI e do código LLRP;
- todos os fluxos podem ser testados sem hardware por meio de protocolos e
  fakes.

### Limitações aceitas

- não há conexão, monitoramento ou reconexão automática da Waveshare;
- não há leitura contínua, eventos de sensores ou controle de relés;
- quando o PyModbus não expõe a causa da falha ao abrir a porta, a aplicação
  apresenta a mensagem de porta indisponível e mantém o detalhe no log;
- a confirmação final com COM e Waveshare reais continua sendo uma validação
  manual de hardware.

## Escopo preservado

Não há alteração no monitor do FX9600, sessão LLRP, inventário, tabela e resumo
de EPCs, consulta ao Power Automate ou status de internet. A leitura Modbus
pontual só ocorre após clique explícito em **Testar conexão**.

## Validação

Os testes automatizados cobrem defaults, porta vazia, validação, persistência,
recarga do `.env`, teste sem salvar, sucesso, timeout, porta indisponível, porta
ocupada, erro Modbus, prevenção de testes simultâneos, fila da interface e
fechamento da conexão.

A validação manual com a Waveshare física permanece pendente e deverá confirmar
a COM atribuída pelo Windows, a resposta Modbus e a ausência de acionamento dos
relés.
