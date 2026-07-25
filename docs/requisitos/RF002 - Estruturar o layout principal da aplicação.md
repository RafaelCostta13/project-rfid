# 002 - Estruturar o layout principal da aplicação

## Objetivo

Reorganizar a interface principal da aplicação RFID para criar uma estrutura visual que permita adicionar novas funcionalidades gradualmente.

A aplicação deverá possuir:

* cabeçalho principal;
* área discreta para os estados das conexões;
* menu lateral de navegação;
* área central para exibição das páginas.

---

## Contexto

Atualmente, a aplicação apresenta os estados da conexão com o reader RFID e da conexão com a internet em dois cartões na tela principal.

Nesta etapa, o objetivo é reorganizar essa interface para que ela funcione como a estrutura base de toda a aplicação.

As verificações de conexão já implementadas devem continuar funcionando. Esta funcionalidade deve alterar principalmente a organização visual da interface.

---

## Escopo

Esta funcionalidade contempla:

* iniciar a aplicação com a janela maximizada;
* criar o cabeçalho principal;
* criar um subcabeçalho com os estados das conexões;
* criar uma barra lateral de navegação;
* criar uma área central de conteúdo;
* adicionar as opções iniciais do menu;
* destacar visualmente a opção atualmente selecionada;
* preservar o funcionamento das verificações de conexão existentes.

---

## Fora do escopo

Esta funcionalidade não contempla:

* modo de tela cheia sem bordas;
* leitura de etiquetas RFID;
* inventário RFID;
* alteração das configurações do reader;
* implementação completa da página de configurações;
* banco de dados;
* autenticação;
* controle de permissões;
* menu recolhível;
* personalização de tema;
* suporte a diferentes resoluções de dispositivos móveis.

---

# Estrutura do layout

A interface deve seguir a seguinte organização:

```text
┌──────────────────────────────────────────────────────────────┐
│ Leitor RFID                                                  │
├──────────────────────────────────────────────────────────────┤
│ RFID: Conectado                         Internet: Conectado   │
├───────────────────┬──────────────────────────────────────────┤
│                   │                                          │
│ Status do sistema │                                          │
│                   │          Área de conteúdo                │
│ Configurações RFID│                                          │
│                   │                                          │
│                   │                                          │
└───────────────────┴──────────────────────────────────────────┘
```

---

## 1. Janela principal

A aplicação deve iniciar com a janela maximizada, ocupando toda a área disponível da tela.

A janela deve continuar utilizando os controles normais do sistema operacional:

* minimizar;
* maximizar ou restaurar;
* fechar.

Não deve ser utilizado modo de tela cheia sem bordas.

---

## 2. Cabeçalho

A parte superior da aplicação deve possuir um cabeçalho com o título:

```text
Leitor RFID
```

O título deve ser facilmente identificável, mas sem ocupar uma área excessiva da tela.

O cabeçalho será mantido em todas as páginas da aplicação.

---

## 3. Subcabeçalho de conexões

Abaixo do cabeçalho deve existir uma área horizontal para mostrar os estados essenciais da aplicação.

Devem ser apresentados:

```text
RFID: Conectado
Internet: Conectado
```

Os estados devem:

* utilizar texto pequeno;
* possuir aparência discreta;
* permanecer visíveis em todas as páginas;
* continuar sendo atualizados pelas verificações existentes;
* apresentar indicação textual e visual.

Exemplo:

```text
● RFID: Conectado     ● Internet: Conectado
```

Sugestão de indicação:

| Estado       | Aparência                     |
| ------------ | ----------------------------- |
| Conectado    | indicador verde               |
| Desconectado | indicador vermelho            |
| Verificando  | indicador amarelo             |
| Erro         | indicador vermelho ou laranja |

A informação não deve depender somente da cor. O texto do estado deve permanecer visível.

---

## 4. Barra lateral

A lateral esquerda da aplicação deve possuir um menu de navegação.

Nesta etapa, o menu deve conter as seguintes opções:

* **Status do sistema**
* **Configurações RFID**

A barra lateral deve permanecer visível durante a navegação entre as páginas.

A opção selecionada deve possuir um destaque visual diferente das demais.

Exemplos de destaque:

* fundo diferente;
* borda lateral;
* texto em negrito;
* combinação dessas opções.

---

## 5. Área central de conteúdo

Ao lado da barra lateral deve existir uma área destinada ao conteúdo da opção selecionada.

Essa área deve ser independente do cabeçalho, do subcabeçalho e da barra lateral.

A estrutura deve permitir a substituição do conteúdo central sem recriar toda a janela principal.

---

# Páginas iniciais

## Status do sistema

A opção **Status do sistema** deve ser selecionada por padrão ao iniciar a aplicação.

Nesta primeira versão, a página pode apresentar:

* título `Status do sistema`;
* identificação do reader configurado;
* endereço IP do reader;
* status da conexão RFID;
* status da conexão com a internet;
* data e hora da última verificação.

Os dados já disponíveis na aplicação devem ser reaproveitados.

Não é necessário criar gráficos ou histórico de eventos nesta etapa.

---

## Configurações RFID

A opção **Configurações RFID** deve estar disponível na barra lateral.

Ao selecionar essa opção, a área central deve exibir inicialmente apenas uma página provisória.

Exemplo:

```text
Configurações RFID

As configurações do reader serão disponibilizadas em uma próxima etapa.
```

Nesta funcionalidade, não deve ser implementada a alteração real de configurações.

---

# Requisitos funcionais

## RF001 — Inicializar a janela maximizada

Ao iniciar a aplicação, a janela principal deve ser aberta maximizada.

---

## RF002 — Exibir o cabeçalho

A aplicação deve exibir o título `Leitor RFID` no cabeçalho principal.

---

## RF003 — Exibir os estados no subcabeçalho

A aplicação deve exibir no subcabeçalho:

* estado da conexão RFID;
* estado da conexão com a internet.

---

## RF004 — Atualizar os estados

Os estados do subcabeçalho devem continuar sendo atualizados pelas verificações já implementadas.

A reorganização do layout não deve interromper o funcionamento atual das verificações.

---

## RF005 — Exibir a barra lateral

A aplicação deve possuir uma barra lateral com as opções:

* Status do sistema;
* Configurações RFID.

---

## RF006 — Definir a página inicial

A página **Status do sistema** deve ser exibida automaticamente ao iniciar a aplicação.

---

## RF007 — Navegar entre páginas

Ao selecionar uma opção da barra lateral, a aplicação deve atualizar somente a área central de conteúdo.

O cabeçalho, o subcabeçalho e a barra lateral devem permanecer visíveis.

---

## RF008 — Destacar a opção selecionada

A opção atualmente aberta deve possuir destaque visual na barra lateral.

---

## RF009 — Exibir página provisória de configurações

Ao selecionar **Configurações RFID**, a aplicação deve exibir uma mensagem informando que essa funcionalidade será implementada posteriormente.

---

# Requisitos não funcionais

## RNF001 — Separação dos componentes

O layout deve ser organizado em componentes ou classes separadas, considerando pelo menos:

* janela principal;
* cabeçalho;
* subcabeçalho de estados;
* barra lateral;
* área de conteúdo;
* página de status;
* página provisória de configurações.

---

## RNF002 — Preservar regras existentes

A alteração do layout não deve modificar as regras de conexão já implementadas.

A interface deve apenas consumir os estados fornecidos pela camada responsável pelas conexões.

---

## RNF003 — Não duplicar verificações

Os componentes visuais não devem criar novas conexões ou verificações independentes.

Deve existir uma única fonte de estado para:

* conexão RFID;
* conexão com a internet.

---

## RNF004 — Compatibilidade

O layout deve continuar compatível com Windows e Linux.

---

## RNF005 — Preparação para expansão

A área central deve permitir a inclusão futura de novas páginas sem necessidade de reconstruir a estrutura principal da aplicação.

---

# Regras de negócio

## RN001 — Página inicial

Ao iniciar a aplicação, a opção **Status do sistema** deve estar selecionada.

---

## RN002 — Estados globais

Os estados do RFID e da internet são informações globais da aplicação.

Por esse motivo, devem permanecer visíveis mesmo quando o usuário acessar outra página.

---

## RN003 — Configurações apenas visuais

A página **Configurações RFID** será apenas um espaço reservado nesta etapa.

Nenhuma configuração deve ser alterada no reader.

---

## RN004 — Reutilização dos estados existentes

Os estados apresentados atualmente nos cartões devem ser reutilizados no novo subcabeçalho e, quando necessário, na página de status.

Não devem existir estados divergentes em diferentes partes da interface.

---

# Critérios de aceite

## CA001

Dado que a aplicação seja iniciada, quando a janela for exibida, então ela deve estar maximizada.

## CA002

Dado que a tela principal esteja aberta, então o cabeçalho deve exibir o título `Leitor RFID`.

## CA003

Dado que a aplicação esteja em execução, então o subcabeçalho deve exibir os estados do RFID e da internet.

## CA004

Dado que um estado de conexão seja alterado, quando a interface for atualizada, então o novo estado deve aparecer no subcabeçalho.

## CA005

Dado que a aplicação seja iniciada, então a barra lateral deve exibir as opções `Status do sistema` e `Configurações RFID`.

## CA006

Dado que a aplicação seja iniciada, então a página `Status do sistema` deve aparecer selecionada.

## CA007

Dado que o usuário selecione `Configurações RFID`, então somente a área central deve ser alterada.

## CA008

Dado que uma página esteja aberta, então sua respectiva opção deve aparecer destacada na barra lateral.

## CA009

Dado que a página de configurações seja selecionada, então nenhuma configuração real do reader deve ser alterada.

## CA010

Dado que o layout tenha sido reorganizado, então as verificações de RFID e internet já existentes devem continuar funcionando.

---

# Definição de pronto

A funcionalidade será considerada concluída quando:

* a aplicação iniciar maximizada;
* o cabeçalho exibir `Leitor RFID`;
* o subcabeçalho exibir os estados do RFID e da internet;
* a barra lateral possuir as duas opções definidas;
* a página de status for exibida inicialmente;
* a navegação alterar somente a área central;
* a opção selecionada possuir destaque visual;
* a página provisória de configurações estiver disponível;
* as verificações de conexão existentes continuarem funcionando;
* nenhuma configuração persistente do reader for alterada.
