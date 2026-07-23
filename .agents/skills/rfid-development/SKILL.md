---
name: rfid-development
description: Implementar e revisar comunicação RFID em Python, especialmente Zebra FX9600, LLRP, inventário, EPC, antenas, RSSI, callbacks, reconexão e tratamento de eventos. Não usar para tarefas Python genéricas sem relação com RFID.
---

# RFID Development

## Objetivo

Orientar mudanças relacionadas à comunicação e às operações RFID do projeto.

## Antes de implementar

1. Leia o `AGENTS.md`.
2. Leia a funcionalidade correspondente em `docs/`.
3. Identifique quais partes dependem do equipamento físico.
4. Separe comportamento testável localmente de validação em hardware.
5. Confirme que o escopo não inclui operações destrutivas ou persistentes no reader.

## Regras arquiteturais

- Encapsule a biblioteca LLRP dentro da implementação do reader.
- Não exponha objetos específicos da biblioteca ao domínio ou à CLI.
- Converta relatórios do protocolo para modelos internos.
- Permita substituir o reader real por fake em testes.
- Mantenha estado explícito: desconectado, conectado e inventariando.
- Operações devem ser idempotentes quando razoável.
- `disconnect` deve tentar parar o inventário antes de encerrar.
- Callbacks da biblioteca não devem executar regras demoradas.
- Prefira uma fila interna quando o callback produzir eventos continuamente.

## Modelo de leitura

Normalize cada leitura para um objeto interno contendo:

- EPC em hexadecimal padronizado;
- identificação do reader;
- antena;
- timestamp UTC;
- RSSI opcional;
- contador de aparições opcional.

Não invente valores ausentes no relatório recebido.

## LLRP

Ao trabalhar com LLRP:

- trate a porta como configuração;
- não assuma que sempre será `5084`;
- diferencie conexão TCP de sessão LLRP pronta;
- trate timeout e encerramento remoto;
- garanta remoção ou encerramento dos recursos de inventário criados;
- não dependa de IDs fixos do protocolo espalhados no código;
- isole detalhes de ROSpec, AISpec, AccessSpec e reports;
- documente limitações específicas da biblioteca utilizada.

## Inventário

A implementação deve:

- validar antenas;
- iniciar apenas quando conectada;
- impedir múltiplos inventários concorrentes não intencionais;
- aceitar parada explícita;
- encerrar corretamente em `Ctrl+C`;
- entregar leituras sem bloquear o recebimento do protocolo;
- registrar mudança de estado.

## Reconexão

- Use espera progressiva com limite.
- Inclua jitter somente quando trouxer benefício real.
- Permita cancelamento.
- Reinicie o inventário após reconectar apenas se ele estava ativo e essa for a política configurada.
- Não crie loop apertado.
- Registre tentativa, motivo e recuperação.

## Deduplicação

A deduplicação não pertence ao driver LLRP.

Use chave inicialmente composta por:

```text
reader_id + antenna_id + epc
```

Use relógio monotônico para medir janelas locais.

Não perca o timestamp original da leitura.

## Testes

Sem hardware:

- parser e normalização;
- transições de estado;
- callback simulado;
- timeout;
- desconexão;
- reconexão;
- deduplicação;
- encerramento.

Com hardware:

- marcar com `pytest.mark.hardware`;
- não executar por padrão;
- documentar variáveis necessárias;
- não alterar configurações persistentes do reader;
- informar claramente o que foi e não foi validado.

## Segurança

Não implementar automaticamente:

- escrita em EPC;
- escrita em User Memory;
- bloqueio;
- kill;
- alteração de região;
- atualização de firmware;
- mudança persistente de potência;
- acionamento de GPIO.

Essas operações exigem funcionalidade explícita e confirmação humana.

## Resultado esperado

Ao concluir, informe separadamente:

- comportamento implementado;
- testes sem hardware;
- testes realizados no FX9600;
- limitações conhecidas;
- configuração necessária para execução.
