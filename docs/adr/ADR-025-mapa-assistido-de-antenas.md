# ADR-025 — Mapa assistido de antenas

## Contexto

O RSSI e a antena identificam a intensidade observada, mas não permitem determinar a posição física ou o ângulo da etiqueta. O diagnóstico precisa compartilhar o reader sem misturar amostras com passagens operacionais.

## Decisão

O operador seleciona o ângulo e inicia um inventário de diagnóstico somente com o modo automático parado. O runtime reserva a sessão do reader e bloqueia o início automático enquanto o mapa estiver reservado. As leituras seguem diretamente para o serviço de mapeamento, sem consulta ao backend, tabela operacional ou notificações de passagem.

O mapa mantém o maior PeakRSSI por antena, ângulo e EPC, até 2.000 pontos. O gráfico usa uma escala visual limitada entre -90 e -30 dBm; os valores originais ficam na lista. A falta de antena ou RSSI é informada e não gera ponto.

## Consequências

O mapa auxilia a comparação de sinal, mas não representa distância nem cobertura física medida automaticamente. Fechar o mapa solicita a parada do inventário. A validação de RSSI, polaridade e comportamento das antenas depende de testes no equipamento físico.
