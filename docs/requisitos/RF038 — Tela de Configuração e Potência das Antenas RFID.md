# RF038 — Tela de Configuração e Potência das Antenas RFID

Projeto: DSV RFID System
Requisito: RF038
Categoria: RFID / Interface / Configuração
Tecnologia: Python + PySide6/QML + sllurp/LLRP
Hardware: Zebra FX9600
Sistema operacional: Windows
Prioridade: Alta

---

## 1. OBJETIVO

Criar uma área específica no software
para configuração das antenas RFID
do reader Zebra FX9600.

Atualmente, a aplicação possui
uma área de configurações RFID.

Precisamos adicionar, dentro dessa área,
um botão que abra uma nova tela
ou modal específico para antenas RFID.

Essa nova área deverá permitir:

1. Visualizar quantas antenas
   estão conectadas/configuradas
   no reader.

2. Visualizar a lista das antenas.

3. Configurar a potência
   individual de cada antena.

4. Salvar essas configurações
   no software.

5. Preparar a base para futuras
   rotinas de calibração.

---

## 2. CONTEXTO

O DSV RFID System já se comunica
com o reader Zebra FX9600
utilizando LLRP por meio da biblioteca sllurp.

O projeto já possui suporte
à configuração de múltiplas antenas
por variável de ambiente,
por exemplo:

    RFID_ANTENNAS=1,2

Agora precisamos de uma interface visual
para facilitar a configuração
das antenas conectadas.

O objetivo é evitar que esse ajuste
fique somente por arquivo/configuração textual.

IMPORTANTE:

Esse requisito é focado em:

- Interface de configuração das antenas.
- Exibição da quantidade de antenas.
- Ajuste da potência por antena.

O mapa de leitura será tratado
em um requisito separado.

---

## 3. FLUXO GERAL

Na área de Configurações RFID,
adicionar um botão com um texto como:

    Antenas RFID

ou:

    Configurar antenas

Ao clicar nesse botão,
o sistema deverá abrir uma nova tela,
subtela, modal grande ou página dedicada,
desde que mantenha o padrão visual
do sistema.

Nessa nova tela deverão aparecer:

- Quantidade de antenas disponíveis.
- Lista das antenas.
- Status de cada antena.
- Campo de potência individual.
- Botão para salvar.
- Botão para atualizar/recarregar detecção.
- Botão opcional para testar aplicação
  das configurações.

---

## 4. DETECÇÃO DAS ANTENAS

O sistema deverá mostrar quantas antenas
estão disponíveis para uso.

O Codex deverá analisar a melhor forma
de obter essa informação, considerando
o que já existe no projeto.

Fonte preferencial da informação:

1. Antenas configuradas no software
   (lista atual já usada em runtime).

2. Quando viável, validação com o reader
   para verificar se a antena está habilitada
   e operacional.

Como resultado, a interface deverá exibir:

    Quantidade de antenas configuradas

    Quantidade de antenas ativas/disponíveis

Exemplo visual esperado:

    Antenas configuradas: 2
    Antenas detectadas: 2

ou:

    Antenas configuradas: 4
    Antenas detectadas: 3

Se não for possível confirmar
fisicamente pelo reader,
o software deverá pelo menos exibir
as antenas configuradas atualmente
e documentar essa limitação.

IMPORTANTE:

Não bloquear a tela caso o reader
esteja temporariamente indisponível.

Exibir mensagens claras.

---

## 5. LISTA DAS ANTENAS

Exibir uma listagem clara das antenas.

Para cada antena, mostrar no mínimo:

- ID da antena
- Status
- Potência configurada
- Campo para ajuste da potência

Exemplo conceitual:

    Antena 1
    Status: Ativa
    Potência: [ 27.0 ]

    Antena 2
    Status: Ativa
    Potência: [ 28.5 ]

Se houver mais antenas,
a tela deverá comportar scroll vertical,
sem quebrar o layout.

---

## 6. AJUSTE DE POTÊNCIA

Cada antena deverá ter seu próprio campo
de potência.

O Codex deverá primeiro analisar
como o Zebra FX9600 e a implementação atual
trabalham a potência de transmissão.

IMPORTANTE:

A interface deve utilizar uma unidade
clara para o usuário.

Preferência:

- Exibir em dBm, se isso for consistente
  com a implementação.

Se a biblioteca/reader trabalhar
com outro formato interno,
o Codex poderá fazer a conversão
internamente.

Caso não seja seguro converter,
poderá exibir a unidade técnica real,
desde que isso fique claro na interface.

Regras:

- Cada antena deve possuir
  uma potência independente.
- O valor deverá ser editável.
- O valor deverá ser validado.
- Não aceitar campo vazio.
- Não aceitar texto inválido.
- Não aceitar valores fora da faixa suportada.

O Codex deverá identificar a faixa real
aceita pelo reader e aplicar validação.

Exemplo:

    Potência mínima: X
    Potência máxima: Y

Não inventar uma faixa fixa
sem verificar a implementação.

---

## 7. SALVAMENTO DAS CONFIGURAÇÕES

A tela deverá possuir botão:

    Salvar configurações

Ao salvar:

- Persistir as configurações no mecanismo
  já utilizado pelo projeto.
- Preservar a estratégia atual
  de configuração do software.
- Manter compatibilidade
  com o ambiente Windows.

O Codex deverá analisar onde
essas configurações devem ser salvas.

Preferência:

- Reutilizar o arquivo/configuração
  já usada pelo projeto para RFID.

Não criar um segundo formato de configuração
desnecessário se o projeto já possui
um padrão consolidado.

---

## 8. APLICAÇÃO DAS CONFIGURAÇÕES

O Codex deverá verificar
como as configurações RFID são carregadas.

Definir comportamento claro para quando
a potência for alterada:

### Opção preferencial

Salvar a configuração e aplicar
na próxima inicialização do inventário.

### Opção aceitável

Se já existir infraestrutura segura,
permitir botão:

    Aplicar agora

porém somente se isso não criar instabilidade
na sessão ativa.

IMPORTANTE:

Não reiniciar automaticamente
o fluxo operacional sem controle.

Se houver inventário ativo,
o sistema poderá:

- Bloquear a alteração.
- Solicitar que a leitura seja parada.
- Ou informar que a nova potência
  será aplicada na próxima sessão.

O comportamento deve ser explícito.

---

## 9. INTERFACE VISUAL

A nova tela deve seguir
o padrão Corporate Dark
já utilizado no DSV RFID System.

A tela deverá conter:

- Título claro
- Resumo da quantidade de antenas
- Lista das antenas
- Campos de potência
- Botões de ação

Exemplo de organização:

    Título: Configuração de Antenas RFID

    Resumo:
        Antenas configuradas: 2
        Antenas detectadas: 2

    Card/lista:
        Antena 1
        Status
        Potência

        Antena 2
        Status
        Potência

    Ações:
        [ Recarregar ]
        [ Salvar ]
        [ Fechar ]

Não alterar a identidade visual do sistema.

---

## 10. REGRAS IMPORTANTES

Este requisito NÃO deve alterar:

- Fluxo de leitura DI1 / DI2 / DI3
- Relés CH1, CH2 e CH3
- Backend Rails
- Extra box
- Tabela da tela Start
- Filtro EPC
- Lógica de deduplicação
- Regras do RF037
- Áudio RF033/RF035

Este requisito é exclusivamente
para criar a tela de configuração
das antenas e permitir o ajuste
da potência por antena.

---

## 11. TRATAMENTO DE ERROS

Se o reader Zebra estiver indisponível:

- A tela ainda deve abrir.
- Exibir as antenas configuradas localmente,
  quando disponível.
- Informar que não foi possível validar
  as antenas no equipamento.

Se a leitura das informações falhar:

- Exibir mensagem clara.
- Não travar a interface.
- Não apagar configurações existentes.

Se houver erro ao salvar:

- Informar erro ao usuário.
- Preservar os dados preenchidos na tela.

---

## 12. TESTES OBRIGATÓRIOS

### Teste 1 — Abertura da tela

Na área de Configurações RFID,
clicar no botão de antenas.

Resultado esperado:

- Nova tela abre corretamente.

### Teste 2 — Quantidade de antenas

Com RFID_ANTENNAS=1

Resultado esperado:

- Mostrar 1 antena.

Com RFID_ANTENNAS=1,2

Resultado esperado:

- Mostrar 2 antenas.

### Teste 3 — Exibição individual

Confirmar que cada antena
aparece separadamente
com seu ID e campo de potência.

### Teste 4 — Edição de potência

Alterar a potência da Antena 1
sem alterar a Antena 2.

Resultado esperado:

- Valores independentes.

### Teste 5 — Validação

Inserir valor inválido.

Resultado esperado:

- Sistema bloquear salvamento
  ou exibir erro claro.

### Teste 6 — Salvar

Salvar as configurações.

Resultado esperado:

- Persistência correta.

### Teste 7 — Reabertura da tela

Fechar e abrir novamente.

Resultado esperado:

- Valores permanecem carregados.

### Teste 8 — Reader indisponível

Simular reader offline.

Resultado esperado:

- Tela abre
- Mensagem informativa
- Sem travamento

### Teste 9 — Regressão

Confirmar que o restante do sistema
continua funcionando normalmente.

---

## 13. CRITÉRIOS DE ACEITE

- [ ] Botão de acesso às antenas criado
      na área de Configurações RFID.
- [ ] Nova tela/modal/página criada.
- [ ] Quantidade de antenas exibida.
- [ ] Lista individual das antenas exibida.
- [ ] Campo de potência por antena criado.
- [ ] Validação de potência implementada.
- [ ] Persistência das configurações implementada.
- [ ] Mensagens de erro implementadas.
- [ ] Reader offline tratado corretamente.
- [ ] Layout Corporate Dark preservado.
- [ ] Nenhuma regressão no fluxo operacional RFID.

---

## 14. PROCEDIMENTO DO CODEX

Antes de implementar:

1. Ler AGENTS.md.
2. Verificar a branch atual.
3. Executar git status.
4. Identificar a tela Configurações RFID.
5. Identificar como o projeto carrega
   as antenas atualmente.
6. Identificar como o runtime recebe
   a lista de antenas.
7. Identificar se já existe suporte
   para potência por antena.
8. Verificar como isso é suportado
   pela implementação atual do sllurp/LLRP.

Durante a implementação:

- Reutilizar a arquitetura atual.
- Criar a tela de forma isolada.
- Não alterar o fluxo Start/Stop.
- Não alterar regras operacionais.
- Não adicionar dependências desnecessárias.

Após implementar:

1. Executar testes.
2. Validar detecção e exibição das antenas.
3. Validar edição e salvamento da potência.
4. Validar reader offline.
5. Executar git diff.
6. Informar arquivos alterados
   e testes realizados.

Não executar git reset --hard.
Não descartar alterações locais.
Não realizar commit automaticamente.
Não realizar push automaticamente.
Não realizar merge automaticamente.

---

## 15. RESULTADO ESPERADO

O DSV RFID System deverá possuir,
na área de Configurações RFID,
um acesso específico para configuração
das antenas do reader.

Ao abrir essa tela,
o usuário deverá conseguir ver:

- Quantas antenas estão configuradas/ativas.
- Quais antenas estão disponíveis.
- A potência individual de cada antena.
- Ajustar e salvar a potência
  de cada uma delas.

IMPLEMENTAR O RF038.

CRIAR A TELA DE CONFIGURAÇÃO
DE ANTENAS RFID.

EXIBIR QUANTIDADE DE ANTENAS.

PERMITIR AJUSTE DE POTÊNCIA
POR ANTENA.

PRESERVAR O RESTANTE DO SISTEMA.