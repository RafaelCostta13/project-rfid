# RF022 — Exibição de Extra Box na Tabela RFID

**Projeto:** RFID System
**Requisito:** RF022
**Categoria:** Nova funcionalidade / Interface / UX
**Prioridade:** Alta
**Ambiente:** Windows
**Tecnologia:** Python + PySide6 + Qt Quick/QML
**Tema:** Corporate Dark
**Requisitos relacionados:** RF016, RF017, RF018, RF019 e RF020
**Status:** A implementar

---

# 1. Objetivo

Implementar a exibição das etiquetas classificadas como Extra box
na tabela principal do Dashboard RFID.

Atualmente, o sistema possui dois contadores:

- EPCs encontrados
- Extra box

Entretanto, as etiquetas Extra box são apenas contabilizadas,
não sendo apresentadas na tabela de etiquetas lidas.

O RF022 deverá modificar esse comportamento.

A partir deste requisito:

1. EPCs encontrados continuarão aparecendo na tabela.
2. EPCs classificados como Extra box também aparecerão na tabela.
3. As linhas Extra box deverão possuir um destaque amarelo discreto.
4. O contador Extra box continuará funcionando normalmente.
5. Não poderão existir registros duplicados na tabela durante a sessão.
6. Nenhuma regra operacional RFID deverá ser modificada.

IMPORTANTE:

Esta funcionalidade deverá reutilizar a classificação Extra box
já implementada no sistema.

Não criar uma segunda lógica de classificação.

---

# 2. Contexto atual

O Dashboard RFID possui:

- Card EPCs encontrados.
- Card Extra box.
- Container de inventário RFID automático.
- Botões Iniciar leitura e Parar leitura.
- Tabela de etiquetas lidas.

A tabela possui as seguintes colunas:

    Status
    Cliente
    Nota fiscal
    Volume
    Pedido
    Doca

Atualmente, apenas os registros considerados encontrados
são apresentados na tabela.

Os registros Extra box são contabilizados separadamente.

O RF022 deverá permitir que ambos os tipos sejam exibidos
na mesma tabela.

Não criar uma tabela adicional.

---

# 3. Regras de classificação

O RF022 deverá respeitar a classificação estabelecida
no RF019 e seus ajustes posteriores.

## 3.1 EPC encontrado

Condição:

    GET /api/v1/rfid_records/:epc

Resposta:

    HTTP 200

Status do registro:

    pendente

Classificação:

    EPC encontrado

Comportamento:

- Manter o fluxo operacional existente.
- Apresentar o registro na tabela.
- Utilizar a aparência visual normal.
- Preservar o registro de passagem conforme RF017.

## 3.2 Extra box — EPC não cadastrado

Condição:

    GET /api/v1/rfid_records/:epc

Resposta:

    HTTP 404

Classificação:

    Extra box

Comportamento:

- Contabilizar conforme RF019.
- Adicionar o EPC à tabela.
- Destacar a linha com amarelo discreto.
- Não executar POST de passagem para um EPC inexistente.
- Não preencher informações inexistentes com dados fictícios.

## 3.3 Extra box — EPC previamente lido

Condição:

    GET /api/v1/rfid_records/:epc

Resposta:

    HTTP 200

Status retornado:

    lido

O EPC já estava classificado como lido antes
do processamento da passagem atual.

Classificação:

    Extra box

Comportamento:

- Contabilizar conforme RF019.
- Adicionar o registro à tabela.
- Destacar a linha com amarelo discreto.
- Apresentar os dados existentes retornados pelo Backend.
- Preservar as regras atuais de registro de passagem.

IMPORTANTE:

Não confundir um EPC previamente lido com um EPC que
acabou de mudar de "pendente" para "lido" durante
a sessão atual.

Uma etiqueta processada normalmente na sessão atual
não deverá se transformar em Extra box apenas porque
o Backend atualizou seu status após o POST.

---

# 4. RF022.01 — Exibição de Extra Box

Modificar o comportamento da tabela para aceitar
registros classificados como:

    ENCONTRADO
    EXTRA_BOX

A classificação deverá ser realizada pela camada
operacional Python existente.

A tabela deverá receber os registros já classificados.

Não realizar consultas HTTP diretamente no QML.

Não implementar regras de negócio dentro dos
componentes visuais.

---

# 5. RF022.02 — Aparência das linhas Extra Box

## 5.1 Objetivo visual

As etiquetas Extra box deverão ser facilmente
identificadas pelo operador.

Entretanto, o destaque deverá ser discreto e
compatível com o tema Corporate Dark.

Não utilizar amarelo vibrante.

Não utilizar fundo amarelo puro.

Não utilizar efeitos chamativos.

## 5.2 Paleta proposta

Utilizar como referência:

    Fundo normal:
    Cor atual da tabela

    Fundo Extra box:
    #3A372C

    Fundo Extra box em hover:
    #454031

    Destaque âmbar:
    #D9B86C

    Texto principal:
    Manter a cor clara atual da aplicação

    Texto secundário:
    Manter a cor secundária atual, garantindo legibilidade

Esses valores representam a referência visual desejada.

Caso o projeto possua tokens de cores ou um sistema
centralizado de temas, integrar as novas cores a esse
sistema.

Não espalhar valores hexadecimais pelos componentes.

## 5.3 Aplicação da cor

O fundo amarelo discreto deverá ocupar toda a
largura da linha Extra box.

Não destacar apenas a célula Status.

A cor deverá acompanhar todas as colunas:

    Status
    Cliente
    Nota fiscal
    Volume
    Pedido
    Doca

A linha deverá permanecer claramente identificável
mesmo quando possuir campos vazios.

## 5.4 Identificação complementar

Além da cor, apresentar a classificação:

    Extra box

Na coluna Status.

Não depender exclusivamente da cor para identificar
um registro Extra box.

Essa identificação é importante para acessibilidade
e compreensão do operador.

---

# 6. RF022.03 — Diferenciação visual

A tabela deverá apresentar dois estilos.

## 6.1 Registro encontrado

Exemplo conceitual:

    ┌───────────┬──────────────┬─────────────┬────────┬────────┬──────┐
    │ Status    │ Cliente      │ Nota fiscal │ Volume │ Pedido │ Doca │
    ├───────────┼──────────────┼─────────────┼────────┼────────┼──────┤
    │ Lido      │ Cliente A    │ 123456      │ 1/5    │ 78910  │ D01  │
    └───────────┴──────────────┴─────────────┴────────┴────────┴──────┘

Aparência:

    Fundo normal da tabela.

## 6.2 Registro Extra box

Exemplo conceitual:

    ┌───────────┬──────────────┬─────────────┬────────┬────────┬──────┐
    │ Status    │ Cliente      │ Nota fiscal │ Volume │ Pedido │ Doca │
    ├───────────┼──────────────┼─────────────┼────────┼────────┼──────┤
    │ Extra box │ Cliente B    │ 654321      │ 2/5    │ 12345  │ D02  │
    └───────────┴──────────────┴─────────────┴────────┴────────┴──────┘

Aparência:

    Fundo âmbar escuro em toda a linha.

Os exemplos são apenas representações conceituais.

Preservar os componentes e a organização atual
da tabela QML.

---

# 7. RF022.04 — Extra Box não cadastrado

Quando o Backend retornar HTTP 404, não existirão
informações cadastrais disponíveis para o EPC.

Nesse cenário, a tabela deverá apresentar:

    Status: Extra box
    Cliente: —
    Nota fiscal: —
    Volume: —
    Pedido: —
    Doca: —

Não utilizar:

    Cliente desconhecido
    Pedido fictício
    Doca padrão
    Nota fiscal padrão

Não preencher campos com informações de outros registros.

Não utilizar a doca configurada localmente como se
fosse a doca cadastrada do EPC.

O caractere "—" representa informação indisponível.

---

# 8. RF022.05 — Identificação do EPC

Como os registros Extra box também poderão representar
etiquetas inexistentes no Backend, o operador precisa
conseguir identificar qual EPC foi lido.

Atualmente, a tabela não possui uma coluna exclusiva
para o código EPC.

Para evitar alterações desnecessárias no layout,
adotar a seguinte solução:

## 8.1 Coluna Status

Para registros Extra box, apresentar:

    Extra box

E, em uma segunda linha de texto menor, apresentar
a identificação do EPC.

Exemplo:

    Extra box
    E280691500005029EEA6A275

Utilizar tipografia secundária discreta.

Não aumentar excessivamente a altura das linhas.

Caso o EPC ultrapasse a largura disponível:

- Aplicar elisão visual.
- Disponibilizar o EPC completo em tooltip.
- Preservar o valor integral no modelo de dados.

## 8.2 Registros encontrados

Preservar o comportamento visual atual da coluna Status.

Não adicionar uma segunda linha obrigatória
a todos os registros encontrados.

## 8.3 Restrições

Não adicionar uma nova coluna EPC neste requisito.

Não modificar o formato de armazenamento do EPC.

Não converter automaticamente hexadecimal para ASCII.

Utilizar o EPC normalizado que já identifica
a etiqueta no sistema.

---

# 9. RF022.06 — Motivo do Extra Box

O sistema deverá preservar internamente a razão
pela qual o EPC foi classificado como Extra box.

Categorias:

    NOT_FOUND
    ALREADY_READ

Significados:

    NOT_FOUND:
    EPC não encontrado no Backend.

    ALREADY_READ:
    EPC encontrado com status previamente "lido".

Os nomes são sugestões.

Reutilizar os tipos ou enumerações existentes,
caso já estejam implementados.

## 9.1 Apresentação

Na coluna Status, manter:

    Extra box

O motivo poderá ser apresentado por meio de
tooltip ou texto secundário discreto.

Exemplos:

    Extra box — Não cadastrado

    Extra box — Já lido

Evitar poluição visual.

Não criar novas colunas para o motivo.

## 9.2 Preservação do status original

Não modificar o status real retornado pelo Backend.

A classificação visual Extra box deverá ser
um atributo da apresentação ou do domínio da sessão.

Não substituir o campo persistido "lido" por
"Extra box" no PostgreSQL.

---

# 10. RF022.07 — Deduplicação

A tabela deverá apresentar cada EPC distinto
apenas uma vez durante a sessão.

Exemplo:

    EPC A -> HTTP 404
    EPC A -> HTTP 404
    EPC A -> HTTP 404

Resultado:

    Extra box = 1

    Tabela:
    1 linha Extra box

Outro exemplo:

    EPC B -> HTTP 200 / status lido
    EPC B -> HTTP 200 / status lido

Resultado:

    Extra box = 1

    Tabela:
    1 linha Extra box

## Regra obrigatória

Não criar uma linha a cada callback do Zebra FX9600.

Reutilizar a deduplicação existente.

A inclusão do registro na tabela não poderá
incrementar novamente o contador.

O contador deverá continuar sendo atualizado
pela classificação operacional existente.

A tabela deverá apenas refletir essa classificação.

---

# 11. RF022.08 — Consistência entre tabela e contadores

Os cards existentes deverão continuar funcionando:

    EPCs encontrados
    Extra box

Exemplo:

    EPC A -> pendente
    EPC B -> pendente
    EPC C -> lido
    EPC D -> HTTP 404
    EPC E -> HTTP 404

Resultado esperado:

    EPCs encontrados = 2

    Extra box = 3

    Total de linhas na tabela = 5

Distribuição:

    2 linhas normais

    3 linhas destacadas em amarelo discreto

A contagem deverá considerar EPCs distintos
conforme as regras da sessão.

## Atenção

Não calcular o contador Extra box simplesmente
pela quantidade de linhas amarelas.

O contador existente deverá continuar sendo
a fonte de verdade.

A tabela deverá refletir o mesmo estado de sessão.

Se uma atualização ocorrer de maneira assíncrona,
a interface deverá convergir para valores consistentes.

---

# 12. RF022.09 — Prevenção de classificação incorreta

Considerar o seguinte cenário:

1. EPC A é consultado.
2. Backend retorna status "pendente".
3. EPC A segue o fluxo normal.
4. POST de passagem é executado.
5. Backend atualiza status para "lido".
6. Zebra identifica EPC A novamente na mesma sessão.

Resultado esperado:

    EPC A continua classificado conforme
    seu processamento original na sessão.

Não adicionar uma segunda linha Extra box.

Não incrementar Extra box.

Não duplicar a linha encontrada.

Não executar novas operações apenas para
atualizar a aparência da tabela.

Preservar a classificação já consolidada
para aquele EPC na sessão.

---

# 13. RF022.10 — Atualização da tabela em tempo real

Quando um EPC for classificado como Extra box,
a linha correspondente deverá aparecer
automaticamente na tabela.

Fluxo:

    Zebra FX9600
          |
          v
    RFID Service
          |
          v
    Application Controller
          |
          v
    Consulta Backend
          |
          v
    Classificação Extra box
          |
          v
    Atualização do estado da sessão
          |
          v
    Qt Bridge / Table Model
          |
          v
    QML Table View
          |
          v
    Nova linha destacada

Não exigir atualização manual da página.

Não recriar toda a tabela a cada leitura.

Não executar operações HTTP no QML.

Não manipular objetos QML diretamente a partir
de threads de leitura RFID.

Preservar os mecanismos de signals/slots
já utilizados no projeto.

---

# 14. RF022.11 — Modelo de dados da tabela

Analisar o modelo atual responsável pelos
registros apresentados na tabela.

Verificar se já existe suporte para:

- EPC.
- Status original.
- Classificação.
- Identificação de Extra box.
- Motivo da classificação.

Se necessário, adicionar propriedades equivalentes a:

    epc
    classification
    extra_box_reason

Os nomes são apenas referências.

Não duplicar informações que já estejam disponíveis.

## 14.1 Regras para o modelo Qt

Caso a tabela utilize QAbstractTableModel,
adicionar ou reutilizar roles apropriadas
para informar ao QML:

    É Extra box?
    Qual o motivo?
    Qual o EPC?

Preservar os roles e bindings existentes.

Emitir notificações corretas quando dados
forem inseridos ou atualizados.

Evitar reinicialização completa do modelo
para adicionar uma única linha.

---

# 15. RF022.12 — Comportamento visual da tabela

## 15.1 Linhas normais

Preservar:

- Cor atual.
- Tipografia.
- Bordas.
- Hover.
- Seleção.
- Espaçamento.

## 15.2 Linhas Extra box

Aplicar:

    Fundo âmbar escuro.
    Texto claro.
    Identificação Extra box.

O destaque deverá ocupar a linha inteira.

## 15.3 Hover

Quando o mouse passar sobre uma linha Extra box,
utilizar uma variação ligeiramente mais clara
do fundo âmbar.

Não remover a identificação visual.

## 15.4 Seleção

Caso a tabela possua seleção de linhas,
preservar esse comportamento.

Uma linha Extra box selecionada deverá
continuar distinguível das linhas normais.

A cor de seleção não poderá comprometer
a leitura do texto.

## 15.5 Contraste

Garantir contraste adequado entre:

- Fundo.
- Texto principal.
- Texto secundário.
- Indicadores de status.

Buscar contraste mínimo de 4,5:1
para textos de tamanho normal.

## 15.6 Rolagem

Preservar:

- Rolagem vertical.
- Rolagem horizontal, quando necessária.
- Cabeçalho.
- Alinhamento das colunas.
- Dimensionamento responsivo.

Não reduzir a área útil da tabela.

---

# 16. RF022.13 — Preservação do RF020

O RF020 reorganizou o Dashboard para priorizar
a tabela de etiquetas.

O RF022 deverá preservar essa estrutura.

Não modificar:

- Header.
- Logotipo DSV.
- Indicadores de conexão.
- Sidebar retrátil.
- Botão de expansão da sidebar.
- Navegação Start/Configurações.
- Seletor de tema.
- Cards de contabilização.
- Botões de inventário.
- Dimensionamento principal da tabela.

A nova funcionalidade deverá ser incorporada
à tabela já existente.

Não criar um segundo componente de tabela.

---

# 17. RF022.14 — Preservação do Backend

O RF022 não exige alterações no Backend Rails.

Continuar utilizando:

    GET /api/v1/rfid_records/:epc

Preservar:

    POST /api/v1/rfid_reads

O comportamento de registro de passagem deverá
continuar obedecendo ao RF017 e às regras
operacionais atualmente implementadas.

Não criar POST para EPC inexistente.

Não alterar os contratos HTTP.

Não criar migrations.

Não criar novas tabelas no PostgreSQL.

Não adicionar armazenamento local.

Não criar novos endpoints.

A classificação Extra box continuará sendo
gerenciada pelo software RFID.

---

# 18. RF022.15 — Tratamento de erros

Não criar linhas Extra box para falhas técnicas.

## HTTP 500

    Não classificar como Extra box.
    Preservar tratamento atual.

## Timeout

    Não classificar como Extra box.
    Preservar tratamento atual.

## Falha de conexão

    Não classificar como Extra box.
    Preservar tratamento atual.

## Resposta inválida

    Não classificar automaticamente como Extra box.
    Preservar tratamento atual.

## EPC inválido

    Preservar validação existente.
    Não contabilizar indevidamente.

Apenas classificações confirmadas pelo fluxo
operacional poderão produzir linhas Extra box.

---

# 19. RF022.16 — Ciclo de vida da sessão

A tabela deverá acompanhar o ciclo de vida
já estabelecido para a sessão RFID.

Verificar:

- Início da sessão.
- Reinicialização dos contadores.
- Início do inventário.
- Encerramento pelo DI2.
- Encerramento pelo timeout.
- Acionamento de Stop.
- Navegação entre páginas.
- Reconexão dos serviços.

Os registros Extra box deverão seguir
a mesma política de retenção e limpeza
dos registros encontrados.

Não apagar as linhas Extra box antes
das linhas normais.

Não manter registros Extra box de uma sessão
anterior quando os demais registros já
tiverem sido reinicializados.

## Respostas tardias

Uma resposta HTTP de uma sessão encerrada
não poderá adicionar registros à sessão atual.

Reutilizar o mecanismo existente de identificação
de sessão ou geração.

---

# 20. RF022.17 — Preservação operacional

Este requisito não poderá alterar:

- Comunicação LLRP.
- Zebra FX9600.
- Comunicação Modbus.
- Waveshare Relay.
- DI1.
- DI2.
- CH1.
- CH2.
- CH3.
- Timer de 60 segundos.
- Máquina de estados.
- Start/Stop.
- Monitoramento de conectividade.
- Consulta remota de EPC.
- Registro de passagem.
- Regras de deduplicação.
- Regras de contabilização Extra box.

A alteração deverá se concentrar na
apresentação dos registros na tabela.

Não modificar serviços operacionais sem
necessidade técnica comprovada.

---

# 21. Análise obrigatória antes da implementação

Antes de modificar o código, o Codex deverá:

1. Ler AGENTS.md.
2. Confirmar a branch atual.
3. Verificar o estado do Git.
4. Consultar RF016, RF017, RF018, RF019 e RF020.
5. Localizar o controller de leitura RFID.
6. Localizar a classificação Extra box.
7. Localizar o contador Extra box.
8. Localizar o modelo de dados da tabela.
9. Localizar a Qt Bridge.
10. Localizar o componente QML da tabela.
11. Identificar os delegates responsáveis pelas linhas.
12. Identificar o mecanismo de atualização da tabela.
13. Identificar os testes existentes.

Verificar especialmente se os EPCs Extra box
já estão disponíveis no estado da sessão
e apenas não são enviados ao modelo da tabela.

Caso estejam disponíveis, reutilizar esses dados.

Não implementar um fluxo paralelo de consulta.

Não criar uma segunda fonte de verdade.

---

# 22. Estratégia de implementação

## Etapa 1 — Inspeção

Analisar como os registros encontrados
são enviados à tabela.

Identificar onde os registros Extra box
deixam de ser encaminhados.

## Etapa 2 — Modelo

Adaptar o modelo existente para representar
registros encontrados e Extra box.

Preservar os dados e roles existentes.

## Etapa 3 — Integração

Permitir que a classificação Extra box
gere uma linha na tabela.

Não modificar o contador.

## Etapa 4 — Identificação

Disponibilizar no modelo:

- EPC.
- Classificação.
- Motivo Extra box.

## Etapa 5 — QML

Aplicar o estilo visual amarelo discreto
às linhas classificadas como Extra box.

## Etapa 6 — Testes

Executar testes unitários, de integração
simulada e de interface.

## Etapa 7 — Revisão

Revisar o diff.

Confirmar que não houve alterações
desnecessárias em serviços operacionais.

---

# 23. Testes obrigatórios

## Teste 01 — EPC encontrado

Entrada:

    EPC A -> HTTP 200
    status = pendente

Resultado:

    EPCs encontrados = 1
    Extra box = 0

    Tabela:
    1 linha normal

## Teste 02 — EPC não cadastrado

Entrada:

    EPC A -> HTTP 404

Resultado:

    EPCs encontrados = 0
    Extra box = 1

    Tabela:
    1 linha Extra box

    Fundo amarelo discreto

## Teste 03 — EPC previamente lido

Entrada:

    EPC A -> HTTP 200
    status = lido

Resultado:

    Extra box = 1

    Tabela:
    1 linha Extra box

    Dados cadastrais preservados

## Teste 04 — Múltiplos Extra box

Entrada:

    EPC A -> HTTP 404
    EPC B -> HTTP 404
    EPC C -> status lido

Resultado:

    Extra box = 3

    Tabela:
    3 linhas Extra box

## Teste 05 — Leitura mista

Entrada:

    EPC A -> pendente
    EPC B -> lido
    EPC C -> HTTP 404
    EPC D -> pendente
    EPC E -> HTTP 404

Resultado:

    EPCs encontrados = 2
    Extra box = 3

    Tabela:
    5 linhas

    2 linhas normais
    3 linhas amarelas

## Teste 06 — EPC repetido

Entrada:

    EPC A -> HTTP 404
    EPC A -> HTTP 404
    EPC A -> HTTP 404

Resultado:

    Extra box = 1

    Tabela:
    1 linha Extra box

## Teste 07 — EPC processado na sessão

Entrada:

    EPC A -> pendente
    POST -> sucesso
    EPC A identificado novamente

Resultado:

    Nenhuma nova linha Extra box.
    Nenhuma duplicação.
    Contadores consistentes.

## Teste 08 — Erro técnico

Entrada:

    EPC A -> HTTP 500
    EPC B -> Timeout

Resultado:

    Nenhuma nova linha Extra box.

## Teste 09 — Dados inexistentes

Entrada:

    EPC A -> HTTP 404

Resultado:

    Status = Extra box
    Cliente = —
    Nota fiscal = —
    Volume = —
    Pedido = —
    Doca = —

## Teste 10 — Identificação do EPC

Entrada:

    EPC A -> HTTP 404

Resultado:

    EPC disponível na coluna Status.
    EPC completo acessível em tooltip
    quando houver elisão visual.

## Teste 11 — Hover

Posicionar o mouse sobre uma linha Extra box.

Resultado:

    Fundo recebe variação discreta.
    Texto permanece legível.

## Teste 12 — Rolagem

Adicionar quantidade suficiente de registros
para exigir rolagem.

Resultado:

    Linhas normais e Extra box permanecem
    corretamente formatadas.

## Teste 13 — Sidebar

Recolher e expandir a sidebar.

Resultado:

    Tabela se adapta.
    Destaques permanecem corretos.
    Nenhum registro é perdido.

## Teste 14 — Nova sessão

Encerrar a sessão e iniciar outra.

Resultado:

    Tabela e contadores seguem a mesma
    política de reinicialização.

## Teste 15 — Resposta tardia

Receber resposta HTTP de sessão encerrada.

Resultado:

    Nenhuma linha é adicionada à sessão atual.

## Teste 16 — Regressão operacional

Validar:

- Iniciar leitura.
- Parar leitura.
- DI1.
- DI2.
- Timer.
- CH1.
- CH2.
- CH3.
- GET de EPC.
- POST de passagem.
- Contadores.
- Indicadores de conexão.

---

# 24. Critérios de aceite

- [ ] EPCs encontrados continuam aparecendo na tabela.
- [ ] EPCs Extra box também aparecem na tabela.
- [ ] EPC não cadastrado gera linha Extra box.
- [ ] EPC previamente lido gera linha Extra box.
- [ ] Linhas Extra box possuem fundo amarelo discreto.
- [ ] Destaque ocupa toda a largura da linha.
- [ ] Cores são compatíveis com Corporate Dark.
- [ ] Texto permanece legível.
- [ ] Status apresenta identificação Extra box.
- [ ] EPC pode ser identificado na linha Extra box.
- [ ] Registros não cadastrados não recebem dados fictícios.
- [ ] Registros previamente lidos preservam seus dados cadastrais.
- [ ] Não existem linhas duplicadas por EPC na sessão.
- [ ] Contador Extra box permanece correto.
- [ ] Contador EPCs encontrados permanece correto.
- [ ] EPC processado na sessão não vira Extra box indevidamente.
- [ ] Erros técnicos não geram linhas Extra box.
- [ ] Tabela continua responsiva.
- [ ] Rolagem permanece funcional.
- [ ] Sidebar retrátil permanece funcional.
- [ ] Tema Corporate Dark preservado.
- [ ] Backend não foi modificado.
- [ ] Serviços RFID não foram modificados.
- [ ] Regras operacionais preservadas.
- [ ] Testes automatizados aprovados.

---

# 25. Fora do escopo

Não implementar:

- Nova tabela.
- Nova tela.
- Nova coluna EPC.
- Novos contadores.
- Novos endpoints.
- Alterações no Rails.
- Alterações no PostgreSQL.
- Exportação de Extra box.
- Persistência local de Extra box.
- Novas regras de classificação.
- Novas regras de deduplicação.
- Alterações nos relés.
- Alterações nos sensores.
- Alterações no timer.
- Redesenho completo do Dashboard.
- Nova biblioteca gráfica.
- Refatoração ampla do projeto.

---

# 26. Relatório final obrigatório

Ao concluir, apresentar:

1. Branch utilizada.
2. Arquivos modificados.
3. Local onde os registros Extra box passaram
   a ser encaminhados para a tabela.
4. Alterações realizadas no modelo Qt.
5. Alterações realizadas no QML.
6. Cores utilizadas.
7. Comportamento do hover e seleção.
8. Tratamento de EPC não cadastrado.
9. Tratamento de EPC previamente lido.
10. Garantias de deduplicação.
11. Testes implementados.
12. Testes executados.
13. Resultados dos testes.
14. Resultado da regressão.
15. Confirmação de preservação dos serviços operacionais.

---

# 27. Definição de pronto

O RF022 estará concluído quando a tabela principal
do Dashboard RFID apresentar tanto os EPCs encontrados
quanto os EPCs classificados como Extra box.

Os registros Extra box deverão possuir destaque
visual amarelo discreto, compatível com o tema
Corporate Dark da aplicação.

O operador deverá conseguir identificar:

- Quais registros foram encontrados normalmente.
- Quais registros são Extra box.
- Qual EPC corresponde a cada Extra box.
- Se o Extra box representa uma etiqueta não cadastrada
  ou previamente lida.

Os contadores deverão continuar consistentes
com os registros da sessão.

A implementação deverá reutilizar a classificação
existente, sem modificar o funcionamento operacional
do sistema RFID.

**Implementar o RF022 completo, incluindo integração
com o modelo da tabela, apresentação QML, destaque
visual e testes automatizados, preservando todas
as funcionalidades existentes.**