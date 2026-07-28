````markdown
# RF008 — Configurar conexão com o Reader RFID pela interface

## Objetivo

Permitir que o usuário visualize, altere, teste e salve as configurações de conexão do reader RFID diretamente pela tela já existente:

```text
Configurações RFID
````

Atualmente, os dados do reader são configurados manualmente em arquivo.

A nova funcionalidade deve permitir alterar pela interface:

* nome do reader;
* endereço IP;
* porta de comunicação.

As informações devem continuar sendo persistidas no arquivo de configuração já utilizado pela aplicação.

Deixar como default o IP e porta do reader:
RFID_READER_HOST=192.168.0.214
RFID_READER_PORT=5084
RFID_READER_NAME=fx9600-01

Não é necessário criar banco de dados.

---

# Contexto atual

A aplicação já possui:

* tela `Configurações RFID`;
* comunicação com reader RFID;
* conexão com Zebra FX9600;
* configuração carregada por arquivo;
* campos internos para:

  * nome do reader;
  * endereço IP;
  * porta;
* rotina de conexão já utilizada pela aplicação.

A nova funcionalidade deve reaproveitar essa estrutura.

Não criar um segundo arquivo de configuração sem necessidade.

Não duplicar a lógica de conexão com o reader.

---

# Resultado esperado

Na tela `Configurações RFID`, exibir um formulário semelhante a:

```text
Configurações RFID

Nome do reader
[ Reader Doca 01                         ]

Endereço IP
[ 192.168.0.214                         ]

Porta
[ 5084                                  ]

[ Testar conexão ]       [ Salvar configurações ]
```

Também deve existir uma área para apresentar o resultado do teste ou do salvamento.

Exemplos:

```text
Conexão realizada com sucesso.
```

```text
Não foi possível conectar ao reader.
```

```text
Configurações salvas com sucesso.
```

---

# Campos da tela

## Nome do reader

Campo de texto usado para identificar o equipamento dentro da aplicação.

Exemplo:

```text
Reader Doca 01
```

---

## Endereço IP

Campo de texto contendo o endereço IPv4 ou hostname do reader.

Exemplos válidos:

```text
192.168.0.214
```

```text
reader-doca-01
```

Caso o projeto atualmente aceite apenas IP, manter somente validação de IPv4.

Não ampliar para hostname sem necessidade.

---

## Porta

Campo numérico contendo a porta usada na comunicação LLRP.

Exemplo:

```text
5084
```

A porta não deve ser assumida como fixa.

---

# Botões

## Testar conexão

O botão deve testar a conexão utilizando os valores atualmente preenchidos no formulário.

O teste não deve exigir que as configurações tenham sido salvas previamente.

Exemplo:

1. O usuário altera o IP.
2. Clica em `Testar conexão`.
3. A aplicação testa o novo IP digitado.
4. O arquivo de configuração permanece inalterado.
5. Somente ao clicar em `Salvar configurações` os valores são persistidos.

---

## Salvar configurações

O botão deve validar os campos e gravar os novos valores no arquivo de configuração já existente.

Após salvar, a aplicação deve utilizar os novos dados conforme a estratégia já adotada pelo projeto.

Caso a aplicação precise ser reiniciada para aplicar as alterações, isso deve ser informado claramente ao usuário.

Preferencialmente, atualizar a configuração em memória sem exigir reinicialização, desde que isso não introduza risco ou refatoração ampla.

---

# Requisitos funcionais

## RF001 — Exibir as configurações atuais

Ao abrir a tela `Configurações RFID`, preencher os campos com os valores atualmente carregados do arquivo de configuração.

Exemplo:

```text
Nome do reader: Reader Principal
Endereço IP: 192.168.0.214
Porta: 5084
```

---

## RF002 — Editar nome do reader

Permitir que o usuário altere o nome do reader.

O nome deve ser salvo no mesmo campo já utilizado internamente pela aplicação.

---

## RF003 — Editar endereço IP

Permitir que o usuário altere o endereço IP do reader.

O valor não deve ser aplicado ou salvo antes da validação.

---

## RF004 — Editar porta

Permitir que o usuário altere a porta de comunicação.

A porta deve ser tratada internamente como número inteiro.

---

## RF005 — Validar nome do reader

O nome do reader:

* não pode ser vazio;
* não pode conter apenas espaços;
* deve ter os espaços do início e do fim removidos antes do salvamento.

Não impor limite excessivamente pequeno.

Caso exista padrão de limite no projeto, reutilizá-lo.

---

## RF006 — Validar endereço IP

Caso o projeto utilize IPv4, validar se o valor possui formato válido.

Exemplos válidos:

```text
192.168.0.214
10.0.0.15
```

Exemplos inválidos:

```text
192.168.0.999
192.168
texto vazio
```

Não verificar a disponibilidade do reader durante a validação básica.

A disponibilidade será verificada pelo botão `Testar conexão`.

---

## RF007 — Validar porta

A porta:

* deve ser numérica;
* deve ser inteira;
* deve estar entre `1` e `65535`.

Exemplos inválidos:

```text
0
65536
abc
5084.5
```

---

## RF008 — Testar conexão com os dados do formulário

Ao clicar em `Testar conexão`, utilizar:

* IP digitado;
* porta digitada;
* nome digitado somente como identificação do teste.

O teste deve utilizar os valores do formulário, mesmo que sejam diferentes do arquivo atualmente salvo.

---

## RF009 — Não salvar durante o teste

O botão `Testar conexão` não deve alterar o arquivo de configuração.

Também não deve substituir permanentemente a configuração em memória da aplicação.

---

## RF010 — Informar teste em andamento

Enquanto o teste estiver em execução:

* exibir indicação como `Testando conexão...`;
* impedir múltiplos testes simultâneos;
* desabilitar temporariamente o botão de teste, se necessário.

---

## RF011 — Informar sucesso no teste

Quando a conexão for estabelecida corretamente, exibir:

```text
Conexão realizada com sucesso.
```

Opcionalmente, incluir o endereço utilizado:

```text
Conexão realizada com sucesso em 192.168.0.214:5084.
```

Não exibir dados técnicos desnecessários ao usuário.

---

## RF012 — Informar falha no teste

Quando a conexão falhar, exibir mensagem amigável.

Exemplos:

```text
Não foi possível conectar ao reader.
```

```text
Tempo limite de conexão excedido.
```

```text
Conexão recusada pelo reader.
```

Os detalhes técnicos devem ser enviados ao log.

---

## RF013 — Encerrar conexão de teste

Após um teste bem-sucedido, a conexão temporária deve ser encerrada corretamente.

O teste não deve:

* iniciar inventário;
* manter sessão LLRP aberta;
* interferir na leitura atual;
* deixar socket aberto;
* criar conexão duplicada permanente.

---

## RF014 — Impedir teste durante inventário ativo

Caso exista uma sessão de leitura RFID ativa, o sistema não deve abrir uma conexão de teste concorrente com o mesmo reader.

Neste caso, informar:

```text
Pare a leitura RFID antes de testar uma nova configuração.
```

Não interromper automaticamente uma leitura ativa.

---

## RF015 — Salvar configurações

Ao clicar em `Salvar configurações`, validar os campos e gravar:

* nome do reader;
* endereço IP;
* porta.

Utilizar o arquivo de configuração já existente no projeto.

---

## RF016 — Não salvar valores inválidos

Se qualquer campo for inválido:

* não alterar o arquivo;
* destacar ou informar o campo com problema;
* preservar os valores digitados no formulário para correção.

---

## RF017 — Confirmar salvamento

Após salvar com sucesso, exibir:

```text
Configurações salvas com sucesso.
```

---

## RF018 — Tratar falha de escrita

Caso o arquivo não possa ser atualizado:

* não informar sucesso;
* registrar o erro técnico;
* exibir mensagem amigável.

Exemplo:

```text
Não foi possível salvar as configurações.
```

---

## RF019 — Preservar demais configurações

Ao atualizar nome, IP e porta, não remover ou sobrescrever outras configurações existentes no arquivo.

A escrita deve alterar somente os campos relacionados ao reader.

---

## RF020 — Atualizar configuração em memória

Após salvar, atualizar o objeto de configuração utilizado pela aplicação, desde que seja seguro dentro da arquitetura atual.

A próxima conexão deve utilizar os novos valores.

Não manter valores antigos em memória quando o arquivo já possuir os novos valores.

---

## RF021 — Não reconectar automaticamente

Salvar as configurações não deve iniciar automaticamente uma conexão com o reader.

O usuário poderá:

* testar antes de salvar;
* salvar;
* iniciar a leitura posteriormente.

---

## RF022 — Manter campos após salvar

Após o salvamento, os campos devem permanecer preenchidos com os valores salvos.

Não limpar o formulário.

---

## RF023 — Carregar configuração novamente

Ao sair e retornar à tela, os valores exibidos devem corresponder à configuração atualmente salva.

---

# Regras de negócio

## RN001 — Arquivo existente é a fonte persistente

O arquivo de configuração atual continua sendo a fonte persistente das informações do reader.

Não criar banco de dados.

---

## RN002 — Testar não significa salvar

O teste de conexão e o salvamento são ações independentes.

Um teste bem-sucedido não deve salvar automaticamente os dados.

---

## RN003 — Salvar não significa testar

O usuário pode salvar uma configuração válida sintaticamente mesmo sem testar a conexão.

Não exigir teste bem-sucedido como condição obrigatória para salvar, salvo se essa regra já existir no projeto.

---

## RN004 — Teste sem inventário

O teste deve validar somente a conexão com o reader.

Não iniciar leitura de etiquetas.

---

## RN005 — Configuração temporária isolada

Durante o teste, criar uma configuração temporária com os valores do formulário.

Não modificar o estado permanente antes do salvamento.

---

## RN006 — Leitura ativa tem prioridade

Uma leitura RFID ativa não deve ser interrompida pela tela de configurações.

---

## RN007 — Porta configurável

Não assumir que a porta será sempre:

```text
5084
```

A porta deve continuar configurável.

---

## RN008 — Nome não interfere na conexão

O nome do reader é uma identificação interna e visual.

A conexão deve utilizar:

* endereço IP;
* porta.

---

# Persistência no arquivo

## Reaproveitar o formato atual

Antes de implementar:

1. identificar o arquivo utilizado atualmente;
2. identificar o formato:

   * `.env`;
   * JSON;
   * TOML;
   * YAML;
   * INI;
   * outro;
3. localizar a classe ou função responsável por carregar a configuração;
4. reutilizar a mesma estrutura.

Não criar uma segunda fonte de configuração.

---

## Escrita segura

A gravação deve reduzir o risco de corromper o arquivo.

Preferencialmente:

1. ler a configuração atual;
2. alterar somente os campos necessários;
3. gravar em arquivo temporário;
4. substituir o arquivo original de forma segura.

Caso o projeto já possua utilitário de escrita, reutilizá-lo.

---

## Preservação do arquivo

A operação de salvamento deve preservar:

* demais chaves;
* estrutura válida;
* encoding;
* valores não relacionados ao RFID.

Se o arquivo contiver comentários e o formato permitir preservá-los, evitar removê-los sem necessidade.

---

## Valores esperados

Adaptar aos nomes reais do projeto.

Exemplo conceitual:

```env
RFID_READER_NAME=Reader Doca 01
RFID_READER_IP=192.168.0.214
RFID_READER_PORT=5084
```

Não renomear as variáveis atuais sem necessidade.

---

# Segurança

## Não exibir segredos

Caso o arquivo possua outras configurações sensíveis:

* não carregá-las na interface;
* não exibi-las;
* não registrá-las no log;
* não sobrescrevê-las.

---

## Não registrar arquivo completo

Não registrar o conteúdo completo do arquivo de configuração.

Registrar somente informações necessárias para diagnóstico.

---

## Não permitir caminho informado pelo usuário

A interface não deve permitir que o usuário escolha arbitrariamente outro arquivo de configuração.

Usar somente o arquivo já definido pela aplicação.

---

# Requisitos não funcionais

## RNF001 — Alteração mínima

Não refatorar a comunicação RFID inteira.

Modificar somente o necessário para:

* carregar os campos na tela;
* validar os dados;
* testar a conexão;
* salvar no arquivo;
* atualizar a configuração em memória.

---

## RNF002 — Separação de responsabilidades

Separar, conforme a arquitetura existente:

* interface;
* validação;
* persistência da configuração;
* teste de conexão RFID.

A tela não deve escrever diretamente no arquivo linha por linha se já existir camada de configuração.

---

## RNF003 — Reutilizar o reader existente

O teste deve reutilizar a abstração de conexão já existente.

Não importar e utilizar `sllurp` diretamente dentro da tela.

---

## RNF004 — Interface não bloqueante

O teste de conexão pode levar alguns segundos.

Ele não deve congelar a aplicação.

Utilizar o mecanismo de tarefas ou threads já adotado pelo projeto.

A atualização visual final deve ocorrer de forma segura na thread da interface.

---

## RNF005 — Timeout

O teste deve possuir timeout configurável ou reutilizar o timeout já definido para conexão.

Não aguardar indefinidamente.

---

## RNF006 — Compatibilidade

A implementação deve funcionar em:

* Windows;
* Linux.

Evitar manipulação de caminhos específica de um único sistema operacional.

Utilizar `pathlib`.

---

## RNF007 — Tipagem e testes

Manter:

* type hints;
* modelos pequenos;
* exceções específicas;
* testes sem hardware;
* testes de hardware separados.

---

# Fluxo principal — Carregar tela

1. O usuário acessa `Configurações RFID`.
2. A aplicação lê a configuração atual.
3. Os campos são preenchidos.
4. Nenhuma conexão adicional é iniciada.

---

# Fluxo — Testar conexão

1. O usuário altera os campos.
2. Clica em `Testar conexão`.
3. A aplicação valida os dados.
4. Verifica se existe inventário ativo.
5. Exibe `Testando conexão...`.
6. Cria uma configuração temporária.
7. Tenta conectar ao IP e à porta informados.
8. Se conectar:

   * confirma sucesso;
   * encerra a conexão temporária.
9. Se falhar:

   * informa a falha;
   * registra detalhes no log.
10. O arquivo permanece inalterado.

---

# Fluxo — Salvar configurações

1. O usuário altera os campos.
2. Clica em `Salvar configurações`.
3. A aplicação valida os dados.
4. Lê o arquivo atual.
5. Atualiza somente nome, IP e porta.
6. Salva de forma segura.
7. Atualiza a configuração em memória.
8. Exibe confirmação.
9. Não inicia conexão automaticamente.

---

# Fluxos de erro

## Dados inválidos

Exemplo:

```text
Endereço IP inválido.
```

```text
A porta deve estar entre 1 e 65535.
```

```text
Informe o nome do reader.
```

---

## Reader indisponível

Exibir:

```text
Não foi possível conectar ao reader informado.
```

---

## Timeout

Exibir:

```text
Tempo limite de conexão excedido.
```

---

## Inventário ativo

Exibir:

```text
Pare a leitura RFID antes de testar uma nova configuração.
```

---

## Erro ao salvar arquivo

Exibir:

```text
Não foi possível salvar as configurações.
```

O arquivo anterior deve continuar válido.

---

# Critérios de aceite

## CA001

A tela `Configurações RFID` deve exibir os campos:

* nome do reader;
* endereço IP;
* porta.

## CA002

Os campos devem ser preenchidos com a configuração atualmente salva.

## CA003

O usuário deve conseguir alterar os três campos.

## CA004

A tela deve possuir o botão:

```text
Testar conexão
```

## CA005

A tela deve possuir o botão:

```text
Salvar configurações
```

## CA006

O teste deve utilizar os valores atualmente digitados no formulário.

## CA007

O teste não deve salvar os valores no arquivo.

## CA008

Um teste bem-sucedido deve exibir uma confirmação visual.

## CA009

Um teste com falha deve exibir mensagem amigável sem encerrar a aplicação.

## CA010

A conexão criada para teste deve ser encerrada após o resultado.

## CA011

O teste não deve iniciar inventário RFID.

## CA012

Não deve ser permitido executar teste concorrente durante inventário ativo.

## CA013

O salvamento deve atualizar o arquivo de configuração existente.

## CA014

O salvamento deve preservar as demais configurações do arquivo.

## CA015

Valores inválidos não devem ser gravados.

## CA016

Após salvar, os campos devem permanecer preenchidos com os valores salvos.

## CA017

Ao reabrir a tela ou reiniciar a aplicação, os valores salvos devem ser carregados.

## CA018

Salvar não deve iniciar conexão automática com o reader.

## CA019

A próxima conexão normal deve utilizar os novos dados salvos.

## CA020

Uma falha de escrita não deve corromper ou apagar a configuração anterior.

## CA021

O teste não deve bloquear a interface enquanto aguarda resposta.

## CA022

A lógica existente de leitura RFID deve continuar funcionando sem alteração.

---

# Testes esperados

## Testes de validação

Adicionar testes para:

* nome válido;
* nome vazio;
* nome contendo apenas espaços;
* remoção de espaços externos;
* IP válido;
* IP inválido;
* porta válida;
* porta zero;
* porta acima de 65535;
* porta não numérica;
* porta decimal.

---

## Testes de carregamento

Validar:

* leitura dos dados existentes;
* preenchimento do formulário;
* ausência de campo;
* valor inválido no arquivo;
* aplicação de valores padrão conforme comportamento atual.

---

## Testes de salvamento

Validar:

* alteração de nome;
* alteração de IP;
* alteração de porta;
* preservação das demais chaves;
* escrita no arquivo correto;
* falha de permissão;
* falha durante substituição do arquivo;
* configuração anterior preservada em caso de erro;
* atualização da configuração em memória.

Utilizar arquivos temporários nos testes.

Não modificar o arquivo real do desenvolvedor.

---

## Testes do botão Testar conexão

Utilizar fake do reader para validar:

* conexão bem-sucedida;
* conexão recusada;
* timeout;
* encerramento após sucesso;
* encerramento após falha parcial;
* ausência de inventário;
* bloqueio quando já existe inventário ativo;
* valores do formulário utilizados no teste;
* arquivo não alterado pelo teste;
* prevenção de testes simultâneos.

---

## Testes da interface

Validar:

* campos exibidos;
* valores iniciais;
* botões exibidos;
* estado `Testando conexão...`;
* mensagem de sucesso;
* mensagem de falha;
* erros de validação;
* botão de teste temporariamente desabilitado;
* formulário mantido após salvamento.

---

## Teste com hardware

Criar ou documentar teste manual com o Zebra FX9600:

1. abrir `Configurações RFID`;
2. confirmar os valores atuais;
3. informar IP e porta corretos;
4. clicar em `Testar conexão`;
5. confirmar sucesso;
6. verificar que nenhuma leitura foi iniciada;
7. salvar;
8. reiniciar a aplicação;
9. confirmar que os valores persistiram;
10. iniciar leitura normalmente.

Marcar testes automatizados de hardware, caso existam, com:

```python
@pytest.mark.hardware
```

Não executar testes de hardware por padrão.

---

# Fora do escopo

Não implementar nesta funcionalidade:

* banco de dados;
* cadastro de vários readers;
* lista de readers;
* descoberta automática de reader na rede;
* alteração de região;
* alteração de potência;
* configuração de antenas;
* alteração de ROSpec;
* configuração de GPIO;
* atualização de firmware;
* autenticação;
* criptografia de arquivo;
* importação ou exportação de configuração;
* escolha manual do caminho do arquivo;
* conexão automática ao salvar;
* início de inventário durante o teste.

---

# Restrições de implementação

* Não colocar lógica do `sllurp` diretamente na interface.
* Não duplicar o serviço de conexão existente.
* Não criar novo arquivo de configuração sem justificativa.
* Não salvar durante o teste.
* Não interromper inventário automaticamente.
* Não apagar outras chaves do arquivo.
* Não registrar segredos.
* Não declarar sucesso antes da gravação terminar.
* Não manter socket temporário aberto.
* Não alterar configurações persistentes do Zebra FX9600.

---

# Verificações obrigatórias

Executar:

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Quando houver teste de hardware configurado, executar separadamente somente em ambiente autorizado.

Revisar o diff antes de finalizar.

---

# Relatório final esperado do Codex

Ao concluir, apresentar:

* arquivos alterados;
* campos adicionados à tela;
* formato de configuração reutilizado;
* serviço responsável pelo salvamento;
* estratégia de escrita segura;
* funcionamento do botão `Testar conexão`;
* confirmação de que o teste não salva dados;
* confirmação de que o teste não inicia inventário;
* confirmação de encerramento da conexão temporária;
* comportamento durante inventário ativo;
* testes adicionados ou atualizados;
* comandos executados;
* validação realizada com fake;
* validação realizada ou pendente no Zebra FX9600;
* limitações conhecidas.

```

Este requisito deve ser registrado como **RF008**, seguindo a sequência atual do projeto.
```
