# 001 - Criar tela principal e exibir status das conexões

## Objetivo

Criar a tela principal da aplicação RFID e apresentar ao usuário o
estado atual das conexões essenciais para o funcionamento do sistema:

-   conexão com o reader RFID;
-   conexão com a internet.

Esta funcionalidade será a base visual da aplicação e deverá permitir
que novos recursos sejam adicionados posteriormente.

------------------------------------------------------------------------

## Contexto

A aplicação será utilizada para se comunicar com um reader RFID Zebra
FX9600.

A conexão com o equipamento já foi validada por meio da biblioteca
`sllurp`, utilizando o protocolo LLRP.

Antes de implementar as operações de inventário e leitura de tags, é
necessário criar a interface principal da aplicação e permitir que o
usuário visualize rapidamente se o sistema está conectado ao reader RFID
e se possui acesso à internet.

------------------------------------------------------------------------

## Escopo

### Esta funcionalidade contempla

-   criar a janela principal da aplicação;
-   criar uma área para exibir o status das conexões;
-   verificar a conexão com o reader RFID;
-   verificar a conexão com a internet;
-   apresentar os estados de forma visual e textual;
-   permitir a atualização periódica dos estados;
-   registrar alterações importantes de estado no log da aplicação.

------------------------------------------------------------------------

## Fora do escopo

-   leitura de tags RFID;
-   inventário RFID;
-   exibição de EPC;
-   seleção ou configuração de antenas;
-   gravação em etiquetas;
-   alteração de potência do reader;
-   configuração persistente do Zebra FX9600;
-   reconexão automática avançada;
-   cadastro de readers;
-   autenticação de usuários;
-   armazenamento em banco de dados;
-   tela de configurações;
-   histórico de conexões.

------------------------------------------------------------------------

## Requisitos Funcionais

-   Exibir a tela principal.
-   Exibir o status da conexão com o reader RFID.
-   Exibir o status da conexão com a internet.
-   Atualizar os estados periodicamente.
-   Exibir estados: **Conectado**, **Desconectado**, **Verificando** e
    **Erro**.
-   Encerrar corretamente conexões e verificações ao fechar a aplicação.
-   Registrar mudanças de estado no log.

------------------------------------------------------------------------

## Requisitos Não Funcionais

-   Compatível com Windows e Linux.
-   Configurações externas para IP, porta LLRP, timeout e intervalo de
    verificação.
-   A interface não deve acessar diretamente a biblioteca `sllurp`.
-   As verificações devem permitir uso de implementações fake para
    testes.
-   Falhas não devem encerrar a aplicação.
-   Não executar operações destrutivas no reader.

------------------------------------------------------------------------

## Regras de Negócio

-   Os status iniciam como **Verificando**.
-   O reader só é considerado conectado após a sessão LLRP estar pronta.
-   A internet e o RFID possuem estados independentes.

------------------------------------------------------------------------

## Critérios de Aceite

-   A tela principal é exibida.
-   Os status RFID e Internet aparecem ao iniciar.
-   Os estados são atualizados automaticamente.
-   A conexão RFID muda corretamente entre Conectado, Desconectado e
    Erro.
-   A conexão com a internet muda corretamente entre Conectado e
    Desconectado.
-   O fechamento da aplicação encerra conexões corretamente.

------------------------------------------------------------------------

## Testes

### Sem hardware

-   Reader fake conectado.
-   Reader fake desconectado.
-   Timeout.
-   Internet conectada.
-   Internet desconectada.
-   Alteração de estado.
-   Encerramento correto.

### Com hardware

-   Conectar ao Zebra FX9600.
-   Reader desligado.
-   Cabo de rede desconectado.
-   Recuperação da conexão.
-   Encerramento correto da sessão LLRP.

------------------------------------------------------------------------

## Definição de Pronto

A funcionalidade será considerada concluída quando:

-   a tela principal estiver implementada;
-   os status RFID e Internet forem exibidos;
-   as verificações ocorrerem periodicamente;
-   os testes automatizados passarem;
-   a conexão com o FX9600 for validada manualmente;
-   nenhuma operação persistente ou destrutiva for executada no reader.
