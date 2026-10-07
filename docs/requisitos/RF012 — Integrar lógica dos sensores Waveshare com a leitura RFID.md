# RF012 — Integrar sensores Waveshare com a operação automática do RFID

## 1. Objetivo

Integrar a lógica dos sensores fotoelétricos conectados à Waveshare com a operação automática de leitura RFID do Zebra FX9600.

A lógica deve utilizar o comportamento físico dos sensores já validado anteriormente no projeto.

Os sensores utilizados trabalham com feixe de luz.

Portanto:

- quando o feixe está livre, a entrada digital está ATIVA;
- quando um objeto interrompe o feixe, a entrada digital fica DESATIVADA.

Esta interpretação é fundamental para toda a implementação do RF012.

O sistema deverá:

1. aguardar a passagem de um objeto pelo sensor de entrada;
2. detectar a interrupção do feixe através da desativação de DI1;
3. iniciar automaticamente a leitura RFID;
4. manter a leitura por no máximo 30 segundos;
5. detectar a passagem pelo sensor de saída através da desativação de DI2;
6. interromper imediatamente a leitura RFID;
7. controlar CH1, CH2 e CH3 conforme a lógica física já validada.

---

# 2. Ambiente oficial

O ambiente oficial do projeto é exclusivamente:

Windows

Todo desenvolvimento, execução, testes automatizados e testes físicos devem considerar Windows.

Não utilizar WSL para executar ou validar este requisito.

Considerar:

- Python nativo do Windows;
- ambiente virtual Python do Windows;
- portas COM;
- Waveshare via Modbus RTU;
- Zebra FX9600 via LLRP/rede.

---

# 3. Regra fundamental dos sensores

ATENÇÃO:

Os sensores utilizados são sensores de luz/fotoelétricos.

O estado físico deve ser interpretado da seguinte maneira:

| Situação física | Entrada digital |
|---|---|
| Feixe de luz livre | ATIVA |
| Objeto interrompendo o feixe | DESATIVADA |

Portanto:

DESATIVAR uma entrada significa que um objeto interrompeu aquele sensor.

Isso vale para:

- DI1 — sensor de entrada;
- DI2 — sensor de saída.

NÃO interpretar "sensor acionado pela passagem do objeto" como entrada digital ativa.

Fisicamente ocorre o contrário:

Objeto chega
    ↓
corta o feixe
    ↓
entrada digital DESATIVA

---

# 4. Terminologia obrigatória

Para evitar novas ambiguidades, utilizar neste requisito preferencialmente os termos:

- `FEIXE LIVRE`;
- `FEIXE INTERROMPIDO`;
- `DI ATIVA`;
- `DI DESATIVADA`.

Evitar utilizar isoladamente expressões como:

- "sensor ativado";
- "sensor acionado";

porque elas podem ser interpretadas incorretamente.

A referência deve sempre ser o estado real da entrada digital.

---

# 5. Entradas utilizadas

Utilizar:

DI1 = Sensor de entrada

DI2 = Sensor de saída

As demais entradas:

DI3
DI4
DI5

não participam da lógica automática do RF012.

Não alterar o funcionamento delas.

---

# 6. Relés utilizados

Utilizar:

CH1 = Estado de espera / condição inicial
CH2 = Ciclo RFID em andamento
CH3 = Estado correspondente à condição em que os dois sensores estão com seus feixes interrompidos

Os canais:

CH4
CH5
CH6
CH7
CH8

não participam da lógica automática deste requisito.

---

# 7. Lógica física já validada

A implementação do RF012 deve preservar a lógica dos sensores e relés já validada anteriormente nos testes da Waveshare.

A referência é:

## Situação 1 — DI1 e DI2 ativas

Significa:

Sensor de entrada = feixe livre
Sensor de saída   = feixe livre

Estado:

DI1 = ATIVA
DI2 = ATIVA

Relés:

CH1 = ON
CH2 = OFF
CH3 = OFF

RFID:

OFF

---

## Situação 2 — DI1 desativa

Significa:

um objeto chegou ao sensor de entrada e interrompeu o feixe.

Transição:

DI1:

ATIVA
  ↓
DESATIVADA

Essa transição inicia o ciclo RFID.

Resultado:

CH1 = OFF
CH2 = ON
CH3 = OFF

RFID = ON

Timer de 30 segundos = INICIADO

---

## Situação 3 — DI2 desativa durante o ciclo

Significa:

o objeto chegou ao sensor de saída e interrompeu também o segundo feixe.

Nesse momento:

DI1 = DESATIVADA
DI2 = DESATIVADA

Essa condição deve:

1. parar imediatamente a leitura RFID;
2. cancelar/finalizar o timer;
3. desligar CH1;
4. desligar CH2;
5. ligar CH3.

Resultado:

RFID = OFF

CH1 = OFF
CH2 = OFF
CH3 = ON

IMPORTANTE:

Esta é a lógica física já validada anteriormente.

NÃO retornar CH1 para ON neste momento.

---

# 8. Correção em relação à versão anterior do RF012

A versão anterior continha uma interpretação incorreta ao determinar que, após a passagem pelo DI2:

CH1 = ON
CH2 = OFF
CH3 = OFF

Essa regra deve ser DESCONSIDERADA.

Quando DI2 for interrompido enquanto DI1 também estiver interrompido:

DI1 = DESATIVADA
DI2 = DESATIVADA

o estado correto é:

CH1 = OFF
CH2 = OFF
CH3 = ON

RFID = OFF

Essa regra deve prevalecer durante a implementação.

---

# 9. Tabela principal da lógica

Utilizar a seguinte tabela como referência funcional:

| DI1 | DI2 | Situação física | RFID | CH1 | CH2 | CH3 |
|---|---|---|---|---|---|---|
| ATIVA | ATIVA | Ambos os feixes livres | OFF | ON | OFF | OFF |
| DESATIVADA | ATIVA | Objeto passou pelo sensor de entrada | ON | OFF | ON | OFF |
| DESATIVADA | DESATIVADA | Objeto interrompendo ambos / chegou ao segundo sensor | OFF | OFF | OFF | ON |

Essa é a tabela principal da implementação.

---

# 10. Estado inicial

Quando:

DI1 = ATIVA
DI2 = ATIVA

significa que nenhum objeto está interrompendo os sensores.

O sistema deve estar:

RFID = OFF

CH1 = ON
CH2 = OFF
CH3 = OFF

Estado operacional:

AGUARDANDO

---

# 11. Início do ciclo RFID

O ciclo NÃO começa quando DI1 fica ativa.

O ciclo começa quando DI1 DESATIVA.

Evento:

DI1:

ATIVA
  ↓
DESATIVADA

Interpretação:

Objeto interrompeu o sensor de entrada.

Nesse momento:

1. validar que não existe ciclo ativo;
2. desligar CH1;
3. ligar CH2;
4. garantir CH3 desligado;
5. iniciar a leitura RFID;
6. iniciar timer de 30 segundos.

---

# 12. Estado durante leitura RFID

Durante a passagem entre o sensor de entrada e o sensor de saída:

DI1 = DESATIVADA
DI2 = ATIVA

Estado esperado:

RFID = ON

CH1 = OFF
CH2 = ON
CH3 = OFF

Timer = ATIVO

Estado operacional:

LEITURA_RFID

---

# 13. Timer de 30 segundos

Quando DI1 realizar a transição:

ATIVA -> DESATIVADA

iniciar uma janela máxima de:

30 segundos

A leitura RFID poderá terminar antes dos 30 segundos caso DI2 seja interrompido.

Os 30 segundos representam apenas o tempo máximo permitido para o ciclo.

---

# 14. DI2 encerra imediatamente a leitura

Durante:

LEITURA_RFID

quando DI2 realizar:

ATIVA
  ↓
DESATIVADA

a leitura RFID deverá ser interrompida imediatamente.

Não aguardar completar os 30 segundos.

---

# 15. Estado após DI2 ser interrompido

Quando:

DI1 = DESATIVADA
DI2 = DESATIVADA

executar:

Stop RFID

Cancelar timer

CH1 = OFF
CH2 = OFF
CH3 = ON

Estado operacional:

AMBOS_INTERROMPIDOS

Essa condição representa a lógica já validada nos testes anteriores.

---

# 16. CH3 não significa automaticamente falha técnica

Importante:

Neste requisito, CH3 deve representar a condição física definida pela lógica validada:

DI1 = DESATIVADA
DI2 = DESATIVADA

Portanto, não tratar automaticamente CH3 como:

- erro de comunicação;
- falha do Zebra;
- falha do Modbus;
- exceção de software.

CH3 representa um estado físico/operacional da sequência dos sensores.

Falhas técnicas devem continuar sendo tratadas separadamente através do mecanismo de erro/log existente.

---

# 17. Retorno dos sensores ao estado livre

Após a passagem completa do objeto, os sensores voltarão fisicamente ao estado normal.

Quando ambos retornarem para:

DI1 = ATIVA
DI2 = ATIVA

o sistema deve retornar para:

CH1 = ON
CH2 = OFF
CH3 = OFF

RFID = OFF

Estado:

AGUARDANDO

O sistema estará pronto para receber o próximo objeto.

---

# 18. Sequência completa esperada

## Etapa A — Sem objeto

DI1 = ATIVA
DI2 = ATIVA

RFID = OFF

CH1 = ON
CH2 = OFF
CH3 = OFF

---

## Etapa B — Objeto interrompe DI1

DI1 = DESATIVADA
DI2 = ATIVA

Executar:

Start RFID

Timer = 30 segundos

Relés:

CH1 = OFF
CH2 = ON
CH3 = OFF

---

## Etapa C — Objeto chega ao DI2

DI1 = DESATIVADA
DI2 = DESATIVADA

Executar:

Stop RFID

Cancelar timer

Relés:

CH1 = OFF
CH2 = OFF
CH3 = ON

---

## Etapa D — Objeto deixa os sensores

DI1 = ATIVA
DI2 = ATIVA

RFID permanece OFF.

Relés:

CH1 = ON
CH2 = OFF
CH3 = OFF

Sistema pronto para novo ciclo.

---

# 19. Diagrama do ciclo

Fluxo esperado:

DI1 ATIVA + DI2 ATIVA
        |
        | objeto chega
        v
DI1 DESATIVA
        |
        +--> CH1 OFF
        +--> CH2 ON
        +--> CH3 OFF
        +--> START RFID
        +--> TIMER 30s
        |
        v
Objeto segue pelo processo
        |
        v
DI2 DESATIVA
        |
        +--> STOP RFID
        +--> cancelar timer
        +--> CH1 OFF
        +--> CH2 OFF
        +--> CH3 ON
        |
        v
Objeto deixa os sensores
        |
        v
DI1 ATIVA + DI2 ATIVA
        |
        +--> RFID OFF
        +--> CH1 ON
        +--> CH2 OFF
        +--> CH3 OFF
        |
        v
AGUARDAR PRÓXIMO OBJETO

---

# 20. Detecção por transição

Não executar ações repetidamente apenas porque uma entrada permanece no mesmo estado.

Para DI1, detectar especificamente a transição:

ATIVA -> DESATIVADA

Essa transição representa:

ENTRADA DO OBJETO

Para DI2, durante um ciclo ativo, detectar:

ATIVA -> DESATIVADA

Essa transição representa:

SAÍDA / SEGUNDO SENSOR ATINGIDO

---

# 21. Estado anterior das entradas

Manter internamente o estado anterior de:

DI1
DI2

Conceitualmente:

previous_di1
current_di1

previous_di2
current_di2

Somente gerar eventos quando houver uma transição relevante.

---

# 22. Não iniciar RFID repetidamente

Se DI1 permanecer:

DESATIVADA

durante vários ciclos de polling, executar:

Start RFID

apenas uma vez.

Não:

- reiniciar RFID;
- criar novo timer;
- reiniciar os 30 segundos;
- criar novo ciclo.

---

# 23. Encerramento por DI2 apenas durante ciclo válido

DI2 deve encerrar a leitura quando houver um ciclo iniciado anteriormente por DI1.

Não executar lógica de encerramento de ciclo indevidamente caso DI2 seja interrompido sem existir um ciclo RFID ativo.

Registrar a ocorrência para diagnóstico quando necessário.

---

# 24. Timeout de 30 segundos

Se após DI1 desativar:

DI2 não desativar dentro de 30 segundos

a leitura RFID deverá ser interrompida obrigatoriamente.

Fluxo:

DI1 DESATIVA
    ↓
RFID ON
    ↓
30 segundos
    ↓
DI2 não foi interrompida
    ↓
STOP RFID

Não permitir leitura RFID indefinida.

---

# 25. Estado após timeout

O timeout representa uma condição anormal do ciclo.

Ao atingir 30 segundos sem a transição esperada de DI2:

1. parar RFID;
2. desligar CH2;
3. cancelar/finalizar timer;
4. registrar timeout;
5. impedir que a leitura continue indefinidamente.

A condição dos relés após timeout deve respeitar prioritariamente o estado físico real dos sensores e a lógica já validada.

Não sobrescrever incorretamente a tabela física dos sensores apenas para representar uma falha técnica.

Caso seja necessário um estado visual/software específico de timeout, mantê-lo internamente e no log.

Não inventar uma nova combinação física de CH1/CH2/CH3 sem requisito adicional.

---

# 26. Prioridade da lógica física

A tabela física dos sensores deve ser a referência principal:

DI1 ATIVA + DI2 ATIVA
-> CH1

DI1 DESATIVADA + DI2 ATIVA
-> CH2 durante ciclo RFID

DI1 DESATIVADA + DI2 DESATIVADA
-> CH3

Essa regra não deve ser substituída por interpretações anteriores do RF012.

---

# 27. RFID somente durante a janela de leitura

RFID deve estar ON somente durante o ciclo iniciado pela interrupção de DI1 e antes de:

- DI2 ser interrompida; ou
- ocorrer timeout de 30 segundos.

Conceitualmente:

DI1 DESATIVA
    ↓
RFID ON
    ↓
DI2 DESATIVA OU timeout
    ↓
RFID OFF

---

# 28. Integração com o Zebra FX9600

Reutilizar a implementação existente de Start/Stop RFID.

Não criar um segundo mecanismo de inventário LLRP.

Fluxo:

Evento DI1
    ↓
Controller da lógica
    ↓
serviço RFID existente
    ↓
Start Inventory
    ↓
FX9600

E:

Evento DI2 / timeout
    ↓
Controller da lógica
    ↓
serviço RFID existente
    ↓
Stop Inventory
    ↓
FX9600

---

# 29. Processamento dos EPCs

Durante a leitura RFID, preservar integralmente o comportamento atual.

Isso inclui:

- recebimento dos EPCs;
- validação;
- deduplicação;
- consulta à API;
- consideração somente dos EPCs encontrados;
- atualização da tabela;
- atualização do contador.

Não alterar essas regras no RF012.

---

# 30. Sessão RFID

Analisar como o sistema atualmente controla uma sessão iniciada pelo botão Start.

A leitura iniciada por DI1 deve reutilizar o mesmo mecanismo sempre que possível.

Não criar dois motores de leitura separados:

manual_rfid_engine
automatic_rfid_engine

Reutilizar o serviço existente.

---

# 31. CH1

CH1 representa o estado:

AGUARDANDO / FEIXES LIVRES

CH1 deve estar ON quando:

DI1 = ATIVA
DI2 = ATIVA

e nenhum ciclo RFID estiver em andamento.

---

# 32. CH2

CH2 representa:

LEITURA RFID EM ANDAMENTO

CH2 deve ser ligado quando:

DI1 realiza ATIVA -> DESATIVADA

e o Start RFID for realizado corretamente.

CH2 deve ser desligado quando:

- DI2 desativar;
- ocorrer timeout;
- leitura RFID precisar ser abortada.

---

# 33. CH3

CH3 representa a condição:

DI1 = DESATIVADA
DI2 = DESATIVADA

Ou seja:

os dois feixes estão interrompidos.

Nesse estado:

RFID = OFF

CH1 = OFF
CH2 = OFF
CH3 = ON

---

# 34. Exclusividade CH1/CH2/CH3

Durante a operação automática, apenas um dos três relés deve representar o estado operacional.

Evitar combinações como:

CH1 ON + CH2 ON

CH1 ON + CH3 ON

CH2 ON + CH3 ON

Estados principais:

AGUARDANDO:
CH1 ON

LEITURA:
CH2 ON

AMBOS_INTERROMPIDOS:
CH3 ON

---

# 35. CH4 até CH8

Não utilizar automaticamente:

CH4
CH5
CH6
CH7
CH8

O RF012 deve controlar automaticamente somente:

CH1
CH2
CH3

Não alterar CH4-CH8 durante transições dos sensores.

---

# 36. Falha ao iniciar RFID

Caso DI1 desative mas o Zebra não consiga iniciar a leitura:

não indicar falsamente que existe leitura RFID em andamento.

Portanto:

- não manter CH2 como indicador de leitura ativa;
- não considerar Start RFID concluído;
- registrar erro;
- tratar a falha através da infraestrutura existente.

O Codex deve analisar o comportamento atual do serviço RFID antes de definir a recuperação.

---

# 37. Falha ao parar RFID

Caso DI2 desative e o Stop RFID apresente falha:

- registrar erro;
- não ignorar a exceção;
- não iniciar uma nova leitura enquanto o estado anterior estiver inconsistente;
- utilizar o tratamento seguro já existente no serviço RFID.

Não alterar a interpretação física de DI1/DI2 por causa de uma falha técnica.

---

# 38. Perda da Waveshare

Se a comunicação com a Waveshare for perdida durante uma leitura:

1. solicitar Stop RFID;
2. cancelar o timer;
3. interromper o ciclo automático;
4. registrar a falha;
5. não continuar leitura indefinidamente.

Como o estado dos relés não poderá ser confirmado sem Modbus, não assumir que um comando foi executado.

---

# 39. Perda do Zebra

Se o Zebra perder comunicação durante o ciclo:

1. interromper o ciclo;
2. cancelar o timer;
3. registrar a falha;
4. não continuar indicando leitura RFID ativa.

A lógica de recuperação deve respeitar a arquitetura existente.

---

# 40. Timer não bloqueante

O timer de 30 segundos não deve bloquear a thread principal.

A interface deve continuar funcionando normalmente durante:

- polling Modbus;
- leitura RFID;
- processamento de EPC;
- consultas API;
- timer.

---

# 41. Timer único por ciclo

Criar apenas um timer por ciclo.

DI1 permanecer desativada não deve criar novos timers.

---

# 42. Proteção contra timer antigo

Cada timer deve estar associado ao ciclo que o criou.

Cenário:

Ciclo A inicia
    ↓
DI2 encerra Ciclo A
    ↓
Ciclo B inicia
    ↓
callback antigo do Ciclo A

O callback antigo NÃO pode interromper o RFID do Ciclo B.

Implementar identificação/cancelamento adequado do ciclo.

---

# 43. Inicialização da lógica

Ao iniciar o monitoramento automático:

1. conectar/validar Waveshare;
2. ler DI1 e DI2;
3. armazenar os estados iniciais;
4. NÃO tratar a primeira leitura como uma transição;
5. somente depois começar a detectar mudanças.

Isso é fundamental.

Exemplo:

aplicação inicia e DI1 já está DESATIVADA.

A aplicação não deve assumir automaticamente que acabou de ocorrer uma nova passagem.

---

# 44. Retorno ao estado AGUARDANDO

Após o objeto deixar completamente a região dos sensores:

DI1 = ATIVA
DI2 = ATIVA

executar estado:

AGUARDANDO

Garantir:

RFID = OFF
CH1 = ON
CH2 = OFF
CH3 = OFF

O próximo ciclo poderá então ser iniciado.

---

# 45. Novo ciclo

Um novo ciclo somente deve começar após o sistema ter retornado para uma condição válida de espera.

Fluxo esperado:

AGUARDANDO
    ↓
DI1 DESATIVA
    ↓
LEITURA
    ↓
DI2 DESATIVA
    ↓
AMBOS_INTERROMPIDOS
    ↓
DI1/DI2 retornam
    ↓
AGUARDANDO
    ↓
novo ciclo permitido

Evitar que oscilações do sensor criem múltiplos ciclos.

---

# 46. Debounce / estabilidade

Antes de adicionar qualquer debounce artificial, verificar se já existe tratamento no código de leitura da Waveshare.

Caso os sensores apresentem oscilações reais durante os testes, utilizar uma estratégia mínima de estabilidade/debounce.

Não adicionar atrasos arbitrários que prejudiquem a detecção da passagem.

Documentar qualquer debounce implementado.

---

# 47. Tela de diagnóstico

A tela de teste da Waveshare criada anteriormente deve continuar funcionando.

Ela deve continuar permitindo:

- visualizar DI1-DI5;
- testar CH1-CH8 manualmente.

Entretanto, controle manual e controle automático não devem disputar os mesmos relés simultaneamente.

---

# 48. Modo diagnóstico versus automático

Evitar:

modo automático controlando CH1
+
usuário da tela de teste controlando CH1

simultaneamente.

Quando a lógica automática estiver ativa, impedir ou desabilitar comandos manuais conflitantes de CH1-CH3.

Não alterar CH4-CH8 por causa dessa restrição, salvo se tecnicamente necessário.

---

# 49. Botões Start/Stop RFID existentes

Não remover os controles manuais existentes.

Analisar como impedir conflito entre:

Start manual
Stop manual
Start automático por DI1
Stop automático por DI2

Não permitir dois inventários simultâneos.

Não criar dois estados independentes para o mesmo Zebra.

---

# 50. Logging

Registrar somente eventos relevantes.

Exemplos:

DI1: ATIVA -> DESATIVADA
Objeto detectado na entrada
Iniciando RFID
RFID iniciado
CH2 ativado
DI2: ATIVA -> DESATIVADA
Objeto detectado na saída
Parando RFID
RFID parado
CH3 ativado
Sensores liberados
CH1 ativado
Timeout RFID
Falha Waveshare
Falha Zebra

Não gerar log a cada polling quando nada mudou.

---

# 51. Cenário de teste — estado inicial

Entradas:

DI1 = ATIVA
DI2 = ATIVA

Esperado:

RFID = OFF
CH1 = ON
CH2 = OFF
CH3 = OFF

---

# 52. Cenário de teste — objeto chega à entrada

Inicial:

DI1 = ATIVA
DI2 = ATIVA

Evento:

DI1 -> DESATIVADA

Esperado:

Start RFID

Timer = 30 segundos

CH1 = OFF
CH2 = ON
CH3 = OFF

---

# 53. Cenário de teste — DI1 permanece interrompida

Após iniciar o ciclo:

DI1 = DESATIVADA
DI2 = ATIVA

Manter essa condição durante vários pollings.

Esperado:

- somente um Start RFID;
- somente um timer;
- CH2 permanece ON;
- timer não reinicia.

---

# 54. Cenário de teste — objeto chega ao segundo sensor

Estado anterior:

DI1 = DESATIVADA
DI2 = ATIVA

Evento:

DI2 -> DESATIVADA

Resultado:

DI1 = DESATIVADA
DI2 = DESATIVADA

Esperado:

Stop RFID
Timer cancelado

CH1 = OFF
CH2 = OFF
CH3 = ON

---

# 55. Cenário de teste — sensores ficam livres novamente

Estado anterior:

DI1 = DESATIVADA
DI2 = DESATIVADA

Após passagem do objeto:

DI1 = ATIVA
DI2 = ATIVA

Esperado:

RFID = OFF

CH1 = ON
CH2 = OFF
CH3 = OFF

Sistema pronto para novo ciclo.

---

# 56. Cenário de teste — ciclo completo

Sequência:

1.
DI1 = ATIVA
DI2 = ATIVA

Resultado:
CH1

2.
DI1 = DESATIVADA
DI2 = ATIVA

Resultado:
CH2 + RFID ON + timer

3.
DI1 = DESATIVADA
DI2 = DESATIVADA

Resultado:
CH3 + RFID OFF + timer cancelado

4.
DI1 = ATIVA
DI2 = ATIVA

Resultado:
CH1 + pronto para novo ciclo

Essa sequência deve ser utilizada como principal teste funcional do RF012.

---

# 57. Cenário de teste — timeout

Sequência:

DI1 = ATIVA
DI2 = ATIVA
    ↓
DI1 = DESATIVADA
DI2 = ATIVA
    ↓
RFID ON
    ↓
DI2 não desativa
    ↓
30 segundos

Esperado:

RFID = OFF
CH2 = OFF
timeout registrado

O estado subsequente dos relés deve continuar respeitando a condição física real dos sensores e a lógica definida neste requisito.

---

# 58. Testes automatizados

Os testes automatizados não devem depender do hardware real.

Utilizar mocks/fakes para:

- Waveshare;
- Zebra;
- timer.

Cobrir no mínimo:

- DI1/DI2 inicialmente ativas;
- primeira leitura não gerar evento;
- DI1 ativa -> desativada;
- Start RFID;
- CH1 OFF;
- CH2 ON;
- CH3 OFF;
- timer iniciado;
- DI1 mantida desativada;
- DI2 ativa -> desativada;
- Stop RFID;
- cancelamento do timer;
- CH1 OFF;
- CH2 OFF;
- CH3 ON;
- retorno DI1/DI2 para ativas;
- CH1 ON;
- CH2 OFF;
- CH3 OFF;
- timeout;
- timer antigo;
- múltiplos ciclos;
- falha Waveshare;
- falha Zebra;
- CH4-CH8 não alterados;
- conflito diagnóstico/automático.

---

# 59. Teste manual obrigatório

Executar no Windows com hardware real.

## Estado inicial

Confirmar:

DI1 = ATIVA
DI2 = ATIVA

CH1 = ON
CH2 = OFF
CH3 = OFF

RFID = OFF

## Interromper sensor de entrada

Cortar fisicamente o feixe de DI1.

Confirmar:

DI1 = DESATIVADA

CH1 = OFF
CH2 = ON
CH3 = OFF

RFID inicia.

## Interromper sensor de saída

Durante os 30 segundos, cortar DI2.

Confirmar:

DI2 = DESATIVADA

RFID para.

CH1 = OFF
CH2 = OFF
CH3 = ON

## Liberar sensores

Após o objeto deixar os sensores, confirmar:

DI1 = ATIVA
DI2 = ATIVA

CH1 = ON
CH2 = OFF
CH3 = OFF

RFID permanece parado.

---

# 60. Fora do escopo

NÃO implementar neste requisito:

- lógica para DI3;
- lógica para DI4;
- lógica para DI5;
- controle automático CH4;
- controle automático CH5;
- controle automático CH6;
- controle automático CH7;
- controle automático CH8;
- alterações na API;
- alterações no Power Automate;
- alterações no SharePoint;
- histórico de ciclos;
- dashboard;
- relatórios;
- estatísticas;
- configuração do timeout pela interface;
- redesign da aplicação.

O timeout permanece fixo em:

30 segundos

---

# 61. Preservar funcionalidades existentes

Não alterar sem necessidade:

- configuração do Zebra;
- configuração da Waveshare;
- tela de diagnóstico;
- teste DI1-DI5;
- teste CH1-CH8;
- comunicação Modbus;
- comunicação LLRP;
- processamento de EPC;
- consulta API;
- tabela RFID;
- contador de EPCs encontrados;
- navegação;
- logging existente.

---

# 62. Análise obrigatória antes da implementação

Antes de modificar qualquer código, analisar:

1. AGENTS.md;
2. implementação atual da Waveshare;
3. RF anterior da tela de diagnóstico;
4. código já validado dos sensores;
5. polaridade atual de DI1;
6. polaridade atual de DI2;
7. representação de entrada ativa/desativada;
8. controle CH1-CH8;
9. Start RFID atual;
10. Stop RFID atual;
11. estado do inventário RFID;
12. timer/threading existente;
13. polling Modbus;
14. concorrência serial;
15. modo diagnóstico;
16. processamento de EPC;
17. cleanup do Zebra;
18. cleanup da Waveshare.

A implementação deve partir da lógica física já validada.

---

# 63. Confirmação obrigatória da polaridade

Antes de implementar, o Codex deve confirmar no código existente que:

FEIXE LIVRE
-> entrada digital ATIVA

FEIXE INTERROMPIDO
-> entrada digital DESATIVADA

Se o código existente representar os valores brutos de outra maneira, criar/adaptar uma camada semântica clara.

Por exemplo:

is_beam_clear
is_beam_blocked

ou equivalente.

Evitar espalhar comparações de 0/1 por toda a lógica operacional.

---

# 64. Plano antes da alteração

Antes de escrever código, apresentar:

- arquivos que serão alterados;
- como DI1/DI2 são lidas;
- polaridade encontrada;
- como será representado feixe livre/interrompido;
- como as transições serão detectadas;
- como Start RFID será reutilizado;
- como Stop RFID será reutilizado;
- como CH1-CH3 serão controlados;
- como o timer será implementado;
- como timer antigo será invalidado;
- como conflito diagnóstico/automático será evitado.

Somente depois implementar.

---

# 65. Alterações mínimas

Não realizar refatoração geral.

Implementar somente a integração necessária entre:

DI1
DI2
CH1
CH2
CH3
Timer 30 segundos
Start RFID
Stop RFID

Não alterar automaticamente CH4-CH8.

---

# 66. Critérios de aceite

O RF012 será considerado concluído quando:

1. o sistema reconhecer que DI ativa significa feixe livre;
2. o sistema reconhecer que DI desativada significa feixe interrompido;
3. DI1 ATIVA -> DESATIVADA iniciar o ciclo;
4. DI1 interrompida iniciar RFID;
5. CH1 desligar no início da leitura;
6. CH2 ligar durante leitura;
7. CH3 permanecer desligado durante leitura;
8. timer de 30 segundos iniciar uma única vez;
9. DI1 mantida desativada não reiniciar ciclo;
10. DI2 ATIVA -> DESATIVADA encerrar RFID;
11. DI2 interrompida parar RFID imediatamente;
12. timer ser cancelado após DI2;
13. DI1 e DI2 desativadas resultarem em CH3 ON;
14. nessa condição CH1 permanecer OFF;
15. nessa condição CH2 permanecer OFF;
16. quando DI1 e DI2 voltarem a ATIVA, CH1 voltar a ON;
17. nesse retorno CH2 ficar OFF;
18. nesse retorno CH3 ficar OFF;
19. RFID permanecer OFF após encerramento;
20. novo ciclo somente iniciar de maneira controlada;
21. timeout parar RFID após 30 segundos;
22. timer antigo não interferir em novo ciclo;
23. CH4-CH8 não serem alterados;
24. processamento de EPC continuar funcionando;
25. tela de diagnóstico continuar funcionando;
26. UI não bloquear;
27. falhas de comunicação serem tratadas;
28. implementação funcionar no Windows;
29. testes automatizados passarem;
30. teste físico reproduzir a lógica já validada.

---

# 67. Validação

Executar exclusivamente no Windows utilizando o ambiente virtual oficial do projeto.

Executar as ferramentas já existentes no projeto.

Quando disponíveis:

ruff check .
ruff format --check .
mypy src
pytest

Não instalar ou atualizar dependências sem necessidade.

---

# 68. Relatório final esperado

Ao concluir, informar:

- análise realizada;
- arquivos alterados;
- polaridade real identificada de DI1;
- polaridade real identificada de DI2;
- representação utilizada para feixe livre;
- representação utilizada para feixe interrompido;
- transição utilizada para iniciar RFID;
- transição utilizada para parar RFID;
- método reutilizado para Start RFID;
- método reutilizado para Stop RFID;
- comportamento de CH1;
- comportamento de CH2;
- comportamento de CH3;
- implementação do timer de 30 segundos;
- tratamento de timeout;
- proteção contra timers antigos;
- tratamento de concorrência;
- tratamento de falha Waveshare;
- tratamento de falha Zebra;
- testes criados;
- resultados dos testes;
- validação física realizada ou pendente;
- confirmação de que CH4-CH8 não foram alterados;
- confirmação de que a lógica implementada corresponde à lógica física já validada.