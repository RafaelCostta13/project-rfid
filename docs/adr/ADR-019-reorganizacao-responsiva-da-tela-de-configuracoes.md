# ADR-019 — Reorganização responsiva da tela de configurações

## Contexto

A tela de Configurações concentrava grupos distintos no mesmo card e utilizava largura total para o filtro EPC. Isso dificultava localizar opções e aumentava a rolagem necessária em resoluções desktop.

## Decisão

A página passa a organizar os grupos existentes em um grid responsivo de duas colunas, reduzido para uma coluna quando a largura disponível não comporta os controles. RFID, Waveshare, Doca Estação, Áudio, Ferramentas de Teste, Filtro EPC e Backend RFID possuem cards próprios. A lista de prefixos EPC permanece no mesmo card, com rolagem interna e altura limitada.

As configurações Data bits e Paridade, bem como Stop bits e Device ID, são apresentadas lado a lado no card Waveshare. Os componentes, sinais e bindings existentes são preservados.

## Consequências

O acesso às configurações fica mais compacto em desktop sem mudar regras de negócio, serviços ou integrações de hardware. Em telas estreitas, os cards são empilhados para evitar sobreposição e corte dos controles.
