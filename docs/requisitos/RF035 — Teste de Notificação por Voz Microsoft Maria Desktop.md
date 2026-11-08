# RF035 — Teste de Notificação por Voz Microsoft Maria Desktop

Projeto: DSV RFID System
Requisito: RF035
Requisito base: RF033
Categoria: Áudio / Interface / Testes
Tecnologia: Python + PySide6/QML
Sistema operacional: Windows
Branch de referência: feature/efeito-sonoro
Prioridade: Média

---

## 1. OBJETIVO

Implementar um recurso de notificação por voz
utilizando a voz feminina Microsoft Maria Desktop,
disponível no Windows.

A implementação deverá ocorrer exclusivamente
na área de testes de áudio do aplicativo,
onde atualmente testamos o bip sonoro do RF033.

O operador poderá informar uma quantidade
de caixas e solicitar a reprodução de uma frase.

Exemplo:

    Quantidade: 10

    Mensagem: "Passou 10 caixas"

IMPORTANTE:

Nesta etapa, não implementar a reprodução
automática durante a operação RFID.

O objetivo é apenas validar a integração
com a voz instalada no Windows.

---

## 2. CONTEXTO

O DSV RFID System já possui um recurso
de notificação sonora implementado no RF033.

Esse recurso reproduz um bip suave
quando um novo EPC válido é encontrado.

Agora precisamos testar uma segunda
forma de notificação:

    Notificação por voz.

A tecnologia escolhida será o mecanismo
nativo de síntese de fala do Windows.

A voz já foi instalada e testada
manualmente com sucesso.

Identificação:

    Nome: Microsoft Maria Desktop
    Idioma: Português (Brasil)
    Código: pt-BR
    Gênero: Feminino

Não será necessário utilizar:

- Piper TTS.
- Serviços de inteligência artificial.
- APIs externas.
- Serviços de nuvem.
- Conexão com a internet.

---

## 3. CONFIGURAÇÕES DA VOZ

Utilizar as seguintes configurações:

    Voz: Microsoft Maria Desktop

    Volume: 80%

    Velocidade: Normal

    Idioma: pt-BR

    Saída: Dispositivo de áudio padrão
           do Windows

    Funcionamento: Offline

Esses valores serão fixos nesta primeira etapa.

Não é necessário criar uma tela completa
de configurações de voz.

O objetivo é validar o funcionamento.

---

## 4. ÁREA DE TESTES

Localizar no projeto a área onde
atualmente testamos o bip do RF033.

Preservar os componentes existentes.

Adicionar uma nova seção:

    Notificação por voz — RF035

A organização sugerida será:

    +--------------------------------------+
    | TESTE DE ÁUDIO                       |
    +--------------------------------------+
    |                                      |
    | Bip RFID — RF033                     |
    |                                      |
    | [          Testar bip           ]    |
    |                                      |
    +--------------------------------------+
    |                                      |
    | Notificação por voz — RF035          |
    |                                      |
    | Voz: Microsoft Maria Desktop         |
    | Idioma: Português (Brasil)           |
    |                                      |
    | Quantidade de caixas                 |
    | [              10              ]    |
    |                                      |
    | Mensagem: Passou 10 caixas           |
    |                                      |
    | [          Testar voz           ]    |
    |                                      |
    +--------------------------------------+

Manter o tema Corporate Dark.

Preservar:

- Cores existentes.
- Tipografia.
- Espaçamentos.
- Botões.
- Componentes QML.
- Identidade visual do aplicativo.

Não criar uma nova janela se os controles
puderem ser adicionados à área existente.

---

## 5. CAMPO QUANTIDADE DE CAIXAS

Adicionar um campo numérico:

    Quantidade de caixas

Valor inicial:

    10

Permitir números inteiros:

    Mínimo: 0
    Máximo: 9999

Não permitir:

- Valores negativos.
- Números decimais.
- Caracteres alfabéticos.
- Campos vazios durante a execução.

Utilizar validação apropriada no QML
e também na camada Python.

---

## 6. MENSAGEM DE VOZ

A mensagem deverá ser construída
dinamicamente conforme a quantidade.

Formato:

    Passou {quantidade} caixas

Aplicar a regra de singular e plural.

Exemplos:

    0  -> Passou 0 caixas
    1  -> Passou 1 caixa
    2  -> Passou 2 caixas
    5  -> Passou 5 caixas
    10 -> Passou 10 caixas
    25 -> Passou 25 caixas
    100 -> Passou 100 caixas

A mensagem deverá ser apresentada
na interface antes da reprodução.

Quando a quantidade for alterada,
atualizar a mensagem automaticamente.

Não utilizar frases gravadas.

O texto deverá ser enviado diretamente
ao mecanismo de síntese de fala.

---

## 7. BOTÃO TESTAR VOZ

Adicionar o botão:

    Testar voz

Ao clicar:

1. Validar a quantidade informada.
2. Verificar a disponibilidade da voz.
3. Construir a mensagem.
4. Solicitar a reprodução.
5. Aguardar a conclusão sem bloquear a UI.
6. Restaurar o estado do botão.

Exemplo:

    Quantidade: 10

    Operador clica em Testar voz.

    Sistema reproduz:

    "Passou 10 caixas"

Não executar nenhuma leitura RFID.

Não consultar o backend.

Não modificar os contadores operacionais.

---

## 8. TECNOLOGIA DE SÍNTESE

Utilizar o mecanismo de síntese
de fala nativo do Windows.

A voz Microsoft Maria Desktop foi
validada por meio de System.Speech.

Código utilizado no teste manual:

    Add-Type -AssemblyName System.Speech

    $voz = New-Object System.Speech.Synthesis.SpeechSynthesizer

    $voz.SelectVoice("Microsoft Maria Desktop")

    $voz.Volume = 80

    $voz.Rate = 0

    $voz.Speak("Passou 10 caixas")

O Codex deverá avaliar a forma mais simples
e confiável de integrar esse mecanismo
ao aplicativo Python.

Alternativas permitidas:

- Integração com Windows SAPI.
- System.Speech via PowerShell controlado.
- Qt Text-to-Speech, caso consiga acessar
  corretamente a voz Microsoft Maria Desktop.

Priorizar a solução que:

- Preserve a voz escolhida.
- Funcione offline.
- Não adicione dependências pesadas.
- Seja compatível com PyInstaller.
- Não bloqueie a interface.
- Não abra janelas adicionais.

Se utilizar PowerShell:

- Não utilizar shell=True.
- Não interpolar entradas não validadas.
- Não abrir janelas de console.
- Tratar erros e timeout do processo.

Não instalar Piper TTS.

---

## 9. SERVIÇO DE VOZ

Criar um serviço independente para
gerenciar a reprodução das mensagens.

Responsabilidades:

- Verificar a disponibilidade da voz.
- Construir ou receber a mensagem validada.
- Executar a síntese.
- Informar início e término.
- Tratar falhas.
- Impedir reproduções simultâneas.

O serviço deverá ser reutilizável
em requisitos futuros.

Entretanto, nesta etapa,
não conectar o serviço ao fluxo RFID.

Evitar adicionar lógica de reprodução
diretamente dentro dos componentes QML.

Utilizar a arquitetura de serviços
já adotada pelo projeto.

---

## 10. REPRODUÇÃO ASSÍNCRONA

A síntese de voz não deverá bloquear
a interface gráfica.

Durante a reprodução:

- A interface deve continuar responsiva.
- O aplicativo não pode congelar.
- Não devem ocorrer reproduções sobrepostas.
- O botão Testar voz pode ficar desabilitado.
- O botão deve ser reabilitado ao finalizar.

Caso o usuário clique repetidamente,
não criar várias instâncias simultâneas
do sintetizador.

Utilizar o mecanismo de execução
assíncrona apropriado para PySide6.

Garantir encerramento seguro do serviço
quando a janela ou aplicativo for fechado.

---

## 11. VERIFICAÇÃO DA VOZ

Antes da reprodução, verificar se
a Microsoft Maria Desktop está disponível.

Nome esperado:

    Microsoft Maria Desktop

Idioma esperado:

    pt-BR

Se a voz estiver instalada:

    Permitir reprodução.

Se a voz não estiver instalada:

    Apresentar mensagem:

    "A voz Microsoft Maria Desktop
     não está instalada neste Windows."

Não substituir automaticamente por:

- Microsoft David Desktop.
- Microsoft Zira Desktop.
- Outras vozes em inglês.

Não encerrar o aplicativo.

Não bloquear os outros recursos.

O usuário será responsável por instalar
a voz no computador operacional.

Não implementar instalação automática
de pacotes de idioma nesta etapa.

---

## 12. PRESERVAR O RF033

O recurso de bip existente deverá
continuar funcionando normalmente.

Não modificar:

- Arquivo WAV.
- Frequência de 880 Hz.
- Duração de 80 ms.
- Intervalo mínimo de 300 ms.
- Fila de áudio.
- Critérios de acionamento.
- Lógica de EPC encontrado.

O teste de voz deverá funcionar
independentemente do teste de bip.

Não substituir o bip pela voz.

Não reproduzir a voz automaticamente
quando o bip for acionado.

---

## 13. ISOLAMENTO DO FLUXO OPERACIONAL

Esta implementação será exclusivamente
para testes.

Não alterar:

- Zebra FX9600.
- Comunicação LLRP.
- Inventário RFID.
- Filtro de EPCs.
- Sensores DI1 e DI2.
- Temporizador de 60 segundos.
- Waveshare Modbus RTU Relay D.
- Relés CH1, CH2 e CH3.
- Botões Start e Stop.
- Backend Rails.
- Registros de passagem.
- Contadores da tela Start.

Não implementar voz automática:

- Ao detectar DI1.
- Ao detectar DI2.
- Ao atingir o timeout.
- Ao finalizar o inventário.
- Ao clicar em Stop.
- Ao identificar um EPC.

A integração operacional será
desenvolvida em outro requisito.

---

## 14. SIMULADOR RFID

Não modificar o simulador RF034.

Não adicionar o recurso de voz
ao modal Simulador RFID nesta etapa.

O teste deverá permanecer exclusivamente
na área onde testamos o bip RF033.

Posteriormente, poderemos reutilizar
o serviço de voz no simulador.

---

## 15. COMPATIBILIDADE WINDOWS

O sistema operacional oficial
do projeto é Windows.

A implementação deverá funcionar
no ambiente de desenvolvimento
e no executável compilado.

Validar:

- Windows 10/11 compatível.
- Voz Microsoft Maria Desktop instalada.
- Saída de áudio padrão.
- Funcionamento offline.
- Execução sem console adicional.
- Compatibilidade com PyInstaller.

Não incorporar a voz Microsoft Maria
dentro do executável.

O aplicativo utilizará a voz
instalada no sistema operacional.

Não adicionar arquivos grandes
de modelos de inteligência artificial.

---

## 16. TESTES OBRIGATÓRIOS

### Teste 1 — Identificação da voz

Abrir a área de testes.

Confirmar:

    Microsoft Maria Desktop
    Português (Brasil)

### Teste 2 — Dez caixas

Informar:

    Quantidade: 10

Clicar:

    Testar voz

Resultado:

    "Passou 10 caixas"

### Teste 3 — Zero caixas

Informar:

    Quantidade: 0

Resultado:

    "Passou 0 caixas"

### Teste 4 — Uma caixa

Informar:

    Quantidade: 1

Resultado:

    "Passou 1 caixa"

### Teste 5 — Outras quantidades

Testar:

    2
    5
    25
    100

Confirmar a pronúncia correta.

### Teste 6 — Campo inválido

Tentar informar:

    -1
    2.5
    ABC

Confirmar que a entrada é rejeitada
ou validada corretamente.

### Teste 7 — Interface responsiva

Reproduzir uma mensagem.

Confirmar que a interface
não apresenta congelamentos.

### Teste 8 — Cliques repetidos

Clicar rapidamente no botão Testar voz.

Confirmar:

- Sem sobreposição de falas.
- Sem criação excessiva de processos.
- Sem travamento.

### Teste 9 — Voz indisponível

Simular ausência da voz.

Confirmar:

- Mensagem de erro.
- Aplicativo continua funcionando.
- Teste do bip permanece disponível.

### Teste 10 — Regressão RF033

Executar o teste do bip.

Confirmar que o som continua
funcionando exatamente como antes.

### Teste 11 — Sem equipamentos

Executar o teste de voz sem:

- Zebra FX9600.
- Waveshare.
- Backend Rails.
- Internet.

Confirmar funcionamento normal.

### Teste 12 — Executável

Gerar o executável Windows.

Confirmar:

- Voz reproduzida corretamente.
- Sem console adicional.
- Sem dependências ausentes.
- Sem aumento significativo do tamanho.

---

## 17. CRITÉRIOS DE ACEITE

- [ ] Área de teste de áudio localizada.
- [ ] Interface existente preservada.
- [ ] Seção de voz adicionada.
- [ ] Campo de quantidade implementado.
- [ ] Botão Testar voz implementado.
- [ ] Prévia da mensagem funcionando.
- [ ] Microsoft Maria Desktop selecionada.
- [ ] Idioma pt-BR validado.
- [ ] Volume configurado em 80%.
- [ ] Velocidade normal.
- [ ] Singular e plural corretos.
- [ ] Reprodução assíncrona.
- [ ] Sem falas simultâneas.
- [ ] Tratamento de voz indisponível.
- [ ] Funcionamento offline.
- [ ] Sem Piper TTS.
- [ ] Sem dependências pesadas.
- [ ] Tema Corporate Dark preservado.
- [ ] Bip RF033 preservado.
- [ ] Simulador RF034 não modificado.
- [ ] Fluxo operacional RFID não modificado.
- [ ] Compatibilidade Windows validada.
- [ ] Executável PyInstaller validado.

---

## 18. PROCEDIMENTO DO CODEX

Antes de implementar:

1. Ler AGENTS.md.
2. Verificar a branch atual.
3. Executar git status.
4. Identificar a implementação do RF033.
5. Localizar a área de teste do bip.
6. Identificar os serviços de áudio existentes.
7. Identificar os componentes QML relacionados.
8. Preservar alterações locais.

Durante a implementação:

- Reutilizar a arquitetura existente.
- Criar serviço de voz reutilizável.
- Preservar o serviço de bip.
- Evitar dependências desnecessárias.
- Não modificar o fluxo operacional.
- Manter o tema visual existente.
- Aplicar alterações mínimas.

Após implementar:

1. Executar testes automatizados disponíveis.
2. Validar a reprodução da voz.
3. Validar singular e plural.
4. Validar tratamento de erros.
5. Testar o bip RF033.
6. Verificar a responsividade.
7. Validar o executável Windows, se disponível.
8. Executar git diff.
9. Apresentar relatório dos arquivos modificados.
10. Informar testes executados e limitações.

Não executar git reset --hard.
Não descartar alterações locais.

Não realizar commit automaticamente.
Não realizar push automaticamente.
Não realizar merge na main.

---

## 19. RESULTADO ESPERADO

A área de testes de áudio do DSV RFID System
deverá apresentar dois recursos independentes:

    1. Testar bip RFID — RF033

    2. Testar voz — RF035

O operador poderá informar uma quantidade
e ouvir a mensagem correspondente utilizando
a voz Microsoft Maria Desktop.

Exemplo:

    Quantidade: 10

    Mensagem: "Passou 10 caixas"

O sistema deverá funcionar offline,
sem bibliotecas pesadas e sem modificar
o funcionamento real do portal RFID.

IMPLEMENTAR O RF035.

IMPLEMENTAÇÃO EXCLUSIVA NA ÁREA DE TESTES.

NÃO INTEGRAR A VOZ AO FLUXO OPERACIONAL
NESTA ETAPA.