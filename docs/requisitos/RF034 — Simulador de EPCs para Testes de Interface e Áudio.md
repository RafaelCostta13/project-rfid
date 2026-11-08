# RF034 — Simulador de EPCs para Testes de Interface e Áudio

Projeto: DSV RFID System
Requisito: RF034
Categoria: Testes / Frontend / Simulação RFID
Tecnologia: Python + PySide6/QML
Branch atual: feature/efeito-sonoro
Prioridade: Média

---

## 1. OBJETIVO

Criar uma ferramenta de simulação de leitura
de etiquetas RFID dentro do aplicativo.

A ferramenta deverá permitir testar:

- Contador de EPCs encontrados.
- Contador de Extra box.
- Tabela de registros RFID.
- Classificação visual dos registros.
- Notificação sonora implementada no RF033.
- Comportamento visual durante uma sessão.

O simulador não deverá depender de:

- Leitor Zebra FX9600.
- Antenas RFID.
- Placa Waveshare.
- Sensores DI1 e DI2.
- Conexão com o backend Rails.
- Conexão com a internet.

O objetivo é testar exclusivamente
o frontend e o serviço de áudio.

Não modificar a lógica operacional real.

---

## 2. LOCALIZAÇÃO DO SIMULADOR

Adicionar na página:

    Configurações

Um novo botão:

    Simulador RFID

Ícone sugerido:

    flask-conical

Ao clicar no botão, abrir uma pequena
janela de simulação.

A janela deverá seguir o tema visual
Corporate Dark utilizado pelo sistema.

Não criar uma nova página na sidebar.

Não modificar a organização das páginas:

- Start.
- Status.
- Configurações.

---

## 3. JANELA DE SIMULAÇÃO

Criar uma janela modal compacta.

Título:

    Simulador RFID

Dimensão sugerida:

    360 x 300 px

Ajustar conforme necessário.

A janela deverá apresentar:

1. Botão Iniciar sessão.
2. Botão EPC encontrado.
3. Botão Extra box.
4. Botão Finalizar sessão.
5. Indicação do estado da simulação.

Opcionalmente, mostrar os contadores
da sessão dentro da própria janela.

A interface deverá ser simples.

Não adicionar campos desnecessários.

A janela deverá permanecer visível
enquanto o operador executa os testes.

---

## 4. ESTADO INICIAL

Ao abrir a janela:

    Sessão: Inativa

Botões:

    Iniciar sessão: Habilitado
    EPC encontrado: Desabilitado
    Extra box: Desabilitado
    Finalizar sessão: Desabilitado

Nenhum EPC deverá ser gerado
automaticamente ao abrir a janela.

Nenhum som deverá ser reproduzido.

---

## 5. BOTÃO INICIAR SESSÃO

Ao clicar em:

    Iniciar sessão

O sistema deverá:

1. Criar uma sessão de simulação.
2. Inicializar os contadores simulados.
3. Inicializar uma lista vazia de EPCs.
4. Habilitar os botões de simulação.
5. Habilitar Finalizar sessão.
6. Desabilitar Iniciar sessão.
7. Apresentar o estado:

    Simulação ativa

8. Exibir a página Start, mantendo
   a janela de simulação disponível.

IMPORTANTE:

Não executar o método real de início
de inventário RFID.

Não iniciar comunicação LLRP.

Não acionar os relés da Waveshare.

Não modificar os indicadores reais
de conectividade.

Não realizar chamadas HTTP.

A sessão simulada deverá funcionar
independentemente dos quatro indicadores.

---

## 6. BOTÃO EPC ENCONTRADO

Ao clicar em:

    EPC encontrado

Gerar um registro RFID fictício
classificado como encontrado.

O sistema deverá:

1. Gerar um EPC único.
2. Criar os dados fictícios do registro.
3. Adicionar o registro à tabela Start.
4. Incrementar o contador:

    EPCs encontrados +1

5. Reproduzir o bip suave do RF033.
6. Atualizar a interface imediatamente.

Exemplo:

    Antes:

    EPCs encontrados: 0
    Extra box: 0

    Após um clique:

    EPCs encontrados: 1
    Extra box: 0

    Após cinco cliques:

    EPCs encontrados: 5
    Extra box: 0

Cada clique deverá representar
um EPC diferente.

---

## 7. BOTÃO EXTRA BOX

Ao clicar em:

    Extra box

Gerar um registro RFID fictício
classificado como Extra box.

O sistema deverá:

1. Gerar um EPC único.
2. Criar os dados fictícios.
3. Adicionar o registro à tabela Start.
4. Incrementar o contador:

    Extra box +1

5. Aplicar a apresentação visual
   existente para registros Extra box.

Não reproduzir bip.

Preservar a regra do RF033:

    EPC encontrado -> Bip suave

    Extra box -> Sem bip

Não realizar consulta real à API
para simular HTTP 404 ou status lido.

A classificação deverá ser simulada
internamente, sem requisições HTTP.

---

## 8. GERAÇÃO DOS EPCs

Os EPCs gerados deverão ser diferentes
dentro da mesma sessão.

Utilizar EPCs hexadecimais válidos
para a representação utilizada
pelo sistema.

Exemplo de prefixo autorizado:

    424D57

Esse prefixo corresponde a BMW.

Exemplos fictícios:

    424D57000000000000000001
    424D57000000000000000002
    424D57000000000000000003

O gerador poderá utilizar valores
aleatórios ou um contador incremental.

Requisitos:

- EPC em letras maiúsculas.
- Somente caracteres hexadecimais.
- Não repetir EPC na mesma sessão.
- Preservar comprimento compatível
  com o modelo utilizado pelo sistema.

Não utilizar EPCs reais conhecidos.

Não persistir os EPCs simulados
no backend ou no banco operacional.

---

## 9. DADOS FICTÍCIOS

Os demais campos poderão ser fixos.

Exemplo:

    status: pendente
    fornecedor: BMW do Brasil Ltda
    notafiscal: 1198497
    volume: 1/1
    pedido: 0007818432
    doca: DOCA 42
    destinatario: DEALER TESTE
    epc: GERADO_AUTOMATICAMENTE

Para cada clique, gerar um novo EPC.

Os demais campos podem permanecer iguais.

Os registros deverão ser claramente
identificáveis internamente como simulados.

Não misturar registros fictícios
com registros reais da operação.

---

## 10. TABELA DA TELA START

O RF030 definiu a seguinte ordem
de colunas:

1. Status
2. Cliente
3. Nota Fiscal
4. Volume
5. Pedido
6. Doca
7. Dealer

Preservar exatamente essa estrutura.

Mapeamento:

    Status      -> status visual
    Cliente     -> fornecedor
    Nota Fiscal -> notafiscal
    Volume      -> volume
    Pedido      -> pedido
    Doca        -> doca
    Dealer      -> destinatario

O EPC deverá continuar disponível
no modelo interno da linha.

Não adicionar uma coluna EPC.

Não modificar os cabeçalhos existentes.

Registros encontrados deverão seguir
a apresentação visual normal.

Registros Extra box deverão seguir
a apresentação visual existente.

Preservar:

    Fundo Extra box: #3A372C
    Hover Extra box: #454031
    Destaque: #D9B86C

---

## 11. INTEGRAÇÃO COM O RF033

O RF033 implementou o serviço
de notificação sonora.

O simulador deverá reutilizar
esse serviço.

Não implementar um segundo
mecanismo de reprodução de áudio.

Não criar outro arquivo WAV.

Utilizar:

    bip_01_suave.wav

Características:

    Frequência: 880 Hz
    Duração: 80 ms
    Intervalo mínimo: 300 ms

Cada clique em EPC encontrado
deverá solicitar um bip.

Se o operador clicar rapidamente
várias vezes:

    EPC 1 -> Bip
    EPC 2 -> Bip
    EPC 3 -> Bip
    EPC 4 -> Bip

A fila de áudio deverá respeitar
o intervalo configurado no RF033.

Não bloquear a interface.

Não utilizar time.sleep()
na thread principal.

O botão Extra box não deverá
solicitar notificação sonora.

Respeitar a configuração existente
de som ativado ou desativado.

---

## 12. ISOLAMENTO DA SIMULAÇÃO

A implementação deverá manter
separação clara entre:

    Operação RFID real

e

    Simulação de interface

Não reutilizar o processamento real
de EPCs se isso provocar:

- Consulta GET ao backend.
- Registro POST de passagem.
- Inventário LLRP.
- Comandos Modbus.
- Acionamento de relés.
- Alteração de sensores.
- Alteração do estado real do leitor.

É permitido reutilizar:

- Modelos de apresentação.
- Componentes QML.
- Atualização de contadores.
- Formatação de registros.
- Classificação visual.
- Serviço de áudio.
- Fila de notificações.

Criar um serviço de simulação
pequeno e independente, utilizando
os contratos existentes de apresentação.

Não duplicar desnecessariamente
os componentes visuais.

---

## 13. SEGURANÇA OPERACIONAL

A simulação não deverá ocorrer
simultaneamente com um inventário real.

Antes de iniciar a sessão simulada:

1. Verificar se existe inventário real ativo.
2. Se houver, impedir a simulação.
3. Exibir uma mensagem orientando
   a finalizar a leitura real.

Se o modo automático real estiver
habilitado, exigir sua parada manual
antes de iniciar a simulação.

Não desligar relés automaticamente
apenas para abrir o simulador.

Não modificar o estado físico
dos equipamentos.

Durante a simulação, impedir que
uma leitura real seja iniciada
simultaneamente.

O simulador deve funcionar mesmo
quando os serviços reais estiverem
desconectados.

Não exigir que os indicadores
RFID, Internet, Comandos e Sistema
estejam OK.

Preservar o RF032.

---

## 14. VISUALIZAÇÃO DA SIMULAÇÃO

Ao iniciar a sessão simulada,
a tela Start deverá apresentar
os dados fictícios.

Os contadores deverão mostrar
somente os dados da simulação ativa.

Exemplo:

    EPCs encontrados: 8

    Extra box: 3

A tabela deverá apresentar
os 11 registros simulados.

A interface deverá continuar
utilizando os componentes existentes.

Não criar uma segunda tabela
para apresentar a simulação.

Utilizar um modelo de dados isolado
ou um mecanismo de apresentação
que permita alternar entre dados
reais e simulados com segurança.

Preservar os dados reais
que estavam sendo apresentados
antes da simulação.

---

## 15. BOTÃO FINALIZAR SESSÃO

Ao clicar em:

    Finalizar sessão

O sistema deverá:

1. Encerrar a sessão simulada.
2. Desabilitar EPC encontrado.
3. Desabilitar Extra box.
4. Cancelar bips simulados pendentes.
5. Habilitar Iniciar sessão.
6. Atualizar o estado:

    Simulação finalizada

Não realizar POST de encerramento.

Não registrar passagem real.

Não modificar os equipamentos.

Permitir visualizar o resultado
da sessão até que a janela seja
fechada ou uma nova sessão iniciada.

Ao iniciar uma nova sessão,
reiniciar os contadores simulados.

---

## 16. FECHAMENTO DA JANELA

Quando a janela for fechada:

Se existir uma sessão simulada ativa:

    Finalizar a simulação internamente.

Cancelar eventos sonoros pendentes
originados pela simulação.

Restaurar a apresentação normal
da tela Start.

Não deixar contadores fictícios
misturados aos dados reais.

Não alterar o estado operacional
real do sistema.

Não persistir dados simulados
para a próxima execução.

---

## 17. ARQUITETURA PYTHON / QML

Implementar preferencialmente:

    Serviço de simulação Python
            |
            v
       Qt Bridge
            |
            v
       Modelo QML
            |
            v
       Tela Start

Para EPC encontrado:

    Clique
      |
      v
    Gerar EPC fictício
      |
      v
    Criar registro encontrado
      |
      +--> Atualizar tabela
      |
      +--> Incrementar contador
      |
      +--> Serviço de áudio RF033

Para Extra box:

    Clique
      |
      v
    Gerar EPC fictício
      |
      v
    Criar registro Extra box
      |
      +--> Atualizar tabela
      |
      +--> Incrementar contador

Não passar os registros simulados
pela comunicação LLRP ou pela API.

O modal deverá ser controlado
pela camada QML existente.

Evitar criar uma nova janela
independente do aplicativo.

Garantir que a janela permaneça
funcional após navegar para Start.

---

## 18. TESTES OBRIGATÓRIOS

TESTE 1 — Abrir simulador

Resultado:

    Janela abre.
    Sessão inativa.
    Botões de EPC desabilitados.

TESTE 2 — Iniciar sessão

Resultado:

    Sessão ativa.
    Botões habilitados.
    Contadores iniciados em zero.

TESTE 3 — EPC encontrado

Clicar uma vez.

Resultado:

    EPCs encontrados = 1
    Extra box = 0
    Uma notificação sonora solicitada.

TESTE 4 — Múltiplos EPCs

Clicar dez vezes em EPC encontrado.

Resultado:

    EPCs encontrados = 10

    Dez EPCs únicos na tabela.

    Dez notificações solicitadas.

TESTE 5 — Extra box

Clicar cinco vezes em Extra box.

Resultado:

    Extra box = 5

    Cinco registros Extra box.

    Nenhuma notificação sonora adicional.

TESTE 6 — Sessão mista

Simular:

    7 EPCs encontrados
    3 Extra box

Resultado:

    EPCs encontrados = 7
    Extra box = 3

    Total de linhas = 10

    Total de bips solicitados = 7

TESTE 7 — Intervalo de áudio

Gerar múltiplos EPCs rapidamente.

Confirmar:

    Intervalo mínimo configurado.
    Sem travamento da interface.
    Sem reprodução sobreposta.

TESTE 8 — Finalizar sessão

Resultado:

    Botões de EPC desabilitados.
    Bips pendentes cancelados.
    Dados preservados para inspeção.

TESTE 9 — Nova sessão

Iniciar novamente.

Resultado:

    Contadores zerados.
    Nova lista de registros.
    Sem resíduos da sessão anterior.

TESTE 10 — Serviços desconectados

Simular:

    RFID = Desconectado
    Internet = Desconectado
    Comandos = Desconectado
    Sistema = Indisponível

Resultado:

    Simulador funciona normalmente.

TESTE 11 — Sem backend

Executar simulação sem API Rails.

Resultado:

    Nenhuma requisição HTTP.
    Interface atualizada.
    Bip funcionando.

TESTE 12 — Sem hardware

Executar sem Zebra e Waveshare.

Resultado:

    Simulador funciona normalmente.

TESTE 13 — Isolamento

Confirmar:

    Nenhum GET real.
    Nenhum POST real.
    Nenhum comando LLRP.
    Nenhum comando Modbus.
    Nenhum acionamento de relé.

TESTE 14 — Proteção contra operação simultânea

Tentar iniciar simulação
com inventário real ativo.

Resultado:

    Simulação bloqueada.

TESTE 15 — Fechamento

Fechar a janela durante a simulação.

Resultado:

    Sessão encerrada.
    Áudio pendente cancelado.
    Dados reais preservados.
    Apresentação normal restaurada.

---

## 19. PRESERVAR FUNCIONALIDADES

Não modificar:

- Zebra FX9600.
- Comunicação LLRP.
- Configuração das antenas.
- Filtro de EPC RF023.
- Waveshare Modbus.
- Sensores DI1 e DI2.
- Relés CH1, CH2 e CH3.
- Timer de 60 segundos.
- Máquina de estados.
- Backend Rails.
- Requisições GET e POST.
- Classificação real Extra box.
- Deduplicação real.
- Botão Iniciar/Parar leitura.
- Inicialização automática RF032.
- Notificação sonora RF033.
- Tabela RF030.
- Layout RF031.
- Página Status.
- Build Windows.
- GitHub Actions.

O RF034 deverá ser uma ferramenta
auxiliar de testes.

---

## 20. CRITÉRIOS DE ACEITE

- [ ] Botão Simulador RFID em Configurações.
- [ ] Modal pequeno e simples.
- [ ] Botão Iniciar sessão.
- [ ] Botão EPC encontrado.
- [ ] Botão Extra box.
- [ ] Botão Finalizar sessão.
- [ ] Botões habilitados conforme a sessão.
- [ ] EPCs fictícios únicos.
- [ ] Dados fictícios válidos.
- [ ] Contador de encontrados atualizado.
- [ ] Contador Extra box atualizado.
- [ ] Tabela Start atualizada.
- [ ] Bip suave para EPC encontrado.
- [ ] Sem bip para Extra box.
- [ ] Intervalo RF033 respeitado.
- [ ] Funciona sem leitor RFID.
- [ ] Funciona sem Waveshare.
- [ ] Funciona sem backend.
- [ ] Nenhum GET ou POST real.
- [ ] Nenhum comando de hardware.
- [ ] Dados simulados isolados.
- [ ] Operação real preservada.
- [ ] Sessão pode ser reiniciada.
- [ ] Fechamento restaura a tela normal.
- [ ] Testes automatizados aprovados.

---

## 21. PROCEDIMENTO DO CODEX

Antes de implementar:

1. Ler AGENTS.md.
2. Confirmar a branch atual.
3. Executar git status.
4. Identificar o serviço de áudio RF033.
5. Identificar o modelo de registros.
6. Identificar os contadores.
7. Identificar a tabela Start.
8. Identificar a página Configurações.
9. Identificar o Qt Bridge.
10. Preservar alterações locais.

Durante a implementação:

- Criar a menor solução funcional.
- Reutilizar os componentes existentes.
- Manter simulação isolada.
- Não adicionar dependências desnecessárias.
- Não modificar regras de negócio reais.

Após implementar:

1. Executar testes.
2. Validar interface.
3. Validar som.
4. Validar contadores.
5. Validar tabela.
6. Validar ausência de chamadas reais.
7. Validar fechamento da sessão.
8. Executar git diff.
9. Apresentar relatório.

Não executar git reset --hard.
Não descartar alterações locais.

Não realizar commit automaticamente.
Não realizar push automaticamente.
Não realizar merge na main.

---

## 22. RESULTADO ESPERADO

O operador deverá acessar:

    Configurações
        |
        v
    Simulador RFID
        |
        v
    Iniciar sessão

Em seguida, poderá clicar:

    EPC encontrado

ou:

    Extra box

Cada clique deverá gerar um novo
registro fictício na tela Start.

EPC encontrado:

    Atualiza contador.
    Adiciona registro.
    Reproduz bip suave.

Extra box:

    Atualiza contador.
    Adiciona registro Extra box.
    Não reproduz som.

Ao finalizar:

    Finalizar sessão

A simulação deverá encerrar
sem modificar o funcionamento real.

IMPLEMENTAR O RF034.

OBJETIVO PRINCIPAL:

PERMITIR TESTAR OS CONTADORES,
A TABELA RFID E O BIP SUAVE
SEM PRECISAR DOS EQUIPAMENTOS
OU DO BACKEND RAILS.
