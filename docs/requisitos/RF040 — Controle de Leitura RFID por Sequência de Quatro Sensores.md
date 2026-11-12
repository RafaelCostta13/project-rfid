# RF040 — Controle de Leitura RFID por Sequência de Quatro Sensores

Projeto: DSV RFID System
Requisito: RF040
Requisitos relacionados: RF012, RF037
Categoria: RFID / Automação / Waveshare / Sensores
Tecnologia: Python + PySide6/QML
Hardware: Zebra FX9600 + Waveshare Modbus RTU Relay D
Sistema operacional: Windows
Prioridade: Alta

---

## 1. OBJETIVO

Modificar a lógica de acionamento dos sensores
do portal RFID.

Atualmente, o sistema utiliza:

    DI1 — Sensor de entrada
    DI2 — Sensor de saída
    DI3 — Pedal de reabertura

Agora foram instalados mais dois sensores:

    DI4 — Segundo sensor de entrada
    DI5 — Primeiro sensor de saída

O objetivo é implementar uma validação
sequencial para iniciar e encerrar
a leitura RFID.

NOVA REGRA DE INÍCIO:

    DI1 → DI4 → INICIAR LEITURA

NOVA REGRA DE ENCERRAMENTO:

    DI5 → DI2 → ENCERRAR PASSAGEM

O pedal DI3 deverá continuar funcionando
conforme o requisito RF037.

IMPORTANTE:

A ordem de acionamento é obrigatória.

Não basta que dois sensores estejam
acionados simultaneamente.

O sistema deverá identificar
a sequência correta de eventos.

QUALQUER OUTRA SEQUÊNCIA NÃO DEVERÁ
INICIAR OU ENCERRAR UMA PASSAGEM RFID.

Preservar as proteções de segurança
e os controles manuais existentes.

---

## 2. CONTEXTO OPERACIONAL

O portal RFID utiliza sensores
fotoelétricos para identificar
a passagem de caixas.

A lógica anterior utilizava
um sensor para iniciar
e outro para encerrar a passagem.

Com a instalação de quatro sensores,
queremos garantir que a movimentação
ocorra na direção correta.

A sequência de entrada será:

    DI1 → DI4

A sequência de saída será:

    DI5 → DI2

Assim, o sistema poderá validar
a direção e a ordem dos acionamentos,
reduzindo leituras iniciadas ou
encerradas incorretamente.

O pedal DI3 continuará sendo utilizado
para leitura complementar após timeout.

---

## 3. MAPEAMENTO DAS ENTRADAS

A placa utilizada é:

    Waveshare Modbus RTU Relay D

Entradas digitais:

    DI1 — Sensor de entrada 1

    DI2 — Sensor de saída 2

    DI3 — Pedal de reabertura

    DI4 — Sensor de entrada 2

    DI5 — Sensor de saída 1

Sequência física esperada:

    ENTRADA                           SAÍDA
       |                                 |
       v                                 v

      DI1 ------ DI4 ------ DI5 ------ DI2
                    |
                    |
               ÁREA DE LEITURA
                    |
                    |
              ANTENAS RFID

O pedal DI3 é um acionamento manual
independente dos sensores de passagem.

Não alterar o mapeamento das entradas.

---

## 4. INTERPRETAÇÃO DOS SENSORES

IMPORTANTE:

No projeto atual, os sensores
fotoelétricos possuem uma interpretação
elétrica já estabelecida.

O estado normal do sensor corresponde
ao sinal ativo da entrada digital.

A interrupção da barreira fotoelétrica
é interpretada como acionamento
operacional do sensor.

Portanto:

    Sensor acionado = barreira interrompida.

O Codex deverá preservar
essa interpretação existente.

Não assumir que o acionamento
corresponde obrigatoriamente
ao nível elétrico HIGH ou LOW.

Utilizar a normalização existente
no serviço Waveshare.

A sequência deverá considerar
eventos de acionamento,
não apenas o estado atual das entradas.

Exemplo:

    DI1 detectou interrupção.

    Depois DI4 detectou interrupção.

    Resultado: sequência válida.

A simples leitura de DI1 e DI4
simultaneamente interrompidos
não comprova a ordem dos eventos.

---

## 5. FLUXO OPERACIONAL COMPLETO

A nova sequência será:

    SISTEMA PRONTO
           |
           v
    AGUARDAR DI1
           |
           v
    DI1 ACIONADO
           |
           v
    AGUARDAR DI4
           |
           v
    DI4 ACIONADO
           |
           v
    INICIAR INVENTÁRIO RFID
           |
           v
    TEMPORIZADOR 60 SEGUNDOS
           |
           |
           +------ DI5 → DI2
           |             |
           |             v
           |      ENCERRAMENTO
           |      DEFINITIVO
           |
           |
           +------ TIMEOUT
                         |
                         v
                 PARAR INVENTÁRIO
                         |
                         v
                 AGUARDAR DI3
                 OU SAÍDA VÁLIDA
                         |
                         +---- DI3
                         |      |
                         |      v
                         | REABRIR LEITURA
                         | MESMA PASSAGEM
                         |
                         +---- DI5 → DI2
                                |
                                v
                         ENCERRAMENTO
                         DEFINITIVO

REGRAS FUNDAMENTAIS:

1. DI1 isoladamente não inicia leitura.

2. DI4 isoladamente não inicia leitura.

3. DI1 seguido de DI4 inicia a leitura.

4. DI2 isoladamente não encerra a passagem.

5. DI5 isoladamente não encerra a passagem.

6. DI5 seguido de DI2 encerra a passagem.

7. DI3 preserva a lógica de reabertura
   após timeout.

8. O timeout para o inventário,
   mas não encerra definitivamente
   a passagem.

9. A passagem só será encerrada
   normalmente pela sequência DI5 → DI2.

10. Stop manual e condições de segurança
    permanecem funcionando conforme
    as regras existentes.

---

## 6. REGRA DE INÍCIO — DI1 → DI4

O inventário RFID somente poderá iniciar
quando o sistema detectar a sequência:

    Primeiro: DI1

    Depois: DI4

### 6.1 Primeiro acionamento

Quando DI1 for acionado:

    Registrar o evento de DI1.

    Armar a sequência de entrada.

    Aguardar o acionamento de DI4.

NÃO iniciar inventário nesse momento.

NÃO iniciar temporizador.

NÃO ativar CH2.

### 6.2 Segundo acionamento

Quando DI4 for acionado depois
de um DI1 válido:

    Confirmar sequência correta.

    Iniciar inventário RFID.

    Iniciar temporizador de 60 segundos.

    Atualizar o estado operacional.

    Ativar CH2.

    Desativar CH1.

    Manter CH3 desativado,
    se não houver erro.

### 6.3 Sequência inválida

Se DI4 for acionado antes de DI1:

    Ignorar o evento para início.

    Não iniciar inventário.

    Não iniciar temporizador.

    Não ativar CH2.

Se DI1 for acionado posteriormente,
será necessário um novo evento
válido de DI4 para iniciar a leitura.

Não aproveitar retroativamente
o acionamento anterior de DI4.

---

## 7. REGRA DE ENCERRAMENTO — DI5 → DI2

O encerramento definitivo da passagem
somente poderá ocorrer quando o sistema
detectar a sequência:

    Primeiro: DI5

    Depois: DI2

### 7.1 Primeiro acionamento

Quando DI5 for acionado durante
uma passagem válida:

    Registrar o evento de DI5.

    Armar a sequência de saída.

    Aguardar o acionamento de DI2.

NÃO encerrar a passagem nesse momento.

NÃO limpar os registros.

NÃO zerar os contadores.

NÃO encerrar antecipadamente
o inventário apenas por DI5.

### 7.2 Segundo acionamento

Quando DI2 for acionado depois
de um DI5 válido:

    Confirmar sequência correta.

    Parar o inventário,
    se estiver ativo.

    Cancelar o temporizador,
    se estiver ativo.

    Encerrar definitivamente a passagem.

    Invalidar a possibilidade
    de reabertura pelo DI3.

    Aplicar o estado operacional
    de passagem encerrada.

### 7.3 Sequência inválida

Se DI2 for acionado antes de DI5:

    Não encerrar a passagem.

    Não parar o inventário
    por encerramento normal.

    Não limpar dados.

    Não alterar contadores.

Um DI5 posterior não poderá
aproveitar retroativamente
o acionamento anterior de DI2.

Será necessário um novo evento
válido de DI2 depois de DI5.

IMPORTANTE:

A lógica antiga, em que DI2 sozinho
encerrava a passagem, deverá ser
substituída pelo novo pareamento.

---

## 8. PRESERVAR O PEDAL DI3 — RF037

O pedal continuará conectado à DI3.

Sua função permanece:

    Reabrir uma leitura interrompida
    pelo timeout de 60 segundos.

Condições para reabertura:

1. A passagem foi iniciada corretamente
   pela sequência DI1 → DI4.

2. O inventário foi parado por timeout.

3. A passagem ainda não foi encerrada
   pela sequência DI5 → DI2.

4. O modo automático continua habilitado.

5. O sistema está operacional.

6. Não existe condição de segurança
   impedindo a leitura.

Ao acionar DI3:

    Reabrir o inventário RFID.

    Reiniciar o temporizador em 60 segundos.

    Preservar todos os EPCs anteriores.

    Preservar os registros da tabela.

    Preservar os contadores.

    Manter a mesma passagem.

Não criar uma nova sessão lógica.

Não executar uma nova sequência
de entrada DI1 → DI4 para reabrir
a passagem pelo pedal.

O DI3 funciona independentemente
da sequência de entrada,
mas somente após um início válido
e um timeout.

---

## 9. DI3 APÓS ENCERRAMENTO

Depois de uma sequência válida:

    DI5 → DI2

A passagem estará
definitivamente encerrada.

Nesse estado:

    DI3 não poderá reabrir a leitura.

    DI3 não poderá reiniciar o timer.

    DI3 não poderá reutilizar
    a passagem anterior.

Para iniciar uma nova passagem,
será obrigatória uma nova sequência:

    DI1 → DI4

IMPORTANTE:

DI5 ou DI2 isolados não devem
ser tratados como encerramento
definitivo da passagem.

O bloqueio definitivo do pedal
por encerramento normal deverá ocorrer
quando a sequência completa
DI5 → DI2 for confirmada.

Preservar os bloqueios já existentes
decorrentes de erro ou Stop manual.

---

## 10. TEMPORIZADOR DE 60 SEGUNDOS

Preservar o temporizador atual.

O temporizador deverá iniciar somente:

- Após DI1 → DI4 válido.
- Após uma reabertura válida pelo DI3.

Não iniciar timer:

- Apenas por DI1.
- Apenas por DI4.
- Por DI4 → DI1.
- Apenas por DI5.
- Apenas por DI2.

Quando o temporizador chegar a zero:

    Parar o inventário RFID.

    Desativar CH2.

    Ativar CH1, se o sistema
    estiver operacional.

    Preservar a passagem.

    Preservar os EPCs.

    Preservar a tabela.

    Preservar os contadores.

    Permitir a reabertura por DI3,
    enquanto a passagem estiver elegível.

O timeout NÃO deverá ser confundido
com o encerramento definitivo
pela sequência de saída.

Se DI5 → DI2 ocorrer após o timeout,
o sistema deverá encerrar
definitivamente a passagem,
mesmo que o inventário já esteja parado.

---

## 11. CONTROLE DE SEQUÊNCIA

Implementar um controle de estados
para validar a ordem dos acionamentos.

Não utilizar apenas condições como:

    if DI1 and DI4:
        iniciar_leitura()

Ou:

    if DI5 and DI2:
        encerrar_leitura()

Essas condições não garantem
que os sensores foram acionados
na ordem correta.

Utilizar eventos de transição
das entradas digitais.

Estados conceituais sugeridos:

    AGUARDANDO_ENTRADA_DI1

    AGUARDANDO_ENTRADA_DI4

    LEITURA_ATIVA

    AGUARDANDO_COMPLEMENTACAO

    AGUARDANDO_SAIDA_DI2

    PASSAGEM_ENCERRADA

    ERRO

O Codex deverá analisar
o controlador existente e integrar
os estados necessários.

Não criar um segundo controlador
independente para o mesmo processo.

O estado de saída aguardando DI2
deverá ser compatível com:

- Inventário ainda ativo.
- Inventário parado por timeout.

A leitura física e a sequência de saída
são conceitos distintos.

---

## 12. EVENTOS INVÁLIDOS

O sistema deverá ignorar eventos
que não atendam às sequências exigidas.

### Caso 1

    DI4 → DI1

Resultado:

    Não iniciar leitura.

### Caso 2

    DI1 → DI2

Resultado:

    Não iniciar leitura.

    Não encerrar passagem.

### Caso 3

    DI1 → DI5

Resultado:

    Não iniciar leitura.

### Caso 4

    DI2 → DI5

Resultado:

    Não encerrar passagem.

### Caso 5

    DI1 → DI4

Resultado:

    Iniciar leitura.

### Caso 6

    DI1 → DI4 → DI2

Resultado:

    DI1 → DI4 inicia leitura.

    DI2 isolado não encerra
    a passagem.

### Caso 7

    DI1 → DI4 → DI5

Resultado:

    Leitura permanece ativa,
    se o timer não terminou.

    Aguardar DI2 para encerramento.

### Caso 8

    DI1 → DI4 → DI5 → DI2

Resultado:

    Iniciar leitura após DI4.

    Encerrar definitivamente após DI2.

### Caso 9

    DI1 → DI4 → TIMEOUT → DI3

Resultado:

    Reabrir leitura da mesma passagem.

### Caso 10

    DI1 → DI4 → DI5 → DI2 → DI3

Resultado:

    Passagem encerrada.

    DI3 ignorado.

### Caso 11

    DI1 → DI4 → TIMEOUT → DI3 → DI5 → DI2

Resultado:

    Reabrir a passagem após DI3.

    Encerrar definitivamente após DI2.

### Caso 12

    DI1 → DI4 → DI3

Com inventário ainda ativo:

    DI3 ignorado.

    Timer não reiniciado.

---

## 13. EVENTOS CONCORRENTES E RESET

O Codex deverá garantir que eventos
de sensores não sejam reaproveitados
indevidamente entre passagens.

Regras:

- Uma passagem encerrada não poderá
  reutilizar o DI1 da passagem anterior.

- Um DI4 recebido antes de DI1
  não poderá iniciar leitura posteriormente
  sem novo acionamento.

- Um DI2 recebido antes de DI5
  não poderá encerrar a passagem
  posteriormente sem novo acionamento.

- Limpar estados pendentes
  ao encerrar definitivamente a passagem.

- Limpar sequências pendentes
  após Stop manual ou erro impeditivo,
  conforme o ciclo de recuperação existente.

- Evitar que um novo DI1 durante
  uma passagem em andamento
  crie outra passagem.

- Não aceitar novas sequências de entrada
  enquanto existir uma passagem ativa
  ou aguardando complementação.

Se o operador reabrir a leitura pelo DI3
com uma sequência de saída incompleta
pendente, invalidar esse pareamento
para evitar que um DI2 posterior
encerre a passagem baseado
em um DI5 antigo.

Uma nova finalização deverá exigir:

    Novo DI5 → Novo DI2

---

## 14. DEBOUNCE E DETECÇÃO DE BORDA

A leitura dos sensores deverá utilizar
o mecanismo de polling/eventos
já implementado na Waveshare.

Preservar o debounce existente.

Evitar:

- Múltiplos eventos por uma interrupção.
- Repetições enquanto o sensor
  permanece interrompido.
- Inícios duplicados.
- Encerramentos duplicados.
- Reaberturas indevidas.

Uma sequência somente poderá ser
confirmada quando o software observar
os eventos na ordem correta.

Se DI1 e DI4 já estiverem interrompidos
na inicialização do aplicativo,
não presumir uma sequência válida.

Não iniciar inventário automaticamente
sem identificar um novo ciclo válido
de acionamento dos sensores.

O mesmo vale para DI5 e DI2.

Caso a ordem não possa ser determinada
com segurança em um mesmo ciclo
de polling, não assumir que
a sequência foi correta.

---

## 15. CONTROLE DOS RELÉS

Preservar o funcionamento existente
dos relés da Waveshare.

### Sistema pronto

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

### DI1 acionado, aguardando DI4

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

O inventário ainda não começou.

### DI1 → DI4 confirmado

    CH1 = OFF
    CH2 = ON
    CH3 = OFF

### Leitura reaberta pelo DI3

    CH1 = OFF
    CH2 = ON
    CH3 = OFF

### Timeout

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

### DI5 acionado, aguardando DI2

Se o inventário estiver ativo:

    CH1 = OFF
    CH2 = ON
    CH3 = OFF

Não parar antecipadamente
o inventário apenas por DI5.

Se o inventário já terminou por timeout,
preservar o estado de inventário parado.

### DI5 → DI2 confirmado

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

### Erro

Preservar:

    CH1 = OFF
    CH2 = OFF
    CH3 = ON

IMPORTANTE:

O acionamento dos relés deverá
continuar sendo responsabilidade
do controlador operacional existente.

Não adicionar comandos Modbus
diretamente nos novos handlers
dos sensores.

---

## 16. PRESERVAÇÃO DOS DADOS

Preservar a lógica atual
de armazenamento dos EPCs.

Durante:

    DI1 → DI4

    TIMEOUT

    DI3

    DI5 → DI2

O sistema deverá manter
os dados pertencentes
à mesma passagem.

Não apagar EPCs durante timeout.

Não apagar EPCs durante reabertura.

Não duplicar registros.

Não reiniciar a contagem
ao pressionar o pedal.

Novos EPCs encontrados
deverão ser adicionados normalmente.

Preservar:

- Status.
- Cliente.
- Nota Fiscal.
- Volume.
- Pedido.
- Doca.
- Dealer.

Preservar a lógica do RF023
e a deduplicação existente.

---

## 17. BACKEND RFID

Preservar a integração
com o backend Rails.

Endpoints existentes:

    GET /api/v1/rfid_records/:epc

    POST /api/v1/rfid_reads

A alteração da sequência
dos sensores não deverá modificar
o contrato da API.

Regras:

- A abertura válida da passagem
  ocorre após DI1 → DI4.

- O timeout encerra apenas
  a janela de inventário.

- O pedal DI3 continua
  a mesma passagem.

- O encerramento normal definitivo
  ocorre após DI5 → DI2.

- Não duplicar GET para EPCs
  já processados.

- Não duplicar POST
  para a mesma leitura já registrada.

- Preservar a rastreabilidade
  dos registros.

O Codex deverá verificar
se existem rotinas atuais
executadas diretamente
no acionamento isolado de DI1 ou DI2.

Essas rotinas deverão ser acionadas
pelos novos eventos validados,
quando relacionadas à abertura
ou encerramento normal da passagem.

Não alterar serviços que não
tenham relação com a sequência
dos sensores.

---

## 18. PRESERVAR ÁUDIO E INTERFACE

Não modificar:

- RF033 — Bip sonoro.
- RF035 — Notificação por voz.
- RF034 — Simulador RFID.
- RF036 — Layout de configurações.
- RF038 — Configuração de antenas.
- RF039 — Mapa de leitura RFID.

Preservar a tela Start.

Não alterar as sete colunas
da tabela operacional.

O objetivo deste requisito
é modificar exclusivamente
o controle de acionamento
dos sensores de entrada e saída.

Não criar novos cards.

Não reorganizar o layout.

Se existir uma área de diagnóstico
das entradas da Waveshare,
ela deverá continuar exibindo
corretamente DI1 até DI5.

---

## 19. SEGURANÇA OPERACIONAL

A nova lógica deverá preservar
os mecanismos de segurança existentes.

Não permitir que uma sequência válida
ignore condições impeditivas como:

- Falha na Waveshare.
- Falha no Zebra FX9600.
- Stop manual.
- Modo automático desabilitado.
- Estados de erro existentes.

Preservar as regras de acionamento
do CH3 para falhas operacionais.

Se o projeto possuir uma regra
de erro baseada na combinação
de estados dos sensores,
o Codex deverá verificar se ela
continua compatível com o novo
posicionamento físico de DI1, DI4,
DI5 e DI2.

Não remover nem modificar
silenciosamente proteções existentes.

Caso uma regra de segurança antiga
entre em conflito com a nova
sequência física, documentar
o conflito antes de alterá-la.

IMPORTANTE:

O requisito de sequência obrigatória
não elimina a necessidade
de paradas manuais ou por segurança.

O sistema poderá parar por timeout,
Stop ou erro impeditivo,
sem considerar esses eventos
um encerramento normal de passagem
pela sequência de saída.

---

## 20. TESTES OBRIGATÓRIOS

### Teste 1 — DI1 isolado

Acionar somente DI1.

Resultado:

    Inventário não inicia.

    Timer não inicia.

    CH2 permanece desligado.

### Teste 2 — Entrada correta

Acionar:

    DI1 → DI4

Resultado:

    Inventário inicia.

    Timer inicia em 60 segundos.

    CH2 liga.

### Teste 3 — Entrada invertida

Acionar:

    DI4 → DI1

Resultado:

    Inventário não inicia.

### Teste 4 — DI4 isolado

Acionar somente DI4.

Resultado:

    Nenhuma leitura iniciada.

### Teste 5 — Saída correta

Com passagem válida, acionar:

    DI5 → DI2

Resultado:

    Inventário para.

    Passagem encerrada definitivamente.

    CH1 ligado.

    CH2 desligado.

### Teste 6 — Saída invertida

Acionar:

    DI2 → DI5

Resultado:

    Não encerrar passagem.

### Teste 7 — DI2 isolado

Durante leitura ativa,
acionar somente DI2.

Resultado:

    Não encerrar a passagem
    pelo fluxo normal.

    Não finalizar registros
    por encerramento normal.

### Teste 8 — DI5 isolado

Durante leitura ativa,
acionar somente DI5.

Resultado:

    Não encerrar passagem.

    Aguardar DI2.

### Teste 9 — Timeout

Acionar:

    DI1 → DI4

Aguardar 60 segundos.

Resultado:

    Inventário parado.

    Passagem preservada.

    Dados preservados.

    DI3 disponível, se elegível.

### Teste 10 — Pedal DI3

Executar:

    DI1 → DI4 → TIMEOUT → DI3

Resultado:

    Mesma passagem reaberta.

    Timer reiniciado.

    EPCs preservados.

### Teste 11 — Pedal durante leitura

Executar:

    DI1 → DI4 → DI3

Resultado:

    Nenhuma nova leitura iniciada.

    Timer não reiniciado.

### Teste 12 — Pedal após encerramento

Executar:

    DI1 → DI4 → DI5 → DI2 → DI3

Resultado:

    DI3 ignorado.

    Nenhuma reabertura.

### Teste 13 — Leitura complementar

Primeira leitura:

    7 EPCs encontrados.

Após timeout:

    DI3 acionado.

Segunda leitura:

    3 EPCs novos.

Resultado:

    Total: 10 EPCs.

    Nenhuma duplicação.

### Teste 14 — Saída após timeout

Executar:

    DI1 → DI4 → TIMEOUT → DI5 → DI2

Resultado:

    Passagem encerrada definitivamente.

    Nenhuma reabertura posterior
    permitida pelo DI3.

### Teste 15 — Saída após reabertura

Executar:

    DI1 → DI4 → TIMEOUT → DI3 → DI5 → DI2

Resultado:

    Leitura encerrada.

    Dados preservados.

    Passagem finalizada.

### Teste 16 — Entradas repetidas

Acionar DI1 várias vezes
sem completar a sequência.

Resultado:

    Nenhum inventário duplicado.

Acionar DI4 repetidamente
durante inventário ativo.

Resultado:

    Nenhuma nova sessão.

### Teste 17 — Eventos simultâneos

Simular DI1 e DI4 detectados
no mesmo ciclo sem ordem comprovada.

Resultado:

    Não presumir sequência válida.

Repetir para DI5 e DI2.

### Teste 18 — Stop manual

Iniciar inventário corretamente.

Acionar Stop.

Resultado:

    Inventário parado.

    Sequências pendentes invalidadas.

    DI3 não reabre enquanto
    o modo automático estiver parado.

### Teste 19 — Estados dos relés

Validar CH1, CH2 e CH3 em:

- Sistema pronto.
- DI1 aguardando DI4.
- Leitura ativa.
- Timeout.
- Reabertura DI3.
- DI5 aguardando DI2.
- Encerramento definitivo.
- Erro.

### Teste 20 — Backend

Validar:

- Consultas GET existentes.
- Registros POST existentes.
- Deduplicação.
- Integridade dos registros.
- Continuidade da passagem por DI3.

### Teste 21 — Regressão

Executar os testes existentes
relacionados a:

- Waveshare.
- Zebra FX9600.
- Controle LLRP.
- Sensores.
- Timer.
- Relés.
- RF037.
- Filtro EPC.
- Áudio RF033.
- Backend Rails.

Confirmar ausência de regressões.

---

## 21. CRITÉRIOS DE ACEITE

- [ ] DI1 identificado como primeiro sensor de entrada.
- [ ] DI4 identificado como segundo sensor de entrada.
- [ ] DI5 identificado como primeiro sensor de saída.
- [ ] DI2 identificado como segundo sensor de saída.
- [ ] DI3 preservado como pedal.
- [ ] Entrada exige DI1 → DI4.
- [ ] DI1 isolado não inicia leitura.
- [ ] DI4 isolado não inicia leitura.
- [ ] DI4 → DI1 não inicia leitura.
- [ ] Leitura inicia somente após DI4 válido.
- [ ] Timer inicia somente após entrada válida.
- [ ] Encerramento normal exige DI5 → DI2.
- [ ] DI5 isolado não encerra passagem.
- [ ] DI2 isolado não encerra passagem.
- [ ] DI2 → DI5 não encerra passagem.
- [ ] DI5 → DI2 encerra definitivamente.
- [ ] Timeout preserva a passagem.
- [ ] DI3 continua funcionando após timeout.
- [ ] DI3 não cria nova passagem.
- [ ] DI3 não reinicia inventário ativo.
- [ ] DI3 bloqueado após encerramento válido.
- [ ] EPCs preservados na reabertura.
- [ ] Nenhuma duplicação de EPCs.
- [ ] Dados da tabela preservados.
- [ ] Backend preservado.
- [ ] Relés preservados.
- [ ] Tratamento de segurança preservado.
- [ ] Debounce e eventos de borda validados.
- [ ] Nenhum início por sequência inválida.
- [ ] Nenhum encerramento normal por sequência inválida.
- [ ] Testes automatizados aprovados.
- [ ] Testes de regressão aprovados.

---

## 22. PROCEDIMENTO DO CODEX

Antes de implementar:

1. Ler AGENTS.md.

2. Verificar a branch atual.

3. Executar git status.

4. Preservar alterações locais.

5. Identificar o serviço Waveshare.

6. Identificar como DI1, DI2 e DI3
   são processados atualmente.

7. Verificar a disponibilidade
   de DI4 e DI5 na leitura Modbus.

8. Identificar o controlador
   de estados operacionais.

9. Identificar o ponto atual
   de início do inventário RFID.

10. Identificar o ponto atual
    de encerramento do inventário.

11. Identificar a implementação
    do RF037 e do pedal DI3.

12. Identificar o timer de 60 segundos.

13. Identificar a lógica de CH1,
    CH2 e CH3.

14. Identificar o fluxo GET e POST.

15. Identificar as regras de segurança
    baseadas nas entradas digitais.

Durante a implementação:

- Reutilizar o controlador existente.
- Implementar validação de sequência.
- Utilizar eventos de acionamento.
- Preservar a normalização dos sensores.
- Não modificar o protocolo Modbus.
- Não alterar o serviço RFID desnecessariamente.
- Preservar o timer.
- Preservar a lógica DI3.
- Preservar os relés.
- Preservar a deduplicação de EPCs.
- Preservar o backend.
- Evitar dependências adicionais.
- Não modificar a interface sem necessidade.

Após implementar:

1. Executar testes automatizados.

2. Validar DI1 → DI4.

3. Validar DI5 → DI2.

4. Validar sequências invertidas.

5. Validar acionamentos isolados.

6. Validar timeout.

7. Validar pedal DI3.

8. Validar deduplicação.

9. Validar estados dos relés.

10. Validar integração com backend.

11. Executar testes de regressão.

12. Executar git diff.

13. Apresentar os arquivos modificados.

14. Informar os testes executados.

15. Informar eventuais conflitos
    encontrados nas regras anteriores.

Não executar git reset --hard.

Não descartar alterações locais.

Não realizar commit automaticamente.

Não realizar push automaticamente.

Não realizar merge na main.

---

## 23. RESULTADO ESPERADO

O DSV RFID System deverá controlar
o início e o encerramento das passagens
utilizando sequências obrigatórias
de sensores.

INÍCIO:

    DI1
     |
     v
    DI4
     |
     v
    INICIAR LEITURA RFID

LEITURA COMPLEMENTAR:

    TIMEOUT
       |
       v
    DI3 — PEDAL
       |
       v
    REABRIR MESMA PASSAGEM

ENCERRAMENTO:

    DI5
     |
     v
    DI2
     |
     v
    ENCERRAR DEFINITIVAMENTE

Qualquer sequência diferente
não deverá iniciar ou encerrar
normalmente a passagem RFID.

O pedal deverá continuar permitindo
a complementação após timeout,
sem duplicar EPCs ou reiniciar
a sessão lógica.

IMPLEMENTAR O RF040.

INÍCIO EXCLUSIVAMENTE POR DI1 → DI4.

ENCERRAMENTO NORMAL EXCLUSIVAMENTE
POR DI5 → DI2.

PRESERVAR O PEDAL DI3.

PRESERVAR O TIMEOUT DE 60 SEGUNDOS.

PRESERVAR EPCs, CONTADORES E BACKEND.

NÃO MODIFICAR O LAYOUT.

PRESERVAR TODAS AS REGRAS DE SEGURANÇA
E O FUNCIONAMENTO EXISTENTE DO SISTEMA.