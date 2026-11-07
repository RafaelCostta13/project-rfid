# RF032 — Inicialização Automática e Status de Prontidão RFID

Projeto: DSV RFID System
Requisito: RF032
Categoria: Automação / Controle operacional / Interface
Tecnologia: Python + PySide6/QML
Prioridade: Alta

---

## 1. OBJETIVO

Implementar a habilitação automática do modo
de leitura RFID durante a inicialização do software.

Atualmente, o operador precisa clicar no botão:

    Iniciar leitura

Para habilitar o funcionamento automático
do sistema RFID.

O novo comportamento deverá permitir que,
ao abrir o programa, o software habilite
automaticamente esse mesmo modo operacional
quando todos os indicadores estiverem OK.

Indicadores obrigatórios:

1. RFID
2. Internet
3. Comandos
4. Sistema

IMPORTANTE:

A lógica atual do botão Iniciar leitura
e Parar leitura está funcionando corretamente.

O RF032 não deverá reimplementar essa lógica.

A inicialização automática deverá reutilizar
o mesmo fluxo operacional já existente.

---

## 2. COMPORTAMENTO ATUAL

Atualmente:

1. O software é aberto.
2. Os serviços são inicializados.
3. O sistema verifica as conexões.
4. O operador clica em Iniciar leitura.
5. O modo automático é habilitado.
6. O sistema aguarda o sensor DI1.
7. Quando DI1 é interrompido, inicia
   o inventário RFID.
8. O inventário termina por DI2 ou timeout.

O botão Parar leitura desabilita
o modo automático.

Essa lógica deverá ser preservada.

---

## 3. NOVO COMPORTAMENTO

Ao abrir o programa:

1. Inicializar normalmente a aplicação.
2. Inicializar os serviços existentes.
3. Verificar os quatro indicadores.
4. Aguardar a conclusão das verificações.
5. Confirmar que todos estão OK.
6. Executar internamente a mesma operação
   utilizada pelo botão Iniciar leitura.
7. Habilitar o modo automático.
8. Apresentar o status:

    Pronto para leitura

9. Aguardar a interrupção do sensor DI1.

Não exigir que o operador clique
manualmente em Iniciar leitura.

ATENÇÃO:

Habilitar o modo automático não significa
iniciar imediatamente o inventário RFID.

O inventário continua dependendo do DI1.

---

## 4. PRÉ-REQUISITOS

A habilitação automática somente poderá
ocorrer quando os quatro indicadores
estiverem em condição positiva.

Condições obrigatórias:

    RFID = OK
    Internet = OK
    Comandos = OK
    Sistema = OK

Utilizar os mesmos critérios de prontidão
já implementados para o botão Iniciar leitura.

Não criar verificações alternativas.

Não considerar os estados abaixo como OK:

- Desconectado.
- Verificando.
- Indisponível.
- Erro.
- Estado desconhecido.

Não considerar um indicador OK apenas
porque uma conexão foi iniciada.

A condição deve refletir o estado real
dos serviços existentes.

Preservar também as validações operacionais
e de segurança atualmente aplicadas
ao início do modo automático.

---

## 5. NOVO STATUS: PRONTO PARA LEITURA

Adicionar ou ajustar o indicador de estado
existente no painel:

    Inventário RFID automático

Quando o modo automático estiver habilitado,
todos os serviços estiverem OK e o sistema
estiver aguardando o início do inventário,
exibir:

    Pronto para leitura

Cor:

    Verde

Utilizar a mesma paleta positiva
do tema Corporate Dark.

Esse status significa:

- Sistema conectado.
- Serviços operacionais.
- Modo automático habilitado.
- Aguardando o sensor de entrada.
- Nenhum inventário em andamento.

Não utilizar esse status enquanto
o inventário estiver efetivamente ativo.

---

## 6. NOVO STATUS: LEITURA PARADA

Quando o modo automático estiver desabilitado,
ou algum dos quatro serviços obrigatórios
estiver indisponível, exibir:

    Leitura parada

Cor:

    Vermelho

Exemplos:

- RFID desconectado.
- Internet desconectada.
- Comandos desconectados.
- Sistema indisponível.
- Operador acionou Parar leitura.
- Aplicação ainda não atingiu as condições
  necessárias para habilitar a leitura.

Durante a inicialização, enquanto
os serviços estiverem sendo verificados,
não apresentar falsamente o sistema
como pronto.

Preservar estados de erro específicos
quando exigidos pela lógica operacional.

---

## 7. LEITURA EM ANDAMENTO

Quando DI1 iniciar o inventário RFID,
preservar o estado de leitura existente.

Não apresentar:

    Pronto para leitura

Enquanto o inventário estiver ativo.

Manter a indicação operacional de
leitura em andamento já utilizada
pelo software.

Preservar:

- Timer de 60 segundos.
- Estado de leitura.
- Contagem de EPCs.
- Processamento das etiquetas.
- Comunicação com o backend.
- Acionamento dos relés.

Após o encerramento normal do inventário,
se o modo automático continuar habilitado
e os serviços estiverem OK, retornar para:

    Pronto para leitura

---

## 8. PRESERVAR BOTÃO INICIAR/PARAR LEITURA

O RF031 posicionou o botão dinâmico
no cabeçalho superior do aplicativo.

Preservar esse posicionamento.

### 8.1 Inicialização automática bem-sucedida

Quando o sistema habilitar automaticamente
o modo de leitura:

O botão deverá apresentar:

    Parar leitura

Exatamente como acontece atualmente
quando o operador clica em Iniciar leitura.

### 8.2 Parada manual

Quando o operador clicar em:

    Parar leitura

O sistema deverá:

1. Executar o comando atual de parada.
2. Desabilitar o modo automático.
3. Preservar o comportamento dos relés.
4. Atualizar o status para:

    Leitura parada

5. Apresentar o botão:

    Iniciar leitura

IMPORTANTE:

Uma parada manual deverá ser respeitada.

Não reativar automaticamente a leitura
apenas porque os quatro indicadores
continuam OK.

O operador deverá clicar em Iniciar leitura
para retomar o funcionamento nessa sessão.

Ao reiniciar o aplicativo, a política
de inicialização automática volta a valer.

### 8.3 Início manual

Quando o operador clicar em:

    Iniciar leitura

Preservar integralmente a lógica atual.

Não criar um segundo fluxo de inicialização.

---

## 9. RECUPERAÇÃO AUTOMÁTICA DE CONEXÕES

Cenário:

O programa foi aberto, mas um dos
serviços estava indisponível.

Exemplo:

    RFID = OK
    Internet = OK
    Comandos = Desconectado
    Sistema = OK

Resultado:

    Leitura parada

Posteriormente, a comunicação
com Comandos é restabelecida.

Novo cenário:

    RFID = OK
    Internet = OK
    Comandos = OK
    Sistema = OK

Resultado esperado:

O software deverá habilitar
automaticamente o modo de leitura.

Exibir:

    Pronto para leitura

Essa recuperação deverá ocorrer
sem necessidade de reiniciar o programa.

IMPORTANTE:

A recuperação automática somente deverá
acontecer quando não houver uma parada
manual vigente na sessão.

Reutilizar os mecanismos de monitoramento
e reconexão existentes.

---

## 10. PERDA DE CONEXÃO DURANTE A OPERAÇÃO

Se algum serviço obrigatório ficar
indisponível durante o funcionamento:

1. Detectar a alteração do estado.
2. Impedir novos inventários enquanto
   os pré-requisitos estiverem inválidos.
3. Aplicar o procedimento seguro de parada
   ou falha já implementado.
4. Preservar as regras de encerramento
   e tratamento de inventários ativos.
5. Atualizar o indicador operacional.
6. Não apresentar Pronto para leitura
   enquanto houver falha.

Status esperado quando a leitura
estiver efetivamente desabilitada:

    Leitura parada

Quando os serviços forem recuperados,
o sistema poderá voltar automaticamente
ao modo de prontidão, desde que não exista
uma parada manual vigente.

Não ignorar falhas de comunicação.

Não alterar os comportamentos de segurança
da máquina de estados.

---

## 11. PRESERVAR A LÓGICA DOS SENSORES

Não modificar o funcionamento dos sensores:

    DI1 = Sensor de entrada
    DI2 = Sensor de saída

Preservar a interpretação atual:

- Sensor normal: ativo.
- Sensor interrompido: entrada desativada.

O novo fluxo deverá continuar funcionando
da seguinte maneira:

ESTADO PRONTO:

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

Conforme as condições de segurança atuais.

DI1 INTERROMPIDO:

    Iniciar inventário RFID.
    Iniciar timer de até 60 segundos.

    CH1 = OFF
    CH2 = ON
    CH3 = OFF

DI2 INTERROMPIDO:

    Encerrar inventário.

    CH1 = ON
    CH2 = OFF
    CH3 = OFF

AMBOS OS SENSORES INTERROMPIDOS:

    Preservar condição de erro.

    CH1 = OFF
    CH2 = OFF
    CH3 = ON

Preservar todas as proteções existentes.

O RF032 não deverá modificar
a máquina de estados dos sensores.

---

## 12. IMPLEMENTAÇÃO PYTHON / QT

Identificar a implementação atual
responsável pelo comando Iniciar leitura.

Reutilizar o método ou serviço existente.

A inicialização automática deverá
ser implementada preferencialmente
na camada de controle Python.

Não simular um clique no botão QML.

Não implementar uma lógica paralela
somente na interface.

Não duplicar:

- Controladores de inventário.
- Conexões LLRP.
- Conexões seriais.
- Threads de monitoramento.
- Timers.
- Requisições HTTP.

O estado real deverá continuar sendo
publicado para a interface por meio
do Qt Bridge existente.

A interface deverá apenas refletir
o estado operacional recebido.

---

## 13. CONTROLE DE INICIALIZAÇÃO

Implementar a habilitação automática
de forma segura e idempotente.

Requisitos:

1. Não executar Start repetidamente
   quando os indicadores permanecerem OK.

2. Não iniciar múltiplos inventários.

3. Não criar múltiplas conexões com o leitor.

4. Não iniciar automaticamente enquanto
   os serviços ainda estão sendo inicializados.

5. Não bloquear a thread principal da GUI.

6. Não permitir condições de corrida entre
   inicialização automática e comando manual.

7. Não reativar o modo automático após
   uma parada manual na mesma sessão.

8. Preservar o encerramento seguro
   ao fechar o aplicativo.

9. Não persistir uma parada manual de
   sessão como bloqueio permanente para
   as próximas inicializações.

Reutilizar a arquitetura de concorrência
já existente no projeto.

---

## 14. NOVA LÓGICA DE ESTADO

A apresentação visual deverá considerar
o estado real da operação.

REGRAS:

Se o inventário estiver em andamento:

    Preservar estado de leitura ativa.

Se o modo automático estiver habilitado,
todos os serviços estiverem OK e o
sistema estiver apto a aguardar DI1:

    Pronto para leitura
    Cor verde

Se o modo automático estiver desabilitado:

    Leitura parada
    Cor vermelha

Se algum serviço obrigatório estiver
indisponível e a leitura não puder operar:

    Leitura parada
    Cor vermelha

Se houver uma condição de erro específica:

    Preservar o tratamento de erro
    da implementação existente.

Não derivar o status somente das cores
dos quatro indicadores.

Considerar também o estado real
do modo automático e do inventário.

---

## 15. INTERFACE QML

Modificar somente os componentes
necessários para apresentar os novos estados.

Localizar o indicador de estado existente
no painel Inventário RFID automático.

Exemplos atuais:

    Sistema indisponível

Atualizar a apresentação conforme
as novas regras:

    Pronto para leitura
    Leitura parada

Preservar:

- Fonte.
- Posicionamento.
- Espaçamento.
- Alinhamento.
- Tema Corporate Dark.
- Responsividade.

Não criar novos cards.

Não adicionar novos botões.

Não modificar a sidebar.

Não modificar a página Status do RF031.

A página Status continuará exibindo
os quatro indicadores individuais.

---

## 16. TESTES OBRIGATÓRIOS

### TESTE 1 — Inicialização com todos OK

Simular:

    RFID = OK
    Internet = OK
    Comandos = OK
    Sistema = OK

Resultado:

- Modo automático habilitado.
- Status Pronto para leitura.
- Cor verde.
- Botão Parar leitura.
- Inventário ainda não iniciado.

### TESTE 2 — Inicialização com falha

Simular:

    RFID = OK
    Internet = OK
    Comandos = Desconectado
    Sistema = OK

Resultado:

- Modo automático não habilitado.
- Status Leitura parada.
- Cor vermelha.
- Nenhum inventário iniciado.

### TESTE 3 — Recuperação

Simular:

1. Iniciar com Comandos desconectado.
2. Restaurar a conexão.
3. Confirmar os quatro indicadores OK.

Resultado:

- Habilitação automática.
- Status Pronto para leitura.
- Nenhuma duplicação de serviços.

### TESTE 4 — Parada manual

Simular:

1. Inicialização automática bem-sucedida.
2. Operador clica em Parar leitura.

Resultado:

- Modo automático desabilitado.
- Status Leitura parada.
- Botão Iniciar leitura.

Confirmar que o sistema não reinicia
sozinho enquanto os indicadores
permanecerem OK.

### TESTE 5 — Reinício após parada manual

Simular:

1. Parada manual.
2. Fechamento do aplicativo.
3. Nova inicialização.
4. Todos os indicadores OK.

Resultado:

- Modo automático habilitado novamente.

### TESTE 6 — Início manual

Simular:

1. Parada manual.
2. Operador clica em Iniciar leitura.

Resultado:

- Modo automático habilitado.
- Status Pronto para leitura.
- Botão Parar leitura.

### TESTE 7 — Sensor DI1

Com o sistema pronto:

1. Interromper DI1.
2. Confirmar início do inventário.
3. Confirmar timer.
4. Confirmar relés.

### TESTE 8 — Sensor DI2

Durante o inventário:

1. Interromper DI2.
2. Confirmar encerramento.
3. Confirmar retorno ao estado
   de prontidão quando aplicável.

### TESTE 9 — Timeout

Confirmar encerramento após
o tempo máximo de 60 segundos.

Preservar a lógica atual.

### TESTE 10 — Perda de conexão

Simular perda de um dos quatro
serviços durante o modo automático.

Confirmar:

- Estado operacional seguro.
- Bloqueio de novos inventários.
- Status coerente.
- Recuperação conforme as regras.

### TESTE 11 — Inicialização repetida

Simular múltiplas atualizações
dos indicadores com estado OK.

Confirmar:

- Apenas uma habilitação do modo automático.
- Nenhuma conexão duplicada.
- Nenhum inventário duplicado.

### TESTE 12 — Regressão

Executar os testes existentes para:

- RFID.
- Waveshare.
- Sensores.
- Relés.
- Backend.
- Extra box.
- Qt Bridge.
- Interface QML.

Utilizar mocks e simulações
quando não houver hardware disponível.

---

## 17. PRESERVAR FUNCIONALIDADES

Não modificar:

- Zebra FX9600.
- Protocolo LLRP.
- Configuração de múltiplas antenas.
- Filtro de EPC.
- Comunicação Waveshare.
- Sensores DI1 e DI2.
- Relés CH1, CH2 e CH3.
- Timeout de inventário.
- Consulta GET ao Backend.
- Registro POST de passagem.
- Classificação Extra box.
- Deduplicação.
- Contadores.
- Tabela RF030.
- Sidebar e página Status RF031.
- Ícone Windows.
- Configurações persistentes.
- Logs.
- Build PyInstaller.
- GitHub Actions.

Não alterar o contrato da API Rails.

---

## 18. PROCEDIMENTO DO CODEX

Antes de implementar:

1. Ler AGENTS.md.
2. Verificar a branch atual.
3. Executar git status.
4. Identificar a lógica atual do botão Start.
5. Identificar a lógica atual do botão Stop.
6. Identificar o monitoramento dos indicadores.
7. Identificar a máquina de estados.
8. Identificar os componentes QML envolvidos.
9. Analisar os testes existentes.
10. Preservar alterações locais.

Durante a implementação:

- Reutilizar os serviços existentes.
- Realizar alterações mínimas.
- Não duplicar lógica.
- Preservar segurança operacional.
- Evitar mudanças desnecessárias.

Após a implementação:

1. Executar os testes relevantes.
2. Validar os estados operacionais.
3. Validar os novos textos.
4. Validar as cores.
5. Validar o botão Start/Stop.
6. Validar o comportamento automático.
7. Verificar git diff.
8. Identificar possíveis regressões.

Não executar git reset --hard.
Não descartar alterações locais.

Não realizar commit automaticamente.
Não realizar push automaticamente.
Não realizar merge na main.

---

## 19. CRITÉRIOS DE ACEITE

- [ ] Inicialização automática implementada.
- [ ] Quatro indicadores obrigatórios.
- [ ] Mesma lógica do botão Iniciar leitura.
- [ ] Sem inventário imediato ao abrir.
- [ ] Pronto para leitura exibido em verde.
- [ ] Leitura parada exibido em vermelho.
- [ ] Estado de leitura ativa preservado.
- [ ] Botão Iniciar/Parar funcionando.
- [ ] Botão atualizado após início automático.
- [ ] Parada manual respeitada.
- [ ] Recuperação automática funcionando.
- [ ] Nenhuma inicialização duplicada.
- [ ] Segurança dos sensores preservada.
- [ ] Relés preservados.
- [ ] Timeout preservado.
- [ ] Qt Bridge preservado.
- [ ] Interface RF031 preservada.
- [ ] Testes automatizados aprovados.
- [ ] Nenhuma regressão operacional.

---

## 20. RELATÓRIO FINAL

Ao finalizar, informar:

1. Branch utilizada.
2. Arquivos modificados.
3. Método reutilizado para habilitar leitura.
4. Como a inicialização automática foi acionada.
5. Como os quatro indicadores são verificados.
6. Como a parada manual é respeitada.
7. Como a recuperação automática funciona.
8. Como os estados são enviados ao QML.
9. Testes executados.
10. Resultados dos testes.
11. Riscos identificados.
12. Pendências de teste com hardware real.

IMPLEMENTAR O RF032.

OBJETIVO PRINCIPAL:

AO ABRIR O DSV RFID SYSTEM, QUANDO RFID,
INTERNET, COMANDOS E SISTEMA ESTIVEREM OK,
HABILITAR AUTOMATICAMENTE O MODO DE LEITURA.

EXIBIR:

    PRONTO PARA LEITURA — VERDE

QUANDO A LEITURA ESTIVER DESABILITADA:

    LEITURA PARADA — VERMELHO

PRESERVAR INTEGRALMENTE O FUNCIONAMENTO
ATUAL DO BOTÃO INICIAR/PARAR LEITURA
E TODA A LÓGICA OPERACIONAL RFID.