# RF041 — Diagnóstico e Otimização da Leitura dos Sensores Waveshare

Projeto: DSV RFID System
Requisito: RF041
Requisitos relacionados: RF010, RF012, RF037, RF040
Categoria: Diagnóstico / Performance / Waveshare / Sensores
Tecnologia: Python + PySide6/QML
Hardware: Waveshare Modbus RTU Relay D
Sistema operacional: Windows
Prioridade: Alta
Tipo de alteração: Diagnóstico e otimização de comunicação

---

## 1. OBJETIVO

Analisar e otimizar o processo de leitura
das entradas digitais da placa
Waveshare Modbus RTU Relay D.

Atualmente, o sistema utiliza cinco
entradas digitais:

    DI1 — Primeiro sensor de entrada
    DI2 — Segundo sensor de saída
    DI3 — Pedal de reabertura
    DI4 — Segundo sensor de entrada
    DI5 — Primeiro sensor de saída

Foi identificado durante testes físicos
que os sensores detectam a passagem
de objetos, porém alguns acionamentos
rápidos não são reconhecidos pelo software.

O objetivo deste requisito é:

1. Identificar o intervalo real de polling.
2. Analisar o desempenho da comunicação Modbus.
3. Verificar a existência de pulsos perdidos.
4. Analisar a implementação de debounce.
5. Identificar possíveis bloqueios na leitura.
6. Medir os tempos de resposta.
7. Avaliar melhorias de desempenho.
8. Implementar otimizações seguras.
9. Preservar a lógica operacional existente.

IMPORTANTE:

NÃO ALTERAR AS REGRAS DE ACIONAMENTO
DOS SENSORES DEFINIDAS NO RF040.

NÃO ALTERAR O FUNCIONAMENTO DOS RELÉS.

NÃO MODIFICAR O FLUXO OPERACIONAL RFID.

---

## 2. CONTEXTO DO PROBLEMA

Durante testes realizados com os sensores
fotoelétricos, foi observado o seguinte:

Quando um objeto passa lentamente:

    O sensor detecta a passagem.

    A placa Waveshare recebe o sinal.

    O software reconhece o evento.

Quando um objeto passa rapidamente:

    O sensor detecta a passagem.

    O indicador físico do sensor
    acende e apaga rapidamente.

    Entretanto, em algumas situações,
    o software não reconhece o evento.

Esse comportamento pode indicar
que o pulso digital é mais curto
que o intervalo efetivo de observação
utilizado pelo software.

Entretanto, essa hipótese precisa
ser confirmada por medições.

Outras possibilidades incluem:

- Polling muito lento.
- Debounce excessivo.
- Timeout de comunicação.
- Atrasos na comunicação serial.
- Bloqueio de threads.
- Retries Modbus.
- Leitura sequencial desnecessária.
- Processamento excessivo entre consultas.
- Interferência elétrica.
- Instabilidade da alimentação.
- Comprimento ou qualidade dos cabos.
- Filtragem interna das entradas digitais.

O Codex deverá investigar essas
possibilidades antes de aplicar alterações.

---

## 3. HARDWARE UTILIZADO

Placa:

    Waveshare Industrial Modbus RTU 8-Channel Relay Module (D), RS9625

Características do equipamento utilizado:

    8 saídas de relé:
        CH1 a CH8

    8 entradas digitais disponíveis:
        DI1 a DI8
    5 entradas utilizadas pelo projeto:
        DI1 a DI5

Segundo as especificações fornecidas, a placa possui debounce interno nas
entradas. Sua duração e configurabilidade ainda precisam ser confirmadas.
Consultar a referência em ../WAVESHARE/WAVESHARE_MODBUS_RTU_RELAY_D.md.

    Comunicação:
        Modbus RTU

    Interfaces:
        RS-485 / RS-232,
        conforme a conexão utilizada.

O sistema utiliza comunicação serial
com a placa através do Windows.

O Codex deverá identificar:

- Porta COM configurada.
- Baud rate atual.
- Data bits.
- Paridade.
- Stop bits.
- Device ID.
- Timeout serial.
- Intervalo de polling.
- Quantidade de consultas Modbus.
- Estratégia de leitura das entradas.
- Biblioteca Python utilizada.

Não modificar esses parâmetros
antes de identificar seus valores atuais.

---

## 4. ANÁLISE DO POLLING

Identificar onde o software realiza
a consulta periódica das entradas
digitais da Waveshare.

Verificar:

1. Qual função executa a leitura.

2. Qual intervalo está configurado
   entre as consultas.

3. Se o intervalo é fixo ou variável.

4. Se todas as entradas digitais
   são consultadas juntas.

5. Se existe uma consulta individual
   para cada entrada.

6. Se existem operações adicionais
   entre as leituras.

7. Se o polling utiliza uma thread
   independente.

8. Se a leitura pode ser bloqueada
   por operações da interface.

9. Se existem outras operações Modbus
   concorrendo pela mesma porta serial.

10. Se o polling continua funcionando
    durante as leituras RFID.

IMPORTANTE:

Durante testes anteriores,
foi discutido um intervalo de 50 ms.

Entretanto, o Codex deverá verificar
o intervalo REAL implementado no código.

Não assumir que o sistema atualmente
utiliza exatamente 50 ms.

---

## 5. MEDIÇÃO DO INTERVALO REAL

Adicionar instrumentação temporária
ou diagnóstica para medir o intervalo
efetivo entre consultas.

Utilizar um relógio monotônico,
como:

    time.perf_counter()

Registrar:

    Timestamp da consulta.

    Tempo de início.

    Tempo de término.

    Duração da operação Modbus.

    Intervalo entre consultas.

    Intervalo entre respostas.

    Sucesso ou falha.

    Quantidade de retries.

Exemplo de log:

    [WAVESHARE]
    Poll solicitado: 20 ms
    Intervalo real: 24.5 ms
    Duração Modbus: 7.2 ms
    Resultado: OK

Esses valores são apenas ilustrativos.

O software deverá registrar
as medições reais do equipamento.

Não utilizar os valores do exemplo
como referência fixa de desempenho.

---

## 6. ANÁLISE DE DESEMPENHO

Medir os seguintes indicadores:

### 6.1 Tempo médio de polling

Calcular a média dos intervalos
efetivos entre consultas.

### 6.2 Tempo mínimo

Identificar o menor intervalo observado.

### 6.3 Tempo máximo

Identificar o maior intervalo observado.

### 6.4 Percentil 95

Calcular o P95 dos intervalos
efetivos de polling.

### 6.5 Tempo de resposta Modbus

Medir a duração das consultas
realizadas à Waveshare.

### 6.6 Erros de comunicação

Contabilizar:

- Timeouts.
- Respostas inválidas.
- Falhas de leitura.
- Retries.
- Desconexões.

### 6.7 Atraso do processamento

Medir o intervalo entre:

    Recebimento da resposta Modbus

e:

    Entrega do novo estado
    ao controlador operacional.

IMPORTANTE:

Não confundir o tempo de processamento
do software com a latência física
do sensor até a placa.

A latência física completa somente
poderá ser determinada se houver
uma referência externa de medição
ou instrumentação adequada.

---

## 7. ANÁLISE DAS CONSULTAS MODBUS

Verificar como as cinco entradas
digitais são consultadas.

Preferir, quando suportado
pela placa e pela implementação,
uma única operação Modbus
para obter todas as entradas.

Exemplo conceitual:

    Ler DI1, DI2, DI3, DI4 e DI5
    em uma única consulta.

Evitar, quando desnecessário:

    Consultar DI1.
    Consultar DI2.
    Consultar DI3.
    Consultar DI4.
    Consultar DI5.

Individualmente em cada ciclo.

O Codex deverá confirmar
no protocolo da placa
se existe suporte à leitura
conjunta das entradas.

Não inventar registradores Modbus.

Não modificar endereços
sem consultar o mapeamento
utilizado no projeto.

Não alterar a interpretação
dos bits das entradas digitais.

---

## 8. ANÁLISE DE PULSOS PERDIDOS

Investigar se pulsos curtos
podem ocorrer completamente
entre duas consultas Modbus.

Exemplo:

    Consulta 1:
        Sensor normal.

    Pulso:
        Sensor interrompido.
        Sensor retorna ao normal.

    Consulta 2:
        Sensor normal.

Resultado:

    O software não observou
    a mudança de estado.

Esse comportamento pode ocorrer
mesmo com comunicação Modbus
funcionando corretamente.

O Codex deverá verificar:

- Se a placa disponibiliza
  algum recurso de captura
  ou retenção de eventos.

- Se existe leitura de estado
  latched, contador ou equivalente.

- Se o protocolo utilizado
  permite detectar eventos
  mais curtos que o polling.

Não presumir que esses recursos
existem no hardware.

Caso a placa ofereça apenas
o estado instantâneo das entradas,
registrar essa limitação.

IMPORTANTE:

Reduzir o intervalo de polling
pode diminuir a probabilidade
de perda de eventos.

Entretanto, não garante a captura
de qualquer pulso arbitrariamente curto.

---

## 9. ANÁLISE DO DEBOUNCE

Identificar se existe debounce
implementado na leitura
das entradas digitais.

Verificar:

- Tempo configurado.
- Tipo de filtro aplicado.
- Quantidade de amostras exigidas.
- Tratamento de transições.
- Diferença entre acionamento
  e desacionamento.

Analisar se o debounce atual
pode estar descartando
pulsos rápidos legítimos.

IMPORTANTE:

Não remover indiscriminadamente
o debounce existente.

O debounce também pode proteger
contra ruídos elétricos
e acionamentos falsos.

O Codex deverá avaliar
se existem tratamentos distintos
para:

    Sensores fotoelétricos.

    Pedal mecânico DI3.

O pedal mecânico pode precisar
de um debounce diferente
dos sensores fotoelétricos.

Preservar a regra de um evento
por pressionamento do DI3.

---

## 10. COMPARAÇÃO DE INTERVALOS

Após identificar a implementação atual,
avaliar diferentes intervalos de polling.

Sugestão de testes:

    100 ms

    50 ms

    30 ms

    20 ms

    10 ms, somente se tecnicamente viável.

Os valores são candidatos de teste.

Não configurar automaticamente
o menor intervalo.

A escolha deverá considerar:

- Baud rate utilizado.
- Duração de cada consulta.
- Tempo de resposta da placa.
- Estabilidade Modbus.
- Quantidade de erros.
- Utilização da porta serial.
- Consumo de CPU.
- Concorrência com comandos de relés.

Caso determinado intervalo
seja menor que o tempo necessário
para completar uma consulta,
não utilizar polling concorrente
para tentar mantê-lo.

Evitar acúmulo de requisições.

---

## 11. TESTE DE PERFORMANCE

Criar uma rotina de diagnóstico
capaz de medir o desempenho
do polling durante um período definido.

Sugestão:

    Duração: 60 segundos.

Durante o teste:

- Executar consultas periódicas.
- Medir os intervalos reais.
- Registrar o tempo das respostas.
- Registrar falhas.
- Registrar mudanças nas entradas.
- Calcular estatísticas.

Ao finalizar:

Apresentar um resumo como:

    Intervalo configurado: XX ms

    Intervalo médio: XX ms

    Intervalo mínimo: XX ms

    Intervalo máximo: XX ms

    Percentil 95: XX ms

    Tempo médio Modbus: XX ms

    Consultas realizadas: XXXX

    Consultas com sucesso: XXXX

    Falhas: XX

    Eventos DI detectados: XX

Não apresentar valores inventados.

Utilizar exclusivamente as medições
obtidas durante o teste.

---

## 12. DIAGNÓSTICO DAS ENTRADAS DIGITAIS

Aproveitar, quando possível,
a tela de diagnóstico Waveshare
já existente no aplicativo.

Adicionar uma área de monitoramento
para as cinco entradas:

    DI1
    DI2
    DI3
    DI4
    DI5

Exibir:

- Estado atual.
- Última mudança detectada.
- Quantidade de transições observadas.
- Horário da última transição.

Exemplo:

    DI1 — Normal
    Eventos detectados: 15

    DI2 — Normal
    Eventos detectados: 15

    DI3 — Normal
    Eventos detectados: 3

    DI4 — Normal
    Eventos detectados: 15

    DI5 — Normal
    Eventos detectados: 15

IMPORTANTE:

Esses contadores representam
eventos observados pelo software.

Não representam necessariamente
todos os pulsos físicos ocorridos.

Não criar uma segunda rotina
independente de polling
apenas para atualizar essa tela.

Reutilizar o serviço de leitura
das entradas já existente.

---

## 13. LOG DE TRANSIÇÕES

Implementar logging de diagnóstico
para mudanças nas entradas digitais.

Exemplo:

    10:25:31.125 — DI1 — ACIONADO

    10:25:31.184 — DI1 — NORMAL

    10:25:31.210 — DI4 — ACIONADO

    10:25:31.265 — DI4 — NORMAL

Cada evento deverá possuir:

- Timestamp.
- Entrada digital.
- Estado anterior.
- Novo estado.
- Identificação da origem.
- Informações diagnósticas relevantes.

Utilizar timestamps com precisão
suficiente para analisar
eventos em milissegundos.

Para medições de intervalo,
utilizar relógio monotônico.

Evitar gravação síncrona excessiva
em disco durante cada ciclo de polling.

O logging não poderá prejudicar
a velocidade de leitura.

Permitir habilitar/desabilitar
o diagnóstico detalhado.

---

## 14. ISOLAMENTO DA THREAD

Verificar se a comunicação Waveshare
está executando fora da thread
principal da interface QML.

A leitura Modbus não deverá
bloquear a interface gráfica.

Verificar:

- Uso de QThread ou mecanismo equivalente.
- Temporizadores utilizados.
- Operações bloqueantes.
- Contenção de locks.
- Compartilhamento da porta serial.
- Tempo gasto em callbacks.

Se o polling estiver sendo executado
na thread principal:

Avaliar a migração para
uma thread de comunicação dedicada.

Entretanto:

Não criar múltiplas threads
consultando simultaneamente
a mesma porta COM.

Preservar acesso serializado
ao dispositivo.

---

## 15. CONCORRÊNCIA COM OS RELÉS

A mesma placa Waveshare
também controla os relés:

    CH1 — Verde

    CH2 — Amarelo

    CH3 — Vermelho

O Codex deverá investigar
se comandos de relés interferem
no intervalo de consulta
das entradas digitais.

Exemplo:

    Leitura de entradas.

    Comando CH1.

    Comando CH2.

    Nova leitura de entradas.

Verificar se comandos repetitivos
ou desnecessários podem introduzir
atrasos no polling.

Evitar escrever continuamente
o mesmo estado dos relés
quando não houver alteração.

Entretanto, não modificar
a semântica nem o estado dos relés.

Qualquer otimização deverá preservar
as regras do controlador operacional.

---

## 16. COMUNICAÇÃO SERIAL

Analisar os parâmetros
de comunicação utilizados:

    Porta COM

    Baud rate

    Data bits

    Paridade

    Stop bits

    Device ID

    Timeout

Verificar se os parâmetros
estão consistentes com a configuração
real da placa.

Não alterar automaticamente
o baud rate.

Não modificar parâmetros
de comunicação sem necessidade.

Avaliar se existe oportunidade
de otimização sem prejudicar
a confiabilidade.

Registrar as conclusões
no relatório técnico.

---

## 17. ANÁLISE ELÉTRICA

O software não consegue determinar
sozinho se existe um problema
elétrico na instalação.

Entretanto, o Codex deverá
documentar possíveis fatores
externos que precisam ser
verificados durante os testes.

Itens:

1. Tensão de alimentação da placa.

2. Faixa de tensão suportada
   pelos sensores.

3. Comprimento dos cabos.

4. Tipo de cabo utilizado.

5. Interferência eletromagnética.

6. Qualidade das conexões.

7. Aterramento adequado.

8. Tempo mínimo do pulso
   produzido pelos sensores.

9. Tempo de resposta das entradas
   digitais da Waveshare.

10. Eventuais filtros internos
    do equipamento.

IMPORTANTE:

Não assumir que os cabos
ou a alimentação são
a causa do problema.

Esses fatores deverão ser
considerados hipóteses,
não diagnósticos confirmados.

---

## 18. PRESERVAR O RF040

O RF040 define as sequências:

    DI1 → DI4

para iniciar leitura.

E:

    DI5 → DI2

para encerrar a passagem.

O RF041 não poderá modificar
essas sequências.

Preservar também:

    DI3 — Pedal de reabertura.

Regras obrigatórias:

- DI1 isolado não inicia leitura.
- DI4 isolado não inicia leitura.
- DI4 → DI1 não inicia leitura.
- DI5 isolado não encerra passagem.
- DI2 isolado não encerra passagem.
- DI2 → DI5 não encerra passagem.
- DI3 funciona após timeout.
- DI3 não reabre passagem encerrada.
- Timeout permanece em 60 segundos.

O diagnóstico deverá trabalhar
na camada de aquisição
das entradas digitais.

Não modificar a máquina
de estados operacional.

---

## 19. PRESERVAR O RF037

O pedal DI3 deverá continuar
funcionando normalmente.

Preservar:

- Reabertura após timeout.
- Mesma passagem lógica.
- Dados já encontrados.
- Deduplicação de EPCs.
- Temporizador de 60 segundos.
- Bloqueio após encerramento definitivo.

Se o debounce do pedal
precisar ser ajustado,
a alteração deverá ser isolada
e validada por testes específicos.

Não permitir múltiplas reaberturas
com o pedal mantido pressionado.

---

## 20. PRESERVAR O FLUXO RFID

Não modificar:

- Zebra FX9600.
- Comunicação LLRP.
- Inventário RFID.
- Configuração das antenas.
- Potência das antenas.
- Filtro de EPC.
- Deduplicação.
- Backend Rails.
- GET e POST.
- Extra box.
- Contadores.
- Tabela Start.
- Áudio RF033.
- Voz RF035.
- Simulador RFID.
- Regras dos relés.

O requisito é dedicado
à leitura das entradas digitais
e ao diagnóstico de desempenho.

---

## 21. ESTRATÉGIA DE OTIMIZAÇÃO

A implementação deverá ocorrer
em duas etapas.

### Etapa 1 — Diagnóstico

Antes de modificar parâmetros:

1. Identificar o polling atual.
2. Instrumentar a leitura.
3. Medir os intervalos reais.
4. Medir duração das consultas.
5. Analisar debounce.
6. Verificar concorrência.
7. Identificar possíveis gargalos.
8. Registrar os resultados.

### Etapa 2 — Otimização

Após o diagnóstico:

1. Selecionar ajustes tecnicamente seguros.
2. Reduzir operações desnecessárias.
3. Avaliar polling mais frequente.
4. Preservar acesso serializado.
5. Ajustar debounce somente se necessário.
6. Executar medições comparativas.
7. Verificar estabilidade.
8. Validar detecção dos sensores.

Não implementar otimizações
sem apresentar evidências
de que são adequadas.

---

## 22. TESTES OBRIGATÓRIOS

### Teste 1 — Polling atual

Identificar o intervalo
configurado no software.

Registrar o valor encontrado.

### Teste 2 — Intervalo real

Executar diagnóstico por 60 segundos.

Registrar:

- Média.
- Mínimo.
- Máximo.
- Percentil 95.

### Teste 3 — Latência Modbus

Medir a duração
das consultas à placa.

### Teste 4 — Pulsos lentos

Acionar os sensores lentamente.

Confirmar que as transições
são reconhecidas corretamente.

### Teste 5 — Pulsos rápidos

Acionar os sensores rapidamente.

Registrar quantos acionamentos
foram observados pelo software.

Comparar com uma contagem física
independente, quando disponível.

Não presumir que todos os pulsos
foram capturados somente porque
o indicador visual do sensor piscou.

### Teste 6 — Polling 50 ms

Se tecnicamente viável,
realizar testes com intervalo
de 50 ms.

Registrar resultados.

### Teste 7 — Polling 20 ms

Se tecnicamente viável,
realizar testes com intervalo
de 20 ms.

Comparar com 50 ms.

### Teste 8 — Polling 10 ms

Executar somente se a comunicação
e o hardware suportarem.

Verificar se há benefício real.

Não adotar esse intervalo
automaticamente.

### Teste 9 — Debounce

Verificar se o debounce
descarta transições válidas.

Testar também a estabilidade
contra ruídos e eventos falsos.

### Teste 10 — Relés

Durante o polling,
executar comandos de relés
no ambiente de diagnóstico.

Confirmar que não existem
atrasos excessivos ou falhas.

Não acionar relés em operação real
apenas para realizar este teste.

### Teste 11 — Interface responsiva

Executar o diagnóstico
durante 60 segundos.

Confirmar que o PySide6/QML
permanece responsivo.

### Teste 12 — Sequência RF040

Testar:

    DI1 → DI4

Resultado:

    Início correto.

Testar:

    DI5 → DI2

Resultado:

    Encerramento correto.

### Teste 13 — Sequências inválidas

Testar:

    DI4 → DI1

    DI2 → DI5

Resultado:

    Nenhum início
    ou encerramento normal indevido.

### Teste 14 — Pedal DI3

Executar:

    DI1 → DI4 → TIMEOUT → DI3

Resultado:

    Reabertura preservada.

### Teste 15 — Falha de comunicação

Simular timeout ou desconexão
da Waveshare.

Confirmar:

- Erro identificado.
- Interface responsiva.
- Sem estados falsos de sensores.
- Recuperação conforme lógica existente.

### Teste 16 — Regressão geral

Executar os testes existentes
de comunicação Waveshare,
sensores e controle operacional.

Confirmar ausência de regressões.

---

## 23. CRITÉRIOS DE ACEITE

- [ ] Intervalo atual de polling identificado.
- [ ] Intervalo real de polling medido.
- [ ] Tempo das consultas Modbus medido.
- [ ] Intervalo médio calculado.
- [ ] Intervalo mínimo calculado.
- [ ] Intervalo máximo calculado.
- [ ] Percentil 95 calculado.
- [ ] Erros de comunicação contabilizados.
- [ ] Debounce analisado.
- [ ] Leitura conjunta das entradas avaliada.
- [ ] Concorrência serial analisada.
- [ ] Interferência dos comandos de relés avaliada.
- [ ] Diagnóstico DI1 a DI5 disponível.
- [ ] Log de transições implementado.
- [ ] Testes de pulsos rápidos realizados.
- [ ] Limitações de captura documentadas.
- [ ] Comparação entre intervalos realizada.
- [ ] Melhor configuração tecnicamente justificada.
- [ ] Otimizações seguras implementadas.
- [ ] Interface permanece responsiva.
- [ ] Regras RF040 preservadas.
- [ ] Pedal RF037 preservado.
- [ ] Timeout de 60 segundos preservado.
- [ ] Relés CH1/CH2/CH3 preservados.
- [ ] Nenhuma alteração no fluxo RFID.
- [ ] Testes de regressão aprovados.
- [ ] Relatório técnico entregue.

---

## 24. RELATÓRIO TÉCNICO

Ao finalizar, o Codex deverá produzir
um relatório contendo:

### 24.1 Configuração inicial

    Intervalo de polling encontrado:

    Baud rate:

    Timeout serial:

    Estratégia de leitura:

    Debounce existente:

### 24.2 Diagnóstico

    Intervalo médio:

    Intervalo mínimo:

    Intervalo máximo:

    P95:

    Tempo médio Modbus:

    Quantidade de consultas:

    Quantidade de falhas:

### 24.3 Comparação

Apresentar os resultados
dos intervalos efetivamente testados.

Exemplo de estrutura:

    Intervalo | Tempo real | Falhas | Observações
    ----------|------------|--------|------------
    100 ms    | Medido     | Medido | Resultado
    50 ms     | Medido     | Medido | Resultado
    20 ms     | Medido     | Medido | Resultado

Não preencher a tabela
com resultados estimados.

### 24.4 Conclusão

Informar:

- Gargalos identificados.
- Causa provável dos pulsos perdidos.
- Evidências coletadas.
- Melhor intervalo de polling.
- Melhorias implementadas.
- Resultados após otimização.
- Limitações do hardware.
- Recomendações adicionais.

Diferenciar claramente:

    Problema confirmado.

    Hipótese ainda não comprovada.

    Limitação do equipamento.

---

## 25. PROCEDIMENTO DO CODEX

Antes de implementar:

1. Ler AGENTS.md.

2. Verificar a branch atual.

3. Executar git status.

4. Preservar alterações locais.

5. Localizar o serviço Waveshare.

6. Localizar a rotina de polling.

7. Identificar a biblioteca Modbus.

8. Identificar os parâmetros seriais.

9. Identificar o debounce existente.

10. Identificar a leitura das entradas.

11. Identificar o controlador RF040.

12. Identificar o tratamento do pedal DI3.

13. Identificar os comandos de relés.

14. Identificar a tela de diagnóstico existente.

Durante a implementação:

- Instrumentar a rotina de polling.
- Implementar métricas.
- Implementar logs de diagnóstico.
- Evitar operações bloqueantes.
- Preservar a comunicação existente.
- Não criar polling concorrente.
- Avaliar leitura conjunta das entradas.
- Medir antes de otimizar.
- Realizar alterações mínimas.
- Preservar a máquina de estados.
- Preservar todas as funcionalidades.

Após implementar:

1. Executar testes automatizados.

2. Executar diagnóstico de polling,
   se o equipamento estiver disponível.

3. Comparar resultados.

4. Validar DI1 a DI5.

5. Validar o RF040.

6. Validar o RF037.

7. Validar os relés.

8. Validar a interface.

9. Executar testes de regressão.

10. Executar git diff.

11. Apresentar os arquivos modificados.

12. Entregar o relatório técnico.

13. Informar testes não executados
    por ausência de hardware.

Não inventar resultados
de testes físicos.

Não executar git reset --hard.

Não descartar alterações locais.

Não realizar commit automaticamente.

Não realizar push automaticamente.

Não realizar merge na main.

---

## 26. RESULTADO ESPERADO

O DSV RFID System deverá possuir
um processo de leitura das entradas
digitais Waveshare mais eficiente,
mensurável e confiável.

O Codex deverá identificar
a implementação atual do polling
e investigar a perda de acionamentos
rápidos dos sensores.

Após a análise, deverá implementar
somente as otimizações tecnicamente
justificadas pelos resultados.

Objetivos principais:

    Reduzir atrasos de leitura.

    Reduzir a probabilidade
    de perder pulsos rápidos.

    Melhorar a estabilidade Modbus.

    Preservar a responsividade
    da interface.

    Manter a lógica de sequenciamento:

        DI1 → DI4

        DI5 → DI2

    Preservar a reabertura pelo DI3.

IMPORTANTE:

Nenhuma otimização poderá comprometer
a confiabilidade operacional
ou modificar as regras existentes.

IMPLEMENTAR O RF041.

ANALISAR O POLLING REAL.

MEDIR ANTES DE OTIMIZAR.

INVESTIGAR PULSOS PERDIDOS.

OTIMIZAR A COMUNICAÇÃO MODBUS.

PRESERVAR O RF040.

PRESERVAR O PEDAL RF037.

NÃO ALTERAR O FLUXO OPERACIONAL RFID.

ENTREGAR RELATÓRIO TÉCNICO
COM OS RESULTADOS DAS MEDIÇÕES.
