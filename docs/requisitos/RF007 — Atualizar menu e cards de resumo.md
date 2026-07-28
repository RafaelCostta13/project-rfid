````markdown
# RF007 - Alteração da funcionalidade 002/004 — Atualizar menu e cards de resumo

## Objetivo

Atualizar a tela principal da aplicação para:

- alterar o texto da opção `Status do sistema` para `Start`;
- remover da área principal a seção que exibe o nome do reader, o status do reader e o status da internet;
- substituir essa seção por dois cards de resumo:
  - total de EPCs encontrados na base;
  - total de EPCs não encontrados na base.

A lógica atual de leitura, consulta e classificação das etiquetas deve ser preservada.

---

# Alterações solicitadas

## 1. Sidebar

Alterar o texto da opção:

```text
Status do sistema
````

para:

```text
Start
```

Essa alteração é apenas visual.

A opção deve continuar:

* sendo a página inicial da aplicação;
* carregando o mesmo conteúdo atualmente associado ao status do sistema;
* permanecendo selecionada ao iniciar a aplicação;
* mantendo a navegação atual.

Não alterar identificadores internos, rotas, nomes de classes ou comandos, salvo quando necessário para manter consistência no código.

---

## 2. Área de resumo da tela Start

Atualmente existe uma seção contendo informações como:

* nome do reader;
* status do reader;
* status da internet.

Essa seção deve ser removida da área central da página `Start`.

No lugar, devem ser exibidos dois cards:

```text
EPCs encontrados
EPCs não encontrados
```

Cada card deve apresentar o total correspondente da sessão atual de leitura.

---

# Estrutura visual esperada

Exemplo conceitual:

```text
Start

┌──────────────────────────────┐   ┌──────────────────────────────┐
│ EPCs encontrados             │   │ EPCs não encontrados         │
│                              │   │                              │
│              15              │   │               3              │
└──────────────────────────────┘   └──────────────────────────────┘
```

Os cards devem aparecer acima da tabela de etiquetas.

A tabela existente deve permanecer abaixo dos cards.

---

# Definição dos contadores

## EPCs encontrados

O card `EPCs encontrados` deve mostrar a quantidade de EPCs distintos da sessão atual cujo resultado final seja:

```text
Encontrada
```

Equivalente ao retorno da API:

```json
"sucesso": true
```

---

## EPCs não encontrados

O card `EPCs não encontrados` deve mostrar a quantidade de EPCs distintos da sessão atual cujo resultado final seja:

```text
Não encontrada
```

Equivalente ao retorno da API:

```json
"sucesso": false
```

---

# Requisitos funcionais

## RF001 — Renomear item da sidebar

A sidebar deve exibir:

```text
Start
```

no lugar de:

```text
Status do sistema
```

---

## RF002 — Manter Start como página inicial

Ao iniciar a aplicação, a opção `Start` deve estar selecionada.

O comportamento atual da página inicial deve ser mantido.

---

## RF003 — Remover seção antiga da área central

Remover da área central da página `Start` a seção que apresenta:

* nome do reader;
* status do reader;
* status da internet.

Essa alteração não deve remover a lógica de monitoramento dessas conexões.

Caso os estados do reader e da internet continuem sendo apresentados no subcabeçalho global, eles devem permanecer funcionando normalmente.

---

## RF004 — Exibir card de encontrados

Criar um card com o título:

```text
EPCs encontrados
```

O card deve exibir o total de etiquetas encontradas na base durante a sessão atual.

---

## RF005 — Exibir card de não encontrados

Criar um card com o título:

```text
EPCs não encontrados
```

O card deve exibir o total de etiquetas não encontradas na base durante a sessão atual.

---

## RF006 — Inicializar contadores com zero

Ao abrir a aplicação, os cards devem mostrar:

```text
0
```

---

## RF007 — Atualizar contador de encontrados

Quando uma etiqueta passar do estado `Consultando` para `Encontrada`, incrementar o contador de encontrados em uma unidade.

---

## RF008 — Atualizar contador de não encontrados

Quando uma etiqueta passar do estado `Consultando` para `Não encontrada`, incrementar o contador de não encontrados em uma unidade.

---

## RF009 — Não contar erros

Etiquetas com estado:

```text
Erro
```

não devem ser incluídas em nenhum dos dois cards.

---

## RF010 — Não contar etiquetas em consulta

Etiquetas com estado:

```text
Consultando
```

não devem ser incluídas em nenhum dos dois cards.

---

## RF011 — Não duplicar contagem

O mesmo EPC não deve ser contado mais de uma vez na mesma sessão.

Mesmo que o reader leia a mesma etiqueta repetidamente, o contador deve refletir apenas a classificação final daquele EPC distinto.

---

## RF012 — Preservar contagem após atualização visual

Atualizações da tabela ou re-renderizações da interface não devem incrementar novamente os contadores.

A contagem deve ser baseada no estado interno das etiquetas, e não no número de vezes que a interface foi atualizada.

---

## RF013 — Reiniciar contadores em nova sessão

Ao iniciar uma nova sessão de leitura, seguindo o comportamento atual de limpeza da tabela, os dois contadores também devem voltar para zero.

Exemplo:

```text
EPCs encontrados: 0
EPCs não encontrados: 0
```

---

## RF014 — Manter contadores ao parar leitura

Ao clicar em `Parar leitura`, os totais atuais devem permanecer visíveis.

Eles só devem ser reiniciados quando uma nova sessão for iniciada ou quando a lógica atual de limpeza for executada.

---

## RF015 — Processar alteração de resultado com segurança

Caso um EPC já classificado tenha seu estado alterado excepcionalmente, a contagem deve continuar consistente.

Exemplo:

```text
Encontrada -> Erro
```

Nesse caso, ele não deve permanecer contado como encontrado.

A implementação preferencial deve calcular os totais a partir do conjunto de resultados da sessão ou manter controle explícito do estado anterior, evitando incrementos cegos.

---

# Regras de negócio

## RN001 — Contagem por EPC distinto

Os cards devem representar a quantidade de EPCs distintos, não a quantidade bruta de leituras recebidas do reader.

---

## RN002 — Encontrado

Um EPC é considerado encontrado somente quando seu resultado final for:

```text
Encontrada
```

---

## RN003 — Não encontrado

Um EPC é considerado não encontrado somente quando seu resultado final for:

```text
Não encontrada
```

---

## RN004 — Erros fora dos totais

Resultados de erro técnico não devem ser classificados como não encontrados.

---

## RN005 — Sessão atual

Os contadores devem representar somente a sessão atual de leitura.

Não utilizar histórico de sessões anteriores.

---

## RN006 — EPC permanece interno

A contagem deve utilizar o EPC hexadecimal interno como identificador único.

Não utilizar somente a Tag ASCII exibida na tabela como chave de contagem.

---

# Requisitos não funcionais

## RNF001 — Alteração mínima

Não alterar:

* comunicação LLRP;
* integração com Power Automate;
* formato da requisição;
* interpretação da resposta;
* deduplicação atual;
* conversão de EPC para Tag;
* lógica dos estados.

Modificar apenas o necessário para:

* renomear a opção da sidebar;
* alterar a área de resumo;
* criar e atualizar os contadores.

---

## RNF002 — Fonte única de estado

Os cards devem utilizar os mesmos resultados internos usados para preencher a tabela.

Não criar uma segunda lógica independente para determinar se uma etiqueta foi encontrada.

---

## RNF003 — Separação entre interface e regra

A interface deve apenas exibir os totais calculados pelo estado ou controlador da sessão.

Evitar espalhar regras de contagem diretamente nos componentes visuais.

---

## RNF004 — Atualização segura da interface

A atualização dos cards deve seguir o mesmo mecanismo seguro já usado para atualizar a tabela.

Não atualizar componentes gráficos diretamente a partir do callback do `sllurp` ou da thread de consulta HTTP.

---

## RNF005 — Compatibilidade

A alteração deve continuar compatível com Windows e Linux.

---

# Fluxo esperado

1. A aplicação é iniciada.
2. A sidebar apresenta `Start`.
3. A página `Start` é aberta automaticamente.
4. Os cards exibem:

```text
EPCs encontrados: 0
EPCs não encontrados: 0
```

5. O usuário inicia a leitura.
6. Uma etiqueta é lida e passa para `Consultando`.
7. Nenhum contador é alterado.
8. A API retorna `sucesso = true`.
9. A etiqueta passa para `Encontrada`.
10. O card de encontrados passa para `1`.
11. Outra etiqueta retorna `sucesso = false`.
12. O card de não encontrados passa para `1`.
13. O usuário para a leitura.
14. Os totais permanecem visíveis.
15. Ao iniciar uma nova sessão, os dois totais voltam para zero.

---

# Critérios de aceite

## CA001

A sidebar deve exibir `Start` no lugar de `Status do sistema`.

## CA002

Ao iniciar a aplicação, `Start` deve estar selecionado.

## CA003

A seção central com nome do reader, status do reader e status da internet não deve mais aparecer na página `Start`.

## CA004

A página deve exibir um card chamado `EPCs encontrados`.

## CA005

A página deve exibir um card chamado `EPCs não encontrados`.

## CA006

Os dois cards devem iniciar com valor zero.

## CA007

Quando uma etiqueta for classificada como `Encontrada`, o total de encontrados deve ser atualizado.

## CA008

Quando uma etiqueta for classificada como `Não encontrada`, o total de não encontrados deve ser atualizado.

## CA009

Etiquetas em estado `Consultando` não devem alterar os contadores.

## CA010

Etiquetas em estado `Erro` não devem alterar os contadores.

## CA011

O mesmo EPC lido repetidamente não deve ser contado mais de uma vez.

## CA012

Ao parar a leitura, os valores atuais devem permanecer visíveis.

## CA013

Ao iniciar uma nova sessão, os dois contadores devem voltar para zero.

## CA014

A tabela de etiquetas deve continuar funcionando normalmente abaixo dos cards.

## CA015

Os estados do reader e da internet devem continuar funcionando no local global em que já são apresentados, sem alteração da lógica.

---

# Testes esperados

Adicionar ou atualizar testes para validar:

* texto `Start` na sidebar;
* `Start` como página inicial;
* ausência da seção antiga na área central;
* cards iniciando em zero;
* incremento de encontrados;
* incremento de não encontrados;
* EPC em estado `Consultando`;
* EPC em estado `Erro`;
* deduplicação da contagem;
* várias etiquetas encontradas;
* várias etiquetas não encontradas;
* mistura de encontradas, não encontradas e erros;
* reinício dos totais em uma nova sessão;
* manutenção dos totais ao parar a leitura;
* alteração excepcional de status sem inconsistência nos totais;
* contagem baseada no EPC interno;
* tabela permanecendo funcional.

Os testes unitários não devem utilizar:

* endpoint real;
* conexão de rede;
* Zebra FX9600 real.

Utilizar os fakes existentes no projeto.

---

# Exemplo de teste de contagem

```python
def test_counts_found_and_not_found_epcs() -> None:
    session = ReadingSession()

    session.add_result(epc="AAA1", status="Encontrada")
    session.add_result(epc="BBB2", status="Não encontrada")
    session.add_result(epc="CCC3", status="Erro")

    assert session.found_count == 1
    assert session.not_found_count == 1
```

Adaptar ao modelo e à arquitetura já existentes.

---

# Fora do escopo

Não implementar nesta alteração:

* card de total geral;
* card de erros;
* histórico de leituras;
* persistência dos totais;
* gráficos;
* exportação;
* filtros;
* contagem por cliente;
* contagem por nota fiscal;
* mudança no subcabeçalho global;
* mudança na consulta ao SharePoint;
* mudança na conversão de EPC para Tag;
* refatoração ampla da aplicação.

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
* alteração realizada na sidebar;
* seção removida;
* cards criados;
* regra utilizada para os totais;
* confirmação de contagem por EPC distinto;
* comportamento ao iniciar e parar sessões;
* testes adicionados ou atualizados;
* comandos executados;
* validações manuais pendentes.

```
```
