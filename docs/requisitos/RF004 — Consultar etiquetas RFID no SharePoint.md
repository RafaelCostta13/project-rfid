# Funcionalidade 004 — Consultar etiquetas RFID no SharePoint

## Objetivo

Integrar os EPCs lidos pelo Zebra FX9600 com um fluxo do Power Automate que consulta dados no SharePoint.

Para cada etiqueta RFID lida, a aplicação deverá:

1. capturar o EPC;
2. enviar o EPC para o endpoint HTTP;
3. processar a resposta;
4. informar na interface se a etiqueta foi encontrada;
5. continuar preparada para processar várias etiquetas durante a mesma leitura.

Inicialmente, a validação manual será realizada utilizando apenas uma etiqueta.

---

## Contexto atual

A aplicação já possui:

- conexão com o Zebra FX9600 via LLRP;
- verificação do estado do reader;
- botões `Iniciar leitura` e `Parar leitura`;
- recebimento dos EPCs;
- exibição dos EPCs na interface;
- encerramento do inventário ao clicar em `Parar leitura`.

A nova funcionalidade deve ser integrada ao fluxo existente sem reimplementar a conexão ou o inventário RFID.

---

## Endpoint

O endpoint utilizado é um gatilho HTTP do Power Automate.

O endereço não deve ficar fixo no código-fonte.

Criar uma variável de ambiente:

```env
SHAREPOINT_LOOKUP_URL=https://<endpoint-power-automate>?sig=<assinatura>
````

Adicionar essa variável ao `.env.example` sem incluir uma assinatura real:

```env
SHAREPOINT_LOOKUP_URL=
```

Garantir que o arquivo `.env` real esteja ignorado pelo Git.

Não registrar a URL completa em logs, pois ela contém uma assinatura de acesso.

---

## Formato da requisição

A aplicação deve enviar uma requisição HTTP `POST`.

Cabeçalho:

```http
Content-Type: application/json
```

Corpo:

```json
{
  "epc": "484C44303430313237333134"
}
```

O valor de `epc` deve ser o EPC efetivamente recebido do reader.

---

## Formato esperado da resposta

Considerar inicialmente uma resposta JSON contendo:

```json
{
  "sucesso": true,
  "mensagem": "Etiqueta encontrada",
  "epc": "484C44303430313237333134"
}
```

Campos esperados:

* `sucesso`: indica se a etiqueta foi encontrada;
* `mensagem`: texto retornado pelo fluxo;
* `epc`: EPC relacionado à resposta.

A implementação deve tolerar `sucesso` como booleano ou como string, caso o Power Automate retorne `"true"` ou `"false"`.

Normalizar internamente os seguintes valores como verdadeiro:

```text
true
"true"
"True"
1
"1"
```

Qualquer outro valor deve ser tratado como falso, salvo erro de contrato da resposta.

---

# Comportamento esperado

## Etiqueta encontrada

Quando a API retornar `sucesso = true`, a aplicação deve apresentar na tela:

```text
EPC: 484C44303430313237333134
Status: Encontrada
Mensagem: Etiqueta encontrada
```

Utilizar uma indicação visual positiva, como texto ou marcador verde.

---

## Etiqueta não encontrada

Quando a API retornar `sucesso = false`, a aplicação deve apresentar:

```text
EPC: 484C44303430313237333134
Status: Não encontrada
Mensagem: <mensagem retornada pela API>
```

Utilizar uma indicação visual de atenção, como texto ou marcador vermelho ou laranja.

Não tratar uma etiqueta não encontrada como falha técnica da aplicação.

---

## Erro de comunicação

Quando ocorrer timeout, falha de rede, resposta HTTP inválida ou JSON inválido, apresentar:

```text
EPC: 484C44303430313237333134
Status: Erro na consulta
Mensagem: Não foi possível consultar a etiqueta.
```

O detalhe técnico deve ser registrado no log, sem exibir informações sensíveis ao usuário.

---

# Interface

Na tela onde os EPCs são exibidos, apresentar uma lista ou tabela contendo, no mínimo:

| EPC                      | Consulta       | Mensagem                   |
| ------------------------ | -------------- | -------------------------- |
| 484C44303430313237333134 | Encontrada     | Etiqueta encontrada        |
| EPC_EXEMPLO_2            | Não encontrada | Etiqueta não localizada    |
| EPC_EXEMPLO_3            | Erro           | Não foi possível consultar |

Estados possíveis para cada linha:

* `Aguardando consulta`;
* `Consultando`;
* `Encontrada`;
* `Não encontrada`;
* `Erro`.

Ao receber um novo EPC, ele deve aparecer inicialmente como:

```text
Consultando
```

Depois, a mesma linha deve ser atualizada com o resultado da API.

---

# Requisitos funcionais

## RF001 — Consultar EPC recebido

Para cada novo EPC recebido durante o inventário, a aplicação deve solicitar a consulta ao serviço do Power Automate.

---

## RF002 — Enviar JSON correto

A requisição deve utilizar o método `POST` e enviar:

```json
{
  "epc": "<EPC_LIDO>"
}
```

---

## RF003 — Exibir estado de consulta

Enquanto a resposta não for recebida, o EPC deve ser apresentado com o estado:

```text
Consultando
```

---

## RF004 — Exibir etiqueta encontrada

Quando `sucesso` for verdadeiro, o EPC deve ser marcado como:

```text
Encontrada
```

---

## RF005 — Exibir etiqueta não encontrada

Quando `sucesso` for falso, o EPC deve ser marcado como:

```text
Não encontrada
```

---

## RF006 — Exibir mensagem da API

A mensagem retornada pela API deve ser apresentada junto ao resultado, quando disponível.

---

## RF007 — Validar o EPC da resposta

Quando a API retornar o campo `epc`, a resposta deve ser associada ao EPC correspondente.

Se o EPC retornado for diferente do EPC enviado, registrar erro de inconsistência e não atualizar outra etiqueta incorretamente.

---

## RF008 — Processar várias etiquetas

A implementação deve estar preparada para receber e consultar vários EPCs durante a mesma sessão de leitura.

Uma consulta não deve sobrescrever o resultado de outra etiqueta.

Cada EPC deve possuir seu próprio estado de consulta.

---

## RF009 — Evitar consultas repetidas

Durante uma mesma sessão de leitura, o mesmo EPC deve ser consultado apenas uma vez.

Como o reader pode reportar repetidamente uma etiqueta que permanece no campo da antena, novas aparições do mesmo EPC não devem gerar novas chamadas ao endpoint.

A deduplicação desta funcionalidade deve ser feita pela chave:

```text
reader_id + antenna_id + epc
```

Caso `reader_id` ou `antenna_id` ainda não estejam disponíveis na camada visual, a consulta pode utilizar temporariamente o EPC como chave, mantendo a deduplicação fora do driver LLRP.

Ao iniciar uma nova sessão de leitura, a lista de EPCs consultados deve ser reiniciada.

---

## RF010 — Parar novas consultas

Ao clicar em `Parar leitura`:

* o inventário deve ser interrompido;
* nenhum novo EPC deve ser aceito;
* nenhuma nova consulta deve ser criada.

As consultas que já tiverem sido enviadas antes da parada podem finalizar e atualizar seus respectivos resultados.

Não permitir que um resultado antigo seja aplicado a uma nova sessão de leitura.

---

## RF011 — Limpar estado ao iniciar nova sessão

Ao clicar em `Iniciar leitura`, a aplicação deve:

* limpar a lista visual anterior, seguindo o comportamento atual;
* limpar o controle de EPCs já consultados;
* criar um identificador interno para a nova sessão de leitura.

---

## RF012 — Tratar indisponibilidade da API

Falhas de consulta não devem:

* encerrar a aplicação;
* desconectar o reader;
* interromper automaticamente o inventário;
* impedir que outras etiquetas sejam processadas.

---

# Requisitos não funcionais

## RNF001 — Separação de responsabilidades

A interface gráfica não deve executar diretamente chamadas HTTP.

Criar uma camada específica para a integração, por exemplo:

```text
Interface gráfica
       ↓
Serviço de consulta de etiquetas
       ↓
Cliente Power Automate / SharePoint
       ↓
Endpoint HTTP
```

Sugestão de componentes:

```text
src/
├── integrations/
│   └── sharepoint_client.py
├── services/
│   └── tag_lookup_service.py
└── domain/
    └── tag_lookup_result.py
```

Adaptar os nomes à estrutura existente do projeto.

---

## RNF002 — Modelo interno

Criar um modelo interno para representar o resultado da consulta, sem expor diretamente o objeto da biblioteca HTTP.

Exemplo conceitual:

```python
@dataclass(frozen=True)
class TagLookupResult:
    epc: str
    found: bool
    message: str
```

Caso seja necessário representar erro técnico separadamente, utilizar um estado ou modelo explícito em vez de tratar erro como `found=False`.

---

## RNF003 — Timeout

A chamada HTTP deve possuir timeout configurável.

Adicionar ao `.env.example`:

```env
SHAREPOINT_LOOKUP_TIMEOUT_SECONDS=10
```

O sistema não deve aguardar indefinidamente por uma resposta.

---

## RNF004 — Múltiplas consultas

Não bloquear o recebimento do protocolo LLRP enquanto a consulta HTTP estiver sendo realizada.

O callback da biblioteca RFID deve apenas encaminhar o evento para uma fila ou serviço interno.

Não executar chamadas HTTP dentro do callback do `sllurp`.

Utilizar uma fila interna com processamento controlado.

Nesta primeira versão, um único consumidor sequencial é suficiente, desde que a arquitetura permita adicionar paralelismo controlado futuramente.

---

## RNF005 — Limite de processamento

A implementação deve possuir uma fila com tamanho limitado ou outra estratégia de proteção contra crescimento ilimitado.

Caso a fila atinja o limite, registrar o ocorrido e marcar o EPC afetado como erro, sem travar a aplicação.

Não criar uma thread ilimitada para cada etiqueta.

---

## RNF006 — Configuração externa

Centralizar as seguintes configurações:

```env
SHAREPOINT_LOOKUP_URL=
SHAREPOINT_LOOKUP_TIMEOUT_SECONDS=10
SHAREPOINT_LOOKUP_QUEUE_SIZE=100
```

Validar configurações ausentes ou inválidas na inicialização.

A mensagem de erro deve citar o nome da variável inválida, sem exibir seu conteúdo sensível.

---

## RNF007 — Logs

Registrar:

* início da consulta, preferencialmente em nível `DEBUG`;
* EPC consultado;
* resultado encontrado ou não encontrado;
* código HTTP em falhas;
* timeout;
* resposta inválida;
* divergência entre EPC enviado e EPC retornado;
* fila cheia.

Não registrar:

* assinatura `sig`;
* URL completa;
* segredos;
* corpo completo da resposta quando puder conter dados sensíveis.

---

## RNF008 — Cliente HTTP

Antes de adicionar uma nova dependência, verificar as dependências já existentes no projeto.

Caso não exista cliente HTTP, utilizar uma solução compatível com a arquitetura e com Windows e Linux.

Toda dependência adicionada deve ser registrada no `pyproject.toml`.

---

# Regras de negócio

## RN001 — Uma consulta por EPC por sessão

O mesmo EPC não deve gerar múltiplas consultas dentro da mesma sessão de leitura.

---

## RN002 — Nova sessão

Ao parar e iniciar novamente a leitura, o mesmo EPC poderá ser consultado novamente.

---

## RN003 — Resultado individual

O resultado de uma etiqueta não pode alterar o estado de outra.

---

## RN004 — Resposta negativa não é erro técnico

Quando a API responder corretamente com `sucesso = false`, a situação deve ser mostrada como:

```text
Não encontrada
```

Não como erro de comunicação.

---

## RN005 — Ausência de conexão com o reader

Se o reader estiver desconectado, nenhuma leitura ou consulta deverá ser iniciada.

---

## RN006 — EPC imutável

O EPC enviado à API deve ser o mesmo EPC normalizado pela camada RFID.

Não converter o EPC para texto ASCII, decimal ou outro formato antes de enviar.

---

# Fluxo principal

1. O usuário clica em `Iniciar leitura`.
2. A aplicação inicia uma nova sessão de inventário.
3. O reader recebe uma etiqueta.
4. A camada RFID produz um evento com o EPC.
5. A aplicação verifica se o EPC já foi consultado na sessão.
6. Caso ainda não tenha sido consultado:

   * adiciona o EPC à interface;
   * define o estado como `Consultando`;
   * adiciona a consulta à fila.
7. O serviço envia o EPC ao endpoint.
8. O serviço valida a resposta.
9. A interface atualiza a linha correspondente:

   * `Encontrada`;
   * `Não encontrada`;
   * ou `Erro`.
10. O inventário continua aceitando outras etiquetas.
11. O usuário clica em `Parar leitura`.
12. Nenhuma nova etiqueta ou consulta é adicionada.

---

# Fluxos de erro

## Timeout

1. O endpoint não responde dentro do tempo configurado.
2. O EPC é marcado como `Erro`.
3. A mensagem amigável é exibida.
4. O timeout é registrado no log.
5. O inventário continua ativo.

---

## Resposta HTTP não esperada

1. O endpoint retorna um código HTTP fora da faixa de sucesso.
2. O EPC é marcado como `Erro`.
3. O código HTTP é registrado.
4. A aplicação continua processando outras etiquetas.

---

## JSON inválido

1. O endpoint retorna um conteúdo que não pode ser interpretado.
2. O EPC é marcado como `Erro`.
3. A falha de contrato é registrada.
4. A aplicação continua funcionando.

---

## Campos ausentes

Caso a resposta não contenha os campos esperados:

* não assumir que a etiqueta foi encontrada;
* marcar o resultado como erro de resposta;
* registrar quais campos obrigatórios estavam ausentes.

---

# Critérios de aceite

## CA001

Dado que uma etiqueta seja lida, quando o EPC for recebido, então a aplicação deve enviar um `POST` com o campo `epc`.

## CA002

Dado que a API retorne `sucesso = true`, então a interface deve apresentar a etiqueta como `Encontrada`.

## CA003

Dado que a API retorne `sucesso = false`, então a interface deve apresentar a etiqueta como `Não encontrada`.

## CA004

Dado que a API retorne uma mensagem, então ela deve ser exibida na linha da etiqueta correspondente.

## CA005

Dado que o mesmo EPC seja lido várias vezes durante a mesma sessão, então somente uma requisição deve ser enviada.

## CA006

Dado que vários EPCs diferentes sejam lidos, então cada um deve possuir seu próprio resultado na interface.

## CA007

Dado que uma consulta esteja em andamento, então o recebimento de novas leituras RFID não deve ser bloqueado.

## CA008

Dado que o usuário clique em `Parar leitura`, então nenhum novo EPC deve gerar consulta.

## CA009

Dado que ocorra timeout ou falha HTTP, então a etiqueta deve ser marcada como erro sem encerrar o inventário.

## CA010

Dado que uma nova sessão seja iniciada, então um EPC consultado na sessão anterior poderá ser consultado novamente.

## CA011

Dado que a aplicação seja executada, então a URL do endpoint não deve estar gravada diretamente no código-fonte.

## CA012

Dado que a API retorne um EPC diferente daquele enviado, então a aplicação não deve associar a resposta à etiqueta errada.

---

# Testes sem hardware

Criar testes unitários usando cliente HTTP fake e reader fake para validar:

* montagem correta do JSON;
* header `Content-Type`;
* resposta com `sucesso = true`;
* resposta com `sucesso = false`;
* `sucesso` como booleano;
* `sucesso` como string;
* mensagem retornada;
* timeout;
* erro HTTP;
* JSON inválido;
* campos ausentes;
* EPC divergente;
* deduplicação na mesma sessão;
* nova consulta em uma nova sessão;
* processamento de vários EPCs;
* parada da leitura;
* resultado de sessão antiga não alterando sessão nova;
* fila cheia;
* URL ausente na configuração.

Os testes unitários não devem realizar chamadas reais ao endpoint.

---

# Teste manual com hardware

1. Configurar `SHAREPOINT_LOOKUP_URL` no `.env`.
2. Iniciar a aplicação.
3. Confirmar conexão com o Zebra FX9600.
4. Clicar em `Iniciar leitura`.
5. Aproximar a etiqueta de teste.
6. Confirmar que o EPC aparece como `Consultando`.
7. Confirmar que o resultado muda para `Encontrada` ou `Não encontrada`.
8. Manter a etiqueta no campo e confirmar que não são realizadas chamadas repetidas.
9. Clicar em `Parar leitura`.
10. Confirmar que nenhuma nova consulta é criada.
11. Iniciar outra sessão e confirmar que a etiqueta pode ser consultada novamente.

Marcar testes que dependem do equipamento ou do endpoint real como integração/hardware e não executá-los por padrão.

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

---

# Restrições

Não implementar nesta funcionalidade:

* escrita em EPC;
* leitura de TID;
* alteração de potência;
* alteração de antenas;
* GPIO;
* banco de dados local;
* cache persistente;
* retentativas automáticas ilimitadas;
* processamento concorrente ilimitado;
* consulta direta ao SharePoint sem passar pelo endpoint informado;
* alteração no fluxo do Power Automate.

---

# Resultado esperado no resumo final

Informar:

* arquivos alterados;
* serviço de integração criado;
* formato da requisição;
* tratamento da resposta;
* estratégia para várias etiquetas;
* estratégia de deduplicação;
* testes adicionados;
* comandos executados;
* validações feitas com o endpoint real;
* validações feitas com o Zebra FX9600;
* limitações conhecidas.

```

**Observação de segurança:** essa URL contém uma assinatura `sig` que concede acesso ao fluxo. Como ela foi exposta diretamente, é recomendável gerar uma nova URL/assinatura no Power Automate depois dos testes e manter o novo valor apenas no `.env`, nunca no Git.
```
