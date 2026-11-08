# RF036 — Reorganização do Layout da Tela de Configurações

Projeto: DSV RFID System
Requisito: RF036
Categoria: Interface / Layout / Usabilidade
Tecnologia: Python + PySide6/QML
Sistema operacional: Windows
Prioridade: Média
Tipo de alteração: Exclusivamente visual

---

## 1. OBJETIVO

Reorganizar o layout da tela Configurações
do DSV RFID System.

Atualmente, a tela apresenta diversos
componentes de configuração que precisam
ser melhor distribuídos visualmente.

A nova organização deverá utilizar:

    GRID DE DUAS COLUNAS

Cada grupo de funcionalidades deverá
possuir seu próprio card.

O objetivo é:

- Melhorar a organização visual.
- Facilitar a localização das configurações.
- Reduzir espaços desperdiçados.
- Melhorar a distribuição dos componentes.
- Reduzir a necessidade de rolagem.
- Preservar a identidade visual do sistema.
- Tornar a interface mais compacta e organizada.

IMPORTANTE:

TODAS AS FUNCIONALIDADES ATUAIS
ESTÃO FUNCIONANDO CORRETAMENTE.

NÃO ALTERAR REGRAS DE NEGÓCIO.

NÃO MODIFICAR SERVIÇOS.

NÃO ALTERAR COMUNICAÇÕES COM HARDWARE.

NÃO ALTERAR O FUNCIONAMENTO DOS BOTÕES.

ESTE REQUISITO É EXCLUSIVAMENTE
PARA REORGANIZAÇÃO DO LAYOUT.

---

## 2. ESTRUTURA GERAL

A tela Configurações deverá utilizar
um grid de duas colunas.

Cada coluna deverá ocupar aproximadamente
50% da largura disponível.

Manter espaçamento uniforme entre
os cards.

Estrutura visual sugerida:

    +--------------------------------+--------------------------------+
    |                                |                                |
    | CONFIGURAÇÕES RFID             | CONFIGURAÇÕES WAVESHARE        |
    |                                |                                |
    +--------------------------------+                                |
    |                                |                                |
    | DOCA ESTAÇÃO                   |                                |
    |                                |                                |
    +--------------------------------+--------------------------------+
    |                                |                                |
    | CONFIGURAÇÕES DE ÁUDIO         | BACKEND RFID                   |
    |                                |                                |
    +--------------------------------+--------------------------------+
    |                                |                                |
    | FERRAMENTAS DE TESTE           | FILTRO EPC                     |
    |                                |                                |
    +--------------------------------+--------------------------------+

A disposição apresentada é uma referência.

O Codex poderá ajustar a ordem dos cards
para aproveitar melhor o espaço disponível.

Requisitos:

- Duas colunas em resoluções desktop.
- Larguras equilibradas.
- Espaçamentos consistentes.
- Alinhamento superior dos cards.
- Altura de cada card conforme seu conteúdo.
- Não forçar todos os cards a terem
  a mesma altura.
- Evitar espaços vazios excessivos.

Preferir uma estrutura com duas colunas
e cards empilhados verticalmente,
caso isso produza melhor aproveitamento
do espaço do que um GridLayout tradicional.

Em janelas estreitas, permitir adaptação
para uma coluna quando necessário,
sem sobreposição ou corte dos controles.

---

## 3. CARD — CONFIGURAÇÕES RFID

Criar um card exclusivo denominado:

    Configurações RFID

Mover para esse card todos os componentes
existentes relacionados à configuração
do leitor Zebra FX9600.

Exemplos de configurações:

- Endereço IP do leitor.
- Porta de comunicação.
- Nome do leitor.
- Configurações de antenas, se existentes.
- Demais parâmetros RFID existentes.
- Botões de salvar.
- Botões de testar conexão.

IMPORTANTE:

Não adicionar novas configurações.

Não remover campos existentes.

Não modificar:

- Validação de IP.
- Porta de comunicação.
- Configuração LLRP.
- Persistência das configurações.
- Testes de conexão.
- Comportamento dos botões.

Apenas reorganizar os componentes
existentes dentro do novo card.

---

## 4. CARD — CONFIGURAÇÕES WAVESHARE

Manter todas as configurações da Waveshare
dentro de um único card.

Título:

    Configurações da Waveshare

NÃO dividir as configurações Waveshare
em múltiplos cards.

Preservar todos os campos existentes.

Realizar os seguintes ajustes
de posicionamento.

### 4.1 Data Bits e Paridade

Os campos:

    Data bits
    Paridade

Deverão ficar lado a lado.

Exemplo:

    +--------------------+--------------------+
    | Data bits          | Paridade           |
    | [       8       ]  | [      None     ]  |
    +--------------------+--------------------+

Utilizar duas colunas internas
com larguras equivalentes.

### 4.2 Stop Bits e Device ID

Os campos:

    Stop bits
    Device ID

Também deverão ficar lado a lado.

Exemplo:

    +--------------------+--------------------+
    | Stop bits          | Device ID          |
    | [       1       ]  | [       1       ]  |
    +--------------------+--------------------+

### 4.3 Demais configurações

Preservar os demais componentes
da Waveshare.

Exemplos:

- Porta COM.
- Baud rate.
- Configurações seriais existentes.
- Botões de salvar.
- Botões de testar.
- Demais controles existentes.

Não modificar a lógica dos campos.

Não alterar:

- Comunicação Modbus RTU.
- Configuração serial.
- Endereço do dispositivo.
- Comandos de leitura.
- Comandos de escrita.
- Testes de conexão.
- Acionamento de relés.
- Leitura de entradas digitais.

A alteração será apenas visual.

---

## 5. CARD — DOCA ESTAÇÃO

Criar um card exclusivo denominado:

    Doca Estação

Mover para esse card os componentes
existentes relacionados à seleção
da doca operacional.

Manter obrigatoriamente:

1. Dropdown de seleção da doca.
2. Botão Salvar doca.

Estrutura sugerida:

    +--------------------------------------+
    | DOCA ESTAÇÃO                         |
    |                                      |
    | Selecionar doca                      |
    | [              ▼               ]    |
    |                                      |
    | [          Salvar doca          ]    |
    +--------------------------------------+

Preservar:

- Opções disponíveis no dropdown.
- Valor atualmente selecionado.
- Persistência da doca.
- Evento do botão Salvar doca.
- Mensagens de sucesso.
- Mensagens de erro.
- Validações existentes.

Não alterar a forma como a doca
é utilizada pelo sistema RFID.

---

## 6. CARD — CONFIGURAÇÕES DE ÁUDIO

Criar um card exclusivo denominado:

    Configurações de Áudio

Esse card deverá concentrar todas
as funcionalidades existentes
relacionadas à sonoridade do sistema.

Incluir os controles existentes
relacionados a:

### 6.1 Bip RFID — RF033

Mover os componentes relacionados
ao bip sonoro.

Preservar:

- Botão de teste do bip.
- Configurações existentes.
- Arquivo de áudio utilizado.
- Serviço de reprodução.
- Fila de áudio.
- Volume, se configurável.
- Demais controles existentes.

### 6.2 Notificação por voz — RF035

Mover os componentes relacionados
à voz do sistema.

Preservar:

- Voz Microsoft Maria Desktop.
- Campo de quantidade de caixas.
- Prévia da mensagem.
- Botão Testar voz.
- Indicadores ou mensagens de erro.
- Demais controles existentes.

Não modificar a tecnologia de voz.

Não modificar o serviço Windows SAPI.

Não alterar a mensagem reproduzida.

Não alterar volume ou velocidade
configurados no RF035.

### 6.3 Organização interna

Separar visualmente os dois recursos
dentro do mesmo card.

Exemplo:

    +--------------------------------------+
    | CONFIGURAÇÕES DE ÁUDIO               |
    |                                      |
    | Bip RFID                             |
    |                                      |
    | [          Testar bip           ]    |
    |                                      |
    | ------------------------------------ |
    |                                      |
    | Notificação por voz                  |
    |                                      |
    | Voz: Microsoft Maria Desktop         |
    |                                      |
    | Quantidade de caixas                 |
    | [              10              ]    |
    |                                      |
    | [          Testar voz           ]    |
    +--------------------------------------+

Não criar cards separados para
bip e voz.

Ambos deverão permanecer dentro
do card Configurações de Áudio.

Não adicionar novas funcionalidades
de áudio neste requisito.

---

## 7. CARD — FERRAMENTAS DE TESTE

Criar um card exclusivo denominado:

    Ferramentas de Teste

Mover para esse card o botão:

    Simulador

Esse botão deverá continuar abrindo
o Simulador RFID implementado no RF034.

Estrutura sugerida:

    +--------------------------------------+
    | FERRAMENTAS DE TESTE                 |
    |                                      |
    | Simulador RFID                       |
    |                                      |
    | [          Simulador            ]    |
    +--------------------------------------+

Preservar:

- Evento de abertura do simulador.
- Modal existente.
- Contadores.
- Tabela de registros.
- Botões de simulação.
- Estados da sessão.
- Isolamento do hardware.
- Todas as funcionalidades RF034
  e RF034.01.

Não modificar o modal Simulador RFID.

Não alterar a lógica da simulação.

Apenas mover o botão para o novo card.

---

## 8. CARD — FILTRO EPC

O card Filtro EPC já existe.

Não recriar a funcionalidade.

O objetivo é reduzir o espaço
ocupado por esse componente.

Problema atual:

O card está excessivamente grande,
tanto na largura quanto na altura.

Como o sistema poderá possuir
muitos filtros EPC, a visualização
atual exige muita rolagem.

Precisamos tornar esse card
mais compacto e organizado.

### 8.1 Largura

O card deverá ocupar apenas
uma coluna do grid principal.

Não utilizar largura total
da tela Configurações.

Respeitar as margens do grid.

Evitar componentes que ultrapassem
a largura disponível.

### 8.2 Altura

Reduzir a altura ocupada
pela listagem dos filtros EPC.

Definir uma altura máxima
para a área de listagem.

Valor inicial sugerido:

    Altura máxima: 250 a 300 px

O Codex poderá ajustar esse valor
conforme os componentes existentes.

IMPORTANTE:

A limitação de altura deverá
ser aplicada à listagem dos filtros,
não aos controles essenciais do card.

Manter visíveis e acessíveis
os botões de configuração existentes.

### 8.3 Rolagem interna

Se houver muitos filtros:

    Utilizar scroll interno.

O scroll deverá ocorrer apenas
dentro da área de listagem.

Não permitir que a lista aumente
indefinidamente a altura do card.

Exemplo:

    +--------------------------------------+
    | FILTRO EPC                           |
    |                                      |
    | Prefixos autorizados                 |
    |                                      |
    | +----------------------------------+ |
    | | 445543                           | |
    | | 474143                           | |
    | | 47574D                           | |
    | | 484C44                           | |
    | | 4A4554                           | |
    | | ...                         ↕    | |
    | +----------------------------------+ |
    |                                      |
    | [ Controles existentes do filtro ]   |
    +--------------------------------------+

### 8.4 Fonte

Reduzir o tamanho da fonte
utilizada na listagem dos filtros.

Valor sugerido:

    11 a 12 px

Ajustar conforme a fonte
e o tema utilizados no projeto.

Preservar legibilidade.

Não reduzir excessivamente
o tamanho dos botões.

Reduzir também, quando apropriado:

- Altura das linhas.
- Espaçamento entre itens.
- Padding interno da listagem.

### 8.5 Preservar funcionalidades

Não alterar:

- Lista de prefixos autorizados.
- Regras de filtragem.
- Comparação dos primeiros 6 hex.
- Normalização dos EPCs.
- Persistência dos filtros.
- Inclusão de filtros.
- Remoção de filtros.
- Edição de filtros.
- Validações existentes.
- Eventos dos botões.

Não modificar a lógica RF023.

O filtro deverá continuar funcionando
exatamente como antes.

---

## 9. CARD — BACKEND RFID

O card Backend RFID está funcionando
corretamente.

NÃO ALTERAR SEU CONTEÚDO.

Preservar:

- Campos existentes.
- Botões existentes.
- Testes de conexão.
- Configurações da API.
- Persistência.
- Validações.
- Mensagens de status.
- Indicadores relacionados.

Apenas posicionar o card
dentro do novo grid de duas colunas.

Não modificar:

- Endpoints.
- Requisições HTTP.
- Configurações de conexão.
- Integração com Rails.
- Health check.
- Autenticação, se existente.
- Tratamento de respostas.

O conteúdo e o comportamento
desse card deverão permanecer intactos.

---

## 10. PADRONIZAÇÃO VISUAL DOS CARDS

Todos os cards deverão seguir
a identidade visual Corporate Dark
já utilizada no DSV RFID System.

Padronizar:

- Cor de fundo.
- Bordas.
- Arredondamento.
- Padding.
- Espaçamento entre elementos.
- Títulos.
- Tipografia.
- Alinhamento.
- Dimensões dos inputs.
- Estilo dos botões.

Não criar uma nova identidade visual.

Não alterar a paleta de cores
aprovada para o sistema.

Manter as cores funcionais:

    Verde: estados positivos.

    Vermelho: erros e estados negativos.

    Âmbar: alertas e Extra box.

Evitar excesso de elementos decorativos.

Priorizar uma interface limpa,
compacta e corporativa.

---

## 11. COMPORTAMENTO DO GRID

Utilizar duas colunas principais.

Os cards deverão respeitar
a largura disponível.

Requisitos:

- Cards com larguras equilibradas.
- Espaçamento horizontal uniforme.
- Espaçamento vertical uniforme.
- Conteúdo alinhado ao topo.
- Altura individual por conteúdo.
- Sem sobreposição.
- Sem cortes de texto.
- Sem inputs ultrapassando os cards.
- Sem botões parcialmente ocultos.

Não forçar um card pequeno
a ocupar a altura de um card grande.

Evitar grandes áreas vazias.

Se necessário, utilizar:

    RowLayout
        ColumnLayout
        ColumnLayout

Ou outra estrutura QML equivalente,
desde que o resultado visual
mantenha duas colunas.

Não utilizar posicionamentos absolutos
que prejudiquem o redimensionamento.

---

## 12. ROLAGEM DA TELA

A tela Configurações poderá continuar
possuindo rolagem vertical.

Entretanto, o objetivo é reduzir
a necessidade de rolagem excessiva.

Regras:

- Utilizar a altura necessária dos cards.
- Não adicionar margens exageradas.
- Não expandir listas indefinidamente.
- Manter scroll interno no Filtro EPC.
- Evitar scroll horizontal na página.
- Preservar acesso a todos os controles.

A rolagem da página deverá funcionar
normalmente com o mouse.

Não criar regiões de scroll
desnecessárias em outros cards.

---

## 13. RESPONSIVIDADE

A aplicação é utilizada em Windows
e possui uma janela redimensionável.

O layout deverá se adaptar
ao espaço disponível.

Em resoluções desktop:

    Utilizar duas colunas.

Em larguras reduzidas:

    Ajustar dimensões dos componentes.

Caso não exista espaço suficiente
para manter os inputs legíveis,
permitir uma coluna.

Não permitir:

- Campos sobrepostos.
- Botões cortados.
- Textos fora dos cards.
- Scroll horizontal desnecessário.
- Perda de acesso às configurações.

Manter a janela principal
e a navegação existentes.

---

## 14. PRESERVAÇÃO DE ESTADO

A reorganização visual não poderá
alterar os valores configurados.

Ao abrir Configurações:

- Os campos deverão apresentar
  seus valores atuais.

Ao salvar:

- Os valores deverão continuar
  sendo persistidos normalmente.

Ao navegar entre telas:

- Preservar o comportamento existente.

Não recriar serviços desnecessariamente
ao mover componentes QML.

Não duplicar propriedades ou bindings
que possam gerar inconsistências.

Preservar:

- Connections.
- Signals.
- Slots.
- Properties.
- Models.
- Context properties.
- Chamadas Python/QML.

Caso seja necessário mover um componente,
garantir que suas conexões continuem válidas.

---

## 15. RESTRIÇÕES DE IMPLEMENTAÇÃO

ESTE RF NÃO AUTORIZA ALTERAÇÕES
NAS FUNCIONALIDADES DO SISTEMA.

Não modificar:

- Leitor Zebra FX9600.
- Comunicação LLRP.
- Waveshare Modbus RTU.
- Entradas digitais.
- Relés.
- Sensores.
- Temporizadores.
- Fluxo automático RFID.
- Backend Rails.
- Consultas EPC.
- Registros de passagem.
- Filtro de EPC.
- Serviço de bip.
- Serviço de voz.
- Simulador RFID.
- Lógica Start/Stop.

Não alterar arquivos de backend
sem necessidade diretamente relacionada
ao layout.

Não adicionar dependências novas.

Não criar novas funcionalidades.

Não remover funcionalidades existentes.

Não renomear propriedades utilizadas
pela integração Python/QML
sem atualizar todas as referências.

Priorizar alterações exclusivamente
nos arquivos de interface.

---

## 16. TESTES OBRIGATÓRIOS

### Teste 1 — Grid principal

Abrir Configurações.

Confirmar:

- Layout com duas colunas.
- Cards organizados.
- Espaçamentos uniformes.
- Sem sobreposição.
- Sem componentes cortados.

### Teste 2 — Configurações RFID

Confirmar:

- Card exclusivo.
- Todos os campos existentes.
- Valores preservados.
- Botões funcionando.
- Salvar funcionando.
- Testar conexão funcionando.

### Teste 3 — Waveshare

Confirmar:

    Data bits | Paridade

Na mesma linha.

Confirmar:

    Stop bits | Device ID

Na mesma linha.

Verificar:

- Todos os campos preservados.
- Um único card Waveshare.
- Botões funcionando.
- Valores persistidos.
- Nenhuma alteração na comunicação.

### Teste 4 — Doca Estação

Confirmar:

- Card exclusivo.
- Dropdown funcionando.
- Doca selecionada preservada.
- Botão Salvar doca funcionando.

### Teste 5 — Configurações de Áudio

Confirmar:

- Card exclusivo.
- Teste do bip funcionando.
- Teste da voz funcionando.
- Campo de quantidade funcionando.
- Mensagem de voz correta.
- Nenhuma alteração no RF033 ou RF035.

### Teste 6 — Ferramentas de Teste

Confirmar:

- Card exclusivo.
- Botão Simulador presente.
- Modal abre normalmente.
- Simulador funciona normalmente.

### Teste 7 — Filtro EPC

Confirmar:

- Card ocupa uma coluna.
- Fonte menor.
- Listagem compacta.
- Altura limitada.
- Scroll interno funcionando.
- Todos os filtros acessíveis.
- Controles de edição preservados.
- Persistência funcionando.

Testar também com uma quantidade
elevada de filtros.

### Teste 8 — Backend RFID

Confirmar:

- Card preservado.
- Todos os campos existentes.
- Botões funcionando.
- Health check funcionando.
- Nenhuma alteração de comportamento.

### Teste 9 — Redimensionamento

Testar diferentes larguras
da janela principal.

Confirmar:

- Duas colunas em desktop.
- Sem sobreposição.
- Sem cortes.
- Sem scroll horizontal desnecessário.
- Adaptação em janelas estreitas.

### Teste 10 — Persistência

Alterar uma configuração
utilizando o fluxo existente.

Salvar.

Fechar e abrir o aplicativo.

Confirmar que o valor permanece salvo.

### Teste 11 — Regressão

Executar os testes existentes
relacionados a:

- RFID.
- Waveshare.
- Backend.
- Doca.
- Filtro EPC.
- Bip RF033.
- Voz RF035.
- Simulador RF034.

Confirmar ausência de regressões.

---

## 17. CRITÉRIOS DE ACEITE

- [ ] Tela Configurações reorganizada.
- [ ] Grid de duas colunas implementado.
- [ ] Card exclusivo Configurações RFID.
- [ ] Card Waveshare mantido único.
- [ ] Data bits e Paridade lado a lado.
- [ ] Stop bits e Device ID lado a lado.
- [ ] Card exclusivo Doca Estação.
- [ ] Dropdown de doca preservado.
- [ ] Botão Salvar doca preservado.
- [ ] Card exclusivo Configurações de Áudio.
- [ ] Teste do bip preservado.
- [ ] Teste da voz preservado.
- [ ] Card exclusivo Ferramentas de Teste.
- [ ] Botão Simulador movido.
- [ ] Modal Simulador preservado.
- [ ] Filtro EPC com largura reduzida.
- [ ] Filtro EPC com fonte menor.
- [ ] Filtro EPC com altura limitada.
- [ ] Scroll interno do filtro funcionando.
- [ ] Funcionalidades do filtro preservadas.
- [ ] Backend RFID preservado.
- [ ] Cards alinhados corretamente.
- [ ] Espaçamentos padronizados.
- [ ] Tema Corporate Dark preservado.
- [ ] Layout responsivo.
- [ ] Sem componentes sobrepostos.
- [ ] Sem alterações nas regras de negócio.
- [ ] Sem alterações nos serviços.
- [ ] Sem regressões funcionais.

---

## 18. PROCEDIMENTO DO CODEX

Antes de implementar:

1. Ler AGENTS.md.
2. Verificar a branch atual.
3. Executar git status.
4. Identificar a tela Configurações.
5. Identificar os componentes QML existentes.
6. Mapear os cards atuais.
7. Identificar todos os campos e botões.
8. Identificar bindings e conexões Python/QML.
9. Preservar alterações locais.

Durante a implementação:

- Trabalhar prioritariamente na camada QML.
- Reutilizar componentes existentes.
- Reorganizar os cards.
- Implementar o grid de duas colunas.
- Ajustar os campos Waveshare.
- Compactar a listagem Filtro EPC.
- Preservar sinais e bindings.
- Não modificar regras de negócio.
- Não adicionar dependências.
- Não alterar serviços funcionais.

Após implementar:

1. Executar testes disponíveis.
2. Validar o layout completo.
3. Validar os sete cards.
4. Validar os botões existentes.
5. Validar persistência das configurações.
6. Validar redimensionamento.
7. Validar o scroll do Filtro EPC.
8. Executar git diff.
9. Apresentar os arquivos modificados.
10. Informar testes executados e resultados.

Não executar git reset --hard.
Não descartar alterações locais.

Não realizar commit automaticamente.
Não realizar push automaticamente.
Não realizar merge na main.

---

## 19. RESULTADO ESPERADO

A tela Configurações deverá apresentar
uma organização visual mais compacta,
utilizando duas colunas.

Cards esperados:

    1. Configurações RFID

    2. Configurações da Waveshare

    3. Doca Estação

    4. Configurações de Áudio

    5. Ferramentas de Teste

    6. Filtro EPC

    7. Backend RFID

O card Waveshare deverá apresentar:

    Data bits | Paridade

    Stop bits | Device ID

O card Filtro EPC deverá ocupar
menos espaço e possuir uma listagem
compacta com rolagem interna.

Todos os componentes existentes
deverão continuar funcionando
exatamente como antes.

IMPLEMENTAR O RF036.

ALTERAÇÃO EXCLUSIVAMENTE VISUAL.

NÃO MODIFICAR FUNCIONALIDADES.

NÃO ALTERAR REGRAS DE NEGÓCIO.

NÃO ALTERAR SERVIÇOS OU HARDWARE.

PRESERVAR INTEGRALMENTE
O FUNCIONAMENTO ATUAL DO SISTEMA.