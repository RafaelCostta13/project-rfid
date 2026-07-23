# RFID Reader

Base em Python para o software de comunicação com leitores RFID, inicialmente o
Zebra FX9600. Nesta etapa, o projeto apenas carrega e valida a configuração local:
a conexão LLRP e o inventário ainda não estão implementados.

## Requisitos

- Python 3.12 ou superior;
- `pip`;
- um terminal Bash, PowerShell ou Prompt de Comando.

## Preparação do ambiente

No Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

No Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

No Windows Prompt de Comando, use `.venv\Scripts\activate.bat` para ativar o
ambiente.

## Configuração

Copie o arquivo de exemplo e ajuste os valores para o seu ambiente:

No Linux:

```bash
cp .env.example .env
```

No Windows:

```powershell
Copy-Item .env.example .env
```

O arquivo `.env` é local e ignorado pelo Git. A variável `RFID_READER_HOST` é
obrigatória. As demais possuem valores padrão, mas valores informados são sempre
validados.

## Verificar a configuração

Com o ambiente virtual ativado:

```bash
rfid-reader check-config
```

Também é possível executar:

```bash
python -m rfid_reader.cli check-config
```

Esse comando somente valida e apresenta a configuração; ele não acessa a rede nem
tenta se conectar ao FX9600.

## Qualidade e testes

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Testes futuros que dependam de hardware serão marcados com `hardware` e não farão
parte da execução padrão.
