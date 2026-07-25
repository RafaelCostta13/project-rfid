# ADR-001 — Interface desktop e sessão LLRP compartilhada

- Status: Aceita
- Data: 2026-07-25
- Funcionalidades relacionadas: RF001, RF002 e RF003
- Commit da implementação: `df3c9c571725af6495d16ac9aa77f2e433e38809`
- Commit abreviado: `df3c9c5`
- Branch de entrega: `main`
- Destino do push: `origin/main`

## Contexto

O projeto precisava evoluir da validação de configuração em linha de comando
para uma aplicação desktop capaz de:

- apresentar os estados das conexões com o Zebra FX9600 e com a internet;
- fornecer uma estrutura visual para novas páginas;
- iniciar e parar manualmente um inventário RFID;
- exibir os EPCs recebidos em tempo real;
- encerrar o inventário e a conexão de forma controlada.

A comunicação com o Zebra FX9600 utiliza LLRP por meio da biblioteca `sllurp`.
As chamadas dessa biblioteca não devem chegar à interface gráfica nem aos
modelos de domínio.

## Decisão

### Interface desktop

A interface será implementada com Tkinter e iniciada pelo comando:

```bash
rfid-reader show
```

A janela possui cabeçalho, barra global de conexões, navegação lateral e área
central de conteúdo. A página **Status do sistema** concentra o inventário
manual e a lista de EPCs. A página **Configurações RFID** permanece apenas como
espaço reservado nesta etapa.

### Separação de responsabilidades

A aplicação será organizada nas seguintes camadas:

- `domain`: estados, eventos e modelo independente de leitura;
- `readers`: contrato interno do reader e integração exclusiva com `sllurp`;
- `services`: monitoramento de conexão e coordenação do inventário manual;
- `ui`: componentes Tkinter, navegação e apresentação;
- `application`: composição dos componentes e controle do ciclo de vida;
- `cli`: validação da configuração e ponto de entrada.

As threads de conexão e LLRP não atualizarão widgets diretamente. Os eventos
serão enviados por filas seguras para threads e consumidos periodicamente pela
thread principal do Tkinter.

### Sessão LLRP

A aplicação manterá uma única sessão LLRP persistente e compartilhada entre:

- o monitor do estado da conexão RFID;
- o serviço de inventário manual.

Não será aberta uma segunda conexão ao iniciar uma leitura. O inventário usará
somente a primeira antena definida em `RFID_ANTENNAS`, conforme o escopo atual.

O ROSpec usado no inventário é transitório. Ao parar a leitura ou fechar a
aplicação, o recebimento de novas tags é bloqueado, o inventário é interrompido
e somente depois a conexão é encerrada. Nenhuma configuração persistente do
FX9600 é alterada.

### Estados e erros

As conexões RFID e internet serão verificadas de maneira independente. O acesso
à internet será validado por HTTPS para não depender da disponibilidade da porta
DNS 53.

O inventário manual terá os estados:

- `Parado`;
- `Lendo`;
- `Erro`.

Não será permitido iniciar inventários simultâneos. A lista será limpa no início
de uma nova leitura, e eventos recebidos depois da parada serão descartados.

### Configuração

Os tempos de conexão e atualização serão configuráveis pelas variáveis:

```dotenv
RFID_CONNECTION_TIMEOUT_SECONDS=3.0
RFID_STATUS_CHECK_INTERVAL_SECONDS=5.0
```

O Tkinter é uma dependência do runtime do Python/sistema operacional. A
biblioteca `sllurp` é uma dependência Python de produção.

## Alternativas consideradas

### Abrir uma conexão LLRP para o status e outra para o inventário

Rejeitada porque aumentaria o risco de conflito entre sessões, duplicaria
recursos e contrariaria o requisito de reutilizar a conexão existente.

### Acessar `sllurp` diretamente pela interface

Rejeitada porque acoplaria os widgets ao protocolo, dificultaria testes sem
hardware e misturaria responsabilidades.

### Implementar uma interface web

Rejeitada porque não fazia parte das funcionalidades solicitadas e introduziria
servidor, dependências e complexidade desnecessários para a operação local.

### Atualizar widgets a partir das threads de conexão

Rejeitada porque o Tkinter exige que alterações visuais ocorram na thread
principal.

## Consequências

### Positivas

- uma única conexão representa o estado real usado pelo inventário;
- a interface permanece independente da biblioteca LLRP;
- regras de início, parada e desconexão podem ser testadas sem equipamento;
- o layout permite adicionar novas páginas sem reconstruir a janela;
- o encerramento ordenado reduz o risco de ROSpec ativo ou thread pendente;
- Windows e Linux continuam suportados.

### Limitações aceitas

- somente a primeira antena configurada é usada no inventário manual;
- não há deduplicação, filtros, RSSI, histórico ou persistência de leituras;
- a página de configurações ainda não executa alterações no reader;
- a disponibilidade do Tkinter depende da instalação do suporte Tk no sistema.

## Resultado das funcionalidades

### RF001 — Tela principal e status das conexões

- comando `rfid-reader show`;
- janela desktop com status RFID e internet;
- verificações independentes e periódicas;
- configuração de timeout e intervalo por ambiente;
- logs de mudanças de estado.

### RF002 — Layout principal

- janela maximizada mantendo os controles do sistema operacional;
- cabeçalho e barra global de conexões;
- menu lateral com destaque da página ativa;
- área central com páginas de status e configurações;
- atualização consistente dos estados em todas as áreas da interface.

### RF003 — Teste de leitura RFID

- início e parada manual do inventário;
- exibição dos EPCs em tempo real e sem formatação adicional;
- limpeza da lista em cada novo início;
- prevenção de inventários simultâneos;
- estado de erro quando não há conexão ou ela é perdida;
- bloqueio de leituras tardias;
- parada do inventário antes da desconexão.

## Validação

Foram executadas as seguintes verificações:

- `ruff check .`;
- `ruff format --check .`;
- `mypy src`;
- `pytest`, com 54 testes aprovados;
- ciclo de vida da interface com eventos simulados;
- validação de acesso à internet;
- validação operacional com o Zebra FX9600 e etiquetas reais, confirmada pelo
  usuário em 2026-07-25.

## Rastreabilidade do Git

O commit que consolida RF001, RF002 e RF003 e deve fazer parte do push é:

```text
df3c9c571725af6495d16ac9aa77f2e433e38809
feat: implement GUI status and RFID inventory
```

Esta ADR é adicionada em um commit documental posterior porque um commit não
pode conter o próprio hash: qualquer alteração no conteúdo modificaria esse
hash. Ao executar o push da branch `main`, os dois commits serão enviados para
`origin/main`.
