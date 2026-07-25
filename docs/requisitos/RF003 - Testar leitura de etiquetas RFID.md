# 003 - Testar leitura de etiquetas RFID

## Objetivo

Implementar uma funcionalidade simples para validar a leitura de etiquetas RFID pelo reader Zebra FX9600.

O usuário deverá conseguir iniciar e interromper o inventário manualmente e visualizar, em tempo real, os EPCs das etiquetas recebidas.

Esta funcionalidade tem como objetivo validar a comunicação entre a aplicação e o reader antes da implementação das funcionalidades completas de inventário.

---

# Contexto

A comunicação com o reader RFID já foi validada.

Nesta etapa será implementada apenas uma leitura simples das etiquetas presentes na área de cobertura da antena.

Não será realizada nenhuma regra de negócio sobre as leituras.

O objetivo é apenas confirmar que a aplicação consegue receber os EPCs enviados pelo reader.

---

# Escopo

Esta funcionalidade contempla:

* botão **Iniciar leitura**;
* botão **Parar leitura**;
* iniciar o inventário RFID;
* interromper o inventário RFID;
* receber EPCs enviados pelo reader;
* apresentar as etiquetas lidas na tela;
* atualizar a lista em tempo real;
* impedir múltiplos inventários simultâneos.

---

# Fora do escopo

Esta funcionalidade não contempla:

* gravação de etiquetas;
* filtros de EPC;
* deduplicação;
* RSSI;
* potência da antena;
* múltiplas antenas;
* seleção de antenas;
* banco de dados;
* histórico permanente;
* exportação;
* leitura de TID;
* leitura de User Memory;
* inventário automático ao abrir a aplicação.

---

# Fluxo da funcionalidade

### Iniciar leitura

1. O usuário pressiona **Iniciar leitura**.
2. A aplicação verifica se existe conexão com o reader.
3. Caso exista conexão:

   * inicia o inventário;
   * altera o estado da interface para **Lendo**;
   * habilita o recebimento das leituras.
4. Cada EPC recebido deve aparecer na tela.

---

### Parar leitura

1. O usuário pressiona **Parar leitura**.
2. A aplicação encerra o inventário.
3. O estado muda para **Parado**.
4. Nenhuma nova leitura deve ser recebida após a interrupção.

---

# Interface

A página **Status do Sistema** deve possuir:

```text
+------------------------------------------------------+

[ Iniciar leitura ]   [ Parar leitura ]

Status:
● Parado

--------------------------------------------------------

Etiquetas lidas

E2801170000002081890A123
E2801170000002081890A124
E2801170000002081890A125
E2801170000002081890A126

--------------------------------------------------------
```

---

# Requisitos funcionais

## RF001 — Iniciar leitura

Ao clicar em **Iniciar leitura**, a aplicação deve iniciar o inventário RFID.

---

## RF002 — Parar leitura

Ao clicar em **Parar leitura**, a aplicação deve interromper imediatamente o inventário.

---

## RF003 — Exibir EPC

Cada etiqueta recebida deve ser apresentada na tela utilizando seu EPC.

---

## RF004 — Atualização em tempo real

A lista deve ser atualizada conforme novas etiquetas forem recebidas.

Não é necessário atualizar por lote.

---

## RF005 — Não permitir múltiplas leituras

Caso o inventário já esteja ativo, clicar novamente em **Iniciar leitura** não deve iniciar um novo inventário.

---

## RF006 — Estado da leitura

A interface deve indicar um dos estados:

* Parado
* Lendo
* Erro

---

## RF007 — Limpar lista

Sempre que uma nova leitura for iniciada, a lista de etiquetas deve ser limpa.

---

## RF008 — Encerrar corretamente

Ao fechar a aplicação durante uma leitura ativa, o inventário deve ser encerrado antes do fechamento da conexão LLRP.

---

# Requisitos não funcionais

## RNF001 — Reutilizar a conexão existente

A funcionalidade deve utilizar a conexão RFID já estabelecida pela aplicação.

Não deve abrir uma segunda conexão com o reader.

---

## RNF002 — Arquitetura

A interface gráfica não deve acessar diretamente a biblioteca `sllurp`.

A leitura deve ocorrer através da camada responsável pelo reader RFID.

---

## RNF003 — Não alterar configurações

Nenhuma configuração persistente do Zebra FX9600 deve ser modificada.

---

## RNF004 — Compatibilidade

A implementação deve continuar compatível com Windows e Linux.

---

# Regras de negócio

## RN001

A leitura somente poderá ser iniciada quando o reader estiver conectado.

---

## RN002

Caso o reader seja desconectado durante o inventário, a leitura deve ser interrompida automaticamente.

---

## RN003

Após clicar em **Parar leitura**, nenhuma nova etiqueta deve ser adicionada à lista.

---

## RN004

Cada EPC deve ser exibido exatamente como recebido do reader.

Nesta etapa não deve existir qualquer tratamento ou formatação adicional.

---

## RN005

Esta funcionalidade tem finalidade exclusivamente de validação operacional do reader.

Não devem ser implementadas regras de negócio relacionadas às etiquetas.

---

# Critérios de aceite

### CA001

Ao clicar em **Iniciar leitura**, o inventário deve ser iniciado.

---

### CA002

Com etiquetas presentes na área de leitura, seus EPCs devem aparecer na tela.

---

### CA003

Ao clicar em **Parar leitura**, nenhuma nova etiqueta deve ser exibida.

---

### CA004

Não deve ser possível iniciar dois inventários simultaneamente.

---

### CA005

Caso o reader esteja desconectado, a leitura não deve iniciar e a interface deve informar o erro.

---

### CA006

Ao iniciar uma nova leitura, a lista anterior deve ser limpa.

---

### CA007

Ao fechar a aplicação durante uma leitura ativa, o inventário deve ser encerrado corretamente.

---

# Testes sem hardware

* Iniciar leitura utilizando um reader fake.
* Receber EPCs simulados.
* Parar leitura.
* Tentar iniciar duas leituras simultaneamente.
* Simular perda de conexão.
* Validar limpeza da lista ao iniciar nova leitura.

---

# Testes com o Zebra FX9600

* Iniciar inventário.
* Aproximar uma etiqueta RFID.
* Confirmar que o EPC é exibido.
* Afastar a etiqueta.
* Parar leitura.
* Confirmar que nenhum novo EPC é recebido.
* Desligar o reader durante a leitura e validar o tratamento da desconexão.

---

# Definição de pronto

A funcionalidade será considerada concluída quando:

* o botão **Iniciar leitura** iniciar o inventário RFID;
* o botão **Parar leitura** interromper o inventário;
* os EPCs forem exibidos em tempo real na interface;
* não seja possível executar dois inventários simultaneamente;
* a leitura seja encerrada corretamente ao fechar a aplicação;
* os testes com o Zebra FX9600 confirmem o recebimento e a interrupção das leituras.

### Uma recomendação de arquitetura

Em vez de chamar essa funcionalidade de **"Testar leitura de etiquetas"**, eu a chamaria de **"Inventário RFID Manual"**. Ela continuará servindo para testes agora, mas depois poderá ser reaproveitada como a base do inventário definitivo, evitando retrabalho quando adicionarmos recursos como filtros de EPC, RSSI, deduplicação, múltiplas antenas e eventos de leitura.
