````markdown
# Alteração do RF007 — Exibir somente EPCs encontrados na base

## Objetivo

Alterar a tela de leitura RFID para apresentar somente os itens cujo EPC tenha sido localizado com sucesso na base consultada pela API.

A partir desta alteração:

- EPCs encontrados devem aparecer na tabela;
- EPCs não encontrados devem ser desconsiderados;
- EPCs inválidos devem ser desconsiderados;
- erros técnicos não devem gerar linhas na tabela;
- deve permanecer apenas o card de EPCs encontrados;
- a coluna `Tag` deve ser removida;
- a conversão do EPC hexadecimal para Tag ASCII deve ser removida.

A alteração deve ser pontual.

Não remover ou modificar outras funcionalidades que já estejam funcionando.

---

# Contexto atual

Atualmente, a aplicação:

1. recebe o EPC hexadecimal do reader;
2. converte o EPC hexadecimal para uma Tag em formato ASCII;
3. adiciona a etiqueta na tabela;
4. consulta o EPC na API;
5. classifica o resultado como:
   - encontrado;
   - não encontrado;
   - erro;
6. exibe cards com:
   - EPCs encontrados;
   - EPCs não encontrados.

Após esta alteração, somente os resultados encontrados deverão ser apresentados ao usuário.

---

# Resultado esperado

## EPC encontrado

Quando a API retornar:

```json
{
  "body": {
    "sucesso": true,
    "epc": "484C44303130313237353835",
    "cliente": "HARLEY DAVIDSON",
    "notaFiscal": "127585",
    "pedido": "100066805",
    "volume": "1/2",
    "doca": ""
  }
}
````

o item deve:

* aparecer na tabela;
* apresentar os dados retornados pela API;
* ser contabilizado no card `EPCs encontrados`.

---

## EPC não encontrado

Quando a API retornar:

```json
{
  "body": {
    "sucesso": false,
    "epc": "484C44303130313237353835",
    "mensagem": "EPC não localizado"
  }
}
```

o item deve:

* ser desconsiderado;
* não aparecer na tabela;
* não alterar nenhum contador;
* não ser exibido como erro.

---

## EPC inválido

Quando o reader retornar um EPC considerado inválido pela validação já existente, o item deve:

* ser desconsiderado;
* não ser enviado para a tabela;
* não alterar o contador;
* não gerar uma linha com status de erro.

O tratamento técnico pode continuar sendo registrado em log.

---

## Erro técnico

Em casos como:

* timeout;
* falha de conexão;
* resposta inválida;
* JSON inválido;
* exceção inesperada;

o item não deve aparecer na tabela.

O tratamento de erro e os logs existentes devem ser preservados.

Não transformar falhas técnicas em itens encontrados.

---

# Layout esperado

## Card

Remover o card:

```text
EPCs não encontrados
```

Manter somente:

```text
EPCs encontrados
```

Exemplo:

```text
┌──────────────────────────────────┐
│ EPCs encontrados                 │
│                                  │
│                12                │
└──────────────────────────────────┘
```

---

## Tabela

Remover a coluna:

```text
Tag
```

A tabela deve manter as demais colunas atualmente existentes.

Estrutura esperada:

```text
Status | Cliente | Nota fiscal | Volume | Pedido | Doca
```

Não remover outras colunas nesta alteração.

Não adicionar uma coluna `EPC` no lugar da coluna `Tag`, salvo se ela já existir atualmente.

---

# Análise obrigatória antes da implementação

Antes de alterar o código, o Codex deve analisar o fluxo atual e identificar:

1. onde o EPC recebido pelo reader é validado;
2. onde o EPC é convertido para Tag ASCII;
3. onde a coluna `Tag` é criada e preenchida;
4. em qual momento uma linha é adicionada à tabela;
5. onde o resultado da API é interpretado;
6. onde os itens não encontrados são armazenados;
7. onde os itens com erro são armazenados;
8. como os cards são calculados;
9. como a deduplicação por EPC funciona;
10. quais testes dependem da coluna `Tag`;
11. quais módulos utilizam a função de conversão;
12. se a função de conversão possui algum uso além da apresentação visual.

A implementação somente deve começar após essa análise.

No relatório final, informar os pontos encontrados e a estratégia adotada.

---

# Requisitos funcionais

## RF001 — Remover a coluna Tag

Remover da tabela a coluna:

```text
Tag
```

Remover também:

* cabeçalho da coluna;
* preenchimento da célula;
* atributo visual utilizado apenas pela coluna;
* atualização da coluna;
* testes específicos da exibição da Tag.

Não remover o EPC hexadecimal interno.

---

## RF002 — Remover a conversão para Tag ASCII

Remover a lógica utilizada para converter um EPC hexadecimal em texto ASCII para apresentação na coluna `Tag`.

Exemplo da lógica que deixa de ser necessária:

```text
484C44303130313237353835
        ↓
HLD010127585
```

A função de conversão deve ser removida somente se não possuir outros usos necessários.

Antes de removê-la, localizar todas as referências no projeto.

---

## RF003 — Preservar o EPC interno

O EPC hexadecimal recebido pelo reader deve continuar sendo utilizado internamente para:

* identificar a leitura;
* realizar deduplicação;
* consultar a API;
* relacionar a resposta ao item consultado;
* controlar os resultados da sessão.

A remoção da coluna `Tag` não significa remover o EPC do fluxo interno.

---

## RF004 — Preservar o payload da API

A requisição deve continuar enviando o EPC no formato atualmente utilizado.

Exemplo:

```json
{
  "epc": "484C44303130313237353835"
}
```

Não alterar:

* nome do campo;
* formato do EPC;
* endpoint;
* método HTTP;
* headers;
* timeout;
* contrato da integração.

---

## RF005 — Exibir somente resultados encontrados

Uma linha somente deve permanecer visível na tabela quando a API confirmar:

```json
"sucesso": true
```

Itens com outros resultados não devem aparecer.

---

## RF006 — Não exibir EPCs não encontrados

Quando a API retornar:

```json
"sucesso": false
```

o item deve ser desconsiderado pela interface.

Ele não deve:

* aparecer na tabela;
* aparecer como `Não encontrado`;
* aparecer como `Erro`;
* incrementar contador;
* permanecer como `Consultando`.

---

## RF007 — Não exibir EPCs inválidos

EPCs considerados inválidos pela validação atual não devem ser adicionados à tabela.

Não criar uma nova regra de validação sem necessidade.

Reutilizar a validação de EPC já existente.

---

## RF008 — Não exibir erros técnicos na lista

Quando não for possível confirmar que o EPC foi encontrado, não adicionar o item à tabela.

Os erros devem continuar sendo:

* tratados internamente;
* registrados no log;
* protegidos contra encerramento inesperado da aplicação.

Não remover o tratamento de exceções existente.

---

## RF009 — Remover card de não encontrados

Remover da interface o card:

```text
EPCs não encontrados
```

Remover também:

* título;
* valor;
* variável visual;
* atualização da interface;
* testes específicos do card;
* lógica criada exclusivamente para exibir esse total.

---

## RF010 — Manter card de encontrados

Manter o card:

```text
EPCs encontrados
```

Ele deve representar a quantidade de EPCs distintos encontrados na base durante a sessão atual.

---

## RF011 — Contar somente EPCs encontrados

O contador deve incluir somente resultados com:

```json
"sucesso": true
```

Não contabilizar:

* EPC não encontrado;
* EPC inválido;
* consulta em andamento;
* timeout;
* erro HTTP;
* erro de parsing;
* resposta inválida.

---

## RF012 — Contar por EPC distinto

Um mesmo EPC encontrado deve ser contabilizado somente uma vez por sessão.

Exemplo:

```text
EPC A lido 20 vezes
API retorna sucesso = true
```

Resultado:

```text
EPCs encontrados: 1
```

---

## RF013 — Não inserir linha antes da confirmação

Preferencialmente, não adicionar uma linha à tabela antes da confirmação da API.

Fluxo recomendado:

```text
EPC recebido
    ↓
Validação interna
    ↓
Consulta à API
    ↓
Resultado encontrado?
    ├── Sim: adicionar à tabela e atualizar card
    └── Não: desconsiderar
```

Caso a arquitetura atual adicione uma linha antes da consulta, ajustar o fluxo para garantir que itens não encontrados, inválidos ou com erro nunca permaneçam visíveis.

---

## RF014 — Manter dados retornados pela API

Para os itens encontrados, continuar exibindo os campos atuais:

* Status;
* Cliente;
* Nota fiscal;
* Volume;
* Pedido;
* Doca.

Não alterar a interpretação desses campos.

---

## RF015 — Manter status dos itens encontrados

A coluna `Status` deve continuar exibindo o status já utilizado para itens encontrados.

Exemplo:

```text
Encontrada
```

Não remover a coluna `Status` nesta alteração.

---

## RF016 — Reiniciar contador em nova sessão

Ao iniciar uma nova sessão conforme o comportamento atual:

```text
EPCs encontrados: 0
```

A tabela também deve ser limpa conforme a regra já existente.

---

## RF017 — Manter resultados ao parar leitura

Ao parar a leitura:

* os itens encontrados devem permanecer na tabela;
* o total encontrado deve permanecer no card.

Somente uma nova sessão deve reiniciar esses dados, conforme o comportamento atual.

---

# Regras de negócio

## RN001 — Somente resultados confirmados

A tabela representa exclusivamente itens confirmados pela base.

---

## RN002 — Não encontrado deve ser ignorado

Um EPC não localizado é um resultado válido da consulta, mas não deve ser apresentado ao usuário.

---

## RN003 — EPC inválido deve ser ignorado

Um EPC inválido não deve fazer parte da lista de resultados.

---

## RN004 — Erro técnico não é resultado encontrado

Falhas técnicas não devem produzir linhas na tabela.

---

## RN005 — EPC continua sendo a chave interna

Mesmo sem uma coluna visual de Tag ou EPC, o EPC hexadecimal deve continuar sendo a chave interna de identificação e deduplicação.

---

## RN006 — Remoção apenas visual da Tag

A remoção da Tag não deve afetar:

* comunicação com o reader;
* consulta à API;
* deduplicação;
* relacionamento entre requisição e resposta.

---

# Requisitos não funcionais

## RNF001 — Alteração mínima

Não realizar refatoração ampla.

Alterar somente o necessário para:

* remover a coluna Tag;
* remover a conversão para ASCII;
* remover o card de não encontrados;
* filtrar a tabela para mostrar somente encontrados;
* ajustar os testes relacionados.

---

## RNF002 — Preservar funcionalidades existentes

Não alterar:

* conexão LLRP;
* início da leitura;
* parada da leitura;
* conexão com o Zebra FX9600;
* consulta ao Power Automate;
* payload da API;
* campos retornados pela API;
* tela `Configurações RFID`;
* monitoramento do reader;
* monitoramento da internet;
* navegação;
* tratamento de threads;
* mecanismo de atualização segura da interface.

---

## RNF003 — Não remover logs

Itens ignorados podem continuar sendo registrados em log para diagnóstico.

Exemplos:

```text
EPC não encontrado na base
EPC inválido ignorado
Falha ao consultar EPC
```

Não exibir esses registros como linhas da tabela.

---

## RNF004 — Fonte única de resultados

O card e a tabela devem utilizar a mesma coleção interna de EPCs encontrados.

Evitar manter listas independentes que possam gerar contagens inconsistentes.

---

# Fluxo principal

1. O reader identifica uma etiqueta.
2. A aplicação recebe o EPC hexadecimal.
3. O EPC é validado.
4. Caso seja inválido:

   * ignorar;
   * registrar no log, quando aplicável.
5. Caso seja válido:

   * consultar a API.
6. Caso a API retorne `sucesso = false`:

   * ignorar;
   * não adicionar à tabela.
7. Caso ocorra erro técnico:

   * tratar o erro;
   * não adicionar à tabela.
8. Caso a API retorne `sucesso = true`:

   * registrar o resultado interno;
   * adicionar o item à tabela;
   * atualizar o card de encontrados.
9. Caso o EPC já esteja registrado como encontrado:

   * não duplicar a linha;
   * não incrementar novamente o contador.

---

# Critérios de aceite

## CA001

A coluna `Tag` não deve mais aparecer na tabela.

## CA002

A conversão do EPC hexadecimal para Tag ASCII deve deixar de ser executada.

## CA003

O EPC hexadecimal deve continuar sendo enviado normalmente para a API.

## CA004

A tabela deve exibir somente itens retornados com:

```json
"sucesso": true
```

## CA005

Itens retornados com:

```json
"sucesso": false
```

não devem aparecer na tabela.

## CA006

EPCs inválidos não devem aparecer na tabela.

## CA007

Erros técnicos não devem criar linhas na tabela.

## CA008

O card `EPCs não encontrados` não deve mais aparecer.

## CA009

O card `EPCs encontrados` deve continuar funcionando.

## CA010

O card deve contar somente EPCs distintos encontrados.

## CA011

A leitura repetida do mesmo EPC não deve duplicar a linha nem o contador.

## CA012

As demais colunas da tabela devem continuar funcionando.

## CA013

Os dados de cliente, nota fiscal, volume, pedido e doca devem continuar sendo exibidos.

## CA014

A lógica de leitura RFID deve continuar funcionando sem regressão.

## CA015

A integração com a API não deve sofrer alteração de contrato.

## CA016

Os tratamentos e logs de erro devem continuar existindo.

## CA017

Os testes existentes não relacionados a esta alteração devem continuar passando.

---

# Testes obrigatórios

## Teste 1 — EPC encontrado

Entrada:

```json
{
  "body": {
    "sucesso": true,
    "epc": "AAA1",
    "cliente": "Cliente A"
  }
}
```

Resultado esperado:

```text
Tabela: 1 linha
EPCs encontrados: 1
```

---

## Teste 2 — EPC não encontrado

Entrada:

```json
{
  "body": {
    "sucesso": false,
    "epc": "BBB2"
  }
}
```

Resultado esperado:

```text
Tabela: nenhuma nova linha
EPCs encontrados: 0
```

---

## Teste 3 — EPC inválido

Entrada:

```text
EPC inválido conforme a validação atual
```

Resultado esperado:

```text
API não consultada, caso esse seja o comportamento atual
Tabela: nenhuma nova linha
EPCs encontrados: 0
```

Não criar uma nova definição de EPC válido apenas para satisfazer o teste.

---

## Teste 4 — Erro técnico

Simular:

```text
Timeout na API
```

Resultado esperado:

```text
Tabela: nenhuma nova linha
EPCs encontrados: 0
Erro registrado ou tratado internamente
```

---

## Teste 5 — Resultados mistos

Entrada:

```text
EPC A -> encontrado
EPC B -> não encontrado
EPC C -> inválido
EPC D -> erro técnico
EPC E -> encontrado
```

Resultado esperado:

```text
Tabela:
- EPC A
- EPC E

EPCs encontrados: 2
```

A identificação interna por EPC pode ser validada no teste mesmo sem uma coluna visual de EPC ou Tag.

---

## Teste 6 — EPC encontrado repetido

Entrada:

```text
EPC A -> encontrado
EPC A -> encontrado
EPC A -> encontrado
```

Resultado esperado:

```text
Tabela: 1 linha
EPCs encontrados: 1
```

---

## Teste 7 — Ausência da coluna Tag

Validar que:

* o cabeçalho `Tag` não existe;
* nenhuma célula de Tag é criada;
* a conversão para ASCII não é chamada.

---

## Teste 8 — Ausência do card de não encontrados

Validar que:

* o card não é criado;
* o total de não encontrados não é renderizado;
* não existe atualização visual desse contador.

---

## Teste 9 — Payload preservado

Validar que a API continua recebendo:

```json
{
  "epc": "VALOR_HEXADECIMAL_ORIGINAL"
}
```

---

# Fora do escopo

Não implementar nesta alteração:

* nova coluna de EPC;
* novo contador;
* contador de erros;
* contador de EPCs inválidos;
* histórico de itens ignorados;
* tela de auditoria;
* exportação;
* banco de dados;
* alteração da API;
* alteração do Power Automate;
* alteração do SharePoint;
* nova validação de EPC;
* alteração da tela de configurações;
* refatoração da comunicação RFID;
* mudança nos dados retornados para itens encontrados.

---

# Processo obrigatório para o Codex

## Etapa 1 — Analisar

Inspecionar:

* modelo de leitura;
* callback do reader;
* validação de EPC;
* conversão hexadecimal para ASCII;
* serviço de consulta;
* controlador da sessão;
* componente da tabela;
* componente dos cards;
* testes relacionados.

---

## Etapa 2 — Registrar impacto

Antes da implementação, identificar:

* arquivos que serão alterados;
* função de conversão que será removida;
* referências à coluna `Tag`;
* referências ao contador de não encontrados;
* momento atual de inserção na tabela;
* dependências que precisam ser preservadas.

---

## Etapa 3 — Implementar alteração mínima

Realizar somente as mudanças previstas neste documento.

Não remover funcionalidades adicionais por considerar que deixaram de ser necessárias.

---

## Etapa 4 — Testar

Executar:

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Executar também testes específicos relacionados a:

```text
found
not_found
invalid_epc
tag_conversion
summary_card
```

Adaptar os nomes à estrutura real do projeto.

---

## Etapa 5 — Revisar o diff

Confirmar que:

* somente encontrados aparecem;
* não encontrados são ignorados;
* inválidos são ignorados;
* erros não aparecem na tabela;
* coluna Tag foi removida;
* conversão visual foi removida;
* card de não encontrados foi removido;
* card de encontrados permanece funcionando;
* EPC hexadecimal continua sendo enviado à API;
* demais funcionalidades permanecem intactas.

---

# Relatório final esperado

Ao concluir, informar:

* análise realizada antes da alteração;
* arquivos analisados;
* arquivos alterados;
* referências da coluna `Tag` removidas;
* função de conversão removida;
* confirmação de que o EPC hexadecimal interno foi preservado;
* estratégia usada para exibir somente itens encontrados;
* tratamento aplicado para não encontrados;
* tratamento aplicado para EPCs inválidos;
* tratamento aplicado para erros técnicos;
* card removido;
* card preservado;
* testes adicionados ou atualizados;
* comandos executados;
* resultado dos testes;
* validações manuais pendentes.

```

Esta solicitação deve ser registrada como uma **alteração do RF007**, e não como um novo requisito sequencial. O **RF008** continua sendo a funcionalidade de configuração do reader pela interface.
```
