# RF031 — Reorganização do Layout, Tela Status e Ícone Windows

Projeto: DSV RFID System
Requisito: RF031
Categoria: Interface / Navegação / Empacotamento
Tecnologia: Python + PySide6/QML
Sistema operacional de destino: Windows
Prioridade: Média

---

## 1. OBJETIVO

Reorganizar a interface do DSV RFID System,
preservando integralmente a lógica operacional.

As alterações são:

1. Remover a barra horizontal de status da tela Start.
2. Criar uma nova página chamada "Status".
3. Mover os quatro indicadores para essa página.
4. Adicionar a opção Status à sidebar.
5. Mover o botão Iniciar/Parar leitura para o
   cabeçalho superior da aplicação.
6. Reposicionar os cards de contadores.
7. Preservar a tabela de inventário.
8. Incorporar um ícone personalizado ao
   executável Windows.

IMPORTANTE:

O RF031 é principalmente uma alteração de layout.

Não modificar as regras de funcionamento do RFID.

---

## 2. ANÁLISE INICIAL

Antes de implementar:

1. Ler AGENTS.md.
2. Identificar a branch atual.
3. Executar git status.
4. Preservar alterações locais existentes.
5. Identificar a estrutura QML atual.
6. Localizar o cabeçalho superior.
7. Localizar a barra horizontal de status.
8. Localizar a sidebar.
9. Localizar o botão dinâmico Start/Stop.
10. Localizar o modelo de indicadores.
11. Identificar o mecanismo de navegação.
12. Identificar os scripts de build Windows.

Arquivos e componentes relevantes podem incluir:

- Main.qml
- StartPage.qml
- SettingsPage.qml
- Componentes compartilhados
- Qt Bridge
- application.py
- tools/build_windows.py
- tools/verify_windows.py

Verificar os caminhos reais antes de modificar.

Não criar componentes duplicados desnecessários.

---

## 3. REMOVER A BARRA HORIZONTAL DE STATUS

Atualmente existe uma barra horizontal
abaixo do cabeçalho principal contendo:

- RFID
- Internet
- Comandos
- Sistema
- Botão Iniciar/Parar leitura

Essa barra deverá ser removida do layout.

ATENÇÃO:

Remover somente o componente visual
e seu espaço reservado na tela.

Não remover:

- Serviços de monitoramento.
- Indicadores internos.
- Atualização dos estados.
- Qt Bridge.
- Comunicação com hardware.
- Verificações de conectividade.
- Comandos de Start/Stop.

A remoção não deverá interromper
o monitoramento dos equipamentos.

---

## 4. NOVA PÁGINA STATUS

Criar uma página dedicada ao monitoramento
dos componentes do sistema.

Nome exibido na navegação:

    Status

Título principal da página:

    Status sistema

A página deverá apresentar os quatro
indicadores já existentes:

1. RFID
2. Internet
3. Comandos
4. Sistema

### 4.1 RFID

Exibir o estado real do leitor Zebra FX9600.

Preservar os estados e textos existentes,
incluindo situações de:

- Verificando.
- Conectado.
- Desconectado.
- Erro, quando aplicável.

### 4.2 Internet

Exibir o estado real de conectividade
já utilizado pelo sistema.

Não criar uma nova lógica de verificação.

### 4.3 Comandos

Exibir o estado real da comunicação
com a placa Waveshare.

Preservar a interpretação atual
de conexão e desconexão.

### 4.4 Sistema

Exibir o estado real do serviço de backend
conforme a implementação existente.

Não alterar endpoints ou critérios de health.

---

## 5. COMPORTAMENTO DOS INDICADORES

REGRA OBRIGATÓRIA:

A nova página Status deverá utilizar
exatamente a mesma fonte de dados
da barra horizontal atual.

Não criar indicadores simulados.

Não utilizar valores estáticos.

Não criar monitoramento paralelo.

Não duplicar conexões com os equipamentos.

Não criar novas requisições HTTP
apenas para atualizar a interface.

Reutilizar:

- Estados Python existentes.
- Qt Bridge.
- Signals.
- Properties.
- Modelos de status existentes.

Os indicadores deverão continuar
atualizando automaticamente.

A navegação entre páginas não deverá:

- Reiniciar conexões.
- Desconectar equipamentos.
- Reiniciar o monitoramento.
- Limpar estados.
- Criar verificações duplicadas.

---

## 6. LAYOUT DA PÁGINA STATUS

Utilizar o tema Corporate Dark existente.

Apresentar:

    Status sistema

    RFID
    [Indicador e estado atual]

    Internet
    [Indicador e estado atual]

    Comandos
    [Indicador e estado atual]

    Sistema
    [Indicador e estado atual]

A organização visual poderá utilizar
cards responsivos, seguindo os componentes
e padrões já utilizados pelo projeto.

Preservar a semântica das cores:

- Verde: condição positiva.
- Vermelho: desconectado ou erro.
- Amarelo: verificando ou aguardando,
  conforme o comportamento atual.

Não alterar as cores dos estados existentes.

Não adicionar novos controles operacionais
à página Status.

A página terá função de monitoramento.

---

## 7. ADICIONAR STATUS À SIDEBAR

Atualmente a sidebar possui:

- Start
- Configurações

Adicionar:

- Status

Ordem desejada:

1. Start
2. Status
3. Configurações

A opção Status deverá possuir um ícone
adequado ao monitoramento do sistema.

Sugestão:

- Activity
- Monitor
- Gauge

Utilizar preferencialmente o conjunto
de ícones já empregado na interface.

Não adicionar biblioteca de ícones
sem necessidade.

### 7.1 Navegação

Ao clicar em Status:

- Abrir a nova página Status.
- Destacar o item selecionado.
- Exibir os quatro indicadores.
- Preservar o estado operacional.

Ao clicar em Start:

- Retornar ao dashboard.
- Preservar a sessão RFID.
- Preservar contadores e registros.

Ao clicar em Configurações:

- Manter o funcionamento atual.

### 7.2 Sidebar recolhida

Preservar o recurso "Recolher menu".

Quando recolhida:

- O ícone Status deverá continuar disponível.
- A navegação deverá continuar funcionando.
- O layout não deverá apresentar sobreposições.

---

## 8. MOVER O BOTÃO INICIAR/PARAR LEITURA

Atualmente, o cabeçalho superior contém:

- Logo DSV.
- Texto RFID SYSTEM.
- Texto OPERAÇÃO RFID no lado direito.

Remover somente o texto:

    OPERAÇÃO RFID

No lugar dele, adicionar o botão dinâmico:

    Iniciar leitura / Parar leitura

Esse botão já existe no sistema.

Não criar uma nova lógica de Start/Stop.

Reutilizar o comportamento implementado
no RF027.

---

## 9. COMPORTAMENTO DO BOTÃO

### 9.1 Modo automático desativado

Exibir:

    Iniciar leitura

Utilizar:

- Ícone Play.
- Aparência verde.
- Estado habilitado ou desabilitado
  conforme os pré-requisitos atuais.

### 9.2 Modo automático ativado

Exibir:

    Parar leitura

Utilizar:

- Ícone Stop.
- Aparência vermelha.

### 9.3 Regras obrigatórias

Preservar integralmente:

- Habilitação do modo automático.
- Validação dos pré-requisitos.
- Comunicação com Zebra.
- Comunicação Waveshare.
- Estados DI1 e DI2.
- Inventário de até 60 segundos.
- Encerramento por DI2.
- Encerramento por timeout.
- Comportamento dos relés.
- Tratamento de erros.

IMPORTANTE:

Clicar em Iniciar leitura continua apenas
habilitando o modo automático.

Não iniciar imediatamente o inventário RFID.

A leitura continua dependendo do sensor DI1.

### 9.4 Estado real

O botão deverá refletir o estado real
fornecido pelo backend Python/Qt Bridge.

Não utilizar um estado visual independente
que possa ficar divergente.

Preservar a possibilidade de interromper
o modo automático quando ele já estiver ativo,
inclusive nas situações de falha previstas
pela implementação atual.

---

## 10. BOTÃO NO CABEÇALHO SUPERIOR

O botão deverá ficar no canto superior direito,
ocupando a posição do texto OPERAÇÃO RFID.

Layout esperado:

[LOGO DSV] RFID SYSTEM       [Iniciar leitura]

Ou:

[LOGO DSV] RFID SYSTEM       [Parar leitura]

Requisitos:

1. Preservar o logo DSV.
2. Preservar o título RFID SYSTEM.
3. Preservar a altura visual do cabeçalho,
   salvo ajuste mínimo necessário.
4. Manter o botão alinhado verticalmente.
5. Preservar o tema Corporate Dark.
6. Preservar a responsividade.
7. Não permitir sobreposição com o título.
8. Manter o botão visível nas páginas
   Start, Status e Configurações.

Não duplicar o botão em outras regiões.

O cabeçalho deverá continuar acessível
durante a navegação.

---

## 11. REPOSICIONAR OS CARDS DE CONTADORES

Atualmente existem dois cards:

- EPCs encontrados.
- Extra box.

Eles ficam abaixo da barra horizontal
de status.

Como essa barra será removida,
os cards deverão subir e ocupar
o espaço vertical liberado.

Resultado esperado:

CABEÇALHO SUPERIOR
    Logo DSV
    RFID SYSTEM
    Botão Start/Stop

CONTEÚDO PRINCIPAL
    Sidebar

    EPCs encontrados | Extra box

    Inventário RFID automático
    Tabela de etiquetas lidas

Requisitos:

- Não deixar espaço vazio onde estava
  a barra de status.
- Preservar o alinhamento dos cards.
- Preservar os valores e as cores.
- Preservar o comportamento responsivo.
- Preservar a largura relativa dos cards.
- Preservar a integração com a sessão RFID.

Não alterar a lógica dos contadores.

---

## 12. TABELA DE INVENTÁRIO

A tabela deverá continuar abaixo dos cards.

Preservar o RF030.

A ordem das colunas é obrigatória:

1. Status
2. Cliente
3. Nota Fiscal
4. Volume
5. Pedido
6. Doca
7. Dealer

Mapeamento:

Status      -> regra atual
Cliente     -> data.fornecedor
Nota Fiscal -> data.notafiscal
Volume      -> data.volume
Pedido      -> data.pedido
Doca        -> data.doca
Dealer      -> data.destinatario

Não modificar esses campos.

Não adicionar novamente a coluna Tag.

Não modificar:

- Classificação Extra box.
- Cores das linhas.
- Deduplicação.
- Contadores.
- Atualização da tabela.
- Rolagem.
- Estado de tabela vazia.

A tabela poderá aproveitar o espaço
vertical disponível após a remoção
da barra de status.

Preservar o dimensionamento responsivo.

---

## 13. ESTADO DO INVENTÁRIO

O painel "Inventário RFID automático"
atualmente apresenta seu estado operacional,
por exemplo:

    Sistema indisponível

Esse indicador pertence ao próprio
painel de inventário.

Preservar sua lógica e apresentação.

Não confundir esse estado com os quatro
indicadores globais movidos para Status.

O RF031 deverá remover somente a barra
horizontal global de status.

---

## 14. ÍCONE DO EXECUTÁVEL WINDOWS

O usuário forneceu uma imagem personalizada
para representar o DSV RFID System.

Essa imagem deverá ser utilizada como
ícone do executável Windows.

IMPORTANTE:

O objetivo é modificar o ícone exibido:

- No arquivo DSV-RFID.exe.
- Na área de trabalho, quando criado um atalho.
- No Explorador de Arquivos do Windows.

Não substituir o logo DSV do cabeçalho
da aplicação.

Não utilizar a imagem como ícone
da nova opção Status da sidebar.

São recursos diferentes.

---

## 15. ARQUIVOS DO ÍCONE

O usuário disponibilizará os seguintes
arquivos no repositório:

    packaging/assets/dsv_rfid_icon.png

    packaging/assets/dsv_rfid.ico

O arquivo ICO foi gerado a partir
da imagem fornecida pelo usuário.

Contém resoluções:

- 16x16
- 24x24
- 32x32
- 48x48
- 64x64
- 128x128
- 256x256

Preservar a arte original.

Não redesenhar o logo.

Não substituir as cores.

Não gerar outra identidade visual.

Se os arquivos não estiverem presentes,
informar ao usuário antes de executar
o build, em vez de utilizar um ícone genérico.

---

## 16. INTEGRAR ÍCONE AO PYINSTALLER

O projeto utiliza:

    tools/build_windows.py

E gera:

    DSV-RFID.exe

Modificar o processo existente para
incorporar o ícone:

    packaging/assets/dsv_rfid.ico

Utilizar o mecanismo de ícones do PyInstaller,
por exemplo o parâmetro --icon ou a
configuração equivalente no arquivo .spec.

Verificar a implementação real antes
de escolher o ponto de integração.

Não criar um novo sistema de build.

Não substituir o PyInstaller.

Não modificar o modo --onedir.

O ícone deverá ser incorporado ao
recurso do executável Windows.

Não basta copiar o arquivo ICO
para a pasta dist.

O executável deverá apresentar
o ícone personalizado no Windows.

---

## 17. COMPATIBILIDADE COM GITHUB ACTIONS

O RF029 já implementou o build Windows
via GitHub Actions.

Preservar:

    .github/workflows/build-windows.yml

O build deverá continuar funcionando:

1. Localmente no Windows.
2. No runner Windows do GitHub Actions.

O arquivo ICO deverá ser versionado
junto ao código-fonte.

O GitHub Actions deverá utilizar o
mesmo ícone do build local.

Não adicionar dependência de caminhos
absolutos específicos de uma máquina.

Utilizar caminhos relativos à raiz
do projeto ou resolvidos pelo script.

Não criar secrets ou tokens.

Não alterar as permissões do workflow.

---

## 18. VALIDAÇÃO DO ÍCONE

Validar:

1. Arquivo ICO presente.
2. Arquivo ICO válido.
3. Resoluções suportadas.
4. Integração com PyInstaller.
5. Build Windows executado.
6. Ícone incorporado ao executável.
7. Ícone exibido no Explorador do Windows.
8. Atalho na área de trabalho utilizando
   o ícone do executável.

A verificação visual dos itens 7 e 8
deverá ser realizada em um Windows real.

Se o Windows continuar exibindo o ícone
antigo devido ao cache, documentar
como atualizar o atalho ou o cache
sem modificar o software.

Não considerar apenas a presença
do arquivo .ico como validação completa.

---

## 19. TESTES DA NOVA PÁGINA STATUS

Criar ou atualizar testes para confirmar:

1. A opção Status existe na sidebar.
2. A página Status abre corretamente.
3. O título "Status sistema" aparece.
4. Os quatro indicadores estão presentes.
5. Os estados são obtidos da fonte real.
6. As atualizações continuam funcionando.
7. As cores são preservadas.
8. A navegação não reinicia conexões.
9. A sidebar recolhida funciona.
10. Não existem indicadores globais
    duplicados na tela Start.

Utilizar simulações e mocks
quando não houver hardware disponível.

---

## 20. TESTES DO BOTÃO START/STOP

Validar:

1. O botão aparece no cabeçalho superior.
2. O texto OPERAÇÃO RFID foi removido.
3. O botão apresenta Iniciar leitura
   quando o modo automático está desativado.
4. O botão apresenta Parar leitura
   quando o modo automático está ativo.
5. O ícone muda corretamente.
6. As cores são preservadas.
7. O estado habilitado/desabilitado
   respeita a lógica atual.
8. O botão funciona em todas as páginas.
9. Navegar entre páginas não altera
   o modo automático.
10. Não existem botões duplicados.
11. Iniciar não dispara inventário imediato.
12. Parar continua executando o comando
    operacional existente.

Não modificar os serviços de controle.

---

## 21. TESTES DE LAYOUT

Validar visualmente:

- Cabeçalho superior.
- Botão alinhado à direita.
- Sidebar expandida.
- Sidebar recolhida.
- Página Start.
- Página Status.
- Página Configurações.
- Cards reposicionados.
- Tabela com sete colunas.
- Estado de tabela vazia.
- Registros normais.
- Registros Extra box.

Executar testes em diferentes
tamanhos de janela.

Verificar que não existem:

- Sobreposições.
- Componentes cortados.
- Espaços vazios desnecessários.
- Botões duplicados.
- Perda de navegação.
- Truncamento indevido de dados.

---

## 22. PRESERVAR REGRAS OPERACIONAIS

Não modificar:

- Zebra FX9600.
- Protocolo LLRP.
- Múltiplas antenas.
- Filtro de EPC.
- Waveshare.
- Sensores DI1 e DI2.
- Relés CH1, CH2 e CH3.
- Timer de 60 segundos.
- Máquina de estados.
- Backend Rails.
- Consultas GET.
- Registro POST.
- Deduplicação.
- Extra box.
- Banco de dados.
- Configurações persistentes.
- Logs.
- Segurança do GitHub Actions.

O RF031 deverá preservar o
funcionamento operacional atual.

---
## 22.1 Taamnho da fonte das letras da tabela. 
- Diminua o tamanho da fonte da tabela, apenas do resultado e nao dos titulos das colunas.
- faça caber uma lista com 10 linhas.
## 23. CRITÉRIOS DE ACEITE

- [ ] Barra horizontal de status removida.
- [ ] Nova página Status criada.
- [ ] Sidebar possui opção Status com ícone.
- [ ] Título "Status sistema" exibido.
- [ ] Indicador RFID preservado.
- [ ] Indicador Internet preservado.
- [ ] Indicador Comandos preservado.
- [ ] Indicador Sistema preservado.
- [ ] Estados atualizados em tempo real.
- [ ] Sem monitoramento duplicado.
- [ ] Botão Start/Stop movido para o cabeçalho.
- [ ] Texto OPERAÇÃO RFID removido.
- [ ] Lógica Start/Stop preservada.
- [ ] Cards reposicionados para cima.
- [ ] Espaço da barra antiga eliminado.
- [ ] Tabela RF030 preservada.
- [ ] Sidebar recolhida funcionando.
- [ ] Logo do cabeçalho preservado.
- [ ] Ícone Windows personalizado integrado.
- [ ] PyInstaller utiliza o arquivo ICO.
- [ ] Build local Windows preservado.
- [ ] GitHub Actions preservado.
- [ ] Testes automatizados aprovados.
- [ ] Nenhuma regressão operacional.

---

## 24. RELATÓRIO FINAL

Ao concluir, apresentar:

1. Branch utilizada.
2. Arquivos criados.
3. Arquivos modificados.
4. Componentes QML alterados.
5. Estrutura final da sidebar.
6. Estrutura da página Status.
7. Origem dos estados dos indicadores.
8. Localização final do botão Start/Stop.
9. Confirmação da preservação da lógica.
10. Ajustes de posicionamento dos cards.
11. Situação da tabela RF030.
12. Caminho do arquivo ICO.
13. Alterações no PyInstaller.
14. Impacto no GitHub Actions.
15. Testes executados.
16. Resultado dos testes.
17. Validações visuais realizadas.
18. Pendências de teste no Windows real.
19. Possíveis problemas identificados.

Não realizar commit automaticamente.
Não realizar push automaticamente.
Não realizar merge na main.

Não executar git reset --hard.
Não descartar alterações locais.

---

## 25. RESULTADO ESPERADO

A aplicação deverá apresentar:

CABEÇALHO SUPERIOR
    Logo DSV
    RFID SYSTEM
    Iniciar leitura / Parar leitura

SIDEBAR
    Start
    Status
    Configurações

PÁGINA START
    EPCs encontrados | Extra box
    Inventário RFID automático
    Tabela de etiquetas lidas

PÁGINA STATUS
    Status sistema
    RFID
    Internet
    Comandos
    Sistema

EXECUTÁVEL WINDOWS
    DSV-RFID.exe
    Ícone personalizado DSV RFID

IMPLEMENTAR O RF031.

PRESERVAR INTEGRALMENTE A LÓGICA OPERACIONAL.
ALTERAR SOMENTE O NECESSÁRIO PARA O NOVO LAYOUT
E PARA A PERSONALIZAÇÃO DO ÍCONE WINDOWS.