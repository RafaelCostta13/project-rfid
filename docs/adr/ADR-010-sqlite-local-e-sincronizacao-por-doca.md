# ADR-010 — SQLite local e sincronização por Doca

- Status: Aceita
- Data: 2026-10-05
- Requisito: RF014
- Substitui: decisão operacional de consulta remota por EPC descrita em ADR-002, ADR-005 e ADR-009

## Contexto

O fluxo anterior consultava Power Automate/SharePoint para cada EPC lido. Esse
modelo colocava rede, Power Automate e SharePoint no caminho crítico da leitura
RFID e também fazia o status `Base de dados` representar a disponibilidade
remota, não a base efetivamente usada pela operação.

O RF014 separa duas responsabilidades:

- sincronização da fonte oficial usando `doca` e `modifiedSince`;
- consulta operacional local usando `epc` e a Doca configurada.

SharePoint continua sendo a fonte oficial. O SQLite local passa a ser a réplica
operacional consultada durante a leitura RFID.

## Decisão

Criar um repositório SQLite em `services/local_database.py`, usando somente
`sqlite3` da biblioteca padrão. O caminho padrão do banco é:

```text
%LOCALAPPDATA%\rfid-reader\rfid-reader.sqlite3
```

Quando `RFID_LOCAL_DATABASE_PATH` estiver configurado, esse caminho substitui o
padrão. Isso permite testes e instalações controladas sem depender do diretório
atual.

O schema local contém:

- `etiquetas`, com `sharepoint_id`, `epc`, `status`, `cliente`,
  `nota_fiscal`, `volume`, `pedido`, `doca`, `sharepoint_modified` e
  `synced_at`;
- `sync_control`, com cursor separado por Doca: `doca`, `last_sync`,
  `last_full_sync`, `last_success_at` e `initialized`;
- índice para a busca frequente por Doca e EPC.

O UPSERT usa `sharepoint_id` como identificador estável do registro de negócio
originado no SharePoint. A combinação `doca + epc` também é única para impedir
duplicidade operacional incompatível.

A sincronização HTTP fica em `integrations/sharepoint_sync_client.py` e envia
somente:

```json
{
  "doca": "D01",
  "modifiedSince": "2026-10-05T10:00:00Z"
}
```

O endpoint remoto nunca recebe EPC. A resposta é validada antes de qualquer
escrita local. `syncUntil` só é salvo em `sync_control` dentro da mesma transação
que grava todos os itens. Falha de UPSERT ou gravação provoca rollback e preserva
a base anterior.

Após validação com o fluxo real do Power Automate, o cliente também aceita uma
resposta composta por uma lista direta de itens, sem envelope `success`,
`syncUntil`, `count` e `items`. Nesse formato, a lista é tratada como `items`, o
`count` é calculado localmente e o cursor `syncUntil` é derivado do maior
`modified` retornado. O campo `notafiscal` também é aceito como equivalente a
`notaFiscal`, preservando `nota_fiscal` no schema SQLite.

Essa compatibilidade não altera o contrato de requisição: o software continua
enviando somente `doca` e `modifiedSince`, nunca EPC.

O `TagLookupService` continua assíncrono e mantém deduplicação por sessão, mas
passa a consultar `LocalTagRepository.find_by_epc(epc, dock)`. EPC inexistente,
pertencente a outra Doca ou com `status = Inativo` não gera linha na tabela nem
incrementa contador. Não existe fallback remoto por EPC.

O status `Base de dados` passa a representar o SQLite local operacional:

- arquivo abre;
- schema existe;
- Doca configurada possui carga inicial confirmada;
- consultas locais podem ser feitas.

Foi adicionado o status `Sincronização` para representar o endpoint remoto. A
falha de sincronização com uma base local válida não bloqueia a operação RFID e
não força CH3. `system_ready` continua dependendo de Internet, RFID, Comandos e
Base de dados local; `Sincronização` é monitoramento separado.

## Alternativas Consideradas

- Manter fallback `EPC -> Power Automate`: rejeitado porque recria a dependência
  removida do caminho operacional.
- Usar ORM: rejeitado porque `sqlite3` atende ao escopo e evita dependência de
  produção.
- Salvar `syncUntil` antes dos itens: rejeitado porque poderia perder registros
  depois de uma falha parcial.
- Apagar registros locais ausentes no incremental: rejeitado porque exclusões
  físicas e troca de Doca ainda não têm política de reconciliação definida.

## Consequências

A leitura RFID passa a depender da disponibilidade local do SQLite, não da rede.
Uma falha remota temporária preserva a última base válida. A primeira execução de
uma Doca sem carga inicial válida mantém `Base de dados = NOK` e impede operação.

O incremento não detecta, sozinho, exclusões físicas no SharePoint nem todos os
casos de transferência de registro entre Docas. Uma futura política de full
reconciliation por Doca deve tratar esses casos sem apagar dados
automaticamente por ausência em uma resposta incremental.

Quando o endpoint responde no formato de lista direta, a consistência do cursor
depende de todos os itens retornados possuírem `modified` em UTC e de o maior
`modified` representar com segurança o limite superior da janela retornada. O
formato envelopado com `syncUntil` explícito continua sendo preferível porque
deixa esse limite sob responsabilidade do servidor.

Testes sem hardware cobrem criação do SQLite, schema, UPSERT, rollback, cursor
por Doca, carga inicial vazia, incremental, health check sem avanço de cursor,
consulta local por EPC, EPC inexistente, EPC de outra Doca, registro inativo e a
separação entre `Base de dados` e `Sincronização`.
