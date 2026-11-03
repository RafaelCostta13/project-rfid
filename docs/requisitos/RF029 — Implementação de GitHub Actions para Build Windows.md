# RF029 — Implementação de GitHub Actions para Build Windows

Projeto: DSV RFID System
Requisito: RF029
Categoria: Automação / Distribuição / Segurança
Prioridade: Alta
Ambiente de desenvolvimento: Linux ou Windows
Ambiente de compilação: Windows x64
Linguagem: Python 3.12
Interface: PySide6 + QML
Ferramenta de empacotamento: PyInstaller

---

# 1. OBJETIVO

Implementar GitHub Actions para gerar automaticamente
um executável Windows do DSV RFID System.

O desenvolvedor deverá conseguir:

1. Desenvolver o software no Linux.
2. Enviar as alterações ao GitHub.
3. Acessar a página GitHub Actions.
4. Iniciar manualmente a compilação Windows.
5. Acompanhar o resultado dos testes.
6. Baixar o pacote gerado.
7. Extrair o pacote em um computador Windows.
8. Executar o DSV-RFID.exe sem instalar Python.

IMPORTANTE:

A compilação local no Windows deverá continuar
funcionando normalmente.

O GitHub Actions será um método adicional de build,
não um substituto do processo existente.

---

# 2. CONTEXTO DO PROJETO

O projeto utiliza:

- Python 3.12.
- PySide6 6.10.3.
- QML.
- sllurp para Zebra FX9600.
- pymodbus para Waveshare.
- pyserial.
- python-dotenv.
- Backend Rails API.
- Configurações externas.
- Logs persistentes.

O projeto já possui:

    packaging/windows_entry.py

    tools/build_windows.py

    tools/verify_windows.py

O RF028 implementou ou preparou o empacotamento
Windows utilizando PyInstaller --onedir.

REGRAS:

- Reutilizar os scripts existentes.
- Não criar outro sistema de empacotamento.
- Não duplicar lógica de build.
- Não modificar o funcionamento operacional do RFID.
- Não substituir o PyInstaller sem justificativa técnica.

---

# 3. ANÁLISE INICIAL OBRIGATÓRIA

Antes de implementar:

1. Ler AGENTS.md.
2. Verificar a branch atual.
3. Executar git status.
4. Identificar alterações locais existentes.
5. Examinar pyproject.toml.
6. Examinar os scripts de build e verificação.
7. Identificar os testes automatizados.
8. Verificar a estrutura de diretórios.
9. Verificar se já existem workflows GitHub Actions.
10. Verificar como o RF028 trata logs e configurações.

Não sobrescrever alterações locais do usuário.

Não apagar arquivos existentes.

Não executar git reset --hard.

Não executar git clean -fd.

Se já existir um workflow semelhante, avaliar
sua reutilização antes de criar outro.

---

# 4. ESTRUTURA DO GITHUB ACTIONS

Criar o arquivo:

    .github/workflows/build-windows.yml

Nome exibido no GitHub:

    Build DSV RFID Windows

A implementação deverá utilizar:

    workflow_dispatch

Inicialmente, a execução será exclusivamente manual.

NÃO configurar automaticamente:

- push.
- pull_request.
- pull_request_target.
- schedule.
- release.
- deployment.

MOTIVO:

O usuário está começando a utilizar GitHub Actions.

Nesta primeira implementação, ele deverá ter
controle sobre quando a compilação será executada.

Não executar build automaticamente a cada commit.

Não criar releases automaticamente.

Não publicar executáveis em páginas públicas.

---

# 5. AMBIENTE DE COMPILAÇÃO

Utilizar um runner Windows hospedado pelo GitHub.

Preferência inicial:

    runs-on: windows-2022

Validar a disponibilidade e compatibilidade
do runner com as Actions selecionadas.

Configurar:

    Python 3.12
    Arquitetura x64

Não utilizar Linux para gerar diretamente
o executável Windows com PyInstaller.

O executável deverá ser produzido
nativamente em ambiente Windows.

Configurar timeout para evitar execuções
indefinidas.

Sugestão inicial:

    timeout-minutes: 30

Não instalar ferramentas de sistema
desnecessárias.

---

# 6. SEGURANÇA DO WORKFLOW

Este requisito é obrigatório.

O workflow deverá seguir o princípio
do menor privilégio.

Configurar explicitamente:

    permissions:
      contents: read

Não conceder:

- contents: write.
- actions: write.
- packages: write.
- deployments: write.
- id-token: write.

Não utilizar permissões de administrador.

Não criar tokens de acesso pessoal.

Não utilizar PAT.

Não utilizar chaves SSH para o build.

Não utilizar credenciais de produção.

Não solicitar segredos GitHub para compilar.

A compilação deverá funcionar sem secrets.

O checkout deverá utilizar:

    persist-credentials: false

Utilizar somente Actions oficiais do GitHub,
quando possível.

Exemplos:

- actions/checkout.
- actions/setup-python.
- actions/upload-artifact.

Utilizar versões estáveis compatíveis.

Para proteção da cadeia de suprimentos,
preferir Actions fixadas por SHA completo
de commit, verificado no repositório oficial.

Não inventar valores SHA.

Se não for possível verificar um SHA,
informar a limitação e não substituir
por um identificador não verificado.

Não utilizar Actions desconhecidas
de terceiros sem justificativa.

Não executar comandos externos
no formato curl | bash.

Não executar scripts remotos não auditados.

Não utilizar código proveniente de pull requests
não confiáveis em contextos privilegiados.

Não imprimir variáveis sensíveis nos logs.

Não habilitar debug detalhado contendo
informações confidenciais.

---

# 7. PROTEÇÃO DO CÓDIGO-FONTE

O workflow deverá apenas:

1. Ler o repositório.
2. Instalar dependências.
3. Executar testes.
4. Gerar o executável.
5. Verificar o executável.
6. Disponibilizar o pacote para download.

Não deverá:

- Alterar a branch main.
- Criar commits.
- Executar git push.
- Fazer merge.
- Criar tags.
- Criar GitHub Releases.
- Publicar código em outro repositório.
- Enviar arquivos para serviços externos
  além dos necessários ao build.

O código-fonte deverá permanecer
sob o controle do usuário.

Não alterar a visibilidade do repositório.

---

# 8. INSTALAÇÃO DAS DEPENDÊNCIAS

Utilizar a configuração existente no projeto.

Comando de referência:

    python -m pip install --upgrade pip

    python -m pip install -e ".[build-windows]"

Verificar se a configuração atual do
pyproject.toml suporta esse comando.

Não criar um requirements.txt duplicado
sem necessidade.

Não atualizar indiscriminadamente
as dependências do projeto.

Preservar as versões definidas.

Caso existam dependências sem versão fixa,
identificar o risco de builds não reproduzíveis.

Se existir arquivo de lock ou constraints,
utilizar a estratégia oficial do projeto.

Executar:

    python -m pip check

O workflow deverá falhar caso existam
incompatibilidades relevantes.

---

# 9. EXECUÇÃO DOS TESTES

Antes de gerar o executável:

Executar os testes automatizados existentes
que sejam compatíveis com o runner Windows.

Identificar o comando correto de testes
a partir da estrutura real do projeto.

Não presumir que pytest esteja configurado
sem verificar.

Não criar testes fictícios.

Não remover testes existentes.

Não utilizar:

    continue-on-error: true

para ignorar falhas de testes obrigatórios.

Não utilizar:

    || true

para mascarar erros.

Testes que dependam de equipamentos físicos
deverão ser identificados separadamente.

O runner GitHub não possui:

- Zebra FX9600.
- Antenas RFID físicas.
- Waveshare.
- Sensores DI1 e DI2.

Portanto, testes de hardware devem ser
simulados ou excluídos de maneira explícita
e documentada.

Não afirmar que houve homologação física.

---

# 10. GERAÇÃO DO EXECUTÁVEL

Utilizar obrigatoriamente:

    python tools/build_windows.py

Não substituir o script por comandos
PyInstaller duplicados dentro do YAML.

O resultado esperado será:

    dist/
    └── DSV-RFID/
        ├── DSV-RFID.exe
        ├── _internal/
        └── .env.example

A estrutura exata deverá respeitar
o empacotamento atual do projeto.

O executável deverá continuar utilizando
PyInstaller --onedir.

Garantir que o build seja limpo.

Não aproveitar um bundle antigo presente
na pasta dist.

O build deverá refletir exatamente
o commit utilizado na execução.

---

# 11. VERIFICAÇÃO DO EXECUTÁVEL

Após o build, executar:

    python tools/verify_windows.py

Verificar:

1. Existência de DSV-RFID.exe.
2. Existência da pasta _internal.
3. Recursos QML.
4. Logo DSV.
5. Plugins Qt.
6. Inicialização do aplicativo.
7. Dependências Python empacotadas.
8. Modo preview.
9. Modo configure.
10. Check-config.
11. Funcionamento sem Python no PATH.

Verificar o comportamento do script
no ambiente GitHub Actions.

O runner pode não disponibilizar uma
sessão gráfica interativa convencional.

Se necessário, adaptar os smoke tests
para execução não interativa.

Não desabilitar testes silenciosamente.

Não deixar processos gráficos abertos
indefinidamente.

Não substituir a validação real por
uma simples verificação de existência do EXE.

Se a verificação falhar, o workflow
deverá terminar com erro.

---

# 12. PROTEÇÃO DOS ARQUIVOS DE CONFIGURAÇÃO

ATENÇÃO ESPECIAL A ESTA ETAPA.

O projeto utiliza arquivos de configuração
que podem conter informações sensíveis.

Nunca incluir no pacote:

    .env

    station.env

    *.key

    *.pem

    Credenciais reais

    Tokens

    Senhas

    Dados operacionais de produção

    Bancos SQLite operacionais

    Logs de produção

O arquivo permitido será:

    .env.example

Desde que contenha apenas valores de exemplo
e não exponha informações sensíveis.

Verificar o conteúdo do .env.example.

Não copiar automaticamente todos os
arquivos ocultos do repositório.

Não utilizar upload-artifact apontando
para a raiz do projeto.

O upload deverá conter exclusivamente
o pacote de distribuição validado.

IMPORTANTE:

O GitHub Actions pode excluir arquivos
iniciados com ponto durante o upload.

Para garantir a inclusão controlada
do .env.example, criar um ZIP do bundle
utilizando Python zipfile, após validar
os arquivos que serão incluídos.

Não habilitar indiscriminadamente
include-hidden-files: true.

---

# 13. CRIAÇÃO DO PACOTE ZIP

Após o build e a verificação:

Criar um pacote ZIP contendo
a pasta completa DSV-RFID.

Nome sugerido:

    DSV-RFID-Windows-<commit-curto>.zip

Exemplo ilustrativo:

    DSV-RFID-Windows-a1b2c3d.zip

A identificação deverá utilizar
o commit real do GitHub Actions.

Estrutura interna:

    DSV-RFID/
        DSV-RFID.exe
        _internal/
        .env.example

Preservar todos os arquivos necessários.

Não incluir:

- Código-fonte desnecessário.
- Ambiente virtual.
- Arquivos de desenvolvimento.
- Diretório .git.
- Diretório .github.
- Credenciais.
- Logs.
- Dados operacionais.

Antes de gerar o ZIP:

1. Validar a pasta de distribuição.
2. Verificar arquivos obrigatórios.
3. Verificar arquivos proibidos.
4. Falhar caso algum arquivo sensível
   ou inesperado seja identificado.

Implementar essa validação de maneira
restritiva e verificável.

Não considerar a ausência de um arquivo
sensível conhecido como prova absoluta
de que o pacote não contém segredos.

---

# 14. INTEGRIDADE E IDENTIFICAÇÃO

Gerar um hash SHA-256 do ZIP final.

Utilizar uma ferramenta padrão do Windows
ou uma implementação Python.

Gerar um arquivo de checksum contendo:

- Nome do pacote.
- Hash SHA-256.

Exemplo:

    DSV-RFID-Windows-a1b2c3d.zip
    SHA256: <hash-real>

Não utilizar valores fictícios
no resultado da compilação.

Registrar no relatório do build:

- Commit completo.
- Branch.
- Versão do Python.
- Versão do PyInstaller.
- Nome do pacote.
- Tamanho do pacote.
- Hash SHA-256.
- Resultado dos testes.

Essas informações não devem conter segredos.

O hash serve para verificação de integridade,
não substitui uma assinatura digital
do executável.

---

# 15. DISPONIBILIZAÇÃO NO GITHUB

Utilizar:

    actions/upload-artifact

Publicar somente:

- ZIP validado do DSV RFID System.
- Arquivo de checksum correspondente.

Nome sugerido do artifact:

    DSV-RFID-Windows

Configurar:

    if-no-files-found: error

Retenção sugerida:

    retention-days: 7

Verificar a política de retenção do repositório.

Não publicar automaticamente em GitHub Releases.

Não criar links públicos externos.

Não enviar o pacote para serviços
de armazenamento de terceiros.

O download deverá ocorrer pela
interface do GitHub Actions.

O artifact deverá permitir recuperar
a pasta completa do executável.

---

# 16. TRATAMENTO DE FALHAS

O workflow deverá indicar claramente
em qual etapa ocorreu uma falha.

Etapas recomendadas:

1. Checkout do repositório.
2. Configuração do Python.
3. Instalação das dependências.
4. Validação das dependências.
5. Testes automatizados.
6. Build Windows.
7. Verificação do executável.
8. Auditoria dos arquivos.
9. Criação do ZIP.
10. Geração do checksum.
11. Upload do artifact.

Se qualquer etapa obrigatória falhar:

- Interromper o processo.
- Apresentar o erro.
- Não publicar o pacote como aprovado.
- Não mascarar a falha.
- Não realizar correções perigosas automaticamente.

Evitar logs excessivamente detalhados
que possam expor dados do ambiente.

---

# 17. CONTROLE DE EXECUÇÕES

Implementar proteção básica contra
execuções concorrentes desnecessárias.

Utilizar concurrency quando apropriado.

Não cancelar automaticamente uma compilação
já iniciada sem necessidade.

Não implementar execução recorrente.

Não implementar publicação automática.

A primeira versão deverá continuar
dependendo de acionamento manual.

---

# 18. DOCUMENTAÇÃO PARA INICIANTES

Criar:

    docs/github-actions-windows.md

O documento deverá ser escrito
em português brasileiro.

Considerar que o usuário não possui
experiência com GitHub Actions.

Explicar objetivamente:

## 18.1 O que é GitHub Actions

Explicar:

- Workflow.
- Job.
- Step.
- Runner.
- Artifact.

Utilizar linguagem simples.

## 18.2 Como executar

Incluir instruções:

1. Acessar o repositório GitHub.
2. Abrir a aba Actions.
3. Selecionar Build DSV RFID Windows.
4. Clicar em Run workflow.
5. Selecionar a branch correta.
6. Confirmar a execução.
7. Aguardar o resultado.

Explicar que o workflow deverá estar
presente na branch padrão para aparecer
como opção de execução manual.

## 18.3 Como acompanhar

Explicar:

- Indicador verde: sucesso.
- Indicador vermelho: falha.
- Como abrir os detalhes da execução.
- Como identificar a etapa com erro.

## 18.4 Como baixar

Explicar:

1. Abrir a execução concluída.
2. Localizar Artifacts.
3. Baixar DSV-RFID-Windows.
4. Extrair o artifact.
5. Extrair o ZIP de distribuição.
6. Copiar a pasta DSV-RFID para o Windows.
7. Executar DSV-RFID.exe.

Explicar que o usuário não deve
copiar somente o EXE.

## 18.5 Configuração da estação

Explicar o uso do arquivo externo:

    C:\ProgramData\DSV-RFID\station.env

Exemplo de execução:

    C:\DSV-RFID\DSV-RFID.exe --env-file C:\ProgramData\DSV-RFID\station.env

Explicar que o station.env deve ser
criado ou fornecido de forma segura
na estação de destino.

Não incluir credenciais reais
na documentação.

## 18.6 Compilação local Windows

Documentar que continua disponível:

    python tools/build_windows.py

    python tools/verify_windows.py

Explicar que GitHub Actions não é
obrigatório para compilar localmente.

## 18.7 Custos e limites

Explicar que o GitHub Actions está
sujeito às cotas, políticas e cobrança
aplicáveis ao plano e repositório.

Não afirmar que o serviço é ilimitado
ou permanentemente gratuito.

---

# 19. CONFIGURAÇÕES DE SEGURANÇA NO GITHUB

Adicionar ao documento um checklist
para o usuário verificar no GitHub.

Caminho:

    Repository
    → Settings
    → Actions
    → General

Orientar a verificar:

1. Se GitHub Actions está habilitado.
2. Quais Actions são permitidas.
3. Se as Actions oficiais são permitidas.
4. Permissões padrão do GITHUB_TOKEN.
5. Políticas de execução aplicáveis.

Recomendar permissões somente de leitura
para o token, quando compatíveis
com o workflow.

Não solicitar ao usuário que conceda
permissões de escrita desnecessárias.

Não alterar configurações do repositório
automaticamente.

Se alguma política impedir o build,
documentar o motivo e solicitar
uma decisão do usuário.

---

# 20. COMPATIBILIDADE COM BUILD LOCAL

A implementação deverá preservar:

    tools/build_windows.py

    tools/verify_windows.py

A compilação local Windows deverá continuar
utilizando os mesmos comandos existentes.

Não introduzir dependência obrigatória
do GitHub para gerar o executável.

Não introduzir chamadas obrigatórias
à API do GitHub no aplicativo.

Não adicionar GitHub Actions como
dependência do software em produção.

O sistema RFID deverá continuar
funcionando sem conexão com GitHub.

---

# 21. LIMITAÇÕES DO EXECUTÁVEL

O workflow não deverá alterar:

- Comunicação Zebra FX9600.
- Comunicação LLRP.
- Múltiplas antenas.
- Filtro EPC.
- Comunicação Waveshare.
- Sensores DI1 e DI2.
- Relés CH1, CH2 e CH3.
- Timer de leitura.
- Extra Box.
- Backend Rails.
- Banco de dados.
- Interface QML.
- Layout.
- Botão Start/Stop.
- Regras operacionais.

O objetivo é exclusivamente
automatizar a compilação Windows.

O workflow não substitui testes
físicos na estação RFID.

O executável poderá precisar de
homologação e assinatura digital
antes de distribuição em produção.

Não implementar assinatura digital
neste requisito.

---

# 22. TESTES DO RF029

Executar os testes locais disponíveis
para validar os arquivos adicionados.

Verificar:

- Sintaxe YAML.
- Estrutura do workflow.
- Permissões mínimas.
- Ausência de secrets.
- Ausência de publicação automática.
- Compatibilidade dos comandos de build.
- Caminhos dos scripts.
- Inclusão do .env.example.
- Exclusão de arquivos sensíveis.
- Geração correta do ZIP.
- Geração correta do SHA-256.
- Documentação de utilização.

Se existir ferramenta de validação
de GitHub Actions disponível,
utilizá-la quando apropriado.

Não instalar ferramentas desnecessárias
sem justificativa.

Não afirmar que o workflow executou
com sucesso no GitHub sem uma execução real.

---

# 23. CRITÉRIOS DE ACEITE

- [ ] Workflow criado em .github/workflows.
- [ ] Execução exclusivamente manual.
- [ ] Runner Windows x64 configurado.
- [ ] Python 3.12 configurado.
- [ ] Permissões mínimas definidas.
- [ ] Checkout sem credenciais persistentes.
- [ ] Actions oficiais e versões verificadas.
- [ ] Dependências instaladas.
- [ ] Testes automatizados executados.
- [ ] Build Windows executado.
- [ ] verify_windows.py executado.
- [ ] DSV-RFID.exe gerado.
- [ ] Recursos QML incluídos.
- [ ] Pasta _internal incluída.
- [ ] .env.example incluído.
- [ ] Arquivos sensíveis excluídos.
- [ ] ZIP de distribuição gerado.
- [ ] Hash SHA-256 gerado.
- [ ] Artifact disponível para download.
- [ ] Falhas não são ocultadas.
- [ ] Documentação em português criada.
- [ ] Build local Windows preservado.
- [ ] Nenhuma regra operacional alterada.

IMPORTANTE:

Diferenciar critérios verificados localmente
daqueles que dependem de execução no GitHub.

---

# 24. RELATÓRIO FINAL DO CODEX

Ao concluir, apresentar:

1. Branch utilizada.
2. Arquivos criados.
3. Arquivos modificados.
4. Nome do workflow.
5. Eventos que iniciam o workflow.
6. Runner utilizado.
7. Versão do Python.
8. Actions utilizadas e versões/SHA.
9. Permissões concedidas.
10. Comandos de build.
11. Comandos de teste.
12. Estrutura do pacote.
13. Estratégia de proteção de arquivos.
14. Estratégia de checksum.
15. Caminho da documentação.
16. Testes executados.
17. Resultados dos testes.
18. Limitações identificadas.
19. Etapas que dependem do GitHub.
20. Instruções para o primeiro uso.

Informar explicitamente:

- Se o workflow foi apenas criado.
- Se foi validado localmente.
- Se foi executado no GitHub.
- Se o artifact foi efetivamente gerado.

Não declarar sucesso de etapas
que ainda não foram executadas.

---

# 25. RESTRIÇÕES FINAIS

NÃO:

- Fazer commit automaticamente.
- Fazer push automaticamente.
- Fazer merge na main.
- Alterar permissões do repositório.
- Criar GitHub Secrets.
- Criar tokens.
- Publicar GitHub Releases.
- Expor arquivos .env.
- Enviar dados para terceiros.
- Modificar regras RFID.
- Modificar a interface QML.
- Substituir os scripts de build existentes.

IMPLEMENTAR O RF029 COM FOCO EM:

SEGURANÇA
SIMPLICIDADE
REPRODUTIBILIDADE
RASTREABILIDADE
COMPATIBILIDADE COM WINDOWS

Ao finalizar, aguardar revisão e autorização
do usuário para enviar as alterações ao GitHub.