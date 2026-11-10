# ADR 021: Seleção da voz das notificações

## Contexto

A voz usada nas notificações era fixa e podia não estar instalada no Windows.

## Decisão

Listar as vozes habilitadas disponíveis no System.Speech, apresentando nome e idioma. Salvar o nome escolhido em `RFID_VOICE_NAME` e usá-lo nas notificações e no teste de voz.

## Consequências

A lista depende das vozes instaladas e acessíveis ao System.Speech. A frase permanece em português; uma voz de outro idioma altera sua pronúncia, mas não traduz a mensagem. Se a voz escolhida for removida, a reprodução informa o erro.
