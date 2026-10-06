# RF012 — Integrar Waveshare e sensores ao fluxo principal de leitura RFID

## 1. Objetivo

Integrar definitivamente a Waveshare, os sensores fotoelétricos e os relés ao fluxo principal da aplicação RFID.

Atualmente o projeto já possui:

- configuração da Waveshare;
- tela de teste da Waveshare;
- leitura das entradas digitais;
- controle dos relés;
- lógica dos sensores já validada fisicamente;
- conexão com Zebra FX9600;
- leitura RFID;
- status de Internet;
- status RFID;
- status de Comandos/Waveshare.

Essas funcionalidades já existentes devem ser reutilizadas.

O objetivo do RF012 é fazer com que a lógica automática dos sensores passe a funcionar no fluxo principal da aplicação quando o usuário clicar no botão:

`Iniciar Leitura`

na tela `Start`.

A tela de teste da Waveshare deve continuar existindo e funcionando independentemente.

---

# 2. Importante — este RF012 substitui versões anteriores

Esta versão deve ser considerada a especificação oficial do RF012.

Desconsiderar versões anteriores do RF012 que utilizavam:

- timer de 30 segundos;
- CH3 automaticamente apenas pela combinação física dos dois sensores;
- início imediato do inventário RFID ao clicar em `Iniciar Leitura`.

O comportamento correto está definido neste documento.

O tempo máximo de leitura RFID deste requisito é:

60 segundos

---

# 3. Ambiente oficial

O projeto deve continuar sendo desenvolvido, executado e testado exclusivamente no:

Windows

Não utilizar WSL para executar ou validar este requisito.

Considerar:

- Python nativo do Windows;
- ambiente virtual do Windows;
- porta COM;
- Waveshare via Modbus RTU;
- Zebra FX9600 via LLRP;
- rede/internet utilizada pela aplicação.

---

# 4. Componentes envolvidos

O fluxo principal deverá integrar:

## Entradas digitais

- DI1 — Sensor de entrada;
- DI2 — Sensor de saída.

DI3, DI4 e DI5 não participam da automação deste requisito.

## Relés

- CH1 — Luz verde / sistema apto;
- CH2 — Luz amarela / leitura RFID em andamento;
- CH3 — Luz vermelha / sistema indisponível ou erro de status.

CH4 até CH8 não participam da automação deste requisito.

---

# 5. Nomenclatura

É importante não confundir entradas digitais com relés.

Entradas:

DI1
DI2

Relés:

CH1
CH2
CH3

Portanto, quando este requisito disser:

"desligar a luz amarela"

significa:

CH2 = OFF

E quando disser:

"ligar novamente a luz verde"

significa:

CH1 = ON

---

# 6. Polaridade dos sensores

Os sensores utilizados são sensores fotoelétricos/de luz.

A lógica física já foi validada anteriormente e NÃO deve ser invertida.

## Feixe livre

Quando nenhum objeto está interrompendo o sensor:

DI = ATIVA

## Feixe interrompido

Quando um objeto passa pelo sensor e corta o feixe:

DI = DESATIVADA

Portanto:

FEIXE LIVRE
    ↓
DI ATIVA

OBJETO PASSA
    ↓
FEIXE INTERROMPIDO
    ↓
DI DESATIVADA

O evento de passagem deve ser detectado pela transição:

ATIVA -> DESATIVADA

Essa regra vale para DI1 e DI2.

---

# 7. Estados de comunicação da aplicação

Antes de permitir a operação automática, considerar os status já existentes na aplicação:

- Internet;
- RFID;
- Comandos/Waveshare.

O sistema somente está completamente apto para operação quando:

Internet = OK
RFID = OK
Comandos/Waveshare = OK

Conceitualmente:

Internet OK
    +
RFID OK
    +
Waveshare OK
    ↓
SISTEMA APTO

---

# 8. Estado de sistema apto

Quando:

Internet = OK
RFID = OK
Comandos/Waveshare = OK

o sistema deverá indicar que está apto.

Nesse momento:

CH1 = ON
CH2 = OFF
CH3 = OFF

A luz verde conectada ao CH1 ficará ligada.

Isso indica fisicamente:

SISTEMA APTO PARA OPERAÇÃO

Esse estado pode existir mesmo antes de o usuário clicar em `Iniciar Leitura`.

---

# 9. Regra de exclusividade dos relés

CH1, CH2 e CH3 são indicadores mutuamente exclusivos.

Sempre que um deles for ligado, os outros dois deverão ser desligados.

Portanto:

## Verde

CH1 = ON
CH2 = OFF
CH3 = OFF

## Amarelo

CH1 = OFF
CH2 = ON
CH3 = OFF

## Vermelho

CH1 = OFF
CH2 = OFF
CH3 = ON

Nunca permitir intencionalmente:

CH1 + CH2 ligados

CH1 + CH3 ligados

CH2 + CH3 ligados

ao mesmo tempo.

---

# 10. Função dos indicadores

## CH1 — Verde

Representa:

SISTEMA APTO / AGUARDANDO OBJETO

## CH2 — Amarelo

Representa:

LEITURA RFID EM ANDAMENTO

## CH3 — Vermelho

Representa:

SISTEMA INDISPONÍVEL / ERRO DE STATUS

A lógica do fluxo principal deve utilizar esses significados.

---

# 11. CH3 no fluxo principal

No fluxo principal definido por este RF012, CH3 deve ser utilizado como indicador de indisponibilidade do sistema.

Quando a Waveshare estiver disponível para receber comandos e ocorrer perda/falha de:

- conexão RFID; ou
- conexão com Internet;

executar:

CH1 = OFF
CH2 = OFF
CH3 = ON

Portanto:

RFID NOK
    OU
Internet NOK
    ↓
LUZ VERMELHA

Não utilizar CH3 no fluxo principal simplesmente porque DI1 e DI2 estão momentaneamente desativadas.

A tela de teste/diagnóstico existente pode continuar com a lógica que já foi validada para os testes físicos.

Não alterar a tela de teste neste RF.

---

# 12. Waveshare indisponível

Existe uma exceção física importante.

Se:

Comandos/Waveshare = NOK

a aplicação não consegue garantir o acionamento de CH3, pois a própria comunicação responsável por controlar o relé está indisponível.

Nesse caso:

- sistema deve ser considerado NÃO APTO;
- `Iniciar Leitura` não deve iniciar o fluxo automático;
- registrar a falha;
- manter o status visual da aplicação indicando problema de Comandos/Waveshare;
- não apresentar internamente CH3 como confirmado se o comando não pôde ser enviado.

Não simular um estado físico de relé que não foi confirmado.

---

# 13. Tela Start

A integração automática deve funcionar na tela:

`Start`

O botão existente:

`Iniciar Leitura`

passará a habilitar o fluxo automático baseado nos sensores.

---

# 14. Mudança importante no botão Iniciar Leitura

Atualmente o botão pode possuir comportamento relacionado ao início direto da leitura RFID.

Para o RF012, analisar a implementação atual antes de alterar.

No novo fluxo automático:

clicar em `Iniciar Leitura`

NÃO significa necessariamente começar imediatamente o inventário RFID.

O botão deve colocar o sistema em:

MODO AUTOMÁTICO / AGUARDANDO SENSOR

A leitura real do Zebra deve começar somente quando DI1 detectar a passagem do objeto.

---

# 15. Pré-condição para Iniciar Leitura

Ao clicar em:

`Iniciar Leitura`

verificar:

Internet = OK
RFID = OK
Comandos/Waveshare = OK

Se qualquer uma das condições necessárias não estiver disponível:

NÃO iniciar o fluxo automático.

---

# 16. Estado ao clicar em Iniciar Leitura

Se:

Internet = OK
RFID = OK
Comandos/Waveshare = OK

e os sensores estiverem em estado normal:

DI1 = ATIVA
DI2 = ATIVA

então:

CH1 = ON
CH2 = OFF
CH3 = OFF

RFID = NÃO LENDO

O sistema deve permanecer aguardando a passagem pelo primeiro sensor.

---

# 17. Estado AGUARDANDO

Após clicar em `Iniciar Leitura`, enquanto nenhum objeto tiver interrompido DI1:

Estado:

AGUARDANDO

Entradas esperadas:

DI1 = ATIVA
DI2 = ATIVA

Relés:

CH1 = ON
CH2 = OFF
CH3 = OFF

RFID:

OFF

A aplicação deve monitorar os sensores em background.

---

# 18. Passagem pelo primeiro sensor

Quando um objeto passar pelo primeiro sensor:

DI1 realizará:

ATIVA
    ↓
DESATIVADA

Essa transição representa:

OBJETO DETECTADO NA ENTRADA

Nesse momento iniciar o ciclo RFID.

---

# 19. Ações ao detectar DI1

Quando ocorrer:

DI1 ATIVA -> DESATIVADA

durante o modo automático:

1. confirmar que o sistema ainda está apto;
2. confirmar que não existe outra leitura automática ativa;
3. iniciar o inventário RFID;
4. desligar CH1;
5. ligar CH2;
6. garantir CH3 desligado;
7. iniciar timer de 60 segundos;
8. alterar estado interno para `LENDO`.

Resultado:

RFID = ON

CH1 = OFF
CH2 = ON
CH3 = OFF

Timer = 60 segundos

---

# 20. Luz amarela

CH2 contém a luz amarela.

Portanto, enquanto o RFID estiver efetivamente realizando a leitura:

CH2 = ON

Isso representa visualmente:

LEITURA RFID EM ANDAMENTO

Não ligar CH2 antes de o sistema efetivamente conseguir iniciar a leitura RFID.

---

# 21. Timer de leitura

Cada ciclo RFID iniciado por DI1 deve possuir um timer máximo de:

60 segundos

O timer começa no início efetivo da leitura RFID.

O RFID poderá parar:

- antes dos 60 segundos, caso DI2 detecte o objeto; ou
- automaticamente ao atingir 60 segundos.

---

# 22. Durante a leitura

Enquanto o ciclo estiver ativo:

Estado = LENDO

RFID = ON

CH1 = OFF
CH2 = ON
CH3 = OFF

Timer = ATIVO

A aplicação deve continuar:

- monitorando DI2;
- recebendo EPCs;
- processando EPCs;
- realizando consultas existentes;
- atualizando a tabela;
- atualizando contador;
- mantendo a interface responsiva.

---

# 23. Não reiniciar por DI1 permanecer interrompida

Após o objeto interromper DI1, essa entrada poderá permanecer desativada durante vários ciclos de polling.

Isso NÃO deve provocar:

- múltiplos Start RFID;
- múltiplos timers;
- reinício dos 60 segundos;
- múltiplos ciclos;
- múltiplas sessões.

Utilizar detecção de transição:

ATIVA -> DESATIVADA

e estado interno do ciclo.

---

# 24. Passagem pelo segundo sensor

Durante a leitura RFID, quando o objeto passar pelo segundo sensor:

DI2 realizará:

ATIVA
    ↓
DESATIVADA

Essa transição deve encerrar imediatamente a leitura.

---

# 25. Ações ao detectar DI2

Quando ocorrer:

DI2 ATIVA -> DESATIVADA

durante uma leitura ativa:

1. parar imediatamente o timer;
2. parar a leitura RFID;
3. desligar CH2;
4. ligar CH1;
5. garantir CH3 desligado;
6. finalizar o ciclo atual;
7. retornar ao estado de espera.

Resultado:

RFID = OFF

Timer = CANCELADO

CH1 = ON
CH2 = OFF
CH3 = OFF

Estado = AGUARDANDO

---

# 26. Importante — comportamento após DI2

Para o fluxo principal definido neste RF012, após DI2 encerrar corretamente a leitura:

CH2 deve desligar.

CH1 deve ligar novamente.

Portanto:

DI2 detectado
    ↓
STOP RFID
    ↓
STOP TIMER
    ↓
CH2 OFF
    ↓
CH1 ON
    ↓
AGUARDAR PRÓXIMO CICLO

Não utilizar CH3 simplesmente porque os dois sensores possam estar fisicamente interrompidos naquele instante.

CH3 no fluxo principal está reservado para a condição de indisponibilidade definida neste requisito.

---

# 27. Retorno ao estado inicial

Após o encerramento normal por DI2:

CH1 = ON
CH2 = OFF
CH3 = OFF

O sistema continua em modo automático e fica preparado para o próximo ciclo, desde que:

Internet = OK
RFID = OK
Comandos/Waveshare = OK

---

# 28. Timeout de 60 segundos

Caso DI2 não seja detectado dentro de 60 segundos:

o RFID NÃO pode continuar lendo indefinidamente.

Ao completar 60 segundos:

1. parar a leitura RFID;
2. finalizar o timer;
3. desligar CH2;
4. registrar o timeout;
5. verificar novamente os status do sistema.

Se:

Internet = OK
RFID = OK
Comandos/Waveshare = OK

retornar para:

CH1 = ON
CH2 = OFF
CH3 = OFF

Estado = AGUARDANDO

Não utilizar CH3 apenas por causa do timeout, pois neste requisito CH3 representa indisponibilidade dos status do sistema.

---

# 29. Novo ciclo após timeout

Após timeout, não permitir que DI1 ainda mantida desativada inicie imediatamente outro ciclo.

Um novo ciclo deve exigir uma nova transição válida de DI1:

ATIVA -> DESATIVADA

Isso evita:

timeout
    ↓
DI1 continua DESATIVADA
    ↓
novo RFID inicia sozinho
    ↓
novo timeout
    ↓
loop infinito

Esse comportamento não deve ocorrer.

---

# 30. Internet indisponível antes do ciclo

Se:

Internet = NOK

e:

Comandos/Waveshare = OK

executar:

CH1 = OFF
CH2 = OFF
CH3 = ON

O sistema não deve iniciar uma nova leitura automática.

---

# 31. RFID indisponível antes do ciclo

Se:

RFID = NOK

e:

Comandos/Waveshare = OK

executar:

CH1 = OFF
CH2 = OFF
CH3 = ON

O sistema não deve iniciar uma nova leitura automática.

---

# 32. Perda de Internet durante leitura

Cenário:

RFID = LENDO
CH2 = ON
Timer = ATIVO

e a Internet muda para:

NOK

A aplicação deve:

1. interromper o ciclo;
2. parar RFID;
3. cancelar o timer;
4. desligar CH1;
5. desligar CH2;
6. ligar CH3;
7. registrar a ocorrência.

Resultado:

RFID = OFF

CH1 = OFF
CH2 = OFF
CH3 = ON

---

# 33. Perda de RFID durante o ciclo

Se a conexão RFID for perdida durante a leitura:

1. cancelar o timer;
2. encerrar o ciclo;
3. desligar CH1;
4. desligar CH2;
5. ligar CH3, caso Waveshare continue disponível;
6. registrar a falha.

Não manter a luz amarela ligada se o RFID não estiver efetivamente lendo.

---

# 34. Perda da Waveshare durante o ciclo

Se a comunicação com a Waveshare for perdida:

1. interromper o fluxo automático;
2. solicitar Stop RFID se estiver lendo;
3. cancelar o timer;
4. registrar a falha;
5. atualizar o status `Comandos/Waveshare`;
6. não assumir que qualquer relé foi alterado.

Como não existe comunicação com a Waveshare, não é possível garantir fisicamente:

CH1
CH2
CH3

Não apresentar comandos não confirmados como executados.

---

# 35. Recuperação dos status

Quando o sistema recuperar:

Internet = OK
RFID = OK
Comandos/Waveshare = OK

e não existir leitura ativa:

deve ser possível retornar ao estado apto:

CH1 = ON
CH2 = OFF
CH3 = OFF

Não iniciar automaticamente uma leitura RFID apenas porque a conexão foi recuperada.

O sistema deve aguardar uma nova transição válida de DI1 quando o modo automático estiver habilitado.

---

# 36. Fluxo completo principal

Sequência esperada:

SISTEMA INICIALIZA
        ↓
verificar status
        ↓
Internet OK?
RFID OK?
Waveshare OK?
        ↓
SIM
        ↓
CH1 ON
CH2 OFF
CH3 OFF
        ↓
LUZ VERDE
        ↓
usuário clica
"INICIAR LEITURA"
        ↓
modo automático habilitado
        ↓
DI1 ATIVA
DI2 ATIVA
        ↓
aguardando objeto
        ↓
objeto corta DI1
        ↓
DI1 ATIVA -> DESATIVADA
        ↓
START RFID
        ↓
START TIMER 60s
        ↓
CH1 OFF
CH2 ON
CH3 OFF
        ↓
LUZ AMARELA
        ↓
aguardar DI2
        ↓
objeto corta DI2
        ↓
DI2 ATIVA -> DESATIVADA
        ↓
STOP TIMER
        ↓
STOP RFID
        ↓
CH1 ON
CH2 OFF
CH3 OFF
        ↓
LUZ VERDE
        ↓
aguardar próximo ciclo

---

# 37. Fluxo de timeout

DI1 detectado
        ↓
RFID ON
        ↓
CH2 ON
        ↓
Timer 60 segundos
        ↓
DI2 não detectado
        ↓
60 segundos atingidos
        ↓
STOP RFID
        ↓
CH2 OFF
        ↓
status continuam OK?
        ↓
SIM
        ↓
CH1 ON
        ↓
aguardar nova transição válida de DI1

---

# 38. Fluxo de erro de status

Durante estado de espera ou leitura:

Internet NOK
        OU
RFID NOK
        ↓
se Waveshare disponível
        ↓
CH1 OFF
CH2 OFF
CH3 ON
        ↓
LUZ VERMELHA
        ↓
bloquear novos ciclos

Após recuperação:

Internet OK
RFID OK
Waveshare OK
        ↓
CH1 ON
CH2 OFF
CH3 OFF

---

# 39. Máquina de estados

Preferencialmente utilizar estados explícitos para evitar combinações inconsistentes.

Estados mínimos sugeridos:

- `NAO_APTO`;
- `AGUARDANDO`;
- `LENDO`.

## NAO_APTO

Sistema não possui todas as condições necessárias.

Quando Waveshare estiver comunicando:

CH1 = OFF
CH2 = OFF
CH3 = ON

RFID automático = OFF

## AGUARDANDO

Sistema apto e aguardando DI1.

CH1 = ON
CH2 = OFF
CH3 = OFF

RFID = OFF

## LENDO

Objeto detectado em DI1 e inventário RFID ativo.

CH1 = OFF
CH2 = ON
CH3 = OFF

RFID = ON

Timer = ATIVO

Adaptar os nomes à arquitetura existente do projeto.

---

# 40. Prioridade dos estados

A disponibilidade do sistema deve ter prioridade sobre a leitura.

Conceitualmente:

se sistema NÃO APTO:
    estado = NAO_APTO

senão se RFID está lendo:
    estado = LENDO

senão:
    estado = AGUARDANDO

Não permitir que CH1 indique verde se o sistema não estiver apto.

Não permitir que CH2 indique amarelo se o RFID não estiver efetivamente lendo.

---

# 41. Função central de controle dos relés

Evitar espalhar comandos individuais para CH1, CH2 e CH3 em diversos pontos da aplicação.

Preferencialmente centralizar os estados.

Exemplo conceitual:

set_indicator_state(READY)

deve resultar em:

CH1 ON
CH2 OFF
CH3 OFF

set_indicator_state(READING)

deve resultar em:

CH1 OFF
CH2 ON
CH3 OFF

set_indicator_state(ERROR)

deve resultar em:

CH1 OFF
CH2 OFF
CH3 ON

Adaptar à arquitetura existente.

O objetivo é garantir que apenas um relé permaneça ligado.

---

# 42. Reutilização da lógica Waveshare existente

A tela de teste da Waveshare já possui:

- conexão;
- leitura das entradas;
- comandos dos relés;
- lógica previamente validada.

NÃO duplicar desnecessariamente o código Modbus.

Analisar o que pode ser reutilizado no fluxo principal.

Preferencialmente:

Tela de teste
       ↓
       ├──── WaveshareService
       │
Fluxo principal
       ↓
WaveshareService
       ↓
Modbus
       ↓
Waveshare

A tela de teste e o fluxo principal podem possuir regras de orquestração diferentes, mas devem reutilizar a mesma infraestrutura de comunicação com o hardware.

---

# 43. Não alterar a tela de teste sem necessidade

A tela de teste já está funcional.

Este RF012 é destinado à integração com o fluxo principal.

Não alterar a lógica da tela de teste apenas para fazê-la coincidir visualmente com a lógica operacional da tela Start.

A tela de teste continua sendo uma ferramenta de diagnóstico.

O fluxo automático principal passa a seguir as regras deste RF012.

---

# 44. Start RFID existente

Não criar uma nova implementação de inventário.

Reutilizar o mecanismo atual que inicia a leitura do Zebra FX9600.

Fluxo:

DI1 detectado
    ↓
controlador do fluxo automático
    ↓
serviço RFID existente
    ↓
Start Inventory

---

# 45. Stop RFID existente

Da mesma forma, DI2 e timeout devem utilizar o mecanismo existente para parar o inventário.

Fluxo:

DI2 detectado
    OU
timeout 60s
    ↓
controlador
    ↓
serviço RFID existente
    ↓
Stop Inventory

---

# 46. Start RFID somente após DI1

Após o usuário clicar em:

`Iniciar Leitura`

o RFID não deve começar imediatamente se os sensores estiverem livres.

Estado:

DI1 = ATIVA
DI2 = ATIVA

deve significar:

AGUARDANDO

Somente:

DI1 ATIVA -> DESATIVADA

deve efetivamente iniciar o inventário.

---

# 47. Timer associado ao ciclo

Cada leitura deve possuir exatamente um timer.

Quando DI1 inicia o ciclo:

criar timer de 60 segundos.

Quando DI2 encerra:

cancelar o timer.

Quando 60 segundos são atingidos:

encerrar o ciclo.

Não permitir múltiplos timers para o mesmo ciclo.

---

# 48. Proteção contra timer antigo

Um timer pertencente a um ciclo anterior não pode afetar um ciclo novo.

Exemplo:

Ciclo A começa
    ↓
DI2 encerra Ciclo A
    ↓
Ciclo B começa
    ↓
callback antigo do timer A

O callback do ciclo A NÃO pode parar o RFID do ciclo B.

Associar o timer a um identificador/estado do ciclo ou utilizar a estratégia equivalente existente no projeto.

---

# 49. Polling dos sensores

Reutilizar o polling já validado da Waveshare.

Não criar um segundo polling concorrente para a mesma porta COM se a arquitetura atual já possui um mecanismo central de leitura.

O fluxo principal deve receber os estados de DI1 e DI2 através da infraestrutura existente.

---

# 50. Concorrência Modbus

Não permitir que:

- polling;
- comandos CH1;
- comandos CH2;
- comandos CH3;
- tela de teste;

acessem a porta serial de forma concorrente e descontrolada.

Reutilizar a estratégia existente de:

- lock;
- worker;
- fila;
- serviço serializado;

conforme a arquitetura atual.

---

# 51. Conflito com a tela de teste

A tela de teste e o fluxo automático não devem controlar CH1-CH3 simultaneamente.

Se o modo automático estiver ativo:

impedir ou controlar adequadamente o teste manual conflitante.

Da mesma forma, não permitir que a tela de teste crie uma segunda conexão concorrente na mesma COM enquanto o fluxo principal estiver utilizando a Waveshare.

Analisar a arquitetura atual antes de implementar.

---

# 52. Botão Parar Leitura

O botão existente:

`Parar Leitura`

deve encerrar o modo automático.

Ao clicar:

1. impedir novos ciclos iniciados por DI1;
2. parar RFID caso exista leitura ativa;
3. cancelar timer ativo;
4. finalizar o ciclo atual;
5. manter o sistema em condição segura;
6. não deixar worker/timer órfão.

Se:

Internet = OK
RFID = OK
Comandos/Waveshare = OK

CH1 pode permanecer:

ON

pois a luz verde representa que o sistema está apto.

Entretanto, após `Parar Leitura`, os sensores não devem iniciar uma nova leitura até que o usuário clique novamente em `Iniciar Leitura`.

---

# 53. Processamento dos EPCs

Durante os 60 segundos ou até DI2 encerrar a leitura, manter integralmente o processamento RFID existente.

Não alterar:

- recebimento dos EPCs;
- validação;
- deduplicação;
- consulta API;
- Power Automate;
- tabela;
- contador de encontrados;
- regras atuais de exibição.

O RF012 somente controla quando o inventário começa e termina.

---

# 54. Interface não bloqueante

Não bloquear a thread principal com:

- polling;
- timer;
- Start RFID;
- Stop RFID;
- comandos Modbus.

A tela deve permanecer responsiva durante todo o processo.

---

# 55. Inicialização dos sensores

Ao ativar o modo automático:

1. ler o estado atual de DI1;
2. ler o estado atual de DI2;
3. armazenar os estados;
4. não considerar a primeira leitura como uma transição.

Exemplo:

se DI1 já estiver DESATIVADA quando o usuário clicar em `Iniciar Leitura`, não assumir automaticamente que um novo objeto acabou de chegar.

Aguardar uma sequência válida antes de iniciar um novo ciclo.

---

# 56. Detecção de borda

Utilizar os estados anteriores para detectar:

DI1:

ATIVA -> DESATIVADA

e:

DI2:

ATIVA -> DESATIVADA

Não utilizar apenas:

if DI1 == False

porque isso executaria repetidamente durante todos os pollings em que o feixe permanecesse interrompido.

---

# 57. Logs

Registrar eventos relevantes sem gerar log a cada polling.

Exemplos:

- sistema apto;
- sistema não apto;
- modo automático iniciado;
- DI1 interrompida;
- ciclo RFID iniciado;
- CH2 ativado;
- timer 60s iniciado;
- DI2 interrompida;
- timer cancelado;
- RFID parado;
- CH1 ativado;
- timeout de 60 segundos;
- Internet indisponível;
- RFID indisponível;
- Waveshare indisponível;
- modo automático parado.

---

# 58. Cenário 1 — Sistema inicializado e apto

Condições:

Internet = OK
RFID = OK
Waveshare = OK

Esperado:

CH1 = ON
CH2 = OFF
CH3 = OFF

Luz verde ligada.

---

# 59. Cenário 2 — Clicar em Iniciar Leitura

Condições:

Internet = OK
RFID = OK
Waveshare = OK

DI1 = ATIVA
DI2 = ATIVA

Usuário:

clica `Iniciar Leitura`

Esperado:

modo automático = ON

RFID = OFF

CH1 = ON
CH2 = OFF
CH3 = OFF

Sistema aguarda DI1.

---

# 60. Cenário 3 — Passagem pelo DI1

Estado:

modo automático = ON

DI1:

ATIVA -> DESATIVADA

Esperado:

RFID = ON

Timer = 60 segundos

CH1 = OFF
CH2 = ON
CH3 = OFF

Luz amarela ligada.

---

# 61. Cenário 4 — DI1 permanece interrompida

Manter:

DI1 = DESATIVADA

durante vários pollings.

Esperado:

- somente um Start RFID;
- somente um timer;
- timer não reinicia;
- CH2 continua ON.

---

# 62. Cenário 5 — Passagem pelo DI2

Durante a leitura:

DI2:

ATIVA -> DESATIVADA

Esperado imediatamente:

Timer = CANCELADO

RFID = OFF

CH1 = ON
CH2 = OFF
CH3 = OFF

Luz verde ligada novamente.

Sistema continua aguardando próximo ciclo.

---

# 63. Cenário 6 — Timeout

DI1 inicia o ciclo.

DI2 não é detectado.

Após:

60 segundos

Esperado:

RFID = OFF

Timer = FINALIZADO

CH2 = OFF

Se todos os status permanecerem OK:

CH1 = ON
CH3 = OFF

Não reiniciar leitura enquanto DI1 permanecer interrompida.

---

# 64. Cenário 7 — Internet desconectada

Condições:

Waveshare = OK

Internet = NOK

Esperado:

CH1 = OFF
CH2 = OFF
CH3 = ON

Luz vermelha ligada.

Não permitir novo ciclo RFID.

---

# 65. Cenário 8 — RFID desconectado

Condições:

Waveshare = OK

RFID = NOK

Esperado:

CH1 = OFF
CH2 = OFF
CH3 = ON

Luz vermelha ligada.

Não permitir novo ciclo.

---

# 66. Cenário 9 — Waveshare desconectada

Condição:

Comandos/Waveshare = NOK

Esperado:

- sistema não apto;
- bloquear fluxo automático;
- atualizar status visual;
- não assumir estado de CH1/CH2/CH3;
- registrar falha.

---

# 67. Cenário 10 — Falha durante leitura

Estado inicial:

RFID lendo
CH2 ON

Durante o ciclo:

Internet -> NOK

ou:

RFID -> NOK

Esperado, quando Waveshare continuar disponível:

- cancelar timer;
- interromper ciclo;
- RFID OFF quando tecnicamente possível;
- CH1 OFF;
- CH2 OFF;
- CH3 ON.

---

# 68. Cenário 11 — Múltiplos ciclos

Executar:

Ciclo 1:
DI1 -> DI2

Ciclo 2:
DI1 -> DI2

Ciclo 3:
DI1 -> DI2

Cada ciclo deve possuir:

- um Start RFID;
- um timer;
- um Stop RFID;
- cancelamento correto do timer;
- retorno ao CH1;
- nenhuma interferência do ciclo anterior.

---

# 69. Testes automatizados

Os testes automatizados não devem depender do hardware físico.

Utilizar mocks/fakes já existentes ou criar somente o necessário para testar a orquestração.

Cobrir pelo menos:

- todos os status OK;
- CH1 ligado quando sistema apto;
- exclusividade CH1/CH2/CH3;
- Internet NOK;
- RFID NOK;
- Waveshare NOK;
- clique em Iniciar Leitura;
- Iniciar Leitura não iniciar RFID imediatamente;
- DI1 ativa -> desativada;
- Start RFID;
- CH1 OFF;
- CH2 ON;
- timer de 60 segundos;
- DI1 mantida desativada;
- DI2 ativa -> desativada;
- Stop RFID;
- timer cancelado;
- CH2 OFF;
- CH1 ON;
- timeout;
- retorno ao CH1 após timeout quando status OK;
- timer antigo não afetar ciclo novo;
- perda de Internet durante leitura;
- perda de RFID durante leitura;
- perda da Waveshare;
- botão Parar Leitura;
- múltiplos ciclos;
- CH4-CH8 não alterados;
- tela de teste não sofrer regressão;
- processamento de EPC não sofrer regressão.

---

# 70. Teste físico obrigatório — preparação

Executar no Windows com:

- Zebra FX9600;
- Waveshare;
- sensores DI1/DI2;
- luz verde no CH1;
- luz amarela no CH2;
- luz vermelha no CH3;
- Internet disponível.

Confirmar inicialmente:

Internet = OK
RFID = OK
Comandos/Waveshare = OK

Esperado:

luz verde ligada.

---

# 71. Teste físico — ciclo normal

1. confirmar CH1 ON;
2. confirmar CH2 OFF;
3. confirmar CH3 OFF;
4. clicar `Iniciar Leitura`;
5. confirmar que RFID ainda não iniciou;
6. confirmar que CH1 continua ON;
7. interromper o feixe de DI1;
8. confirmar Start RFID;
9. confirmar CH1 OFF;
10. confirmar CH2 ON;
11. confirmar luz amarela;
12. confirmar timer de 60 segundos;
13. passar pelo DI2 antes dos 60 segundos;
14. confirmar Stop RFID;
15. confirmar timer cancelado;
16. confirmar CH2 OFF;
17. confirmar CH1 ON;
18. confirmar luz verde novamente.

---

# 72. Teste físico — timeout

1. clicar `Iniciar Leitura`;
2. interromper DI1;
3. confirmar RFID ON;
4. confirmar CH2 ON;
5. não passar por DI2;
6. aguardar 60 segundos;
7. confirmar Stop RFID;
8. confirmar CH2 OFF;
9. confirmar CH1 ON caso os status permaneçam OK;
10. confirmar que DI1 ainda interrompida não inicia automaticamente outro ciclo.

---

# 73. Teste físico — luz vermelha

Com Waveshare funcionando:

1. provocar condição controlada de Internet NOK;
2. confirmar CH1 OFF;
3. confirmar CH2 OFF;
4. confirmar CH3 ON;
5. restaurar Internet;
6. confirmar retorno ao CH1 quando todos os status estiverem OK.

Repetir o teste com indisponibilidade controlada do RFID.

---

# 74. Fora do escopo

NÃO implementar neste RF:

- alterações na lógica da tela de teste da Waveshare;
- novas regras para DI3;
- novas regras para DI4;
- novas regras para DI5;
- automação CH4;
- automação CH5;
- automação CH6;
- automação CH7;
- automação CH8;
- alterações no Power Automate;
- alterações no SharePoint;
- alterações no contrato da API;
- novos campos na tabela;
- novos contadores;
- histórico de ciclos;
- banco de dados;
- dashboard adicional;
- configuração do timer pela interface;
- redesign da tela Start;
- refatoração geral do RFID;
- atualização desnecessária de bibliotecas.

---

# 75. Preservar funcionalidades existentes

Preservar:

- configuração do Zebra;
- configuração da Waveshare;
- tela de teste da Waveshare;
- leitura DI1-DI5;
- teste manual CH1-CH8;
- conexão LLRP;
- comunicação Modbus;
- consulta API;
- processamento dos EPCs;
- tabela de resultados;
- contador de EPCs encontrados;
- status existentes;
- logs existentes;
- navegação existente.

---

# 76. Análise obrigatória antes da implementação

Antes de alterar código, o Codex deve analisar:

1. `AGENTS.md`;
2. estrutura atual da tela Start;
3. implementação atual de `Iniciar Leitura`;
4. implementação atual de `Parar Leitura`;
5. serviço RFID existente;
6. Start Inventory existente;
7. Stop Inventory existente;
8. serviço Waveshare existente;
9. lógica atualmente utilizada pela tela de teste;
10. polling atual de DI1-DI5;
11. controle atual CH1-CH8;
12. polaridade validada de DI1/DI2;
13. status atual de Internet;
14. status atual de RFID;
15. status atual de Comandos/Waveshare;
16. gerenciamento da porta COM;
17. threads/workers;
18. timers;
19. cleanup da aplicação;
20. testes existentes.

Não implementar antes dessa análise.

---

# 77. Atenção especial — não duplicar serviços

O Codex deve verificar se a tela de teste já possui funções reutilizáveis para:

- ler DI;
- escrever relé;
- verificar Waveshare;
- controlar acesso serial.

Se existirem, reutilizá-las.

Não copiar a implementação da tela de teste para dentro da tela Start.

O objetivo é reutilizar o serviço de hardware e adicionar somente a orquestração necessária ao fluxo principal.

---

# 78. Plano obrigatório antes da alteração

Após a análise, apresentar antes da implementação:

- arquivos que serão alterados;
- arquivos que não precisam ser alterados;
- serviços que serão reutilizados;
- comportamento atual de `Iniciar Leitura`;
- mudança necessária em `Iniciar Leitura`;
- comportamento atual de `Parar Leitura`;
- como os três status serão avaliados;
- como CH1 será ativado quando o sistema estiver apto;
- como DI1 iniciará RFID;
- como DI2 interromperá RFID;
- como o timer de 60 segundos será implementado;
- como CH1/CH2/CH3 serão mutuamente exclusivos;
- como a perda de Internet será tratada;
- como a perda de RFID será tratada;
- como a perda da Waveshare será tratada;
- como será evitado conflito com a tela de teste;
- como timers antigos serão invalidados.

Somente depois iniciar as alterações.

---

# 79. Alterações mínimas

Implementar somente o necessário para integrar o fluxo principal.

Não aproveitar o RF012 para:

- reorganizar módulos não relacionados;
- renomear componentes;
- alterar arquitetura da API;
- alterar processamento de EPC;
- alterar interface sem necessidade;
- atualizar dependências;
- modificar lógica da tela de teste;
- criar novo serviço Modbus se já existir um funcional;
- criar novo serviço RFID se já existir um funcional.

Ao finalizar, revisar o diff e remover alterações fora do escopo.

---

# 80. Critérios de aceite

O RF012 estará concluído quando:

1. Internet, RFID e Waveshare forem considerados na disponibilidade;
2. todos OK resultarem em CH1 ON;
3. CH1 representar luz verde;
4. CH2 representar luz amarela;
5. CH3 representar luz vermelha;
6. apenas um entre CH1/CH2/CH3 permanecer ligado;
7. `Iniciar Leitura` habilitar o modo automático;
8. `Iniciar Leitura` não iniciar RFID imediatamente quando sensores estiverem livres;
9. DI1 ATIVA -> DESATIVADA iniciar RFID;
10. DI1 iniciar timer de 60 segundos;
11. CH1 desligar quando RFID iniciar;
12. CH2 ligar quando RFID iniciar;
13. CH3 permanecer desligado durante leitura normal;
14. DI1 mantida desativada não reiniciar ciclo;
15. DI2 ATIVA -> DESATIVADA parar RFID;
16. DI2 cancelar timer;
17. DI2 desligar CH2;
18. DI2 ligar CH1 novamente;
19. leitura parar automaticamente após 60 segundos;
20. timeout não criar loop de novas leituras;
21. Internet NOK acionar CH3 quando Waveshare estiver disponível;
22. RFID NOK acionar CH3 quando Waveshare estiver disponível;
23. sistema não iniciar ciclo quando não estiver apto;
24. Waveshare NOK bloquear o fluxo sem fingir que CH3 foi comandado;
25. recuperação dos status permitir retorno ao CH1;
26. botão `Parar Leitura` interromper o modo automático;
27. após `Parar Leitura`, DI1 não iniciar novo ciclo;
28. CH4-CH8 não serem alterados;
29. DI3-DI5 não participarem da lógica;
30. tela de teste continuar funcionando;
31. processamento atual de EPC continuar funcionando;
32. tabela continuar funcionando;
33. contador continuar funcionando;
34. UI não bloquear;
35. timers antigos não interferirem em novos ciclos;
36. múltiplos ciclos funcionarem corretamente;
37. implementação funcionar no Windows;
38. testes automatizados passarem;
39. teste físico confirmar verde -> amarelo -> verde;
40. teste físico confirmar vermelho quando houver indisponibilidade de Internet/RFID.

---

# 81. Validação do projeto

Executar exclusivamente no Windows.

Utilizar o ambiente virtual oficial do projeto.

Executar apenas ferramentas já configuradas no repositório.

Quando disponíveis:

ruff check .
ruff format --check .
mypy src
pytest

Não instalar ou atualizar dependências sem necessidade.

Caso alguma ferramenta não esteja configurada, registrar no relatório em vez de modificar o ambiente sem necessidade.

---

# 82. Relatório final esperado

Ao concluir, o Codex deve apresentar:

- análise realizada;
- arquivos alterados;
- diff revisado;
- serviços existentes reutilizados;
- comportamento final do botão `Iniciar Leitura`;
- comportamento final do botão `Parar Leitura`;
- forma utilizada para avaliar Internet;
- forma utilizada para avaliar RFID;
- forma utilizada para avaliar Waveshare;
- comportamento de CH1;
- comportamento de CH2;
- comportamento de CH3;
- confirmação da exclusividade dos relés;
- polaridade utilizada para DI1;
- polaridade utilizada para DI2;
- método reutilizado para Start RFID;
- método reutilizado para Stop RFID;
- implementação do timer de 60 segundos;
- tratamento do DI2;
- tratamento do timeout;
- proteção contra timers antigos;
- tratamento da perda de Internet;
- tratamento da perda de RFID;
- tratamento da perda da Waveshare;
- comportamento do modo automático;
- tratamento de conflito com a tela de teste;
- testes adicionados/alterados;
- comandos de validação executados;
- resultados dos testes;
- validação física realizada ou pendente;
- confirmação de que CH4-CH8 não foram alterados;
- confirmação de que DI3-DI5 não foram alterados;
- confirmação de que a tela de teste não sofreu alteração desnecessária;
- confirmação de que funcionalidades fora do RF012 não foram modificadas.

---

# 83. Resumo funcional definitivo

O comportamento esperado do fluxo principal é:

SISTEMA OK
    ↓
CH1 ON — VERDE
    ↓
usuário clica "Iniciar Leitura"
    ↓
AGUARDAR DI1
    ↓
objeto interrompe DI1
    ↓
START RFID
    ↓
TIMER 60 SEGUNDOS
    ↓
CH1 OFF
CH2 ON — AMARELO
    ↓
objeto interrompe DI2
    ↓
STOP RFID
STOP TIMER
    ↓
CH2 OFF
CH1 ON — VERDE
    ↓
AGUARDAR PRÓXIMO OBJETO

Se durante a operação:

Internet = NOK
ou
RFID = NOK

e a Waveshare continuar disponível:

CH1 OFF
CH2 OFF
CH3 ON — VERMELHO

A polaridade dos sensores permanece:

FEIXE LIVRE = DI ATIVA

FEIXE INTERROMPIDO PELO OBJETO = DI DESATIVADA

Portanto, os eventos de passagem utilizados pelo fluxo são:

DI1: ATIVA -> DESATIVADA = iniciar leitura

DI2: ATIVA -> DESATIVADA = parar leitura