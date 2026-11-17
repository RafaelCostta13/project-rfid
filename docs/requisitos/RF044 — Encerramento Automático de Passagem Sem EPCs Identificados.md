# RF044 — Encerramento Automático de Passagem Sem EPCs Identificados

Projeto: DSV RFID System
Requisito: RF044
Requisitos relacionados: RF012, RF037, RF042, RF043
Categoria: RFID / Automação / Controle de Sessão
Tecnologia: Python + PySide6/QML
Hardware: Zebra FX9600 + Waveshare Modbus RTU Relay D
Sistema operacional: Windows
Prioridade: Alta
Tipo de alteração: Lógica operacional / Tratamento de timeout

---

## 1. OBJETIVO

Implementar o encerramento automático de uma
passagem RFID quando o temporizador de inventário
chegar a zero e nenhuma etiqueta válida tiver
sido identificada pelo leitor.

Atualmente, o inventário RFID possui
um temporizador de 20 segundos.

Quando esse temporizador termina,
o inventário é interrompido, mas a passagem
permanece aberta aguardando:

- Acionamento do sensor DI2.
- Reabertura pelo pedal DI3.

Esse comportamento pode impedir
o início de uma nova passagem.

Exemplo:

    DI1 inicia a passagem.

    O inventário permanece ativo por 20 segundos.

    Nenhum EPC é identificado.

    O temporizador termina.

    O sensor DI2 não é acionado.

    O sistema permanece aguardando
    o encerramento da passagem.

    Um novo acionamento de DI1
    não inicia outra passagem.

O objetivo do RF044 é corrigir
esse comportamento.

NOVA REGRA:

    TIMEOUT DE 20 SEGUNDOS
                |
                v
    VERIFICAR EPCs IDENTIFICADOS
                |
                +---- 0 EPCs
                |       |
                |       v
                |   ENCERRAR PASSAGEM
                |       |
                |       v
                |   RETORNAR AO ESTADO PRONTO
                |
                +---- 1 OU MAIS EPCs
                        |
                        v
                    PRESERVAR PASSAGEM
                        |
                        v
                    AGUARDAR DI2 OU DI3

IMPORTANTE:

Não alterar o tempo atual de inventário.

Não adicionar um segundo temporizador.

Não modificar as regras de início
e encerramento estabelecidas no RF043.

---

## 2. CONTEXTO OPERACIONAL

O sistema utiliza:

    DI1 — Sensor de entrada.

    DI2 — Sensor de saída.

    DI3 — Pedal de acionamento manual
          e reabertura da passagem.

O inventário pode ser iniciado por:

    DI1 — Início automático.

    DI3 — Início manual.

O encerramento definitivo normal ocorre por:

    DI2 — Sensor de saída.

O pedal DI3 também permite
reabrir uma passagem cujo inventário
tenha sido interrompido por timeout.

Entretanto, uma passagem que não
identificou nenhuma etiqueta não precisa
permanecer indefinidamente aberta.

Por isso, implementaremos uma condição
de encerramento automático baseada
na quantidade de EPCs identificados.

---

## 3. NOVA REGRA DE TIMEOUT

Quando o temporizador de 20 segundos
chegar a zero, o sistema deverá:

1. Interromper o inventário RFID.

2. Verificar a quantidade de EPCs
   únicos válidos identificados
   durante a passagem.

3. Avaliar o resultado.

4. Executar uma das duas condições:

    CONDIÇÃO A:
        Nenhum EPC identificado.

    CONDIÇÃO B:
        Um ou mais EPCs identificados.

A verificação deverá utilizar
a contagem real de EPCs únicos
da passagem atual.

Não utilizar a quantidade bruta
de eventos recebidos do Zebra.

Não utilizar somente o número
de linhas atualmente visíveis na tabela.

---

## 4. CONDIÇÃO A — ZERO EPCs IDENTIFICADOS

Quando o temporizador chegar a zero
e a quantidade de EPCs identificados
for igual a zero:

    EPCs identificados = 0

O sistema deverá:

1. Parar o inventário RFID.

2. Finalizar o temporizador.

3. Encerrar definitivamente
   a passagem atual.

4. Limpar o contexto operacional
   da passagem vazia.

5. Descartar estados pendentes
   de complementação.

6. Impedir a reabertura
   da passagem vazia pelo DI3.

7. Retornar ao estado pronto,
   desde que não exista erro impeditivo.

8. Permitir o início de uma nova passagem.

Não exigir o acionamento do DI2
para finalizar essa passagem vazia.

IMPORTANTE:

O retorno ao estado pronto deverá
utilizar a rotina centralizada
de encerramento existente.

Não criar uma segunda implementação
independente de finalização.

---

## 5. NOVA PASSAGEM APÓS TIMEOUT SEM EPCs

Após o encerramento automático,
o sistema deverá aceitar normalmente:

    DI1 — Nova passagem automática.

    DI3 — Nova passagem manual.

Exemplo:

    DI1 acionado.
        |
        v
    Inventário iniciado.
        |
        v
    Timeout de 20 segundos.
        |
        v
    Zero EPCs encontrados.
        |
        v
    Passagem encerrada.
        |
        v
    Sistema pronto.
        |
        v
    Novo DI1 acionado.
        |
        v
    Nova passagem iniciada.

Não reutilizar a passagem anterior.

Não preservar estados de
AGUARDANDO_COMPLEMENTACAO
para uma passagem vazia.

O novo inventário deverá utilizar
um contexto de passagem independente.

IMPORTANTE:

Exigir um novo evento válido
de acionamento dos sensores.

Se DI1 permanecer fisicamente acionado
após o encerramento automático,
não iniciar outra passagem repetidamente.

O mesmo vale para o pedal DI3.

Preservar o controle de borda
e o debounce existentes.

---

## 6. CONDIÇÃO B — UM OU MAIS EPCs IDENTIFICADOS

Quando o temporizador terminar
e existir pelo menos um EPC válido
identificado na passagem:

    EPCs identificados >= 1

O comportamento deverá permanecer
exatamente como no RF043.

O sistema deverá:

1. Parar o inventário RFID.

2. Finalizar o temporizador.

3. Preservar a passagem lógica.

4. Preservar os EPCs encontrados.

5. Preservar os registros da tabela.

6. Preservar os contadores.

7. Entrar no estado:

    AGUARDANDO_COMPLEMENTACAO

8. Permitir reabertura pelo DI3.

9. Permitir encerramento definitivo
   pelo sensor DI2.

IMPORTANTE:

Não encerrar automaticamente
uma passagem que tenha identificado
um ou mais EPCs válidos.

Não alterar o funcionamento
do pedal nesse cenário.

---

## 7. CONTAGEM UTILIZADA NA DECISÃO

O RF043 implementou o indicador:

    EPCs identificados: X

Esse indicador representa
a quantidade de EPCs únicos válidos
recebidos pelo leitor RFID.

A contagem considera:

- EPCs normalizados.
- EPCs com prefixos autorizados.
- EPCs encontrados na base.
- EPCs classificados como Extra box.

Não considera:

- EPCs duplicados na mesma passagem.
- EPCs inválidos.
- EPCs com prefixos não autorizados.

O RF044 deverá utilizar
a mesma fonte de dados
desse indicador.

IMPORTANTE:

Não criar um segundo contador
independente para o timeout.

A decisão de encerramento
deverá utilizar o conjunto
de EPCs únicos válidos já mantido
pelo controlador da passagem.

O label da interface e a decisão
de timeout deverão apresentar
resultados consistentes.

---

## 8. EXEMPLOS DE COMPORTAMENTO

### Exemplo 1 — Nenhuma etiqueta

    DI1 inicia leitura.

    Tempo: 20 segundos.

    EPCs identificados: 0.

    Timeout.

Resultado:

    Encerrar passagem automaticamente.

    Retornar ao estado pronto.

    Permitir novo DI1 ou DI3.

### Exemplo 2 — Uma etiqueta encontrada

    DI1 inicia leitura.

    EPCs identificados: 1.

    Timeout.

Resultado:

    Parar inventário.

    Preservar passagem.

    Aguardar DI2 ou DI3.

### Exemplo 3 — Dez etiquetas encontradas

    DI1 inicia leitura.

    EPCs identificados: 10.

    Timeout.

Resultado:

    Preservar os 10 EPCs.

    Aguardar DI2 ou DI3.

### Exemplo 4 — Apenas Extra box

    DI1 inicia leitura.

    EPCs encontrados: 0.

    Extra box: 2.

    EPCs identificados: 2.

    Timeout.

Resultado:

    Preservar passagem.

    Permitir complementação.

Não encerrar automaticamente,
pois existem EPCs válidos identificados.

### Exemplo 5 — Apenas EPCs não autorizados

    DI1 inicia leitura.

    Reader recebe etiquetas
    com prefixos não autorizados.

    EPCs identificados: 0.

    Timeout.

Resultado:

    Encerrar passagem automaticamente.

    Retornar ao estado pronto.

### Exemplo 6 — Início manual sem etiquetas

    DI3 inicia nova passagem.

    Nenhum EPC identificado.

    Timeout de 20 segundos.

Resultado:

    Encerrar passagem automaticamente.

    Retornar ao estado pronto.

    Novo acionamento DI3 poderá
    iniciar outra passagem manual.

---

## 9. PRESERVAR O PEDAL DI3

O pedal continuará com
duas funcionalidades.

### 9.1 Início manual

Quando não existir passagem aberta:

    DI3 inicia nova passagem.

### 9.2 Reabertura após timeout

Quando existir passagem
aguardando complementação:

    DI3 reabre a mesma passagem.

Entretanto, a reabertura
somente será permitida
se o timeout tiver ocorrido
com pelo menos um EPC válido
identificado na passagem.

Exemplo:

    EPCs identificados: 5.

    Timeout.

    DI3 acionado.

Resultado:

    Reabrir mesma passagem.

    Preservar os 5 EPCs.

    Reiniciar timer de 20 segundos.

Se o timeout ocorrer com zero EPCs:

    Encerrar passagem.

Nesse cenário, um acionamento posterior
de DI3 deverá iniciar uma NOVA passagem,
e não reabrir a passagem vazia.

IMPORTANTE:

Não modificar o debounce do pedal.

Não permitir múltiplas ações
com o pedal mantido pressionado.

---

## 10. PRESERVAR O SENSOR DI1

O DI1 continuará sendo
o sensor de entrada.

Quando o sistema estiver pronto:

    DI1 acionado
        |
        v
    Iniciar inventário RFID.

Após um timeout sem EPCs:

    Encerrar passagem vazia.

    Retornar ao estado pronto.

    Aguardar novo acionamento válido
    de DI1.

Não exigir DI2 para liberar
o próximo acionamento de DI1.

Não exigir DI4.

Não modificar o comportamento
de início manual pelo DI3.

---

## 11. PRESERVAR O SENSOR DI2

O DI2 continuará sendo
o sensor de saída.

Quando acionado durante
uma passagem existente:

    Encerrar definitivamente
    a passagem.

Essa regra deverá funcionar
independentemente da quantidade
de EPCs identificados.

Exemplos:

    DI2 + 0 EPCs:
        Encerrar passagem.

    DI2 + 1 EPC:
        Encerrar passagem.

    DI2 + 10 EPCs:
        Encerrar passagem.

O RF044 não deverá modificar
o encerramento normal pelo DI2.

A nova regra será aplicada
exclusivamente ao timeout
sem EPCs válidos.

---

## 12. TEMPORIZADOR DE INVENTÁRIO

Preservar o tempo atual:

    20 segundos.

Não retornar para:

    30 segundos.

    60 segundos.

O temporizador deverá continuar
sendo iniciado após:

- DI1 válido.
- DI3 iniciando nova passagem.
- DI3 reabrindo passagem elegível.

Não adicionar temporizadores
de recuperação.

Não implementar contagem regressiva
adicional para encerramento automático.

A nova condição deverá ser avaliada
quando o timer existente atingir zero.

---

## 13. CONTROLE DOS RELÉS

Preservar a lógica atual
dos relés da Waveshare.

### Sistema pronto

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

### Inventário ativo

    CH1 = OFF
    CH2 = ON
    CH3 = OFF

### Timeout com zero EPCs

Resultado:

    Passagem encerrada.

    Sistema pronto.

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

### Timeout com um ou mais EPCs

Resultado:

    Inventário parado.

    Passagem aguardando complementação.

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

### Erro operacional

Preservar:

    CH1 = OFF
    CH2 = OFF
    CH3 = ON

IMPORTANTE:

O timeout não poderá sobrescrever
um estado de erro impeditivo
com o estado pronto.

Não criar comandos Modbus
diretamente na nova regra de timeout.

Utilizar o controlador operacional
existente para atualizar os relés.

---

## 14. CONTROLE DOS ESTADOS

Reutilizar a máquina de estados
existente no projeto.

Estados relevantes:

    PRONTO

    LEITURA_ATIVA

    AGUARDANDO_COMPLEMENTACAO

    PASSAGEM_ENCERRADA

    ERRO

A nova transição será:

    LEITURA_ATIVA
          |
          v
       TIMEOUT
          |
          v
    EPCs IDENTIFICADOS?
          |
          +--- ZERO
          |     |
          |     v
          |  ENCERRAR PASSAGEM
          |     |
          |     v
          |   PRONTO
          |
          +--- UM OU MAIS
                |
                v
          AGUARDANDO_COMPLEMENTACAO

Não criar uma segunda máquina
de estados independente.

Não utilizar variáveis isoladas
que possam ficar inconsistentes
com o controlador principal.

---

## 15. PREVENÇÃO DE CONDIÇÕES DE CORRIDA

Garantir que o encerramento automático
não entre em conflito com:

- Eventos DI1.
- Eventos DI2.
- Eventos DI3.
- Callbacks do inventário RFID.
- Atualizações de EPCs.
- Temporizador.
- Encerramento manual.

### 15.1 DI2 e timeout simultâneos

Se DI2 e o timeout ocorrerem
praticamente ao mesmo tempo:

    Encerrar a passagem uma única vez.

    Não executar finalização duplicada.

### 15.2 Novo EPC próximo ao timeout

Garantir que a decisão utilize
um estado consistente dos EPCs
já recebidos e aceitos
para a passagem.

Não encerrar a passagem como vazia
enquanto houver EPCs já recebidos
aguardando processamento
na fila correspondente.

O Codex deverá considerar
o processamento assíncrono
de eventos RFID e consultas HTTP.

### 15.3 DI3 próximo ao timeout

Evitar que o pedal execute
simultaneamente:

    Nova passagem.

    Reabertura da passagem anterior.

Uma única transição deverá
ser confirmada pelo controlador.

### 15.4 Eventos atrasados

Após o encerramento da passagem vazia,
não permitir que callbacks atrasados
sejam associados incorretamente
a uma nova passagem.

Utilizar a identificação ou geração
de sessão existente para manter
o isolamento dos registros.

---

## 16. REGISTRO DA PASSAGEM

O encerramento automático deverá
utilizar o mecanismo de finalização
já existente no projeto.

Entretanto, será necessário
identificar o motivo do encerramento.

Motivo conceitual:

    timeout_sem_epcs

Esse motivo deverá ser utilizado
internamente para diagnóstico
e rastreabilidade.

O Codex deverá verificar
como o backend atualmente registra
o encerramento de uma passagem.

Preservar:

    GET /api/v1/rfid_records/:epc

    POST /api/v1/rfid_reads

Não inventar novos endpoints.

Não modificar o contrato
da API Rails neste requisito.

Não enviar registros fictícios
de EPCs quando nenhuma etiqueta
tiver sido identificada.

Se a implementação atual
possuir registro de sessão vazia,
preservar o contrato existente
e adaptar somente o motivo interno,
quando suportado.

Não duplicar requisições POST.

---

## 17. PRESERVAR A INTERFACE START

Não modificar o layout
da tela Start.

Preservar:

- Card EPCs encontrados.
- Card Extra box.
- Label EPCs identificados.
- Lista de inventário.
- Sete colunas.
- Altura mínima de 10 linhas.
- Estilo Corporate Dark.

Durante um inventário sem EPCs:

    EPCs identificados: 0

Após o encerramento automático:

    Preservar a apresentação
    conforme o comportamento existente
    de finalização de passagem.

Ao iniciar uma nova passagem:

    Reiniciar os dados de sessão
    conforme a lógica atual.

Não criar novos cards.

Não criar novos botões.

Não adicionar mensagens invasivas.

Se existir um indicador de status,
ele deverá refletir corretamente
o retorno ao estado pronto.

---

## 18. PRESERVAR O POLLING WAVESHARE

Manter o intervalo estabelecido
no RF042 e preservado no RF043:

    20 ms.

Não retornar para 50 ms.

Não modificar:

- Porta COM.
- Baud rate.
- Data bits.
- Paridade.
- Stop bits.
- Device ID.
- Protocolo Modbus.
- Debounce dos sensores.
- Estratégia de leitura das entradas.

O RF044 não tem como objetivo
alterar o desempenho do polling.

---

## 19. PRESERVAR FUNCIONALIDADES EXISTENTES

Não modificar:

- Zebra FX9600.
- Comunicação LLRP.
- Biblioteca sllurp.
- Filtro EPC RF023.
- Deduplicação de EPCs.
- Configuração das antenas.
- Potência das antenas.
- Mapa de leitura RFID.
- Classificação Extra box.
- Backend Rails.
- Áudio RF033.
- Voz RF035.
- Simulador RFID RF034.
- Configurações RF036.
- Lógica de relés.
- Início manual pelo DI3.
- Reabertura pelo DI3.
- Encerramento pelo DI2.

A alteração deverá ser
restrita ao tratamento de timeout
e à limpeza correta do contexto
de passagens sem EPCs.

---

## 20. TESTES OBRIGATÓRIOS

### Teste 1 — DI1 sem EPCs

Acionar DI1.

Aguardar 20 segundos.

Não apresentar etiquetas.

Resultado:

    Inventário parado.

    Passagem encerrada.

    Sistema pronto.

### Teste 2 — Novo DI1 após timeout vazio

Executar o Teste 1.

Liberar o sensor DI1.

Acioná-lo novamente.

Resultado:

    Nova passagem iniciada.

    Timer reiniciado em 20 segundos.

### Teste 3 — DI3 sem EPCs

Acionar DI3 para início manual.

Aguardar 20 segundos.

Não apresentar etiquetas.

Resultado:

    Passagem encerrada automaticamente.

    Sistema pronto.

### Teste 4 — Novo DI3 após timeout vazio

Executar o Teste 3.

Liberar o pedal.

Pressioná-lo novamente.

Resultado:

    Nova passagem manual iniciada.

    Não reutilizar passagem anterior.

### Teste 5 — Um EPC identificado

Iniciar passagem.

Identificar um EPC válido.

Aguardar timeout.

Resultado:

    Inventário parado.

    Passagem preservada.

    Aguardando DI2 ou DI3.

### Teste 6 — Dez EPCs identificados

Iniciar passagem.

Identificar dez EPCs válidos.

Aguardar timeout.

Resultado:

    Passagem preservada.

    Contador permanece em 10.

    DI3 poderá reabrir leitura.

### Teste 7 — Apenas Extra box

Iniciar passagem.

Identificar dois EPCs válidos
classificados como Extra box.

Aguardar timeout.

Resultado:

    Passagem preservada.

    Não encerrar automaticamente.

### Teste 8 — EPCs não autorizados

Iniciar passagem.

Receber apenas EPCs
com prefixos não autorizados.

Aguardar timeout.

Resultado:

    EPCs identificados = 0.

    Passagem encerrada automaticamente.

### Teste 9 — EPC inválido

Iniciar passagem.

Receber somente EPCs inválidos.

Aguardar timeout.

Resultado:

    Passagem encerrada automaticamente.

### Teste 10 — EPC duplicado

Iniciar passagem.

Identificar um EPC válido.

Receber o mesmo EPC várias vezes.

Aguardar timeout.

Resultado:

    EPCs identificados = 1.

    Passagem preservada.

### Teste 11 — DI2 antes do timeout

Iniciar passagem.

Não identificar EPCs.

Acionar DI2 antes de 20 segundos.

Resultado:

    Passagem encerrada normalmente.

    Nenhuma segunda finalização
    deverá ocorrer pelo timeout.

### Teste 12 — DI2 e timeout concorrentes

Simular DI2 e timeout
no mesmo intervalo de processamento.

Resultado:

    Uma única finalização.

    Nenhum erro de estado.

### Teste 13 — EPC próximo ao timeout

Receber um EPC válido
próximo ao encerramento da janela.

Confirmar que o processamento
do evento não resulta
em encerramento incorreto
de passagem com EPC válido.

### Teste 14 — DI3 após timeout com EPCs

Iniciar passagem.

Identificar cinco EPCs.

Aguardar timeout.

Acionar DI3.

Resultado:

    Mesma passagem reaberta.

    Timer reiniciado em 20 segundos.

    Cinco EPCs preservados.

### Teste 15 — DI3 após timeout sem EPCs

Iniciar passagem.

Não identificar EPCs.

Aguardar timeout.

Acionar DI3 novamente.

Resultado:

    Nova passagem manual iniciada.

    Não reabrir passagem vazia anterior.

### Teste 16 — Sensor mantido acionado

Manter DI1 acionado
após o timeout vazio.

Resultado:

    Não iniciar leituras repetidas.

Liberar DI1 e acionar novamente.

Resultado:

    Nova passagem permitida.

### Teste 17 — Relés

Validar:

- Pronto.
- Inventário ativo.
- Timeout sem EPCs.
- Timeout com EPCs.
- Reabertura.
- Encerramento DI2.
- Erro.

### Teste 18 — Backend

Validar que:

- Nenhum EPC fictício é registrado.
- Não existem POSTs duplicados.
- O encerramento vazio
  não altera o contrato da API.
- O fluxo normal continua funcionando.

### Teste 19 — Polling

Confirmar:

    Intervalo configurado = 20 ms.

### Teste 20 — Regressão

Executar testes existentes de:

- RFID.
- Waveshare.
- DI1.
- DI2.
- DI3.
- Timeout.
- Relés.
- EPCs.
- Extra box.
- Backend.
- Interface Start.

Confirmar ausência de regressões.

---

## 21. CRITÉRIOS DE ACEITE

- [ ] Timeout permanece em 20 segundos.
- [ ] Contagem de EPCs válidos utilizada.
- [ ] Zero EPCs encerra automaticamente a passagem.
- [ ] Zero EPCs retorna ao estado pronto.
- [ ] Novo DI1 funciona após timeout vazio.
- [ ] Novo DI3 inicia passagem após timeout vazio.
- [ ] Não exige DI2 para encerrar passagem vazia.
- [ ] Um ou mais EPCs preservam a passagem.
- [ ] Extra box conta como EPC identificado.
- [ ] EPC inválido não conta.
- [ ] Prefixo não autorizado não conta.
- [ ] EPC duplicado não incrementa contagem.
- [ ] DI3 reabre passagem com EPCs após timeout.
- [ ] DI3 não reabre passagem vazia encerrada.
- [ ] DI2 continua encerrando normalmente.
- [ ] Pedal manual preservado.
- [ ] Debounce preservado.
- [ ] Sem reinício repetitivo com sensor mantido ativo.
- [ ] Contexto de passagem vazia limpo.
- [ ] Sem callbacks atrasados associados a nova passagem.
- [ ] Sem finalizações duplicadas.
- [ ] Relés preservados.
- [ ] Polling mantido em 20 ms.
- [ ] Backend preservado.
- [ ] Tela Start preservada.
- [ ] Nenhum novo temporizador.
- [ ] Nenhuma nova dependência.
- [ ] Testes automatizados aprovados.
- [ ] Testes de regressão aprovados.

---

## 22. PROCEDIMENTO DO CODEX

Antes de implementar:

1. Ler AGENTS.md.

2. Verificar a branch atual.

3. Executar git status.

4. Preservar alterações locais.

5. Identificar o controlador operacional RFID.

6. Identificar o tratamento atual
   do timeout de 20 segundos.

7. Identificar o gerenciamento
   do contexto de passagem.

8. Identificar o contador
   EPCs identificados do RF043.

9. Identificar o conjunto
   de EPCs únicos válidos.

10. Identificar a rotina de encerramento
    definitivo pelo DI2.

11. Identificar a lógica de DI3
    para início manual e reabertura.

12. Identificar o controle de estado
    dos relés CH1, CH2 e CH3.

13. Identificar o processamento
    assíncrono de eventos RFID.

14. Identificar a integração
    com o backend Rails.

Durante a implementação:

- Reutilizar o controlador existente.
- Adicionar decisão ao timeout atual.
- Utilizar a contagem de EPCs únicos.
- Encerrar passagens vazias corretamente.
- Preservar passagens com EPCs.
- Preservar a lógica DI3.
- Preservar a lógica DI2.
- Evitar finalizações duplicadas.
- Tratar eventos concorrentes.
- Preservar relés.
- Não modificar a interface.
- Não adicionar temporizadores.
- Não adicionar dependências.

Após implementar:

1. Executar testes automatizados.

2. Validar timeout sem EPCs.

3. Validar novo DI1.

4. Validar novo DI3.

5. Validar timeout com EPCs.

6. Validar Extra box.

7. Validar deduplicação.

8. Validar encerramento pelo DI2.

9. Validar relés.

10. Validar backend.

11. Executar testes de regressão.

12. Executar git diff.

13. Apresentar os arquivos modificados.

14. Informar testes executados.

15. Informar eventuais limitações.

Não executar git reset --hard.

Não descartar alterações locais.

Não realizar commit automaticamente.

Não realizar push automaticamente.

Não realizar merge na main.

---

## 23. RESULTADO ESPERADO

O DSV RFID System deverá recuperar
automaticamente o estado pronto
quando uma passagem terminar
sem identificar nenhuma etiqueta válida.

FLUXO SEM EPCs:

    DI1 OU DI3
        |
        v
    INICIAR INVENTÁRIO
        |
        v
    TIMER 20 SEGUNDOS
        |
        v
    EPCs IDENTIFICADOS = 0
        |
        v
    ENCERRAR PASSAGEM
        |
        v
    SISTEMA PRONTO
        |
        v
    AGUARDAR NOVO DI1 OU DI3


FLUXO COM EPCs:

    DI1 OU DI3
        |
        v
    INICIAR INVENTÁRIO
        |
        v
    EPCs IDENTIFICADOS >= 1
        |
        v
    TIMEOUT 20 SEGUNDOS
        |
        v
    PRESERVAR PASSAGEM
        |
        v
    AGUARDAR DI2 OU DI3


A nova funcionalidade deverá impedir
que passagens vazias bloqueiem
o início de novas leituras.

Passagens com etiquetas identificadas
deverão continuar permitindo
complementação pelo pedal.

IMPLEMENTAR O RF044.

TIMEOUT = 20 SEGUNDOS.

ZERO EPCs = ENCERRAMENTO AUTOMÁTICO.

UM OU MAIS EPCs = PRESERVAR PASSAGEM.

PRESERVAR DI1, DI2 E DI3.

PRESERVAR POLLING DE 20 MS.

NÃO ADICIONAR NOVOS TEMPORIZADORES.

NÃO MODIFICAR O LAYOUT.

PRESERVAR TODAS AS DEMAIS
FUNCIONALIDADES DO SISTEMA.