# RF042 — Reestruturação do Controle de Leitura RFID

Projeto: DSV RFID System
Requisito: RF042
Requisitos relacionados: RF012, RF037, RF040, RF041
Categoria: RFID / Automação / Sensores / Waveshare
Tecnologia: Python + PySide6/QML
Hardware: Zebra FX9600 + Waveshare Modbus RTU Relay D
Sistema operacional: Windows
Prioridade: Alta
Tipo de alteração: Lógica operacional / Comunicação / Temporizador

---

## 1. OBJETIVO

Modificar a lógica de acionamento do inventário RFID,
simplificando o controle dos sensores e adicionando
a possibilidade de iniciar uma passagem manualmente
através do pedal conectado à entrada DI3.

O novo funcionamento deverá contemplar:

1. Início automático por DI1 e DI4.

2. Encerramento definitivo por DI2.

3. Início manual de passagem pelo pedal DI3.

4. Reabertura de passagem após timeout pelo DI3.

5. Remoção do DI5 da lógica operacional.

6. Redução do polling Waveshare para 20 ms.

7. Redução do temporizador de 60 para 30 segundos.

IMPORTANTE:

Preservar todas as funcionalidades existentes
que não estejam diretamente relacionadas
às alterações descritas neste requisito.

---

## 2. NOVO MAPEAMENTO DOS SENSORES

Hardware:

    Waveshare Modbus RTU Relay D

Entradas digitais:

    DI1 — Primeiro sensor de entrada

    DI2 — Sensor de saída / encerramento

    DI3 — Pedal de acionamento manual
          e reabertura de leitura

    DI4 — Segundo sensor de entrada

    DI5 — Não utilizado

O DI5 não deverá mais participar
de nenhuma decisão operacional.

Remover sua participação em:

- Sequências de entrada.
- Sequências de saída.
- Encerramento de passagem.
- Validação de direção.
- Máquina de estados.
- Condições que autorizam leitura.

IMPORTANTE:

Não remover o suporte físico ao DI5
da camada de comunicação Modbus.

A entrada poderá continuar sendo exibida
na tela de diagnóstico da Waveshare.

Apenas retirar sua participação
na lógica operacional RFID.

---

## 3. NOVA LÓGICA DE INÍCIO AUTOMÁTICO

O sistema deverá permitir o início
do inventário RFID por duas condições.

### Condição A — Sequência de sensores

    DI1 → DI4

Quando o sensor DI1 for acionado
e posteriormente DI4 for acionado:

    Iniciar passagem RFID.

    Iniciar inventário.

    Iniciar temporizador de 30 segundos.

    Ativar CH2.

    Desativar CH1.

### Condição B — Sensores simultaneamente acionados

    DI1 + DI4 = ACIONADOS

Caso ambos estejam acionados,
o sistema deverá iniciar a leitura,
mesmo que a ordem de acionamento
não tenha sido identificada.

Exemplo:

    DI1 = ACIONADO
    DI4 = ACIONADO

Resultado:

    INICIAR INVENTÁRIO RFID.

Essa condição deverá funcionar
independentemente da sequência
de chegada dos eventos.

IMPORTANTE:

O acionamento de DI1 isoladamente
não deverá iniciar a leitura.

O acionamento de DI4 isoladamente
não deverá iniciar a leitura.

A leitura somente poderá iniciar
quando uma das duas condições
for confirmada.

---

## 4. INTERPRETAÇÃO DOS SENSORES

Preservar a interpretação elétrica
existente no projeto.

Os sensores fotoelétricos trabalham
com barreiras de detecção.

No sistema atual:

    Barreira normal = sensor não acionado
                       operacionalmente.

    Barreira interrompida = sensor acionado
                             operacionalmente.

O Codex deverá utilizar a normalização
já existente na comunicação Waveshare.

Não assumir diretamente
que acionado significa HIGH ou LOW.

A nova lógica deverá trabalhar
com estados normalizados.

---

## 5. INÍCIO AUTOMÁTICO — REGRAS

O início automático somente será permitido
quando:

1. O modo automático estiver habilitado.

2. O sistema estiver operacional.

3. Não existir passagem ativa.

4. Não existir passagem aguardando
   complementação após timeout.

5. Não existir condição de erro impeditiva.

6. DI1 → DI4 for identificado
   OU DI1 e DI4 estiverem acionados.

Quando a condição for atendida:

    Criar contexto da passagem.

    Iniciar inventário Zebra FX9600.

    Iniciar temporizador de 30 segundos.

    Atualizar estado operacional.

    Aplicar estado dos relés.

Não criar passagens duplicadas
enquanto os sensores permanecerem acionados.

Uma passagem finalizada deverá exigir
um novo ciclo válido dos sensores
para iniciar outra passagem automática.

Não iniciar nova passagem apenas porque
DI1 e DI4 continuam acionados
desde a passagem anterior.

---

## 6. NOVA LÓGICA DE ENCERRAMENTO

O encerramento definitivo da passagem
deverá ocorrer quando:

    DI2 = ACIONADO

Não será mais necessário
verificar o sensor DI5.

Quando DI2 for acionado:

    Parar inventário RFID, se ativo.

    Cancelar temporizador, se ativo.

    Encerrar definitivamente a passagem.

    Bloquear reabertura pelo DI3.

    Executar o encerramento operacional
    existente.

    Atualizar estado dos relés.

IMPORTANTE:

O DI2 deverá funcionar
independentemente de como
a passagem foi iniciada.

Isso inclui:

- Início automático DI1 → DI4.
- Início automático DI1 + DI4.
- Início manual pelo DI3.
- Reabertura pelo DI3 após timeout.

Não encerrar uma passagem inexistente.

Um DI2 acionado sem passagem válida
não deverá gerar registros
ou encerramentos duplicados.

---

## 7. REMOÇÃO DA LÓGICA DI5

A lógica anterior exigia:

    DI5 → DI2

Essa regra deverá ser removida.

A nova regra será:

    DI2 → ENCERRAMENTO DEFINITIVO

O Codex deverá identificar
todos os pontos do código onde
DI5 participa das decisões operacionais.

Remover as dependências de DI5
relacionadas ao início e encerramento.

Verificar especialmente:

- Controlador de estados.
- Processamento de eventos.
- Validações de sequência.
- Testes automatizados.
- Configurações operacionais.
- Mensagens de status.
- Rotinas de encerramento.

Não alterar a comunicação física
com a entrada DI5.

Não apagar testes genéricos
de leitura digital do DI5.

A alteração se limita
à lógica operacional RFID.

---

## 8. NOVA FUNCIONALIDADE — INÍCIO MANUAL PELO DI3

O pedal conectado ao DI3
passará a possuir duas funcionalidades.

A primeira será:

    INICIAR UMA NOVA PASSAGEM MANUALMENTE.

Essa opção deverá funcionar
quando não existir passagem
ativa ou aguardando complementação.

### Condições para início manual

1. O modo de operação estiver habilitado.

2. O sistema estiver operacional.

3. Não existir inventário RFID ativo.

4. Não existir passagem aberta.

5. Não existir passagem aguardando
   complementação após timeout.

6. Não existir condição de erro impeditiva.

7. O pedal DI3 receber
   um acionamento válido.

Quando essas condições forem atendidas:

    Criar nova passagem RFID.

    Iniciar inventário RFID.

    Iniciar temporizador de 30 segundos.

    Ativar CH2.

    Desativar CH1.

    Preservar CH3 desligado
    se não houver erro.

IMPORTANTE:

O DI3 não deverá depender
do acionamento de DI1 ou DI4
para iniciar uma passagem manual.

Esse será um modo alternativo
de iniciar a leitura.

O operador poderá iniciar
a leitura diretamente pelo pedal.

---

## 9. FUNCIONALIDADE EXISTENTE — REABERTURA PELO DI3

Preservar o comportamento
implementado no RF037.

Quando uma passagem for iniciada
e o temporizador chegar a zero:

    Parar o inventário RFID.

    Preservar a passagem lógica.

    Preservar os EPCs encontrados.

    Preservar os registros da tabela.

    Preservar os contadores.

    Entrar no estado:

        AGUARDANDO_COMPLEMENTACAO

Nesse estado, se o operador
acionar o pedal DI3:

    Reabrir o inventário RFID.

    Reiniciar temporizador em 30 segundos.

    Preservar os EPCs anteriores.

    Manter a mesma passagem lógica.

    Não duplicar registros.

Não criar uma nova passagem
durante essa reabertura.

---

## 10. DIFERENCIAR AS DUAS FUNÇÕES DO DI3

O pedal terá comportamento
dependente do estado operacional.

### Situação A — Sistema pronto

Condições:

    Nenhuma passagem aberta.

    Nenhum inventário ativo.

    Nenhuma complementação pendente.

    Modo de operação habilitado.

    Sistema operacional.

DI3 acionado:

    INICIAR NOVA PASSAGEM MANUAL.

### Situação B — Inventário ativo

Condições:

    Passagem aberta.

    Inventário em andamento.

DI3 acionado:

    IGNORAR ACIONAMENTO.

Não reiniciar o temporizador.

Não iniciar novo inventário.

Não criar nova passagem.

### Situação C — Timeout

Condições:

    Passagem existente.

    Inventário parado por timeout.

    Passagem aguardando complementação.

DI3 acionado:

    REABRIR MESMA PASSAGEM.

Preservar todos os dados anteriores.

### Situação D — Passagem encerrada pelo DI2

Condições:

    Passagem encerrada definitivamente.

DI3 acionado:

    NÃO REABRIR A PASSAGEM ANTERIOR.

Entretanto, após o sistema retornar
validamente ao estado pronto,
o DI3 poderá iniciar uma NOVA
passagem manual.

Essa nova passagem deverá possuir
um contexto independente da anterior.

### Situação E — Stop manual

Condições:

    Modo de operação desabilitado.

DI3 acionado:

    IGNORAR ACIONAMENTO.

Não iniciar inventário.

### Situação F — Erro operacional

Condições:

    Existe erro impeditivo.

DI3 acionado:

    IGNORAR ACIONAMENTO.

Não iniciar inventário.

---

## 11. PRIORIDADE DA LÓGICA DO PEDAL

Ao receber um acionamento válido do DI3,
o sistema deverá verificar o estado atual.

Pseudocódigo conceitual:

    if not modo_operacional_habilitado:
        ignorar_pedal()

    elif existe_erro_impeditivo:
        ignorar_pedal()

    elif inventario_ativo:
        ignorar_pedal()

    elif passagem_aguardando_complementacao:
        reabrir_passagem_existente()

    elif nao_existe_passagem_aberta:
        iniciar_nova_passagem_manual()

    else:
        ignorar_pedal()

IMPORTANTE:

A verificação do estado deverá ocorrer
de forma segura e consistente.

Não permitir que o mesmo acionamento
do pedal execute simultaneamente:

    Nova passagem

e:

    Reabertura de passagem existente.

O sistema deverá executar
somente uma ação por acionamento.

---

## 12. DEBOUNCE DO PEDAL

Preservar o tratamento de debounce
existente para o DI3.

O pedal deverá gerar apenas
um evento por pressionamento válido.

Não permitir:

- Inícios repetidos.
- Reaberturas duplicadas.
- Reinicializações contínuas.
- Múltiplos inventários simultâneos.

Se o pedal permanecer pressionado:

    Executar apenas uma ação.

Para aceitar novo acionamento:

    Exigir liberação do pedal.

    Detectar novo pressionamento válido.

Caso o pedal permaneça pressionado
durante a transição para timeout,
não reabrir automaticamente.

Será necessário um novo pressionamento.

---

## 13. NOVO TEMPORIZADOR — 30 SEGUNDOS

Alterar o tempo padrão
de inventário RFID.

Valor anterior:

    60 segundos.

Novo valor:

    30 segundos.

O temporizador deverá iniciar quando:

- A passagem iniciar automaticamente.
- A passagem iniciar manualmente pelo DI3.
- Uma leitura for reaberta pelo DI3.

Quando chegar a zero:

    Parar inventário RFID.

    Desativar CH2.

    Ativar CH1,
    se o sistema estiver operacional.

    Preservar os dados da passagem.

    Entrar no estado
    AGUARDANDO_COMPLEMENTACAO.

IMPORTANTE:

O timeout não encerra
definitivamente a passagem.

O DI2 continuará sendo responsável
pelo encerramento definitivo.

Não manter referências fixas
de 60 segundos nas rotinas operacionais
que utilizam o temporizador
dessa leitura.

Atualizar testes e constantes
correspondentes.

---

## 14. POLLING WAVESHARE — 20 MS

Alterar o intervalo configurado
de consulta das entradas digitais.

Valor anterior esperado:

    50 ms.

Novo valor:

    20 ms.

Objetivo:

    Reduzir o intervalo entre consultas
    às entradas digitais da Waveshare.

    Melhorar a detecção
    de acionamentos rápidos.

    Reduzir a probabilidade
    de perder pulsos curtos.

O Codex deverá localizar
a implementação atual do polling.

Verificar se o intervalo
realmente está configurado em 50 ms.

Se o valor atual for diferente,
registrar essa informação
no relatório técnico.

Configurar o novo intervalo:

    20 ms = 0,020 segundos.

IMPORTANTE:

O intervalo de 20 ms representa
o valor configurado/solicitado.

O intervalo real poderá ser maior,
dependendo da comunicação Modbus.

Não executar consultas concorrentes
para tentar compensar atrasos.

Não permitir acúmulo de requisições.

Preservar acesso serializado
à porta COM.

Se o tempo de resposta Modbus
impedir a execução a cada 20 ms,
documentar a limitação.

---

## 15. VALIDAÇÃO DO POLLING

Após configurar 20 ms,
validar o comportamento.

Medir:

- Intervalo solicitado.
- Intervalo real médio.
- Intervalo real máximo.
- Duração das consultas Modbus.
- Quantidade de falhas.
- Timeouts.
- Retries.
- Estabilidade da comunicação.

Utilizar medição monotônica
quando aplicável.

Verificar o comportamento
durante:

- Leitura RFID ativa.
- Acionamento de relés.
- Pedal DI3.
- Sensores DI1, DI2 e DI4.

IMPORTANTE:

Reduzir o polling não garante
a captura de todos os pulsos físicos.

Não afirmar que o problema
de pulsos perdidos foi resolvido
sem testes físicos.

---

## 16. CONTROLE DOS RELÉS

Preservar as funções existentes:

    CH1 — Verde / Pronto

    CH2 — Amarelo / Leitura ativa

    CH3 — Vermelho / Erro

### Sistema pronto

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

### Passagem iniciada automaticamente

    CH1 = OFF
    CH2 = ON
    CH3 = OFF

### Passagem iniciada manualmente pelo DI3

    CH1 = OFF
    CH2 = ON
    CH3 = OFF

### Passagem reaberta pelo DI3

    CH1 = OFF
    CH2 = ON
    CH3 = OFF

### Timeout

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

### Encerramento definitivo pelo DI2

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

### Estado de erro

    CH1 = OFF
    CH2 = OFF
    CH3 = ON

Não criar comandos Modbus
diretamente nos handlers do pedal.

O controlador operacional existente
deverá continuar responsável
pelo estado dos relés.

Preservar os tratamentos
de segurança existentes.

---

## 17. PRESERVAÇÃO DE EPCs

Preservar a deduplicação existente.

Durante a reabertura pelo pedal:

    Não apagar EPCs encontrados.

    Não limpar a tabela.

    Não zerar contadores.

    Não repetir registros já processados.

    Não reproduzir novamente o bip
    para EPCs duplicados.

Novos EPCs deverão ser adicionados
normalmente à mesma passagem.

Exemplo:

    Leitura inicial:

        7 EPCs encontrados.

    Timeout:

        Inventário parado.

    DI3:

        Inventário reaberto.

    Novos EPCs:

        3 encontrados.

    Resultado:

        Total = 10 EPCs únicos.

No início de uma NOVA passagem manual:

    Criar um novo contexto de passagem.

    Aplicar a mesma inicialização
    de registros e contadores utilizada
    no início automático.

Não reutilizar os dados
da passagem anterior encerrada.

---

## 18. BACKEND RFID

Preservar os endpoints existentes:

    GET /api/v1/rfid_records/:epc

    POST /api/v1/rfid_reads

Não modificar contratos da API.

Uma passagem iniciada manualmente
deverá utilizar o mesmo fluxo
de processamento de EPCs
das passagens iniciadas automaticamente.

Não criar uma segunda implementação
de consulta ou registro.

Regras:

- EPC novo segue fluxo normal.
- EPC duplicado não é processado novamente.
- Extra box mantém sua classificação.
- Reabertura continua a mesma passagem.
- Nova passagem manual cria novo contexto.
- DI2 encerra definitivamente a passagem.

Não duplicar POSTs.

Não alterar endpoints.

---

## 19. MÁQUINA DE ESTADOS

Reutilizar o controlador existente.

Estados conceituais necessários:

    PRONTO

    AGUARDANDO_DI4

    LEITURA_ATIVA

    AGUARDANDO_COMPLEMENTACAO

    PASSAGEM_ENCERRADA

    ERRO

O Codex deverá adaptar
os estados já existentes
sem criar controladores paralelos.

Transições principais:

    PRONTO
        |
        +-- DI1 → DI4
        |       |
        |       v
        |   LEITURA_ATIVA
        |
        +-- DI1 + DI4 ativos
        |       |
        |       v
        |   LEITURA_ATIVA
        |
        +-- DI3
                |
                v
            LEITURA_ATIVA


    LEITURA_ATIVA
        |
        +-- TIMEOUT
        |       |
        |       v
        |   AGUARDANDO_COMPLEMENTACAO
        |
        +-- DI2
                |
                v
            PASSAGEM_ENCERRADA


    AGUARDANDO_COMPLEMENTACAO
        |
        +-- DI3
        |       |
        |       v
        |   LEITURA_ATIVA
        |
        +-- DI2
                |
                v
            PASSAGEM_ENCERRADA


    PASSAGEM_ENCERRADA
        |
        v
    PRONTO

O retorno para PRONTO deverá respeitar
as condições existentes de segurança,
modo habilitado e ciclo dos sensores.

---

## 20. PREVENÇÃO DE ACIONAMENTOS DUPLICADOS

Evitar múltiplos inícios
para a mesma passagem.

Exemplos:

### Caso A — DI1 e DI4 permanecem acionados

Resultado:

    Iniciar apenas uma passagem.

### Caso B — DI3 pressionado durante início automático

Resultado:

    Não criar segunda passagem.

### Caso C — DI3 pressionado durante inventário

Resultado:

    Não reiniciar inventário.

### Caso D — DI2 permanece acionado

Resultado:

    Encerrar apenas uma vez.

    Não gerar encerramentos duplicados.

### Caso E — DI3 permanece pressionado

Resultado:

    Apenas uma ação por pressionamento.

### Caso F — DI1 e DI4 já acionados após DI2

Resultado:

    Não iniciar automaticamente
    outra passagem usando estados antigos.

    Exigir novo ciclo válido dos sensores.

---

## 21. PRESERVAR FUNCIONALIDADES EXISTENTES

Não modificar:

- Zebra FX9600.
- Comunicação LLRP.
- Biblioteca sllurp.
- Configurações das antenas.
- Potência das antenas.
- Filtro EPC.
- Deduplicação de EPCs.
- Classificação Extra box.
- Tabela Start.
- Backend Rails.
- Áudio RF033.
- Voz RF035.
- Simulador RFID.
- Layout de configurações.
- Mapa de leitura RFID.

Preservar a operação do sistema
em ambiente Windows.

Não adicionar dependências
desnecessárias.

---

## 22. TESTES OBRIGATÓRIOS

### Teste 1 — DI1 isolado

Acionar DI1.

Resultado:

    Leitura não inicia.

### Teste 2 — DI4 isolado

Acionar DI4.

Resultado:

    Leitura não inicia.

### Teste 3 — Sequência DI1 → DI4

Acionar DI1.

Depois DI4.

Resultado:

    Inventário inicia.

    Timer = 30 segundos.

    CH2 ligado.

### Teste 4 — DI1 e DI4 simultâneos

Acionar DI1 e DI4.

Resultado:

    Inventário inicia.

    Apenas uma passagem criada.

### Teste 5 — DI2 encerra leitura automática

Iniciar por DI1 → DI4.

Acionar DI2.

Resultado:

    Inventário encerrado.

    Passagem finalizada.

### Teste 6 — DI2 encerra leitura manual

Iniciar por DI3.

Acionar DI2.

Resultado:

    Inventário encerrado.

    Passagem finalizada.

### Teste 7 — DI5 ignorado

Acionar DI5.

Resultado:

    Nenhuma alteração operacional.

    Nenhum inventário iniciado.

    Nenhuma passagem encerrada.

### Teste 8 — Pedal inicia nova passagem

Sistema pronto.

Sem passagem aberta.

Acionar DI3.

Resultado:

    Nova passagem iniciada.

    Timer = 30 segundos.

    CH2 ligado.

### Teste 9 — Pedal reabre após timeout

Iniciar uma passagem.

Aguardar timeout de 30 segundos.

Acionar DI3.

Resultado:

    Mesma passagem reaberta.

    Timer reiniciado em 30 segundos.

    EPCs preservados.

### Teste 10 — Pedal durante inventário

Com leitura ativa:

    Acionar DI3.

Resultado:

    Nenhum novo inventário.

    Timer não reiniciado.

### Teste 11 — Pedal após encerramento

Iniciar passagem.

Encerrar por DI2.

Retornar validamente ao estado PRONTO.

Acionar DI3.

Resultado:

    Nova passagem manual.

    Não reabrir passagem anterior.

### Teste 12 — Timeout

Iniciar inventário.

Aguardar 30 segundos.

Resultado:

    Inventário parado.

    Dados preservados.

    Aguardando complementação.

### Teste 13 — Deduplicação

Primeira leitura:

    7 EPCs.

Timeout.

Reabertura DI3.

Ler novamente os 7 EPCs anteriores
e mais 3 novos.

Resultado:

    Total: 10 EPCs únicos.

### Teste 14 — Relés

Validar:

- Sistema pronto.
- Leitura automática.
- Leitura manual.
- Reabertura.
- Timeout.
- Encerramento.
- Erro.

### Teste 15 — Polling

Confirmar:

    Intervalo configurado = 20 ms.

Medir o intervalo real
e registrar resultados.

### Teste 16 — Pulsos rápidos

Executar testes com acionamentos
rápidos de DI1, DI2, DI3 e DI4.

Registrar eventos observados.

### Teste 17 — Stop manual

Desabilitar modo operacional.

Acionar DI3.

Resultado:

    Nenhum inventário iniciado.

### Teste 18 — Erro operacional

Simular erro impeditivo.

Acionar DI3.

Resultado:

    Nenhum inventário iniciado.

### Teste 19 — Backend

Confirmar:

- GET funcionando.
- POST funcionando.
- Sem registros duplicados.
- Início manual utilizando
  processamento normal.

### Teste 20 — Regressão

Executar testes existentes
de RFID, Waveshare, pedal,
relés, timer e backend.

---

## 23. CRITÉRIOS DE ACEITE

- [ ] DI1 → DI4 inicia inventário.
- [ ] DI1 e DI4 acionados iniciam inventário.
- [ ] DI1 isolado não inicia inventário.
- [ ] DI4 isolado não inicia inventário.
- [ ] DI2 encerra definitivamente a passagem.
- [ ] DI5 removido da lógica operacional.
- [ ] DI3 inicia nova passagem manual.
- [ ] DI3 reabre passagem após timeout.
- [ ] DI3 não reinicia inventário ativo.
- [ ] DI3 não reabre passagem encerrada.
- [ ] Novo acionamento DI3 após encerramento
      inicia nova passagem independente.
- [ ] Timer alterado para 30 segundos.
- [ ] Polling configurado em 20 ms.
- [ ] Polling real medido.
- [ ] EPCs preservados na reabertura.
- [ ] Deduplicação preservada.
- [ ] Relés CH1/CH2/CH3 preservados.
- [ ] Backend preservado.
- [ ] Regras de segurança preservadas.
- [ ] Interface preservada.
- [ ] Testes automatizados aprovados.
- [ ] Testes de regressão aprovados.

---

## 24. PROCEDIMENTO DO CODEX

Antes de implementar:

1. Ler AGENTS.md.

2. Verificar a branch atual.

3. Executar git status.

4. Preservar alterações locais.

5. Identificar o controlador operacional.

6. Identificar os handlers DI1 a DI5.

7. Identificar a implementação do RF037.

8. Identificar as alterações do RF040.

9. Identificar o polling Waveshare.

10. Identificar o temporizador atual.

11. Identificar o gerenciamento
    de passagens RFID.

12. Identificar a lógica de deduplicação.

13. Identificar a integração GET/POST.

14. Identificar os comandos de relés.

Durante a implementação:

- Reutilizar o controlador existente.
- Simplificar a sequência de saída.
- Remover dependências operacionais do DI5.
- Adicionar início manual pelo DI3.
- Preservar reabertura após timeout.
- Alterar timer para 30 segundos.
- Alterar polling para 20 ms.
- Preservar acesso serializado.
- Preservar a comunicação Modbus.
- Preservar a lógica de EPCs.
- Preservar integração Rails.
- Evitar alterações de interface.
- Não adicionar dependências pesadas.

Após implementar:

1. Executar testes automatizados.

2. Validar início automático.

3. Validar início manual.

4. Validar reabertura pelo pedal.

5. Validar encerramento pelo DI2.

6. Validar remoção do DI5.

7. Validar timeout de 30 segundos.

8. Validar polling de 20 ms.

9. Validar relés.

10. Validar deduplicação.

11. Validar backend.

12. Executar testes de regressão.

13. Executar git diff.

14. Apresentar arquivos modificados.

15. Informar testes realizados.

16. Informar limitações de hardware
    identificadas durante os testes.

Não executar git reset --hard.

Não descartar alterações locais.

Não realizar commit automaticamente.

Não realizar push automaticamente.

Não realizar merge na main.

---

## 25. RESULTADO ESPERADO

O DSV RFID System deverá permitir
iniciar uma passagem RFID de duas formas.

MODO AUTOMÁTICO:

    DI1 → DI4
        |
        v
    INICIAR LEITURA

OU:

    DI1 + DI4 ACIONADOS
        |
        v
    INICIAR LEITURA


MODO MANUAL:

    DI3 — PEDAL
        |
        v
    INICIAR NOVA PASSAGEM


REABERTURA:

    LEITURA ATIVA
        |
        v
    TIMEOUT 30 SEGUNDOS
        |
        v
    AGUARDANDO COMPLEMENTAÇÃO
        |
        v
    DI3 — PEDAL
        |
        v
    REABRIR MESMA PASSAGEM


ENCERRAMENTO:

    DI2 ACIONADO
        |
        v
    ENCERRAR DEFINITIVAMENTE


O sensor DI5 não participará
mais das decisões operacionais.

O intervalo de polling deverá
ser configurado em 20 ms.

O temporizador de inventário
deverá ser reduzido para 30 segundos.

Todas as funcionalidades existentes
não relacionadas deverão ser preservadas.

IMPLEMENTAR O RF042.

INÍCIO AUTOMÁTICO POR DI1 → DI4
OU DI1 + DI4 ACIONADOS.

ENCERRAMENTO DEFINITIVO POR DI2.

DI3 INICIA NOVA PASSAGEM MANUAL
OU REABRE PASSAGEM APÓS TIMEOUT.

REMOVER DI5 DA LÓGICA OPERACIONAL.

POLLING WAVESHARE = 20 MS.

TEMPORIZADOR RFID = 30 SEGUNDOS.

PRESERVAR EPCs, RELÉS, BACKEND
E REGRAS DE SEGURANÇA.