# RF023 — Filtro de EPC por Múltiplos Prefixos Autorizados

**Projeto:** RFID System
**Requisito:** RF023
**Categoria:** Funcionalidade / Processamento RFID
**Prioridade:** Alta
**Ambiente:** Windows
**Tecnologia:** Python + PySide6 + QML
**Leitor:** Zebra FX9600
**Biblioteca:** sllurp / LLRP
**Requisitos relacionados:** RF016, RF017, RF018, RF019, RF020 e RF022
**Status:** A implementar

---

# 1. OBJETIVO

Implementar um sistema de filtragem de etiquetas RFID baseado
nos primeiros 6 caracteres hexadecimais do EPC.

O objetivo é permitir que somente etiquetas pertencentes
a determinados grupos autorizados sejam processadas
pelo software.

Atualmente, o Zebra FX9600 identifica todas as etiquetas
presentes no campo das antenas.

Com o RF023, o leitor continuará funcionando normalmente,
mas o Python deverá verificar o prefixo de cada EPC recebido
antes de encaminhá-lo ao restante da aplicação.

Os EPCs não autorizados deverão ser completamente ignorados
pelo fluxo operacional.

IMPORTANTE:

O filtro será executado exclusivamente no Python.

Não implementar pré-filtros LLRP no Zebra FX9600.

Não modificar a configuração de inventário do leitor.

Não modificar a biblioteca sllurp.

---

# 2. CONTEXTO DO PROJETO

O software RFID utiliza:

- Python.
- PySide6 + QML.
- Zebra FX9600.
- Biblioteca sllurp.
- Waveshare Modbus RTU Relay.
- Backend Rails.
- Banco PostgreSQL.
- Comunicação HTTP com o Backend.

O fluxo operacional existente possui:

1. Habilitação do modo automático.
2. Monitoramento dos sensores DI1 e DI2.
3. Início do inventário RFID após interrupção de DI1.
4. Leitura dos EPCs pelo Zebra.
5. Consulta remota dos EPCs.
6. Classificação como encontrado ou Extra Box.
7. Atualização dos contadores.
8. Exibição dos registros na tabela.
9. Registro de passagem conforme regras existentes.
10. Encerramento por DI2 ou timeout de 60 segundos.

O RF023 deverá ser integrado a esse fluxo sem alterar
seu funcionamento operacional.

---

# 3. REGRA PRINCIPAL

Para cada EPC recebido do Zebra FX9600:

1. Normalizar o valor hexadecimal.
2. Extrair os primeiros 6 caracteres.
3. Comparar o prefixo com a lista de prefixos autorizados.
4. Permitir ou rejeitar o processamento.

Se o prefixo estiver autorizado:

    Continuar o processamento RFID normalmente.

Se o prefixo não estiver autorizado:

    Ignorar o EPC imediatamente.

A comparação deverá ser exata.

Não utilizar comparação parcial.

Não utilizar busca por substring em qualquer posição.

O prefixo deverá obrigatoriamente estar nos
primeiros 6 caracteres hexadecimais do EPC.

---

# 4. RF023.01 — PREFIXOS AUTORIZADOS

Implementar inicialmente os seguintes prefixos:

| Prefixo hexadecimal | Identificação |
|---------------------|---------------|
| 445543              | DUC           |
| 474143              | GAC           |
| 47574D              | GWM           |
| 484C44              | HLD           |
| 4A4554              | JET           |
| 4D5743              | MWC           |
| 4F4D44              | OMD           |
| 534143              | SAC           |
| 424D57              | BMW           |

Total inicial:

    9 prefixos autorizados.

Cada prefixo possui:

    6 caracteres hexadecimais
    24 bits
    3 bytes

A identificação ASCII é apenas informativa.

A comparação operacional deverá utilizar
exclusivamente o valor hexadecimal.

---

# 5. RF023.02 — EXEMPLO DE FUNCIONAMENTO

Considere o seguinte EPC:

    484C44303430313237333134

Separação:

    Prefixo:
    484C44

    Restante do EPC:
    303430313237333134

Identificação:

    HLD

Resultado:

    EPC AUTORIZADO.

O EPC deverá continuar para consulta ao Backend.

Outro exemplo:

    313233343536373839303132

Prefixo:

    313233

Esse prefixo não está na lista.

Resultado:

    EPC NÃO AUTORIZADO.

O registro deverá ser descartado antes de entrar
no fluxo operacional.

---

# 6. RF023.03 — ARQUITETURA DO FILTRO

O filtro deverá ser implementado na camada Python,
imediatamente após o recebimento do EPC.

Fluxo esperado:

    ZEBRA FX9600
          |
          v
    BIBLIOTECA SLLURP
          |
          v
    EPC RECEBIDO
          |
          v
    NORMALIZAÇÃO DO EPC
          |
          v
    FILTRO DE PREFIXOS
          |
          v
    PREFIXO AUTORIZADO?
          |
          +------ NÃO ------+
          |                 |
          |                 v
          |           IGNORAR EPC
          |
         SIM
          |
          v
    DEDUPLICAÇÃO DA SESSÃO
          |
          v
    CONSULTA AO BACKEND
          |
          v
    CLASSIFICAÇÃO DO EPC
          |
          +------------------+
          |                  |
          v                  v
      ENCONTRADO         EXTRA BOX
          |                  |
          +--------+---------+
                   |
                   v
          ATUALIZAÇÃO DA TABELA
          E DOS CONTADORES

O fluxo acima é conceitual.

Preservar a ordem efetiva das operações existentes,
especialmente as regras do RF017.

O filtro deverá ocorrer antes de qualquer operação
que registre ou contabilize o EPC.

---

# 7. RF023.04 — IMPLEMENTAÇÃO EM PYTHON

Criar uma função ou serviço responsável por validar
os prefixos EPC.

Utilizar preferencialmente uma estrutura set,
permitindo consulta eficiente.

Referência de implementação:

    PREFIXOS_PERMITIDOS = {
        "445543",
        "474143",
        "47574D",
        "484C44",
        "4A4554",
        "4D5743",
        "4F4D44",
        "534143",
        "424D57",
    }

    def epc_autorizado(epc: str) -> bool:
        epc = epc.strip().upper()

        if len(epc) < 6:
            return False

        return epc[:6] in PREFIXOS_PERMITIDOS

O código acima é uma referência conceitual.

A implementação definitiva deverá:

1. Reutilizar a normalização existente do EPC.
2. Validar o formato hexadecimal.
3. Preservar o valor original normalizado.
4. Utilizar a lista configurada pelo usuário.
5. Evitar reconstruir o conjunto a cada leitura.
6. Ser independente do QML.
7. Ser facilmente testável.
8. Não adicionar bibliotecas externas.

Não converter o EPC para ASCII durante a validação.

Não modificar o valor do EPC enviado ao Backend.

Não modificar sua identificação original.

---

# 8. RF023.05 — NORMALIZAÇÃO

Antes da comparação:

- Remover espaços externos.
- Normalizar letras hexadecimais para maiúsculas.
- Verificar se o EPC possui ao menos 6 caracteres.
- Verificar se contém apenas caracteres hexadecimais.
- Preservar as validações já existentes no projeto.

Exemplo:

    Entrada:
    484c44303430313237333134

    Normalizado:
    484C44303430313237333134

Resultado:

    AUTORIZADO.

Não rejeitar um EPC válido apenas porque
a biblioteca retornou letras minúsculas.

EPCs inválidos deverão seguir o tratamento
de erro ou descarte apropriado já existente.

Não classificá-los automaticamente como Extra Box.

---

# 9. RF023.06 — CONFIGURAÇÕES RFID

Adicionar uma nova seção na tela:

    Configurações → RFID

Título:

    Filtro de EPC

Essa seção deverá permitir:

1. Habilitar ou desabilitar o filtro.
2. Visualizar os prefixos cadastrados.
3. Adicionar novos prefixos.
4. Remover prefixos existentes.
5. Salvar a configuração.
6. Recuperar a configuração salva.

Preservar a identidade visual Corporate Dark.

Não redesenhar a tela de configurações.

---

# 10. RF023.07 — HABILITAR / DESABILITAR

Adicionar um controle:

    Habilitar filtro de EPC

Tipo recomendado:

    Switch ou Checkbox.

## Filtro habilitado

O sistema deverá comparar cada EPC recebido
com a lista de prefixos autorizados.

Somente EPCs autorizados poderão continuar
no processamento.

## Filtro desabilitado

O sistema deverá ignorar a restrição de prefixos.

Todos os EPCs válidos deverão seguir o
processamento normal anterior ao RF023.

Isso permitirá executar testes e utilizar
o sistema sem restrições quando necessário.

## Configuração inicial

Em uma instalação sem configuração anterior,
utilizar:

    Filtro habilitado: SIM

    Prefixos:
    Os 9 prefixos definidos neste requisito.

Em instalações existentes, preservar as
demais configurações RFID já armazenadas.

---

# 11. RF023.08 — GERENCIAMENTO DOS PREFIXOS

Apresentar a lista de prefixos autorizados.

Exemplo:

    Filtro de EPC

    [X] Habilitar filtro

    Prefixos autorizados:

    445543    DUC
    474143    GAC
    47574D    GWM
    484C44    HLD
    4A4554    JET
    4D5743    MWC
    4F4D44    OMD
    534143    SAC
    424D57    BMW

    [Adicionar prefixo]

    [Salvar]

Permitir remover prefixos individualmente.

A identificação ASCII poderá ser apresentada
automaticamente como informação auxiliar,
quando representar caracteres legíveis.

Não exigir descrição para cadastrar um prefixo.

Não permitir prefixos duplicados.

A lista deverá ser editável sem necessidade
de modificar o código-fonte.

---

# 12. RF023.09 — VALIDAÇÃO DOS PREFIXOS

Ao cadastrar um prefixo, validar:

1. Comprimento exato de 6 caracteres.
2. Caracteres permitidos: 0-9, A-F.
3. Normalização para maiúsculas.
4. Ausência de duplicidade.
5. Ausência de campos inválidos.

Exemplos:

    484C44 -> Válido.

    484c44 -> Válido após normalização.

    484C4 -> Inválido.

    484C444 -> Inválido.

    ZZZZZZ -> Inválido.

    484C4G -> Inválido.

    Campo vazio -> Inválido.

Quando o filtro estiver habilitado,
deverá existir pelo menos um prefixo autorizado.

Não permitir salvar o filtro habilitado
com uma lista vazia.

Apresentar mensagens claras de validação.

Não descartar configurações previamente
salvas quando o usuário informar um valor inválido.

---

# 13. RF023.10 — PERSISTÊNCIA

Salvar a configuração no mecanismo local
já utilizado pelo software.

Não criar um banco de dados adicional.

Não criar armazenamento no Backend Rails.

Não adicionar SQLite.

Não criar uma nova estrutura paralela de configuração.

Exemplo conceitual:

    {
        "epc_filter": {
            "enabled": true,
            "prefixes": [
                "445543",
                "474143",
                "47574D",
                "484C44",
                "4A4554",
                "4D5743",
                "4F4D44",
                "534143",
                "424D57"
            ]
        }
    }

Integrar essa estrutura ao arquivo de configuração
existente, respeitando seu formato real.

Não substituir o conteúdo completo do arquivo.

Preservar:

- IP do Zebra.
- Porta LLRP.
- Nome do leitor.
- Configurações de comunicação.
- Configurações Waveshare.
- Configurações do Backend.
- Configuração visual.
- Demais parâmetros existentes.

Ao reiniciar a aplicação, o filtro deverá
recuperar automaticamente os valores salvos.

---

# 14. RF023.11 — APLICAÇÃO DAS CONFIGURAÇÕES

As alterações dos prefixos deverão ser aplicadas
de maneira controlada.

Regra:

    Salvar nova configuração
           |
           v
    Persistir no arquivo local
           |
           v
    Disponibilizar para o próximo inventário

Se um inventário RFID estiver em andamento,
não modificar a lista efetiva durante aquela leitura.

Utilizar um snapshot imutável da configuração
no início de cada inventário.

As alterações salvas durante uma leitura
deverão entrar em vigor no próximo inventário.

Apresentar uma indicação discreta, caso necessário:

    As alterações serão aplicadas na próxima leitura.

Não interromper a leitura atual.

Não reiniciar o Zebra.

Não alterar o timer.

Não modificar os relés.

Não desabilitar o modo automático.

---

# 15. RF023.12 — EPC NÃO AUTORIZADO

Quando o filtro estiver habilitado e o EPC
não possuir um prefixo permitido:

O sistema deverá:

- Ignorar o EPC.
- Não consultar o Backend.
- Não executar POST de passagem.
- Não registrar o EPC na sessão.
- Não adicionar o EPC à tabela.
- Não incrementar EPCs encontrados.
- Não incrementar Extra Box.
- Não modificar o estado operacional.
- Não reiniciar o timer.
- Não acionar relés.

O descarte deverá ocorrer antes da deduplicação
e dos demais processamentos de negócio.

A leitura física do Zebra continuará normal.

Somente o processamento no software será bloqueado.

---

# 16. RF023.13 — INTEGRAÇÃO COM EXTRA BOX

Preservar integralmente as regras de classificação
Extra Box implementadas no RF019 e RF022.

Um EPC com prefixo autorizado deverá continuar
sendo classificado conforme a resposta do Backend.

## Cenário A

    Prefixo autorizado.
    HTTP 200.
    Status pendente.

Resultado:

    EPC encontrado.

## Cenário B

    Prefixo autorizado.
    HTTP 200.
    Status lido anteriormente.

Resultado:

    Extra Box.

## Cenário C

    Prefixo autorizado.
    HTTP 404.

Resultado:

    Extra Box.

## Cenário D

    Prefixo não autorizado.
    HTTP não deverá ser solicitado.

Resultado:

    Ignorar EPC.

IMPORTANTE:

Uma etiqueta não autorizada não poderá
ser classificada como Extra Box.

O filtro deverá executar antes da consulta HTTP.

As etiquetas Extra Box autorizadas continuarão
aparecendo na tabela com o destaque amarelo
discreto estabelecido no RF022.

---

# 17. RF023.14 — DEDUPLICAÇÃO

Preservar a deduplicação existente por sessão.

Exemplo:

    EPC A -> Prefixo autorizado.
    EPC A -> Prefixo autorizado.
    EPC A -> Prefixo autorizado.

Resultado:

    EPC A processado uma única vez,
    conforme as regras existentes.

Outro exemplo:

    EPC B -> Prefixo não autorizado.
    EPC B -> Prefixo não autorizado.

Resultado:

    EPC B ignorado.

Não adicionar EPC B ao conjunto de EPCs
processados da sessão.

Não permitir que EPCs descartados ocupem
a lista de etiquetas válidas.

Não alterar a deduplicação dos registros
encontrados ou Extra Box.

---

# 18. RF023.15 — PERFORMANCE

A filtragem deverá possuir baixo custo computacional.

Requisitos:

1. Utilizar comparação de prefixo.
2. Utilizar set para consulta.
3. Evitar loops desnecessários.
4. Não consultar arquivo de configuração por EPC.
5. Não realizar operações HTTP para verificar prefixos.
6. Não executar consultas ao banco de dados.
7. Não criar threads adicionais somente para o filtro.
8. Não atualizar componentes QML para EPCs rejeitados.
9. Não gerar logs repetitivos para cada leitura descartada.
10. Evitar processamento desnecessário no callback RFID.

A lista autorizada deverá estar disponível
em memória durante o inventário.

O filtro não deverá bloquear a thread responsável
pelo recebimento dos EPCs.

IMPORTANTE:

O filtro Python não reduz a quantidade de etiquetas
inventariadas fisicamente pelo Zebra.

Ele reduz o processamento posterior,
o tráfego HTTP e as atualizações da aplicação.

Não apresentar essa implementação como
um pré-filtro de rádio ou LLRP.

---

# 19. RF023.16 — LOGS E DIAGNÓSTICO

Adicionar registros de diagnóstico proporcionais
à necessidade de manutenção.

Exemplo ao iniciar inventário:

    RFID EPC Filter enabled.
    Allowed prefixes: 9.

Exemplo com filtro desabilitado:

    RFID EPC Filter disabled.

Evitar escrever uma mensagem para cada callback
de um EPC rejeitado.

Se necessário, utilizar logging DEBUG
ou métricas agregadas para diagnóstico.

Não exibir EPCs rejeitados no Dashboard.

Não criar um novo card de rejeições.

Não alterar o conceito de Extra Box.

---

# 20. RF023.17 — INTEGRAÇÃO COM QML

O QML será responsável exclusivamente por
apresentar e editar as configurações.

A validação operacional deverá permanecer
na camada Python.

Arquitetura esperada:

    QML
     |
     v
    Qt Bridge / Configuration Controller
     |
     v
    Configuração local
     |
     v
    RFID Service
     |
     v
    EPC Prefix Filter
     |
     v
    Processamento existente

Reutilizar:

- Signals.
- Slots.
- Properties.
- Componentes visuais.
- Sistema de configuração atual.

Não implementar regras de filtragem dentro do QML.

Não duplicar a lista de prefixos em várias camadas
como fontes independentes.

---

# 21. RF023.18 — PRESERVAÇÃO OPERACIONAL

O RF023 não poderá modificar:

- Comunicação LLRP.
- Configuração de antenas.
- Potência do Zebra FX9600.
- Inventário RFID.
- Biblioteca sllurp.
- Controle dos sensores.
- DI1.
- DI2.
- Timer de 60 segundos.
- CH1.
- CH2.
- CH3.
- Comunicação Waveshare.
- Modbus RTU.
- Estados operacionais.
- Botões Iniciar e Parar leitura.
- Indicadores de conectividade.
- Consulta GET do Backend.
- Registro POST de passagem.
- Classificação Extra Box.
- Deduplicação da sessão.

A implementação deverá ser restrita à
validação dos EPCs e à configuração do filtro.

Não realizar refatorações amplas.

---

# 22. RF023.19 — TRATAMENTO DE ERROS

## Configuração inválida

Não aceitar o salvamento.

Apresentar mensagem ao usuário.

Preservar a última configuração válida.

## Falha ao salvar

Informar o erro.

Não apresentar sucesso indevidamente.

Manter consistente o estado efetivo do filtro.

## Configuração ausente

Inicializar com os nove prefixos definidos
neste requisito e filtro habilitado.

## Configuração legada

Migrar ou complementar a estrutura existente
sem perder outras configurações.

## Configuração armazenada inválida

Não iniciar silenciosamente um filtro vazio
que descarte todas as etiquetas.

Não desabilitar silenciosamente o filtro,
permitindo etiquetas não autorizadas.

Registrar o problema e exigir uma
configuração válida antes de iniciar
um novo inventário.

## EPC inválido

Preservar o tratamento de validação existente.

Não contabilizar como Extra Box.

---

# 23. ANÁLISE OBRIGATÓRIA DO REPOSITÓRIO

Antes da implementação:

1. Ler AGENTS.md.
2. Verificar a branch atual.
3. Executar git status.
4. Identificar os serviços RFID.
5. Localizar o callback do Zebra FX9600.
6. Localizar a normalização dos EPCs.
7. Localizar a deduplicação.
8. Localizar a consulta GET ao Backend.
9. Localizar o tratamento Extra Box.
10. Localizar a atualização da tabela.
11. Localizar a Qt Bridge.
12. Localizar a tela Configurações → RFID.
13. Localizar o arquivo de configuração.
14. Identificar os testes automatizados existentes.

Verificar se existe mais de um caminho
de entrada para EPCs.

O filtro deverá ser aplicado ao ponto de entrada
comum do processamento operacional.

Não implementar filtros separados e inconsistentes
em diferentes componentes.

Caso existam funções de diagnóstico que precisem
receber todos os EPCs, preservar o comportamento
diagnóstico existente sem permitir que ele
contorne o filtro do inventário operacional.

---

# 24. ESTRATÉGIA DE IMPLEMENTAÇÃO

## Etapa 1 — Inspeção

Identificar o fluxo completo de recebimento
e processamento de EPCs.

## Etapa 2 — Serviço de filtragem

Implementar a validação dos prefixos em Python.

Utilizar uma única fonte de configuração.

## Etapa 3 — Integração operacional

Executar o filtro antes da deduplicação,
consulta ao Backend e atualização da sessão.

## Etapa 4 — Configuração

Adicionar a seção de gerenciamento de prefixos
na tela Configurações → RFID.

## Etapa 5 — Persistência

Integrar os parâmetros ao mecanismo local existente.

## Etapa 6 — Ciclo de vida

Garantir snapshot do filtro por inventário,
recarregamento controlado e consistência entre sessões.

## Etapa 7 — Testes

Criar e executar testes automatizados
sem depender do hardware físico.

## Etapa 8 — Revisão

Verificar o diff e confirmar que nenhuma
regra operacional foi alterada.

---

# 25. TESTES OBRIGATÓRIOS

## Teste 01 — Validar os nove prefixos

Testar individualmente:

    445543
    474143
    47574D
    484C44
    4A4554
    4D5743
    4F4D44
    534143
    424D57

Resultado esperado:

    Todos autorizados.

Utilizar EPCs completos contendo esses prefixos.

## Teste 02 — EPC autorizado

Entrada:

    484C44303430313237333134

Resultado:

    EPC autorizado.
    Continua para processamento.

## Teste 03 — EPC não autorizado

Entrada:

    313233343536373839303132

Resultado:

    EPC rejeitado.
    Nenhuma consulta HTTP.
    Nenhuma atualização de contador.
    Nenhuma linha na tabela.

## Teste 04 — Minúsculas

Entrada:

    484c44303430313237333134

Resultado:

    EPC autorizado.

## Teste 05 — Prefixo incompleto

Entrada:

    484C4

Resultado:

    EPC rejeitado como inválido.

## Teste 06 — EPC inválido

Entrada:

    ZZZZZZ303030303030303030

Resultado:

    EPC inválido.
    Nenhum processamento.

## Teste 07 — Filtro desabilitado

Configuração:

    enabled = false

Entrada:

    EPC válido com prefixo não cadastrado.

Resultado:

    EPC continua para o processamento existente.

## Teste 08 — Prefixo duplicado

Tentar cadastrar:

    484C44

Duas vezes.

Resultado:

    Duplicidade não aceita.

## Teste 09 — Prefixo inválido

Tentar cadastrar:

    484C4G

Resultado:

    Salvamento rejeitado.
    Configuração anterior preservada.

## Teste 10 — Persistência

Adicionar um novo prefixo válido.

Salvar.

Fechar e reabrir o software.

Resultado:

    Prefixo permanece cadastrado.

## Teste 11 — Remoção

Remover um prefixo.

Salvar.

Iniciar novo inventário.

Resultado:

    EPCs desse prefixo deixam de ser autorizados.

## Teste 12 — EPC encontrado

Entrada:

    Prefixo autorizado.
    HTTP 200.
    Status pendente.

Resultado:

    EPC encontrado.
    Fluxo normal preservado.

## Teste 13 — Extra Box não cadastrado

Entrada:

    Prefixo autorizado.
    HTTP 404.

Resultado:

    Extra Box contabilizado.
    Linha amarela apresentada na tabela.

## Teste 14 — Extra Box já lido

Entrada:

    Prefixo autorizado.
    HTTP 200.
    Status lido anteriormente.

Resultado:

    Extra Box contabilizado.
    Linha amarela apresentada na tabela.

## Teste 15 — EPC não autorizado e HTTP 404

Entrada:

    Prefixo não autorizado.

Resultado:

    Nenhuma requisição HTTP realizada.
    Nenhum Extra Box contabilizado.

## Teste 16 — Deduplicação

Entrada:

    Mesmo EPC autorizado recebido
    múltiplas vezes.

Resultado:

    Deduplicação atual preservada.

## Teste 17 — Múltiplas leituras

Simular centenas ou milhares de callbacks
contendo EPCs autorizados e não autorizados.

Resultado:

    Apenas os autorizados continuam.
    Sem degradação relevante no processamento.
    Sem consultas HTTP para EPCs rejeitados.

## Teste 18 — Alteração durante inventário

Iniciar inventário.

Alterar a configuração do filtro.

Salvar.

Resultado:

    Inventário atual utiliza a configuração
    capturada no início.

    Próximo inventário utiliza os novos valores.

## Teste 19 — Configuração ausente

Inicializar o software sem configuração
prévia de filtro, preservando as demais
configurações quando existirem.

Resultado:

    Filtro habilitado.
    Nove prefixos iniciais carregados.

## Teste 20 — Configuração corrompida

Simular lista inválida no arquivo persistido.

Resultado:

    Erro identificado.
    Nenhum inventário iniciado com
    política de filtragem inconsistente.

## Teste 21 — Regressão operacional

Validar:

- Iniciar leitura.
- Parar leitura.
- DI1.
- DI2.
- Timer de 60 segundos.
- CH1.
- CH2.
- CH3.
- GET de EPC.
- POST de passagem.
- Deduplicação.
- Contadores.
- Extra Box.
- Tabela.
- Indicadores de conexão.

Nenhum comportamento operacional deverá regredir.

---

# 26. CRITÉRIOS DE ACEITE

- [ ] Filtro implementado em Python.
- [ ] Leitura sllurp preservada.
- [ ] Nenhum pré-filtro LLRP implementado.
- [ ] Comparação dos primeiros 6 caracteres hexadecimais.
- [ ] Nove prefixos iniciais cadastrados corretamente.
- [ ] EPCs autorizados seguem o processamento normal.
- [ ] EPCs não autorizados são ignorados.
- [ ] EPCs rejeitados não consultam o Backend.
- [ ] EPCs rejeitados não são contabilizados.
- [ ] EPCs rejeitados não aparecem na tabela.
- [ ] EPCs rejeitados não geram POST.
- [ ] Extra Box funciona somente com EPCs autorizados.
- [ ] Filtro pode ser habilitado e desabilitado.
- [ ] Prefixos podem ser adicionados.
- [ ] Prefixos podem ser removidos.
- [ ] Validação impede prefixos inválidos.
- [ ] Duplicidades não são permitidas.
- [ ] Configuração salva localmente.
- [ ] Configuração recuperada após reinicialização.
- [ ] Configurações existentes preservadas.
- [ ] Alterações durante leitura não afetam o inventário ativo.
- [ ] Interface segue o tema Corporate Dark.
- [ ] Nenhuma alteração no Backend.
- [ ] Nenhuma alteração no protocolo LLRP.
- [ ] Sensores e relés preservados.
- [ ] Timer de 60 segundos preservado.
- [ ] RF019 e RF022 preservados.
- [ ] Testes automatizados aprovados.
- [ ] Sem regressões operacionais.

---

# 27. FORA DO ESCOPO

Não implementar:

- Pré-filtros no Zebra FX9600.
- Comandos LLRP Select.
- Alterações internas na biblioteca sllurp.
- Mudanças de potência das antenas.
- Alterações no protocolo RFID.
- Novos endpoints Rails.
- Modificações no PostgreSQL.
- Persistência adicional de EPCs.
- Novos cards no Dashboard.
- Contador de etiquetas rejeitadas.
- Exibição de EPCs rejeitados.
- Alterações na lógica Extra Box.
- Alterações na lógica dos sensores.
- Alterações nos relés.
- Alterações no timer.
- Refatoração ampla da aplicação.

---

# 28. RELATÓRIO FINAL OBRIGATÓRIO

Após a implementação, apresentar:

1. Branch utilizada.
2. Arquivos modificados.
3. Serviço responsável pelo filtro.
4. Ponto exato onde o filtro foi integrado.
5. Estrutura utilizada para comparação.
6. Comportamento do filtro habilitado.
7. Comportamento do filtro desabilitado.
8. Implementação da tela de configuração.
9. Local de persistência.
10. Tratamento de configurações inválidas.
11. Tratamento de alterações durante inventário.
12. Integração com RF019 e RF022.
13. Testes criados.
14. Testes executados.
15. Resultados dos testes.
16. Eventuais limitações.
17. Confirmação de que o LLRP não foi modificado.
18. Confirmação de que os sensores e relés foram preservados.

Não realizar commit ou merge automaticamente.

---

# 29. DEFINIÇÃO DE PRONTO

O RF023 estará concluído quando o software RFID
permitir cadastrar uma lista de prefixos autorizados
e utilizar essa configuração para filtrar os EPCs
recebidos pelo Zebra FX9600.

O filtro deverá:

- Ser executado no Python.
- Utilizar os primeiros 6 caracteres hexadecimais.
- Permitir configurar múltiplos prefixos.
- Ser habilitado ou desabilitado.
- Persistir suas configurações.
- Ignorar EPCs não autorizados antes de qualquer
  processamento operacional.
- Preservar a classificação Extra Box.
- Preservar o funcionamento da aplicação.

O Zebra FX9600 continuará inventariando
normalmente todas as etiquetas presentes
no campo das antenas.

A seleção das etiquetas autorizadas será
responsabilidade exclusiva do software Python.

**IMPLEMENTAR O RF023 COMPLETO, PRIORIZANDO
SIMPLICIDADE, PERFORMANCE, FLEXIBILIDADE
E PRESERVAÇÃO DA ARQUITETURA EXISTENTE.**