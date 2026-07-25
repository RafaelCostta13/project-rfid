````markdown
# Alteração da funcionalidade 004 — Ocultar EPC e exibir Tag em ASCII

## Objetivo

Alterar somente a apresentação da tabela de resultados.

Atualmente, a tabela exibe o código EPC em hexadecimal. A nova versão deve:

- remover a coluna visual `EPC`;
- manter o EPC hexadecimal internamente, sem alterar a lógica existente;
- converter o EPC hexadecimal para texto ASCII;
- exibir o resultado convertido em uma nova coluna chamada `Tag`.

A consulta à API deve continuar sendo realizada pelo EPC hexadecimal original.

Não alterar:

- leitura RFID;
- consulta ao endpoint;
- deduplicação;
- associação entre resposta e etiqueta;
- controle de sessão;
- lógica dos estados;
- armazenamento interno do EPC.

---

# Contexto atual

O reader RFID retorna o EPC no formato hexadecimal.

Exemplo:

```text
484C44303130313237353835
````

Esse valor é utilizado internamente para:

* identificar a etiqueta;
* consultar a API;
* deduplicar leituras;
* relacionar a resposta recebida;
* localizar e atualizar a linha correta;
* validar o EPC retornado pelo endpoint.

Ao converter esse hexadecimal para ASCII, o resultado esperado é:

```text
HLD010127585
```

Na interface, o usuário deve visualizar a Tag em ASCII, e não o EPC hexadecimal.

---

# Estrutura atual da tabela

```text
EPC | Status | Cliente | Nota fiscal | Volume | Pedido | Doca
```

---

# Nova estrutura da tabela

```text
Tag | Status | Cliente | Nota fiscal | Volume | Pedido | Doca
```

A coluna `EPC` deve deixar de ser exibida.

A coluna `Tag` deve ocupar seu lugar.

---

# Regra principal

O EPC hexadecimal deve continuar sendo a identificação interna da leitura.

A alteração é apenas de apresentação.

Exemplo:

```text
EPC interno: 484C44303130313237353835
Tag exibida: HLD010127585
```

A aplicação deve continuar enviando para a API:

```json
{
  "epc": "484C44303130313237353835"
}
```

Não enviar o valor ASCII no campo `epc`.

---

# Requisitos funcionais

## RF001 — Remover a coluna visual EPC

Remover da tabela a coluna intitulada:

```text
EPC
```

O EPC não deve mais aparecer visualmente para o usuário nessa tabela.

---

## RF002 — Adicionar a coluna Tag

Adicionar como primeira coluna:

```text
Tag
```

A ordem final deve ser:

```text
Tag | Status | Cliente | Nota fiscal | Volume | Pedido | Doca
```

---

## RF003 — Converter EPC hexadecimal para ASCII

Para cada leitura, converter o EPC hexadecimal para bytes e depois para texto ASCII.

Exemplo:

```text
484C44303130313237353835
```

deve resultar em:

```text
HLD010127585
```

A conversão deve ocorrer em uma função ou componente específico, sem espalhar essa lógica pela interface.

Exemplo conceitual:

```python
def epc_hex_to_ascii(epc: str) -> str: ...
```

---

## RF004 — Manter EPC internamente

O modelo interno deve continuar armazenando o EPC original em hexadecimal.

Exemplo conceitual:

```python
@dataclass(frozen=True)
class TagLookupResult:
    epc: str
    tag: str
    found: bool
    message: str
    customer: str
    invoice_number: str
    order_number: str
    volume: str
    dock: str
```

Os nomes devem seguir o padrão atual do projeto.

O campo `epc` não deve ser removido do modelo caso seja utilizado para a lógica existente.

---

## RF005 — Manter consulta pelo EPC

A chamada ao Power Automate deve continuar utilizando o EPC hexadecimal original.

Exemplo:

```json
{
  "epc": "484C44303130313237353835"
}
```

Nunca substituir esse valor pelo texto ASCII.

---

## RF006 — Manter deduplicação pelo EPC

A deduplicação deve continuar utilizando o EPC hexadecimal, juntamente com os demais campos já utilizados pela aplicação.

Não utilizar a Tag em ASCII como chave principal de deduplicação.

---

## RF007 — Atualizar a linha pelo EPC interno

A aplicação deve continuar localizando e atualizando a linha correta usando o EPC interno ou o identificador interno já existente.

A Tag exibida não deve ser utilizada como único identificador da linha.

---

## RF008 — Exibir Tag durante a consulta

Assim que a etiqueta for lida, a linha deve ser criada com a Tag já convertida.

Exemplo:

```text
Tag: HLD010127585
Status: Consultando
Cliente:
Nota fiscal:
Volume:
Pedido:
Doca:
```

---

# Tratamento da conversão

## EPC válido

Quando o EPC contiver uma sequência hexadecimal válida e representar caracteres ASCII válidos, exibir o texto convertido.

Exemplo:

```text
Hexadecimal: 484C44303130313237353835
ASCII: HLD010127585
```

---

## Letras minúsculas ou maiúsculas

A função deve aceitar EPC hexadecimal em letras maiúsculas ou minúsculas.

Exemplos equivalentes:

```text
484c44303130313237353835
484C44303130313237353835
```

---

## Quantidade ímpar de caracteres

Caso o EPC hexadecimal possua uma quantidade ímpar de caracteres:

* não interromper a aplicação;
* registrar o problema no log;
* utilizar uma representação segura na coluna Tag.

Sugestão:

```text
Tag inválida
```

Não alterar nem descartar o EPC interno.

---

## Caracteres hexadecimais inválidos

Caso o EPC contenha caracteres que não façam parte do formato hexadecimal:

* manter o EPC internamente;
* não tentar consultar utilizando um valor modificado;
* registrar o erro de conversão;
* exibir:

```text
Tag inválida
```

A lógica atual de consulta não deve ser alterada por essa falha visual.

---

## Bytes não ASCII

Se os bytes não puderem ser decodificados como ASCII:

* não encerrar a aplicação;
* registrar o erro;
* exibir uma representação segura.

Sugestão inicial:

```text
Tag não ASCII
```

Não utilizar conversão com perda silenciosa de caracteres, como ignorar bytes inválidos, sem justificativa explícita.

---

## Espaços e caracteres de controle

Caso a conversão produza:

* espaços no início ou no final;
* quebras de linha;
* tabulações;
* caracteres de controle;

não exibir esses caracteres diretamente na tabela.

Adotar uma normalização mínima de apresentação.

Sugestão:

* remover espaços apenas do início e do final;
* considerar inválida uma Tag com caracteres de controle não imprimíveis.

Não modificar o EPC original.

---

# Requisitos não funcionais

## RNF001 — Alteração mínima

Não refatorar a integração com o Power Automate nem a comunicação RFID.

Modificar somente o necessário para:

* criar a conversão hexadecimal para ASCII;
* disponibilizar a Tag no modelo de apresentação;
* trocar a coluna `EPC` por `Tag`;
* atualizar os testes.

---

## RNF002 — Separação de responsabilidades

A interface não deve realizar diretamente operações como:

```python
bytes.fromhex(epc).decode("ascii")
```

A conversão deve ficar em uma função utilitária, serviço ou modelo apropriado.

A interface deve receber o valor da Tag já preparado para apresentação.

---

## RNF003 — Conversão determinística

Para o mesmo EPC válido, a conversão deve sempre produzir o mesmo texto.

A função não deve depender de:

* sistema operacional;
* codificação padrão do ambiente;
* locale.

Utilizar explicitamente:

```text
ASCII
```

---

## RNF004 — Compatibilidade

A implementação deve permanecer compatível com Windows e Linux.

---

## RNF005 — Logs

Registrar erros de conversão contendo informação suficiente para diagnóstico.

Não registrar:

* URL completa do endpoint;
* assinatura da API;
* segredos.

O EPC pode ser registrado no contexto do erro seguindo a política atual de logs do projeto.

---

# Regras de negócio

## RN001 — EPC é o identificador técnico

O EPC hexadecimal continua sendo o identificador técnico da etiqueta dentro da aplicação.

---

## RN002 — Tag é informação de apresentação

A Tag em ASCII é apenas o valor exibido ao usuário.

Ela não substitui o EPC nas regras internas.

---

## RN003 — Consulta permanece inalterada

A API deve continuar recebendo o campo `epc` com o valor hexadecimal original.

---

## RN004 — Resposta permanece associada ao EPC

A validação entre EPC enviado e EPC retornado pela API deve continuar funcionando da mesma forma.

---

## RN005 — Falha na conversão não remove a leitura

Caso a conversão para ASCII falhe:

* a leitura deve continuar registrada internamente;
* a consulta pode continuar usando o EPC original;
* a linha deve exibir uma mensagem segura na coluna Tag;
* a aplicação não deve encerrar.

---

## RN006 — Não converter outros campos

Não aplicar conversão hexadecimal para ASCII em:

* cliente;
* nota fiscal;
* pedido;
* volume;
* doca;
* mensagem;
* resposta completa da API.

Somente o EPC lido deve gerar a Tag de apresentação.

---

# Exemplo de fluxo esperado

1. O reader recebe:

```text
484C44303130313237353835
```

2. A aplicação mantém internamente:

```text
epc = "484C44303130313237353835"
```

3. A aplicação converte para apresentação:

```text
tag = "HLD010127585"
```

4. A tabela exibe:

```text
HLD010127585 | Consultando |  |  |  |  |
```

5. A consulta envia:

```json
{
  "epc": "484C44303130313237353835"
}
```

6. Quando a resposta chegar, a mesma linha é atualizada:

```text
HLD010127585 | Encontrada | HARLEY DAVIDSON | 127585 | 1/2 | 100066805 |
```

---

# Critérios de aceite

## CA001

Dado que a tela de resultados seja exibida, então a tabela não deve possuir uma coluna chamada `EPC`.

---

## CA002

A tabela deve possuir exatamente as seguintes colunas:

```text
Tag | Status | Cliente | Nota fiscal | Volume | Pedido | Doca
```

---

## CA003

Dado o EPC:

```text
484C44303130313237353835
```

quando convertido para ASCII, então a coluna Tag deve exibir:

```text
HLD010127585
```

---

## CA004

Dado que uma etiqueta seja lida, então o EPC hexadecimal deve continuar armazenado internamente.

---

## CA005

Dado que a API seja consultada, então o valor enviado no campo `epc` deve continuar sendo o hexadecimal original.

---

## CA006

Dado que o mesmo EPC seja lido novamente na mesma sessão, então a deduplicação atual deve continuar funcionando.

---

## CA007

Dado que a resposta da API seja recebida, então a linha correta deve continuar sendo atualizada utilizando o identificador interno existente.

---

## CA008

Dado que o EPC seja inválido para conversão, então a aplicação não deve encerrar e deve exibir uma mensagem segura na coluna Tag.

---

## CA009

Dado que várias etiquetas sejam lidas, então cada uma deve apresentar sua própria Tag convertida e seus respectivos dados de consulta.

---

## CA010

A alteração não deve modificar o comportamento dos estados:

```text
Consultando
Encontrada
Não encontrada
Erro
```

---

# Testes esperados

Adicionar ou atualizar testes para:

* conversão de hexadecimal para ASCII;
* conversão usando letras hexadecimais minúsculas;
* EPC vazio;
* quantidade ímpar de caracteres;
* caractere hexadecimal inválido;
* byte não ASCII;
* caracteres de controle;
* preservação do EPC original;
* criação da linha com Tag e status `Consultando`;
* atualização da linha após resposta;
* consulta HTTP ainda utilizando EPC hexadecimal;
* deduplicação ainda utilizando EPC;
* várias etiquetas com Tags diferentes;
* títulos e ordem das colunas;
* ausência da coluna visual EPC;
* falha na conversão sem interrupção da consulta.

Exemplo mínimo obrigatório:

```python
def test_converts_epc_hex_to_ascii() -> None:
    assert epc_hex_to_ascii("484C44303130313237353835") == "HLD010127585"
```

Os testes não devem utilizar rede real nem depender do Zebra FX9600.

---

# Fora do escopo

Não implementar nesta alteração:

* mudança no formato enviado para a API;
* conversão da Tag de volta para EPC;
* gravação em etiqueta;
* alteração do EPC;
* leitura de TID;
* mudança na deduplicação;
* persistência da Tag;
* pesquisa da API pela Tag ASCII;
* alteração da resposta do Power Automate;
* refatoração ampla da tabela;
* mudança na lógica do inventário.

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
* local da função de conversão;
* alteração realizada na tabela;
* confirmação de que o EPC continua interno;
* confirmação de que a consulta continua usando o EPC hexadecimal;
* testes adicionados ou alterados;
* comandos executados;
* limitações encontradas.

```

O ponto mais importante para o Codex é: **a Tag é somente uma representação visual em ASCII; o EPC hexadecimal continua sendo a chave técnica de toda a operação.**
```
