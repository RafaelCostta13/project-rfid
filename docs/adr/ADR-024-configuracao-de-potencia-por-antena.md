# ADR-024 — Configuração de potência por antena

## Contexto

O operador precisa ajustar individualmente as antenas sem interromper uma leitura. Os níveis disponíveis dependem da tabela de capacidades do reader.

## Decisão

Persistir os valores locais em dBm no arquivo de configuração existente. Validar a escolha contra os níveis discretos retornados pelo reader conectado e converter para índices LLRP antes da próxima janela de inventário. Sem tabela disponível, exibir a configuração local e bloquear gravações que não possam ser validadas. A interface não declara antenas fisicamente ativas sem confirmação.

## Consequências

O ajuste não reinicia uma leitura e não altera configuração persistente do equipamento. Um valor salvo incompatível com a tabela de uma conexão posterior impede o início do inventário, em vez de ser arredondado silenciosamente. A disponibilidade física e a potência efetiva exigem homologação no equipamento.
