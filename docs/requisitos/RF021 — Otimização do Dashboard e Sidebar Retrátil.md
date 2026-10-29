# RF020 — Otimização do Dashboard e Sidebar Retrátil

**Projeto:** RFID System
**Requisito:** RF020
**Categoria:** Interface / UX / UI
**Prioridade:** Alta
**Ambiente:** Windows
**Tecnologia:** Python + PySide6 + Qt Quick/QML
**Referência visual:** Screenshot atual do Dashboard fornecido pelo usuário
**Status:** A implementar

---

# 1. Objetivo

Modernizar a organização da tela principal do software RFID,
priorizando a visualização da tabela de etiquetas e melhorando
a utilização do espaço disponível.

As alterações solicitadas são:

1. Remover o título "Start" do conteúdo principal.
2. Remover o subtítulo "Resumo da sessão atual de leitura".
3. Aumentar significativamente a área ocupada pela tabela de etiquetas.
4. Remover o texto explicativo abaixo dos botões de leitura.
5. Remover o texto "OPERAÇÃO RFID" da parte inferior da sidebar.
6. Implementar uma sidebar expansível e retrátil.
7. Quando recolhida, a sidebar deverá apresentar somente ícones.
8. Adicionar um botão com ícone para expandir/recolher a sidebar.
9. Aproveitar o espaço liberado pela sidebar recolhida para ampliar o conteúdo principal.

IMPORTANTE:

Este requisito é exclusivamente de interface.

Não alterar regras operacionais, comunicação com equipamentos,
consultas ao Backend ou lógica de contabilização RFID.

---

# 2. Contexto atual

A interface foi desenvolvida utilizando:

- PySide6.
- Qt Quick/QML.
- Tema Corporate Dark.
- Componentes visuais reutilizáveis.

A tela principal possui:

- Header com logotipo DSV.
- Indicadores de conexão.
- Sidebar de navegação.
- Cards de contabilização.
- Container de inventário RFID automático.
- Botões Iniciar leitura e Parar leitura.
- Tabela de etiquetas.

Atualmente, parte significativa do espaço vertical é utilizada
por textos explicativos e margens entre componentes.

A tabela de etiquetas é o principal elemento operacional,
mas ocupa uma área relativamente pequena.

O RF020 deverá corrigir essa distribuição.

---

# 3. Estrutura visual esperada

## 3.1 Sidebar expandida

Representação conceitual:

    ┌──────────────────────────────────────────────────────────────┐
    │ DSV                         RFID SYSTEM                      │
    ├──────────────────────────────────────────────────────────────┤
    │ RFID       Internet       Comandos       Sistema            │
    ├───────────────┬──────────────────────────────────────────────┤
    │               │                                              │
    │ [≡]           │ ┌────────────────┐ ┌────────────────┐        │
    │               │ │ EPCs           │ │ Extra box      │        │
    │ [▦] Start     │ │ encontrados    │ │                │        │
    │               │ │       15       │ │       4        │        │
    │ [⚙] Config.   │ └────────────────┘ └────────────────┘        │
    │               │                                              │
    │               │ ┌──────────────────────────────────────────┐ │
    │               │ │ Inventário RFID automático               │ │
    │               │ │                                          │ │
    │               │ │ [Iniciar leitura] [Parar leitura]        │ │
    │               │ │                                          │ │
    │               │ │ Etiquetas lidas                          │ │
    │               │ │ ┌──────────────────────────────────────┐ │ │
    │               │ │ │ Status | Cliente | NF | Volume ...  │ │ │
    │               │ │ ├──────────────────────────────────────┤ │ │
    │               │ │ │                                      │ │ │
    │               │ │ │                                      │ │ │
    │               │ │ │          TABELA RFID                 │ │ │
    │               │ │ │                                      │ │ │
    │               │ │ │                                      │ │ │
    │               │ │ │                                      │ │ │
    │               │ │ └──────────────────────────────────────┘ │ │
    │               │ └──────────────────────────────────────────┘ │
    │               │                                              │
    │ [◐] Tema      │                                              │
    └───────────────┴──────────────────────────────────────────────┘

O desenho é apenas uma referência estrutural.

Preservar a identidade visual atual.

Não redesenhar o software.

---

# 4. RF020.01 — Remover título Start

Na área principal do Dashboard, remover o título:

    Start

Atualmente, esse título aparece acima dos cards de contabilização.

Após a alteração, os cards deverão ocupar a região superior
do conteúdo principal.

IMPORTANTE:

Não remover a opção Start da sidebar.

O item Start deverá continuar existindo no menu de navegação.

Remover exclusivamente o título da página.

---

# 5. RF020.02 — Remover subtítulo

Remover o texto:

    Resumo da sessão atual de leitura.

Esse texto aparece imediatamente abaixo do título Start.

Após sua remoção, eliminar também os espaços e margens
reservados exclusivamente para esse elemento.

Não manter containers vazios.

Não deixar espaçamento excessivo entre o topo do conteúdo
e os cards de contabilização.

---

# 6. RF020.03 — Preservar cards de contabilização

Manter os dois cards existentes:

    EPCs encontrados
    Extra box

Preservar:

- Contadores.
- Fontes de dados.
- Atualizações em tempo real.
- Regras de deduplicação.
- Cores.
- Bordas.
- Tipografia.
- Integração com a Qt Bridge.

Os cards deverão permanecer lado a lado.

Não alterar a lógica do RF019.

O espaço vertical economizado com a remoção dos textos
deverá ser aproveitado principalmente pela tabela RFID.

Não aumentar desnecessariamente a altura dos cards.

---

# 7. RF020.04 — Remover texto explicativo da leitura

No container:

    Inventário RFID automático

Remover o texto:

    Iniciar leitura habilita o modo automático;
    o inventário aguarda DI1.

Remover o componente visual e seu espaçamento.

IMPORTANTE:

A remoção é exclusivamente visual.

O botão Iniciar leitura continuará:

1. Habilitando o modo automático.
2. Aguardando o acionamento do sensor DI1.
3. Iniciando o inventário conforme as regras existentes.

Não modificar o comportamento do botão.

Não iniciar o inventário imediatamente ao clicar em Iniciar leitura.

Não alterar o funcionamento de Parar leitura.

---

# 8. RF020.05 — Ampliar a tabela de etiquetas

## 8.1 Objetivo

A tabela de etiquetas deverá ocupar a maior área possível
do espaço vertical disponível no Dashboard.

Essa tabela é o principal componente operacional do software.

Ela deverá receber prioridade no dimensionamento da interface.

## 8.2 Comportamento esperado

Após a remoção dos textos desnecessários:

- Os cards permanecem na parte superior.
- Os controles de leitura ficam logo abaixo.
- A tabela ocupa a maior parte do espaço restante.
- O container de inventário se adapta ao tamanho da janela.

Não deixar grandes áreas vazias abaixo da tabela.

Não limitar a tabela à altura reduzida atual.

## 8.3 Dimensionamento dinâmico

A tabela deverá crescer e diminuir conforme o tamanho
da janela principal.

Utilizar os mecanismos de layout do Qt Quick/QML.

Preferir recursos como:

    Layout.fillWidth
    Layout.fillHeight
    Layout.minimumHeight
    Layout.preferredHeight

Quando compatíveis com a estrutura atual.

Evitar alturas fixas que impeçam a adaptação.

A tabela deverá ocupar o espaço disponível sem
sobrepor outros componentes.

## 8.4 Rolagem

Quando a quantidade de etiquetas ultrapassar a
área visível:

- Manter o cabeçalho da tabela.
- Permitir rolagem vertical.
- Preservar o alinhamento das colunas.
- Não aumentar indefinidamente a janela.
- Não prejudicar os botões de operação.

## 8.5 Estado vazio

Quando nenhuma etiqueta estiver disponível,
preservar a mensagem:

    Nenhum registro encontrado

A mensagem deverá permanecer centralizada na
área útil da tabela.

Preservar também o texto secundário existente.

## 8.6 Colunas

Manter as colunas:

    Status
    Cliente
    Nota fiscal
    Volume
    Pedido
    Doca

Não alterar:

- Ordem das colunas.
- Conteúdo dos registros.
- Fonte dos dados.
- Regras de atualização.
- Deduplicação.
- Modelo Python da tabela.

Caso a ampliação horizontal permita melhor distribuição,
ajustar somente as larguras visuais das colunas.

Não remover informações.

---

# 9. RF020.06 — Remover texto OPERAÇÃO RFID da sidebar

Na parte inferior da sidebar existe o texto:

    OPERAÇÃO RFID

Remover esse texto.

Eliminar também o espaçamento exclusivo desse título.

IMPORTANTE:

O texto "OPERAÇÃO RFID" localizado no header superior,
caso exista como elemento independente, não faz parte
desta alteração.

Remover somente o texto localizado na sidebar.

Preservar os demais componentes do header.

---

# 10. RF020.07 — Implementar sidebar retrátil

## 10.1 Objetivo

Permitir que o usuário alterne entre dois estados:

    EXPANDIDA
    RECOLHIDA

A sidebar deverá continuar funcional em ambos os estados.

## 10.2 Estado expandido

Quando expandida, apresentar:

- Ícones de navegação.
- Textos dos menus.
- Destaque do menu selecionado.
- Botão de recolhimento.
- Configuração de tema.
- Rodapé existente, quando aplicável.

Exemplo:

    ┌─────────────────────────┐
    │                     [<] │
    │                         │
    │ [▦] Start               │
    │                         │
    │ [⚙] Configurações       │
    │                         │
    │                         │
    │ [◐] Tema                │
    └─────────────────────────┘

A largura expandida deverá ser próxima à largura
atualmente utilizada pela aplicação.

Evitar alterações desnecessárias na identidade visual.

## 10.3 Estado recolhido

Quando recolhida, apresentar somente ícones.

Exemplo:

    ┌───────┐
    │  [>]  │
    │       │
    │  [▦]  │
    │       │
    │  [⚙]  │
    │       │
    │       │
    │  [◐]  │
    └───────┘

Não apresentar textos dos menus.

Não apresentar labels.

Não apresentar descrições.

Não apresentar o rodapé textual.

Manter os ícones centralizados horizontalmente.

## 10.4 Largura da sidebar

Valores sugeridos:

    Expandida: aproximadamente 250 px
    Recolhida: aproximadamente 72 px

Esses valores são referências.

Ajustar conforme o design atual e o comportamento
real dos componentes QML.

Não utilizar uma largura que corte os ícones.

Não utilizar uma largura expandida excessiva.

## 10.5 Aproveitamento do espaço

Ao recolher a sidebar, o conteúdo principal deverá
expandir automaticamente para ocupar o espaço liberado.

Não deixar uma faixa vazia correspondente à largura
original da sidebar.

Ao expandir novamente, o conteúdo principal deverá
se ajustar à nova largura disponível.

Os cards e a tabela deverão acompanhar essa mudança.

---

# 11. RF020.08 — Botão de expansão/recolhimento

Adicionar um botão com ícone na região superior da sidebar.

Esse botão deverá alternar entre:

    Expandir sidebar
    Recolher sidebar

## 11.1 Ícone

Utilizar um ícone compatível com o design atual.

Sugestões:

- Chevron.
- Menu lateral.
- Panel left open/close.

Preferir os recursos de ícones já utilizados no projeto.

Não adicionar bibliotecas externas apenas para esse botão.

## 11.2 Comportamento

Sidebar expandida:

    Clique no botão
          |
          v
    Sidebar recolhida

Sidebar recolhida:

    Clique no botão
          |
          v
    Sidebar expandida

O botão deverá permanecer visível e acessível
nos dois estados.

## 11.3 Aparência

O botão deverá:

- Seguir a paleta Corporate Dark.
- Possuir estado hover.
- Possuir estado pressionado.
- Possuir área de clique adequada.
- Apresentar indicação visual de sua função.

Não utilizar texto permanente ao lado do botão
quando a sidebar estiver recolhida.

## 11.4 Tooltip

Ao posicionar o mouse sobre o botão, apresentar:

    Recolher menu

ou:

    Expandir menu

Conforme o estado atual.

---

# 12. RF020.09 — Navegação com sidebar recolhida

Os itens existentes deverão continuar funcionando:

    Start
    Configurações

## 12.1 Estado expandido

Apresentar:

    Ícone + Texto

## 12.2 Estado recolhido

Apresentar:

    Somente ícone

## 12.3 Navegação

Ao clicar em um ícone:

- Abrir a página correspondente.
- Preservar o estado da sidebar.
- Atualizar o destaque do menu ativo.
- Não reinicializar serviços operacionais.
- Não recriar desnecessariamente a sessão RFID.

## 12.4 Tooltips

Quando recolhida:

    Ícone Start -> Tooltip "Start"

    Ícone Configurações -> Tooltip "Configurações"

O usuário deverá conseguir identificar a função
de cada ícone.

## 12.5 Destaque visual

Preservar a indicação do menu selecionado.

Exemplo:

    Start selecionado

O ícone Start deverá continuar destacado mesmo
com a sidebar recolhida.

---

# 13. RF020.10 — Configuração de tema

Atualmente, a sidebar possui o seletor:

    Tema
    Corporate Dark

Essa funcionalidade deverá ser preservada.

## 13.1 Sidebar expandida

Manter o seletor de tema atual.

Preservar os temas existentes e a lógica de seleção.

## 13.2 Sidebar recolhida

Ocultar o texto e o seletor expandido.

Apresentar somente um ícone representando a
configuração de tema.

Ao clicar no ícone, permitir acessar a seleção
de tema sem comprometer o layout.

Solução recomendada:

    Ícone de tema
         |
         v
    Popup compacto
         |
         v
    Seleção do tema

Reutilizar o seletor ou o mecanismo de configuração
já existente.

Não duplicar a lógica de gerenciamento de temas.

Não perder a configuração atual ao recolher a sidebar.

---

# 14. RF020.11 — Comportamento responsivo

A interface deverá funcionar corretamente em diferentes
tamanhos de janela.

Validar especialmente:

- Janela maximizada.
- Janela restaurada.
- Resolução Full HD.
- Resoluções menores suportadas pelo projeto.
- Sidebar expandida.
- Sidebar recolhida.

## Regras

1. Não sobrepor componentes.
2. Não cortar os botões de leitura.
3. Não cortar os indicadores superiores.
4. Não ocultar colunas sem possibilidade de acesso.
5. Não permitir que a tabela ultrapasse seu container.
6. Não deixar áreas vazias desnecessárias.
7. Não deformar os cards.
8. Não criar barras de rolagem desnecessárias na página inteira.

Quando a largura disponível for insuficiente para
todas as colunas, preservar acesso aos dados por
rolagem horizontal da tabela, se necessário.

A rolagem horizontal não deverá afetar os botões
nem os cards de contabilização.

---

# 15. RF020.12 — Transição visual da sidebar

A expansão e o recolhimento deverão ocorrer
de maneira visualmente suave.

Utilizar animações nativas do QML quando apropriado.

Exemplo conceitual:

    Sidebar expandida
          |
          v
    Clique
          |
          v
    Transição de largura
          |
          v
    Sidebar recolhida

A animação deverá ser curta e discreta.

Não utilizar efeitos excessivos.

Não bloquear a thread principal.

Não interferir nas atualizações da tabela.

Não interromper a leitura RFID durante a animação.

Se a animação apresentar problemas de layout ou
desempenho, priorizar uma transição estável.

---

# 16. RF020.13 — Preservação da interface existente

Manter integralmente:

## Header

- Logotipo DSV.
- Nome RFID SYSTEM.
- Identidade visual.
- Organização geral.

## Indicadores

Manter exclusivamente:

    RFID
    Internet
    Comandos
    Sistema

Não adicionar novamente:

    Base de dados
    Sincronização

## Dashboard

Preservar:

- EPCs encontrados.
- Extra box.
- Inventário RFID automático.
- Iniciar leitura.
- Parar leitura.
- Status operacional.
- Tabela de etiquetas.

## Configurações

Preservar:

- Configuração do Zebra.
- Configuração da Waveshare.
- Configuração do Backend.
- Testes de comunicação.
- Demais funcionalidades existentes.

---

# 17. RF020.14 — Restrições operacionais

O RF020 não poderá modificar:

- Zebra FX9600.
- Comunicação LLRP.
- Waveshare Modbus RTU Relay.
- Comunicação serial.
- Sensores DI1 e DI2.
- Relés CH1, CH2 e CH3.
- Timer de 60 segundos.
- Máquina de estados.
- Lógica Start/Stop.
- Backend Rails.
- PostgreSQL.
- Endpoint GET de EPC.
- Endpoint POST de passagem.
- Deduplicação de EPCs.
- Classificação Extra box.
- Contadores da sessão.
- Monitoramento de conectividade.

A sidebar e os componentes visuais não deverão
executar regras operacionais.

Toda a lógica de equipamentos continuará
na camada Python existente.

---

# 18. Arquitetura de implementação

Preservar a arquitetura estabelecida no RF018.

    ┌────────────────────────────────────┐
    │              Python                │
    │                                    │
    │ RFID Service                       │
    │ Waveshare Service                  │
    │ Backend Client                     │
    │ Application Controller             │
    └─────────────────┬──────────────────┘
                      |
                      v
    ┌────────────────────────────────────┐
    │             Qt Bridge              │
    │                                    │
    │ Signals / Slots / Properties       │
    └─────────────────┬──────────────────┘
                      |
                      v
    ┌────────────────────────────────────┐
    │               QML                  │
    │                                    │
    │ Header                             │
    │ Status Indicators                  │
    │ Sidebar expansível                 │
    │ Dashboard                          │
    │ Cards                              │
    │ Inventário RFID                    │
    │ Tabela expandida                   │
    └────────────────────────────────────┘

A implementação do RF020 deverá ocorrer
principalmente na camada QML.

Não modificar serviços Python sem necessidade
técnica comprovada.

---

# 19. Análise obrigatória antes da implementação

Antes de modificar o código, o Codex deverá:

1. Ler AGENTS.md.
2. Identificar a branch atual.
3. Verificar o estado do Git.
4. Localizar o componente principal QML.
5. Localizar o componente Sidebar.
6. Localizar a tela Start.
7. Localizar os cards de contabilização.
8. Localizar o container de inventário.
9. Localizar o componente da tabela.
10. Localizar o seletor de tema.
11. Identificar os layouts e bindings utilizados.
12. Identificar os testes existentes.

Verificar se a sidebar já possui propriedades
que permitam controlar sua largura.

Verificar se o componente de tabela já utiliza
dimensionamento dinâmico.

Reutilizar os componentes existentes.

Não criar uma segunda implementação da sidebar.

Não substituir a arquitetura QML atual.

---

# 20. Estratégia de implementação

## Etapa 1 — Limpeza visual

Remover:

- Título Start do conteúdo principal.
- Subtítulo da sessão.
- Texto explicativo dos botões.
- Texto OPERAÇÃO RFID da sidebar.

Eliminar os espaços associados.

## Etapa 2 — Reorganização vertical

Aproximar os cards da região superior.

Compactar os espaços entre:

- Cards.
- Container de inventário.
- Botões.
- Tabela.

Preservar espaçamento suficiente para leitura
e utilização confortável da interface.

## Etapa 3 — Ampliação da tabela

Modificar o layout para que a tabela ocupe
a maior parte da altura disponível.

Implementar dimensionamento dinâmico.

Validar rolagem vertical e horizontal.

## Etapa 4 — Sidebar retrátil

Implementar:

- Estado expandido.
- Estado recolhido.
- Controle de largura.
- Botão de alternância.
- Exibição condicional dos textos.
- Alinhamento dos ícones.

## Etapa 5 — Navegação

Validar Start e Configurações nos dois estados.

Preservar o destaque do item ativo.

Adicionar tooltips.

## Etapa 6 — Tema

Adaptar o seletor de tema para funcionar
também com a sidebar recolhida.

## Etapa 7 — Testes

Executar testes visuais, funcionais
e de regressão.

---

# 21. Testes obrigatórios

## Teste 01 — Remoção do título

Abrir o Dashboard.

Resultado esperado:

    O título Start não aparece no conteúdo principal.

O menu Start continua disponível na sidebar.

## Teste 02 — Remoção do subtítulo

Resultado esperado:

    O texto "Resumo da sessão atual de leitura"
    não aparece.

## Teste 03 — Remoção da instrução

Resultado esperado:

    O texto explicativo abaixo dos botões
    não aparece.

Os botões continuam funcionando.

## Teste 04 — Sidebar expandida

Resultado esperado:

    Ícones e textos visíveis.

## Teste 05 — Sidebar recolhida

Resultado esperado:

    Somente ícones visíveis.

## Teste 06 — Expansão

Clicar no botão de expansão.

Resultado esperado:

    Sidebar retorna ao estado expandido.

## Teste 07 — Navegação

Com sidebar recolhida:

    Clicar em Configurações.

Resultado esperado:

    Página Configurações aberta.

A sidebar permanece recolhida.

## Teste 08 — Tooltips

Posicionar o mouse sobre os ícones.

Resultado esperado:

    Nome da funcionalidade exibido.

## Teste 09 — Tema

Com sidebar recolhida:

    Acessar seleção de tema.

Resultado esperado:

    Seleção funcional.

## Teste 10 — Ampliação da tabela

Abrir o Dashboard com janela maximizada.

Resultado esperado:

    Tabela ocupa a maior parte da área
    vertical disponível abaixo dos controles.

## Teste 11 — Redimensionamento

Reduzir e aumentar a janela.

Resultado esperado:

    Layout se adapta sem sobreposição.

## Teste 12 — Recolhimento e conteúdo

Recolher a sidebar.

Resultado esperado:

    Dashboard utiliza o espaço horizontal liberado.

## Teste 13 — Dados RFID

Simular registros na tabela.

Resultado esperado:

    Colunas e dados preservados.

## Teste 14 — Contadores

Simular atualização de:

    EPCs encontrados
    Extra box

Resultado esperado:

    Ambos continuam atualizando corretamente.

## Teste 15 — Fluxo operacional

Validar que a alteração visual não afeta:

- Iniciar leitura.
- Parar leitura.
- DI1.
- DI2.
- Timer.
- CH1.
- CH2.
- CH3.

## Teste 16 — Troca de páginas durante leitura

Com uma sessão RFID ativa, quando for seguro
executar o cenário em ambiente simulado:

    Recolher sidebar.
    Expandir sidebar.
    Navegar entre páginas.

Resultado esperado:

    Nenhuma alteração indevida no estado operacional.
    Nenhuma reinicialização da sessão.
    Nenhuma perda de registros.

---

# 22. Critérios de aceite

- [ ] Título Start removido do conteúdo principal.
- [ ] Subtítulo da sessão removido.
- [ ] Texto explicativo dos botões removido.
- [ ] Texto OPERAÇÃO RFID removido da sidebar.
- [ ] Cards EPCs encontrados e Extra box preservados.
- [ ] Cards posicionados próximos ao topo.
- [ ] Tabela significativamente ampliada.
- [ ] Tabela utiliza dimensionamento dinâmico.
- [ ] Rolagem vertical funcional.
- [ ] Colunas preservadas.
- [ ] Sidebar possui estado expandido.
- [ ] Sidebar possui estado recolhido.
- [ ] Botão de expansão/recolhimento implementado.
- [ ] Sidebar recolhida apresenta somente ícones.
- [ ] Tooltips implementados.
- [ ] Navegação funcional nos dois estados.
- [ ] Menu ativo continua destacado.
- [ ] Seletor de tema permanece acessível.
- [ ] Conteúdo principal expande ao recolher a sidebar.
- [ ] Interface funciona com janela maximizada.
- [ ] Interface funciona com janela restaurada.
- [ ] Identidade visual DSV preservada.
- [ ] Quatro indicadores de conexão preservados.
- [ ] Contadores RFID preservados.
- [ ] Regras operacionais preservadas.
- [ ] Testes automatizados aprovados.

---

# 23. Fora do escopo

Não implementar:

- Novo dashboard.
- Novos indicadores.
- Novos gráficos.
- Novos cards.
- Novas colunas.
- Novos endpoints.
- Alterações no Backend.
- Alterações no PostgreSQL.
- Alterações no fluxo RFID.
- Alterações na Waveshare.
- Alterações nos sensores.
- Alterações no timer.
- Alterações nos relés.
- Nova biblioteca gráfica.
- Migração de QML para outra tecnologia.
- Refatoração ampla do projeto.

---

# 24. Relatório final obrigatório

Ao concluir, apresentar:

1. Branch utilizada.
2. Arquivos modificados.
3. Componentes QML alterados.
4. Textos removidos.
5. Alterações no layout da tabela.
6. Implementação da sidebar retrátil.
7. Funcionamento do botão de expansão.
8. Comportamento do seletor de tema.
9. Testes executados.
10. Resultados dos testes.
11. Verificações de regressão.
12. Pendências identificadas.

Informar explicitamente se algum serviço Python
precisou ser modificado e justificar a necessidade.

---

# 25. Definição de pronto

O RF020 estará concluído quando:

1. O Dashboard estiver visualmente mais compacto.
2. A tabela de etiquetas ocupar uma área maior.
3. Os textos desnecessários tiverem sido removidos.
4. A sidebar puder ser expandida e recolhida.
5. A sidebar recolhida apresentar somente ícones.
6. O conteúdo principal aproveitar o espaço liberado.
7. Todas as funcionalidades RFID permanecerem operacionais.

A interface deverá manter a identidade visual
corporativa DSV e a arquitetura PySide6 + QML.

**Implementar o RF020 completo, priorizando a tabela RFID
e a utilização eficiente do espaço, sem modificar as
regras operacionais existentes.**