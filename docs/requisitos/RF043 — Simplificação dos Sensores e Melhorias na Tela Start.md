# RF043 — Simplificação dos Sensores e Melhorias na Tela Start

Projeto: DSV RFID System
Requisito: RF043
Requisitos relacionados: RF012, RF030, RF031, RF037, RF040, RF042
Categoria: RFID / Automação / Sensores / Interface
Tecnologia: Python + PySide6/QML
Hardware: Zebra FX9600 + Waveshare Modbus RTU Relay D
Sistema operacional: Windows
Prioridade: Alta

---

## 1. OBJETIVO

Simplificar a lógica operacional dos sensores
do portal RFID e realizar melhorias
na interface da tela Start.

Após os testes com quatro sensores,
foi identificado que a configuração
não apresentou o comportamento esperado.

Por esse motivo, vamos retornar
à utilização de dois sensores fotoelétricos
e um pedal de acionamento manual.

Implementar as seguintes alterações:

1. DI1 passa a iniciar diretamente
   a leitura RFID.

2. DI2 passa a encerrar definitivamente
   a passagem RFID.

3. DI3 continua funcionando como pedal
   para início manual e reabertura
   de passagem após timeout.

4. DI4 e DI5 deixam de participar
   da lógica operacional.

5. Reduzir o temporizador
   de 30 para 20 segundos.

6. Adicionar um label discreto
   mostrando a quantidade de EPCs
   identificados pelo leitor.

7. Ajustar a tabela de inventário
   para exibir no mínimo 10 linhas.

8. Reduzir o tamanho da fonte
   utilizada nas linhas da tabela.

IMPORTANTE:

Preservar todas as funcionalidades
existentes que não estejam diretamente
relacionadas às alterações deste requisito.

---

## 2. NOVO MAPEAMENTO DOS SENSORES

Hardware:

    Waveshare Modbus RTU Relay D

Entradas digitais:

    DI1 — Sensor de entrada.

    DI2 — Sensor de saída.

    DI3 — Pedal de acionamento manual
          e reabertura de passagem.

    DI4 — Não utilizado operacionalmente.

    DI5 — Não utilizado operacionalmente.

O DI4 e o DI5 não deverão participar
de nenhuma decisão de início,
encerramento ou reabertura de passagem.

IMPORTANTE:

Não remover o suporte físico
às entradas DI4 e DI5
do serviço de comunicação Waveshare.

As cinco entradas poderão continuar
sendo monitoradas na tela
de diagnóstico da placa.

A alteração deverá afetar apenas
a lógica operacional RFID.

---

## 3. LÓGICA DE INÍCIO AUTOMÁTICO — DI1

A passagem RFID deverá iniciar
diretamente quando DI1 for acionado.

Não será mais necessário aguardar DI4.

Condição:

    DI1 ACIONADO
         |
         v
    INICIAR LEITURA RFID

Ao detectar um acionamento válido de DI1:

1. Verificar se o modo automático
   está habilitado.

2. Verificar se o sistema
   está operacional.

3. Verificar se não existe
   passagem aberta.

4. Verificar se não existe
   passagem aguardando complementação.

5. Verificar se não existe
   erro impeditivo.

6. Criar o contexto da passagem.

7. Iniciar o inventário Zebra FX9600.

8. Iniciar temporizador de 20 segundos.

9. Atualizar o estado operacional.

10. Acionar os relés correspondentes.

IMPORTANTE:

DI1 deverá iniciar a leitura sozinho.

Não exigir:

    DI1 → DI4

Não exigir:

    DI1 + DI4

Não utilizar DI4
como condição complementar.

---

## 4. INTERPRETAÇÃO DOS SENSORES

Preservar a interpretação elétrica
utilizada atualmente no projeto.

Os sensores fotoelétricos
possuem dois estados:

    Barreira livre.

    Barreira interrompida.

O acionamento operacional corresponde
à interrupção da barreira.

O Codex deverá utilizar
a normalização existente
no serviço Waveshare.

Não assumir diretamente
que acionado corresponde
a nível elétrico HIGH ou LOW.

Utilizar os eventos normalizados
de acionamento dos sensores.

Preservar o debounce e a detecção
de transições existentes,
desde que compatíveis
com a nova lógica.

---

## 5. LÓGICA DE ENCERRAMENTO — DI2

A passagem deverá ser encerrada
definitivamente quando DI2 for acionado.

Fluxo:

    DI2 ACIONADO
         |
         v
    ENCERRAR PASSAGEM RFID

Quando ocorrer um acionamento válido
de DI2 durante uma passagem existente:

1. Parar o inventário RFID,
   caso esteja ativo.

2. Cancelar o temporizador,
   caso esteja ativo.

3. Encerrar definitivamente
   a passagem atual.

4. Invalidar a possibilidade
   de reabertura dessa passagem
   pelo pedal DI3.

5. Executar as rotinas existentes
   de encerramento.

6. Atualizar o estado dos relés.

Não exigir:

    DI5 → DI2

Não depender do DI5.

IMPORTANTE:

DI2 deverá funcionar tanto
para passagens iniciadas
automaticamente pelo DI1
quanto para passagens iniciadas
manualmente pelo DI3.

Se não houver passagem aberta,
DI2 não deverá criar
um encerramento fictício.

Não gerar registros duplicados.

---

## 6. LÓGICA DO PEDAL DI3

O pedal DI3 deverá manter
as duas funcionalidades
estabelecidas no RF042.

### 6.1 Iniciar uma nova passagem manualmente

Quando não existir passagem aberta
ou aguardando complementação,
o acionamento válido do pedal
deverá iniciar uma nova passagem.

Condições:

- Modo operacional habilitado.
- Sistema operacional.
- Nenhum inventário ativo.
- Nenhuma passagem aberta.
- Nenhuma complementação pendente.
- Nenhum erro impeditivo.

Resultado:

    Criar nova passagem RFID.

    Iniciar inventário.

    Iniciar timer de 20 segundos.

    Ativar CH2.

    Desativar CH1.

O DI3 não deverá depender
do DI1 para iniciar
uma passagem manual.

### 6.2 Reabrir passagem após timeout

Quando uma passagem existente
for interrompida pelo timeout:

    Parar inventário.

    Preservar passagem.

    Preservar EPCs.

    Preservar tabela.

    Preservar contadores.

    Aguardar complementação.

Se DI3 for acionado:

    Reabrir a mesma passagem.

    Reiniciar inventário.

    Reiniciar timer de 20 segundos.

    Preservar EPCs já processados.

    Não duplicar registros.

### 6.3 DI3 durante inventário ativo

Se o operador pressionar o pedal
durante uma leitura em andamento:

    Ignorar acionamento.

    Não reiniciar timer.

    Não criar nova passagem.

    Não reiniciar inventário.

### 6.4 DI3 após encerramento pelo DI2

Depois que DI2 encerrar
definitivamente uma passagem,
ela não poderá ser reaberta.

Entretanto, quando o sistema
retornar validamente ao estado pronto,
um novo acionamento do DI3
poderá iniciar uma NOVA passagem manual.

Essa nova passagem não deverá
reutilizar o contexto anterior.

---

## 7. DEBOUNCE DO PEDAL

Preservar o tratamento
de debounce do DI3.

Regras:

- Um evento por pressionamento.
- Não repetir enquanto pressionado.
- Exigir liberação antes
  de um novo acionamento.
- Não criar passagens duplicadas.
- Não criar inventários simultâneos.

Se o pedal permanecer pressionado
durante o timeout:

    Não reabrir automaticamente.

Exigir novo pressionamento válido
após a liberação.

---

## 8. NOVO TEMPORIZADOR — 20 SEGUNDOS

Alterar o temporizador de inventário.

Valor anterior:

    30 segundos.

Novo valor:

    20 segundos.

O temporizador deverá iniciar:

- Após DI1 válido.
- Após início manual pelo DI3.
- Após reabertura válida pelo DI3.

Quando chegar a zero:

    Parar inventário RFID.

    Desativar CH2.

    Ativar CH1,
    se o sistema estiver operacional.

    Preservar a passagem.

    Preservar os EPCs.

    Preservar os contadores.

    Preservar os registros da tabela.

    Aguardar eventual complementação
    pelo DI3 ou encerramento pelo DI2.

IMPORTANTE:

Timeout NÃO significa encerramento
definitivo da passagem.

O DI2 continuará responsável
pelo encerramento definitivo.

Atualizar constantes,
testes e textos relacionados
ao temporizador de inventário.

Evitar valores de 30 ou 60 segundos
fixos nas rotinas que utilizam
o tempo dessa leitura.

---

## 9. REMOÇÃO DA LÓGICA DI4 E DI5

O Codex deverá revisar
o controlador operacional
e identificar os pontos
onde DI4 e DI5 participam
das decisões de leitura.

Remover sua participação em:

- Início automático.
- Validação de sequência.
- Encerramento.
- Reabertura.
- Regras de direção.
- Estados intermediários.
- Condições de autorização
  de inventário.

Não remover:

- Leitura física de DI4.
- Leitura física de DI5.
- Exibição no diagnóstico Waveshare.
- Testes genéricos de entradas digitais.

IMPORTANTE:

Não deixar estados pendentes
do fluxo anterior impedirem
o início ou o encerramento.

O sistema não deverá aguardar
DI4 ou DI5 em nenhuma condição
operacional.

---

## 10. FLUXO OPERACIONAL ATUALIZADO

O fluxo deverá funcionar assim:

    SISTEMA PRONTO
           |
           |
           +------ DI1
           |        |
           |        v
           |   INÍCIO AUTOMÁTICO
           |
           |
           +------ DI3
                    |
                    v
               INÍCIO MANUAL
                    |
                    v
              LEITURA ATIVA
                    |
                    v
               TIMER 20s
                    |
                    |
                    +------ DI2
                    |        |
                    |        v
                    |   ENCERRAMENTO
                    |   DEFINITIVO
                    |
                    |
                    +------ TIMEOUT
                              |
                              v
                       PARAR INVENTÁRIO
                              |
                              v
                         AGUARDAR
                       COMPLEMENTAÇÃO
                              |
                              |
                              +------ DI3
                              |        |
                              |        v
                              |   REABRIR MESMA
                              |   PASSAGEM
                              |
                              |
                              +------ DI2
                                       |
                                       v
                                  ENCERRAMENTO
                                  DEFINITIVO

IMPORTANTE:

O início pelo DI1
e o início manual pelo DI3
deverão utilizar a mesma rotina
operacional de abertura de passagem.

Não criar duas implementações
independentes de inventário RFID.

---

## 11. CONTROLE DOS RELÉS

Preservar o funcionamento
dos relés existentes.

### Sistema pronto

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

### Leitura iniciada pelo DI1

    CH1 = OFF
    CH2 = ON
    CH3 = OFF

### Leitura iniciada pelo DI3

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

### Encerramento pelo DI2

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

### Erro

    CH1 = OFF
    CH2 = OFF
    CH3 = ON

Não modificar a função
dos relés existentes.

Preservar as regras de segurança.

Não adicionar comandos Modbus
diretamente nos handlers dos sensores.

O controlador operacional deverá
continuar gerenciando os relés.

---

## 12. LABEL — EPCs IDENTIFICADOS

Na tela Start, adicionar
um label discreto mostrando
a quantidade de EPCs identificados
pelo reader RFID.

Texto:

    EPCs identificados: X

Exemplo:

    EPCs identificados: 2

Posicionamento obrigatório:

    Abaixo dos cards:

        EPCs encontrados

        Extra box

    E acima da tabela:

        Lista de inventário

Exemplo:

    +----------------------+----------------------+
    | EPCs encontrados     | Extra box            |
    |         8            |         2            |
    +----------------------+----------------------+

    EPCs identificados: 10

    +---------------------------------------------+
    | LISTA DE INVENTÁRIO                         |
    +---------------------------------------------+
    | Status | Cliente | NF | Volume | ...        |
    | ...                                         |
    +---------------------------------------------+

O label deverá ser discreto.

Não utilizar um novo card.

Não utilizar fonte grande.

Não utilizar cores chamativas.

---

## 13. REGRA DE CONTAGEM DO LABEL

O label deverá representar
a quantidade de EPCs únicos
identificados pelo leitor RFID
durante a passagem atual.

Essa contagem será independente
da classificação operacional
dos registros.

IMPORTANTE:

O contador não deverá ser
simplesmente uma cópia
do card EPCs encontrados.

Também não deverá ser
uma cópia do card Extra box.

A contagem deverá ocorrer
após a normalização do EPC
e aplicação do filtro de prefixos
autorizados do RF023,
mas antes da classificação
do EPC pelo backend.

Assim:

- EPC válido encontrado na base:
  contabilizar no label.

- EPC válido classificado como Extra box:
  contabilizar no label.

- EPC duplicado na mesma passagem:
  não contabilizar novamente.

- EPC com prefixo não autorizado:
  não contabilizar.

- EPC inválido:
  não contabilizar.

Exemplo:

    EPCs encontrados: 8

    Extra box: 2

    EPCs identificados: 10

A contagem deverá utilizar
um conjunto de EPCs únicos
da passagem atual.

Não contabilizar cada evento
bruto recebido das antenas
como um novo EPC.

A mesma etiqueta poderá ser lida
várias vezes pelo Zebra FX9600.

Isso deverá representar
apenas um EPC identificado.

---

## 14. ATUALIZAÇÃO DO LABEL

O label deverá ser atualizado
imediatamente após a identificação
de um novo EPC válido.

Exemplo:

    Primeira etiqueta:
        EPCs identificados: 1

    Segunda etiqueta:
        EPCs identificados: 2

    Terceira etiqueta:
        EPCs identificados: 3

Durante uma reabertura pelo DI3:

    Preservar o valor anterior.

    Somar somente novos EPCs.

Ao iniciar uma nova passagem:

    Reiniciar a contagem conforme
    a lógica existente de nova sessão.

Ao finalizar pelo DI2:

    Preservar a exibição dos dados
    conforme o comportamento atual
    da tela Start.

Não modificar a forma como
os outros dois cards contabilizam
seus respectivos registros.

---

## 15. ESTILO VISUAL DO LABEL

Seguir o padrão Corporate Dark.

Características:

    Texto:
        EPCs identificados: X

    Fonte:
        Pequena.

    Peso:
        Regular ou Medium.

    Cor:
        Cinza claro discreto.

    Alinhamento:
        Esquerda.

    Margem:
        Pequena.

    Fundo:
        Transparente.

Não utilizar:

- Card adicional.
- Borda decorativa.
- Ícone grande.
- Fonte destacada.
- Cores de alerta.

O objetivo é fornecer
uma informação complementar
sem chamar mais atenção
do que os cards principais.

---

## 16. TABELA — LISTA DE INVENTÁRIO

Atualmente, a tabela
Lista de inventário
exibe aproximadamente 8 linhas
na área disponível.

Precisamos aumentar
a quantidade de linhas visíveis.

Novo requisito:

    Exibir no mínimo 10 linhas
    simultaneamente.

O objetivo é melhorar
a visualização operacional
sem exigir rolagem tão frequente.

IMPORTANTE:

Não adicionar colunas.

Não remover colunas.

Não modificar os dados apresentados.

Não modificar a lógica de preenchimento.

A alteração será exclusivamente
no dimensionamento visual.

---

## 17. DIMENSIONAMENTO DA TABELA

O Codex deverá analisar
a altura atual da tabela
e dos elementos internos.

Realizar os ajustes necessários
para permitir a exibição
de pelo menos 10 registros.

Priorizar:

1. Redução da altura das linhas.

2. Redução do tamanho da fonte.

3. Redução do padding vertical.

4. Melhor aproveitamento
   da altura disponível.

5. Ajuste da altura da tabela,
   se necessário.

Não reduzir a legibilidade
excessivamente.

Não sobrepor textos.

Não cortar registros.

Não esconder o cabeçalho.

IMPORTANTE:

O objetivo é apresentar
10 linhas completas,
além do cabeçalho da tabela.

Não considerar o cabeçalho
como uma das 10 linhas.

---

## 18. TAMANHO DA FONTE

Reduzir o tamanho da fonte
dos dados apresentados
nas linhas da tabela.

Valor inicial sugerido:

    11 a 12 px.

O Codex deverá verificar
a tipografia atual
e escolher o tamanho
mais adequado ao layout.

Preservar legibilidade
em ambiente operacional.

Não reduzir exageradamente
os títulos das colunas.

O cabeçalho poderá manter
um tamanho ligeiramente maior
ou peso de fonte superior.

Reduzir, quando necessário:

- Altura das células.
- Margens internas.
- Espaçamento vertical.
- Padding dos delegates QML.

Não modificar cores de status.

Não modificar o destaque Extra box.

---

## 19. PRESERVAR AS SETE COLUNAS

A tabela deverá continuar
apresentando exatamente:

1. Status
2. Cliente
3. Nota Fiscal
4. Volume
5. Pedido
6. Doca
7. Dealer

Preservar o mapeamento:

    Status      -> status do registro

    Cliente     -> fornecedor

    Nota Fiscal -> notafiscal

    Volume      -> volume

    Pedido      -> pedido

    Doca        -> doca

    Dealer      -> destinatario

Não adicionar uma coluna EPC.

Não remover informações existentes.

Não modificar a ordenação
dos registros.

Não alterar os dados
recebidos do backend.

---

## 20. PRESERVAR O ESTILO EXTRA BOX

A tabela possui uma apresentação
específica para registros Extra box.

Preservar:

    Fundo: #3A372C

    Hover: #454031

    Destaque: #D9B86C

Não modificar essas cores.

A redução da fonte e das linhas
também deverá funcionar
para os registros Extra box.

Preservar as demais regras
de destaque e classificação.

---

## 21. RESPONSIVIDADE DA TELA START

A tela Start deverá continuar
funcionando em diferentes
resoluções de monitor.

Priorizar a visualização
de 10 linhas nas dimensões
operacionais utilizadas pelo projeto.

Evitar:

- Scroll horizontal desnecessário.
- Linhas sobrepostas.
- Textos cortados verticalmente.
- Botões fora da tela.
- Tabela ultrapassando o conteúdo.
- Cabeçalho oculto.

Caso a janela seja reduzida
abaixo da altura necessária,
preservar a usabilidade com
rolagem adequada.

Não impor uma altura fixa
que ultrapasse a área disponível
em monitores menores.

---

## 22. PRESERVAR O POLLING WAVESHARE

Manter o intervalo de polling
estabelecido no RF042:

    20 ms.

Não retornar para 50 ms.

Não modificar a estratégia
de comunicação Modbus,
salvo correções estritamente
necessárias para remover
dependências operacionais
de DI4 e DI5.

Preservar:

- Porta COM.
- Baud rate.
- Data bits.
- Paridade.
- Stop bits.
- Device ID.
- Timeout serial.
- Tratamento de comunicação.
- Acesso serializado.

O RF043 não tem como objetivo
executar uma nova otimização
do polling.

---

## 23. PRESERVAR O BACKEND

Não alterar os endpoints:

    GET /api/v1/rfid_records/:epc

    POST /api/v1/rfid_reads

Preservar:

- Consulta de EPC.
- Registro de passagem.
- Classificação Extra box.
- Tratamento de erros.
- Deduplicação.
- Campos retornados.
- Integração com Rails.

A nova lógica dos sensores
deverá reutilizar os serviços
operacionais existentes.

Não criar implementações
duplicadas de GET ou POST.

O novo label EPCs identificados
deverá usar informações
já disponíveis no processamento
dos EPCs.

Não realizar chamadas HTTP adicionais
apenas para atualizar o label.

---

## 24. PRESERVAR FUNCIONALIDADES EXISTENTES

Não modificar:

- Zebra FX9600.
- Comunicação LLRP.
- Biblioteca sllurp.
- Configuração de antenas.
- Potência das antenas.
- Mapa de leitura RFID.
- Filtro EPC RF023.
- Deduplicação.
- Backend Rails.
- Áudio RF033.
- Voz RF035.
- Simulador RFID RF034.
- Configurações RF036.
- Relés Waveshare.
- Indicadores de sistema.

Não adicionar dependências
desnecessárias.

Não reorganizar outras telas.

Não modificar o tema Corporate Dark.

---

## 25. TESTES OBRIGATÓRIOS

### Teste 1 — DI1 inicia leitura

Acionar DI1.

Resultado:

    Inventário inicia.

    Timer = 20 segundos.

    CH2 ligado.

### Teste 2 — DI2 encerra leitura

Iniciar passagem por DI1.

Acionar DI2.

Resultado:

    Inventário encerrado.

    Passagem finalizada.

    DI3 não reabre passagem anterior.

### Teste 3 — DI3 inicia leitura manual

Sistema pronto.

Acionar DI3.

Resultado:

    Nova passagem iniciada.

    Timer = 20 segundos.

### Teste 4 — DI3 reabre após timeout

Iniciar passagem por DI1.

Aguardar 20 segundos.

Acionar DI3.

Resultado:

    Mesma passagem reaberta.

    Timer reiniciado em 20 segundos.

    EPCs anteriores preservados.

### Teste 5 — DI3 durante leitura

Com inventário ativo,
acionar DI3.

Resultado:

    Nenhum novo inventário.

    Timer não reiniciado.

### Teste 6 — DI4 ignorado

Acionar DI4.

Resultado:

    Nenhum início ou encerramento
    operacional provocado por DI4.

### Teste 7 — DI5 ignorado

Acionar DI5.

Resultado:

    Nenhum início ou encerramento
    operacional provocado por DI5.

### Teste 8 — Timeout

Iniciar inventário.

Aguardar 20 segundos.

Resultado:

    Inventário parado.

    Passagem preservada.

    Complementação disponível.

### Teste 9 — Contador de EPCs identificados

Ler 2 EPCs válidos e distintos.

Resultado:

    EPCs identificados: 2

### Teste 10 — EPC duplicado

Ler o mesmo EPC
várias vezes.

Resultado:

    EPCs identificados: 1

### Teste 11 — Extra box

Ler:

    2 EPCs encontrados.

    1 EPC Extra box.

Resultado:

    EPCs encontrados: 2

    Extra box: 1

    EPCs identificados: 3

### Teste 12 — Prefixo não autorizado

Ler um EPC com prefixo
não autorizado.

Resultado:

    Não incrementar
    EPCs identificados.

### Teste 13 — Reabertura e contador

Primeira leitura:

    7 EPCs únicos.

Timeout.

Reabertura DI3.

Nova leitura:

    3 EPCs únicos adicionais.

Resultado:

    EPCs identificados: 10

### Teste 14 — Nova passagem

Encerrar passagem anterior.

Iniciar nova passagem.

Resultado:

    Contagem reiniciada
    conforme lógica existente.

### Teste 15 — Tabela com 10 linhas

Inserir 10 registros.

Resultado:

    10 linhas completas visíveis
    simultaneamente.

    Cabeçalho também visível.

### Teste 16 — Fonte da tabela

Confirmar:

- Fonte menor.
- Texto legível.
- Sem sobreposição.
- Sem cortes verticais.

### Teste 17 — Extra box na tabela

Adicionar registros Extra box.

Confirmar:

- Cores preservadas.
- Destaque preservado.
- Fonte reduzida corretamente.

### Teste 18 — Polling

Confirmar que o polling
permanece configurado em 20 ms.

### Teste 19 — Relés

Validar:

- Sistema pronto.
- Leitura ativa.
- Timeout.
- Reabertura.
- Encerramento.
- Erro.

### Teste 20 — Regressão

Executar testes existentes
relacionados a:

- RFID.
- Waveshare.
- Pedal.
- Sensores.
- Temporizador.
- Backend.
- EPCs.
- Extra box.
- Áudio.
- Interface Start.

Confirmar ausência de regressões.

---

## 26. CRITÉRIOS DE ACEITE

- [ ] DI1 inicia leitura diretamente.
- [ ] DI2 encerra definitivamente a passagem.
- [ ] DI3 inicia nova passagem manual.
- [ ] DI3 reabre passagem após timeout.
- [ ] DI3 não reinicia inventário ativo.
- [ ] DI3 não reabre passagem encerrada.
- [ ] DI4 removido da lógica operacional.
- [ ] DI5 removido da lógica operacional.
- [ ] DI4 e DI5 preservados no diagnóstico.
- [ ] Timer alterado para 20 segundos.
- [ ] Timeout preserva a passagem.
- [ ] Polling mantido em 20 ms.
- [ ] Relés preservados.
- [ ] EPCs preservados na reabertura.
- [ ] Deduplicação preservada.
- [ ] Label EPCs identificados adicionado.
- [ ] Label posicionado entre cards e tabela.
- [ ] Label com estilo discreto.
- [ ] EPCs identificados contabiliza EPCs únicos.
- [ ] Extra box incluído na contagem do label.
- [ ] EPCs duplicados ignorados no label.
- [ ] Prefixos não autorizados ignorados.
- [ ] Tabela apresenta no mínimo 10 linhas.
- [ ] Fonte das linhas reduzida.
- [ ] Sete colunas preservadas.
- [ ] Estilo Extra box preservado.
- [ ] Tema Corporate Dark preservado.
- [ ] Backend preservado.
- [ ] Testes automatizados aprovados.
- [ ] Testes de regressão aprovados.

---

## 27. PROCEDIMENTO DO CODEX

Antes de implementar:

1. Ler AGENTS.md.

2. Verificar a branch atual.

3. Executar git status.

4. Preservar alterações locais.

5. Identificar o controlador operacional.

6. Identificar a lógica atual
   de DI1, DI2, DI3, DI4 e DI5.

7. Identificar o temporizador
   de 30 segundos.

8. Identificar o polling Waveshare.

9. Identificar os serviços de leitura RFID.

10. Identificar o processamento
    e deduplicação dos EPCs.

11. Identificar os contadores
    EPCs encontrados e Extra box.

12. Identificar a implementação
    da tela Start.

13. Identificar os componentes QML
    da tabela de inventário.

14. Identificar os estilos
    de linhas e células.

Durante a implementação:

- Reutilizar o controlador existente.
- Simplificar a lógica dos sensores.
- Preservar as duas funções do pedal.
- Reduzir timer para 20 segundos.
- Manter polling em 20 ms.
- Preservar estados dos relés.
- Adicionar label discreto.
- Reutilizar o conjunto de EPCs únicos.
- Ajustar fonte e altura da tabela.
- Preservar todas as sete colunas.
- Preservar o backend.
- Evitar alterações desnecessárias.

Após implementar:

1. Executar testes automatizados.

2. Validar DI1.

3. Validar DI2.

4. Validar DI3 manual.

5. Validar DI3 após timeout.

6. Validar DI4 e DI5 ignorados.

7. Validar timer de 20 segundos.

8. Validar polling de 20 ms.

9. Validar o novo label.

10. Validar deduplicação.

11. Validar a tabela com 10 linhas.

12. Validar o estilo Extra box.

13. Executar testes de regressão.

14. Executar git diff.

15. Apresentar arquivos modificados.

16. Informar testes executados
    e eventuais limitações.

Não executar git reset --hard.

Não descartar alterações locais.

Não realizar commit automaticamente.

Não realizar push automaticamente.

Não realizar merge na main.

---

## 28. RESULTADO ESPERADO

O DSV RFID System deverá utilizar
a seguinte lógica operacional:

INÍCIO AUTOMÁTICO:

    DI1
     |
     v
    LEITURA RFID

INÍCIO MANUAL:

    DI3 — PEDAL
     |
     v
    NOVA PASSAGEM RFID

REABERTURA:

    TIMEOUT 20 SEGUNDOS
           |
           v
    INVENTÁRIO PARADO
           |
           v
    DI3 — PEDAL
           |
           v
    REABRIR MESMA PASSAGEM

ENCERRAMENTO:

    DI2
     |
     v
    ENCERRAMENTO DEFINITIVO

Na tela Start:

    +----------------------+----------------------+
    | EPCs encontrados     | Extra box            |
    |         8            |         2            |
    +----------------------+----------------------+

    EPCs identificados: 10

    +---------------------------------------------+
    | LISTA DE INVENTÁRIO                         |
    +---------------------------------------------+
    |                                             |
    |        MÍNIMO DE 10 LINHAS VISÍVEIS          |
    |                                             |
    +---------------------------------------------+

O sistema deverá continuar funcionando
com todos os serviços já existentes.

IMPLEMENTAR O RF043.

UTILIZAR DI1, DI2 E DI3
NA LÓGICA OPERACIONAL.

REMOVER DEPENDÊNCIAS DE DI4 E DI5.

TEMPORIZADOR RFID = 20 SEGUNDOS.

POLLING WAVESHARE = 20 MS.

ADICIONAR LABEL EPCs IDENTIFICADOS.

EXIBIR NO MÍNIMO 10 LINHAS
NA TABELA DE INVENTÁRIO.

PRESERVAR TODAS AS DEMAIS
FUNCIONALIDADES DO SISTEMA.