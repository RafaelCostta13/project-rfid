# RF025 — Reorganização e Otimização da Tabela RFID

**Projeto:** RFID System
**Requisito:** RF025
**Categoria:** Interface / Correção funcional / UX
**Prioridade:** Alta
**Tecnologia:** Python + PySide6 + QML
**Backend:** Rails API
**Ambiente:** Windows
**Requisitos relacionados:** RF016, RF017, RF018, RF019, RF020, RF022, RF023 e RF024
**Status:** A implementar

---

# 1. OBJETIVO

Realizar melhorias na tabela de etiquetas RFID
apresentada na tela Start do software.

O objetivo é:

1. Adicionar a coluna Tag.
2. Utilizar o campo "tag" retornado pela API.
3. Simplificar as informações da coluna Status.
4. Remover a exibição do EPC na coluna Status.
5. Reorganizar a ordem das colunas.
6. Redistribuir adequadamente a largura das colunas.
7. Garantir a visualização completa do número da doca.
8. Preservar a identificação visual das etiquetas Extra Box.
9. Preservar as funcionalidades operacionais existentes.

IMPORTANTE:

Este requisito modifica apenas o mapeamento
necessário e a apresentação da tabela RFID.

Não modificar regras operacionais.

---

# 2. CONTEXTO ATUAL

A tabela atualmente possui:

    Status
    Fornecedor
    Nota fiscal
    Volume
    Pedido
    Doca

Problemas identificados:

1. A coluna Status apresenta informações desnecessárias.
2. O EPC aparece abaixo da classificação Extra Box.
3. Etiquetas normais apresentam o texto "lido".
4. A informação Tag da API não aparece na tabela.
5. A largura das colunas não está bem distribuída.
6. A coluna Doca apresenta valores cortados.

Exemplo do problema atual:

    DOCA...

O operador não consegue identificar o número
completo da doca.

Essa informação é essencial para a operação.

---

# 3. RF025.01 — NOVA ESTRUTURA DA TABELA

A tabela deverá possuir exatamente as colunas:

    Status
    Fornecedor
    Tag
    Nota fiscal
    Volume
    Pedido
    Doca

Ordem obrigatória:

1. Status
2. Fornecedor
3. Tag
4. Nota fiscal
5. Volume
6. Pedido
7. Doca

Não adicionar outras colunas.

Não modificar essa ordem.

Preservar o cabeçalho e a estrutura visual
existente da tabela.

---

# 4. RF025.02 — ADICIONAR COLUNA TAG

Adicionar uma nova coluna:

    Tag

A informação deverá ser obtida diretamente
do campo "tag" retornado pela API Rails.

Endpoint:

    GET /api/v1/rfid_records/:epc

Exemplo de resposta:

{
  "found": true,
  "data": {
    "datahora": "2026-10-06T16:44:45.000Z",
    "volume": "1/1",
    "volume_numero": 1,
    "volume_total": 1,
    "pedido": "0007818432",
    "notafiscal": "1198497",
    "destinatario": "CALTEX VEICULOS LTDA",
    "endereco": "AV EUSEBIO MATOSO",
    "numero": "730",
    "cidade": "SAO PAULO",
    "uf": "SP",
    "doca": "DOCA 42",
    "epc": "424D57303131313938343937",
    "tag": "BMW011198497",
    "fornecedor": "BMW do Brasil Ltda",
    "status": "pendente",
    "first_read_at": null,
    "last_read_at": null,
    "read_count": 0
  }
}

Mapeamento:

    Coluna Tag = data.tag

Resultado esperado:

    BMW011198497

IMPORTANTE:

Não utilizar o campo EPC para preencher
a coluna Tag.

Não converter o EPC hexadecimal para ASCII
para gerar a Tag.

Não reconstruir a Tag a partir de outros campos.

Utilizar exclusivamente a informação
retornada pela API no campo "tag".

Caso o campo não exista, seja null ou vazio,
apresentar:

    —

Não utilizar valores fictícios.

---

# 5. RF025.03 — ALTERAR A COLUNA STATUS

Atualmente, a coluna Status apresenta valores
como:

    lido

E, para registros Extra Box:

    Extra box
    EPC hexadecimal

Esse comportamento deverá ser alterado.

A partir do RF025, a coluna Status deverá
apresentar exclusivamente:

    OK

Ou:

    Extra box

Não apresentar o EPC.

Não apresentar informações adicionais.

Não apresentar uma segunda linha de texto.

Não apresentar códigos hexadecimais.

Não apresentar a identificação Tag na coluna Status.

---

# 6. RF025.04 — STATUS OK

Quando o registro não estiver classificado
como Extra Box, apresentar:

    OK

Exemplo:

    Status: OK

Não apresentar:

    lido
    pendente
    processado
    encontrado

A classificação visual deverá utilizar
a classificação operacional existente.

IMPORTANTE:

A apresentação "OK" não deverá alterar
o campo "status" retornado pelo Backend.

O Backend continuará utilizando os estados
de negócio existentes.

A mudança é exclusivamente visual.

Preservar a cor verde utilizada atualmente
para identificar os registros normais.

---

# 7. RF025.05 — STATUS EXTRA BOX

Quando o registro estiver classificado
como Extra Box, apresentar exclusivamente:

    Extra box

Não exibir o EPC abaixo do texto.

Exemplo atual:

    Extra box
    47574D3031303...

Novo comportamento:

    Extra box

O texto deverá ocupar uma única linha.

Preservar o destaque amarelo discreto da
linha inteira, implementado no RF022.

Não alterar:

- Classificação Extra Box.
- Contador Extra Box.
- Deduplicação.
- Motivos de classificação.
- Regras de consulta HTTP.

O EPC deverá continuar armazenado
internamente no modelo de dados.

Não remover o EPC da lógica operacional.

Ele continuará sendo necessário para:

- Identificação da etiqueta.
- Deduplicação.
- Consultas ao Backend.
- Registro de passagem.
- Controle de sessão.

Remover somente sua exibição na coluna Status.

---

# 8. RF025.06 — MAPEAMENTO FINAL DA TABELA

Estabelecer o seguinte mapeamento:

| Coluna | Origem |
|--------|--------|
| Status | Classificação operacional |
| Fornecedor | data.fornecedor |
| Tag | data.tag |
| Nota fiscal | data.notafiscal |
| Volume | data.volume |
| Pedido | data.pedido |
| Doca | data.doca |

O campo Status será:

    OK

Para registros normalmente encontrados.

Ou:

    Extra box

Para registros classificados como Extra Box.

Não utilizar diretamente o status bruto
da API como texto da coluna Status.

A classificação operacional existente
deverá continuar sendo a fonte de verdade.

---

# 9. RF025.07 — DISTRIBUIÇÃO DAS LARGURAS

A tabela deverá utilizar melhor o espaço
horizontal disponível.

Atualmente, algumas colunas ocupam muito
espaço enquanto outras apresentam
informações cortadas.

O principal exemplo é:

    DOCA...

Precisamos garantir que o número da doca
permaneça visível.

## Distribuição sugerida

| Coluna | Proporção inicial |
|--------|-------------------|
| Status | 10% |
| Fornecedor | 27% |
| Tag | 19% |
| Nota fiscal | 12% |
| Volume | 8% |
| Pedido | 14% |
| Doca | 10% |

Total:

    100%

Essas proporções são referências.

Não utilizar percentuais rígidos caso
prejudiquem a responsividade.

Preferir um layout dinâmico com limites
mínimos adequados para cada coluna.

## Prioridades

1. A coluna Fornecedor terá a maior largura.
2. A coluna Tag deverá comportar seus identificadores.
3. A coluna Pedido deverá preservar zeros à esquerda.
4. A coluna Nota fiscal deverá apresentar seu número.
5. A coluna Volume poderá ser mais estreita.
6. A coluna Status poderá ser compacta.
7. A coluna Doca deverá apresentar o valor completo.

---

# 10. RF025.08 — LARGURAS MÍNIMAS

Utilizar como referência inicial:

    Status:
    100 px

    Fornecedor:
    240 px

    Tag:
    165 px

    Nota fiscal:
    110 px

    Volume:
    75 px

    Pedido:
    130 px

    Doca:
    110 px

Os valores deverão ser ajustados conforme:

- Fonte utilizada.
- Tamanho do texto.
- Padding das células.
- Largura da tabela.
- Resolução da janela.

O objetivo não é criar colunas fixas,
mas estabelecer limites que garantam
legibilidade.

A coluna Fornecedor deverá receber
preferencialmente o espaço horizontal
adicional disponível.

As colunas menores não deverão crescer
desnecessariamente.

---

# 11. RF025.09 — VISUALIZAÇÃO COMPLETA DA DOCA

Esta é uma exigência importante do RF025.

Atualmente, a coluna Doca apresenta
informações cortadas.

Exemplo:

    DOCA...

Resultado desejado:

    DOCA 42

O número da doca deverá estar visível.

Não aplicar elisão visual ao valor
da doca quando o espaço disponível permitir
acomodar o texto completo.

Ajustar:

- Largura mínima.
- Padding.
- Alinhamento.
- Distribuição das colunas.

Não utilizar padding excessivo.

A largura deverá considerar o conteúdo,
não apenas o título "Doca".

Exemplos que deverão ser apresentados:

    DOCA 1
    DOCA 12
    DOCA 42
    DOCA 100

Caso existam valores maiores no Backend,
a interface deverá oferecer acesso ao
conteúdo completo.

Quando a largura total disponível não
comportar os limites mínimos das colunas,
utilizar rolagem horizontal da tabela,
em vez de ocultar o número da doca.

Não cortar dados críticos.

---

# 12. RF025.10 — COLUNA FORNECEDOR

A coluna Fornecedor deverá continuar utilizando:

    data.fornecedor

Conforme RF024.

Essa será a coluna com maior largura disponível.

Exemplo:

    BMW do Brasil Ltda

Outros fornecedores poderão ter nomes
um pouco maiores.

Ajustar a coluna para comportar adequadamente
os nomes mais frequentes.

Caso o nome ultrapasse o espaço disponível:

- Aplicar elisão visual quando necessária.
- Preservar o texto original completo no modelo.
- Permitir visualizar o nome completo por tooltip.

Não aumentar a altura da linha apenas
por causa de nomes longos.

Não permitir que o texto invada outra coluna.

---

# 13. RF025.11 — COLUNA TAG

A Tag deverá ser apresentada em uma única linha.

Exemplo:

    BMW011198497

Preservar:

- Letras.
- Números.
- Ordem dos caracteres.
- Zeros à esquerda.
- Valor original retornado pela API.

Não modificar a capitalização retornada
pelo Backend sem necessidade.

Não converter o valor para número.

Não utilizar formatação que remova zeros.

A coluna deverá ter largura suficiente
para os identificadores usuais.

Para valores excepcionalmente longos,
permitir elisão visual e tooltip com
o conteúdo completo.

---

# 14. RF025.12 — COLUNAS NUMÉRICAS E IDENTIFICADORES

Preservar os valores de:

    Nota fiscal
    Volume
    Pedido

Exemplos:

    Nota fiscal:
    1198497

    Volume:
    1/1

    Pedido:
    0007818432

IMPORTANTE:

O pedido poderá conter zeros à esquerda.

Não realizar conversão numérica que
remova esses zeros.

Não modificar o formato de volume.

Não modificar o valor da nota fiscal.

A alteração deverá afetar somente
a apresentação e distribuição visual.

---

# 15. RF025.13 — EXTRA BOX NA NOVA TABELA

Preservar integralmente o comportamento
implementado pelo RF022.

## Caso A — Extra Box previamente lido

Resposta:

    HTTP 200

    status = "lido"

Classificação:

    Extra box

Exibir:

    Status: Extra box
    Fornecedor: data.fornecedor
    Tag: data.tag
    Nota fiscal: data.notafiscal
    Volume: data.volume
    Pedido: data.pedido
    Doca: data.doca

Preservar a linha amarela discreta.

## Caso B — Extra Box não cadastrado

Resposta:

    HTTP 404

Classificação:

    Extra box

Exibir:

    Status: Extra box
    Fornecedor: —
    Tag: —
    Nota fiscal: —
    Volume: —
    Pedido: —
    Doca: —

Preservar a linha amarela discreta.

Não gerar informações inexistentes.

Não utilizar o EPC como substituto da Tag.

---

# 16. RF025.14 — ESTILO VISUAL

Preservar o tema Corporate Dark.

## Linhas normais

Status:

    OK

Cor:

    Verde utilizado atualmente.

Fundo:

    Manter a aparência normal da tabela.

## Linhas Extra Box

Status:

    Extra box

Cor:

    Âmbar suave.

Fundo:

    Amarelo discreto conforme RF022.

Referência de cor:

    Fundo Extra Box:
    #3A372C

    Destaque:
    #D9B86C

Não alterar a identidade visual.

Não utilizar amarelo vibrante.

Não alterar os cards de contabilização.

---

# 17. RF025.15 — ALTURA DAS LINHAS

Atualmente, a exibição do EPC abaixo de
"Extra box" utiliza duas linhas de texto.

Após remover essa informação, padronizar
a altura das linhas.

Resultado desejado:

    Todas as linhas com altura consistente.

Não manter espaço vertical vazio
reservado para o EPC removido.

A tabela deverá aproveitar melhor
a área disponível.

Preferir uma altura confortável
para leitura em ambiente operacional.

Não reduzir excessivamente o tamanho
da fonte ou a altura das linhas.

---

# 18. RF025.16 — COMPORTAMENTO RESPONSIVO

A tabela deverá se adaptar automaticamente
à largura disponível.

Considerar:

- Janela maximizada.
- Janela restaurada.
- Sidebar expandida.
- Sidebar recolhida.
- Resoluções menores suportadas.

Ao recolher a sidebar:

    A tabela recebe mais espaço horizontal.

Ao expandir a sidebar:

    A tabela se ajusta automaticamente.

Não manter uma largura fixa baseada
somente na janela maximizada.

Não permitir sobreposição de textos.

Não permitir que as colunas ultrapassem
o container sem rolagem apropriada.

Priorizar a visibilidade completa de:

    Status
    Tag
    Nota fiscal
    Volume
    Pedido
    Doca

A coluna Fornecedor poderá utilizar
elisão visual quando necessário.

---

# 19. RF025.17 — MODELO PYTHON / QT

Analisar a implementação atual da tabela.

Verificar se utiliza:

- QAbstractTableModel.
- QAbstractListModel.
- ListModel QML.
- Propriedades expostas pela Qt Bridge.
- Estrutura própria de registros.

Adaptar a estrutura existente.

Não criar um modelo paralelo.

O novo modelo visual deverá disponibilizar:

    status_display
    fornecedor
    tag
    notafiscal
    volume
    pedido
    doca

Os nomes são conceituais.

Reutilizar as convenções existentes.

Preservar internamente:

    epc
    status original
    classificação Extra Box
    motivo Extra Box
    identificador de sessão

Não remover dados necessários para
a operação apenas porque deixaram
de aparecer visualmente.

---

# 20. RF025.18 — ATUALIZAÇÃO EM TEMPO REAL

Preservar a atualização automática da tabela
durante o inventário RFID.

Ao receber um EPC autorizado:

1. Consultar o Backend.
2. Classificar o registro.
3. Atualizar o estado da sessão.
4. Adicionar ou atualizar o registro na tabela.
5. Exibir as sete colunas corretamente.

Não recriar toda a tabela para adicionar
um registro, quando o modelo atual permitir
atualização incremental.

Não bloquear a thread principal.

Não executar consultas HTTP no QML.

Não alterar a lógica de deduplicação.

---

# 21. RF025.19 — PRESERVAÇÃO OPERACIONAL

Não modificar:

- Zebra FX9600.
- Biblioteca sllurp.
- Comunicação LLRP.
- Waveshare Modbus RTU Relay.
- DI1.
- DI2.
- CH1.
- CH2.
- CH3.
- Timer de 60 segundos.
- Máquina de estados.
- Iniciar leitura.
- Parar leitura.
- Consulta GET ao Backend.
- Registro POST de passagem.
- Contadores RFID.
- Classificação Extra Box.
- Deduplicação.
- Filtro de prefixos RF023.
- Configurações de comunicação.

O RF025 é um ajuste de apresentação
e mapeamento de dados.

Não alterar a estrutura do Backend Rails.

Não modificar o banco PostgreSQL.

Não criar novos endpoints.

---

# 22. ANÁLISE OBRIGATÓRIA

Antes de implementar:

1. Ler AGENTS.md.
2. Verificar a branch atual.
3. Executar git status.
4. Localizar a tela Start em QML.
5. Localizar o componente da tabela.
6. Localizar a definição das colunas.
7. Localizar o modelo Qt responsável.
8. Localizar o mapeamento da API.
9. Verificar disponibilidade do campo tag.
10. Localizar a apresentação atual do status.
11. Localizar a exibição do EPC no Status.
12. Identificar os cálculos de largura das colunas.
13. Verificar a origem da elisão da coluna Doca.
14. Identificar os testes existentes.

Identificar se o problema da coluna Doca
está relacionado a:

- Largura fixa.
- Distribuição proporcional inadequada.
- Padding excessivo.
- Componentes com largura incorreta.
- Configuração de elisão.
- Problemas de layout QML.

Corrigir a causa do problema.

Não apenas aumentar arbitrariamente
a largura da tabela inteira.

---

# 23. ESTRATÉGIA DE IMPLEMENTAÇÃO

## Etapa 1 — Mapeamento

Adicionar o campo data.tag ao modelo
utilizado pela tabela.

## Etapa 2 — Status

Modificar a apresentação para:

    OK
    Extra box

Remover a exibição do EPC.

## Etapa 3 — Colunas

Adicionar Tag.

Organizar a ordem:

    Status
    Fornecedor
    Tag
    Nota fiscal
    Volume
    Pedido
    Doca

## Etapa 4 — Dimensionamento

Redistribuir a largura das colunas.

Garantir visibilidade do número da doca.

## Etapa 5 — Altura

Padronizar a altura das linhas após
a remoção do EPC exibido.

## Etapa 6 — Extra Box

Validar a manutenção do destaque amarelo.

## Etapa 7 — Testes

Executar testes automatizados e visuais.

## Etapa 8 — Revisão

Revisar o diff e identificar alterações
não relacionadas ao RF025.

---

# 24. TESTES OBRIGATÓRIOS

## Teste 01 — Ordem das colunas

Resultado esperado:

    Status
    Fornecedor
    Tag
    Nota fiscal
    Volume
    Pedido
    Doca

## Teste 02 — Status normal

Entrada:

    EPC normalmente encontrado.
    Classificação não Extra Box.

Resultado:

    Status = OK

Não apresentar "lido".

Não apresentar EPC.

## Teste 03 — Status Extra Box

Entrada:

    EPC classificado como Extra Box.

Resultado:

    Status = Extra box

Não apresentar EPC abaixo.

## Teste 04 — Tag

Resposta:

    tag = BMW011198497

Resultado:

    Coluna Tag = BMW011198497

## Teste 05 — Tag ausente

Resposta:

    tag = null

Resultado:

    Coluna Tag = —

## Teste 06 — Fornecedor

Resposta:

    fornecedor = BMW do Brasil Ltda

Resultado:

    Coluna Fornecedor =
    BMW do Brasil Ltda

## Teste 07 — Doca

Resposta:

    doca = DOCA 42

Resultado:

    Coluna Doca = DOCA 42

O número 42 deverá aparecer integralmente.

## Teste 08 — Doca com três dígitos

Resposta:

    doca = DOCA 100

Resultado:

    Valor completo visível ou acessível
    sem perda da informação.

## Teste 09 — Pedido

Resposta:

    pedido = 0007818432

Resultado:

    0007818432

Preservar zeros à esquerda.

## Teste 10 — Extra Box já lido

Resposta:

    HTTP 200
    status = lido
    fornecedor = BMW do Brasil Ltda
    tag = BMW011198497

Resultado:

    Status = Extra box
    Fornecedor = BMW do Brasil Ltda
    Tag = BMW011198497

Linha amarela preservada.

## Teste 11 — Extra Box HTTP 404

Resposta:

    HTTP 404

Resultado:

    Status = Extra box
    Tag = —
    Demais campos indisponíveis = —

Linha amarela preservada.

## Teste 12 — Sidebar expandida

Resultado:

    Tabela se ajusta.
    Colunas permanecem organizadas.
    Doca continua legível.

## Teste 13 — Sidebar recolhida

Resultado:

    Tabela utiliza o espaço adicional.
    Nenhuma coluna fica desalinhada.

## Teste 14 — Redimensionamento

Reduzir e aumentar a janela.

Resultado:

    Layout responsivo.
    Sem sobreposição.
    Rolagem horizontal quando necessária.

## Teste 15 — Múltiplos registros

Adicionar registros encontrados
e Extra Box à mesma tabela.

Resultado:

    Sete colunas preenchidas corretamente.
    Status apresentados corretamente.
    Nenhum EPC exibido na coluna Status.

## Teste 16 — Atualização em tempo real

Simular recebimento de etiquetas.

Resultado:

    Registros aparecem normalmente.
    Tag é exibida.
    Status correto.
    Sem travamentos.

## Teste 17 — Regressão operacional

Validar:

- Leitura RFID.
- Iniciar/Parar.
- DI1/DI2.
- Timer de 60 segundos.
- Relés CH1/CH2/CH3.
- GET da API.
- POST de passagem.
- Contadores.
- Extra Box.
- Filtro de prefixos.

Nenhuma alteração de comportamento.

---

# 25. CRITÉRIOS DE ACEITE

- [ ] Coluna Tag adicionada.
- [ ] Tag obtida de data.tag.
- [ ] Tag não é reconstruída a partir do EPC.
- [ ] Status normal apresenta somente OK.
- [ ] Status Extra Box apresenta somente Extra box.
- [ ] EPC não aparece na coluna Status.
- [ ] EPC permanece preservado internamente.
- [ ] Ordem das sete colunas implementada.
- [ ] Fornecedor utiliza data.fornecedor.
- [ ] Nota fiscal preservada.
- [ ] Volume preservado.
- [ ] Pedido preserva zeros à esquerda.
- [ ] Doca utiliza data.doca.
- [ ] DOCA 42 aparece integralmente.
- [ ] Larguras redistribuídas adequadamente.
- [ ] Fornecedor possui a maior área horizontal.
- [ ] Tag possui largura suficiente.
- [ ] Linhas possuem altura consistente.
- [ ] Layout responsivo.
- [ ] Rolagem horizontal quando necessária.
- [ ] Cores de Extra Box preservadas.
- [ ] Atualização em tempo real preservada.
- [ ] Sem alterações no Backend.
- [ ] Sem alterações no processamento RFID.
- [ ] Sem regressões operacionais.
- [ ] Testes aprovados.

---

# 26. FORA DO ESCOPO

Não implementar:

- Novos endpoints.
- Alterações no PostgreSQL.
- Novos cards.
- Novos contadores.
- Alterações no fluxo Extra Box.
- Alterações no filtro RF023.
- Alterações no protocolo LLRP.
- Alterações nos sensores.
- Alterações nos relés.
- Mudanças no timer.
- Exportação de dados.
- Novas telas.
- Redesenho completo do Dashboard.
- Refatoração ampla da aplicação.

---

# 27. RELATÓRIO FINAL OBRIGATÓRIO

Ao finalizar, apresentar:

1. Branch utilizada.
2. Arquivos modificados.
3. Local onde o campo Tag foi integrado.
4. Alterações realizadas no modelo Python/Qt.
5. Alterações realizadas no QML.
6. Nova ordem das colunas.
7. Regras de apresentação do Status.
8. Confirmação da remoção visual do EPC.
9. Estratégia de dimensionamento das colunas.
10. Solução aplicada para exibição completa da Doca.
11. Tratamento de campos ausentes.
12. Testes implementados.
13. Testes executados.
14. Resultados dos testes.
15. Confirmação de preservação do Extra Box.
16. Confirmação de preservação dos serviços operacionais.

Não realizar commit ou merge automaticamente.

---

# 28. DEFINIÇÃO DE PRONTO

O RF025 estará concluído quando a tabela RFID
possuir a seguinte estrutura:

    Status
    Fornecedor
    Tag
    Nota fiscal
    Volume
    Pedido
    Doca

E apresentar:

- OK para registros normais.
- Extra box para registros Extra Box.
- Nenhum EPC visível na coluna Status.
- Tag obtida diretamente da API.
- Fornecedor obtido diretamente da API.
- Larguras adequadamente distribuídas.
- Doca com número completamente visível.
- Layout responsivo.
- Linhas Extra Box com destaque amarelo.
- Todas as funções operacionais preservadas.

IMPLEMENTAR O RF025 COMPLETO, PRIORIZANDO
LEGIBILIDADE, ORGANIZAÇÃO, USABILIDADE
E PRESERVAÇÃO DAS FUNCIONALIDADES EXISTENTES.