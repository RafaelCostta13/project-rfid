# ADR-002 — Consultas ao SharePoint assíncronas e limitadas

- Status: Aceita
- Data: 2026-07-25
- Funcionalidades relacionadas: RF004, RF005 e RF006

## Contexto

Cada leitura RFID precisa consultar um fluxo do Power Automate que busca a
etiqueta no SharePoint. O Zebra FX9600 pode produzir relatórios rapidamente e
repetir a mesma etiqueta enquanto ela permanece no campo da antena.

Executar HTTP no callback do `sllurp` bloquearia o processamento do protocolo.
Criar uma thread por EPC permitiria concorrência sem limite. Além disso,
resultados atrasados de uma sessão anterior não podem alterar a sessão visual
atual.

A URL do gatilho contém uma assinatura de acesso e não pode aparecer no
código-fonte, nos logs ou nesta ADR.

## Decisão

### Camadas

A integração será separada em quatro responsabilidades:

- a camada RFID continuará produzindo somente `TagRead`;
- `TagLookupService` controlará sessões, deduplicação e fila;
- `SharePointLookupClient` será responsável pelo contrato HTTP;
- a interface consumirá apenas eventos e modelos internos de consulta.

Objetos de `urllib`, respostas HTTP e detalhes do Power Automate não serão
expostos ao domínio ou à interface.

### Processamento

Será usada uma fila FIFO com tamanho configurável e um único worker. O callback
RFID apenas verifica a sessão, publica o estado `Consultando` e tenta inserir a
tarefa na fila sem esperar.

Essa escolha mantém o processamento LLRP livre de I/O de rede, preserva a ordem
de chegada e estabelece um limite explícito de memória. O desenho permite trocar
o consumidor único por paralelismo controlado futuramente sem alterar a
interface ou o driver RFID.

Se a fila estiver cheia, a etiqueta será marcada como `Erro` e o inventário
continuará.

### Identidade e deduplicação

A chave de uma consulta será:

```text
reader_id + antenna_id + epc
```

Cada início de inventário criará um identificador incremental de sessão e
limpará o conjunto de chaves consultadas. Leituras repetidas na mesma sessão não
gerarão novas chamadas.

Consultas iniciadas antes de uma parada poderão concluir e atualizar sua própria
linha. Ao iniciar outra sessão, resultados da sessão anterior serão ignorados
por meio do identificador, mesmo que a requisição antiga finalize depois.

### Reinício do inventário RFID

Cada nova sessão manual regenerará o ROSpec no `sllurp` e usará a sessão Gen2
`S0`. O padrão `S2` da biblioteca pode preservar por mais tempo o estado
inventariado da etiqueta e impedir uma nova resposta quando o inventário é
reiniciado rapidamente com a tag ainda no campo.

`S0` e um ROSpec novo tornam explícita a fronteira entre sessões de validação:
uma etiqueta deduplicada na sessão anterior pode voltar a ser reportada e
consultada na sessão seguinte. Essa configuração pertence somente ao ROSpec
transitório e não modifica parâmetros persistentes do FX9600.

### Contrato HTTP

O cliente enviará:

```http
POST
Content-Type: application/json
```

```json
{"epc": "<EPC recebido>"}
```

Respostas somente serão aceitas quando:

- o código HTTP estiver entre 200 e 299;
- o corpo for um objeto JSON;
- `sucesso`, `mensagem` e `epc` estiverem presentes;
- `epc` for igual ao valor enviado;
- `epc` e `mensagem` forem textos.

O formato oficial do Power Automate encapsula esses campos no objeto `body`.
Para preservar clientes e testes existentes sem duplicar regras, o parser
selecionará `body` quando ele estiver presente e continuará aceitando o formato
anterior na raiz. Um `body` presente que não seja objeto será considerado erro
de contrato.

Os valores `true`, `"true"`, `"True"`, `1` e `"1"` representam sucesso.
Demais valores representam uma etiqueta não encontrada quando o restante do
contrato for válido.

Os campos complementares `cliente`, `notaFiscal`, `pedido`, `volume` e `doca`
serão normalizados pelo cliente HTTP para nomes internos em inglês. Ausência ou
valor nulo produzirá texto vazio. Strings serão preservadas sem conversão
numérica, mantendo zeros à esquerda e formatos como `1/2`; valores numéricos
recebidos serão convertidos para texto.

`mensagem` continuará obrigatória e armazenada no modelo para diagnóstico, mas
deixará de ser uma coluna visual.

### EPC técnico e Tag de apresentação

O EPC hexadecimal permanecerá inalterado em `TagRead`, `TagLookupKey`,
`TagLookupResult`, deduplicação, payload HTTP e validação da resposta. A linha
visual continuará associada pela chave interna que contém esse EPC.

No momento em que a consulta for aceita pelo serviço, uma função específica
converterá o EPC para ASCII e armazenará o resultado no campo interno `tag`.
Assim, tanto o evento `Consultando` quanto o resultado final carregarão a mesma
representação pronta, sem conversão dentro dos widgets.

A conversão será estrita e determinística:

- hexadecimal válido em maiúsculas ou minúsculas será aceito;
- apenas espaços ASCII nas extremidades serão removidos;
- caracteres de controle, hexadecimal inválido, comprimento ímpar ou resultado
  vazio produzirão `Tag inválida`;
- bytes que não podem ser decodificados como ASCII produzirão `Tag não ASCII`;
- nenhuma conversão com descarte silencioso de bytes será utilizada.

Falhar nessa projeção visual não impedirá a consulta pelo EPC original. A
interface projetará o modelo normalizado na ordem:

```text
Tag | Status | Cliente | Nota fiscal | Volume | Pedido | Doca
```

Timeout, falha de rede, erro HTTP, JSON inválido, campos ausentes e EPC
divergente serão erros técnicos. Eles produzirão uma mensagem amigável na
interface e detalhes seguros no log.

### Cliente HTTP

Será usada a biblioteca padrão `urllib.request`. O contrato é um `POST` JSON
simples e não justifica adicionar outra dependência de produção. O transporte é
injetável para permitir testes sem rede.

### Configuração e segurança

As configurações serão centralizadas em:

```dotenv
SHAREPOINT_LOOKUP_URL=
SHAREPOINT_LOOKUP_TIMEOUT_SECONDS=10
SHAREPOINT_LOOKUP_QUEUE_SIZE=100
```

A URL será obrigatória, HTTPS e armazenada somente no `.env`, que permanece
ignorado pelo Git. Logs nunca incluirão a URL completa, sua assinatura ou o
corpo integral da resposta.

## Alternativas consideradas

### Fazer HTTP diretamente no callback RFID

Rejeitada porque uma consulta lenta bloquearia o recebimento de relatórios LLRP.

### Criar uma thread para cada etiqueta

Rejeitada porque não haveria limite de concorrência ou proteção contra excesso
de leituras.

### Usar múltiplos workers imediatamente

Adiada. Um consumidor sequencial atende o escopo inicial e simplifica ordem,
testes e encerramento. O paralelismo poderá ser configurado em uma decisão
futura baseada em volume medido.

### Deduplicar apenas pelo EPC na interface

Rejeitada porque etiquetas iguais lidas por readers ou antenas diferentes
representam eventos distintos. A chave completa já está disponível no domínio.

### Aceitar o EPC retornado sem comparação

Rejeitada porque uma resposta divergente poderia atualizar a etiqueta errada.

### Exigir somente o novo envelope `body`

Rejeitada porque manter o formato anterior na raiz exige apenas uma seleção no
parser e evita uma quebra desnecessária. Não existem dois modelos ou dois fluxos
de processamento: depois dessa seleção, toda validação é compartilhada.

### Expor os nomes JSON diretamente na interface

Rejeitada para que camelCase e a estrutura do Power Automate permaneçam
restritos ao cliente HTTP. Domínio e interface usam campos internos
normalizados.

### Converter hexadecimal diretamente no widget

Rejeitada porque misturaria regra de apresentação e tratamento de erro com
Tkinter. A interface deve apenas renderizar o campo `tag` já preparado.

### Substituir o EPC interno pela Tag ASCII

Rejeitada porque quebraria deduplicação, payload HTTP, validação de resposta e
associação das linhas. Tag é somente uma projeção visual.

### Ignorar bytes ou caracteres inválidos

Rejeitada porque poderia exibir uma Tag diferente do conteúdo real. Falhas usam
mensagens explícitas e preservam integralmente o EPC técnico.

## Consequências

### Positivas

- nenhuma chamada HTTP ocorre na thread de callback do `sllurp`;
- o crescimento da fila e a quantidade de workers são limitados;
- falhas externas não interrompem inventário nem conexão RFID;
- cada etiqueta mantém seu próprio resultado;
- duplicatas não sobrecarregam o endpoint durante uma sessão;
- resultados antigos não contaminam sessões novas;
- mudanças no envelope externo ficam isoladas no cliente HTTP;
- campos adicionais permanecem associados à chave e à linha do EPC correto;
- usuários visualizam uma Tag legível sem alterar a identidade técnica;
- uma conversão visual inválida não interrompe consulta ou inventário;
- testes unitários não dependem de SharePoint, Power Automate ou hardware.

### Limitações aceitas

- as consultas são sequenciais e uma chamada lenta atrasa as tarefas seguintes;
- não há retentativa automática;
- não há cache ou histórico entre sessões;
- tarefas ainda enfileiradas de uma sessão antiga são descartadas ao serem
  consumidas;
- uma chamada HTTP em andamento só termina quando responde ou alcança o timeout;
- a sessão Gen2 `S0` foi escolhida para o inventário manual de baixa população;
  cenários futuros de alta densidade deverão reavaliar a estratégia de sessão.

## Impacto operacional

A assinatura do endpoint deve ser rotacionada sempre que houver suspeita de
exposição. O novo valor deve existir apenas no `.env` local.

Os testes automatizados usam transportes e readers falsos. A validação real
exige acesso explícito ao endpoint do Power Automate, ao SharePoint e ao Zebra
FX9600.

## Resumo consolidado desde a ADR-001

### RF004 — Consulta de etiquetas no SharePoint

- foi criado um cliente HTTP isolado para enviar `POST` JSON no formato
  `{"epc": "<EPC original>"}`;
- URL, timeout e tamanho da fila passaram a ser configurados por variáveis de
  ambiente validadas;
- consultas são executadas por um worker e uma fila limitada, sem bloquear o
  callback do LLRP;
- cada leitura recebe os estados `Consultando`, `Encontrada`, `Não encontrada`
  ou `Erro`;
- respostas HTTP, JSON e EPC divergente são validados antes de atualizar a
  interface;
- a deduplicação usa `reader_id + antenna_id + epc` e é reiniciada em cada
  sessão.

### Reinício de sessão e releitura do mesmo EPC

- o início do inventário passou a solicitar a regeneração do ROSpec;
- a sessão Gen2 usada pelo inventário manual foi alterada para `S0`;
- a deduplicação e a tabela são limpas no começo de uma nova sessão;
- resultados atrasados de sessões anteriores são ignorados;
- o mesmo EPC pode voltar a ser reportado e consultado depois de parar e iniciar
  novamente.

### RF005 — Dados adicionais

- o parser passou a aceitar o envelope `body` do Power Automate, mantendo
  compatibilidade com respostas no objeto raiz;
- `cliente`, `notaFiscal`, `pedido`, `volume` e `doca` foram normalizados no
  cliente HTTP;
- valores ausentes ou nulos são apresentados como texto vazio;
- valores numéricos são convertidos para texto e strings preservam zeros à
  esquerda;
- a tabela passou a atualizar os dados adicionais na linha associada ao EPC
  correto.

### RF006 — Tag ASCII na interface

- a coluna visual `EPC` foi substituída por `Tag`;
- a conversão hexadecimal para ASCII foi isolada em
  `services/tag_presentation.py`;
- EPC vazio, hexadecimal inválido, quantidade ímpar ou caracteres de controle
  resultam em `Tag inválida`;
- bytes que não representam ASCII resultam em `Tag não ASCII`;
- a falha de apresentação não interrompe a consulta;
- o EPC hexadecimal permanece inalterado no domínio, deduplicação, payload HTTP,
  validação da resposta e associação da linha.

### Arquivos e áreas alteradas

- configuração: `.env.example` e `src/rfid_reader/config.py`;
- integração: `src/rfid_reader/integrations/`;
- domínio e serviços:
  `src/rfid_reader/domain/tag_lookup.py`,
  `src/rfid_reader/services/tag_lookup.py` e
  `src/rfid_reader/services/tag_presentation.py`;
- RFID: regeneração de ROSpec e sessão Gen2 `S0` em
  `src/rfid_reader/readers/zebra_fx9600.py`;
- aplicação e interface:
  `src/rfid_reader/application.py`,
  `src/rfid_reader/ui/main_window.py` e
  `src/rfid_reader/ui/pages.py`;
- documentação: README, requisitos RF004 a RF006 e esta ADR;
- testes unitários de configuração, cliente HTTP, serviço de consulta, tabela,
  conversão da Tag, CLI e reader.

### Validações

Na consolidação das funcionalidades foram executados:

- `ruff check .`;
- `ruff format --check .`;
- `mypy src`;
- `pytest`, com 124 testes aprovados;
- ciclo da interface Tkinter com eventos simulados, confirmando as colunas e a
  ausência visual do EPC;
- revisão do diff e varredura para evitar o versionamento de URL assinada ou
  outros segredos.

O usuário confirmou em 2026-07-25 que a leitura de etiquetas e a consulta
inicial funcionaram com o equipamento e o endpoint reais. A regeneração do
ROSpec, os dados adicionais do RF005 e a apresentação ASCII do RF006 possuem
cobertura automatizada; uma nova validação manual conjunta dessas alterações no
FX9600 e no Power Automate permanece recomendada antes do uso operacional.
