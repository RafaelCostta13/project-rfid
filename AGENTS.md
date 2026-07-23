# AGENTS.md

## 1. Visão geral do projeto

Este repositório contém um software para comunicação com leitores RFID, inicialmente com o **Zebra FX9600**, desenvolvido em **Python**.

O primeiro objetivo do projeto é implementar apenas as operações fundamentais de RFID:

- conectar e desconectar do reader;
- verificar o estado da conexão;
- iniciar e parar o inventário;
- receber leituras de etiquetas;
- retornar o EPC;
- identificar a antena responsável pela leitura;
- capturar RSSI quando disponibilizado;
- eliminar leituras repetidas dentro de uma janela configurável;
- registrar logs técnicos;
- recuperar automaticamente a conexão após falhas.

O protocolo inicial de comunicação será **LLRP**.

Não implementar interface web, aplicativo, banco de dados, integração com WMS/SAP, GPIO, sensores, escrita de tags ou regras de portal sem uma funcionalidade específica solicitando isso.

---

## 2. Objetivo do MVP

O MVP estará concluído quando for possível executar um comando local que:

1. carregue a configuração por variáveis de ambiente;
2. conecte-se ao Zebra FX9600;
3. inicie o inventário em uma ou mais antenas configuradas;
4. exiba no terminal as etiquetas lidas;
5. apresente EPC, antena, RSSI e data/hora quando disponíveis;
6. ignore leituras duplicadas conforme a janela configurada;
7. pare o inventário e encerre a conexão corretamente;
8. possua testes automatizados para as regras que não dependem do equipamento físico.

---

## 3. Princípios de desenvolvimento

- Fazer alterações pequenas, incrementais e fáceis de revisar.
- Não desenvolver funcionalidades fora do escopo solicitado.
- Antes de alterar código, ler os arquivos relacionados e identificar os impactos.
- Preferir soluções simples antes de introduzir novas abstrações.
- Separar comunicação com hardware das regras de negócio.
- Não espalhar chamadas específicas da biblioteca LLRP pelo projeto.
- Encapsular dependências externas atrás de interfaces próprias.
- Não adicionar dependências de produção sem necessidade clara.
- Não alterar configurações do reader automaticamente sem solicitação explícita.
- Nunca registrar senhas, tokens ou outros segredos nos logs.
- Não esconder falhas de conexão; registrar contexto e propagar erros adequadamente.
- Não afirmar que uma integração com hardware funciona sem teste real no reader.

---

## 4. Arquitetura esperada

A estrutura inicial deve seguir aproximadamente:

```text
rfid-reader/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── .env.example
├── docs/
│   └── 000 - Criar ambiente.md
├── src/
│   └── rfid_reader/
│       ├── __init__.py
│       ├── config.py
│       ├── domain/
│       │   ├── __init__.py
│       │   └── tag_read.py
│       ├── readers/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── zebra_fx9600.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── inventory.py
│       │   └── deduplication.py
│       └── cli.py
└── tests/
    ├── unit/
    └── integration/
```

A estrutura pode ser ajustada quando houver justificativa concreta, mas deve manter a separação entre:

- domínio;
- comunicação com o reader;
- serviços;
- configuração;
- interface de execução;
- testes.

---

## 5. Responsabilidades das camadas

### `domain`

Contém modelos independentes da biblioteca LLRP.

O modelo de leitura deve representar, no mínimo:

- `epc`;
- `reader_id`;
- `antenna_id`;
- `read_at`;
- `rssi`, quando disponível;
- `seen_count`, quando disponível.

### `readers`

Contém a abstração do reader e a implementação do Zebra FX9600.

A biblioteca LLRP deve ficar restrita a essa camada.

### `services`

Contém coordenação do inventário, deduplicação, normalização e regras que não pertencem diretamente ao driver.

### `cli`

Contém apenas entrada e saída do terminal e coordenação da aplicação.

---

## 6. Interface mínima do reader

A abstração do reader deve oferecer operações equivalentes a:

```python
class RFIDReader:
    def connect(self) -> None: ...
    def disconnect(self) -> None: ...
    def is_connected(self) -> bool: ...
    def start_inventory(self) -> None: ...
    def stop_inventory(self) -> None: ...
```

O mecanismo de entrega das leituras pode usar callback, iterador ou fila assíncrona, desde que:

- não acople o domínio à biblioteca escolhida;
- permita testes com reader falso;
- tenha encerramento controlado;
- trate falhas de conexão explicitamente.

---

## 7. Configuração

Todas as configurações operacionais devem vir de variáveis de ambiente ou arquivo `.env` local não versionado.

Variáveis inicialmente esperadas:

```dotenv
RFID_READER_HOST=192.168.0.100
RFID_READER_PORT=5084
RFID_READER_NAME=fx9600-01
RFID_ANTENNAS=1
RFID_DEDUPLICATION_WINDOW_SECONDS=2.0
RFID_LOG_LEVEL=INFO
```

Regras:

- manter `.env.example` atualizado;
- nunca versionar `.env`;
- validar a configuração na inicialização;
- falhar com mensagem clara quando uma variável obrigatória estiver ausente;
- converter tipos em um único módulo de configuração.

---

## 8. Padrões Python

- Usar Python 3.12 ou superior.
- Utilizar type hints em funções públicas.
- Preferir `pathlib` a manipulação manual de caminhos.
- Usar `dataclass` ou modelos tipados para objetos de domínio simples.
- Usar UTC internamente para timestamps.
- Não usar `print` fora da camada CLI; usar logging.
- Evitar funções longas e classes com múltiplas responsabilidades.
- Não usar exceções genéricas para representar falhas conhecidas.
- Criar exceções específicas quando melhorarem o tratamento da aplicação.
- Manter compatibilidade com Linux e Windows quando possível.

---

## 9. Ferramentas de qualidade

O projeto deve utilizar:

- `pytest` para testes;
- `ruff` para lint e formatação;
- `mypy` para verificação de tipos.

Comandos esperados:

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Antes de concluir qualquer alteração, executar os comandos aplicáveis.

Se algum comando não puder ser executado, informar claramente:

- qual comando falhou ou não foi executado;
- por qual motivo;
- qual risco permanece.

---

## 10. Estratégia de testes

### Testes unitários

Não devem depender do FX9600 físico.

Cobrir pelo menos:

- validação da configuração;
- normalização de EPC;
- criação do modelo de leitura;
- deduplicação;
- controle de estado do inventário;
- comportamento diante de callbacks simulados;
- reconexão usando doubles ou fakes.

### Testes de integração

Devem ser marcados separadamente e não executados por padrão quando exigirem hardware.

Exemplo:

```bash
pytest -m hardware
```

Nunca fazer o conjunto padrão de testes depender da disponibilidade do reader.

---

## 11. Tratamento de erros e reconexão

- Diferenciar erro de configuração, erro de conexão, timeout e erro de protocolo.
- Aplicar reconexão com espera progressiva e limite configurável.
- Evitar loops de reconexão sem pausa.
- Permitir encerramento por `Ctrl+C`.
- Parar o inventário antes de desconectar quando a conexão permitir.
- Registrar início da conexão, perda da conexão, tentativas e recuperação.
- Não descartar silenciosamente leituras inválidas.

---

## 12. Logs

Usar logs estruturados e úteis para diagnóstico.

Cada evento relevante deve incluir, quando aplicável:

- nome ou ID do reader;
- host;
- antena;
- EPC;
- tipo do evento;
- erro;
- tentativa de reconexão.

Não registrar uma linha para toda leitura repetida descartada em nível `INFO`; usar `DEBUG` quando necessário.

---

## 13. Segurança operacional

- Não modificar região regulatória, potência RF, firmware ou configurações persistentes do equipamento sem solicitação explícita.
- Não executar escrita, bloqueio ou kill de tags durante o MVP.
- Não assumir que uma antena está conectada.
- Validar IDs de antena antes de iniciar o inventário.
- Operações destrutivas ou persistentes no reader exigem confirmação humana.
- Segredos devem permanecer fora do repositório.

---

## 14. Uso das skills

Skills disponíveis no repositório:

- `$rfid-development`: usar ao implementar ou revisar comunicação RFID, LLRP, inventário, eventos de tag, antenas e reconexão.
- `$python-quality`: usar ao criar ou modificar código Python, testes, configuração de lint, tipos e estrutura do projeto.
- `$feature-implementation`: usar ao implementar uma funcionalidade documentada em `docs/`.

Para tarefas RFID em Python, normalmente usar `$rfid-development` e `$python-quality` em conjunto.

---

## 15. Fluxo para implementar funcionalidades

Ao receber uma funcionalidade:

1. Ler este `AGENTS.md`.
2. Ler o documento da funcionalidade em `docs/`.
3. Inspecionar o código existente relacionado.
4. Apresentar um plano curto quando a mudança envolver vários arquivos.
5. Implementar somente o escopo solicitado.
6. Criar ou atualizar testes.
7. Executar lint, formatação, tipos e testes.
8. Revisar o diff.
9. Atualizar documentação somente quando o comportamento ou uso mudar.
10. Resumir o que foi alterado e os testes executados.

Não criar ADR para toda funcionalidade. Criar ADR apenas quando houver uma decisão arquitetural relevante, difícil de reverter ou com alternativas importantes.

---

## 16. Critério de conclusão

Uma tarefa só pode ser considerada concluída quando:

- o comportamento solicitado estiver implementado;
- o código estiver tipado e organizado conforme este documento;
- testes relevantes existirem;
- verificações aplicáveis tiverem sido executadas;
- não houver segredos ou arquivos locais versionados;
- limitações e testes não executados estiverem explicitamente informados;
- o diff tiver sido revisado pelo próprio agente.

---

## 17. Fora do escopo atual

Não implementar sem solicitação futura:

- interface gráfica ou dashboard;
- API HTTP;
- banco de dados;
- autenticação;
- integração com SAP ou WMS;
- Docker ou Kubernetes;
- fila de mensagens;
- MQTT;
- GPIO;
- sensores de presença;
- identificação de direção;
- escrita de EPC;
- leitura ou escrita de TID e User Memory;
- bloqueio ou kill de tags;
- suporte genérico a vários fabricantes;
- alta disponibilidade distribuída.
