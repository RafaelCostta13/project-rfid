````markdown
# Correção do RF007 — Diferenciar “não encontrado” de erro técnico

## Objetivo

Corrigir o comportamento da tabela e dos cards quando a API retorna que um EPC não foi encontrado.

Atualmente, quando a etiqueta não é localizada na API:

- a coluna `Status` da tabela está exibindo `Erro`;
- o card `EPCs não encontrados` não está sendo atualizado corretamente.

O comportamento esperado é:

```text
sucesso = true  -> Encontrada
sucesso = false -> Não encontrado
falha técnica   -> Erro
````

Antes de realizar qualquer alteração, o Codex deve analisar o fluxo atual para identificar a causa raiz.

---

# Análise obrigatória antes da implementação

Antes de modificar o código:

1. localizar o ponto em que a resposta da API é interpretada;
2. localizar onde o status interno é definido;
3. localizar onde a tabela recebe o valor da coluna `Status`;
4. localizar onde os cards são calculados;
5. verificar como o campo `sucesso` é tratado;
6. verificar se `false` está sendo interpretado como ausência de valor;
7. verificar se respostas com `sucesso = false` estão caindo em bloco de exceção;
8. verificar se existe comparação textual inconsistente;
9. verificar se a resposta está encapsulada em `body`;
10. verificar se a API retorna algum status HTTP diferente quando o EPC não existe;
11. verificar se o cliente HTTP trata respostas válidas de negócio como exceção;
12. verificar se o modelo interno possui estado específico para `Não encontrado`.

Não implementar uma correção antes de identificar e registrar a causa raiz.

---

# Possíveis causas a investigar

## Verificação incorreta por truthiness

Código semelhante a:

```python
if response_body.get("sucesso"):
    status = FOUND
else:
    status = ERROR
```

está incorreto, porque:

```python
False
```

é um valor válido para indicar que o EPC não foi encontrado.

O tratamento deve diferenciar:

* `True`;
* `False`;
* campo ausente;
* valor inválido.

---

## Campo obrigatório validado incorretamente

Evitar validações como:

```python
if not response_body.get("sucesso"):
    raise InvalidResponseError()
```

Isso transforma `False` em erro.

Preferir:

```python
if "sucesso" not in response_body:
    raise InvalidResponseError("Campo 'sucesso' ausente")
```

---

## Cliente HTTP tratando resposta de negócio como falha

Verificar se o Power Automate retorna:

* HTTP 200 com `sucesso = false`;
* HTTP 404;
* outro status HTTP.

Se retornar HTTP 200 e `sucesso = false`, isso é resultado válido de negócio.

Se retornar HTTP 404 com JSON informando que o EPC não foi encontrado, analisar o contrato atual e normalizar esse caso como `Não encontrado`, desde que seja realmente o comportamento oficial da API.

Não transformar indiscriminadamente qualquer HTTP 404 em `Não encontrado` sem analisar o corpo da resposta.

---

# Comportamento esperado

## Etiqueta encontrada

Resposta:

```json
{
  "body": {
    "sucesso": true,
    "mensagem": "EPC localizado com sucesso",
    "epc": "484C44303130313237353835"
  }
}
```

Resultado:

```text
Status da tabela: Encontrada
Card EPCs encontrados: +1
Card EPCs não encontrados: sem alteração
```

---

## Etiqueta não encontrada

Resposta:

```json
{
  "body": {
    "sucesso": false,
    "mensagem": "EPC não localizado",
    "epc": "484C44303130313237353835"
  }
}
```

Resultado:

```text
Status da tabela: Não encontrado
Card EPCs encontrados: sem alteração
Card EPCs não encontrados: +1
```

Esse resultado não deve ser classificado como erro.

---

## Erro técnico

Exemplos:

* timeout;
* conexão recusada;
* falha HTTP sem resposta válida de negócio;
* JSON inválido;
* ausência do objeto `body`;
* ausência do campo `sucesso`;
* valor inválido no campo `sucesso`;
* resposta sem EPC quando ele for obrigatório;
* exceção inesperada.

Resultado:

```text
Status da tabela: Erro
Card EPCs encontrados: sem alteração
Card EPCs não encontrados: sem alteração
```

---

# Estados internos esperados

Preferencialmente, utilizar estados internos explícitos.

Exemplo conceitual:

```python
from enum import Enum


class TagLookupStatus(Enum):
    PENDING = "Consultando"
    FOUND = "Encontrada"
    NOT_FOUND = "Não encontrado"
    ERROR = "Erro"
```

Adaptar aos nomes e padrões já existentes no projeto.

Não depender de textos livres espalhados pelo código.

---

# Requisitos funcionais da correção

## RF001 — Interpretar `sucesso = false` como resultado válido

Quando a API retornar:

```json
"sucesso": false
```

a aplicação deve interpretar que o EPC não foi localizado.

Não classificar como erro técnico.

---

## RF002 — Exibir “Não encontrado” na tabela

A coluna `Status` deve exibir exatamente:

```text
Não encontrado
```

quando a resposta válida da API indicar:

```json
"sucesso": false
```

Padronizar esse texto em toda a aplicação.

Não misturar:

```text
Não encontrada
Não encontrado
Nao encontrado
Não localizado
```

Escolher `Não encontrado` como padrão visual para esta correção.

---

## RF003 — Atualizar o card de EPCs não encontrados

Quando o estado interno do EPC for `NOT_FOUND`, incrementar ou recalcular o card:

```text
EPCs não encontrados
```

---

## RF004 — Não contar erros como não encontrados

EPCs classificados como `Erro` não devem ser somados ao card de não encontrados.

---

## RF005 — Contar por EPC distinto

O mesmo EPC deve ser contado apenas uma vez por sessão.

Exemplo:

```text
EPC A lido 15 vezes
Resultado final: Não encontrado
```

Contagem:

```text
EPCs não encontrados: 1
```

---

## RF006 — Usar a mesma fonte de estado

Tabela e cards devem utilizar o mesmo estado interno.

Não interpretar a resposta novamente dentro da interface.

Fluxo esperado:

```text
Resposta da API
    ↓
Resultado interno normalizado
    ↓
Atualização da tabela
    ↓
Recalculo dos cards
```

---

## RF007 — Preservar lógica de encontrado

A correção não deve alterar a lógica que já funciona para:

```json
"sucesso": true
```

O status deve continuar:

```text
Encontrada
```

e o card de encontrados deve continuar funcionando.

---

## RF008 — Preservar lógica de erro

Erros técnicos reais devem continuar aparecendo como:

```text
Erro
```

Não transformar qualquer falha em `Não encontrado`.

---

## RF009 — Tratar booleanos explicitamente

O campo `sucesso` deve ser tratado explicitamente.

Exemplo conceitual:

```python
value = body["sucesso"]

if value is True:
    status = TagLookupStatus.FOUND
elif value is False:
    status = TagLookupStatus.NOT_FOUND
else:
    raise InvalidLookupResponseError("Campo 'sucesso' deve ser booleano")
```

---

## RF010 — Manter compatibilidade com string, caso já exista

Se o projeto já suporta:

```json
"sucesso": "true"
```

e:

```json
"sucesso": "false"
```

manter essa compatibilidade.

Normalizar antes de definir o estado.

Exemplo:

```python
def normalize_success(value: object) -> bool:
    if value is True:
        return True

    if value is False:
        return False

    if isinstance(value, str):
        normalized = value.strip().lower()

        if normalized == "true":
            return True

        if normalized == "false":
            return False

    raise InvalidLookupResponseError("Valor inválido para o campo 'sucesso'")
```

Não aceitar outros valores sem contrato explícito.

---

# Regra de contagem recomendada

Evitar incrementos cegos como:

```python
not_found_count += 1
```

em vários pontos da aplicação.

Preferencialmente, calcular os cards a partir dos resultados únicos da sessão.

Exemplo conceitual:

```python
found_count = sum(
    1 for result in session_results.values() if result.status is TagLookupStatus.FOUND
)

not_found_count = sum(
    1 for result in session_results.values() if result.status is TagLookupStatus.NOT_FOUND
)
```

Onde `session_results` utiliza o EPC hexadecimal interno como chave.

Isso evita:

* contagem duplicada;
* inconsistência entre tabela e card;
* incremento repetido durante re-renderização;
* erro quando um status é atualizado;
* dependência da Tag ASCII como identificador.

---

# Ordem correta de atualização

Quando a resposta da API chegar:

1. identificar o EPC interno;
2. interpretar o objeto `body`;
3. validar o campo `sucesso`;
4. normalizar o resultado;
5. atualizar o estado interno do EPC;
6. atualizar os demais dados da etiqueta;
7. recalcular os totais;
8. atualizar a linha da tabela;
9. atualizar os cards.

Não atualizar os cards com base diretamente no JSON bruto.

---

# Regras de negócio

## RN001 — Não encontrado não é erro

A ausência do EPC na base é um resultado esperado da consulta.

A API respondeu corretamente, porém não localizou o registro.

---

## RN002 — Erro representa falha técnica

O status `Erro` deve ser usado somente quando não for possível determinar corretamente se o EPC existe ou não.

---

## RN003 — Status visual deriva do estado interno

A tabela não deve decidir o texto com base diretamente no valor bruto da API.

Ela deve receber um estado interno normalizado.

---

## RN004 — Contagem por sessão

Os cards representam apenas a sessão atual.

---

## RN005 — Contagem por EPC hexadecimal

A chave de unicidade continua sendo o EPC hexadecimal interno.

Não utilizar somente a Tag ASCII.

---

## RN006 — Resultado final

Etiquetas em estado:

```text
Consultando
```

não devem ser incluídas nos cards finais.

---

# Testes obrigatórios

## Teste 1 — `sucesso = false`

Entrada:

```json
{
  "body": {
    "sucesso": false,
    "mensagem": "EPC não localizado",
    "epc": "AAA1"
  }
}
```

Resultado esperado:

```text
Status da tabela: Não encontrado
EPCs encontrados: 0
EPCs não encontrados: 1
```

---

## Teste 2 — `sucesso = true`

Entrada:

```json
{
  "body": {
    "sucesso": true,
    "mensagem": "EPC localizado",
    "epc": "AAA1"
  }
}
```

Resultado esperado:

```text
Status da tabela: Encontrada
EPCs encontrados: 1
EPCs não encontrados: 0
```

---

## Teste 3 — Campo ausente

Entrada:

```json
{
  "body": {
    "mensagem": "Resposta incompleta",
    "epc": "AAA1"
  }
}
```

Resultado esperado:

```text
Status da tabela: Erro
EPCs encontrados: 0
EPCs não encontrados: 0
```

---

## Teste 4 — Valor inválido

Entrada:

```json
{
  "body": {
    "sucesso": null,
    "epc": "AAA1"
  }
}
```

Resultado esperado:

```text
Status da tabela: Erro
EPCs não encontrados: 0
```

---

## Teste 5 — Timeout

Resultado esperado:

```text
Status da tabela: Erro
EPCs não encontrados: 0
```

---

## Teste 6 — EPC repetido não encontrado

Entrada:

```text
AAA1 -> sucesso false
AAA1 -> sucesso false
AAA1 -> sucesso false
```

Resultado esperado:

```text
EPCs não encontrados: 1
```

---

## Teste 7 — Vários resultados

Entrada:

```text
AAA1 -> sucesso true
BBB2 -> sucesso false
CCC3 -> timeout
DDD4 -> sucesso false
```

Resultado esperado:

```text
AAA1 -> Encontrada
BBB2 -> Não encontrado
CCC3 -> Erro
DDD4 -> Não encontrado

EPCs encontrados: 1
EPCs não encontrados: 2
```

---

## Teste 8 — String `"false"`

Caso já suportado:

```json
{
  "body": {
    "sucesso": "false",
    "epc": "AAA1"
  }
}
```

Resultado esperado:

```text
Status da tabela: Não encontrado
EPCs não encontrados: 1
```

---

## Teste 9 — Consistência entre tabela e card

Não pode existir situação como:

```text
Tabela: Erro
Card não encontrados: 1
```

ou:

```text
Tabela: Não encontrado
Card não encontrados: 0
```

Tabela e card devem refletir o mesmo estado interno.

---

## Teste 10 — Reinício da sessão

Após resultados anteriores:

```text
EPCs encontrados: 2
EPCs não encontrados: 3
```

ao iniciar nova sessão:

```text
EPCs encontrados: 0
EPCs não encontrados: 0
```

---

# Critérios de aceite

## CA001

A causa raiz deve ser identificada antes da implementação.

## CA002

O relatório final deve descrever a causa raiz encontrada.

## CA003

Quando a API retornar `sucesso = false`, a tabela deve exibir:

```text
Não encontrado
```

## CA004

Quando a tabela exibir `Não encontrado`, o card correspondente deve incluir esse EPC.

## CA005

O mesmo EPC não deve ser contado mais de uma vez na sessão.

## CA006

Erros técnicos devem continuar exibindo:

```text
Erro
```

## CA007

Erros técnicos não devem incrementar o card de não encontrados.

## CA008

O card de encontrados deve continuar funcionando.

## CA009

Tabela e cards devem utilizar o mesmo estado interno.

## CA010

Deve existir teste automatizado que reproduza o problema atual antes da correção.

## CA011

Após a correção, o teste de regressão deve passar.

## CA012

Os testes anteriores do RF007 devem continuar passando.

---

# Fora do escopo

Não alterar:

* comunicação LLRP;
* leitura do Zebra FX9600;
* conversão de EPC para ASCII;
* consulta enviada à API;
* endpoint do Power Automate;
* estrutura das colunas;
* tela de configurações;
* lógica de início e parada da leitura;
* persistência;
* deduplicação existente;
* cards adicionais;
* banco de dados.

Não realizar refatoração ampla.

---

# Processo obrigatório para o Codex

## Etapa 1 — Inspeção

Ler:

* `AGENTS.md`;
* documento do RF007;
* serviço de consulta à API;
* parser da resposta;
* modelo de resultado;
* controlador da sessão;
* componente da tabela;
* componente dos cards;
* testes existentes.

---

## Etapa 2 — Reprodução

Criar ou identificar um teste que reproduza:

```text
sucesso = false
    ↓
status exibido como Erro
    ↓
card não atualizado
```

Confirmar que o teste falha antes da correção.

---

## Etapa 3 — Diagnóstico

Registrar a causa raiz de forma objetiva.

Exemplos possíveis:

* uso incorreto de truthiness;
* enum inconsistente;
* parser lançando exceção para `False`;
* comparação textual divergente;
* atualização dos cards antes do modelo;
* cliente HTTP classificando resposta válida como erro.

---

## Etapa 4 — Correção mínima

Corrigir somente o ponto necessário.

Não alterar módulos não relacionados sem justificativa.

---

## Etapa 5 — Testes

Executar:

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Executar também o teste específico da regressão.

Exemplo:

```bash
pytest tests -k "not_found or sucesso_false"
```

Adaptar ao nome real dos testes.

---

## Etapa 6 — Revisão

Revisar o diff e confirmar:

* `True` continua funcionando;
* `False` agora gera `Não encontrado`;
* erro técnico continua sendo `Erro`;
* card de não encontrados é atualizado;
* EPC repetido não duplica;
* nenhuma alteração indevida foi introduzida.

---

# Relatório final esperado

Ao concluir, informar:

* causa raiz;
* arquivos analisados;
* arquivos alterados;
* comportamento anterior;
* comportamento corrigido;
* como `sucesso = false` passou a ser tratado;
* estado interno utilizado;
* como tabela e cards foram sincronizados;
* estratégia de contagem por EPC distinto;
* teste de regressão criado;
* comandos executados;
* resultado dos testes;
* validações manuais pendentes.

```

Essa solicitação continua sendo uma **correção do RF007**, não um novo requisito.
```
