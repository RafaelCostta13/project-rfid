# ADR-003 — Resumo da sessão derivado por EPC

- Status: Substituída pela ADR-006
- Data: 2026-07-27
- Funcionalidade relacionada: RF007

## Contexto

A página inicial precisa substituir o resumo duplicado de reader e conexões por
dois cards: EPCs encontrados e EPCs não encontrados. Os estados globais das
conexões já são apresentados no subcabeçalho persistente e devem continuar sendo
atualizados pelo monitor existente.

As consultas chegam à interface como eventos de sessão e de alteração. Uma linha
da tabela é identificada por reader, antena e EPC, enquanto os cards precisam
contar EPCs hexadecimais distintos em toda a sessão. Estados transitórios e erros
não pertencem aos totais. Além disso, uma reclassificação excepcional deve
substituir a classificação anterior, e não produzir incrementos acumulados.

O Tkinter só pode ser atualizado com segurança na thread principal. Hoje isso é
garantido pelas filas consumidas por `MainWindow`.

## Decisão

Será mantido um `TagLookupSessionSummary` independente do Tkinter. Esse estado
mantém dois conjuntos exclusivos de EPCs hexadecimais, um para cada classificação
final contabilizada:

- `Encontrada` compõe o total de encontrados;
- `Não encontrado` compõe o total de não encontrados;
- `Consultando`, `Erro` e os demais estados não compõem nenhum conjunto.

Ao receber uma atualização, o EPC é removido dos dois conjuntos antes de sua
classificação atual ser aplicada. Assim, eventos repetidos são idempotentes,
reclassificações permanecem consistentes e os totais são obtidos pelo tamanho dos
conjuntos sem percorrer toda a sessão a cada atualização visual.

A chave do resumo será somente o EPC técnico. A chave composta
`reader_id + antenna_id + epc` continuará sendo usada para consultas e linhas da
tabela, sem alteração, mas leituras do mesmo EPC por chaves compostas diferentes
representarão uma única unidade nos cards.

`MainWindow` continuará consumindo `TagLookupChanged` na thread principal. Para
cada evento da sessão ativa, ela atualizará a tabela e o resumo com o mesmo
resultado normalizado e então enviará somente os totais aos widgets. Dessa forma,
os cards não repetem a regra de classificação e não são atualizados por callbacks
de LLRP ou threads HTTP.

Tanto `TagLookupSessionStarted` quanto o evento existente `InventoryCleared`
limparão o resumo e a tabela. Uma simples parada do inventário não altera o
resumo. Eventos atrasados de outra sessão continuarão sendo descartados antes de
alcançar tabela ou cards.

A opção interna `PageId.SYSTEM_STATUS` e a classe `SystemStatusPage` serão
preservadas para evitar uma renomeação estrutural sem benefício funcional. Apenas
o texto exibido na sidebar e o título da página mudarão para `Start`.

## Alternativas consideradas

### Incrementar e decrementar os labels diretamente

Rejeitada porque re-renderizações, eventos repetidos e mudanças excepcionais de
estado exigiriam controle paralelo do valor anterior e poderiam deixar os cards
inconsistentes.

### Calcular os totais percorrendo as linhas do `Treeview`

Rejeitada porque transformaria a representação visual na fonte da regra, usaria a
Tag ASCII em vez do EPC técnico e dificultaria testes sem ambiente gráfico.

### Alterar a deduplicação do serviço de consulta para usar somente EPC

Rejeitada porque mudaria o comportamento de consulta definido na ADR-002 e iria
além do escopo visual e de resumo do RF007.

### Adicionar novos eventos específicos para cada contador

Rejeitada porque os eventos existentes já carregam a identidade técnica e o
estado normalizado necessários. Eventos adicionais duplicariam informação e
criariam outra fonte de verdade.

## Consequências

### Positivas

- a contagem é idempotente por EPC e por sessão;
- mudanças de estado substituem a classificação anterior;
- erros e consultas em andamento ficam fora dos totais;
- iniciar uma nova sessão reinicia tabela e cards em conjunto;
- parar a leitura preserva os valores;
- tabela e cards usam os mesmos resultados internos;
- a lógica pode ser testada sem endpoint, rede, reader ou display gráfico;
- o monitoramento global de RFID e internet permanece inalterado.

### Limitações aceitas

- se o mesmo EPC for consultado simultaneamente por chaves compostas diferentes,
  o último estado recebido representa sua classificação atual nos cards;
- os totais existem somente em memória e não sobrevivem ao encerramento da
  aplicação, conforme o conceito de sessão atual;
- a validação visual final ainda depende de executar a aplicação em um ambiente
  com suporte gráfico.

## Escopo preservado

Não há alteração na comunicação LLRP, no formato HTTP, na interpretação da
resposta, na conversão para Tag ASCII, na deduplicação de consultas nem na lógica
de monitoramento das conexões.
