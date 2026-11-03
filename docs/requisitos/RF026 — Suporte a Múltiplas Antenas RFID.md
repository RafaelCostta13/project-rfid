# RF026 — Suporte a Múltiplas Antenas RFID

**Projeto:** RFID System
**Requisito:** RF026
**Categoria:** Funcionalidade / Integração RFID
**Prioridade:** Alta
**Tecnologia:** Python + PySide6 + QML
**Leitor:** Zebra FX9600
**Protocolo:** LLRP
**Biblioteca:** sllurp
**Sistema operacional:** Windows
**Status:** A implementar

---

# 1. OBJETIVO

Implementar suporte ao uso simultâneo de múltiplas
antenas RFID conectadas ao leitor Zebra FX9600.

Atualmente, o software permite configurar vários
IDs de antena, porém utiliza somente a primeira
antena da lista durante a execução.

O RF026 deverá corrigir essa limitação.

O sistema deverá utilizar todas as antenas
configuradas durante o mesmo inventário RFID.

Configuração inicial obrigatória:

    RFID_ANTENNAS=1,2

O software deverá continuar compatível com:

    RFID_ANTENNAS=1

IMPORTANTE:

Não implementar múltiplas conexões LLRP para
utilizar múltiplas antenas do mesmo leitor.

As antenas deverão ser configuradas na conexão
LLRP existente por meio da biblioteca sllurp.

---

# 2. CONTEXTO ATUAL DO PROJETO

O software utiliza:

- Python.
- PySide6 + QML.
- Zebra FX9600.
- Biblioteca sllurp.
- Protocolo LLRP.
- Waveshare Modbus RTU Relay.
- Backend Rails API.
- Sistema Windows.

O leitor Zebra FX9600 possui portas físicas
para conexão de múltiplas antenas RFID.

A aplicação utiliza inventário automático
controlado pelos sensores DI1 e DI2.

Fluxo operacional atual:

1. Operador habilita o modo automático.
2. Sistema aguarda a interrupção de DI1.
3. Inventário RFID é iniciado.
4. EPCs são recebidos pelo software.
5. Filtro de prefixos EPC é aplicado.
6. EPCs autorizados seguem para processamento.
7. Backend é consultado.
8. Etiquetas são classificadas.
9. Contadores e tabela são atualizados.
10. Inventário encerra por DI2 ou timeout.

O RF026 deverá preservar integralmente
esse fluxo operacional.

---

# 3. SITUAÇÃO ATUAL IDENTIFICADA PELO CODEX

A variável de ambiente já aceita uma lista
de antenas.

Exemplo:

    RFID_ANTENNAS=1,2

O processamento dessa configuração está
implementado em:

    src/rfid_reader/config.py

Entretanto, o runtime utiliza somente:

    settings.antennas[0]

Isso significa que apenas o primeiro ID
configurado é encaminhado ao serviço RFID.

Além disso, a classe:

    ZebraFX9600Reader

Recebe atualmente apenas:

    antenna_id

A configuração enviada ao sllurp utiliza:

    "antennas": [antenna_id]

Esse comportamento deverá ser alterado.

O objetivo é encaminhar a lista completa
de IDs configurados.

---

# 4. RF026.01 — CONFIGURAÇÃO DE MÚLTIPLAS ANTENAS

O software deverá aceitar:

    RFID_ANTENNAS=1

E:

    RFID_ANTENNAS=1,2

Também deverá preservar a capacidade existente
de configurar outros conjuntos de IDs válidos,
conforme a validação de configuração atual.

A quantidade de antenas utilizáveis dependerá
da capacidade e da configuração física do leitor.

Não limitar artificialmente a implementação
a apenas duas antenas.

A validação inicial obrigatória será
realizada com as antenas 1 e 2.

---

# 5. RF026.02 — PRESERVAR O PARSER EXISTENTE

Localizar:

    src/rfid_reader/config.py

Verificar como a variável:

    RFID_ANTENNAS

É convertida para a lista interna:

    settings.antennas

Preservar as validações já implementadas.

A configuração:

    RFID_ANTENNAS=1,2

Deverá produzir uma sequência equivalente a:

    [1, 2]

Não interpretar:

    "1,2"

Como um único identificador.

Não alterar desnecessariamente o parser
se ele já realiza essa conversão corretamente.

---

# 6. RF026.03 — ALTERAR O RUNTIME

Localizar o ponto do runtime que utiliza:

    settings.antennas[0]

Modificar o encaminhamento para utilizar
toda a lista de antenas configuradas.

Comportamento atual:

    antenna_id = settings.antennas[0]

Comportamento desejado:

    antenna_ids = settings.antennas

Os nomes são conceituais.

Adaptar à arquitetura e aos padrões
do código existente.

Requisitos:

1. Preservar todos os IDs configurados.
2. Preservar a ordem da configuração.
3. Não selecionar apenas a primeira antena.
4. Não adicionar antenas que não foram configuradas.
5. Não duplicar IDs.
6. Não modificar outras configurações do leitor.

O runtime deverá encaminhar a lista completa
ao ZebraFX9600Reader.

---

# 7. RF026.04 — MODIFICAR ZebraFX9600Reader

Localizar a classe:

    ZebraFX9600Reader

Atualmente, ela recebe um único:

    antenna_id

Modificar sua interface para aceitar
múltiplos identificadores.

Sugestão:

    antenna_ids

Exemplo conceitual:

    ZebraFX9600Reader(
        ...,
        antenna_ids=[1, 2]
    )

Os demais argumentos deverão permanecer
compatíveis com a implementação atual.

A classe deverá trabalhar internamente
com uma coleção de IDs de antenas.

Requisitos:

- Aceitar uma única antena.
- Aceitar múltiplas antenas.
- Validar ou reutilizar a validação dos IDs.
- Preservar os IDs recebidos.
- Não modificar parâmetros não relacionados.
- Não alterar o ciclo de conexão e desconexão.

Avaliar os pontos do código que ainda
dependem da variável singular antenna_id.

Adaptar somente os trechos necessários.

Não criar uma segunda classe para
múltiplas antenas.

Não duplicar o serviço de leitura RFID.

---

# 8. RF026.05 — CONFIGURAÇÃO DO SLLURP

A configuração do sllurp deverá utilizar
a lista completa de antenas.

Comportamento atual:

    "antennas": [antenna_id]

Novo comportamento:

    "antennas": [1, 2]

Implementação conceitual:

    config = LLRPReaderConfig({
        ...
        "antennas": list(antenna_ids),
        ...
    })

O código acima é apenas uma referência.

Preservar todas as outras opções da
configuração LLRP existente.

Não modificar:

- Potência de transmissão.
- Sensibilidade de recepção.
- Região regulatória.
- Configurações de frequência.
- Parâmetros de inventário existentes.
- Configurações específicas do hardware.

A única alteração funcional solicitada
na configuração LLRP é permitir
a utilização dos múltiplos IDs.

---

# 9. RF026.06 — CONEXÃO LLRP

A aplicação deverá continuar utilizando
uma única conexão com o Zebra FX9600.

Exemplo conceitual:

    Software Python
           |
           v
    Conexão LLRP
           |
           v
       FX9600
           |
       +---+---+
       |       |
       v       v
    Antena 1 Antena 2
       |       |
       +---+---+
           |
           v
    Relatórios RFID
           |
           v
    Processamento existente

Não criar:

- Uma conexão LLRP por antena.
- Uma instância independente do reader
  para cada antena física.
- Threads adicionais para cada antena,
  sem necessidade técnica comprovada.

O inventário deverá utilizar as antenas
configuradas por meio do mesmo leitor.

Observação:

O Zebra FX9600 poderá administrar os ciclos
de transmissão de cada porta conforme
seu funcionamento interno.

O requisito não exige transmissão RF
fisicamente simultânea nas duas portas.

Exige que ambas participem do mesmo
inventário e possam produzir leituras.

---

# 10. RF026.07 — IDENTIFICAÇÃO DA ANTENA

Os relatórios RFID deverão continuar
informando a antena de origem.

Preservar o campo LLRP:

    AntennaID

Exemplo conceitual:

    EPC A
    AntennaID = 1

    EPC B
    AntennaID = 2

O software deverá manter a identificação
correta de cada leitura.

Não atribuir automaticamente:

    antenna_id = 1

A todos os EPCs recebidos.

Não substituir o AntennaID reportado
pela primeira antena configurada.

Não inferir a antena apenas pela configuração.

Utilizar o identificador efetivamente
retornado pelo relatório RFID.

---

# 11. RF026.08 — PROCESSAMENTO DOS RELATÓRIOS

Verificar como o sllurp encaminha
os relatórios de etiquetas ao software.

A implementação deverá preservar:

- EPC.
- Reader ID.
- Antenna ID.
- Demais informações já utilizadas.

O software deverá aceitar relatórios
originados de qualquer antena configurada.

Exemplo:

    EPC A -> Antena 1
    EPC B -> Antena 2
    EPC C -> Antena 1
    EPC D -> Antena 2

Todos deverão seguir o fluxo de
processamento existente.

IMPORTANTE:

Não descartar uma leitura válida
apenas porque sua antena não é a
primeira da lista configurada.

---

# 12. RF026.09 — DEDUPLICAÇÃO

Preservar integralmente a regra
de deduplicação existente.

Chave atual informada pelo Codex:

    reader_id + antenna_id + epc

Essa chave deverá continuar sendo utilizada
nos componentes onde já está implementada.

Exemplo:

    Reader: FX9600
    Antena: 1
    EPC: ABC123

Chave:

    FX9600 + 1 + ABC123

Outro relatório:

    Reader: FX9600
    Antena: 2
    EPC: ABC123

Chave:

    FX9600 + 2 + ABC123

Essas leituras possuem origens distintas.

Não remover antenna_id da chave existente.

Não substituir a chave por somente EPC.

Não modificar silenciosamente as regras
de deduplicação da sessão.

ATENÇÃO:

A deduplicação por antena e a deduplicação
de negócio podem existir em camadas diferentes.

Um mesmo EPC poderá ser identificado
por duas antenas durante a mesma sessão.

Preservar as regras atuais de contagem,
consulta, registro e classificação.

Não implementar novos POSTs duplicados
ou novas contagens indevidas como consequência
da ativação das múltiplas antenas.

Se for encontrada uma inconsistência entre
a deduplicação por antena e a deduplicação
por sessão, documentar o comportamento
e informar o impacto no relatório final.

Não realizar refatorações amplas das regras
de deduplicação dentro deste requisito.

---

# 13. RF026.10 — INTEGRAÇÃO COM FILTRO EPC

Preservar o RF023.

O software utiliza os primeiros 6 caracteres
hexadecimais do EPC para identificar os
prefixos autorizados.

Esse filtro deverá continuar funcionando
independentemente da antena de origem.

Exemplo:

    Antena 1 -> EPC autorizado
    Antena 2 -> EPC autorizado
    Antena 1 -> EPC não autorizado
    Antena 2 -> EPC não autorizado

Resultado esperado:

    EPCs autorizados seguem o processamento.

    EPCs não autorizados são ignorados.

Não criar listas de prefixos diferentes
para cada antena.

Não alterar os prefixos configurados.

Não modificar a lógica de filtragem existente.

---

# 14. RF026.11 — INTEGRAÇÃO COM BACKEND

Preservar os endpoints:

    GET /api/v1/rfid_records/:epc

    POST /api/v1/rfid_reads

As leituras provenientes das diferentes
antenas deverão utilizar o fluxo
de integração atual.

Exemplo:

    Antena 1
       |
       v
    EPC autorizado
       |
       v
    Consulta Backend

    Antena 2
       |
       v
    EPC autorizado
       |
       v
    Consulta Backend

Não criar endpoints específicos por antena.

Não modificar o JSON das requisições.

Não alterar os contratos HTTP.

Não modificar o Backend Rails.

Não realizar migrations.

---

# 15. RF026.12 — INTEGRAÇÃO COM EXTRA BOX

Preservar RF019 e RF022.

Leituras originadas de qualquer antena
configurada poderão ser classificadas como:

    EPC encontrado

Ou:

    Extra Box

Conforme as regras atuais.

Exemplos:

    Antena 1
    EPC pendente
    Resultado: Encontrado

    Antena 2
    EPC previamente lido
    Resultado: Extra Box

    Antena 2
    EPC não cadastrado
    Resultado: Extra Box

Não alterar a lógica de classificação.

Não adicionar novos contadores por antena.

Não criar novas categorias de Extra Box.

Não alterar a apresentação visual da tabela.

---

# 16. RF026.13 — PRESERVAÇÃO DA TABELA QML

O Dashboard deverá continuar apresentando
as informações normalmente.

Estrutura existente:

    Status
    Fornecedor
    Tag
    Nota fiscal
    Volume
    Pedido
    Doca

As etiquetas lidas por ambas as antenas
deverão aparecer na tabela conforme
as regras atuais.

Não adicionar uma coluna Antena neste requisito.

Não alterar:

- Ordenação das colunas.
- Layout.
- Largura das colunas.
- Cores.
- Cards.
- Sidebar.
- Status OK.
- Status Extra Box.
- Destaque amarelo.
- Atualização em tempo real.

A identificação da antena deverá permanecer
disponível internamente, sem necessidade
de exposição adicional na interface.

---

# 17. RF026.14 — LOGS

Atualizar os logs para apresentar
as antenas configuradas e utilizadas.

Exemplo:

    RFID Reader: Zebra FX9600
    Configured antennas: [1, 2]

Ao iniciar o inventário:

    Starting RFID inventory
    Antennas: [1, 2]

Ao encerrar:

    RFID inventory stopped

Os exemplos representam o conteúdo esperado,
não um formato obrigatório.

Utilizar o mecanismo de logging existente.

Não utilizar print em produção caso
o projeto já possua um logger.

Não gerar uma mensagem repetitiva
a cada leitura de etiqueta.

Quando necessário, registrar a antena
de origem em nível DEBUG.

Exemplo:

    EPC received
    AntennaID: 2

Não registrar volumes excessivos
de logs durante inventários intensos.

---

# 18. RF026.15 — TRATAMENTO DE ANTENAS INDISPONÍVEIS

A configuração de múltiplas antenas depende
da disponibilidade física do equipamento.

Exemplo:

    RFID_ANTENNAS=1,2

Porém apenas a antena 1 está conectada.

O comportamento dependerá da resposta
do Zebra FX9600 e da configuração do leitor.

O software deverá:

1. Encaminhar corretamente os IDs configurados.
2. Interpretar erros retornados pelo sllurp/LLRP.
3. Registrar informações úteis para diagnóstico.
4. Não ocultar falhas de configuração.
5. Não substituir silenciosamente [1, 2] por [1].
6. Não informar que ambas estão funcionando
   sem evidência de funcionamento.

Se o leitor rejeitar a configuração:

    Apresentar a falha usando o mecanismo
    de erro existente.

Se o leitor aceitar a configuração,
mas uma antena não produzir leituras:

    Não concluir automaticamente que
    existe falha de hardware.

A ausência de leituras não comprova,
isoladamente, defeito ou desconexão.

Não implementar neste requisito
um novo sistema de diagnóstico
físico de antenas.

---

# 19. RF026.16 — COMPATIBILIDADE

Preservar a configuração anterior:

    RFID_ANTENNAS=1

Resultado esperado:

    Uma única antena configurada.

Também suportar:

    RFID_ANTENNAS=1,2

Resultado esperado:

    Duas antenas configuradas.

A alteração não poderá exigir modificações
no arquivo de configuração de instalações
que já utilizam uma única antena.

Preservar a estrutura existente da aplicação.

Avaliar os pontos de instanciação do
ZebraFX9600Reader para evitar quebra
dos consumidores internos.

Não criar APIs paralelas desnecessárias.

---

# 20. RF026.17 — PRESERVAÇÃO DO FLUXO OPERACIONAL

O RF026 não poderá alterar o funcionamento
dos sensores e relés.

Estados existentes:

## Pronto

    CH1 ON
    CH2 OFF
    CH3 OFF

## Leitura

    CH1 OFF
    CH2 ON
    CH3 OFF

## Erro operacional

    CH1 OFF
    CH2 OFF
    CH3 ON

Preservar o comportamento definido
pelos requisitos anteriores.

O botão Iniciar leitura continuará
habilitando o modo automático.

O inventário deverá aguardar DI1.

Quando DI1 for interrompido,
o sistema iniciará o inventário utilizando
todas as antenas configuradas.

Quando DI2 determinar o encerramento
ou ocorrer o timeout de 60 segundos,
o inventário deverá ser interrompido
para todas as antenas.

Não deixar inventários ativos
em antenas individuais após o encerramento.

Não criar timers independentes por antena.

Não modificar a máquina de estados.

---

# 21. RF026.18 — CICLO DE VIDA

O uso de múltiplas antenas deverá
respeitar o ciclo de vida atual:

    Configuração
         |
         v
    Conexão FX9600
         |
         v
    Modo automático habilitado
         |
         v
    Aguardando DI1
         |
         v
    Inventário com antenas [1, 2]
         |
         v
    Recebimento dos relatórios
         |
         v
    Processamento RFID
         |
         v
    DI2 ou timeout
         |
         v
    Encerramento do inventário

A conexão LLRP deverá continuar
sendo gerenciada pelo serviço existente.

Não abrir ou fechar conexões individualmente
para cada antena.

---

# 22. RF026.19 — ANÁLISE OBRIGATÓRIA

Antes de modificar o código:

1. Ler AGENTS.md.
2. Confirmar a branch atual.
3. Executar git status -sb.
4. Localizar src/rfid_reader/config.py.
5. Verificar a leitura de RFID_ANTENNAS.
6. Localizar settings.antennas[0].
7. Localizar ZebraFX9600Reader.
8. Identificar o construtor atual.
9. Localizar a criação de LLRPReaderConfig.
10. Identificar o campo antennas do sllurp.
11. Localizar o recebimento de AntennaID.
12. Localizar a deduplicação existente.
13. Identificar o início do inventário.
14. Identificar o encerramento do inventário.
15. Localizar os testes existentes.

Pesquisar outros usos de:

    antenna_id

    antennas[0]

    AntennaID

    "antennas"

Identificar todos os pontos que possam
pressupor a existência de apenas uma antena.

Não limitar a análise somente aos arquivos
informados neste requisito.

---

# 23. RF026.20 — ESTRATÉGIA DE IMPLEMENTAÇÃO

## Etapa 1 — Configuração

Verificar o parser atual.

Preservar a lista de antenas.

## Etapa 2 — Runtime

Remover a seleção exclusiva
da primeira antena.

Encaminhar toda a lista configurada.

## Etapa 3 — Reader

Adaptar ZebraFX9600Reader para
receber múltiplos IDs.

## Etapa 4 — sllurp

Configurar a lista completa:

    "antennas": [1, 2]

## Etapa 5 — Relatórios

Preservar o AntennaID real
de cada leitura recebida.

## Etapa 6 — Deduplicação

Confirmar que reader_id,
antenna_id e epc permanecem
disponíveis corretamente.

## Etapa 7 — Logs

Adicionar informações das antenas
utilizadas na conexão e no inventário.

## Etapa 8 — Testes

Executar testes unitários
e integração simulada.

## Etapa 9 — Revisão

Verificar se a mudança permanece
restrita ao suporte a múltiplas antenas.

---

# 24. TESTES OBRIGATÓRIOS

## Teste 01 — Uma antena

Configuração:

    RFID_ANTENNAS=1

Resultado esperado:

    settings.antennas = [1]

    Configuração sllurp:
    "antennas": [1]

O comportamento anterior deverá
continuar funcionando.

---

## Teste 02 — Duas antenas

Configuração:

    RFID_ANTENNAS=1,2

Resultado esperado:

    settings.antennas = [1, 2]

    Configuração sllurp:
    "antennas": [1, 2]

Ambos os IDs deverão ser encaminhados.

---

## Teste 03 — Lista não truncada

Entrada:

    [1, 2]

Verificar que o runtime não utiliza
somente:

    settings.antennas[0]

Resultado esperado:

    Lista completa preservada.

---

## Teste 04 — Instanciação do reader

Criar uma instância simulada de
ZebraFX9600Reader com:

    antenna_ids=[1, 2]

Resultado esperado:

    IDs preservados.

---

## Teste 05 — Construção da configuração LLRP

Simular a criação da configuração sllurp.

Resultado esperado:

    antennas = [1, 2]

Confirmar que nenhuma outra opção
de inventário foi modificada indevidamente.

---

## Teste 06 — Relatório da antena 1

Simular:

    EPC = ABC123
    AntennaID = 1

Resultado esperado:

    EPC recebido.
    AntennaID preservado como 1.

---

## Teste 07 — Relatório da antena 2

Simular:

    EPC = DEF456
    AntennaID = 2

Resultado esperado:

    EPC recebido.
    AntennaID preservado como 2.

---

## Teste 08 — EPC em duas antenas

Simular:

    Reader = FX9600
    AntennaID = 1
    EPC = ABC123

E:

    Reader = FX9600
    AntennaID = 2
    EPC = ABC123

Resultado esperado:

    A camada de deduplicação por antena
    diferencia as duas origens.

    O processamento de negócio mantém
    suas regras atuais por sessão.

Verificar que isso não introduz
contagens ou registros duplicados indevidos.

---

## Teste 09 — Deduplicação na mesma antena

Simular:

    Reader = FX9600
    AntennaID = 1
    EPC = ABC123

Repetir o mesmo relatório.

Resultado esperado:

    Deduplicação existente preservada.

---

## Teste 10 — Filtro EPC

Simular:

    Antena 1 -> Prefixo autorizado.
    Antena 2 -> Prefixo autorizado.
    Antena 2 -> Prefixo não autorizado.

Resultado esperado:

    Apenas EPCs autorizados seguem
    o processamento de negócio.

---

## Teste 11 — Consulta Backend

Simular EPCs distintos originados
das antenas 1 e 2.

Resultado esperado:

    Ambos seguem o fluxo normal
    de consulta ao Backend.

---

## Teste 12 — Extra Box

Simular:

    Antena 1 -> EPC encontrado.
    Antena 2 -> EPC não cadastrado.
    Antena 2 -> EPC previamente lido.

Resultado esperado:

    Classificação existente preservada.

    Contadores consistentes.

    Tabela atualizada conforme
    os requisitos anteriores.

---

## Teste 13 — Start

Iniciar o modo automático.

Interromper DI1 em ambiente simulado.

Resultado esperado:

    Inventário iniciado com a
    lista completa de antenas.

---

## Teste 14 — Stop

Encerrar o inventário.

Resultado esperado:

    Operação encerrada para
    todas as antenas configuradas.

    Nenhuma conexão ou operação
    residual indevida.

---

## Teste 15 — Timeout

Simular encerramento após
60 segundos.

Resultado esperado:

    Inventário interrompido.

    Máquina de estados preservada.

---

## Teste 16 — Configuração inválida

Simular configuração de antena inválida
conforme as regras do parser atual.

Resultado esperado:

    Validação existente preservada.

    Erro tratado adequadamente.

---

## Teste 17 — Falha retornada pelo leitor

Simular rejeição da configuração LLRP
pelo reader.

Resultado esperado:

    Erro identificado e registrado.

    Sem substituição silenciosa
    da lista configurada.

---

## Teste 18 — Logs

Configuração:

    RFID_ANTENNAS=1,2

Resultado esperado:

    Logs informam as antenas [1, 2].

---

## Teste 19 — Regressão

Executar os testes existentes de:

- Configuração RFID.
- Conexão LLRP.
- Inventário.
- Deduplicação.
- Filtro EPC.
- Consulta Backend.
- Registro de passagem.
- Extra Box.
- Start/Stop.
- Sensores.
- Relés.
- Qt Bridge.

Resultado esperado:

    Nenhuma regressão introduzida.

---

# 25. VALIDAÇÃO COM HARDWARE REAL

Após os testes automatizados,
realizar validação com:

    Zebra FX9600

    Antena física 1 conectada.

    Antena física 2 conectada.

Configuração:

    RFID_ANTENNAS=1,2

Procedimento:

1. Confirmar conexão LLRP.
2. Confirmar que as portas selecionadas
   estão disponíveis e habilitadas.
3. Iniciar inventário normalmente.
4. Aproximar uma etiqueta da antena 1.
5. Confirmar recebimento com AntennaID 1.
6. Aproximar outra etiqueta da antena 2.
7. Confirmar recebimento com AntennaID 2.
8. Testar as duas antenas no mesmo inventário.
9. Verificar processamento dos EPCs autorizados.
10. Verificar classificação de Extra Box.
11. Verificar encerramento por DI2.
12. Verificar encerramento por timeout.

IMPORTANTE:

Os testes automatizados não substituem
a validação física.

O Codex deverá informar explicitamente
se não possui acesso ao hardware necessário.

Não afirmar que a validação com duas
antenas físicas foi concluída caso
apenas simulações tenham sido executadas.

---

# 26. CRITÉRIOS DE ACEITE

- [ ] RFID_ANTENNAS=1 continua funcionando.
- [ ] RFID_ANTENNAS=1,2 é aceito.
- [ ] Parser existente preservado.
- [ ] Runtime encaminha a lista completa.
- [ ] ZebraFX9600Reader aceita múltiplos IDs.
- [ ] sllurp recebe antennas=[1, 2].
- [ ] Uma única conexão LLRP é utilizada.
- [ ] Antena 1 produz relatórios válidos.
- [ ] Antena 2 produz relatórios válidos.
- [ ] AntennaID é preservado.
- [ ] Reader ID é preservado.
- [ ] EPC é preservado.
- [ ] Deduplicação existente é preservada.
- [ ] Leituras de ambas as antenas seguem o processamento.
- [ ] Filtro de prefixos funciona em ambas.
- [ ] Backend continua funcionando.
- [ ] Extra Box continua funcionando.
- [ ] Tabela QML permanece inalterada.
- [ ] Logs informam as antenas utilizadas.
- [ ] Erros LLRP são tratados corretamente.
- [ ] Não há fallback silencioso para uma antena.
- [ ] Timer de 60 segundos preservado.
- [ ] Start/Stop preservados.
- [ ] Sensores preservados.
- [ ] Relés preservados.
- [ ] Potência do leitor não é alterada.
- [ ] Região regulatória não é alterada.
- [ ] Configurações persistentes do reader não são alteradas.
- [ ] Testes unitários aprovados.
- [ ] Testes de integração simulada aprovados.
- [ ] Situação da validação física informada explicitamente.

---

# 27. FORA DO ESCOPO

Não implementar:

- Configuração gráfica de antenas.
- Controle individual de potência.
- Potência diferente por antena.
- Configurações de região regulatória.
- Seleção de frequência.
- Novos filtros LLRP.
- Múltiplas conexões ao mesmo leitor.
- Múltiplos leitores RFID.
- Novos indicadores de antena no Dashboard.
- Nova coluna Antena na tabela.
- Novos endpoints Backend.
- Alterações no PostgreSQL.
- Novos contadores por antena.
- Alterações na classificação Extra Box.
- Alterações no filtro RF023.
- Alterações no controle de sensores.
- Alterações nos relés.
- Alterações no timer.
- Refatoração ampla do projeto.

---

# 28. RELATÓRIO FINAL OBRIGATÓRIO

Após implementar, apresentar:

1. Branch utilizada.
2. Arquivos modificados.
3. Alterações realizadas no runtime.
4. Alterações em ZebraFX9600Reader.
5. Configuração final enviada ao sllurp.
6. Confirmação do suporte a [1].
7. Confirmação do suporte a [1, 2].
8. Tratamento do AntennaID.
9. Preservação da deduplicação.
10. Análise do mesmo EPC visto por duas antenas.
11. Alterações nos logs.
12. Testes unitários criados.
13. Testes de integração simulada.
14. Resultados dos testes.
15. Regressões verificadas.
16. Eventuais limitações.
17. Confirmação de que a potência não foi alterada.
18. Confirmação de que a região regulatória não foi alterada.
19. Confirmação de que a configuração persistente
    do leitor não foi modificada.
20. Situação da validação com hardware real.

Caso o Zebra FX9600 com duas antenas
não esteja disponível para testes:

Informar:

    Validação automatizada concluída.

    Validação física com múltiplas
    antenas pendente.

Não realizar commit ou merge automaticamente.

---

# 29. DEFINIÇÃO DE PRONTO

O RF026 estará implementado quando:

1. O runtime encaminhar todas as antenas configuradas.
2. ZebraFX9600Reader aceitar múltiplos IDs.
3. O sllurp receber a lista completa.
4. Relatórios das diferentes antenas forem processados.
5. O AntennaID de cada leitura for preservado.
6. A deduplicação existente continuar funcionando.
7. O filtro EPC funcionar independentemente da antena.
8. O Backend e a classificação Extra Box forem preservados.
9. Os testes automatizados forem aprovados.
10. Não existirem regressões operacionais.

A implementação poderá ser considerada
tecnicamente concluída em ambiente simulado,
mas a homologação operacional dependerá
de testes com o Zebra FX9600 e as antenas
fisicamente conectadas.

IMPLEMENTAR O RF026 COMPLETO, COM SUPORTE
A MÚLTIPLAS ANTENAS, PRESERVANDO A ARQUITETURA
EXISTENTE E TODAS AS REGRAS OPERACIONAIS.