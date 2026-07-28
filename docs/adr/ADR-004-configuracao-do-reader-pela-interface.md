# ADR-004 — Configuração do reader pela interface

- Status: Aceita
- Data: 2026-07-27
- Funcionalidade relacionada: RF008

## Contexto

A aplicação carregava nome, host e porta do Zebra FX9600 a partir de variáveis
do `.env` antes de construir uma única sessão LLRP compartilhada pelo monitor de
conexão e pelo inventário. A página `Configurações RFID` era apenas um espaço
reservado.

O RF008 exige editar, testar e salvar esses três valores sem criar outra fonte de
configuração, bloquear o Tkinter, iniciar inventário, interromper uma leitura
ativa ou reconectar automaticamente o reader compartilhado. O `.env` também pode
conter a URL assinada do Power Automate e outras chaves que não podem ser
exibidas, registradas ou regravadas incorretamente.

## Decisão

### Modelo e validação

`ReaderConnectionSettings` representará somente nome, host e porta. Uma função
central em `config.py` será usada tanto pelo carregamento inicial quanto pelas
ações do formulário.

O nome será normalizado com remoção de espaços externos e não poderá ser vazio,
conter quebras de linha ou uma expressão de interpolação `${...}` do formato
dotenv. A porta deverá ser um inteiro entre 1 e 65535.

O projeto já aceitava hostnames, inclusive em testes e configurações existentes.
Por isso, a validação continuará aceitando IPv4 ou hostname; sequências numéricas
com pontos que não sejam um IPv4 válido serão rejeitadas. IPv6 permanece fora do
escopo. Os valores padrão passam a ser:

```dotenv
RFID_READER_HOST=192.168.0.214
RFID_READER_PORT=5084
RFID_READER_NAME=fx9600-01
```

### Persistência

O caminho do `.env` encontrado no ponto de entrada será passado internamente à
aplicação. A interface não poderá escolher outro caminho.

`DotEnvReaderConfigurationStore` alterará exclusivamente
`RFID_READER_NAME`, `RFID_READER_HOST` e `RFID_READER_PORT`. Linhas de comentário
e chaves não relacionadas serão preservadas sem carregar seu conteúdo na
interface ou nos logs.

A nova versão será escrita em arquivo temporário no mesmo diretório, sincronizada
e aplicada com `os.replace`. Se leitura, escrita ou substituição falhar, o arquivo
original permanecerá como fonte válida e a tela exibirá uma mensagem amigável.

### Estado em memória e próxima conexão

`Settings` continuará imutável. O serviço manterá uma nova instância em memória
depois que a persistência terminar com sucesso.

O `ZebraFX9600Reader` compartilhado manterá separadamente os dados da sessão
ativa e os dados preparados para a próxima conexão. Salvar não desconectará nem
reconectará a sessão atual. Quando uma conexão futura for iniciada pelo fluxo
normal, o reader copiará os valores preparados antes de criar o cliente
`sllurp`.

Essa estratégia permite salvar durante uma sessão ativa sem alterar o
`reader_id`, host ou porta usados por callbacks já registrados.

### Teste temporário

`ReaderConfigurationService` validará os valores digitados e impedirá o teste se
o inventário manual estiver ativo ou se outro teste já estiver em andamento.

O teste criará uma instância temporária de `ZebraFX9600Reader`, usando a mesma
abstração e o mesmo timeout da conexão normal. Ela executará somente `connect`,
verificará o estado e sempre executará `disconnect` em um bloco `finally`.
`start_inventory` não será chamado.

A operação ocorrerá em uma única thread temporária. Início e resultado serão
publicados em uma fila consumida por `MainWindow`, mantendo todas as alterações
de widgets na thread do Tkinter. O teste não acessará o store nem atualizará
`Settings`.

Uma conexão temporária não substitui a sessão compartilhada descrita na ADR-001:
ela existe apenas durante a ação explícita de teste e é encerrada antes da
mensagem final.

## Alternativas consideradas

### Reescrever todo o `.env` a partir de `Settings`

Rejeitada porque poderia remover comentários, chaves desconhecidas e valores
sensíveis que não fazem parte do formulário.

### Atualizar o `.env` diretamente nos callbacks dos botões

Rejeitada porque misturaria Tkinter, validação e persistência, além de dificultar
testes de falha sem interface gráfica.

### Testar com `socket.create_connection`

Rejeitada porque validaria apenas TCP e duplicaria a semântica de conexão. O
reader existente também aguarda a configuração transitória que confirma a
sessão LLRP pronta.

### Reconfigurar ou reconstruir imediatamente a sessão compartilhada

Rejeitada porque salvar poderia interromper inventário, alterar callbacks ativos
ou causar uma reconexão não solicitada.

### Exigir reinicialização da aplicação

Rejeitada porque preparar o mesmo objeto para a próxima conexão é uma mudança
pequena e segura, sem refatorar monitor ou inventário.

### Permitir somente IPv4

Rejeitada porque reduziria uma capacidade já aceita pela configuração atual e
quebraria instalações que usam hostname.

## Consequências

### Positivas

- formulário, carregamento inicial e salvamento compartilham a validação;
- o `.env` continua sendo a única fonte persistente;
- outras chaves e segredos permanecem fora da interface e dos logs;
- falha de substituição não apaga o arquivo anterior;
- o teste não bloqueia a interface, não salva e não inicia inventário;
- toda conexão temporária é encerrada;
- inventário ativo tem prioridade e não é interrompido;
- salvar não cria conexão nem altera a sessão LLRP atual;
- a próxima conexão normal usa os valores salvos;
- todos os fluxos podem ser exercitados com fakes e arquivos temporários.

### Limitações aceitas

- alterações externas no `.env` enquanto a aplicação está aberta não são
  monitoradas automaticamente;
- a sessão LLRP já conectada continua usando os valores anteriores até que uma
  nova conexão seja necessária;
- um teste temporário pode coexistir brevemente com a sessão de monitoramento
  quando não há inventário ativo;
- a confirmação real de compatibilidade depende de teste manual autorizado com o
  FX9600.

## Escopo preservado

Não há alteração de região, potência, antenas, ROSpec persistente, GPIO,
firmware, escrita de tags, formato HTTP ou deduplicação. A biblioteca `sllurp`
permanece restrita à camada `readers`.
