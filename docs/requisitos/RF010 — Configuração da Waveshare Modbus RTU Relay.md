Sim. Nesse caso, faz sentido transformar o **RF009 exclusivamente na configuração da Waveshare**, sem implementar ainda leitura dos sensores nem lógica dos relés. Assim deixamos uma base limpa para o próximo requisito, que será uma tela de diagnóstico/teste das entradas digitais.

A porta **COM começa vazia na primeira execução**, enquanto os demais parâmetros Modbus usam os valores padrão que já funcionaram nos testes. O usuário poderá informar a COM, testar a comunicação e salvar a configuração.

````markdown
# RF009 — Configuração da Waveshare Modbus RTU Relay

## 1. Objetivo

Adicionar ao software RFID uma área de configuração para o módulo Waveshare utilizado no projeto.

A funcionalidade deve permitir configurar e persistir os parâmetros necessários para comunicação serial Modbus RTU com a placa.

Neste requisito NÃO deve ser implementada ainda:

- leitura dos sensores;
- acionamento dos relés;
- lógica automática entre sensores e relés;
- integração dos sensores com a leitura RFID.

O RF009 deve preparar somente a infraestrutura de configuração e teste básico de comunicação com a Waveshare.

---

# 2. Contexto

O projeto utilizará uma placa Waveshare com comunicação:

```text
Modbus RTU
````

A comunicação ocorre através de uma porta serial do computador.

Nos testes anteriores do projeto, a comunicação foi validada utilizando:

```text
Baud rate: 9600
Data bits: 8
Parity: None
Stop bits: 1
Device/Slave ID: 1
```

Esses valores devem continuar sendo utilizados como valores padrão.

A única configuração que NÃO deve possuir valor padrão é:

```text
Porta COM
```

Na primeira execução da aplicação, enquanto nenhuma porta tiver sido configurada, esse campo deve permanecer vazio.

---

# 3. Tela de configuração

Adicionar uma seção para a Waveshare dentro da área de configurações da aplicação.

Sugestão:

```text
Configurações

--------------------------------------------------

Reader RFID

Nome do Reader
[ Reader Principal                    ]

Endereço IP
[ 192.168.0.214                       ]

Porta
[ 5084                                ]

[ Testar conexão ] [ Salvar configurações ]

--------------------------------------------------

Waveshare

Porta COM
[                                      ]

Baud Rate
[ 9600                                 ]

Data Bits
[ 8                                    ]

Paridade
[ None                                 ]

Stop Bits
[ 1                                    ]

Device ID
[ 1                                    ]

[ Testar conexão ] [ Salvar configurações ]
```

A estrutura visual deve seguir o mesmo padrão já utilizado pela aplicação.

Não redesenhar a tela inteira.

---

# 4. Configurações padrão

Utilizar:

| Configuração | Valor padrão |
| ------------ | -----------: |
| Porta COM    |        vazio |
| Baud Rate    |         9600 |
| Data Bits    |            8 |
| Paridade     |         None |
| Stop Bits    |            1 |
| Device ID    |            1 |

IMPORTANTE:

A porta COM não deve receber automaticamente:

```text
COM3
COM4
COM5
```

ou qualquer outro valor.

Ela deve permanecer vazia até que o usuário informe e salve uma porta.

---

# 5. Persistência

As configurações devem utilizar o mesmo mecanismo de persistência em arquivo adotado atualmente pelo projeto.

Não criar banco de dados.

Antes de implementar, identificar:

* onde as configurações atuais são armazenadas;
* como são carregadas;
* como são atualizadas;
* como a configuração do Reader RFID foi estruturada no RF008.

Reutilizar essa arquitetura.

---

# 6. Primeira execução

Quando ainda não existir configuração salva para a Waveshare:

```text
COM = vazio
Baud Rate = 9600
Data Bits = 8
Parity = None
Stop Bits = 1
Device ID = 1
```

A ausência da COM NÃO deve ser considerada erro durante a inicialização da aplicação.

A aplicação deve iniciar normalmente mesmo sem uma Waveshare configurada.

---

# 7. Requisitos funcionais

## RF001 — Criar configuração da Waveshare

Adicionar ao modelo/configuração da aplicação os parâmetros necessários para comunicação com a Waveshare.

Campos:

```text
serial_port
baud_rate
data_bits
parity
stop_bits
device_id
```

Adaptar os nomes ao padrão já utilizado pelo projeto.

---

## RF002 — Porta COM inicialmente vazia

Caso nenhuma porta tenha sido salva anteriormente:

```text
serial_port = ""
```

A aplicação não deve assumir uma porta automaticamente.

---

## RF003 — Valores padrão

Quando não existirem valores persistidos, utilizar:

```text
baud_rate = 9600
data_bits = 8
parity = None
stop_bits = 1
device_id = 1
```

---

## RF004 — Exibir configurações

A interface deve apresentar os parâmetros atuais da Waveshare.

Quando houver configuração salva, carregar os valores persistidos.

---

## RF005 — Permitir informar porta COM

O usuário deve poder digitar manualmente a porta.

Exemplos:

Windows:

```text
COM3
COM5
COM10
```

Não limitar a aplicação às portas utilizadas durante o desenvolvimento.

---

## RF006 — Permitir salvar sem alterar os defaults

O usuário deve poder simplesmente informar:

```text
COM5
```

e salvar.

Os demais valores continuarão:

```text
9600
8
None
1
1
```

---

## RF007 — Salvar configurações

Adicionar botão:

```text
Salvar configurações
```

Ao clicar:

1. validar os campos;
2. atualizar a configuração;
3. persistir no arquivo;
4. atualizar a configuração em memória;
5. informar sucesso.

Mensagem sugerida:

```text
Configurações da Waveshare salvas com sucesso.
```

---

## RF008 — Persistir porta COM

Depois que o usuário salvar:

```text
COM5
```

ao fechar e abrir novamente a aplicação, o campo deve apresentar:

```text
COM5
```

---

# 8. Testar conexão

Adicionar botão:

```text
Testar conexão
```

Esse botão deve realizar apenas um teste básico de comunicação com a Waveshare.

NÃO realizar ainda:

* leitura contínua dos sensores;
* monitoramento;
* acionamento de CH1;
* acionamento de CH2;
* acionamento de CH3;
* lógica operacional RFID.

---

# 9. Comportamento do teste

Ao clicar em:

```text
Testar conexão
```

a aplicação deve utilizar os valores atualmente presentes no formulário.

Isso significa que o usuário pode:

1. informar `COM5`;
2. não salvar;
3. clicar em `Testar conexão`;
4. testar a COM5;
5. salvar posteriormente caso queira.

Testar conexão NÃO deve salvar automaticamente.

---

# 10. Teste Modbus

O teste deve confirmar que existe comunicação real com o dispositivo Modbus.

Não considerar como sucesso apenas conseguir executar:

```python
serial.Serial(...)
```

ou abrir a porta COM.

Abrir a porta apenas confirma que a interface serial está acessível.

Para considerar a Waveshare conectada, deve existir uma resposta Modbus válida da placa.

---

# 11. Operação utilizada para teste

Antes da implementação, o Codex deve analisar o código/protótipo que já funcionou com a Waveshare e identificar uma operação Modbus segura de leitura.

Preferencialmente utilizar uma operação somente de leitura, por exemplo a mesma leitura de entradas digitais que já tenha sido validada nos testes anteriores.

O teste NÃO deve alterar o estado dos relés.

Fluxo esperado:

```text
Abrir porta serial
        ↓
Enviar requisição Modbus de leitura
        ↓
Recebeu resposta Modbus válida?
       / \
     SIM  NÃO
      |    |
Conectado  Falha
      |
Fechar conexão
```

---

# 12. Teste bem-sucedido

Quando a placa responder corretamente:

```text
Conexão com a Waveshare realizada com sucesso.
```

A conexão utilizada no teste deve ser encerrada após a validação.

---

# 13. Falha no teste

Caso não seja possível comunicar com a placa:

```text
Não foi possível conectar à Waveshare.
```

Registrar detalhes técnicos no log.

A aplicação não deve encerrar.

---

# 14. Porta COM vazia

Caso o usuário clique em:

```text
Testar conexão
```

sem informar a porta COM:

não tentar realizar a comunicação.

Exibir:

```text
Informe a porta COM da Waveshare.
```

---

# 15. Porta inexistente

Exemplo:

```text
COM99
```

Se a porta não existir ou não puder ser aberta:

```text
Não foi possível abrir a porta COM informada.
```

A aplicação deve continuar funcionando normalmente.

---

# 16. Porta ocupada

Caso outra aplicação esteja utilizando a porta:

```text
A porta COM está sendo utilizada por outro processo.
```

Quando tecnicamente possível distinguir essa situação.

Caso contrário, apresentar a mensagem genérica de falha e registrar o detalhe técnico no log.

---

# 17. Validações

## Porta COM

Pode permanecer vazia enquanto não configurada.

Para testar conexão:

```text
obrigatória
```

Para salvar:

preferencialmente permitir salvar vazia, mantendo a Waveshare como não configurada.

---

## Baud Rate

Deve ser inteiro positivo.

Default:

```text
9600
```

---

## Data Bits

Default:

```text
8
```

Manter compatibilidade com os valores suportados pela biblioteca serial utilizada.

---

## Paridade

Default:

```text
None
```

---

## Stop Bits

Default:

```text
1
```

---

## Device ID

Default:

```text
1
```

Deve respeitar os limites aceitos pela implementação Modbus atual.

---

# 18. Ausência da Waveshare

A Waveshare deve ser tratada como um dispositivo configurável independente.

Se:

```text
COM = vazio
```

a aplicação RFID deve continuar funcionando normalmente.

Isso não deve impedir:

* abertura do software;
* conexão com Zebra FX9600;
* início da leitura RFID;
* consulta ao Power Automate;
* navegação pelas telas.

Nesta etapa, a Waveshare ainda não é obrigatória para executar a operação RFID.

---

# 19. Requisitos não funcionais

## RNF001 — Não bloquear interface

O teste da Waveshare não deve congelar a interface.

Utilizar o mecanismo de execução assíncrona/thread já adotado no projeto.

---

## RNF002 — Timeout

A comunicação deve possuir timeout.

Não deixar a aplicação aguardando indefinidamente uma resposta Modbus.

Reutilizar o timeout já utilizado no protótipo funcional quando aplicável.

---

## RNF003 — Reutilizar implementação existente

Antes de criar uma nova implementação Modbus, verificar se o projeto já contém código funcional utilizado nos testes da Waveshare.

Reutilizar ou adaptar esse código quando adequado.

---

## RNF004 — Separação de responsabilidades

Não colocar chamadas Modbus diretamente dentro do componente visual.

Estrutura conceitual:

```text
UI
 ↓
WaveshareConfig
 ↓
WaveshareService
 ↓
pymodbus / serial
 ↓
Waveshare
```

Adaptar à arquitetura real do projeto.

---

## RNF005 — Recursos devem ser liberados

Independentemente do resultado:

```text
sucesso
timeout
erro
exceção
```

a porta serial utilizada pelo teste deve ser fechada corretamente.

---

# 20. Não conectar automaticamente

Nesta etapa, NÃO estabelecer comunicação automática com a Waveshare quando a aplicação iniciar.

Também não conectar automaticamente ao:

```text
Salvar configurações
```

A conexão será utilizada somente quando o usuário clicar:

```text
Testar conexão
```

A conexão operacional permanente será definida nos requisitos posteriores.

---

# 21. Testes automatizados

Os testes automatizados não devem depender de:

* Waveshare física;
* COM real;
* USB/RS-485 real.

Utilizar mocks/fakes.

Criar testes para:

* configuração inicial;
* COM vazia;
* defaults;
* carregamento da configuração;
* salvamento;
* persistência da COM;
* alteração da COM;
* teste sem COM;
* conexão simulada com sucesso;
* timeout;
* porta inexistente;
* erro Modbus;
* liberação da conexão;
* teste não salvando configuração.

---

# 22. Teste de primeira execução

Sem configuração anterior:

Esperado:

```text
Porta COM: [           ]
Baud Rate: 9600
Data Bits: 8
Parity: None
Stop Bits: 1
Device ID: 1
```

---

# 23. Teste de persistência

Usuário informa:

```text
COM5
```

e salva.

Depois de reiniciar:

```text
Porta COM: COM5
Baud Rate: 9600
Data Bits: 8
Parity: None
Stop Bits: 1
Device ID: 1
```

---

# 24. Teste manual com hardware

Depois dos testes automatizados, realizar validação manual.

Cenário:

1. conectar adaptador USB/serial;
2. verificar a COM atribuída pelo Windows;
3. abrir a aplicação;
4. acessar configurações da Waveshare;
5. informar a COM;
6. manter os valores padrão;
7. clicar em `Testar conexão`;
8. confirmar resposta Modbus válida;
9. verificar que nenhum relé foi acionado;
10. salvar;
11. reiniciar a aplicação;
12. confirmar persistência da COM.

---

# 25. Fora do escopo do RF009

NÃO implementar ainda:

* tela de monitoramento dos sensores;
* leitura contínua de D1;
* leitura contínua de D2;
* indicadores visuais dos sensores;
* controle manual dos relés;
* CH1;
* CH2;
* CH3;
* timer;
* lógica dos sensores;
* acionamento automático dos relés;
* início automático da leitura RFID;
* parada automática da leitura RFID;
* integração Waveshare + Zebra;
* lógica operacional da esteira/processo;
* reconexão automática da Waveshare.

Essas funcionalidades serão especificadas nos próximos requisitos.

---

# 26. Atenção — preservar o restante do projeto

Esta implementação deve ser isolada.

NÃO alterar o comportamento atual de:

* Zebra FX9600;
* LLRP;
* Start/Stop da leitura RFID;
* tabela de EPCs encontrados;
* card de EPCs encontrados;
* consulta ao Power Automate;
* Configurações RFID;
* status de internet;
* navegação existente.

Não realizar refatorações não relacionadas ao RF009.

---

# 27. Processo obrigatório para o Codex

Antes de implementar:

1. ler `AGENTS.md`;
2. analisar a arquitetura atual de configurações;
3. analisar a implementação do RF008;
4. localizar o arquivo atual de configuração;
5. localizar qualquer código Waveshare/Modbus existente;
6. identificar a versão/API do `pymodbus` utilizada;
7. identificar como o projeto executa operações sem bloquear a UI;
8. identificar uma operação Modbus segura para o teste;
9. informar quais arquivos precisarão ser modificados;
10. somente então implementar.

Evitar alterar a versão do `pymodbus` sem necessidade.

---

# 28. Critérios de aceite

O RF009 será considerado concluído quando:

1. existir área de configuração da Waveshare;
2. COM iniciar vazia quando nunca configurada;
3. baud rate iniciar em 9600;
4. data bits iniciar em 8;
5. parity iniciar em None;
6. stop bits iniciar em 1;
7. device ID iniciar em 1;
8. usuário puder editar e salvar as configurações;
9. configuração persistir após reiniciar;
10. usuário puder testar sem salvar;
11. teste validar comunicação Modbus real;
12. teste não acionar relés;
13. conexão de teste for encerrada corretamente;
14. aplicação funcionar normalmente sem COM configurada;
15. nenhum comportamento RFID existente sofrer regressão;
16. testes automatizados passarem.

---

# 29. Verificações

Executar os comandos disponíveis no projeto, incluindo:

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Não instalar ou atualizar dependências sem verificar primeiro as dependências existentes.

---

# 30. Relatório final esperado

Ao concluir, informar:

* análise realizada;
* arquivos alterados;
* onde a configuração foi persistida;
* defaults utilizados;
* comportamento quando COM está vazia;
* biblioteca utilizada para Modbus;
* operação Modbus escolhida para testar a placa;
* confirmação de que o teste não aciona relés;
* tratamento de timeout;
* tratamento de porta inválida;
* confirmação de fechamento da porta;
* testes criados;
* comandos executados;
* resultado dos testes;
* validação manual pendente com a Waveshare.