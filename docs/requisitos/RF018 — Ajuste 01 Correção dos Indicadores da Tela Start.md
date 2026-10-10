# RF018 — Ajuste 01: Correção dos Indicadores da Tela Start

**Categoria:** Correção de interface (UX/UI)
**Prioridade:** Média
**Ambiente:** Windows
**Tecnologia:** PySide6 + Qt Quick/QML
**Requisito relacionado:** RF015 e RF018
**Tipo:** Correção pontual — sem alteração de regras operacionais

---

## 1. Objetivo

Corrigir a interface PySide6 + QML do software RFID, removendo o indicador visual "Base de dados" da tela Start.

Após a correção, a tela Start deverá apresentar exclusivamente os seguintes indicadores, nesta ordem:

1. RFID
2. Internet
3. Comandos
4. Sistema

O indicador "Base de dados" não deverá aparecer na tela Start.

IMPORTANTE:

A remoção é exclusivamente visual.

Não remover o monitoramento do PostgreSQL, não modificar o endpoint de health e não alterar as condições que determinam se o sistema está apto para operar.

---

## 2. Contexto

Durante a migração da interface Tkinter para PySide6 + QML, realizada no RF018, o indicador "Base de dados" voltou a aparecer na tela Start.

O RF015 estabeleceu a utilização do endpoint:

    GET /api/v1/health

Esse endpoint verifica:

- Disponibilidade do servidor Rails.
- Disponibilidade da conexão PostgreSQL.

A interface deverá continuar utilizando as informações desse endpoint, mas apresentando somente o indicador consolidado "Sistema".

Essa alteração não modifica o contrato da API.

---

## 3. Layout esperado

A área de indicadores da tela Start deverá apresentar:

    ┌─────────────────────────────────────────────────────┐
    │                                                     │
    │   RFID       Internet      Comandos       Sistema   │
    │                                                     │
    │   ● OK       ● OK          ● OK           ● OK      │
    │                                                     │
    └─────────────────────────────────────────────────────┘

O desenho acima é apenas uma representação conceitual.

Preservar o design QML já aprovado.

Não modificar:

- Header.
- Sidebar.
- Paleta de cores.
- Tipografia.
- Estilo dos cards.
- Botões.
- Tabela RFID.
- Organização geral da tela.

Apenas remover o indicador excedente e ajustar o alinhamento dos quatro indicadores restantes.

---

## 4. Requisitos funcionais

### RF018-AJ01.01 — Remover indicador Base de dados

Remover da tela Start:

    Base de dados

A remoção deverá incluir exclusivamente os elementos visuais e bindings que existam apenas para renderizar esse indicador.

Não remover os estados internos associados ao banco de dados.

Não remover propriedades utilizadas por outros componentes ou pela lógica operacional.

### RF018-AJ01.02 — Preservar RFID

O indicador RFID deverá continuar representando o estado real da comunicação com o Zebra FX9600.

Preservar:

- Fonte de dados.
- Atualização automática.
- Tratamento de desconexão.
- Tratamento de reconexão.
- Estados visuais.

### RF018-AJ01.03 — Preservar Internet

O indicador Internet deverá continuar utilizando o mecanismo de monitoramento existente.

Não criar uma nova verificação de conectividade.

Não alterar a frequência de monitoramento.

Não alterar os critérios atuais para determinar a disponibilidade da Internet.

### RF018-AJ01.04 — Preservar Comandos

O indicador Comandos deverá continuar representando o estado real da comunicação com a Waveshare.

Não alterar:

- Porta COM.
- Configurações Modbus.
- Polling.
- Comunicação serial.
- Controle de relés.
- Leitura de entradas digitais.

### RF018-AJ01.05 — Preservar Sistema

O indicador Sistema deverá continuar utilizando o estado operacional existente, associado à comunicação com o Backend RFID.

O endpoint permanece:

    GET /api/v1/health

Contrato esperado:

    {
      "status": "ok",
      "database": "ok"
    }

A avaliação interna de saúde do PostgreSQL deverá permanecer ativa.

Não considerar o sistema operacionalmente apto apenas porque o servidor Rails está respondendo, caso as regras atuais também exijam PostgreSQL disponível.

Preservar integralmente o cálculo de prontidão já implementado.

Não criar uma segunda implementação desse cálculo na interface QML.

---

## 5. Regras visuais

Os quatro indicadores deverão utilizar os componentes QML existentes.

Estados visuais:

| Estado | Cor |
|---|---|
| OK / Conectado | Verde |
| NOK / Desconectado | Vermelho |
| Verificando | Amarelo |
| Desconhecido | Cinza |

Não alterar a paleta visual aprovada.

Não criar novos componentes se os existentes puderem ser reutilizados.

Não deixar espaço vazio correspondente ao indicador removido.

Distribuir os quatro indicadores de maneira equilibrada dentro do container atual.

---

## 6. Preservação dos serviços

Esta correção NÃO autoriza alterações nos seguintes componentes:

- Zebra RFID Service.
- Waveshare Service.
- Backend Client.
- Status Monitor.
- Application Controller.
- Máquina de estados operacional.
- Controle de sessões.
- Timer de 60 segundos.
- Gerenciamento de workers.
- Regras de deduplicação.
- Consulta GET de EPC.
- Registro POST de passagem.

A alteração deve ficar restrita à camada de apresentação e aos testes visuais correspondentes.

Se for identificada necessidade de modificar qualquer serviço operacional, interromper essa alteração e apresentar justificativa técnica.

---

## 7. Verificação da branch

Antes de modificar o código, executar:

    git branch --show-current
    git status -sb
    git log --oneline --decorate -10

Identificar a branch atual e confirmar que ela contém a implementação PySide6 + QML aprovada.

Verificar também:

- Se a interface QML atual é a implementação oficial.
- Se existem alterações não commitadas.
- Se existem conflitos de merge.
- Se o componente visual foi criado a partir de uma versão anterior do RF018.

Não trocar de branch automaticamente.

Não realizar merge.

Não descartar alterações locais.

Não criar commits automaticamente, salvo se houver instrução específica do fluxo de trabalho do projeto.

Caso seja identificada uma inconsistência relevante de branch ou merge, apresentar o diagnóstico antes de modificar arquivos.

---

## 8. Análise obrigatória

Localizar o componente QML responsável pela apresentação dos indicadores da tela Start.

Identificar:

1. Arquivo QML da tela Start.
2. Componente de status reutilizável.
3. Lista ou modelo que define os indicadores.
4. Binding do indicador Base de dados.
5. Fonte do estado Sistema.
6. Testes relacionados à renderização dos indicadores.

Verificar se a lista é construída:

- Diretamente no QML.
- Por um modelo Python.
- Por propriedades da UI Bridge.
- Por uma configuração centralizada.

Realizar a menor alteração possível.

Não alterar o modelo operacional apenas para esconder um indicador.

---

## 9. Testes obrigatórios

### Teste 1 — Quantidade de indicadores

Abrir a tela Start.

Resultado esperado:

    Total de indicadores visíveis = 4

### Teste 2 — Nomes

Verificar a presença de:

    RFID
    Internet
    Comandos
    Sistema

Verificar ausência de:

    Base de dados
    Sincronização

### Teste 3 — Estados reais

Simular ou reproduzir alterações nos estados existentes.

Confirmar que os quatro indicadores continuam atualizando normalmente.

### Teste 4 — Falha do PostgreSQL

Simular uma resposta de health indicando:

    {
      "status": "error",
      "database": "unavailable"
    }

Confirmar que:

- O monitoramento interno continua identificando a falha.
- A prontidão operacional permanece obedecendo às regras atuais.
- O indicador Sistema apresenta o estado correspondente à avaliação operacional existente.
- Nenhum indicador adicional Base de dados é exibido.

Não modificar a semântica dos estados internos para satisfazer o teste visual.

### Teste 5 — Layout

Verificar que:

- Os quatro indicadores estão alinhados.
- Não existe espaço vazio do indicador removido.
- Não existem sobreposições.
- O design aprovado foi preservado.

### Teste 6 — Regressão

Executar os testes existentes relacionados a:

- Interface QML.
- UI Bridge.
- Status Monitor.
- Backend Health.
- Prontidão operacional.

Confirmar que nenhum comportamento operacional foi alterado.

---

## 10. Critérios de aceite

- [ ] A branch foi verificada.
- [ ] A tela Start apresenta exatamente quatro indicadores.
- [ ] RFID está presente.
- [ ] Internet está presente.
- [ ] Comandos está presente.
- [ ] Sistema está presente.
- [ ] Base de dados não aparece.
- [ ] Sincronização não aparece.
- [ ] Layout QML aprovado foi preservado.
- [ ] Os indicadores continuam recebendo estados reais.
- [ ] O monitoramento PostgreSQL continua funcionando.
- [ ] O Backend Health não foi alterado.
- [ ] A prontidão operacional não foi alterada.
- [ ] Os serviços RFID e Waveshare não foram alterados.
- [ ] Os testes relacionados passaram.

---

## 11. Fora do escopo

Não implementar:

- Nova interface.
- Novos indicadores.
- Novos endpoints.
- Alterações no PostgreSQL.
- Alterações no Rails.
- Alterações na lógica dos sensores.
- Alterações nos relés.
- Alterações no timer.
- Alterações no fluxo Start/Stop.
- Alterações na consulta de EPC.
- Alterações no registro de passagem.
- Refatoração ampla da UI Bridge.
- Alteração de biblioteca gráfica.
- Reorganização do layout.

---

## 12. Relatório final

Ao concluir, apresentar:

1. Branch utilizada.
2. Arquivos modificados.
3. Local onde o indicador Base de dados estava sendo criado.
4. Motivo de seu reaparecimento, se identificado.
5. Alteração aplicada.
6. Confirmação de preservação dos serviços operacionais.
7. Testes executados.
8. Resultados dos testes.
9. Diff resumido.

---

## 13. Definição de pronto

O ajuste estará concluído quando a tela Start apresentar exclusivamente:

    RFID | Internet | Comandos | Sistema

O monitoramento de PostgreSQL deverá permanecer ativo internamente.

Nenhuma regra operacional deverá ser modificada.

A alteração deverá ser pequena, localizada e compatível com a arquitetura PySide6 + QML existente.

**Executar somente esta correção visual, preservando integralmente a implementação operacional do RF018.**