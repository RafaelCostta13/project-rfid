# RF018 — Ajuste 01: relatório da correção visual

Data: 2026-10-09. Correção da barra de indicadores da tela Start.

## Branch e estado do repositório

A referência local `.git/HEAD` aponta para `integracao-backend`. Os entrypoints
e o código confirmam Qt como interface oficial. As alterações locais da migração
anterior foram preservadas; nenhum marcador de conflito foi encontrado em
fontes Python/QML. Não houve troca de branch, merge, commit ou descarte de arquivos.

Os comandos exigidos `git branch --show-current`, `git status -sb` e
`git log --oneline --decorate -10` foram tentados, mas falharam porque `git`
não está disponível no PATH deste ambiente. Status e histórico Git não puderam
ser auditados; a revisão usa snapshot local e comparação dos arquivos.

## Origem e alteração

O `Repeater` em `Main.qml` usa `uiBridge.connections`. A
`OperationalBridge._get_connections()` acrescentava `ConnectionKind.DATABASE`
com o nome Base de dados aos quatro itens de `CONNECTION_LABELS`. Essa inclusão
na integração operacional fez reaparecer o quinto indicador.

A ponte agora projeta somente RFID, Internet, Comandos e Sistema. O estado
DATABASE continua recebendo eventos internamente. No QML, os quatro componentes
`StatusIndicator` compartilham o espaço do container; o espaçador final foi
retirado. O nome do container permite localizar a barra nos testes visuais.
Header, sidebar, cards, botões, tabela, tipografia e paleta foram preservados.

## Arquivos

- Modificados: `src/rfid_reader/ui/qt/operational.py`,
  `src/rfid_reader/ui/qml/Main.qml`, `tests/ui/test_qt_operational.py`,
  `README.md`, `docs/adr/ADR-015-migracao-incremental-pyside6-qml.md`.
- Criado: este relatório.
- Nenhum arquivo removido.

Backend Client, monitor, runtime, Zebra, Waveshare, máquina de estados, sessões,
workers, deduplicação, GET/POST e timer permaneceram idênticos. Os hashes dos
demais fontes e componentes são comparados ao snapshot anterior pelo script de
revisão; o diff fica em `build/rf018-aj01-review.diff`.

O endpoint permanece `GET {RFID_BACKEND_BASE_URL}/api/v1/health`. Sistema
continua baseado no campo `status`; o monitor conserva a observação interna de
`database`. Nenhuma segunda avaliação de prontidão foi criada na interface.

## Testes e resultados

Testes direcionados da operação Qt: 24 aprovados. Cinco novos casos cobrem
falha PostgreSQL com Sistema em erro, projeção de eventos de workers e renderização
dos quatro indicadores em 910×512, 1366×768 e 1920×1080. Verificam ordem,
ausência de Base de dados/Sincronização, visibilidade, larguras equilibradas,
alinhamento, falta de sobreposição e captura QML sem avisos.

Regressão final: **382 testes executados, 382 aprovados e 0 reprovados**, em
84,59 segundos. Ruff check e format check aprovados; Mypy aprovado nos
49 arquivos de fonte. Build e verificação do executável Windows concluídos
com código de saída 0, sem hardware nem Python no PATH na execução do bundle.
A comparação de hashes confirmou que todos os demais fontes operacionais e
componentes permaneceram idênticos ao snapshot anterior.

Captura operacional simulada de Start em `build/rf018-aj01-start.png`, com os
quatro indicadores. O bundle atualizado está em `dist/DSV-RFID`; distribuir
a pasta completa. Capturas do bundle ficam em `build/rf018-distribution-smoke`.

Comandos executados:

```powershell
.venv/Scripts/python.exe -m ruff check . --no-cache
.venv/Scripts/python.exe -m ruff format --check .
.venv/Scripts/python.exe -m mypy src
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe tools/build_windows.py
.venv/Scripts/python.exe tools/verify_windows.py
```

Nenhum equipamento físico ou endpoint real foi acionado. A falha PostgreSQL foi
simulada com o transporte falso e os serviços existentes. A limitação de auditoria
Git está registrada acima.
