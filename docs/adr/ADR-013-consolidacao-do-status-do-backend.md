# ADR-013 — Consolidação do status do Backend RFID

- Status: Aceita
- Data: 2026-10-07
- Requisito: Ajuste pós-RF016
- Substitui parcialmente: ADR-011

## Contexto

O RF015 apresentou `Sistema` e `Base de dados` a partir da mesma resposta de
health do Backend. Embora os campos `status` e `database` tenham significados
distintos no contrato Rails, a aplicação desktop não precisa exibir nem usar
dois indicadores para a mesma dependência operacional do Backend.

## Decisão

Manter somente o indicador `Sistema` na interface e na regra de disponibilidade
do software RFID.

O monitor continua fazendo uma única chamada:

```text
GET {RFID_BACKEND_BASE_URL}/api/v1/health
```

Para a aplicação desktop, somente o campo `status` é utilizado:

- `status = "ok"` → `Sistema` conectado;
- qualquer outro status, resposta HTTP não aceita, timeout, falha de rede ou
  contrato inválido → `Sistema` em erro.

O campo `database`, quando retornado pelo Backend, permanece permitido no JSON
mas é ignorado pela aplicação. Não há segundo status, segunda requisição nem
consulta direta ao PostgreSQL.

`system_ready` passa a exigir Internet, RFID, Waveshare e `Sistema`, sem uma
dependência separada chamada `DATABASE`. CH1, CH2 e CH3 mantêm seus significados
anteriores.

## Alternativas consideradas

- Manter os dois indicadores: rejeitado por redundância visual e operacional.
- Fazer duas chamadas para o health: rejeitado por duplicar tráfego e permitir
  estados inconsistentes.
- Usar apenas `database`: rejeitado porque o indicador representa a
  disponibilidade da API Rails como dependência do desktop.

## Consequências

A interface fica mais simples e a disponibilidade do Backend possui uma única
fonte de verdade. Uma falha do PostgreSQL continuará sendo refletida pelo
Backend conforme o contrato de `status`; o desktop não apresenta uma segunda
classificação redundante.

O enum legado `ConnectionKind.DATABASE` pode permanecer para compatibilidade de
módulos históricos, mas não é exibido, monitorado pelo bootstrap atual nem
participa do `system_ready`.
