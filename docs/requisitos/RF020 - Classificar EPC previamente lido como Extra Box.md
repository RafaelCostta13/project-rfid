# RF020 — Classificar EPC previamente lido como Extra Box

## Objetivo

Corrigir a contabilização de etiquetas RFID para que um EPC existente na base,
mas já registrado anteriormente no portal RFID, seja classificado como Extra
Box e não seja somado ao contador de EPCs encontrados.

## Contexto

Após a leitura de um EPC, a aplicação consulta:

```text
GET /api/v1/rfid_records/{epc}
```

O Backend retorna, entre outros campos, `read_count`:

- `0`: o EPC nunca passou pelo portal RFID;
- valor maior que `0`: o EPC já passou pelo portal RFID anteriormente.

Depois de uma consulta encontrada, a aplicação deve continuar registrando a
passagem em:

```text
POST /api/v1/rfid_reads
{"epc": "<EPC_NORMALIZADO>"}
```

O POST deve ocorrer mesmo quando o `read_count` do GET for maior que zero, pois
o Backend deve continuar atualizando seu contador e histórico.

## Regras funcionais

### RF020.1 — EPC não encontrado

Quando o GET não localizar o EPC, a aplicação deve:

- classificar o resultado como `NOT_FOUND`;
- tratar o EPC como Extra Box;
- incrementar o contador de Extra Box somente se esse EPC ainda não tiver sido
  contado na sessão;
- não executar o POST de registro.

### RF020.2 — EPC encontrado pela primeira vez

Quando o GET localizar o EPC com `read_count == 0`, a aplicação deve:

- classificar o resultado como `FOUND`;
- incrementar o contador de EPCs encontrados somente uma vez na sessão;
- executar o POST de registro da passagem.

### RF020.3 — EPC já lido anteriormente

Quando o GET localizar o EPC com `read_count > 0`, a aplicação deve:

- classificar o resultado como `EXTRA_BOX`;
- não incrementar o contador de EPCs encontrados;
- incrementar o contador de Extra Box somente uma vez na sessão;
- executar o POST de registro da passagem;
- preservar e validar a resposta do POST para atualizar os dados da passagem.

### RF020.4 — Fonte do critério

A classificação deve usar o `read_count` recebido no GET. O `read_count`
retornado pelo POST representa o estado após o registro atual e não deve mudar
a classificação definida antes do POST.

### RF020.5 — Deduplicação

O mesmo EPC não deve iniciar novo GET/POST nem aumentar os contadores mais de
uma vez na mesma sessão, respeitando a chave de deduplicação já existente.

Ao iniciar uma nova sessão, os conjuntos e contadores da sessão anterior devem
ser limpos.

### RF020.6 — Erros

Falhas de rede, timeout, HTTP inválido ou resposta inválida devem resultar em
`ERROR`, sem incrementar encontrados ou Extra Box. O POST não deve ser
executado quando o GET não confirmar a existência do EPC.

## Critérios de aceite

- Um EPC com `read_count == 0` aparece como encontrado e incrementa somente o
  contador de encontrados.
- Um EPC com `read_count == 1` aparece como `EXTRA_BOX` e incrementa somente o
  contador de Extra Box.
- Um EPC com qualquer `read_count > 0` executa o POST.
- Um EPC ausente continua sendo Extra Box e não executa o POST.
- Leituras repetidas do mesmo EPC não duplicam nenhum contador.
- Uma nova sessão zera os contadores e permite nova contagem.
- O status `EXTRA_BOX` é distinto de `NOT_FOUND` no modelo de domínio.
- Falhas de GET ou POST não são convertidas em sucesso nem em Extra Box.

## Testes previstos

### Unitários

- parser aceita `read_count == 0`;
- parser aceita `read_count > 0`;
- `read_count == 0` produz `FOUND`;
- `read_count > 0` produz `EXTRA_BOX`;
- EPC `EXTRA_BOX` incrementa somente o total de Extra Box;
- EPC `EXTRA_BOX` executa o POST;
- EPC `NOT_FOUND` continua incrementando Extra Box sem POST;
- EPC repetido não duplica contagem nem POST;
- erro no GET ou POST produz `ERROR` sem atualizar contadores.

### Integração

- consultar um EPC com `read_count == 0` em Backend de teste;
- consultar um EPC com `read_count > 0` e confirmar classificação e POST;
- confirmar que o Backend incrementa o contador após o POST;
- validar o fluxo completo com o Zebra FX9600.

## Fora do escopo

- alterar o contrato do Backend;
- recalcular `read_count` localmente;
- impedir o registro de uma nova passagem para um EPC já lido;
- modificar região, potência, firmware ou configuração persistente do reader;
- implementar escrita, bloqueio ou kill de tags.

