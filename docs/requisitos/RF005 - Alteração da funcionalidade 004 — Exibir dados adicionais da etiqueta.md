Use este prompt para atualizar a funcionalidade no Codex:

````markdown
# Alteração da funcionalidade 004 — Exibir dados adicionais da etiqueta

## Objetivo

Atualizar a integração existente com a API do Power Automate para aproveitar os novos campos retornados pela consulta da etiqueta RFID.

A lógica atual de consulta já está funcionando e deve ser preservada.

A alteração deve apenas:

- ler os novos campos retornados pela API;
- armazená-los no modelo interno;
- exibi-los na tabela da interface;
- renomear a coluna `Consulta` para `Status`.

Não alterar o fluxo atual de leitura RFID, deduplicação, envio do EPC, processamento da consulta ou controle de estados.

---

## Resposta atual da API

A API passou a retornar a seguinte estrutura:

```json
{
  "statusCode": "200",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "sucesso": true,
    "mensagem": "EPC localizado com sucesso",
    "epc": "484C44303130313237353835",
    "cliente": "HARLEY DAVIDSON",
    "notaFiscal": "127585",
    "pedido": "100066805",
    "volume": "1/2",
    "doca": ""
  }
}
````

Os dados úteis da consulta estão dentro do objeto:

```text
body
```

---

## Estrutura atual da tabela

Atualmente a tabela possui as colunas:

```text
EPC | Consulta | Mensagem
```

---

## Nova estrutura da tabela

A tabela deve passar a possuir as seguintes colunas, nesta ordem:

```text
EPC | Status | Cliente | Nota fiscal | Volume | Pedido | Doca
```

A coluna `Consulta` deve apenas ser renomeada para `Status`.

A lógica atual dos estados deve ser mantida.

Estados já existentes:

* `Consultando`;
* `Encontrada`;
* `Não encontrada`;
* `Erro`.

---

## Campos da resposta

Mapear os campos da API da seguinte forma:

| Campo da API      | Campo interno/tabela                                                 |
| ----------------- | -------------------------------------------------------------------- |
| `body.epc`        | EPC                                                                  |
| `body.sucesso`    | Status                                                               |
| `body.cliente`    | Cliente                                                              |
| `body.notaFiscal` | Nota fiscal                                                          |
| `body.volume`     | Volume                                                               |
| `body.pedido`     | Pedido                                                               |
| `body.doca`       | Doca                                                                 |
| `body.mensagem`   | manter disponível no modelo/log, sem necessidade de coluna na tabela |

A mensagem retornada pela API não precisa mais aparecer como uma coluna da tabela.

Ela deve continuar disponível internamente para:

* logs;
* mensagens de erro;
* diagnóstico;
* possível uso futuro na interface.

---

# Comportamento esperado

## Enquanto a consulta estiver em andamento

Ao receber um EPC, inserir uma linha com:

```text
EPC: <epc lido>
Status: Consultando
Cliente:
Nota fiscal:
Volume:
Pedido:
Doca:
```

Os campos ainda não retornados devem permanecer vazios.

---

## Etiqueta encontrada

Quando a resposta possuir:

```json
"sucesso": true
```

Atualizar a linha correspondente com:

```text
Status: Encontrada
Cliente: valor de body.cliente
Nota fiscal: valor de body.notaFiscal
Volume: valor de body.volume
Pedido: valor de body.pedido
Doca: valor de body.doca
```

Exemplo:

```text
484C44303130313237353835 | Encontrada | HARLEY DAVIDSON | 127585 | 1/2 | 100066805 |
```

---

## Etiqueta não encontrada

Quando a resposta possuir:

```json
"sucesso": false
```

Atualizar a linha correspondente para:

```text
Status: Não encontrada
```

Os demais campos devem permanecer vazios, salvo quando a API retornar algum deles.

Não tratar `sucesso = false` como erro técnico.

---

## Erro de consulta

Nos casos de:

* timeout;
* falha HTTP;
* JSON inválido;
* estrutura inesperada;
* ausência do objeto `body`;

manter o comportamento atual de erro:

```text
Status: Erro
```

Os demais campos devem permanecer vazios.

A falha deve continuar sendo registrada no log.

---

# Requisitos funcionais

## RF001 — Interpretar resposta encapsulada

O cliente da API deve interpretar os dados dentro de:

```text
response["body"]
```

Não assumir que `sucesso`, `epc` e os demais campos estão na raiz da resposta.

---

## RF002 — Preservar compatibilidade

Caso a implementação atual ou os testes utilizem uma resposta sem o objeto `body`, avaliar se é simples manter compatibilidade com os dois formatos:

```json
{
  "sucesso": true,
  "epc": "..."
}
```

e:

```json
{
  "body": {
    "sucesso": true,
    "epc": "..."
  }
}
```

Se essa compatibilidade puder ser mantida sem complexidade desnecessária, aceitá-la.

Caso contrário, adotar o novo contrato como formato oficial e atualizar os testes.

---

## RF003 — Atualizar o modelo interno

Atualizar o modelo de resultado da consulta para conter, no mínimo:

```python
@dataclass(frozen=True)
class TagLookupResult:
    epc: str
    found: bool
    message: str
    customer: str
    invoice_number: str
    order_number: str
    volume: str
    dock: str
```

Os nomes internos podem seguir o padrão já utilizado pelo projeto.

Não expor os nomes específicos do JSON diretamente em todas as camadas.

---

## RF004 — Renomear coluna

Alterar o título da coluna:

```text
Consulta
```

para:

```text
Status
```

Apenas o nome visual da coluna deve mudar.

A lógica atual da consulta deve permanecer igual.

---

## RF005 — Adicionar novas colunas

Adicionar à tabela:

* Cliente;
* Nota fiscal;
* Volume;
* Pedido;
* Doca.

---

## RF006 — Atualizar a linha correta

Quando a resposta chegar, atualizar somente a linha relacionada ao EPC consultado.

Não recriar toda a tabela e não alterar o resultado de outras etiquetas.

---

## RF007 — Preservar várias etiquetas

A implementação deve continuar preparada para receber várias etiquetas.

Cada linha deve manter seus próprios dados:

* EPC;
* status;
* cliente;
* nota fiscal;
* volume;
* pedido;
* doca.

---

## RF008 — Tratar campos vazios

Campos ausentes, nulos ou vazios devem ser exibidos como texto vazio.

Exemplos:

```json
"doca": ""
```

ou:

```json
"doca": null
```

devem resultar em uma célula vazia.

Não exibir os textos:

```text
None
null
undefined
```

---

## RF009 — Preservar tipos como texto

Os seguintes campos devem ser tratados como texto:

* EPC;
* nota fiscal;
* pedido;
* volume;
* doca.

Não convertê-los para número.

Isso evita perda de zeros à esquerda e preserva formatos como:

```text
1/2
```

---

# Requisitos não funcionais

## RNF001 — Alteração mínima

Não refatorar a comunicação RFID nem a lógica de consulta já existente.

Modificar somente o necessário para:

* interpretar o novo contrato;
* ampliar o modelo;
* atualizar a tabela;
* ajustar os testes.

---

## RNF002 — Separação de responsabilidades

O cliente HTTP deve continuar responsável por interpretar a resposta externa.

A interface deve receber um modelo interno já normalizado.

A interface não deve navegar diretamente por estruturas como:

```python
response["body"]["notaFiscal"]
```

---

## RNF003 — Mensagem preservada

Embora a coluna `Mensagem` seja removida da tabela, o campo `mensagem` deve continuar armazenado no resultado interno.

Não remover sua leitura ou seu uso em logs e tratamento de erros.

---

## RNF004 — Compatibilidade

Manter compatibilidade com Windows e Linux.

---

# Regras de negócio

## RN001 — Lógica de status inalterada

A lógica atual deve permanecer:

```text
sucesso = true  -> Encontrada
sucesso = false -> Não encontrada
falha técnica   -> Erro
requisição ativa -> Consultando
```

---

## RN002 — Dados pertencem ao EPC

Os dados de cliente, nota fiscal, volume, pedido e doca devem ser associados exclusivamente ao EPC retornado pela consulta.

---

## RN003 — Divergência de EPC

Manter a validação atual entre:

* EPC enviado;
* EPC retornado pela API.

Se forem diferentes, não atualizar uma linha incorreta.

---

## RN004 — Campo vazio não é erro

Um campo vazio, especialmente `doca`, não deve tornar a consulta inválida.

A etiqueta pode estar `Encontrada` mesmo que algum campo complementar esteja vazio.

---

# Critérios de aceite

## CA001

Dado que a API retorne a nova estrutura com o objeto `body`, quando a resposta for processada, então os dados devem ser extraídos corretamente.

## CA002

Dado que `body.sucesso` seja verdadeiro, então o status exibido deve ser `Encontrada`.

## CA003

Dado que `body.sucesso` seja falso, então o status exibido deve ser `Não encontrada`.

## CA004

Dado que a etiqueta seja encontrada, então a tabela deve exibir:

* cliente;
* nota fiscal;
* volume;
* pedido;
* doca.

## CA005

Dado que `doca` esteja vazio, então a célula correspondente deve permanecer vazia e o status deve continuar como `Encontrada`.

## CA006

Dado que a consulta ainda não tenha terminado, então o status deve ser `Consultando` e os campos adicionais devem permanecer vazios.

## CA007

Dado que ocorra erro técnico, então o status deve ser `Erro` e os demais campos devem permanecer vazios.

## CA008

Dado que várias etiquetas sejam lidas, então cada linha deve exibir somente os dados correspondentes ao seu EPC.

## CA009

A tabela deve possuir exatamente as seguintes colunas:

```text
EPC | Status | Cliente | Nota fiscal | Volume | Pedido | Doca
```

## CA010

A lógica atual de leitura, consulta, deduplicação e parada do inventário deve continuar funcionando sem alteração de comportamento.

---

# Testes esperados

Atualizar ou adicionar testes para:

* resposta com objeto `body`;
* extração de `cliente`;
* extração de `notaFiscal`;
* extração de `pedido`;
* extração de `volume`;
* extração de `doca`;
* `doca` vazio;
* campos nulos;
* campo ausente;
* etiqueta encontrada;
* etiqueta não encontrada;
* erro técnico;
* várias etiquetas com dados distintos;
* EPC divergente;
* estado inicial `Consultando`;
* títulos e ordem das colunas da tabela;
* manutenção da mensagem no modelo interno;
* preservação de nota fiscal e pedido como texto.

Utilizar cliente HTTP fake.

Os testes unitários não devem chamar o endpoint real.

---

# Exemplo de resultado esperado

```text
┌──────────────────────────┬───────────────┬─────────────────┬─────────────┬────────┬───────────┬──────┐
│ EPC                      │ Status        │ Cliente         │ Nota fiscal │ Volume │ Pedido    │ Doca │
├──────────────────────────┼───────────────┼─────────────────┼─────────────┼────────┼───────────┼──────┤
│ 484C44303130313237353835 │ Encontrada    │ HARLEY DAVIDSON │ 127585      │ 1/2    │ 100066805 │      │
└──────────────────────────┴───────────────┴─────────────────┴─────────────┴────────┴───────────┴──────┘
```

---

# Verificações obrigatórias

Executar:

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Revisar o diff antes de finalizar.

No resumo final, informar:

* arquivos alterados;
* modelo atualizado;
* parser da resposta atualizado;
* colunas adicionadas;
* testes adicionados ou modificados;
* comandos executados;
* qualquer validação manual pendente.

```

Essa alteração deve ser tratada como uma extensão pequena da funcionalidade atual, evitando refatorações ou mudanças na lógica que já está validada. :contentReference[oaicite:0]{index=0} :contentReference[oaicite:1]{index=1}
```
