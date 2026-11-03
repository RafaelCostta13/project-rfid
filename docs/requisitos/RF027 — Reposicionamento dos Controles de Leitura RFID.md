# RF027 — Reposicionamento dos Controles de Leitura RFID

Projeto: RFID System
Requisito: RF027
Categoria: Interface / UX
Prioridade: Média
Tecnologia: Python + PySide6 + QML
Ambiente: Windows
Requisitos relacionados: RF018, RF020, RF022, RF025 e RF026
Status: A implementar

---

## 1. OBJETIVO

Reorganizar os controles de leitura RFID na interface
principal do software.

Atualmente, os botões:

- Iniciar leitura
- Parar leitura

Estão posicionados dentro do painel:

"Inventário RFID automático"

O objetivo deste requisito é:

1. Remover os dois botões da posição atual.
2. Adicionar um único botão dinâmico à barra superior
   de indicadores.
3. Posicionar esse botão após o indicador "Sistema".
4. Alternar automaticamente entre "Iniciar leitura"
   e "Parar leitura".
5. Aumentar a altura útil da tabela RFID.
6. Preservar toda a lógica operacional existente.

IMPORTANTE:

Este requisito é uma alteração de interface.

Não implementar uma nova lógica de inventário.

Reutilizar os comandos e estados já existentes
no software.

---

## 2. LAYOUT ATUAL

A aplicação possui:

### Header

- Logo DSV.
- RFID SYSTEM.
- OPERAÇÃO RFID.

### Barra de indicadores

- RFID.
- Internet.
- Comandos.
- Sistema.

### Área principal

- Card EPCs encontrados.
- Card Extra box.
- Painel Inventário RFID automático.
- Botão Iniciar leitura.
- Botão Parar leitura.
- Tabela de etiquetas RFID.

Atualmente, os botões ocupam uma área
considerável acima da tabela.

Essa área deverá ser aproveitada para
aumentar a visualização dos registros.

---

## 3. RF027.01 — REMOVER BOTÕES DA POSIÇÃO ATUAL

Localizar o componente QML responsável
pelo painel:

"Inventário RFID automático"

Remover visualmente os botões:

- Iniciar leitura.
- Parar leitura.

Não excluir os métodos Python responsáveis
pelos comandos.

Não remover os signals e slots utilizados
pela aplicação.

Não alterar as funções de Start/Stop.

Apenas transferir os controles para
a barra superior.

Não manter botões duplicados na interface.

---

## 4. RF027.02 — NOVA POSIÇÃO DO BOTÃO

Adicionar o botão de controle de leitura
na barra superior de indicadores.

Ordem visual:

1. RFID
2. Internet
3. Comandos
4. Sistema
5. Botão de controle de leitura

Representação:

| RFID | Internet | Comandos | Sistema | Iniciar leitura |

Quando o sistema estiver ativo:

| RFID | Internet | Comandos | Sistema | Parar leitura |

O botão deverá ficar à direita do
indicador Sistema.

Preservar os quatro indicadores existentes.

Não substituir o indicador Sistema.

Não alterar as regras de conectividade.

---

## 5. RF027.03 — BOTÃO DINÂMICO

Implementar um único botão QML.

Esse botão deverá alterar automaticamente:

- Texto.
- Ícone.
- Cor.
- Ação.
- Estado de habilitação.

A alteração deverá depender do estado
operacional real da aplicação.

Não criar dois botões sobrepostos.

Não utilizar temporizadores QML para
simular a mudança de estado.

Utilizar os estados e propriedades
expostos pela Qt Bridge existente.

---

## 6. RF027.04 — ESTADO INICIAR LEITURA

Quando o modo automático estiver desativado,
o botão deverá apresentar:

Texto:

    Iniciar leitura

Ícone:

    Play

Cor:

    Verde

Ao clicar:

1. Executar o comando existente de iniciar leitura.
2. Habilitar o modo automático.
3. Preservar a verificação dos pré-requisitos.
4. Aguardar a interrupção do sensor DI1.
5. Atualizar o estado do botão.

IMPORTANTE:

Clicar em "Iniciar leitura" não deverá
iniciar imediatamente o inventário RFID.

O inventário continuará dependendo de DI1.

Após a confirmação de que o modo automático
foi habilitado, o botão deverá apresentar:

    Parar leitura

---

## 7. RF027.05 — ESTADO PARAR LEITURA

Quando o modo automático estiver habilitado,
o botão deverá apresentar:

Texto:

    Parar leitura

Ícone:

    Stop

Cor:

    Vermelho

Esse comportamento deverá ser aplicado
inclusive quando o sistema estiver:

    Aguardando DI1

Ou:

    Executando inventário RFID

Ao clicar:

1. Executar o comando de parada existente.
2. Desabilitar o modo automático.
3. Encerrar o inventário, quando aplicável.
4. Preservar o tratamento dos sensores.
5. Preservar a máquina de estados.
6. Atualizar o botão após a confirmação
   da mudança de estado.

Após a parada efetiva, apresentar:

    Iniciar leitura

---

## 8. RF027.06 — REGRAS DE TRANSIÇÃO

O botão deverá acompanhar o estado real
do sistema.

### Cenário A — Sistema pronto

Modo automático:

    Desativado

Botão:

    Iniciar leitura

### Cenário B — Aguardando DI1

Modo automático:

    Ativado

Inventário:

    Não iniciado

Botão:

    Parar leitura

### Cenário C — Inventário em andamento

Modo automático:

    Ativado

Inventário:

    Ativo

Botão:

    Parar leitura

### Cenário D — Inventário encerrado por DI2

Preservar o comportamento atual do
modo automático após o encerramento.

Se o modo automático continuar habilitado:

    Parar leitura

Se o modo automático tiver sido desabilitado:

    Iniciar leitura

Não presumir que o encerramento do inventário
significa necessariamente que o modo
automático foi desabilitado.

### Cenário E — Timeout de 60 segundos

Aplicar a mesma regra do cenário D.

O botão deverá refletir o estado
efetivo do modo automático.

### Cenário F — Sistema indisponível

Quando os pré-requisitos impedirem
o início da operação:

    Iniciar leitura

Estado:

    Desabilitado

Caso o modo automático já esteja ativo
e ocorra uma falha, preservar o tratamento
de segurança existente.

Não ocultar ou desabilitar indevidamente
o comando de parada.

---

## 9. RF027.07 — ATUALIZAÇÃO AUTOMÁTICA

O botão deverá ser atualizado quando:

- O usuário iniciar o modo automático.
- O usuário parar o modo automático.
- O sistema alterar seu estado operacional.
- Ocorrer uma falha de comunicação.
- O inventário for encerrado.
- O sistema for reinicializado.

Utilizar preferencialmente as propriedades
reativas e sinais existentes na Qt Bridge.

Não utilizar uma variável QML independente
como única fonte de verdade.

O texto do botão deverá representar
o estado confirmado pelo Backend local
da aplicação Python.

Não alterar antecipadamente o estado visual
quando um comando ainda puder falhar.

---

## 10. RF027.08 — ESTILO VISUAL

Preservar o tema Corporate Dark.

### Iniciar leitura

Cor principal:

    Verde

Ícone:

    Play

Texto:

    Iniciar leitura

### Parar leitura

Cor principal:

    Vermelho

Ícone:

    Stop

Texto:

    Parar leitura

Utilizar preferencialmente as cores e
componentes já existentes no projeto.

Não introduzir uma nova paleta.

O botão deverá:

- Possuir altura compatível com a barra.
- Ter cantos arredondados.
- Possuir padding adequado.
- Manter boa legibilidade.
- Apresentar feedback visual ao passar o mouse.
- Apresentar feedback ao clicar.
- Diferenciar claramente o estado desabilitado.

Evitar botões excessivamente grandes.

O novo controle deverá ser visualmente
integrado aos indicadores de status.

---

## 11. RF027.09 — DIMENSIONAMENTO DA BARRA

A barra superior deverá continuar
apresentando os quatro indicadores.

O botão será adicionado ao lado direito.

Evitar:

- Sobreposição de elementos.
- Corte do texto.
- Alteração desnecessária da altura.
- Desalinhamento vertical.
- Redução excessiva do espaço dos indicadores.

O botão deverá possuir largura suficiente
para apresentar integralmente:

    Iniciar leitura

E:

    Parar leitura

A barra deverá continuar responsiva.

Em resoluções menores, utilizar uma solução
de layout adaptável que preserve o acesso
ao controle e aos indicadores.

Não ocultar o botão de parada.

Não utilizar posicionamento absoluto
que cause sobreposição ao redimensionar
a janela.

---

## 12. RF027.10 — AUMENTAR ALTURA DA TABELA

Após remover os botões do painel
"Inventário RFID automático",
aproveitar o espaço vertical liberado.

A tabela de etiquetas deverá ocupar
uma área maior do painel.

Objetivo:

    Maximizar a área útil de visualização
    das etiquetas RFID.

Ajustar o layout para que a tabela
se expanda verticalmente.

Não manter o espaço vazio anteriormente
reservado aos botões.

Preservar o título:

    Inventário RFID automático

Preservar o indicador de estado operacional:

    Sistema indisponível
    Aguardando DI1
    Leitura em andamento
    ...

Utilizar os textos efetivamente existentes
no projeto.

O título e o estado operacional deverão
permanecer na parte superior do painel.

A tabela deverá começar logo abaixo
dessa área, respeitando um espaçamento
visual adequado.

---

## 13. RF027.11 — REMOVER ESPAÇAMENTO DESNECESSÁRIO

Analisar os componentes QML responsáveis
pelo posicionamento vertical.

Verificar:

- Margins.
- Spacing.
- Padding.
- Layout.preferredHeight.
- Layout.fillHeight.
- Anchors.
- Alturas fixas.

Remover o espaço reservado aos botões
que serão transferidos.

Evitar valores fixos desnecessários.

A tabela deverá crescer automaticamente
quando houver espaço disponível.

Não aumentar artificialmente a altura
do painel além dos limites da janela.

Não criar barras de rolagem externas
desnecessárias.

Preservar a rolagem interna da tabela.

---

## 14. RF027.12 — TABELA RFID

Preservar integralmente o RF025.

Ordem das colunas:

    Status
    Fornecedor
    Tag
    Nota fiscal
    Volume
    Pedido
    Doca

Não modificar:

- Mapeamento dos dados.
- Largura das colunas.
- Ordem das colunas.
- Status OK.
- Status Extra box.
- Destaque amarelo.
- Contadores.
- Deduplicação.
- Atualização em tempo real.

A alteração deverá aumentar somente
a área útil vertical da tabela.

Não modificar o comportamento dos registros.

---

## 15. RF027.13 — SIDEBAR

Preservar a sidebar retrátil.

Não alterar:

- Ícones.
- Navegação.
- Botão de expansão.
- Botão de recolhimento.
- Tema.
- Largura expandida.
- Largura recolhida.

O novo botão de leitura deverá funcionar
com a sidebar expandida ou recolhida.

O layout deverá se ajustar automaticamente
ao espaço horizontal disponível.

---

## 16. RF027.14 — PRESERVAÇÃO OPERACIONAL

Não modificar:

- Zebra FX9600.
- Biblioteca sllurp.
- Protocolo LLRP.
- Configuração de antenas.
- Suporte a múltiplas antenas RF026.
- Filtro de prefixos RF023.
- Comunicação Waveshare.
- Sensores DI1 e DI2.
- Relés CH1, CH2 e CH3.
- Timer de 60 segundos.
- Máquina de estados.
- Consulta GET ao Backend.
- Registro POST de passagem.
- Classificação Extra Box.
- Deduplicação.
- Contadores RFID.

A alteração deverá ser restrita
à interface e à ligação do botão
com os comandos existentes.

---

## 17. RF027.15 — ANÁLISE OBRIGATÓRIA

Antes de implementar:

1. Ler AGENTS.md.
2. Verificar a branch atual.
3. Executar git status.
4. Localizar a barra superior de indicadores.
5. Localizar os botões Iniciar e Parar leitura.
6. Identificar os comandos Python associados.
7. Identificar as propriedades da Qt Bridge.
8. Localizar os estados do modo automático.
9. Localizar o componente da tabela.
10. Identificar o layout vertical do painel.
11. Verificar o comportamento responsivo.
12. Identificar os testes existentes.

Reutilizar componentes e propriedades
já implementados.

Não duplicar a lógica operacional.

---

## 18. RF027.16 — ESTRATÉGIA DE IMPLEMENTAÇÃO

### Etapa 1 — Inspeção

Identificar a estrutura QML atual.

### Etapa 2 — Botão dinâmico

Criar ou adaptar um componente para
apresentar Iniciar ou Parar leitura.

### Etapa 3 — Integração

Conectar o botão aos comandos existentes
da Qt Bridge.

### Etapa 4 — Barra superior

Posicionar o botão após o indicador Sistema.

### Etapa 5 — Remoção

Retirar os botões antigos do painel
de inventário.

### Etapa 6 — Layout

Redistribuir o espaço vertical liberado
para a tabela.

### Etapa 7 — Responsividade

Validar sidebar expandida e recolhida.

### Etapa 8 — Testes

Executar testes funcionais e visuais.

---

## 19. TESTES OBRIGATÓRIOS

### Teste 01 — Posição do botão

Resultado esperado:

O botão aparece após o indicador Sistema.

### Teste 02 — Sistema pronto

Resultado esperado:

Botão Iniciar leitura habilitado.

### Teste 03 — Sistema indisponível

Resultado esperado:

Botão Iniciar leitura desabilitado.

### Teste 04 — Iniciar leitura

Executar o comando.

Resultado esperado:

Modo automático habilitado.

Botão alterado para Parar leitura.

Inventário aguardando DI1.

### Teste 05 — Aguardando DI1

Resultado esperado:

Botão Parar leitura permanece visível.

### Teste 06 — Inventário ativo

Interromper DI1 em simulação.

Resultado esperado:

Inventário iniciado.

Botão Parar leitura permanece visível.

### Teste 07 — Parar leitura

Executar o comando.

Resultado esperado:

Modo automático desabilitado.

Inventário encerrado conforme regras atuais.

Botão alterado para Iniciar leitura.

### Teste 08 — Encerramento por DI2

Resultado esperado:

Inventário encerrado.

Botão atualizado conforme o estado
real do modo automático.

### Teste 09 — Timeout

Simular timeout de 60 segundos.

Resultado esperado:

Inventário encerrado.

Botão atualizado conforme o estado
real do modo automático.

### Teste 10 — Falha no comando

Simular falha ao iniciar.

Resultado esperado:

Botão não apresenta falsamente
o estado Parar leitura.

### Teste 11 — Falha de conectividade

Simular perda de comunicação.

Resultado esperado:

Estados de segurança preservados.

Comando de parada acessível quando aplicável.

### Teste 12 — Tabela expandida

Resultado esperado:

Tabela ocupa o espaço liberado.

Nenhum espaço vazio desnecessário
permanece no lugar dos botões.

### Teste 13 — Sidebar expandida

Resultado esperado:

Barra superior e tabela organizadas.

### Teste 14 — Sidebar recolhida

Resultado esperado:

Barra superior e tabela organizadas.

### Teste 15 — Redimensionamento

Reduzir e aumentar a janela.

Resultado esperado:

Sem sobreposição de indicadores e botão.

### Teste 16 — Regressão

Validar:

- Start/Stop.
- DI1.
- DI2.
- Timer.
- Relés.
- RFID.
- Backend.
- Extra Box.
- Filtro EPC.
- Múltiplas antenas.
- Tabela QML.

Nenhuma regressão operacional.

---

## 20. CRITÉRIOS DE ACEITE

- [ ] Botões removidos do painel de inventário.
- [ ] Um único botão dinâmico implementado.
- [ ] Botão posicionado após Sistema.
- [ ] Texto Iniciar leitura quando desativado.
- [ ] Texto Parar leitura quando ativado.
- [ ] Ícone Play no estado Iniciar.
- [ ] Ícone Stop no estado Parar.
- [ ] Cor verde para Iniciar.
- [ ] Cor vermelha para Parar.
- [ ] Estado desabilitado respeitado.
- [ ] Comandos Python existentes reutilizados.
- [ ] Nenhuma duplicação de lógica operacional.
- [ ] Botão atualizado pelo estado real da aplicação.
- [ ] Inventário continua aguardando DI1.
- [ ] Botão Parar disponível durante modo automático.
- [ ] Tabela expandida verticalmente.
- [ ] Espaço vazio dos botões removido.
- [ ] Layout responsivo.
- [ ] Sidebar preservada.
- [ ] Indicadores preservados.
- [ ] RF025 preservado.
- [ ] RF026 preservado.
- [ ] Testes aprovados.
- [ ] Nenhuma regressão operacional.

---

## 21. FORA DO ESCOPO

Não implementar:

- Nova máquina de estados.
- Novos comandos RFID.
- Novos controles de sensores.
- Novos relés.
- Alterações no timer.
- Alterações no Backend.
- Alterações na tabela.
- Novos cards.
- Novos indicadores.
- Alterações no protocolo LLRP.
- Mudanças nas configurações de antenas.
- Redesenho completo do Dashboard.

---

## 22. RELATÓRIO FINAL

Ao concluir, apresentar:

1. Branch utilizada.
2. Arquivos modificados.
3. Componentes QML alterados.
4. Localização do novo botão.
5. Propriedade utilizada para determinar o estado.
6. Comandos Python reutilizados.
7. Regras de habilitação e desabilitação.
8. Ajustes de altura da tabela.
9. Comportamento responsivo.
10. Testes realizados.
11. Resultados dos testes.
12. Confirmação de preservação operacional.

Não realizar commit ou merge automaticamente.

---

## 23. DEFINIÇÃO DE PRONTO

O RF027 estará concluído quando:

1. Os botões Iniciar e Parar leitura não estiverem
   mais no painel de inventário.
2. Um único botão dinâmico estiver disponível
   após o indicador Sistema.
3. O botão alternar corretamente entre
   Iniciar leitura e Parar leitura.
4. O controle continuar utilizando os comandos
   e estados operacionais existentes.
5. A tabela RFID ocupar o espaço vertical
   anteriormente utilizado pelos botões.
6. A interface permanecer responsiva.
7. Nenhuma funcionalidade operacional regredir.

IMPLEMENTAR O RF027 PRIORIZANDO
SIMPLICIDADE, USABILIDADE E PRESERVAÇÃO
DA ARQUITETURA EXISTENTE.