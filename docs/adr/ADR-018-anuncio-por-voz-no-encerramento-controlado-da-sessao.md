# ADR-018 — Anúncio por voz no encerramento controlado da sessão

## Contexto

O operador precisa ouvir a quantidade de EPCs classificados como encontrados ao fim de uma sessão RFID. A voz Microsoft Maria Desktop já é disponibilizada de modo assíncrono pelo serviço de voz.

## Decisão

O `AutomaticInventoryController` informa apenas encerramentos normais por DI2, timeout de 60 segundos ou parada manual. O runtime aguarda a fila de consultas já aceitas terminar e publica um resumo com o total de EPCs `FOUND` da sessão. A ponte Qt encaminha esse total ao mesmo serviço de voz usado pelo teste manual e pelo simulador.

Extra box, falhas de consulta e EPCs filtrados não entram no total. Cada sessão controlada produz, no máximo, um anúncio. Perda abrupta de conexão e falha operacional não acionam voz.

## Consequências

A fala pode ocorrer após o RFID já ter parado, enquanto consultas HTTP em andamento são concluídas. Isso preserva um total correto sem bloquear LLRP, Modbus ou a interface. Em falhas operacionais não há anúncio parcial.
