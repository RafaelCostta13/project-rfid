# RF026 — Relatório de implementação e validação

- Data: 2026-10-29
- Branch: `main`
- Resultado: implementação validada em ambiente simulado; homologação física pendente.

## Implementação

O runtime encaminha `settings.antennas` integralmente ao `ZebraFX9600Reader`.
O reader valida IDs positivos, elimina duplicatas preservando a ordem e utiliza
uma única conexão LLRP e um único inventário para todas as antenas.
O parser de `RFID_ANTENNAS` foi preservado.

| Ambiente | Configuração enviada ao sllurp |
| --- | --- |
| `RFID_ANTENNAS=1` | `antennas=[1]` |
| `RFID_ANTENNAS=1,2` | `antennas=[1,2]` |
| `RFID_ANTENNAS=4,2,3,1` | `antennas=[4,2,3,1]` |

Os relatórios mantêm EPC, reader e `AntennaID` reais. Os logs de conexão e
início/parada de inventário informam a lista configurada. A rejeição da sessão
LLRP é registrada e propagada como erro, sem reduzir silenciosamente a lista.

O exemplo de configuração foi atualizado para `RFID_ANTENNAS=1,2`. Para ativar
na instalação, configurar essa variável no `.env` utilizado e reiniciar a
aplicação, com as antenas conectadas às portas correspondentes. O `.env` local
não foi modificado nesta implementação. IDs disponíveis dependem do equipamento.

## Deduplicação entre antenas

Foi identificada uma inconsistência: a chave anterior de consulta
`reader_id + antenna_id + epc` permitia dois GETs e dois POSTs para o mesmo EPC
recebido de antenas diferentes na sessão. A contagem visual por EPC não impedia
a duplicidade no Backend.

Conforme a orientação explícita do solicitante, foi preservada a chave de
origem e adicionado um conjunto de EPCs normalizados por sessão no serviço de
consulta. A reserva ocorre sob lock antes da fila e do HTTP. O mesmo EPC recebido
na antena 1 e depois na 2 gera no máximo uma consulta e um registro de passagem,
quando aplicável, além de uma única linha e contagem. A origem do primeiro
callback aceito é mantida. A decisão está registrada no ADR-017.

O bloqueio também vale durante processamento concorrente, após resposta HTTP de
erro e para Extra Box. EPC não encontrado continua sem POST. Iniciar uma nova
sessão limpa a deduplicação e permite processar novamente a etiqueta. O filtro
de prefixos continua sendo aplicado antes da reserva, em qualquer antena.

## Arquivos desta implementação

- `src/rfid_reader/runtime.py`
- `src/rfid_reader/readers/zebra_fx9600.py`
- `src/rfid_reader/services/tag_lookup.py`
- `.env.example`
- `README.md`
- `tests/unit/test_application_runtime.py`
- `tests/unit/test_zebra_fx9600.py`
- `tests/unit/test_tag_lookup_service.py`
- `tests/ui/fakes_operational.py`
- `tests/ui/test_qt_operational.py`
- `docs/adr/ADR-017-deduplicacao-de-epc-entre-antenas-na-sessao.md`
- `docs/validacao/RF026-multiplas-antenas.md`

O workspace já continha alterações dos requisitos anteriores; elas foram
preservadas. Não foi realizado commit ou merge.

## Validação automatizada

Comandos executados com os executáveis de `.venv/Scripts`:

- `ruff check .`: aprovado.
- `ruff format --check .`: aprovado, 150 arquivos.
- `mypy src`: aprovado, 50 arquivos de código.
- `python -m pytest -q`: 419 testes aprovados.
- Após complementar os testes de rejeição LLRP, logs e EPCs distintos entre
  antenas: `python -m pytest tests/unit/test_zebra_fx9600.py tests/unit/test_tag_lookup_service.py -q`:
  38 testes aprovados.
- `git diff --check`: aprovado.

Os testes cobrem encaminhamento de uma, duas e quatro antenas, preservação da
ordem e do AntennaID, conexão única, configuração inválida, rejeição sem fallback,
parada e descarte de relatórios tardios. A concorrência foi exercitada com 100
callbacks distribuídos entre duas antenas, verificando um processamento de EPC
encontrado, previamente lido, ausente e com falha no POST.

A integração simulada percorre runtime, fila, Backend simulado, Qt Bridge,
tabela e contadores em duas sessões. Verifica filtro de prefixos, EPC repetido
entre antenas, Extra Box e reinício da deduplicação. A suíte de regressão também
exercita Start/Stop, sensores, relés e timeout existentes.

## Limites e homologação física

Potência, região regulatória e configuração persistente do leitor não foram
alteradas. As demais opções LLRP e o fluxo de sensores, relés, timeout e QML
foram preservados nesta implementação.

Não houve acesso ao Zebra FX9600 com duas antenas físicas para homologação.
Validação automatizada concluída. Validação física com múltiplas antenas pendente.
Executar o procedimento da seção 25 do RF026, incluindo leitura pelas duas
portas, mesmo EPC entre antenas, Extra Box e encerramento por DI2 e timeout.

As antenas podem produzir várias leituras físicas: a garantia local é de
processamento único por EPC na sessão. Ela não garante execução exatamente uma
vez no Backend entre sessões distintas ou após reinício da aplicação.
