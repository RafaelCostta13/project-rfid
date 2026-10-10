# RF018 — Evidências da Fase 1 e configuração local 2.1

Estas imagens são capturas do QML efetivamente renderizado no Windows com
Python 3.12.10 e PySide6 6.10.3. Não são imagens geradas nem mockups desenhados.
Os dados apresentados são fictícios; nenhum serviço operacional foi iniciado.

| Arquivo | Cenário |
|---|---|
| [corporate-dark.png](corporate-dark.png) | Corporate Dark, sistema apto |
| [navy-dark.png](navy-dark.png) | Navy Dark, sistema apto, mesma composição |
| [leitura.png](leitura.png) | Leitura simulada, amarelo |
| [falha.png](falha.png) | Sistema indisponível, vermelho |
| [verificando.png](verificando.png) | Verificando, amarelo |
| [sem-registros.png](sem-registros.png) | Tabela vazia, contador zero |
| [wheel-navy.png](wheel-navy.png) | Recursos carregados da distribuição wheel instalada separadamente |
| [configuracoes.png](configuracoes.png) | Etapa 2.1: formulário com valores fictícios, sem conexão/inventário |
| [configuracoes-backend.png](configuracoes-backend.png) | Mesma tela após rolagem; Backend e ações desabilitadas |
| [wheel-configuracoes.png](wheel-configuracoes.png) | SettingsPage e componentes do wheel atualizado, instalado separadamente |

As capturas finais usam a plataforma Windows nativa do Qt e renderização
software. A escala do desktop e a área disponível podem limitar o tamanho
efetivo da janela: `--size` recebe pixels lógicos, não físicos. A tabela possui
scroll; a existência dos cinco registros é verificada nos testes, mesmo quando
nem todas as linhas cabem na janela.

Também foi executada uma matriz automatizada offscreen com resoluções físicas
1366×768, 1600×900 e 1920×1080, nas escalas 100/125/150%. Cada execução carrega
os recursos locais, renderiza, salva PNG e encerra sem erros QML. Essa matriz
não substitui inspeção interativa nos monitores do operador.

**Corporate Dark aprovado** pelo usuário para continuidade da integração
incremental. Navy Dark permanece disponível. Essa aprovação não equivale à
homologação física ou à aprovação do fluxo operacional completo.

Na etapa 2.1, foram instanciados somente serviços de configuração local, sem
reader, cliente HTTP, monitor ou conexão serial. Valores das capturas foram
injetados em memória; o `.env` real não foi aberto nem modificado. Indicadores
desconhecidos são intencionais. Start/Stop, testes de conexão e diagnóstico
continuam desabilitados; a tabela não contém os cinco dados do protótipo.
O formulário também é testado offscreen nas três resoluções × três escalas.

Ver [ADR-015](../../adr/ADR-015-migracao-incremental-pyside6-qml.md) e as instruções
de execução no [README do projeto](../../../README.md).
