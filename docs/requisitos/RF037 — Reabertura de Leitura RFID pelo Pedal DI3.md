# RF037 — Reabertura de Leitura RFID pelo Pedal DI3

Projeto: DSV RFID System
Requisito: RF037
Categoria: RFID / Automação / Waveshare / Controle de Sessão
Tecnologia: Python + PySide6/QML
Hardware: Zebra FX9600 + Waveshare Modbus RTU Relay D
Sistema operacional: Windows
Prioridade: Alta

---

## 1. OBJETIVO

Implementar a possibilidade de reabrir uma leitura RFID
utilizando um pedal de acionamento conectado à entrada
digital DI3 da placa Waveshare Modbus RTU Relay D.

Atualmente, o sistema inicia uma leitura quando o
sensor de entrada DI1 é acionado.

A leitura é encerrada quando:

- O sensor de saída DI2 é acionado.
- O temporizador de 60 segundos termina.

O novo comportamento permitirá que o operador
reabra a leitura após o timeout de 60 segundos,
desde que o sensor DI2 ainda não tenha sido acionado.

Essa reabertura deverá ocorrer mediante
o acionamento do pedal conectado ao DI3.

IMPORTANTE:

A reabertura não deverá criar uma nova sessão.

Ela deverá continuar a sessão lógica existente,
preservando todos os EPCs e registros já encontrados.

O objetivo é permitir a leitura complementar
de etiquetas que não foram identificadas
durante a primeira tentativa.

---

## 2. CONTEXTO OPERACIONAL

O portal RFID é utilizado para identificar
caixas transportadas através das antenas.

Em determinadas situações, o leitor RFID
pode não identificar todas as etiquetas
durante a primeira leitura.

Isso pode ocorrer devido a:

- Posicionamento das etiquetas.
- Orientação das caixas.
- Distância entre etiqueta e antena.
- Interferências no ambiente.
- Condições de propagação do sinal RFID.

Nesses casos, o operador poderá aproximar
manualmente as etiquetas das antenas
para complementar a leitura.

Para isso, será instalado um pedal
de acionamento conectado à entrada DI3.

O pedal permitirá reabrir a leitura,
sem perder os dados já contabilizados.

---

## 3. HARDWARE UTILIZADO

Equipamentos existentes:

    Leitor RFID:
        Zebra FX9600

    Comunicação:
        LLRP / sllurp

    Módulo de entradas e relés:
        Waveshare Modbus RTU Relay D

    Comunicação:
        Modbus RTU

Entradas digitais:

    DI1 — Sensor de entrada

    DI2 — Sensor de saída

    DI3 — Pedal de reabertura da leitura

Saídas existentes:

    CH1 — Estado pronto

    CH2 — Leitura em andamento

    CH3 — Estado de erro

Não alterar o mapeamento de DI1 e DI2.

Não alterar a função dos relés existentes.

O DI3 será utilizado exclusivamente
para solicitar a reabertura da leitura.

---

## 4. COMPORTAMENTO ATUAL

O fluxo operacional existente funciona
da seguinte maneira:

### 4.1 Sistema pronto

Condições:

- RFID conectado.
- Internet disponível.
- Comandos Waveshare funcionando.
- Sistema/API disponível.
- Modo automático habilitado.

Estado:

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

### 4.2 Sensor DI1 acionado

Quando o sensor de entrada detecta
a passagem de caixas:

    Iniciar inventário RFID.

    Iniciar temporizador de 60 segundos.

    CH1 = OFF
    CH2 = ON
    CH3 = OFF

### 4.3 Sensor DI2 acionado

Quando as caixas passam pelo
sensor de saída:

    Encerrar inventário RFID.

    Encerrar a passagem.

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

### 4.4 Timeout de 60 segundos

Caso o sensor DI2 não seja acionado
antes do término do temporizador:

    Encerrar inventário RFID.

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

O RF037 deverá acrescentar a possibilidade
de complementar essa leitura após o timeout.

---

## 5. NOVA REGRA — DIFERENCIAR LEITURA E PASSAGEM

Implementar uma distinção entre:

1. Inventário RFID ativo.
2. Passagem aguardando complementação.
3. Passagem encerrada definitivamente.

Esses estados não deverão ser confundidos.

### 5.1 Inventário ativo

O Zebra FX9600 está executando
o inventário de etiquetas.

O temporizador está ativo.

O sistema está recebendo EPCs.

### 5.2 Aguardando complementação

O inventário foi encerrado
pelo timeout de 60 segundos.

Entretanto, a passagem ainda
não foi encerrada pelo DI2.

Nesse estado:

- O inventário permanece parado.
- O temporizador permanece parado.
- Os EPCs já encontrados são preservados.
- A tabela permanece preenchida.
- Os contadores permanecem preservados.
- O pedal DI3 pode solicitar uma nova leitura.

### 5.3 Passagem encerrada definitivamente

A passagem foi encerrada
pelo acionamento do DI2.

Nesse estado:

- O inventário está parado.
- A passagem está encerrada.
- O pedal DI3 não pode reabrir a leitura.
- Os registros permanecem disponíveis
  conforme o comportamento atual do sistema.

Uma nova passagem deverá seguir
o fluxo normal de DI1.

---

## 6. NOVO FLUXO OPERACIONAL

O novo fluxo deverá funcionar assim:

    SISTEMA PRONTO
           |
           v
    DI1 ACIONADO
           |
           v
    INICIAR LEITURA RFID
           |
           v
    TEMPORIZADOR 60 SEGUNDOS
           |
           |
           +------ DI2 ACIONADO
           |              |
           |              v
           |       ENCERRAMENTO DEFINITIVO
           |              |
           |              v
           |       DI3 BLOQUEADO
           |
           |
           +------ TIMEOUT
                          |
                          v
                  PARAR INVENTÁRIO
                          |
                          v
                AGUARDAR COMPLEMENTAÇÃO
                          |
                          v
                    DI3 ACIONADO
                          |
                          v
                  REABRIR INVENTÁRIO
                          |
                          v
                  PRESERVAR EPCs
                          |
                          v
                  NOVOS 60 SEGUNDOS
                          |
                          +---- DI2
                          |       |
                          |       v
                          |  ENCERRAMENTO
                          |  DEFINITIVO
                          |
                          +---- TIMEOUT
                                  |
                                  v
                           AGUARDAR DI3
                           OU DI2

A qualquer momento, se DI2 for acionado,
a passagem deverá ser encerrada
definitivamente.

---

## 7. EXEMPLO PRÁTICO

Considere uma passagem contendo 10 caixas.

### Etapa 1 — Primeira leitura

O operador passa pelo sensor DI1.

O sistema inicia a leitura.

    Temporizador: 60 segundos

    Caixas esperadas: 10

Durante a leitura, o Zebra identifica:

    EPC 001
    EPC 002
    EPC 003
    EPC 004
    EPC 005
    EPC 006
    EPC 007

Resultado:

    EPCs encontrados: 7

Três etiquetas não foram identificadas.

### Etapa 2 — Timeout

O operador ainda não passou pelo DI2.

O temporizador chega a zero.

O sistema deverá:

    Parar o inventário RFID.

    Preservar os 7 EPCs encontrados.

    Manter os registros na tabela.

    Aguardar eventual acionamento do DI3.

Não limpar a sessão.

Não reiniciar os contadores.

### Etapa 3 — Pedal DI3

O operador pressiona o pedal conectado
à entrada digital DI3.

O sistema deverá:

    Reabrir o inventário RFID.

    Manter os 7 EPCs encontrados.

    Iniciar nova janela de 60 segundos.

    Ativar CH2.

    Desativar CH1.

O operador aproxima as etiquetas
restantes das antenas.

### Etapa 4 — Leitura complementar

O leitor identifica novamente:

    EPC 001
    EPC 002
    EPC 003

Esses EPCs já foram encontrados.

Resultado:

    Não adicionar novas linhas.

    Não aumentar o contador.

    Não consultar novamente o backend
    para esses EPCs.

    Não reproduzir novos bips
    para esses EPCs.

Em seguida, o leitor identifica:

    EPC 008
    EPC 009
    EPC 010

Esses EPCs ainda não foram encontrados.

Resultado:

    EPCs encontrados: 10

A tabela deverá apresentar os registros
sem duplicação.

### Etapa 5 — Sensor DI2

O operador conclui a movimentação
e aciona o sensor DI2.

O sistema deverá:

    Parar o inventário.

    Encerrar definitivamente a passagem.

    Bloquear a reabertura por DI3.

Resultado final:

    EPCs encontrados: 10

Uma tentativa posterior de acionar
o pedal não deverá reabrir essa passagem.

---

## 8. REGRAS PARA ACIONAMENTO DO DI3

O pedal DI3 somente poderá reabrir
uma leitura se TODAS as condições
abaixo forem verdadeiras:

1. O modo automático está habilitado.

2. O sensor DI1 iniciou uma passagem válida.

3. O inventário anterior terminou por timeout.

4. O sensor DI2 ainda não encerrou a passagem.

5. A passagem continua disponível
   para complementação.

6. O sistema está operacional e apto
   a executar inventário RFID.

7. Não existe erro operacional impeditivo.

Caso qualquer condição não seja atendida,
o acionamento do DI3 deverá ser ignorado.

O pedal NÃO poderá:

- Iniciar uma passagem sem DI1.
- Criar uma nova sessão.
- Reabrir uma passagem encerrada pelo DI2.
- Ignorar condições de erro.
- Ignorar o Stop manual do operador.
- Reiniciar automaticamente uma leitura
  que já está em andamento.

---

## 9. COMPORTAMENTO DO DI3 DURANTE A LEITURA

Se o pedal DI3 for acionado enquanto
o inventário RFID já estiver ativo:

    Não reiniciar o inventário.

    Não zerar o temporizador.

    Não modificar a contagem.

    Não criar nova sessão.

O acionamento deverá ser ignorado.

O pedal somente terá efeito
quando a passagem estiver no estado:

    AGUARDANDO COMPLEMENTAÇÃO

Esse estado será atingido após
o timeout de 60 segundos.

---

## 10. TEMPORIZADOR NA REABERTURA

Ao reabrir a leitura pelo DI3:

    Iniciar uma nova janela
    de leitura de 60 segundos.

O temporizador deverá começar
novamente em 60 segundos.

IMPORTANTE:

Reiniciar o temporizador não significa
reiniciar a sessão.

A sessão deverá preservar
todos os dados anteriores.

Exemplo:

    Primeira leitura:
        60 segundos
        7 EPCs encontrados

    Pedal DI3:
        +60 segundos
        Total preservado: 7

    Segunda leitura:
        +3 EPCs encontrados
        Total: 10

Caso a segunda janela de leitura
também termine por timeout:

    Parar o inventário.

    Preservar os 10 EPCs.

    Retornar ao estado
    AGUARDANDO COMPLEMENTAÇÃO.

Se DI2 ainda não foi acionado,
um novo acionamento válido de DI3
poderá reabrir novamente a leitura.

Não estabelecer um limite arbitrário
de acionamentos do pedal neste requisito.

Entretanto, cada acionamento válido
deverá respeitar as regras de segurança
e os estados operacionais.

---

## 11. ENCERRAMENTO DEFINITIVO PELO DI2

O DI2 terá prioridade sobre o DI3.

Quando o DI2 for acionado:

    Encerrar o inventário, se estiver ativo.

    Cancelar o temporizador, se estiver ativo.

    Encerrar definitivamente a passagem.

    Invalidar novas solicitações de DI3
    para essa passagem.

Isso deverá ocorrer inclusive
se o DI2 for acionado:

- Durante a primeira leitura.
- Durante uma leitura reaberta pelo DI3.
- Enquanto a passagem aguarda complementação.
- No mesmo ciclo de leitura de entradas
  em que ocorrer um acionamento do DI3.

Caso DI2 e DI3 sejam identificados
no mesmo ciclo de processamento:

    DI2 tem prioridade.

    Não reabrir a leitura.

Depois de um encerramento por DI2,
o DI3 não poderá reutilizar
os dados dessa passagem.

Uma nova passagem deverá ser iniciada
pelo DI1 conforme a lógica existente.

---

## 12. PRESERVAÇÃO DOS EPCs

Este é um requisito crítico.

Durante a reabertura da leitura:

NÃO apagar:

- EPCs já encontrados.
- Registros da tabela.
- Status dos registros.
- Cliente.
- Nota Fiscal.
- Volume.
- Pedido.
- Doca.
- Dealer.
- Contadores da sessão.
- Classificações Extra box.

O sistema deverá manter o mesmo
conjunto de registros da passagem.

A nova leitura deverá adicionar
somente registros que ainda não
foram identificados na mesma passagem.

O mecanismo de identificação de
duplicidades deverá continuar ativo
entre a primeira leitura e todas
as reaberturas.

---

## 13. CONTROLE DE DUPLICIDADE

O sistema deverá utilizar
um conjunto de EPCs já processados
durante a passagem.

Exemplo:

    EPCs já identificados:

        445543001
        445543002
        445543003

Ao reabrir a leitura:

    EPC recebido: 445543001

Resultado:

    Ignorar duplicidade.

    Não adicionar linha.

    Não incrementar contador.

    Não executar nova consulta GET.

    Não executar novo registro POST
    para o mesmo EPC já registrado.

    Não reproduzir novo bip.

Quando receber:

    EPC recebido: 445543004

Resultado:

    Processar normalmente.

    Consultar o backend, quando aplicável.

    Atualizar a tabela.

    Atualizar o contador.

    Reproduzir o bip RF033,
    se classificado como EPC encontrado.

IMPORTANTE:

O leitor físico poderá transmitir
novamente EPCs já identificados.

A prevenção de duplicidade deverá
ser realizada no software, utilizando
o mecanismo existente de deduplicação.

Não implementar pré-filtros adicionais
no Zebra FX9600.

Preservar a arquitetura de filtragem
definida no RF023.

---

## 14. INTEGRAÇÃO COM O BACKEND RFID

A passagem reaberta deverá permanecer
associada ao mesmo contexto lógico
da passagem original.

Preservar a integração existente com:

    GET /api/v1/rfid_records/:epc

    POST /api/v1/rfid_reads

Regras:

- Não repetir GET desnecessariamente
  para EPCs já processados.

- Não duplicar registros de leitura
  já enviados ao backend.

- Novos EPCs deverão seguir
  o fluxo normal de consulta e registro.

- Não criar uma nova identidade de
  passagem a cada acionamento do pedal.

- Preservar a rastreabilidade
  das leituras complementares.

ATENÇÃO:

Antes da implementação, o Codex deverá
verificar como o sistema atualmente
finaliza e registra uma passagem
quando ocorre timeout.

Como o RF037 permite continuar
a mesma passagem após o timeout,
é necessário garantir que a reabertura
não produza inconsistências no backend.

O Codex deverá:

1. Identificar quando o POST é executado.
2. Identificar se o timeout marca
   a passagem como finalizada.
3. Verificar o controle atual
   de registros já enviados.
4. Preservar a rastreabilidade.
5. Evitar duplicações.
6. Garantir que novos EPCs obtidos
   após a reabertura sejam registrados.

Não inventar novos endpoints.

Não modificar silenciosamente
o contrato da API Rails.

Se o modelo atual do backend
não permitir representar corretamente
uma passagem retomada, documentar
a limitação e a alteração necessária
antes de modificar o contrato da API.

O encerramento do inventário por timeout
não deverá destruir o contexto necessário
para uma eventual complementação.

---

## 15. CONTROLE DOS RELÉS

Preservar os relés existentes.

### Estado pronto

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

### Leitura RFID ativa

Incluindo leituras reabertas pelo DI3:

    CH1 = OFF
    CH2 = ON
    CH3 = OFF

### Timeout aguardando complementação

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

### Encerramento pelo DI2

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

### Estado de erro

Preservar o comportamento existente:

    CH1 = OFF
    CH2 = OFF
    CH3 = ON

IMPORTANTE:

O DI3 não deverá modificar
diretamente os relés.

O pedal deverá solicitar a transição
para o estado de leitura ativa.

O controlador operacional existente
deverá continuar responsável
pelo acionamento dos relés.

Não permitir que o DI3
desative ou ignore um estado de erro.

---

## 16. PRIORIDADE DAS CONDIÇÕES DE SEGURANÇA

A nova funcionalidade deverá respeitar
todas as regras de segurança existentes.

Prioridades:

1. Erros e condições de segurança.
2. Stop manual do operador.
3. Encerramento pelo DI2.
4. Timeout do inventário.
5. Solicitação de reabertura pelo DI3.
6. Início normal pelo DI1.

Preservar especialmente
a regra existente:

Quando os dois sensores
DI1 e DI2 estiverem interrompidos,
o sistema deverá entrar
no estado de erro definido
na lógica atual.

O pedal DI3 não poderá
ignorar essa condição.

Não modificar os tratamentos
de falha de comunicação
com a Waveshare ou o Zebra FX9600.

---

## 17. DETECÇÃO DO PEDAL DI3

A entrada DI3 será utilizada
para detectar o acionamento
de um pedal físico.

O Codex deverá verificar
a implementação atual
de leitura das entradas digitais.

IMPORTANTE:

Os sensores DI1 e DI2 possuem
uma interpretação elétrica já definida.

O pedal DI3 poderá possuir
um comportamento elétrico diferente,
dependendo do contato utilizado.

Não presumir que DI3 acionado
significa obrigatoriamente
valor lógico 0 ou 1.

Implementar uma interpretação
configurável ou devidamente isolada
do estado de acionamento do pedal,
conforme o sinal físico validado
nos testes da Waveshare.

O objetivo é identificar
o evento de pressionamento do pedal.

Requisitos:

- Detectar transição de acionamento.
- Executar apenas uma solicitação
  por pressionamento válido.
- Não repetir eventos enquanto
  o pedal permanecer pressionado.
- Exigir liberação antes
  de aceitar novo acionamento.
- Aplicar tratamento de debounce
  adequado a um contato mecânico.

Não utilizar repetidamente
o nível ativo do DI3
como se fossem vários pressionamentos.

Se o pedal já estiver pressionado
antes do timeout, não reabrir
automaticamente a leitura.

Exigir novo pressionamento válido
após entrar no estado
AGUARDANDO COMPLEMENTAÇÃO.

---

## 18. GERENCIAMENTO DE ESTADOS

Avaliar o controlador de estados
já existente no projeto.

Adicionar os estados ou indicadores
mínimos necessários para representar:

    PRONTO

    LEITURA_ATIVA

    AGUARDANDO_COMPLEMENTACAO

    PASSAGEM_ENCERRADA

    ERRO

Não criar um segundo controlador
operacional independente.

A nova funcionalidade deverá
ser integrada ao controlador existente.

Separar conceitualmente:

    Identidade da passagem

    Inventário RFID ativo

    Temporizador da leitura

    Estado de encerramento

A mesma passagem poderá conter
múltiplas janelas de inventário.

Exemplo:

    Passagem A
        |
        +-- Leitura inicial
        |
        +-- Timeout
        |
        +-- Reabertura DI3
        |
        +-- Timeout
        |
        +-- Reabertura DI3
        |
        +-- Encerramento DI2

Todas as leituras acima pertencem
à mesma passagem A.

Não gerar uma nova sessão lógica
para cada reabertura.

---

## 19. COMPORTAMENTO DA INTERFACE

Preservar o layout atual
da tela Start.

Não criar novas telas.

Não modificar a tabela existente.

A tabela deverá continuar mostrando
exatamente as 7 colunas:

1. Status
2. Cliente
3. Nota Fiscal
4. Volume
5. Pedido
6. Doca
7. Dealer

Durante o timeout:

- Preservar os registros.
- Preservar os contadores.
- Manter os dados visíveis.

Durante a reabertura:

- Atualizar os novos EPCs normalmente.
- Não duplicar registros existentes.
- Manter os dados anteriores visíveis.

O Codex poderá acrescentar,
se necessário, um status discreto:

    Aguardando complementação

Ou:

    Leitura reaberta

Entretanto, não deverá
reorganizar o layout da tela Start.

Não criar novos cards.

Não modificar o layout aprovado
em requisitos anteriores.

---

## 20. PRESERVAR O ÁUDIO RF033

O bip suave deverá continuar funcionando
para novos EPCs encontrados.

Exemplo:

    Primeira leitura:

        7 EPCs novos
        7 solicitações de bip

    Reabertura:

        3 EPCs novos
        3 solicitações de bip

        7 EPCs repetidos
        0 solicitações adicionais

Preservar:

    Frequência: 880 Hz

    Duração: 80 ms

    Intervalo mínimo: 300 ms

    Fila de reprodução existente

Não criar outro serviço de bip.

Não modificar a lógica do RF033.

Não reproduzir bip para EPC duplicado.

Não reproduzir bip para Extra box.

Não integrar automaticamente
a voz RF035 neste requisito.

---

## 21. INTERRUPÇÕES E CONCORRÊNCIA

O controlador deverá impedir
transições duplicadas ou conflitantes.

Exemplos:

### Caso A — DI3 pressionado repetidamente

Se uma solicitação de reabertura
já estiver em andamento:

    Ignorar solicitações adicionais.

### Caso B — DI2 acionado durante a reabertura

    Encerrar a passagem.

    Cancelar a reabertura.

    Não reiniciar o inventário.

### Caso C — Stop manual

    Encerrar o modo automático
    conforme o comportamento existente.

    Cancelar reaberturas pendentes.

    Não aceitar DI3 enquanto
    o modo automático estiver parado.

### Caso D — Falha no Zebra

    Não considerar a reabertura
    como iniciada com sucesso.

    Preservar os dados da passagem.

    Aplicar o tratamento de erro existente.

### Caso E — Falha na Waveshare

    Não assumir um acionamento válido.

    Preservar as regras de segurança.

### Caso F — DI1 novamente durante
           uma passagem aguardando complementação

    Não criar silenciosamente
    uma segunda passagem sobre a atual.

    Preservar a integridade da passagem
    ainda não encerrada por DI2.

    Aplicar a proteção de estado
    e o tratamento operacional existente.

---

## 22. TESTES OBRIGATÓRIOS

### Teste 1 — Fluxo normal

Acionar DI1.

Iniciar inventário.

Acionar DI2 antes de 60 segundos.

Resultado:

    Leitura encerrada.

    DI3 bloqueado.

    Nenhuma reabertura permitida.

### Teste 2 — Timeout

Acionar DI1.

Aguardar 60 segundos.

Não acionar DI2.

Resultado:

    Inventário parado.

    Dados preservados.

    Sistema aguardando complementação.

### Teste 3 — Reabertura pelo DI3

Após o timeout:

    Pressionar DI3.

Resultado:

    Inventário reiniciado.

    Temporizador em 60 segundos.

    Mesma passagem preservada.

    CH2 ligado.

    CH1 desligado.

### Teste 4 — Preservação de registros

Primeira leitura:

    7 EPCs encontrados.

Acionar DI3 após timeout.

Resultado:

    Contador permanece em 7.

    Tabela permanece com os registros.

### Teste 5 — EPCs duplicados

Na reabertura:

    Ler novamente os 7 EPCs anteriores.

Resultado:

    Contador permanece em 7.

    Nenhuma linha duplicada.

    Nenhum novo bip.

    Nenhuma consulta ou registro
    duplicado para os mesmos EPCs.

### Teste 6 — Novos EPCs

Na reabertura:

    Encontrar 3 novos EPCs.

Resultado:

    Contador passa de 7 para 10.

    Novas linhas são adicionadas.

    Registros anteriores preservados.

### Teste 7 — DI3 durante leitura ativa

Com temporizador ativo:

    Pressionar DI3.

Resultado:

    Nenhum novo inventário iniciado.

    Temporizador não reiniciado.

    Dados preservados.

### Teste 8 — DI3 sem DI1

Com sistema pronto,
sem passagem iniciada:

    Pressionar DI3.

Resultado:

    Nenhuma leitura iniciada.

### Teste 9 — DI3 após DI2

Iniciar passagem por DI1.

Encerrar por DI2.

Pressionar DI3.

Resultado:

    Nenhuma reabertura.

### Teste 10 — Múltiplas reaberturas

DI1 inicia a leitura.

Primeiro timeout.

DI3 reabre.

Segundo timeout.

DI3 reabre novamente.

Resultado:

    Mesma passagem.

    Dados acumulados.

    Sem duplicação.

### Teste 11 — DI2 durante reabertura

Reabrir pelo DI3.

Acionar DI2 durante a leitura.

Resultado:

    Inventário parado.

    Passagem encerrada definitivamente.

    Novos acionamentos de DI3 ignorados.

### Teste 12 — Pedal mantido pressionado

Pressionar DI3 e manter pressionado.

Resultado:

    Uma única solicitação.

    Sem reinicializações repetidas.

### Teste 13 — Pedal pressionado antes do timeout

Pressionar e manter DI3
durante a leitura inicial.

Aguardar timeout.

Resultado:

    Não reabrir automaticamente.

    Exigir liberação e novo acionamento.

### Teste 14 — Segurança

Simular condição de erro existente
envolvendo DI1 e DI2.

Pressionar DI3.

Resultado:

    Erro preservado.

    CH3 permanece conforme
    a lógica de segurança.

    DI3 não inicia inventário.

### Teste 15 — Backend

Executar passagem com reabertura.

Confirmar:

- Nenhum EPC duplicado.
- Novos EPCs registrados corretamente.
- GET sem repetição desnecessária.
- POST sem duplicação de registros.
- Consistência do histórico da passagem.

### Teste 16 — Áudio

Executar reabertura.

Confirmar:

- Bip somente para EPCs novos.
- Nenhum bip adicional
  para EPCs duplicados.
- Nenhuma alteração no RF035.

### Teste 17 — Stop manual

Iniciar uma passagem.

Aguardar timeout.

Clicar em Stop.

Pressionar DI3.

Resultado:

    Não reabrir inventário.

### Teste 18 — Regressão operacional

Executar testes existentes de:

- RFID.
- Waveshare.
- DI1.
- DI2.
- CH1.
- CH2.
- CH3.
- Timeout de 60 segundos.
- GET e POST.
- Filtro EPC.
- Deduplicação.
- Áudio RF033.

Confirmar ausência de regressões.

---

## 23. CRITÉRIOS DE ACEITE

- [ ] DI3 integrado ao controlador existente.
- [ ] DI3 identificado como pedal de reabertura.
- [ ] DI1 continua iniciando a passagem.
- [ ] Timeout continua encerrando o inventário.
- [ ] Timeout preserva a possibilidade de complementação.
- [ ] DI3 reabre somente após timeout.
- [ ] DI3 não inicia leitura sem passagem válida.
- [ ] DI3 não reinicia inventário já ativo.
- [ ] Reabertura preserva a mesma passagem.
- [ ] Nova janela de 60 segundos implementada.
- [ ] EPCs anteriores preservados.
- [ ] Dados da tabela preservados.
- [ ] Contadores preservados.
- [ ] EPCs repetidos ignorados.
- [ ] Novos EPCs adicionados normalmente.
- [ ] Sem novos GET para EPCs já processados.
- [ ] Sem registros POST duplicados.
- [ ] DI2 encerra definitivamente a passagem.
- [ ] DI3 bloqueado após DI2.
- [ ] DI2 tem prioridade sobre DI3.
- [ ] Reaberturas sucessivas após timeout permitidas.
- [ ] Debounce do pedal implementado.
- [ ] Um evento por pressionamento.
- [ ] Relés CH1, CH2 e CH3 preservados.
- [ ] Condições de erro preservadas.
- [ ] Stop manual respeitado.
- [ ] Bip RF033 preservado.
- [ ] Voz RF035 não modificada.
- [ ] Layout da tela Start preservado.
- [ ] Integração Rails validada.
- [ ] Testes de regressão aprovados.

---

## 24. PROCEDIMENTO DO CODEX

Antes de implementar:

1. Ler AGENTS.md.

2. Verificar a branch atual.

3. Executar git status.

4. Preservar alterações locais.

5. Identificar o serviço de comunicação Waveshare.

6. Identificar o processamento das entradas DI1 e DI2.

7. Identificar o controlador operacional
   de estados RFID.

8. Identificar a implementação
   do temporizador de 60 segundos.

9. Identificar o gerenciamento
   da sessão de leitura.

10. Identificar onde os EPCs
    são armazenados e deduplicados.

11. Identificar o fluxo GET e POST
    utilizado durante a passagem.

12. Identificar o tratamento
    de encerramento por timeout.

13. Identificar o tratamento
    de encerramento por DI2.

14. Identificar o serviço RF033.

Antes de realizar alterações,
verificar especialmente se o timeout
atualmente limpa ou finaliza
o contexto da passagem.

Essa implementação deverá ser adaptada
para permitir a complementação,
sem introduzir inconsistências.

Durante a implementação:

- Reutilizar o controlador existente.
- Evitar duplicação de lógica.
- Integrar DI3 à leitura Waveshare existente.
- Implementar detecção por borda do pedal.
- Preservar os sensores atuais.
- Preservar os relés existentes.
- Preservar os registros anteriores.
- Preservar a deduplicação por passagem.
- Manter o inventário Zebra via sllurp.
- Não configurar pré-filtros no leitor.
- Não modificar a interface desnecessariamente.
- Manter a operação responsiva.
- Não adicionar dependências desnecessárias.

Após implementar:

1. Executar testes automatizados.

2. Validar o fluxo DI1 → timeout → DI3.

3. Validar o fluxo DI1 → DI2.

4. Validar bloqueio de DI3 após DI2.

5. Validar reaberturas sucessivas.

6. Validar preservação dos EPCs.

7. Validar ausência de duplicidades.

8. Validar GET e POST.

9. Validar estados dos relés.

10. Validar comportamento de erro.

11. Executar testes de regressão.

12. Executar git diff.

13. Apresentar arquivos modificados.

14. Informar testes executados e resultados.

15. Informar eventuais limitações
    identificadas na integração com o backend.

Não executar git reset --hard.

Não descartar alterações locais.

Não realizar commit automaticamente.

Não realizar push automaticamente.

Não realizar merge na main.

---

## 25. RESULTADO ESPERADO

O sistema deverá permitir que o operador
complemente uma passagem RFID
quando o temporizador atingir zero
sem que o sensor DI2 tenha sido acionado.

Fluxo esperado:

    DI1
     |
     v
    Leitura RFID
     |
     v
    7 EPCs encontrados
     |
     v
    Timeout
     |
     v
    Inventário parado
     |
     v
    DI3 — Pedal
     |
     v
    Inventário reaberto
     |
     v
    3 novos EPCs encontrados
     |
     v
    Total: 10 EPCs
     |
     v
    DI2
     |
     v
    Passagem encerrada definitivamente

Os dados da passagem deverão
permanecer preservados
durante todas as reaberturas.

Os EPCs já encontrados
não poderão ser contabilizados novamente.

O DI2 deverá impedir qualquer
reabertura posterior daquela passagem.

IMPLEMENTAR O RF037.

REABERTURA SOMENTE APÓS TIMEOUT.

DI3 NÃO CRIA NOVA PASSAGEM.

PRESERVAR EPCs E CONTADORES.

NÃO DUPLICAR LEITURAS.

DI2 ENCERRA DEFINITIVAMENTE.

PRESERVAR AS REGRAS DE SEGURANÇA
E O FUNCIONAMENTO ATUAL DO RFID.