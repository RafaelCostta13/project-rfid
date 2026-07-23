# 000 - Criar ambiente

## 1. Objetivo

Preparar o ambiente inicial de desenvolvimento do software RFID em Python para comunicação com o reader Zebra FX9600 por LLRP.

Ao concluir esta funcionalidade, o repositório deverá possuir:

- estrutura básica do projeto;
- ambiente virtual Python;
- gerenciamento de dependências;
- configurações de qualidade;
- arquivo de variáveis de ambiente de exemplo;
- aplicação CLI mínima executável;
- testes iniciais;
- documentação para instalação e execução.

Esta funcionalidade não deve implementar ainda a conexão real com o reader nem o inventário RFID.

---

## 2. Contexto

O projeto será desenvolvido com auxílio do Codex CLI.

O equipamento utilizado será o Zebra FX9600, cuja configuração de rede e parâmetros operacionais será realizada externamente. O software receberá o host, porta e demais opções por variáveis de ambiente.

A primeira etapa deve criar uma base pequena e confiável, evitando dependências ou componentes que ainda não são necessários.

---

## 3. Escopo

### Esta funcionalidade contempla

- iniciar um repositório Python organizado no padrão `src`;
- definir Python 3.12 ou superior;
- criar o pacote `rfid_reader`;
- configurar ambiente virtual;
- criar `pyproject.toml`;
- configurar dependências de desenvolvimento;
- configurar Ruff;
- configurar Mypy;
- configurar Pytest;
- criar carregamento e validação de configuração;
- criar `.env.example`;
- criar `.gitignore`;
- criar uma CLI mínima;
- criar testes unitários iniciais;
- criar README com instruções essenciais;
- validar todos os comandos locais.

### Esta funcionalidade não contempla

- conexão LLRP;
- escolha ou integração definitiva da biblioteca LLRP;
- leitura de etiquetas;
- inventário RFID;
- deduplicação;
- reconexão;
- banco de dados;
- API;
- interface gráfica;
- Docker;
- integração com sistemas externos.

---

## 4. Tecnologias

### Obrigatórias

- Python 3.12 ou superior;
- `pytest`;
- `ruff`;
- `mypy`;
- `python-dotenv`, caso seja necessário para carregar `.env`.

### Decisão sobre gerenciamento do projeto

Usar `pyproject.toml` como fonte principal de configuração.

Preferir uma configuração simples com instalação via `pip` no primeiro momento. Não introduzir Poetry, Hatch, PDM ou uv sem uma decisão explícita.

Exemplo de instalação:

```bash
python -m venv .venv
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

---

## 5. Estrutura esperada

```text
rfid-reader/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── docs/
│   └── 000 - Criar ambiente.md
├── src/
│   └── rfid_reader/
│       ├── __init__.py
│       ├── config.py
│       └── cli.py
└── tests/
    └── unit/
        ├── test_config.py
        └── test_cli.py
```

Não criar diretórios vazios para funcionalidades futuras.

---

## 6. Configuração inicial

Criar um objeto tipado de configuração que represente:

```text
reader_host
reader_port
reader_name
antennas
deduplication_window_seconds
log_level
```

Variáveis esperadas:

```dotenv
RFID_READER_HOST=192.168.0.100
RFID_READER_PORT=5084
RFID_READER_NAME=fx9600-01
RFID_ANTENNAS=1
RFID_DEDUPLICATION_WINDOW_SECONDS=2.0
RFID_LOG_LEVEL=INFO
```

### Regras de validação

- `RFID_READER_HOST` é obrigatório.
- `RFID_READER_PORT` deve ser inteiro entre 1 e 65535.
- `RFID_READER_NAME` não pode ser vazio.
- `RFID_ANTENNAS` deve aceitar lista separada por vírgulas, por exemplo `1,2,3,4`.
- Cada antena deve ser um inteiro positivo.
- Antenas duplicadas devem ser normalizadas ou rejeitadas de forma consistente.
- A janela de deduplicação deve ser maior ou igual a zero.
- O nível de log deve aceitar apenas níveis conhecidos.
- Erros devem indicar claramente qual variável está inválida.

A configuração não deve depender diretamente de `os.environ` durante todos os testes. Permitir fornecer um mapeamento explícito para facilitar testes unitários.

---

## 7. CLI mínima

Criar uma entrada executável, por exemplo:

```bash
python -m rfid_reader.cli check-config
```

Ou um script registrado em `pyproject.toml`, por exemplo:

```bash
rfid-reader check-config
```

O comando `check-config` deve:

1. carregar as variáveis;
2. validar a configuração;
3. exibir um resumo sem dados sensíveis;
4. retornar código zero em caso de sucesso;
5. retornar código diferente de zero e mensagem clara em caso de erro.

Exemplo de saída:

```text
Configuração válida
Reader: fx9600-01
Host: 192.168.0.100:5084
Antenas: 1
Log level: INFO
```

Não tentar conectar ao equipamento nesta funcionalidade.

---

## 8. `pyproject.toml`

Configurar no mesmo arquivo:

- metadados básicos do projeto;
- versão inicial;
- versão mínima do Python;
- dependências de produção;
- dependências opcionais de desenvolvimento;
- entrada da CLI;
- Ruff;
- Mypy;
- Pytest.

Configuração esperada:

- Ruff com limite de linha razoável;
- seleção de regras essenciais;
- formatter do Ruff;
- Mypy em modo suficientemente estrito para código novo;
- Pytest procurando testes em `tests`;
- marcador `hardware` declarado para uso futuro.

Não adicionar ferramentas duplicadas, como Black junto com Ruff formatter ou Flake8 junto com Ruff.

---

## 9. `.gitignore`

Deve ignorar pelo menos:

```text
.venv/
.env
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
build/
dist/
*.egg-info/
.coverage
htmlcov/
.idea/
.vscode/
```

Avaliar se `.vscode/` deve ser totalmente ignorado ou se configurações compartilhadas serão versionadas no futuro.

---

## 10. README

O README inicial deve conter:

- objetivo do projeto;
- requisitos;
- como criar e ativar o ambiente virtual no Linux;
- como criar e ativar o ambiente virtual no Windows;
- instalação das dependências;
- criação do `.env`;
- execução do `check-config`;
- comandos de qualidade;
- aviso de que a conexão real com o FX9600 ainda não faz parte desta etapa.

---

## 11. Testes obrigatórios

Criar testes para:

### Configuração válida

- valores completos;
- antena única;
- várias antenas;
- conversão correta de tipos.

### Configuração inválida

- host ausente;
- porta não numérica;
- porta fora do intervalo;
- lista de antenas inválida;
- janela negativa;
- nível de log desconhecido.

### CLI

- retorna sucesso com configuração válida;
- retorna erro com configuração inválida;
- não tenta acessar a rede.

Os testes não podem exigir um arquivo `.env` real.

---

## 12. Comandos de validação

Executar:

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Também validar a instalação editável:

```bash
pip install -e ".[dev]"
```

E executar manualmente:

```bash
rfid-reader check-config
```

ou o comando equivalente definido no projeto.

---

## 13. Critérios de aceite

- [ ] O projeto usa estrutura `src`.
- [ ] O pacote pode ser instalado em modo editável.
- [ ] Existe uma CLI executável.
- [ ] A configuração é carregada e validada.
- [ ] `.env.example` documenta todas as variáveis.
- [ ] `.env` está ignorado pelo Git.
- [ ] Não há conexão de rede nesta funcionalidade.
- [ ] Os testes não dependem do FX9600.
- [ ] Ruff não apresenta erros.
- [ ] A formatação está válida.
- [ ] Mypy não apresenta erros.
- [ ] Pytest passa.
- [ ] README contém instruções para Windows e Linux.
- [ ] Nenhuma dependência desnecessária foi adicionada.

---

## 14. Prompt sugerido para o Codex CLI

```text
Implemente a funcionalidade descrita em "docs/000 - Criar ambiente.md".

Antes de alterar arquivos:
1. leia o AGENTS.md;
2. leia toda a funcionalidade;
3. inspecione o estado atual do repositório;
4. apresente um plano curto.

Use as skills $feature-implementation e $python-quality.

Implemente somente o escopo da funcionalidade 000.
Não implemente comunicação LLRP nem conexão com o FX9600.

Ao terminar:
- execute ruff check .;
- execute ruff format --check .;
- execute mypy src;
- execute pytest;
- revise o diff;
- informe arquivos alterados, decisões tomadas e comandos executados.
```
