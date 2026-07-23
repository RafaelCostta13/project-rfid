---
name: python-quality
description: Criar, alterar ou revisar código Python deste repositório com tipagem, testes Pytest, Ruff, Mypy, configuração por ambiente e estrutura src. Usar em toda mudança Python; não usar isoladamente para decisões específicas de protocolo RFID.
---

# Python Quality

## Fluxo obrigatório

1. Inspecione o código existente.
2. Faça a menor alteração coerente.
3. Adicione ou atualize testes.
4. Execute formatação, lint, tipos e testes.
5. Revise o diff.
6. Informe verificações não executadas.

## Padrões

- Python 3.12+.
- Type hints em interfaces públicas.
- Tipos concretos e pequenos.
- `dataclass` para modelos de domínio simples.
- UTC para timestamps persistentes ou intercambiados.
- `time.monotonic()` para medir intervalos.
- `pathlib` para caminhos.
- Logging no código de aplicação.
- `print` somente na CLI.
- Exceções específicas para erros esperados.
- Não capturar `Exception` sem tratamento ou repropagação justificada.
- Não usar argumentos mutáveis como padrão.
- Evitar estado global mutável.

## Dependências

Antes de adicionar uma dependência:

- confirme que a biblioteca padrão não resolve adequadamente;
- explique o motivo;
- escolha versão compatível com o Python do projeto;
- atualize `pyproject.toml`;
- atualize documentação quando necessário;
- não adicionar duas ferramentas para a mesma função.

## Configuração

- Centralize leitura de variáveis.
- Permita injetar um mapping nos testes.
- Mensagens de erro devem citar a variável inválida.
- Não acessar variáveis de ambiente em módulos de domínio.
- Não carregar `.env` implicitamente em bibliotecas; faça isso no ponto de entrada.

## Testes

- Teste comportamento, não detalhes internos desnecessários.
- Não use rede em testes unitários.
- Não dependa de ordem entre testes.
- Use fakes simples antes de mocks complexos.
- Cubra caminhos de erro relevantes.
- Testes de hardware devem ter marcador próprio.

## Comandos

Execute:

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Quando alterar formatação, pode executar:

```bash
ruff format .
```

Nunca afirme que os checks passaram sem executá-los.

## Revisão final

Verifique:

- código morto;
- imports desnecessários;
- mensagens de erro;
- vazamento de segredos;
- comportamento em encerramento;
- compatibilidade com Windows e Linux;
- documentação desatualizada;
- testes frágeis.
