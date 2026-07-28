# ADR-006 — Lista e resumo somente de EPCs encontrados

- Status: Aceita
- Data: 2026-07-27
- Funcionalidade relacionada: alteração do RF007 documentada como RF009
- Substitui: decisões de apresentação e resumo da ADR-003 e, parcialmente, das
  ADR-002 e ADR-005

## Contexto

O RF007 introduziu dois cards e uma tabela que apresentava todos os estados da
consulta. Para isso, a ADR-003 definiu dois conjuntos de EPCs no resumo da
sessão, enquanto a tabela criava uma linha já no estado `CONSULTING` e a
atualizava para `FOUND`, `NOT_FOUND` ou `ERROR`.

A apresentação também convertia o EPC hexadecimal para ASCII. Essa conversão
era executada em `TagLookupService`, armazenada em `TagLookupResult.tag` e usada
exclusivamente pela coluna visual `Tag`. Na mesma função estavam as verificações
estruturais de EPC hexadecimal: valor não vazio, comprimento par e caracteres
hexadecimais.

O RF009 altera essa regra visual: tabela e resumo devem representar somente EPCs
confirmados pela base. Não encontrados e falhas técnicas continuam relevantes
para o contrato, tratamento e logs, mas não são resultados exibidos. O EPC
hexadecimal continua necessário para deduplicação, consulta e correlação.

## Decisão

`TagLookupSessionSummary` manterá uma única coleção em memória, indexada pelo EPC
hexadecimal e contendo apenas `TagLookupResult` com estado `FOUND`. Essa coleção
será a fonte de aceitação visual e do total do card:

- `MainWindow` entrega um resultado à tabela somente quando ele é aceito pela
  coleção;
- o total exibido é o tamanho da mesma coleção;
- receber novamente um `FOUND` para o mesmo EPC substitui seus dados sem criar
  outra contagem;
- resultados `CONSULTING`, `NOT_FOUND` e `ERROR` não alteram a coleção nem os
  widgets;
- uma confirmação `FOUND` anterior não é removida por uma falha ou resposta
  negativa posterior originada por outra chave de leitura na mesma sessão.

A tabela usará somente o EPC técnico como chave de linha. A chave composta
`reader_id + antenna_id + epc` permanece inalterada no serviço de consulta, mas
resultados do mesmo EPC em antenas diferentes atualizam uma única linha visual.

O card de não encontrados, seu conjunto de estado e suas atualizações serão
removidos. O card restante receberá apenas um total inteiro. A nova sessão
continua limpando a coleção, a tabela e o card; parar a leitura continua
preservando os resultados.

A coluna e o atributo `tag` serão removidos. A conversão hexadecimal para ASCII
também será removida, pois não possui outro consumidor. As verificações
estruturais já existentes serão preservadas como `is_valid_epc`, sem decodificar
o conteúdo para ASCII. Isso evita classificar bytes hexadecimais legítimos como
inválidos apenas porque não representam texto imprimível.

`TagLookupService` aplicará essa validação antes de deduplicar ou enfileirar a
consulta. EPC inválido será ignorado com log técnico e não produzirá evento
visual nem chamada à API.

Os eventos internos de consulta, não encontrado e erro permanecerão. Assim, o
tratamento de timeout, HTTP, resposta inválida e exceções não perde informação
nem deixa de registrar diagnóstico; o filtro ocorre somente na fronteira de
estado visual.

## Alternativas consideradas

### Remover eventos de `CONSULTING`, `NOT_FOUND` e `ERROR`

Rejeitada porque ampliaria a alteração para o contrato assíncrono e reduziria a
capacidade de diagnóstico. Filtrar no controlador atende ao requisito sem
modificar o tratamento técnico.

### Inserir todas as linhas e removê-las depois da resposta

Rejeitada porque criaria conteúdo transitório que o RF009 pede para não exibir e
exigiria lógica adicional de remoção.

### Manter a conversão ASCII apenas para validar o EPC

Rejeitada porque continuaria executando uma conversão sem finalidade visual e
trataria EPCs hexadecimais binários como texto inválido. Somente as verificações
estruturais anteriores são preservadas.

### Manter a chave composta na tabela

Rejeitada porque permitiria múltiplas linhas para o mesmo EPC lido em antenas
diferentes, divergindo da contagem distinta do card.

### Alterar a deduplicação do serviço para usar somente EPC

Rejeitada porque mudaria o contrato de consultas por reader e antena definido
anteriormente. O RF009 exige unicidade na apresentação, não uma alteração no
agendamento técnico das consultas.

## Consequências

### Positivas

- tabela e card representam somente confirmações da base;
- não encontrados, consultas em andamento e erros nunca criam linhas;
- o mesmo EPC ocupa uma linha e uma contagem por sessão;
- não existe conversão ou armazenamento de Tag ASCII;
- o EPC original permanece no payload, na deduplicação e na correlação;
- falhas técnicas e resultados negativos continuam normalizados e registrados;
- o filtro pode ser testado sem display, rede ou reader físico.

### Limitações aceitas

- a tabela não oferece identificação visual por Tag ou EPC, conforme solicitado;
- a validação garante apenas a estrutura hexadecimal já utilizada, não cria
  regras novas sobre tamanho Gen2 ou conteúdo semântico;
- se consultas do mesmo EPC por chaves diferentes retornarem dados encontrados
  distintos, o último resultado `FOUND` atualiza a única linha;
- a validação automatizada não comprova a integração com o Power Automate nem o
  comportamento em um Zebra FX9600 físico.
