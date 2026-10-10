# RF018 — Modernização Visual da Aplicação RFID e Identidade DSV

**Categoria:** UX/UI — Interface Desktop  
**Prioridade:** Alta  
**Ambiente:** Windows  
**Referências:** imagem.png e DSV_Logo.svg  
**Escopo:** Modernização visual sem alteração da composição funcional das telas

---

## 1. Objetivo

Modernizar a interface gráfica do software RFID, adotando uma identidade visual profissional, alinhada à marca DSV e inspirada na referência visual fornecida.

A aplicação deverá apresentar uma interface moderna, consistente, intuitiva e adequada à utilização em ambiente operacional/logístico.

O projeto já possui uma composição de layout considerada satisfatória.

**Portanto, não devemos redesenhar a estrutura da aplicação.**

O objetivo é modernizar:

- Paleta de cores.
- Tipografia.
- Botões.
- Cards.
- Tabelas.
- Indicadores de status.
- Ícones.
- Bordas e superfícies.
- Estados de interação.
- Espaçamento interno dos componentes.
- Identidade visual da empresa.
- Feedback visual ao operador.

A modernização poderá utilizar uma biblioteca gráfica mais moderna que o Tkinter, desde que preserve o funcionamento do sistema.

### Resultado esperado

Uma aplicação desktop com aparência de um software corporativo moderno, semelhante à linguagem visual de dashboards profissionais.

A interface deve transmitir:

- Confiabilidade.
- Organização.
- Clareza operacional.
- Modernidade.
- Identidade corporativa.
- Facilidade de identificação dos estados do sistema.

---

## 2. Regra principal — Preservar o layout atual

A estrutura atual da aplicação já foi aprovada.

**Não modificar a composição do layout.**

Preservar:

1. Header superior.
2. Sidebar de navegação.
3. Área principal de conteúdo.
4. Cards de indicadores.
5. Tabela de resultados RFID.
6. Botões operacionais.
7. Indicadores de conexão.
8. Tela de configurações.
9. Configurações do Zebra FX9600.
10. Configurações da Waveshare.
11. Configurações do Backend.
12. Tela de testes da Waveshare.

Não modificar a ordem dos componentes.

Não criar novas telas desnecessariamente.

Não mover funcionalidades entre menus.

Não alterar o fluxo de navegação.

São permitidos pequenos ajustes de:

- Padding.
- Margens.
- Espaçamento entre elementos.
- Alinhamento interno.
- Altura de componentes.
- Raio das bordas.
- Dimensionamento de fontes.

Esses ajustes devem melhorar o acabamento visual sem descaracterizar o layout atual.

### Referência visual

A imagem `imagem.png` deve ser utilizada como referência para:

- Tema escuro.
- Combinação de cores.
- Superfícies dos cards.
- Sidebar.
- Header.
- Bordas.
- Hierarquia visual.
- Estilo de indicadores.
- Estilo de tabelas.
- Aparência de botões.

**A imagem é uma referência de identidade visual, não um modelo para copiar a estrutura da tela.**

Não copiar logotipos, textos, nomes ou funcionalidades da aplicação exibida na referência.

---

## 3. Biblioteca gráfica — Avaliação obrigatória

Atualmente o software utiliza Tkinter.

O Codex deverá avaliar a melhor alternativa para modernizar a interface.

### 3.1 Alternativa preferencial — CustomTkinter

Avaliar prioritariamente:

    customtkinter

Motivos:

- Interface visual mais moderna que Tkinter tradicional.
- Suporte a temas escuros.
- Componentes com cantos arredondados.
- Botões personalizados.
- Frames modernos.
- Inputs estilizados.
- Integração relativamente simples com a arquitetura Tkinter.
- Menor risco de regressão do sistema existente.

Essa alternativa deve ser priorizada caso permita atingir a qualidade visual desejada.

### 3.2 Alternativa — PySide6

Caso CustomTkinter não ofereça recursos suficientes, avaliar:

    PySide6

Vantagens:

- Framework profissional baseado em Qt.
- Sistema avançado de estilos.
- Suporte a SVG.
- Tabelas modernas.
- Melhor controle visual de componentes.
- Suporte a layouts responsivos.
- Arquitetura robusta para aplicações desktop.
- Suporte a sinais e eventos para comunicação entre threads.

Entretanto, migrar para PySide6 pode exigir uma alteração significativa na interface.

**Não migrar automaticamente toda a aplicação para PySide6 sem justificar tecnicamente a necessidade.**

Caso a migração seja recomendada, apresentar antes:

1. Limitações identificadas no Tkinter/CustomTkinter.
2. Benefícios concretos da migração.
3. Arquivos e componentes afetados.
4. Impacto na arquitetura.
5. Impacto nas threads.
6. Impacto na integração com Zebra.
7. Impacto na comunicação Waveshare.
8. Impacto nos serviços HTTP.
9. Estratégia de migração.
10. Estratégia de rollback.

Aguardar aprovação antes de executar uma reescrita completa da interface.

### 3.3 Regra de arquitetura

Independentemente da biblioteca escolhida:

    UI
     │
     ▼
    Services
     │
     ├── Zebra RFID
     ├── Waveshare
     ├── Backend API
     └── Configurações

A interface não deve conter lógica direta de comunicação com os equipamentos.

Não duplicar regras de negócio.

Não reimplementar serviços que já funcionam.

---

# 4. Identidade visual DSV

O software deverá incorporar o logotipo oficial da DSV fornecido no arquivo:

    DSV_Logo.svg

O logotipo deverá ser exibido no header da aplicação.

### 4.1 Cor institucional

O SVG fornecido utiliza:

    DSV Blue
    #192862

Essa cor deve ser preservada como referência da identidade corporativa.

### 4.2 Regra de contraste

O logotipo original é azul-escuro.

Como a aplicação utilizará um tema escuro, não posicionar diretamente o logotipo azul sobre uma superfície escura com contraste insuficiente.

Utilizar uma superfície clara discreta para acomodar o logotipo.

Exemplo conceitual:

    ┌─────────────────────────────────────────────┐
    │                                             │
    │  ┌─────────────┐                            │
    │  │  DSV LOGO   │   RFID SYSTEM              │
    │  └─────────────┘                            │
    │                                             │
    └─────────────────────────────────────────────┘

A área clara deve:

- Ter bordas arredondadas discretas.
- Preservar o contraste.
- Manter o logotipo centralizado.
- Respeitar a proporção original.
- Não distorcer a imagem.
- Não cortar letras.
- Não adicionar efeitos excessivos.

### 4.3 Tamanho

Referência inicial:

    Largura: 110 a 140 px
    Altura: proporcional

O tamanho final deve considerar o header existente.

Não aumentar a altura do header desnecessariamente.

### 4.4 Tratamento do SVG

O arquivo SVG fornecido contém conteúdo adicional após o fechamento do elemento SVG.

Antes de utilizá-lo:

1. Criar uma cópia limpa do recurso.
2. Preservar o desenho vetorial original.
3. Remover apenas o conteúdo externo inválido.
4. Validar o XML/SVG resultante.
5. Verificar ausência de referências externas desnecessárias.
6. Confirmar que o logotipo renderiza corretamente.
7. Não modificar a geometria da marca.

O arquivo original não deve ser sobrescrito automaticamente.

### 4.5 Assets

Utilizar a estrutura de assets já existente no projeto.

Caso não exista, criar uma estrutura equivalente a:

    assets/
        branding/
            dsv_logo.svg
            dsv_logo.png

A versão PNG poderá ser utilizada caso a biblioteca gráfica escolhida não suporte SVG adequadamente.

Gerar o PNG com resolução suficiente para telas de alta densidade.

Não baixar o logotipo da internet.

Não utilizar caminhos absolutos do computador do desenvolvedor.

---

# 5. Tema visual

O tema principal será:

    DARK CORPORATE

Inspirado na imagem de referência.

A aparência deve utilizar tons de:

- Grafite.
- Azul-acinzentado.
- Azul-marinho.
- Azul institucional.
- Branco suave.
- Cinza claro.

Evitar:

- Preto absoluto em grandes superfícies.
- Cores neon.
- Gradientes exagerados.
- Bordas muito grossas.
- Sombras excessivas.
- Botões com aparência antiga do Windows.
- Componentes com estilos diferentes entre telas.

---

# 6. Paleta de cores oficial da interface

Criar um sistema centralizado de cores.

A paleta inicial deverá ser:

| Token | Cor | Utilização |
|---|---|---|
| `BG_MAIN` | `#353C48` | Fundo principal |
| `BG_HEADER` | `#303641` | Header |
| `BG_SIDEBAR` | `#303641` | Sidebar |
| `BG_CARD` | `#252F3F` | Cards e painéis |
| `BG_SURFACE_ALT` | `#1D2738` | Superfícies secundárias |
| `BG_INPUT` | `#1A2334` | Inputs e campos |
| `BORDER` | `#455368` | Bordas discretas |
| `DSV_BLUE` | `#192862` | Identidade corporativa |
| `PRIMARY` | `#267AAE` | Ações principais |
| `PRIMARY_HOVER` | `#2A78A8` | Hover de ações principais |
| `TEXT_PRIMARY` | `#F5F7FB` | Textos principais |
| `TEXT_SECONDARY` | `#C5D0DF` | Textos secundários |
| `TEXT_MUTED` | `#9DACC1` | Legendas e informações auxiliares |
| `SUCCESS` | `#22C55E` | Status positivos |
| `SUCCESS_TEXT` | `#86EFAC` | Texto positivo |
| `SUCCESS_BG` | `#163B2D` | Fundo positivo |
| `ERROR` | `#FF7B79` | Status negativos |
| `ERROR_TEXT` | `#FDA4A4` | Texto negativo |
| `ERROR_BG` | `#4A2027` | Fundo negativo |
| `WARNING` | `#F6B84A` | Alertas e leitura em andamento |
| `WARNING_TEXT` | `#FDE68A` | Texto de alerta |
| `WARNING_BG` | `#473616` | Fundo de alerta |
| `FOCUS` | `#64B5F6` | Foco de teclado |

Essas cores devem ser centralizadas.

Não espalhar valores hexadecimais diretamente pelos arquivos da interface.

Criar estrutura equivalente a:

    ui/
        theme/
            colors.py
            typography.py
            components.py

Adaptar os nomes e caminhos à organização real do projeto.

### Regra importante

A paleta é a referência inicial.

Pequenos ajustes são permitidos para garantir:

- Contraste.
- Legibilidade.
- Consistência.
- Acessibilidade.

Não alterar arbitrariamente a identidade visual definida.

---

# 7. Sistema semântico de cores

Esta é uma das regras mais importantes do RF018.

As cores devem possuir significados consistentes em toda a aplicação.

## 7.1 Verde — Afirmações e estados positivos

Utilizar verde para:

- Conectado.
- Online.
- Disponível.
- Pronto.
- Sistema OK.
- Banco de dados OK.
- Comandos OK.
- RFID conectado.
- Operação concluída.
- Registro realizado com sucesso.
- EPC validado com sucesso.

Exemplo:

    ● Conectado

    ● Sistema OK

    ● Base de dados OK

    ✓ Registro realizado

O verde deve transmitir que uma condição foi confirmada positivamente.

## 7.2 Vermelho — Estados negativos

Utilizar vermelho para:

- Desconectado.
- Indisponível.
- Erro.
- Falha de comunicação.
- Falha de registro.
- Falha do Backend.
- Falha de conexão RFID.
- Falha da Waveshare.
- Sistema não apto.

Exemplo:

    ● Desconectado

    ● Sistema indisponível

    ✕ Falha na comunicação

Não utilizar vermelho para informações neutras.

## 7.3 Amarelo — Atenção e processamento

Utilizar amarelo para:

- Leitura RFID em andamento.
- Verificação de conexão.
- Aguardando resposta.
- Processando.
- Atenção.
- Estado pendente.
- Condição temporária.

Exemplo:

    ● Lendo etiquetas

    ◷ Verificando conexão

    ● Pendente

**Pendente não deve ser tratado automaticamente como erro.**

## 7.4 Azul — Ações e informações

Utilizar azul para:

- Botões de ação neutra.
- Configurações.
- Testar conexão.
- Navegação selecionada.
- Links.
- Informações.
- Elementos interativos.

## 7.5 Cinza — Estados neutros

Utilizar cinza para:

- Desconhecido.
- Não verificado.
- Desabilitado.
- Informação auxiliar.
- Campos somente leitura.
- Estado inicial ainda não determinado.

---

# 8. Estados operacionais CH1, CH2 e CH3

Preservar o significado dos relés definido no RF012.

| Relé | Estado | Cor visual |
|---|---|---|
| CH1 | Sistema apto | Verde |
| CH2 | Leitura RFID em andamento | Amarelo |
| CH3 | Sistema indisponível/erro | Vermelho |

### CH1

    CH1 ON
        ↓
    SISTEMA APTO
        ↓
    indicador verde

### CH2

    CH2 ON
        ↓
    LEITURA EM ANDAMENTO
        ↓
    indicador amarelo

### CH3

    CH3 ON
        ↓
    ERRO / INDISPONÍVEL
        ↓
    indicador vermelho

Esses estados não devem ser alterados pela modernização.

Apenas sua representação visual deve ser melhorada.

Não criar comandos Modbus adicionais para atualizar a interface.

---

# 9. Header

Preservar a posição e composição do header atual.

Modernizar:

- Cor de fundo.
- Tipografia.
- Logotipo.
- Ícones.
- Alinhamento.
- Separação visual.
- Indicadores existentes.

### Aparência desejada

    ┌───────────────────────────────────────────────────┐
    │                                                   │
    │  DSV    RFID SYSTEM                STATUS / INFO  │
    │                                                   │
    └───────────────────────────────────────────────────┘

O desenho acima representa apenas o tratamento visual.

Não alterar a organização atual dos controles.

### Regras

- Header com fundo `BG_HEADER`.
- Altura preservada.
- Logotipo DSV alinhado verticalmente.
- Título com tipografia moderna.
- Ícones discretos.
- Sem bordas pesadas.
- Separação sutil entre header e conteúdo.

---

# 10. Sidebar

Preservar os menus existentes.

Não adicionar nem remover itens.

Não alterar a navegação.

### Aparência

A sidebar deverá possuir:

    BG_SIDEBAR = #303641

Os itens de menu deverão apresentar estados visuais distintos.

### Item normal

- Texto secundário.
- Ícone discreto.
- Fundo transparente ou da sidebar.

### Hover

- Fundo levemente destacado.
- Transição visual discreta.
- Cursor apropriado.

### Item selecionado

- Fundo diferenciado.
- Texto principal.
- Ícone destacado.
- Pequeno indicador azul de seleção, caso não altere a composição.

### Item desabilitado

- Cor neutra.
- Sem aparência de ação disponível.
- Sem hover de item clicável.

### Regras

- Preservar largura da sidebar.
- Preservar ordem dos menus.
- Preservar hierarquia.
- Não utilizar ícones coloridos aleatoriamente.
- Não criar menus duplicados.
- Manter textos legíveis.

---

# 11. Tipografia

A tipografia deverá ser moderna, limpa e adequada ao Windows.

Priorizar:

    Segoe UI

Alternativas:

    Inter
    Arial

Não exigir instalação manual de fontes.

Não distribuir arquivos de fontes sem necessidade.

### Escala tipográfica

| Elemento | Tamanho sugerido | Peso |
|---|---|---|
| Título principal | 22–26 px | Semibold |
| Título de seção | 16–18 px | Semibold |
| Título de card | 13–15 px | Semibold |
| Texto comum | 13–14 px | Regular |
| Label de input | 12–13 px | Medium |
| Texto de tabela | 12–13 px | Regular |
| Valor de KPI | 26–32 px | Bold |
| Status | 12–13 px | Medium |

Ajustar conforme o dimensionamento real do Windows.

### Regras

- Evitar excesso de negrito.
- Não utilizar texto inteiro em maiúsculas indiscriminadamente.
- Manter hierarquia clara.
- Evitar fontes pequenas demais.
- Garantir contraste.
- Preservar alinhamento.
- Não cortar textos.

---

# 12. Cards

Todos os cards existentes deverão utilizar um padrão visual unificado.

### Aparência

    ┌─────────────────────────────────────┐
    │                                     │
    │  Título do card                     │
    │                                     │
    │  Valor / Informação                 │
    │                                     │
    │  Informação complementar            │
    │                                     │
    └─────────────────────────────────────┘

### Estilo

    Background:
        #252F3F

    Border radius:
        10 a 14 px

    Border:
        1 px discreta, quando necessária

    Padding:
        16 a 20 px

    Shadow:
        sutil, caso suportada

Não criar cards com sombras fortes.

Não utilizar bordas luminosas.

Não criar efeitos 3D exagerados.

### Hierarquia

O valor principal deve possuir maior destaque que a descrição.

Exemplo:

    EPCs encontrados

          15

    Etiquetas identificadas na sessão

O texto acima é apenas uma referência de hierarquia, não uma solicitação para adicionar informações que não existam.

---

# 13. Cards de status

Os indicadores existentes deverão apresentar cores semânticas.

Exemplo conceitual:

    ┌──────────────────────────────┐
    │ RFID                         │
    │ ● Conectado                  │
    └──────────────────────────────┘

    ┌──────────────────────────────┐
    │ Sistema                      │
    │ ● Disponível                 │
    └──────────────────────────────┘

    ┌──────────────────────────────┐
    │ Base de dados                │
    │ ● Conectada                  │
    └──────────────────────────────┘

### Estados

    OK
        → verde

    NOK
        → vermelho

    Verificando
        → amarelo

    Desconhecido
        → cinza

Não representar estado desconhecido como OK.

Não manter um indicador verde quando o estado real já estiver indisponível.

### Regra de arquitetura

A UI deve consumir os estados reais existentes.

Não criar lógica própria de health check dentro dos componentes visuais.

---

# 14. Tabela de resultados RFID

A tabela é um dos componentes mais importantes da aplicação.

Modernizar sua aparência preservando:

- Colunas atuais.
- Ordem das colunas.
- Dados apresentados.
- Filtros existentes.
- Regras de atualização.
- Comportamento de seleção.
- Deduplicação.

### Estrutura atual

    Status
    Cliente
    Nota fiscal
    Volume
    Pedido
    Doca

Não adicionar colunas neste RF.

### 14.1 Cabeçalho

Utilizar:

    Background:
        #1D2738

    Texto:
        #C5D0DF

    Peso:
        Semibold

    Altura:
        36 a 42 px

### 14.2 Linhas

Utilizar:

    Background:
        #252F3F

    Texto:
        #F5F7FB

    Altura:
        36 a 44 px

### 14.3 Separadores

Utilizar separadores discretos.

Evitar grades pesadas.

### 14.4 Hover

Quando o cursor estiver sobre uma linha:

- Destacar levemente o fundo.
- Preservar legibilidade.
- Não alterar os dados.
- Não interferir na seleção.

### 14.5 Seleção

A linha selecionada deverá possuir um destaque azul discreto.

Não utilizar uma seleção excessivamente saturada.

### 14.6 Rolagem

Preservar scroll vertical e horizontal quando necessário.

Não cortar informações sem possibilidade de visualização.

### 14.7 Atualização

A chegada de novos EPCs não deve:

- Congelar a UI.
- Reinicializar a tabela inteira desnecessariamente.
- Fazer a tela piscar.
- Remover a seleção atual sem motivo.
- Alterar a posição de rolagem inesperadamente.

---

# 15. Status dentro da tabela

A coluna Status deverá utilizar representação visual consistente.

Exemplos:

    [ ● Lido ]

    [ ● Pendente ]

### Status `lido`

    Verde

### Status `pendente`

    Amarelo

Se a aplicação já apresentar estados técnicos de falha:

    Vermelho

Não inventar novos estados de negócio.

Utilizar os valores reais retornados pelo Backend.

Não confundir:

    status = lido

com:

    EPC encontrado

São conceitos diferentes.

---

# 16. Botões

Criar um padrão visual único para botões.

### 16.1 Botão primário

Utilizar azul para ações gerais.

Exemplos:

- Testar conexão.
- Abrir configurações.
- Executar ações neutras.

Características:

    Background:
        PRIMARY

    Texto:
        Branco

    Radius:
        8 a 10 px

    Altura:
        36 a 42 px

### 16.2 Ação positiva

Ações operacionais afirmativas podem utilizar verde.

Exemplo:

    Iniciar Leitura

O verde deverá indicar a intenção de iniciar uma operação disponível.

Entretanto, a confirmação de que a operação começou deve continuar dependendo do estado real do sistema.

### 16.3 Ação negativa ou de interrupção

Utilizar vermelho para ações como:

    Parar Leitura

ou ações destrutivas existentes.

O botão deve indicar claramente a ação, sem alterar a lógica de Stop.

### 16.4 Botão secundário

Utilizar fundo discreto e borda sutil.

Exemplos:

    Cancelar
    Voltar
    Fechar

### 16.5 Estados obrigatórios

Todos os botões devem possuir:

    NORMAL
    HOVER
    PRESSED
    DISABLED
    FOCUS

O estado desabilitado deve ser claramente diferente do estado normal.

Não permitir que um botão visualmente desabilitado continue executando a ação.

---

# 17. Inputs e formulários

Modernizar os campos de configuração existentes.

Incluindo:

- IP do Zebra.
- Porta do Zebra.
- Nome do reader.
- Porta COM.
- Baudrate.
- Doca.
- URL do Backend.
- Demais configurações existentes.

### Aparência

    Background:
        #1A2334

    Border:
        #455368

    Texto:
        #F5F7FB

    Radius:
        8 px

    Altura:
        36 a 42 px

### Foco

Quando o input estiver selecionado:

    Border:
        #64B5F6

Não utilizar bordas muito grossas.

### Labels

Posicionar e preservar os labels conforme a composição atual.

Não substituir labels importantes apenas por placeholders.

### Erros de validação

Exemplo:

    URL do Backend inválida

Utilizar:

- Borda vermelha.
- Mensagem curta.
- Ícone, quando adequado.

Não depender exclusivamente da cor.

---

# 18. Combobox e dropdown

Os dropdowns existentes deverão seguir o mesmo tema.

Características:

- Fundo escuro.
- Texto claro.
- Borda discreta.
- Hover consistente.
- Item selecionado destacado.
- Scroll quando necessário.
- Altura coerente com inputs.

Não utilizar dropdowns com aparência clara padrão do Windows dentro de uma interface escura, caso a biblioteca permita personalização adequada.

---

# 19. Feedback visual

A interface deverá fornecer feedback claro para ações existentes.

### Sucesso

Exemplo:

    ✓ Configurações salvas com sucesso

Cor:

    Verde

### Erro

Exemplo:

    ✕ Não foi possível conectar ao Backend

Cor:

    Vermelho

### Processamento

Exemplo:

    ◷ Testando conexão...

Cor:

    Amarelo ou azul informativo

### Atenção

Exemplo:

    ⚠ Configure a porta COM

Cor:

    Amarelo

### Regras

- Mensagens curtas.
- Linguagem objetiva.
- Sem excesso de popups.
- Não bloquear operações por mensagens informativas.
- Não inventar sucesso antes da confirmação real.
- Não substituir mensagens técnicas importantes por textos genéricos.

Preservar os mecanismos de feedback existentes e modernizar sua apresentação.

---

# 20. Estados vazios

Quando uma tabela ou lista não possuir dados, apresentar um estado vazio visualmente organizado.

Exemplo:

    Nenhum EPC registrado nesta sessão.

Não apresentar uma tabela quebrada ou com aparência de erro.

Não utilizar vermelho quando simplesmente não existem registros.

Utilizar cor neutra.

Preservar a regra de que EPCs não encontrados não são apresentados na tabela operacional.

---

# 21. Estados de carregamento

Quando houver uma operação assíncrona existente:

    Verificando conexão...
    Consultando Backend...
    Carregando configurações...

a interface deverá apresentar feedback apropriado.

Não criar animações pesadas.

Não criar loops de animação que interfiram nas threads de comunicação.

Não bloquear a interface inteira quando somente um componente estiver processando.

---

# 22. Ícones

Adotar uma família visual consistente de ícones.

Preferir ícones vetoriais simples, com estilo semelhante ao Lucide.

Exemplos conceituais:

    wifi
    server
    database
    radio-tower
    settings
    play
    square
    check-circle
    circle-alert
    refresh-cw

### Regras

- Ícones com traços consistentes.
- Tamanho entre 16 e 20 px para ações comuns.
- Cores semânticas quando necessário.
- Não misturar ícones 3D e ícones lineares.
- Não utilizar emojis como substitutos permanentes dos ícones.
- Preservar o significado das ações.

Os ícones devem ser armazenados localmente ou fornecidos por biblioteca compatível com o empacotamento da aplicação.

Não depender de internet para renderizar ícones.

---

# 23. Hierarquia visual

A interface deverá possuir três níveis claros de informação.

### Nível 1 — Informação principal

Exemplos:

- Estado geral do sistema.
- Leitura em andamento.
- EPCs encontrados.
- Botões operacionais.

Esses elementos devem possuir maior destaque.

### Nível 2 — Informações operacionais

Exemplos:

- Tabela.
- Detalhes dos registros.
- Configurações.
- Indicadores individuais.

### Nível 3 — Informações auxiliares

Exemplos:

- Legendas.
- Mensagens de ajuda.
- Informações complementares.
- Dados secundários.

Não utilizar o mesmo tamanho e peso de fonte para todos os elementos.

---

# 24. Espaçamento

Utilizar uma escala consistente.

Sugestão:

    4 px
    8 px
    12 px
    16 px
    24 px
    32 px

Aplicação:

    4 px
        separações pequenas

    8 px
        ícone e texto

    12 px
        componentes próximos

    16 px
        padding interno

    24 px
        separação entre grupos

    32 px
        separação de seções maiores

Preservar as dimensões gerais do layout atual.

Não aumentar os espaçamentos a ponto de reduzir significativamente a quantidade de informações visíveis.

---

# 25. Bordas e cantos

Padronizar:

    Botões:
        8–10 px

    Inputs:
        8 px

    Cards:
        10–14 px

    Indicadores:
        formato pill ou raio equivalente

    Modais:
        12–14 px

Evitar misturar:

- Componentes totalmente quadrados.
- Componentes excessivamente arredondados.
- Bordas com espessuras diferentes sem motivo.

---

# 26. Contraste e acessibilidade

A aplicação deverá ser legível em ambientes operacionais.

### Requisitos

- Contraste adequado entre texto e fundo.
- Referência WCAG AA: 4,5:1 para texto comum.
- Ícones importantes com contraste suficiente.
- Status com cor e texto.
- Botões com estados distintos.
- Foco de teclado visível.
- Labels legíveis.
- Não depender apenas de vermelho/verde para comunicar estados.

Exemplo correto:

    ● Conectado

Exemplo inadequado:

    ●

sem qualquer identificação textual.

O operador deve conseguir identificar o estado mesmo com dificuldade de distinção de cores.

---

# 27. Navegação por teclado

Preservar e melhorar, quando aplicável:

    Tab
        próximo campo

    Shift + Tab
        campo anterior

    Enter
        ação principal contextual

    Esc
        fechar diálogo, quando apropriado

Não criar atalhos que acionem inadvertidamente operações físicas.

Não modificar atalhos existentes sem necessidade.

---

# 28. Redimensionamento e resolução

A aplicação deve continuar abrindo maximizada, conforme comportamento atual.

Validar no Windows nas resoluções:

    1366 × 768

    1600 × 900

    1920 × 1080

Também testar escalas de exibição:

    100%

    125%

    150%

### Requisitos

- Não cortar botões.
- Não sobrepor textos.
- Não esconder campos importantes.
- Não distorcer o logotipo.
- Não permitir que cards invadam outras áreas.
- Preservar proporções.
- Manter scroll onde necessário.
- Preservar o posicionamento geral dos componentes.

Não alterar a composição para criar uma interface completamente diferente em resoluções menores.

Priorizar adaptação de tamanho e rolagem.

---

# 29. Animações

Utilizar animações apenas quando agregarem valor.

Permitido:

- Hover suave.
- Indicador discreto de processamento.
- Transição curta de estado.
- Destaque de foco.

Evitar:

- Animações constantes sem necessidade.
- Efeitos luminosos.
- Elementos piscando continuamente.
- Transições longas.
- Animações que consumam CPU excessivamente.

O software controla equipamentos físicos.

A interface deve priorizar estabilidade.

---

# 30. Tela principal — Start

Modernizar a tela principal preservando todos os componentes atuais.

Priorizar visualmente:

1. Estado de prontidão.
2. Botão Iniciar/Parar.
3. Indicadores de conexão.
4. Estado da leitura.
5. Contador de EPCs.
6. Tabela de resultados.

Essa lista representa a prioridade de destaque visual, não uma alteração da ordem ou posição dos componentes.

### Durante leitura

Quando o RFID estiver lendo:

    CH2 = ON

a interface deverá destacar:

    Leitura em andamento

utilizando amarelo.

### Sistema pronto

Quando:

    CH1 = ON

destacar:

    Sistema apto

em verde.

### Erro

Quando:

    CH3 = ON

destacar:

    Sistema indisponível

em vermelho.

Não alterar a lógica de acionamento dos relés.

---

# 31. Tela de configurações

Aplicar a mesma identidade visual.

Preservar as seções existentes:

- Zebra RFID.
- Waveshare.
- Backend RFID.
- Doca.
- Demais configurações.

### Regras

- Utilizar cards ou containers existentes.
- Modernizar inputs.
- Modernizar labels.
- Modernizar botões.
- Preservar validações.
- Preservar persistência.
- Preservar testes de conexão.
- Não alterar nomes de parâmetros de configuração sem necessidade.

---

# 32. Tela de testes Waveshare

Aplicar a nova identidade visual preservando:

    DI1
    DI2
    DI3
    DI4
    DI5

e:

    CH1
    CH2
    CH3
    CH4
    CH5
    CH6
    CH7
    CH8

### Entradas digitais

Representar os estados reais de forma clara.

Não presumir que:

    0 = erro

ou:

    1 = sucesso

O significado depende da configuração elétrica e da lógica do sensor.

Utilizar textos que representem corretamente o estado observado.

### Relés

Preservar os controles manuais existentes.

Não alterar endereços Modbus.

Não alterar comandos.

Não alterar polling.

Não alterar a lógica de leitura das entradas.

Modernizar apenas os componentes visuais.

---

# 33. Interface e threads

A modernização não pode introduzir problemas de concorrência.

O software utiliza comunicação com:

    Zebra FX9600
    Waveshare
    Backend HTTP

Essas operações podem executar em background.

### Se utilizar Tkinter/CustomTkinter

Atualizações visuais devem ocorrer na thread apropriada da UI, utilizando os mecanismos existentes, como agendamento pelo event loop.

### Se utilizar PySide6

Utilizar sinais/slots ou mecanismo equivalente para comunicação segura entre workers e interface.

### Proibições

- Atualizar widgets diretamente de threads incompatíveis.
- Executar HTTP bloqueante na thread principal.
- Executar leitura Modbus bloqueante na UI.
- Executar operações LLRP bloqueantes na UI.
- Criar loops de polling duplicados.
- Criar timers concorrentes desnecessários.

---

# 34. Desempenho

A modernização não deve prejudicar o desempenho.

### Requisitos

- Inicialização sem atraso excessivo.
- Atualização de status responsiva.
- Tabela capaz de receber novas linhas sem travamentos.
- Baixo consumo adicional de CPU.
- Sem renderização contínua desnecessária.
- Sem carregamento remoto de recursos visuais.
- Sem recriação completa de widgets a cada atualização de estado.

Preservar o processamento RFID em tempo real.

---

# 35. Componentes reutilizáveis

Evitar estilizar cada tela manualmente de maneira independente.

Criar componentes reutilizáveis conforme necessidade.

Exemplos conceituais:

    AppHeader
    AppSidebar
    StatusIndicator
    StatusCard
    PrimaryButton
    SecondaryButton
    DangerButton
    StyledInput
    StyledTable
    SectionCard

Esses nomes são sugestões.

Seguir a arquitetura real do projeto.

Não criar abstrações complexas desnecessariamente.

O objetivo é garantir que alterações futuras de cor, fonte e estilo possam ser realizadas em um único lugar.

---

# 36. Tema centralizado

A aplicação deve possuir uma fonte única para o tema.

Exemplo conceitual:

    Theme
        │
        ├── Colors
        ├── Typography
        ├── Spacing
        ├── Radius
        ├── Icons
        └── ComponentStyles

Não repetir:

    "#353C48"

em dezenas de arquivos.

Utilizar tokens centralizados.

Não criar múltiplos temas paralelos neste requisito.

O tema inicial será escuro.

---

# 37. Empacotamento Windows

Verificar que a modernização é compatível com o processo atual de execução e distribuição da aplicação.

Se o projeto utilizar PyInstaller ou equivalente:

- Incluir assets.
- Incluir logotipo.
- Incluir ícones.
- Incluir dependências gráficas.
- Garantir caminhos relativos corretos.
- Verificar execução fora da pasta do projeto.
- Verificar funcionamento após empacotamento.

Não exigir internet para carregar o tema.

Não exigir instalação manual de fontes.

Não depender de caminhos do ambiente de desenvolvimento.

---

# 38. Restrições de escopo

Este requisito é exclusivamente visual.

**Não alterar regras de negócio.**

Não modificar:

- Comunicação LLRP.
- Leitura de EPC.
- Normalização de EPC.
- Deduplicação.
- Consulta GET do RF016.
- Registro POST do RF017.
- Health check do RF015.
- Contrato JSON.
- Banco PostgreSQL.
- Backend Rails.
- Configuração de Doca.
- Configuração do Zebra.
- Configuração da Waveshare.
- Protocolo Modbus.
- Estados DI1/DI2.
- Temporizador de 60 segundos.
- Lógica CH1/CH2/CH3.
- Funcionalidades CH4–CH8.
- Fluxo Start/Stop.
- Persistência das configurações.

Não reintroduzir:

    SQLite operacional
    Power Automate
    Sincronização
    EPCs não encontrados

---

# 39. Análise obrigatória antes da implementação

O Codex deverá analisar:

1. `AGENTS.md`.
2. Estrutura do projeto.
3. Biblioteca gráfica atual.
4. Arquivo principal da UI.
5. Header.
6. Sidebar.
7. Tela Start.
8. Tabela RFID.
9. Cards.
10. Indicadores.
11. Tela de configurações.
12. Tela de testes Waveshare.
13. Serviços de comunicação.
14. Threads.
15. Timers.
16. Sistema de eventos.
17. Assets existentes.
18. Empacotamento Windows.
19. Dependências.
20. Testes existentes.

Identificar todos os pontos em que estilos visuais estão definidos diretamente nos widgets.

---

# 40. Relatório obrigatório antes de alterar o código

Antes da implementação, apresentar:

### Diagnóstico da interface

- Biblioteca gráfica atual.
- Organização das telas.
- Componentes reutilizáveis existentes.
- Componentes visuais duplicados.
- Limitações identificadas.
- Pontos que precisam ser modernizados.

### Decisão tecnológica

- Biblioteca recomendada.
- Justificativa.
- Impacto esperado.
- Dependências necessárias.
- Riscos de migração.
- Estratégia para preservar funcionalidades.

### Plano visual

- Paleta definitiva.
- Estratégia para o logotipo.
- Estratégia para o header.
- Estratégia para a sidebar.
- Estratégia para os cards.
- Estratégia para a tabela.
- Estratégia para os indicadores.
- Estratégia para as telas de configuração.

### Plano técnico

- Arquivos previstos para alteração.
- Arquivos novos.
- Componentes preservados.
- Testes previstos.
- Estratégia de rollback.

Não iniciar uma reescrita ampla sem esse diagnóstico.

---

# 41. Ordem de implementação

Executar preferencialmente em etapas.

## Etapa 1 — Preparação

1. Analisar interface existente.
2. Confirmar biblioteca gráfica.
3. Definir tokens visuais.
4. Preparar logotipo DSV.
5. Organizar assets.
6. Registrar estado visual anterior.

## Etapa 2 — Tema

1. Implementar tema centralizado.
2. Aplicar cores globais.
3. Aplicar tipografia.
4. Aplicar bordas.
5. Aplicar estilos de componentes.

## Etapa 3 — Estrutura visual

1. Modernizar header.
2. Inserir logotipo DSV.
3. Modernizar sidebar.
4. Modernizar cards.
5. Modernizar indicadores.

## Etapa 4 — Operação RFID

1. Modernizar botões.
2. Modernizar tabela.
3. Modernizar status.
4. Modernizar feedback visual.
5. Validar atualização dinâmica.

## Etapa 5 — Configurações

1. Modernizar inputs.
2. Modernizar dropdowns.
3. Modernizar botões.
4. Modernizar mensagens.
5. Modernizar tela Waveshare.

## Etapa 6 — Validação

1. Verificar composição do layout.
2. Verificar contraste.
3. Verificar resoluções.
4. Verificar DPI.
5. Verificar threads.
6. Executar testes de regressão.
7. Validar empacotamento Windows.

---

# 42. Evidências visuais

Antes de alterar o layout, registrar capturas de tela da versão atual.

Depois da implementação, produzir capturas equivalentes.

Comparar:

- Posição dos elementos.
- Dimensões principais.
- Navegação.
- Quantidade de informações.
- Legibilidade.
- Hierarquia.
- Consistência.
- Cores.
- Alinhamento.
- Contraste.

O objetivo é demonstrar que houve modernização visual sem redesenho da aplicação.

---

# 43. Testes visuais obrigatórios

## Teste 1 — Header

Verificar:

- Logotipo DSV renderizado.
- Proporção correta.
- Contraste adequado.
- Nenhum corte.
- Nenhuma sobreposição.
- Header preservado.

## Teste 2 — Sidebar

Verificar:

- Menus preservados.
- Ícones consistentes.
- Hover funcionando.
- Item selecionado destacado.
- Navegação funcional.

## Teste 3 — Cards

Verificar:

- Fundo correto.
- Bordas consistentes.
- Tipografia adequada.
- Espaçamento uniforme.
- Valores legíveis.

## Teste 4 — Tabela

Verificar:

- Cabeçalho legível.
- Colunas preservadas.
- Dados preservados.
- Scroll funcionando.
- Seleção funcionando.
- Novas linhas sem travamentos.

## Teste 5 — Status positivos

Simular:

    Sistema OK

Esperado:

    Verde
    +
    texto indicando estado positivo

## Teste 6 — Status negativos

Simular:

    Sistema NOK

Esperado:

    Vermelho
    +
    texto indicando falha

## Teste 7 — Estado de leitura

Simular:

    CH2 ON

Esperado:

    Amarelo
    +
    texto Leitura em andamento

## Teste 8 — Estado desconhecido

Simular estado inicial sem confirmação.

Esperado:

    Cinza ou indicador de verificação

Nunca verde sem confirmação.

## Teste 9 — Configurações

Verificar:

- Inputs legíveis.
- Dropdowns funcionais.
- Botões corretos.
- Mensagens adequadas.
- Persistência preservada.

## Teste 10 — Resolução

Validar:

    1366 × 768
    1600 × 900
    1920 × 1080

e DPI:

    100%
    125%
    150%

---

# 44. Testes de regressão funcional

A modernização não poderá afetar o comportamento existente.

Validar:

- [ ] Aplicação inicia corretamente.
- [ ] Header carrega.
- [ ] Sidebar funciona.
- [ ] Tela Start funciona.
- [ ] Configurações são carregadas.
- [ ] Configurações são salvas.
- [ ] Zebra FX9600 conecta.
- [ ] Teste de conexão RFID funciona.
- [ ] Waveshare conecta.
- [ ] Teste de conexão Waveshare funciona.
- [ ] DI1–DI5 continuam sendo apresentados corretamente.
- [ ] CH1–CH8 continuam funcionando na tela de teste.
- [ ] Start inicia o modo automático.
- [ ] DI1 inicia leitura conforme RF012.
- [ ] Timer de 60 segundos funciona.
- [ ] DI2 encerra leitura conforme RF012.
- [ ] Stop funciona.
- [ ] CH1 indica sistema apto.
- [ ] CH2 indica leitura em andamento.
- [ ] CH3 indica erro.
- [ ] Backend Health funciona.
- [ ] Sistema é atualizado corretamente.
- [ ] Base de dados é atualizada corretamente.
- [ ] GET de EPC funciona.
- [ ] POST de passagem funciona.
- [ ] Deduplicação funciona.
- [ ] Tabela recebe registros.
- [ ] Contador de EPCs funciona.
- [ ] EPC inexistente continua ignorado.
- [ ] Nenhuma thread de comunicação trava a UI.

Testes visuais automatizados não devem acionar relés físicos inesperadamente.

Utilizar mocks quando apropriado.

---

# 45. Critérios de aceite — identidade visual

- [ ] Tema escuro corporativo implementado.
- [ ] Paleta centralizada.
- [ ] Logotipo DSV inserido no header.
- [ ] Logotipo sem distorção.
- [ ] Contraste do logotipo adequado.
- [ ] Header modernizado.
- [ ] Sidebar modernizada.
- [ ] Cards modernizados.
- [ ] Tabela modernizada.
- [ ] Botões modernizados.
- [ ] Inputs modernizados.
- [ ] Dropdowns modernizados.
- [ ] Ícones consistentes.
- [ ] Tipografia consistente.
- [ ] Bordas padronizadas.
- [ ] Espaçamentos consistentes.

---

# 46. Critérios de aceite — cores

- [ ] Verde representa estados positivos.
- [ ] Vermelho representa estados negativos.
- [ ] Amarelo representa atenção/processamento.
- [ ] Azul representa ações/informações.
- [ ] Cinza representa estados neutros.
- [ ] Status possuem texto e cor.
- [ ] CH1 possui representação verde.
- [ ] CH2 possui representação amarela.
- [ ] CH3 possui representação vermelha.
- [ ] Estado desconhecido não aparece como OK.
- [ ] Status pendente não é automaticamente considerado erro.
- [ ] Contraste adequado.

---

# 47. Critérios de aceite — layout

- [ ] Composição atual preservada.
- [ ] Header permanece na posição atual.
- [ ] Sidebar permanece na posição atual.
- [ ] Menus preservados.
- [ ] Cards preservados.
- [ ] Tabela preservada.
- [ ] Colunas preservadas.
- [ ] Botões operacionais preservados.
- [ ] Navegação preservada.
- [ ] Nenhuma funcionalidade removida.
- [ ] Nenhuma tela desnecessária criada.
- [ ] Aplicação continua abrindo maximizada.
- [ ] Layout validado nas resoluções definidas.

---

# 48. Critérios de aceite — arquitetura

- [ ] Biblioteca gráfica avaliada tecnicamente.
- [ ] Nenhuma migração ampla sem justificativa.
- [ ] Tema centralizado.
- [ ] Componentes visuais reutilizáveis quando adequado.
- [ ] UI separada dos serviços.
- [ ] Nenhuma lógica RFID duplicada.
- [ ] Nenhuma lógica Modbus duplicada.
- [ ] Nenhuma lógica HTTP duplicada.
- [ ] Nenhum timer operacional alterado.
- [ ] Nenhuma regra de negócio modificada.
- [ ] Nenhum problema de concorrência introduzido.
- [ ] Assets incluídos no empacotamento.
- [ ] Aplicação funciona nativamente no Windows.

---

# 49. Fora do escopo

Não implementar:

- Novo dashboard.
- Novos gráficos.
- Novos KPIs.
- Novas colunas.
- Novos endpoints.
- Alterações PostgreSQL.
- Alterações Rails.
- Alterações no protocolo LLRP.
- Alterações no protocolo Modbus.
- Alterações de sensores.
- Alterações de relés.
- Alterações de regras de EPC.
- Alterações no registro da passagem.
- Alterações na deduplicação.
- Novos fluxos operacionais.
- Sistema de múltiplos temas.
- Tela de personalização de cores.
- Autenticação.
- Novas permissões.
- Reorganização da sidebar.
- Reorganização da tela Start.

O foco é exclusivamente:

    UX/UI
    +
    Identidade visual DSV
    +
    Modernização dos componentes

---

# 50. Definição de pronto

O RF018 somente poderá ser considerado concluído quando:

1. A interface estiver visualmente modernizada.
2. O logotipo DSV estiver corretamente integrado.
3. A composição original estiver preservada.
4. Todas as telas existentes seguirem o mesmo tema.
5. Os estados positivos utilizarem verde.
6. Os estados negativos utilizarem vermelho.
7. Os estados de atenção utilizarem amarelo.
8. A tipografia estiver consistente.
9. Os botões possuírem estados visuais adequados.
10. A tabela estiver modernizada.
11. Os indicadores estiverem padronizados.
12. O sistema de cores estiver centralizado.
13. O contraste estiver adequado.
14. A aplicação funcionar nas resoluções definidas.
15. O sistema permanecer responsivo.
16. As integrações com Zebra continuarem funcionando.
17. As integrações com Waveshare continuarem funcionando.
18. As integrações com Backend continuarem funcionando.
19. Os testes de regressão passarem.
20. A aplicação estiver validada no Windows.

---

# 51. Relatório final obrigatório

Ao concluir, o Codex deverá apresentar:

### Arquitetura

- Biblioteca gráfica utilizada.
- Justificativa da escolha.
- Dependências adicionadas.
- Arquivos criados.
- Arquivos modificados.
- Componentes reutilizáveis criados.

### Identidade visual

- Paleta aplicada.
- Tipografia utilizada.
- Estratégia do logotipo.
- Localização dos assets.
- Estilo dos botões.
- Estilo dos cards.
- Estilo da tabela.
- Estilo dos indicadores.

### Preservação funcional

- Confirmação de que o layout foi preservado.
- Confirmação de que a navegação foi preservada.
- Confirmação de que o Zebra não foi alterado.
- Confirmação de que a Waveshare não foi alterada.
- Confirmação de que o Backend não foi alterado.
- Confirmação de que RF012/RF015/RF016/RF017 permanecem funcionais.

### Testes

- Testes executados.
- Resultado dos testes.
- Resoluções verificadas.
- Escalas DPI verificadas.
- Testes de hardware realizados.
- Limitações encontradas.
- Pendências.

### Evidências

Apresentar capturas de tela das interfaces modernizadas, preferencialmente comparadas com a versão anterior.

---

# 52. Resultado final esperado

A aplicação RFID deverá apresentar uma identidade visual semelhante a:

    ┌────────────────────────────────────────────────────────────┐
    │                                                            │
    │  DSV     RFID SYSTEM                        STATUS          │
    │                                                            │
    ├──────────────┬─────────────────────────────────────────────┤
    │              │                                             │
    │  MENU        │  TELA PRINCIPAL                             │
    │              │                                             │
    │  Start       │  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
    │              │  │ RFID     │ │ Sistema  │ │ Database │    │
    │  Config.     │  │ ● OK     │ │ ● OK     │ │ ● OK     │    │
    │              │  └──────────┘ └──────────┘ └──────────┘    │
    │              │                                             │
    │              │  [ Iniciar Leitura ] [ Parar Leitura ]       │
    │              │                                             │
    │              │  ┌──────────────────────────────────────┐   │
    │              │  │ EPCs encontrados                     │   │
    │              │  │                                      │   │
    │              │  │              15                      │   │
    │              │  └──────────────────────────────────────┘   │
    │              │                                             │
    │              │  ┌──────────────────────────────────────┐   │
    │              │  │ TABELA RFID                          │   │
    │              │  │                                      │   │
    │              │  │ Status | Cliente | NF | Pedido ...  │   │
    │              │  │                                      │   │
    │              │  │ ● Lido | ...                         │   │
    │              │  │ ● Lido | ...                         │   │
    │              │  └──────────────────────────────────────┘   │
    │              │                                             │
    └──────────────┴─────────────────────────────────────────────┘

IMPORTANTE:

Esse desenho é apenas uma representação conceitual dos estilos e da identidade visual.

Ele NÃO autoriza reorganizar a tela atual.

A composição existente no código continua sendo a referência estrutural.

---

# 53. Diretriz final para o Codex

A modernização deve ser tratada como um trabalho de UX/UI profissional.

Não realizar apenas uma substituição superficial de cores.

É necessário garantir:

    Consistência visual
           +
    Identidade DSV
           +
    Hierarquia da informação
           +
    Feedback operacional
           +
    Legibilidade
           +
    Acessibilidade
           +
    Estabilidade técnica

O resultado deve parecer uma aplicação corporativa moderna, e não uma interface Tkinter tradicional com cores diferentes.

Entretanto, a modernização NÃO pode comprometer o software operacional.

A prioridade permanece:

    1. Preservar funcionalidades
    2. Preservar layout
    3. Aplicar identidade DSV
    4. Modernizar componentes
    5. Garantir consistência visual
    6. Validar desempenho e estabilidade

**O RF018 estará concluído quando o software RFID apresentar uma identidade visual moderna, consistente e profissional, mantendo integralmente o comportamento operacional existente.**