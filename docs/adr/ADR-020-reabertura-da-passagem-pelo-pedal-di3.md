# ADR-020 — Reabertura da passagem pelo pedal DI3

## Contexto

O timeout encerra a janela de inventário, mas o operador pode precisar complementar a mesma passagem antes de acionar DI2.

## Decisão

O controlador automático mantém a passagem após o timeout e aceita uma nova pressão estabilizada de DI3 para iniciar outra janela de 60 segundos. A sessão de consultas e sua deduplicação são retomadas, sem limpar a tabela. DI2 encerra definitivamente a passagem; Stop e falhas conservam sua prioridade. O nível ativo do pedal fica isolado em `PEDAL_ACTIVE_LEVEL` e deve ser validado conforme a instalação.

## Consequências

EPCs já processados não geram novas consultas ou registros durante a complementação. O anúncio de encerramento ocorre no encerramento definitivo, não no timeout intermediário. A polaridade e o comportamento do pedal exigem validação no equipamento físico.
