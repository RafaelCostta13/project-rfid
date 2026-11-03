# RF028 — Empacotamento e Distribuição Windows

Projeto: RFID System
Requisito: RF028
Categoria: Distribuição / Build / Logging
Prioridade: Alta
Sistema operacional: Windows
Tecnologia: Python 3.12 + PySide6/QML
Empacotamento: PyInstaller --onedir

---

## 1. OBJETIVO

Preparar o RFID System para distribuição
como executável Windows.

O projeto já possui uma estrutura de
empacotamento funcional.

Não criar uma nova implementação de build.

Reutilizar os componentes existentes:

- packaging/windows_entry.py
- tools/build_windows.py
- tools/verify_windows.py

O objetivo é:

1. Implementar logs persistentes.
2. Preservar configurações externas.
3. Validar dependências e recursos.
4. Executar testes automatizados.
5. Gerar um bundle Windows atualizado.
6. Validar o executável gerado.
7. Preparar o pacote para homologação.

---

## 2. CONTEXTO TÉCNICO

O projeto utiliza:

- Python 3.12.
- PySide6 6.10.3.
- QML.
- sllurp.
- pymodbus[serial].
- python-dotenv.
- Zebra FX9600.
- Waveshare Modbus RTU Relay.
- Backend Rails API.

Entrada Windows:

    packaging/windows_entry.py

Entrada Qt:

    src/rfid_reader/ui/qt/application.py

Scripts existentes:

    tools/build_windows.py

    tools/verify_windows.py

O projeto já possui um bundle anterior em:

    dist/DSV-RFID

Esse bundle está desatualizado.

Não reutilizar arquivos antigos
como resultado de uma nova compilação.

---

## 3. RF028.01 — LOGS PERSISTENTES

Atualmente, o software utiliza logging.basicConfig
com saída para o fluxo padrão.

Implementar gravação persistente de logs.

Diretório recomendado:

    %LOCALAPPDATA%\DSV-RFID\logs\

O diretório deverá ser criado automaticamente
quando necessário.

Utilizar preferencialmente:

    logging.handlers.RotatingFileHandler

Configuração inicial sugerida:

    Tamanho máximo: 5 MB

    Backups: 5

    Encoding: UTF-8

Exemplo:

    rfid-system.log
    rfid-system.log.1
    rfid-system.log.2

Preservar o sistema de logging existente.

Evitar duplicação de mensagens.

Não registrar:

- Senhas.
- Tokens.
- Credenciais.
- Segredos de configuração.

O logging deverá funcionar mesmo quando
o executável for iniciado sem console.

Se o diretório de logs não estiver disponível,
tratar a falha sem provocar encerramento
desnecessário da aplicação.

---

## 4. RF028.02 — CONFIGURAÇÕES EXTERNAS

Preservar o suporte ao argumento:

    --env-file

Estrutura recomendada:

    C:\DSV-RFID\
        DSV-RFID.exe
        _internal\
        .env.example

    C:\ProgramData\DSV-RFID\
        station.env

Exemplo de execução:

    C:\DSV-RFID\DSV-RFID.exe --env-file C:\ProgramData\DSV-RFID\station.env

IMPORTANTE:

Não incluir o arquivo .env real
no executável.

Não incorporar credenciais ao bundle.

Preservar as configurações de:

- IP do Zebra FX9600.
- Porta LLRP.
- Antenas RFID.
- Porta COM Waveshare.
- Parâmetros de comunicação.
- Backend Rails.
- Filtro de prefixos EPC.
- Logging.

Verificar se a tela de configurações
continua salvando corretamente os dados
quando o executável utiliza --env-file.

Não alterar os valores de configuração
existentes sem necessidade.

---

## 5. RF028.03 — RECURSOS QML

Verificar se o bundle inclui:

- Main.qml.
- StartPage.
- SettingsPage.
- DiagnosticPage.
- Componentes QML.
- Tema.
- qmldir.
- dsv_logo.svg.

Preservar a estratégia existente:

    --collect-data rfid_reader

Não modificar o design da aplicação.

Não modificar a estrutura da interface.

Não substituir recursos existentes.

---

## 6. RF028.04 — DEPENDÊNCIAS

Validar o empacotamento das bibliotecas:

- PySide6.
- sllurp.
- pymodbus.
- pyserial.
- python-dotenv.

Preservar os imports ocultos existentes:

    sllurp.llrp

    serial.serialwin32

    pymodbus.client

Verificar se existem novas dependências
necessárias devido às alterações recentes.

Não adicionar bibliotecas desnecessárias.

---

## 7. RF028.05 — BUILD WINDOWS

Reutilizar:

    tools/build_windows.py

Executar o build em Windows x64.

Utilizar Python 3.12.

Comandos:

    .\.venv\Scripts\python.exe -m pip install -e ".[build-windows]"

    .\.venv\Scripts\python.exe tools\build_windows.py

Gerar o executável utilizando:

    PyInstaller --onedir

Nome:

    DSV-RFID.exe

Diretório:

    dist\DSV-RFID\

Garantir que o build não utilize
artefatos antigos inadvertidamente.

Preservar o script de build existente,
realizando apenas os ajustes necessários.

---

## 8. RF028.06 — VERIFICAÇÃO AUTOMATIZADA

Executar:

    .\.venv\Scripts\python.exe tools\verify_windows.py

Validar:

1. Inicialização do executável.
2. Carregamento dos recursos QML.
3. Carregamento do logo.
4. Disponibilidade dos plugins Qt.
5. Funcionamento sem Python no PATH.
6. Execução do modo preview.
7. Execução do modo configure.
8. Execução do check-config.
9. Criação do diretório de logs.
10. Gravação de mensagens de log.

Não considerar a geração do arquivo .exe
como validação suficiente.

O executável deverá iniciar corretamente.

---

## 9. RF028.07 — TESTES DE REGRESSÃO

Executar os testes automatizados
existentes antes da distribuição.

Verificar:

- Configurações RFID.
- Conexão Zebra FX9600.
- Múltiplas antenas RF026.
- Filtro EPC RF023.
- Comunicação Waveshare.
- Sensores DI1 e DI2.
- Relés CH1, CH2 e CH3.
- Timer de 60 segundos.
- Start/Stop.
- Backend Rails.
- Extra Box.
- Tabela QML.
- Botão dinâmico RF027.

Não modificar as regras operacionais.

Caso algum teste falhe:

1. Identificar a causa.
2. Informar o problema.
3. Corrigir apenas se estiver relacionado
   ao empacotamento ou logging.
4. Não ocultar falhas.
5. Não remover testes para aprovar o build.

---

## 10. RF028.08 — TESTES SEM HARDWARE

Executar os testes disponíveis sem
equipamentos físicos.

Validar:

- Inicialização da aplicação.
- Carregamento da interface.
- Navegação.
- Tela de configurações.
- Persistência de configurações.
- Logging.
- Recursos QML.
- Modo preview.
- Verificação de configuração.

Não afirmar que a comunicação RFID
ou Waveshare foi validada fisicamente
sem utilizar os equipamentos.

---

## 11. RF028.09 — TESTES COM HARDWARE

Preparar checklist para homologação
na estação operacional.

Equipamentos:

- Zebra FX9600.
- Antenas RFID.
- Waveshare Modbus RTU Relay.
- Sensores DI1 e DI2.

Validar:

1. Conexão Zebra.
2. Inventário com múltiplas antenas.
3. Identificação de EPC.
4. Filtro de prefixos.
5. Consulta Backend.
6. Registro de passagem.
7. Extra Box.
8. Comunicação Waveshare.
9. Estados dos relés.
10. Start/Stop.
11. Timer de 60 segundos.
12. Encerramento do inventário.
13. Logs persistentes.
14. Reinicialização do executável.
15. Persistência das configurações.

Essa validação deverá ser realizada
posteriormente com os equipamentos reais.

---

## 12. RF028.10 — DISTRIBUIÇÃO

O resultado deverá ser uma pasta:

    dist\DSV-RFID\

Contendo:

    DSV-RFID.exe

    _internal\

    .env.example

    Outros arquivos necessários ao runtime.

A pasta deverá ser distribuída integralmente.

Não distribuir somente o arquivo .exe.

Não exigir instalação separada do Python
no computador de destino.

Não incluir:

- Ambiente virtual.
- Código-fonte desnecessário.
- Arquivos .env reais.
- Credenciais.
- Logs de desenvolvimento.
- Cache de testes.

---

## 13. RF028.11 — PRESERVAÇÃO OPERACIONAL

Não modificar:

- Protocolo LLRP.
- Configuração de potência.
- Região regulatória.
- Fluxo RFID.
- Múltiplas antenas.
- Filtro EPC.
- Extra Box.
- Backend Rails.
- Banco PostgreSQL.
- Máquina de estados.
- Sensores.
- Relés.
- Timer.
- Interface QML.
- Layout.
- Botão dinâmico.
- Regras de negócio.

O RF028 deverá se limitar a:

- Empacotamento.
- Logging.
- Configuração externa.
- Validação.
- Distribuição.

---

## 14. CRITÉRIOS DE ACEITE

- [ ] Logs persistentes implementados.
- [ ] Rotação de logs funcionando.
- [ ] Diretório de logs criado automaticamente.
- [ ] Configurações externas preservadas.
- [ ] Arquivo .env real não incluído.
- [ ] Recursos QML incluídos.
- [ ] Logo DSV incluído.
- [ ] Dependências incluídas.
- [ ] Build Windows executado.
- [ ] DSV-RFID.exe gerado.
- [ ] Bundle atualizado.
- [ ] Verificação automatizada aprovada.
- [ ] Aplicação inicia sem Python no PATH.
- [ ] Tela de configurações funciona.
- [ ] Logs são gravados pelo executável.
- [ ] Testes automatizados aprovados.
- [ ] Nenhuma regressão operacional.
- [ ] Validação física identificada como pendente,
      caso não tenha sido executada.

---

## 15. RELATÓRIO FINAL

Ao finalizar, informar:

1. Branch utilizada.
2. Arquivos modificados.
3. Alterações no logging.
4. Diretório final dos logs.
5. Configurações externas utilizadas.
6. Comando de build executado.
7. Localização do executável.
8. Tamanho aproximado do bundle.
9. Resultado do verify_windows.py.
10. Testes automatizados executados.
11. Testes aprovados.
12. Testes que falharam, se houver.
13. Dependências incluídas.
14. Limitações identificadas.
15. Situação da homologação com hardware.
16. Instruções para executar o software.

Não realizar commit ou merge automaticamente.

---

## 16. DEFINIÇÃO DE PRONTO

O RF028 estará concluído quando:

1. O software gerar um executável Windows.
2. O executável iniciar corretamente.
3. Os recursos QML forem carregados.
4. As configurações externas funcionarem.
5. Os logs persistentes forem gravados.
6. O pacote funcionar sem Python instalado.
7. Os testes automatizados forem aprovados.
8. Nenhuma funcionalidade operacional regredir.

IMPLEMENTAR O RF028 UTILIZANDO A ESTRUTURA
DE BUILD EXISTENTE NO PROJETO.

NÃO CRIAR UM NOVO SISTEMA DE EMPACOTAMENTO.