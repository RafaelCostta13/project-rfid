# RFID Reader

Aplicação Python para comunicação com leitores RFID, inicialmente o Zebra FX9600.
A tela principal apresenta o estado da sessão LLRP e do acesso à internet, além
de permitir iniciar e parar um inventário manual para visualizar Tags em tempo
real.

## Requisitos

- Python 3.12 ou superior;
- `pip`;
- suporte Tkinter do Python (normalmente incluído no Windows; no Linux pode exigir
  o pacote `python3-tk`);
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
validados. `RFID_CONNECTION_TIMEOUT_SECONDS` controla o timeout das sondagens e
`RFID_STATUS_CHECK_INTERVAL_SECONDS` define o intervalo entre atualizações.

Para consultar os EPCs pelo fluxo do Power Automate, configure também:

```dotenv
SHAREPOINT_LOOKUP_URL=https://endpoint-do-fluxo
SHAREPOINT_LOOKUP_TIMEOUT_SECONDS=10
SHAREPOINT_LOOKUP_QUEUE_SIZE=100
```

`SHAREPOINT_LOOKUP_URL` é obrigatória e pode conter uma assinatura de acesso.
Mantenha seu valor somente no `.env`; a aplicação não exibe nem registra essa URL
nos logs.

## Abrir a tela principal

Com o ambiente virtual ativado:

```bash
rfid-reader show
```

A aplicação mantém uma única sessão LLRP com o FX9600 e a reutiliza tanto para o
status quanto para o inventário manual. Na página **Status do sistema**, use
**Iniciar leitura** e **Parar leitura** para controlar o inventário e acompanhar
as Tags em tempo real. Cada Tag aparece como **Consultando** e depois recebe o
resultado **Encontrada**, **Não encontrada** ou **Erro**. A lista e a deduplicação
são reiniciadas a cada novo início.

Quando disponibilizados pelo Power Automate, a tabela também apresenta cliente,
nota fiscal, volume, pedido e doca associados ao EPC. Campos ausentes ou nulos
permanecem vazios.

A coluna **Tag** é uma conversão ASCII somente para apresentação. O EPC
hexadecimal original continua sendo usado internamente na consulta, deduplicação
e associação da resposta.

As consultas HTTP são processadas por uma fila limitada e por um único worker,
sem bloquear o callback LLRP. Durante a mesma sessão, a combinação de reader,
antena e EPC é consultada apenas uma vez. Ao parar e iniciar uma nova sessão, o
ROSpec é recriado, a deduplicação é limpa e o mesmo EPC pode ser lido e
consultado novamente.

Nesta etapa, o inventário utiliza somente a primeira antena de `RFID_ANTENNAS`.
São criadas apenas configurações transitórias da sessão e um ROSpec temporário,
removido ao parar a leitura ou fechar a aplicação. Nenhuma configuração
persistente do reader é alterada.

O acesso à internet é verificado por HTTPS, evitando depender da liberação da
porta DNS 53. Os estados de RFID e Internet são verificados de forma independente.

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

Testes automatizados não dependem do equipamento. A confirmação de leitura,
interrupção e desconexão no FX9600 deve ser executada manualmente no ambiente do
reader.
# project-rfid
# project-rfid
