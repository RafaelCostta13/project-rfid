# RF033 — Notificação Sonora para EPCs Encontrados

Projeto: DSV RFID System
Requisito: RF033
Categoria: RFID / Notificações / Interface
Tecnologia: Python + PySide6/QML
Plataforma de destino: Windows
Prioridade: Média

---

## 1. OBJETIVO

Implementar uma notificação sonora para cada
EPC novo encontrado durante uma sessão RFID.

A notificação deverá utilizar a saída de áudio
do computador Windows.

O som escolhido é:

    bip_01_suave.wav

Características:

    Frequência: 880 Hz
    Duração: 80 ms
    Intervalo mínimo: 300 ms
    Formato: WAV

O sistema deverá emitir um bip curto para
cada EPC válido e encontrado, sem repetir
o som para o mesmo EPC na sessão.

IMPORTANTE:

A implementação não poderá interferir
no desempenho ou na lógica operacional RFID.

---

## 2. ANÁLISE INICIAL

Antes de implementar:

1. Ler AGENTS.md.
2. Identificar a branch atual.
3. Executar git status.
4. Verificar alterações locais.
5. Identificar o processamento de EPCs.
6. Identificar a lógica de deduplicação.
7. Identificar a classificação Extra box.
8. Identificar os eventos do Qt Bridge.
9. Identificar a estrutura de recursos.
10. Identificar o build Windows existente.
11. Identificar os testes automatizados.

Reutilizar os componentes existentes.

Não criar um segundo fluxo de processamento
de etiquetas.

---

## 3. REGRA PRINCIPAL

Quando o leitor Zebra FX9600 identificar
um EPC, o sistema deverá seguir normalmente
o processamento existente:

1. Receber o EPC.
2. Normalizar o EPC.
3. Aplicar o filtro de prefixos autorizados.
4. Verificar a deduplicação da sessão.
5. Consultar o Backend Rails.
6. Classificar o registro.
7. Atualizar a sessão e a interface.
8. Emitir o bip quando aplicável.

O bip deverá ser solicitado somente quando
um EPC novo for classificado como encontrado
e incluído entre os registros normais (OK)
da sessão.

Não emitir som apenas porque o leitor
detectou uma etiqueta fisicamente.

A consulta e a classificação existentes
continuam sendo obrigatórias.

---

## 4. CONDIÇÕES PARA EMITIR O BIP

Emitir um bip quando:

- O EPC passou pelo filtro autorizado.
- O EPC pertence à sessão atual.
- O EPC ainda não recebeu bip nessa sessão.
- A consulta à API foi bem-sucedida.
- O registro foi classificado como OK.
- O registro foi incluído nos EPCs encontrados.

Não emitir bip para:

- EPCs repetidos na sessão.
- EPCs rejeitados pelo filtro.
- EPCs classificados como Extra box.
- Respostas HTTP 404.
- Erros HTTP.
- Falhas de comunicação.
- Registros inválidos.
- Eventos simulados sem confirmação
  de classificação como encontrado.

A notificação sonora não representa
confirmação de sucesso do POST de passagem.

Ela representa a identificação de um EPC
válido e encontrado na sessão.

Preservar integralmente a lógica existente
de consulta e registro.

---

## 5. DEDUPLICAÇÃO DO SOM

O Zebra FX9600 pode identificar o mesmo EPC
diversas vezes durante um inventário.

Também é possível que antenas diferentes
identifiquem o mesmo EPC.

Exemplo:

    Antena 1 -> EPC A
    Antena 2 -> EPC A
    Antena 1 -> EPC A
    Antena 2 -> EPC B

Resultado:

    EPC A -> 1 bip
    EPC B -> 1 bip

Não emitir quatro bips.

IMPORTANTE:

Reutilizar a deduplicação de negócio
existente para os EPCs encontrados.

Não utilizar a deduplicação física
por antena como critério para emitir som.

Não criar um novo conceito de sessão.

O controle de notificações deverá seguir
o mesmo escopo de sessão utilizado
pelos contadores e pela tabela RFID.

---

## 6. ARQUIVO DE ÁUDIO

Utilizar o arquivo fornecido pelo usuário:

    bip_01_suave.wav

Local recomendado:

    src/rfid_reader/assets/sounds/bip_01_suave.wav

Verificar a estrutura real do projeto
e ajustar o caminho se necessário.

Não utilizar sons genéricos do Windows.

Não substituir o áudio por:

- Som de erro.
- Som de alerta do sistema.
- Notificação padrão do Windows.
- Beep do terminal.

O objetivo é utilizar exatamente
o som suave escolhido.

Caso o arquivo não esteja disponível,
informar a ausência e não substituir
silenciosamente por outro som.

---

## 7. INTERVALO ENTRE OS BIPS

Implementar um intervalo mínimo de:

    300 milissegundos

Esse intervalo será contado entre
o início de dois bips consecutivos.

Exemplo:

    EPC A -> Bip em 0 ms
    EPC B -> Bip em 300 ms
    EPC C -> Bip em 600 ms
    EPC D -> Bip em 900 ms

Cada bip tem duração aproximada de 80 ms.

O objetivo é impedir que os sons
se sobreponham ou formem um ruído contínuo.

Não utilizar time.sleep() na thread
principal da interface.

Não utilizar pausas no processamento RFID.

Não atrasar consultas à API.

Não atrasar o inventário.

---

## 8. FILA DE NOTIFICAÇÕES

Implementar um mecanismo de fila
para organizar as notificações sonoras.

Exemplo:

O leitor identifica cinco EPCs
em um intervalo muito curto.

O sistema deverá:

1. Processar os cinco EPCs normalmente.
2. Atualizar os registros sem atraso.
3. Adicionar os cinco eventos sonoros à fila.
4. Reproduzir os bips sequencialmente.
5. Respeitar o intervalo mínimo de 300 ms.

A fila de áudio deverá ser independente
da fila de processamento RFID.

A emissão sonora não deverá bloquear:

- Leitura LLRP.
- Consultas HTTP.
- Registro de passagem.
- Atualização dos contadores.
- Atualização da tabela.
- Monitoramento dos sensores.
- Controle dos relés.

Implementar proteção contra crescimento
excessivo da fila em situações anormais.

Se houver sobrecarga, preservar sempre
o processamento RFID e registrar
qualquer descarte de notificação sonora.

Nunca descartar um EPC de negócio
por causa de uma falha na fila de áudio.

---

## 9. IMPLEMENTAÇÃO TÉCNICA

O projeto utiliza Python e PySide6.

Preferir uma implementação simples,
compatível com Windows e com a arquitetura
Qt existente.

Abordagem recomendada:

- Qt Signal para receber o evento de EPC OK.
- QTimer para controlar o intervalo.
- Fila de eventos sonoros.
- winsound.PlaySound no Windows,
  com reprodução assíncrona.

Utilizar as flags adequadas para
reprodução de arquivo WAV sem bloquear
a thread principal.

Avaliar a implementação real antes
de escolher a integração definitiva.

Não utilizar winsound.Beep como substituto
do arquivo WAV escolhido.

Não adicionar dependências externas
desnecessárias.

A implementação deverá continuar
permitindo testes em Linux por meio
de mocks ou abstração do backend de áudio.

A ausência de winsound em Linux
não poderá impedir a inicialização
do aplicativo ou a execução dos testes.

---

## 10. LOCAL DA LÓGICA

A decisão de emitir o bip deverá
ocorrer na camada Python responsável
pela classificação do EPC.

A reprodução sonora deverá ficar
em um serviço ou componente específico.

Separar:

    Decisão de negócio
        EPC encontrado -> notificar

    Serviço de áudio
        Receber evento -> organizar fila
        -> reproduzir WAV

Não colocar toda a lógica de áudio
diretamente no QML.

Não colocar reprodução bloqueante
no callback de leitura do Zebra.

Não duplicar consultas à API
para decidir se o bip deve ocorrer.

---

## 11. NAVEGAÇÃO ENTRE TELAS

O RF031 implementou:

- Start.
- Status.
- Configurações.

A notificação sonora deverá funcionar
independentemente da página selecionada.

Exemplo:

O operador está na página Status.

O leitor identifica um EPC válido.

Resultado:

    O bip deverá ser reproduzido.

Não limitar a reprodução ao momento
em que StartPage.qml estiver visível.

O serviço de áudio deverá permanecer
disponível durante a sessão operacional
da aplicação.

---

## 12. CONFIGURAÇÕES DE ÁUDIO

Adicionar suporte para habilitar
ou desabilitar a notificação sonora.

Configuração:

    Som de leitura

Valores:

    Ativado
    Desativado

Valor padrão:

    Ativado

Adicionar também o intervalo mínimo:

    Intervalo entre bips

Valor padrão:

    300 ms

Permitir configuração dentro de limites
seguros e adequados à duração do som.

Sugestão de intervalo permitido:

    200 ms até 1000 ms

Utilizar o mecanismo de persistência
já existente no aplicativo.

Não criar outro arquivo de configuração
sem necessidade.

Não modificar as configurações de:

- RFID.
- Waveshare.
- Backend.
- Filtro de EPC.

Ao desabilitar o som, interromper
as notificações pendentes sem afetar
a leitura RFID.

---

## 13. COMPORTAMENTO AO PARAR A LEITURA

O sistema possui o botão dinâmico:

    Iniciar leitura / Parar leitura

Preservar integralmente sua lógica.

Quando o operador clicar em Parar leitura:

1. Executar a parada operacional existente.
2. Cancelar os bips ainda pendentes.
3. Não emitir sons atrasados de uma
   sessão que já foi encerrada.
4. Preservar os registros processados.
5. Preservar os contadores.

Ao iniciar uma nova sessão:

- Seguir a deduplicação dessa sessão.
- Permitir notificações para novos EPCs.
- Não reutilizar eventos sonoros antigos.

Não modificar a lógica de Start/Stop.

---

## 14. INICIALIZAÇÃO AUTOMÁTICA RF032

O RF032 implementou a habilitação
automática do modo de leitura quando
os quatro indicadores estiverem OK.

Preservar esse comportamento.

Não emitir bip apenas porque o sistema
entrou em:

    Pronto para leitura

Não emitir bip durante:

- Inicialização do aplicativo.
- Verificação de conectividade.
- Conexão com o leitor.
- Ativação do modo automático.

Emitir som somente quando houver
um novo EPC classificado como encontrado.

---

## 15. EXTRA BOX

Preservar integralmente as regras
de classificação Extra box.

Nesta versão:

    EPC normal encontrado -> Bip suave

    EPC Extra box -> Sem bip

Não criar som de erro para Extra box.

Não modificar:

- Cores.
- Contadores.
- Regras de classificação.
- Deduplicação.
- Mapeamento da API.

Um som específico para Extra box
poderá ser implementado futuramente
em outro requisito.

---

## 16. FALHAS DE ÁUDIO

A ausência de um dispositivo de áudio
não poderá interromper o sistema RFID.

Exemplos:

- Computador sem alto-falantes.
- Saída de áudio desconectada.
- Arquivo WAV indisponível.
- Dispositivo de áudio ocupado.
- Erro de reprodução.

Nesses casos:

1. Registrar o problema no log técnico.
2. Evitar mensagens repetitivas excessivas.
3. Continuar processando os EPCs.
4. Continuar atualizando a interface.
5. Não alterar os estados dos sensores.
6. Não alterar o estado dos relés.
7. Não encerrar o aplicativo.

A notificação sonora é uma funcionalidade
auxiliar, não um pré-requisito operacional.

---

## 17. EMPACOTAMENTO WINDOWS

O sistema utiliza PyInstaller em modo:

    --onedir

O arquivo WAV deverá acompanhar
o executável Windows.

Verificar:

    tools/build_windows.py

E os recursos incluídos no pacote.

O arquivo deverá ser localizado
corretamente quando o programa for
executado a partir de:

    dist/DSV-RFID/DSV-RFID.exe

Não depender do diretório atual
de execução do Windows.

Não utilizar caminhos absolutos
da máquina de desenvolvimento.

Utilizar resolução de recursos
compatível com o pacote Python
e o PyInstaller.

Não incluir arquivos de áudio
desnecessários na distribuição.

---

## 18. GITHUB ACTIONS

Preservar o workflow Windows existente:

    .github/workflows/build-windows.yml

Garantir que:

1. O WAV esteja versionado no repositório.
2. O build inclua o arquivo.
3. A distribuição ZIP contenha o recurso.
4. O executável encontre o WAV.
5. Os testes automatizados não dependam
   de um dispositivo físico de áudio.

Atualizar a verificação de empacotamento
quando necessário.

Não alterar permissões do workflow.

Não adicionar secrets.

Não criar novas etapas de publicação
ou distribuição automática.

---

## 19. TESTES OBRIGATÓRIOS

### TESTE 1 — EPC encontrado

Simular um EPC novo com classificação OK.

Resultado:

    1 bip solicitado.

### TESTE 2 — EPC repetido

Simular cinco leituras do mesmo EPC.

Resultado:

    Apenas 1 bip.

### TESTE 3 — Múltiplas antenas

Simular o mesmo EPC identificado
pelas antenas 1 e 2.

Resultado:

    Apenas 1 bip.

### TESTE 4 — EPCs diferentes

Simular cinco EPCs novos e válidos.

Resultado:

    5 bips solicitados.

### TESTE 5 — Intervalo

Simular cinco eventos consecutivos.

Resultado:

    Intervalo mínimo de 300 ms
    entre o início dos bips.

Utilizar temporizador simulado
para evitar testes lentos ou instáveis.

### TESTE 6 — Extra box

Simular um EPC classificado Extra box.

Resultado:

    Nenhum bip.

### TESTE 7 — HTTP 404

Simular consulta sem registro.

Resultado:

    Nenhum bip.

### TESTE 8 — Erro HTTP

Simular erro de comunicação com a API.

Resultado:

    Nenhum bip.

### TESTE 9 — Filtro de EPC

Simular EPC com prefixo não autorizado.

Resultado:

    Nenhum bip.

### TESTE 10 — Som desativado

Desabilitar a notificação sonora.

Simular um EPC encontrado.

Resultado:

    Nenhum bip.

### TESTE 11 — Parada manual

Simular vários eventos pendentes
e o acionamento de Parar leitura.

Resultado:

    Eventos sonoros pendentes cancelados.

### TESTE 12 — Navegação

Simular a navegação para a página Status.

Resultado:

    A notificação sonora continua ativa.

### TESTE 13 — Falha de áudio

Simular ausência de dispositivo
ou falha de reprodução.

Resultado:

    Aplicativo continua funcionando.
    EPC continua sendo processado.
    Falha registrada no log.

### TESTE 14 — Desempenho

Simular uma sequência rápida
de múltiplos EPCs.

Confirmar:

- Sem bloqueio do inventário.
- Sem atraso artificial na API.
- Sem travamento da GUI.
- Sem duplicação de notificações.
- Sem perda de registros de negócio.

### TESTE 15 — Build Windows

Confirmar:

- WAV incluído no pacote.
- Caminho do recurso válido.
- Execução sem Python instalado.
- GitHub Actions preservado.

A reprodução audível deverá ser
homologada posteriormente em um
computador Windows com saída de áudio.

---

## 20. PRESERVAR FUNCIONALIDADES

Não modificar:

- Zebra FX9600.
- Comunicação LLRP.
- Múltiplas antenas.
- Filtro de EPC.
- Waveshare.
- Sensores DI1 e DI2.
- Relés CH1, CH2 e CH3.
- Timer de 60 segundos.
- Máquina de estados.
- Inicialização automática RF032.
- Botão Start/Stop.
- Consulta GET ao Backend.
- Registro POST de passagem.
- Classificação Extra box.
- Contadores.
- Tabela RF030.
- Layout RF031.
- Página Status.
- Ícone do executável Windows.
- Logs existentes.
- Persistência operacional.

O som deverá ser um recurso adicional
sem impacto nas regras RFID.

---

## 21. CRITÉRIOS DE ACEITE

- [ ] Bip suave implementado.
- [ ] Arquivo WAV utilizado.
- [ ] Saída de áudio do Windows utilizada.
- [ ] Um bip por EPC novo encontrado.
- [ ] Sem repetição para o mesmo EPC.
- [ ] Sem duplicação entre antenas.
- [ ] Intervalo mínimo de 300 ms.
- [ ] Reprodução não bloqueante.
- [ ] Fila de notificações implementada.
- [ ] Extra box não emite som.
- [ ] HTTP 404 não emite som.
- [ ] Erros HTTP não emitem som.
- [ ] EPCs filtrados não emitem som.
- [ ] Som pode ser desativado.
- [ ] Intervalo configurável.
- [ ] Configurações persistidas.
- [ ] Parada cancela bips pendentes.
- [ ] Funciona em qualquer página.
- [ ] Falhas de áudio não afetam o RFID.
- [ ] WAV incluído no build Windows.
- [ ] GitHub Actions preservado.
- [ ] Testes automatizados aprovados.

---

## 22. PROCEDIMENTO DO CODEX

Antes de implementar:

1. Ler AGENTS.md.
2. Verificar branch e git status.
3. Identificar o processamento de EPCs.
4. Identificar a classificação OK.
5. Identificar a deduplicação existente.
6. Identificar os serviços Qt.
7. Identificar os recursos empacotados.
8. Verificar o arquivo WAV.

Durante a implementação:

- Realizar alterações mínimas.
- Reutilizar os serviços existentes.
- Não duplicar regras de negócio.
- Não bloquear threads críticas.
- Preservar a lógica operacional.

Após implementar:

1. Executar testes unitários.
2. Executar testes de integração simulados.
3. Validar deduplicação.
4. Validar intervalo.
5. Validar parada.
6. Validar empacotamento.
7. Executar git diff.
8. Relatar possíveis regressões.

Não executar git reset --hard.
Não descartar alterações locais.
Não realizar commit automaticamente.
Não realizar push automaticamente.
Não realizar merge na main.

---

## 23. RELATÓRIO FINAL

Apresentar:

1. Branch utilizada.
2. Arquivos criados.
3. Arquivos modificados.
4. Local do arquivo WAV.
5. Serviço de áudio implementado.
6. Ponto de integração com EPC encontrado.
7. Estratégia de deduplicação.
8. Estratégia de controle do intervalo.
9. Tratamento de falhas de áudio.
10. Configurações adicionadas.
11. Integração com PyInstaller.
12. Integração com GitHub Actions.
13. Testes executados.
14. Resultados dos testes.
15. Pendências de homologação Windows.

---

## 24. RESULTADO ESPERADO

O DSV RFID System deverá reproduzir
um bip suave para cada EPC novo e
encontrado durante a sessão.

Exemplo:

    EPC 1 encontrado -> Bip
    EPC 2 encontrado -> Bip
    EPC 3 encontrado -> Bip
    EPC 1 repetido   -> Sem bip
    EPC 4 encontrado -> Bip
    EPC 5 encontrado -> Bip

Intervalo mínimo:

    300 ms

Duração do som:

    80 ms

O sistema deverá continuar funcionando
normalmente mesmo que a saída de áudio
esteja indisponível.

IMPLEMENTAR O RF033.

PRESERVAR INTEGRALMENTE O PROCESSAMENTO
RFID, A MÁQUINA DE ESTADOS E O CONTROLE
DOS EQUIPAMENTOS.