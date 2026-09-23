# Waveshare Modbus RTU Relay (D) --- Referência do Projeto RFID

## 1. Objetivo

Referência permanente para o Codex sobre as configurações, testes
físicos e lógica validada da placa **Waveshare Modbus RTU Relay (D)**
usada no projeto RFID.

> **Baseline validada:** comunicação Modbus, DI1/DI2, CH1/CH2/CH3 e
> lógica de timer foram testados fisicamente e funcionaram. Não alterar
> essas regras sem requisito explícito.

## 2. Hardware e comunicação

-   Placa: Waveshare Modbus RTU Relay (D)
-   Comunicação: RS485 / Modbus RTU
-   8 entradas digitais (DI1--DI8)
-   8 saídas a relé (CH1--CH8)
-   Relés com contatos COM / NO / NC
-   Conversor: USB → RS485
-   Porta validada no Windows: `COM5`
-   Baudrate: `9600`
-   Formato: `8N1`
-   Timeout usado: `2 s`
-   Device ID: `1`

## 3. PyModbus

``` python
from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(
    port="COM5",
    baudrate=9600,
    bytesize=8,
    parity="N",
    stopbits=1,
    timeout=2,
)
```

Na versão instalada, usar `device_id=1`. Não usar `slave=1`, pois essa
assinatura gerou `TypeError`.

## 4. Entradas digitais

  Entrada     Endereço Função
  --------- ---------- -------------------
  DI1                0 Sensor de entrada
  DI2                1 Sensor de saída

Leitura validada:

``` python
resultado = client.read_discrete_inputs(
    address=0,
    count=2,
    device_id=1,
)

di1 = resultado.bits[0]
di2 = resultado.bits[1]
```

### Polaridade dos sensores

Os sensores ficam normalmente ativos:

-   `True / ON` = sensor ativo/livre
-   `False / OFF` = sensor desativado/interrompido

O evento relevante é a borda `ON → OFF`:

``` python
entrada_desativada = estado_anterior_di1 and not di1
saida_desativada = estado_anterior_di2 and not di2
```

## 5. Relés

  Relé     Endereço Função
  ------ ---------- ---------------------------------------
  CH1             0 Ambos sensores ativos / estado normal
  CH2             1 Timer ativo / leitura RFID
  CH3             2 Ambos sensores desativados

Escrita validada:

``` python
client.write_coil(
    address=address,
    value=ligado,
    device_id=1,
)
```

Evitar escritas repetitivas: só escrever quando o estado desejado do
relé mudar.

## 6. Contatos e alimentação

Os contatos `COM / NO / NC` são contatos secos. Nos testes foi adotado
`COM + NO`, de modo que a carga fica normalmente desligada e é
energizada quando o relé é acionado.

Exemplo de carga 24 VDC:

``` text
+24 V ── COM ── [RELÉ] ── NO ── (+) Carga
0 V  ─────────────────────────── (-) Carga
```

A mesma fonte 24 V pode alimentar placa, sensores e carga desde que
tenha corrente suficiente. Uma fonte separada pode ser usada para a
carga se necessário.

## 7. Timer e polling

``` python
TIMER_LIMIT = 30.0
POLL_INTERVAL = 0.05
```

Usar `time.monotonic()` para medir intervalos.

Quando DI1 faz `ON → OFF`, iniciar o timer. Quando DI2 faz `ON → OFF`,
finalizar o timer/leitura. Se DI2 não encerrar o ciclo, finalizar por
timeout após 30 segundos.

## 8. Lógica final validada

### Estado normal --- dois sensores ativos

``` text
DI1 = ON
DI2 = ON

CH1 = ON
CH2 = OFF
CH3 = OFF
```

### Leitura RFID --- timer ativo

Após DI1 fazer `ON → OFF`:

``` text
TIMER = ATIVO

CH1 = OFF
CH2 = ON
CH3 = OFF
```

CH2 representa fisicamente **LEITURA RFID ATIVA**.

### Ambos sensores desativados

``` text
DI1 = OFF
DI2 = OFF

CH1 = OFF
CH2 = OFF
CH3 = ON
```

Essa condição tem prioridade sobre o timer.

### Implementação da prioridade

``` python
if not di1 and not di2:
    ch1_desejado = False
    ch2_desejado = False
    ch3_desejado = True

elif timer_ativo:
    ch1_desejado = False
    ch2_desejado = True
    ch3_desejado = False

elif di1 and di2:
    ch1_desejado = True
    ch2_desejado = False
    ch3_desejado = False

else:
    ch1_desejado = False
    ch2_desejado = False
    ch3_desejado = False
```

**Não alterar a ordem acima sem reavaliar a máquina de estados.**

## 9. Sequência normal

``` text
1. AGUARDANDO
   DI1 ON + DI2 ON
   CH1 ON / CH2 OFF / CH3 OFF

          ↓ DI1 ON → OFF

2. LEITURA RFID
   Timer inicia
   CH1 OFF / CH2 ON / CH3 OFF

          ↓ DI2 ON → OFF

3. AMBOS INTERROMPIDOS
   DI1 OFF + DI2 OFF
   Timer/leitura finaliza
   CH1 OFF / CH2 OFF / CH3 ON

          ↓ sensores liberados

4. RETORNO AO NORMAL
   DI1 ON + DI2 ON
   CH1 ON / CH2 OFF / CH3 OFF
```

Enquanto o timer estiver ativo, um retorno momentâneo dos sensores a ON
não deve sozinho encerrar a leitura. Ela termina por DI2 `ON → OFF` ou
timeout.

## 10. Inicialização e encerramento

Fazer leitura inicial de DI1/DI2 antes de detectar bordas, evitando
falso evento na inicialização.

Ao encerrar o programa de testes:

``` python
set_relay(CH1, False)
set_relay(CH2, False)
set_relay(CH3, False)
client.close()
```

Para produção, o comportamento fail-safe definitivo deverá ser avaliado
explicitamente.

## 11. Tratamento de erros

Verificar `resultado.isError()` e tratar `ModbusException`.

`client.connect()` indica principalmente que a porta serial foi aberta;
não prova que a placa respondeu. Confirmar comunicação executando uma
operação Modbus válida, como `read_discrete_inputs()`.

## 12. Histórico de troubleshooting

Nos primeiros testes houve timeout mesmo com a porta serial abrindo. O
TX do adaptador piscava, mas a placa não respondia. Foram verificadas
inversões A/B e configurações seriais.

O cabo/conversor foi substituído e a comunicação passou a funcionar.
Portanto, em futuros timeouts verificar também:

-   conversor USB-RS485;
-   cabo;
-   porta COM;
-   A/B;
-   alimentação;
-   Device ID;
-   baudrate;
-   conexões físicas.

Não confundir RS232 (`RXD/TXD/GND`) com RS485 (`A/B`).

## 13. Integração futura com Zebra FX9600

O projeto RFID já possui leitura funcional do Zebra FX9600 via LLRP,
porta 5084.

A implementação Modbus deve permanecer encapsulada e separada da
implementação LLRP.

Arquitetura desejada:

``` text
Sensores
   ↓
Waveshare / Modbus RTU
   ↓
Módulo de I/O
   ↓
Controlador do processo
   ↓
Módulo RFID / LLRP
   ↓
Zebra FX9600
```

O código RFID não deve conhecer detalhes como endereços DI, coils,
PyModbus ou Device ID.

Eventos conceituais que o módulo poderá expor:

``` text
ENTRY_TRIGGERED
RFID_READING_STARTED
EXIT_TRIGGERED
RFID_READING_FINISHED
READ_TIMEOUT
```

CH2 representa atualmente o período em que, na integração final, o
FX9600 deverá estar lendo tags:

``` text
DI1 ON → OFF
    ├─ inicia timer
    ├─ CH2 ON
    └─ START RFID

DI2 ON → OFF
    ├─ encerra timer
    ├─ CH2 OFF
    └─ STOP RFID

TIMEOUT 30 s
    ├─ encerra timer
    ├─ CH2 OFF
    └─ STOP RFID
```

## 14. Regras para o Codex

Antes de modificar o módulo:

1.  Ler este documento.
2.  Inspecionar a implementação existente.
3.  Não alterar configurações Modbus validadas sem necessidade.
4.  Não alterar a polaridade lógica dos sensores.
5.  Não trocar DI1 e DI2.
6.  Não trocar CH1, CH2 e CH3.
7.  Preservar a detecção de borda `ON → OFF`.
8.  Preservar timeout de 30 s salvo novo requisito.
9.  Preservar a prioridade de `DI1 OFF + DI2 OFF`.
10. Não acoplar PyModbus diretamente ao módulo LLRP.
11. Manter comunicação de hardware encapsulada.
12. Evitar escritas repetitivas nos relés.
13. Usar `time.monotonic()` para intervalos.
14. Garantir fechamento da porta serial.
15. Tratar falhas Modbus.
16. Não modificar uma lógica já validada fisicamente sem requisito
    explícito.

## 15. Configuração consolidada

``` python
PORT = "COM5"
BAUDRATE = 9600
DEVICE_ID = 1

POLL_INTERVAL = 0.05
TIMER_LIMIT = 30.0

DI1 = 0
DI2 = 1

CH1 = 0
CH2 = 1
CH3 = 2
```

## 16. Status

**TESTE DE HARDWARE CONCLUÍDO COM SUCESSO.**

Validado:

-   [x] USB → RS485
-   [x] Modbus RTU
-   [x] COM5
-   [x] Device ID 1
-   [x] 9600 8N1
-   [x] PyModbus
-   [x] DI1
-   [x] DI2
-   [x] Borda ON → OFF
-   [x] Timer de 30 s
-   [x] CH1
-   [x] CH2
-   [x] CH3
-   [x] Lógica sensores + timer + relés
-   [x] CH1 com ambos sensores ativos
-   [x] CH2 durante timer/leitura
-   [x] CH3 com ambos sensores desativados

### Próxima etapa

Refatorar a lógica validada para um módulo/biblioteca reutilizável e
integrá-la ao software RFID existente com o Zebra FX9600.
