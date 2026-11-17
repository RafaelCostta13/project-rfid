# ADR-032 — Encerramento de passagem vazia no timeout

## Contexto

Uma passagem sem etiquetas permanecia aguardando DI2 ou DI3 após o timeout,
impedindo a próxima leitura automática.

## Decisão

Ao parar o inventário pelo timer existente, o controlador consulta o conjunto de
EPCs únicos aceitos pelo serviço de consultas. Sem EPCs, finaliza a passagem com
o motivo interno `timeout_sem_epcs`; caso contrário, preserva a complementação.
A interface recebe a contagem desse mesmo conjunto. A parada aguarda a entrega
dos callbacks já aceitos, e cada início usa uma geração para rejeitar callbacks
antigos após uma nova sessão.

## Consequências

O backend não recebe registros fictícios e a decisão não espera respostas HTTP.
Um callback aceito precisa terminar sua entrega antes da parada ser concluída.
As verificações automatizadas usam fakes; a operação física requer homologação.
