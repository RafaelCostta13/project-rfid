# RF018 — Implementação Operacional Definitiva PySide6 + QML

## 1. Contexto

O projeto RFID está migrando de Tkinter para PySide6 + QML.

A interface visual QML já foi desenvolvida e aprovada.

O Codex identificou as pendências técnicas documentadas em:

docs/adr/ADR-015-migracao-incremental-pyside6-qml.md

O relatório atual indica:

- Interface visual concluída.
- Configurações e adaptadores básicos implementados.
- 383 testes aprovados.
- Núcleo operacional ainda dependente da composição Tkinter.
- Integração real com equipamentos ainda pendente.

Este requisito autoriza a continuidade da implementação até a
conclusão funcional do RF018.

Não criar um novo protótipo.

Não redesenhar a interface aprovada.

Não criar um novo requisito funcional.

## 2. Objetivo

Tornar a interface PySide6 + QML totalmente operacional.

A nova interface deverá utilizar os serviços Python existentes
para controlar:

- Zebra FX9600.
- Waveshare Modbus RTU Relay.
- Backend RFID Rails.
- Estados operacionais.
- Configurações.
- Consulta e registro de EPCs.
- Sensores e relés.
- Ciclo automático de leitura.

A implementação deverá preservar integralmente as regras
dos requisitos anteriores.

## 3. Etapa 1 — Desacoplar a composição operacional

Esta é a primeira implementação obrigatória.

### Problema

A inicialização dos serviços operacionais está vinculada,
direta ou indiretamente, à interface Tkinter.

### Implementação

Identificar e separar:

- Inicialização dos serviços.
- Instanciação dos controllers.
- Estado da aplicação.
- Monitoramento das conexões.
- Eventos operacionais.
- Gerenciamento de sessões.
- Gerenciamento dos workers.
- Encerramento dos serviços.

Criar ou adaptar uma composição reutilizável equivalente a:

    ApplicationRuntime
        |
        +-- RFID Service
        +-- Waveshare Service
        +-- Backend Service
        +-- Status Monitor
        +-- Operational Controller
        +-- Configuration Service

A nomenclatura deverá seguir a arquitetura existente.

### Regras

1. O runtime não pode importar Tkinter.
2. O runtime não pode depender de widgets.
3. O runtime não pode iniciar uma janela.
4. O runtime não pode depender de root.after().
5. O runtime deve fornecer eventos e estados consumíveis pelo Qt.
6. O runtime deve permitir inicialização e encerramento controlados.
7. Não duplicar serviços.
8. Não alterar regras de negócio.
9. Não modificar protocolos de comunicação.

Preservar temporariamente a execução da interface antiga
durante a integração, quando tecnicamente viável.

### Testes

Criar testes demonstrando que o runtime pode:

- Ser instanciado sem Tkinter.
- Inicializar com serviços simulados.
- Publicar estados.
- Receber comandos.
- Encerrar corretamente.

Não avançar com hardware real nesta etapa.

---

## 4. Etapa 2 — Integrar indicadores reais ao Qt

Conectar os indicadores QML ao monitor existente.

Indicadores:

- RFID.
- Internet, caso existente.
- Comandos.
- Sistema.
- Base de dados.

### Fontes

RFID:
    Serviço Zebra.

Comandos:
    Serviço Waveshare.

Sistema:
    GET /api/v1/health
    Campo status.

Base de dados:
    GET /api/v1/health
    Campo database.

Internet:
    Monitor já existente.

### Arquitetura

    Status Monitor
          |
          v
    Application State
          |
          v
    Qt Bridge
          |
          v
    QML Status Indicators

Não criar um segundo monitor de conexões.

Não criar polling dentro do QML.

Não atualizar widgets diretamente de threads de comunicação.

### Testes

Simular:

- Todos conectados.
- RFID desconectado.
- Waveshare desconectada.
- Backend indisponível.
- PostgreSQL indisponível.
- Estado verificando.
- Recuperação de conexão.

Verificar que a interface representa os estados reais.

---

## 5. Etapa 3 — Integrar Backend e tabela QML

Reutilizar os serviços existentes dos requisitos:

- RF015.
- RF016.
- RF017.

Endpoints:

    GET /api/v1/health

    GET /api/v1/rfid_records/:epc

    POST /api/v1/rfid_reads

### Fluxo

    EPC recebido
        |
        v
    Validação
        |
        v
    Deduplicação
        |
        v
    GET EPC
        |
        v
    Registro encontrado
        |
        v
    POST passagem
        |
        v
    Resultado processado
        |
        v
    Qt Model
        |
        v
    Tabela QML

Preservar o contrato JSON real do Backend.

Não utilizar o contrato antigo do SharePoint.

Não consultar SQLite.

Não utilizar Power Automate.

Não duplicar GET/POST em componentes QML.

### Tabela

Preservar as colunas:

- Status.
- Cliente.
- Nota fiscal.
- Volume.
- Pedido.
- Doca.

Utilizar o modelo Qt já implementado, corrigindo-o
apenas quando necessário.

Preservar:

- Deduplicação.
- Atualização incremental.
- Contador da sessão.
- Tratamento de EPC inexistente.
- Tratamento de erros HTTP.
- Tratamento de respostas tardias.

### Regra crítica

A renderização de uma linha não pode executar POST.

O POST deve ocorrer exclusivamente no fluxo operacional.

Não repetir automaticamente POST em falhas ambíguas,
pois o Backend pode já ter registrado a passagem.

### Testes

- GET 200.
- GET 404.
- GET 500.
- Timeout.
- POST sucesso.
- POST falha.
- POST com resposta tardia.
- EPC duplicado.
- Nova sessão.
- Atualização da tabela.
- Contador correto.
- Ausência de POST duplicado.

---

## 6. Etapa 4 — Integrar Zebra FX9600

Conectar o serviço LLRP existente ao controller e à UI Bridge.

### Requisitos

- Conexão.
- Desconexão.
- Recebimento de EPCs.
- Eventos de leitura.
- Estado do reader.
- Tratamento de erros.
- Start/Stop.
- Encerramento seguro.

### Regra Start

O botão Iniciar Leitura deve habilitar o modo automático.

Não iniciar imediatamente o inventário Zebra.

O inventário deve iniciar quando o fluxo operacional
identificar a condição válida de DI1.

### Regra Stop

O botão Parar Leitura deve:

- Desabilitar o modo automático.
- Impedir novos ciclos.
- Encerrar inventário ativo.
- Cancelar o timer.
- Finalizar o ciclo com segurança.

### Threads

O callback LLRP não deve modificar QML diretamente.

Utilizar sinais e mecanismos de entrega seguros do Qt.

Não abrir conexões Zebra duplicadas.

---

## 7. Etapa 5 — Integrar Waveshare

Reutilizar o controlador Modbus existente.

Integrar:

    DI1
    DI2
    DI3
    DI4
    DI5

    CH1
    CH2
    CH3
    CH4
    CH5
    CH6
    CH7
    CH8

### Tela de diagnóstico

Implementar funcionamento real dos controles existentes.

Preservar:

- Leitura das entradas.
- Estado dos relés.
- Comandos manuais.
- Conectar/desconectar.
- Tratamento de erros.

### Regras

Não abrir a porta COM simultaneamente em dois controladores.

Não alterar endereços Modbus.

Não alterar parâmetros de comunicação.

Não alterar o comportamento validado dos relés.

Não permitir que comandos manuais da tela de diagnóstico
conflitem com o controle automático.

Não realizar comandos físicos durante testes simulados.

---

## 8. Etapa 6 — Integrar fluxo operacional completo

Preservar RF012.

### Estado pronto

    DI1 ativo
    DI2 ativo

    CH1 ON
    CH2 OFF
    CH3 OFF

    RFID aguardando

### Entrada detectada

    DI1 ativo → desativado

    Iniciar inventário RFID
    CH1 OFF
    CH2 ON
    CH3 OFF

    Iniciar timer de 60 segundos

### Processamento

    EPC
      |
      v
    GET
      |
      v
    POST
      |
      v
    Atualização Qt

### Saída detectada

    DI2 ativo → desativado

    Parar inventário
    Cancelar timer
    Finalizar ciclo
    Retornar ao estado apto, se possível

### Timeout

    60 segundos

    Parar inventário
    Finalizar ciclo
    Retornar ao estado apto, se possível

### Erros

Preservar a lógica operacional de CH3.

Preservar as condições de falha já implementadas.

Não mover a máquina de estados para QML.

Não mover o timer operacional para QML.

Não permitir que a interface execute comandos físicos
independentemente do controller.

---

## 9. Etapa 7 — Testes integrados com simuladores

Antes de qualquer teste físico, validar o fluxo completo
com serviços simulados.

Simular:

1. Inicialização.
2. Conexões OK.
3. Sistema apto.
4. DI1 interrompido.
5. Inventário iniciado.
6. EPC encontrado.
7. GET bem-sucedido.
8. POST bem-sucedido.
9. Atualização da tabela.
10. Atualização do contador.
11. DI2 interrompido.
12. Encerramento do ciclo.
13. Retorno ao estado apto.

Repetir com:

- Timeout.
- Falha Zebra.
- Falha Waveshare.
- Falha Backend.
- EPC inexistente.
- EPC duplicado.
- POST com resposta tardia.
- Encerramento durante leitura.
- Encerramento durante requisição HTTP.

Todos os testes devem utilizar mocks/fakes isolados
quando não houver autorização explícita para usar hardware.

Não considerar testes simulados como homologação física.

---

## 10. Etapa 8 — Homologação física

Após aprovação dos testes simulados, preparar
a homologação com equipamentos reais.

Equipamentos:

- Zebra FX9600.
- Waveshare Modbus RTU Relay.
- Sensores DI1/DI2.
- Relés CH1/CH2/CH3.
- Backend RFID.

Antes de executar comandos reais, verificar:

- Equipamentos disponíveis.
- Porta COM correta.
- IP do reader.
- URL do Backend.
- Ambiente de testes.
- Condições seguras de operação.

Não executar testes físicos automaticamente
sem confirmação de que o ambiente está preparado.

Produzir checklist de homologação.

Se o Codex não tiver acesso aos equipamentos,
registrar a etapa como pendente.

Não declarar homologação física concluída.

---

## 11. Etapa 9 — Substituição definitiva do Tkinter

Somente após os testes integrados e homologação necessária:

- Definir Qt como interface oficial.
- Atualizar o entrypoint.
- Remover imports Tkinter obsoletos.
- Remover widgets antigos.
- Remover dependências gráficas não utilizadas.
- Remover caminhos de execução legados.
- Preservar serviços operacionais reutilizados.

Não remover arquivos que ainda contenham regras
de negócio necessárias.

Manter a possibilidade de recuperar a versão anterior
através do Git.

---

## 12. Etapa 10 — Empacotamento Windows

Preparar a aplicação para distribuição Windows.

Verificar:

- Dependências PySide6.
- Plugins Qt.
- Arquivos QML.
- Assets.
- Logotipo DSV.
- Configurações.
- Bibliotecas LLRP.
- Bibliotecas Modbus.
- Cliente HTTP.

Não utilizar WSL.

Não depender de caminhos absolutos.

Testar execução fora do ambiente de desenvolvimento.

---

## 13. Estratégia de execução

Executar todas as etapas autorizadas de forma sequencial.

Para cada etapa:

1. Analisar os arquivos envolvidos.
2. Implementar a alteração mínima necessária.
3. Executar testes relacionados.
4. Executar regressão apropriada.
5. Revisar o diff.
6. Corrigir falhas.
7. Registrar o resultado.
8. Avançar para a próxima etapa.

Não interromper para solicitar nova aprovação visual.

Não redesenhar a interface.

Não recriar componentes aprovados.

Não alterar regras de negócio sem autorização.

Não realizar operações físicas sem condições de teste seguras.

Não remover a interface antiga antes da conclusão
das validações necessárias.

---

## 14. Critérios de aceite

- [ ] Runtime independente do Tkinter.
- [ ] Interface Qt utiliza serviços reais.
- [ ] Indicadores reais integrados.
- [ ] Backend Health integrado.
- [ ] GET EPC integrado.
- [ ] POST passagem integrado.
- [ ] Tabela utiliza registros reais.
- [ ] Contador utiliza dados reais.
- [ ] Zebra integrado.
- [ ] Waveshare integrada.
- [ ] Tela de diagnóstico funcional.
- [ ] Start/Stop funcional.
- [ ] Fluxo DI1/DI2 funcional.
- [ ] Timer 60 segundos preservado.
- [ ] CH1/CH2/CH3 preservados.
- [ ] Sem operações bloqueantes na UI.
- [ ] Sem conexões duplicadas.
- [ ] Sem POST duplicado por atualização visual.
- [ ] Encerramento seguro.
- [ ] Testes simulados aprovados.
- [ ] Homologação física realizada ou pendência explicitada.
- [ ] Empacotamento Windows validado.
- [ ] Tkinter removido após homologação.
- [ ] Interface QML aprovada preservada.

---

## 15. Relatório final obrigatório

Apresentar:

1. Etapas implementadas.
2. Arquivos modificados.
3. Arquivos criados.
4. Arquivos removidos.
5. Arquitetura final.
6. Serviços reutilizados.
7. Quantidade de testes executados.
8. Testes aprovados.
9. Testes reprovados.
10. Cobertura dos fluxos operacionais.
11. Pendências de hardware.
12. Status do empacotamento Windows.
13. Status da remoção do Tkinter.
14. Limitações restantes.

Atualizar o ADR-015 para refletir o estado real da migração.

Não declarar RF018 concluído se existirem pendências
operacionais críticas.

---

## 16. Instrução final

O protótipo visual já foi aprovado.

A tarefa agora é IMPLEMENTAR a integração operacional real
da interface PySide6 + QML.

Começar imediatamente pela separação da composição operacional
atualmente vinculada ao Tkinter.

Em seguida, integrar os indicadores utilizando fakes.

Após os testes, avançar sequencialmente pelas demais etapas.

O resultado esperado é o software RFID funcionando
integralmente através da interface Qt, preservando
todos os serviços e regras operacionais existentes.