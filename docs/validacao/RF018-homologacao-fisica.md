# RF018 — Checklist de homologação física

Status: pendente. Nenhum equipamento físico foi utilizado nesta implementação.
Os testes simulados não substituem a homologação.

A retirada do Tkinter e a entrada Qt oficial foram autorizadas pelo usuário
em 2026-10-09 antes desta homologação. A mudança de software não preenche os
itens físicos abaixo nem autoriza presumir que foram validados.

## Preparação

- [ ] Responsável confirma que o ambiente está preparado e autoriza os comandos físicos.
- [ ] Windows nativo; IP/porta e antena do FX9600 conferidos.
- [ ] Porta COM, baud rate, paridade, stop bits e device ID conferidos com a placa.
- [ ] URL do Backend e ambiente Rails de testes conferidos.
- [ ] DI1/DI2 e CH1/CH2/CH3 identificados; pessoas e equipamentos em condição segura.
- [ ] Nenhuma segunda instância ocupa o reader ou a porta COM.
- [ ] `.env` externo revisado pelo operador; segredos permanecem fora do repositório.
- [ ] Versão anterior disponível no Git para recuperação; registrar o commit da versão testada.

## Inicialização e disponibilidade

- [ ] Abrir `rfid-reader --env-file <arquivo>` ou o executável equivalente.
- [ ] RFID, Internet e Comandos representam as conexões reais.
- [ ] Sistema e Base de dados representam `status` e `database` da mesma resposta health.
- [ ] Backend indisponível impede novos ciclos; retorno restaura a disponibilidade.
- [ ] Falha PostgreSQL aparece em Base de dados conforme o contrato do Backend.
- [ ] Conexões usam somente a sessão Zebra e a sessão serial compartilhadas.

## Ciclo RFID e Backend

- [ ] DI ativa significa FEIXE LIVRE; DI desativada significa FEIXE INTERROMPIDO.
- [ ] Iniciar habilita o automático sem iniciar inventário imediatamente.
- [ ] Amostra inicial com DI1 já desativada não cria uma passagem artificial.
- [ ] Com DI1/DI2 livres, CH1 ON, CH2 OFF, CH3 OFF; RFID aguardando.
- [ ] Transição DI1 ATIVA → DESATIVADA inicia um único inventário e timer.
- [ ] Durante leitura: CH1 OFF, CH2 ON, CH3 OFF.
- [ ] EPC encontrado: GET seguido de um POST, com payload contendo somente EPC.
- [ ] Status/Cliente/Nota fiscal/Volume/Pedido/Doca vêm do contrato Rails real.
- [ ] Releituras do mesmo EPC não duplicam linhas, contador ou POST na sessão.
- [ ] EPC inexistente não entra na tabela nem no contador e não gera POST.
- [ ] Falha/timeout de GET ou POST não fabrica sucesso nem repete POST automaticamente.
- [ ] DI2 ATIVA → DESATIVADA encerra o inventário e cancela o timer.
- [ ] Sem DI2, o ciclo termina no limite de 60 segundos.
- [ ] Nova sessão limpa a tabela/contador e pode registrar uma nova passagem legítima.
- [ ] Resposta POST de sessão anterior não modifica a sessão atual.
- [ ] CH1/CH2/CH3 após saída e timeout conferidos com a referência operacional atual.

O RF018 solicita preservar a implementação existente: o controller atual usa
60 segundos e CH3 para indisponibilidade das dependências. O arquivo histórico
RF012 descreve 30 segundos e CH3 para ambos os feixes interrompidos. A migração
mantém o controller atual e o RF018 mais recente; não altera essa lógica física.
Conferir essa divergência com a versão operacional aprovada antes da homologação.

## Diagnóstico e falhas

- [ ] Tela de diagnóstico mostra DI1–DI5 e o retorno confirmado de CH1–CH8.
- [ ] Estados ausentes/desconectados aparecem como Desconhecido.
- [ ] Com automático desabilitado, Ligar/Desligar funciona em cada canal.
- [ ] Durante automático, CH1–CH3 manuais ficam bloqueados; CH4–CH8 permanecem disponíveis.
- [ ] Iniciar após diagnóstico devolve CH1–CH3 ao controller, sem abrir outra COM.
- [ ] Perda da Waveshare interrompe RFID, cancela timer e desabilita automático.
- [ ] Perda do Zebra interrompe leitura; recuperação permite um novo ciclo controlado.
- [ ] Stop impede novos ciclos, encerra leitura ativa e cancela timer.
- [ ] Fechar durante inventário/HTTP termina workers, libera COM e não inicia POST após GET tardio.
- [ ] Comandos que falharem durante encerramento ficam registrados; nenhum sucesso físico é presumido.
- [ ] CH4–CH8 não são modificados automaticamente pelo fluxo de leitura.

## Distribuição e substituição final

- [ ] Repetir os fluxos usando a pasta completa do bundle em Windows sem Python instalado.
- [ ] Confirmar drivers da COM, acesso de rede, permissões de arquivo e logs no destino.
- [ ] Registrar versão, máquina, equipamentos, resultados e evidências sem segredos.
- [ ] Aprovar homologação física e resolver qualquer divergência operacional.
- [x] Qt oficial, entrypoint atualizado e widgets/caminhos Tkinter removidos por autorização explícita.
- [ ] Após homologação, aprovar a implantação da versão na estação de destino.

## Registro

- Responsável / data:
- Commit e checksum do executável:
- FX9600 / antena / porta COM / ambiente Backend:
- Resultados e evidências:
- Falhas ou restrições:
- Aprovação para substituição definitiva:
