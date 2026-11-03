# RF024 — Correção do Mapeamento da Coluna Fornecedor

**Projeto:** RFID System
**Requisito:** RF024
**Categoria:** Correção funcional / Interface
**Prioridade:** Alta
**Tecnologia:** Python + PySide6 + QML
**Backend:** Rails API
**Status:** A implementar

---

# 1. OBJETIVO

Corrigir o mapeamento de dados da tabela de etiquetas
apresentada na tela Start do software RFID.

Atualmente, a tabela possui a coluna:

    Cliente

Essa coluna deverá ser renomeada para:

    Fornecedor

Além disso, os valores apresentados deverão utilizar
exclusivamente o campo "fornecedor" retornado pela API.

A alteração deverá ser aplicada tanto aos registros
encontrados quanto aos registros Extra Box que
possuam informações cadastradas no Backend.

---

# 2. CONTEXTO

A aplicação consulta os registros RFID por meio do endpoint:

    GET /api/v1/rfid_records/:epc

Exemplo real de resposta:

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

Observação:

A resposta possui um objeto "data" que contém
as informações do registro.

O campo desejado é:

    data.fornecedor

Não utilizar:

    data.destinatario
    data.endereco
    data.cidade

---

# 3. RF024.01 — RENOMEAR COLUNA

Na tabela de etiquetas da tela Start:

Alterar:

    Cliente

Para:

    Fornecedor

Manter a posição atual da coluna.

A ordem final deverá ser:

    Status
    Fornecedor
    Nota fiscal
    Volume
    Pedido
    Doca

Não adicionar novas colunas.

Não remover as demais colunas existentes.

Preservar o layout e a identidade visual da aplicação.

---

# 4. RF024.02 — CORRIGIR MAPEAMENTO DA API

Localizar a implementação responsável por converter
a resposta JSON da API em dados apresentados na tabela.

Verificar o mapeamento atual da coluna Cliente.

Identificar qual campo está sendo utilizado atualmente.

Corrigir para:

    fornecedor = response["data"]["fornecedor"]

Essa expressão é apenas uma referência conceitual.

Adaptar ao padrão de parsing e às estruturas de dados
já existentes no projeto.

O campo "fornecedor" deverá ser a única fonte
de informação para a nova coluna.

Não utilizar fallback para:

    destinatario
    endereco
    cliente
    cidade

Não alterar os valores retornados pela API.

Não realizar transformações desnecessárias no nome
do fornecedor.

Preservar acentos, maiúsculas, minúsculas e demais
caracteres retornados pelo Backend.

---

# 5. RF024.03 — RESULTADO ESPERADO

Considerando a resposta JSON apresentada:

    destinatario = CALTEX VEICULOS LTDA

    endereco = AV EUSEBIO MATOSO

    fornecedor = BMW do Brasil Ltda

A tabela deverá apresentar:

| Status | Fornecedor | Nota fiscal | Volume | Pedido | Doca |
|--------|------------|-------------|--------|--------|------|
| lido | BMW do Brasil Ltda | 1198497 | 1/1 | 0007818432 | DOCA 42 |

IMPORTANTE:

A coluna Fornecedor deverá apresentar:

    BMW do Brasil Ltda

Não deverá apresentar:

    CALTEX VEICULOS LTDA

Nem:

    AV EUSEBIO MATOSO

Os demais campos deverão continuar utilizando
seus respectivos mapeamentos atuais.

---

# 6. RF024.04 — INTEGRAÇÃO COM EXTRA BOX

O RF022 implementou a exibição dos registros
Extra Box na tabela RFID.

Essa funcionalidade deverá ser preservada.

Existem duas situações principais.

## Situação A — Extra Box já lido

O Backend retorna:

    HTTP 200

    status = "lido"

O sistema classifica a etiqueta como Extra Box,
conforme as regras atuais.

Nesse cenário, o registro possui informações
cadastrais retornadas pela API.

A coluna Fornecedor deverá utilizar:

    data.fornecedor

Exemplo:

    Status: Extra box
    Fornecedor: BMW do Brasil Ltda

Preservar o fundo amarelo discreto da linha.

## Situação B — Extra Box não cadastrado

O Backend retorna:

    HTTP 404

Nesse cenário, não existe registro cadastrado
com os dados do fornecedor.

A tabela deverá apresentar:

    Status: Extra box
    Fornecedor: —

Não utilizar valores fictícios.

Não copiar o fornecedor de outro registro.

Não tentar utilizar o endereço ou destinatário.

Preservar o EPC apresentado na coluna Status,
conforme RF022.

---

# 7. RF024.05 — TRATAMENTO DE VALORES AUSENTES

O campo fornecedor poderá eventualmente retornar:

    null

Ou:

    ""

Ou estar ausente em uma resposta legada.

Nessas situações, apresentar:

    —

Não permitir que a interface apresente:

    None
    null
    undefined

Não provocar erros no modelo Qt.

Não utilizar destinatario ou endereco
como substitutos automáticos.

Preservar o tratamento de erros existente.

---

# 8. RF024.06 — MODELO PYTHON E QT BRIDGE

Localizar os componentes responsáveis pelo
mapeamento e apresentação dos registros.

Verificar:

1. Backend Client.
2. Parser da resposta JSON.
3. Controller de leitura RFID.
4. Modelo de dados da sessão.
5. Qt Bridge.
6. Table Model.
7. Delegate QML.
8. Cabeçalho da tabela.

Identificar se o campo atualmente utilizado
possui o nome interno:

    cliente

Caso exista, avaliar a necessidade de renomeá-lo
para:

    fornecedor

Preferir nomes semanticamente corretos.

Entretanto, não realizar refatorações amplas
nem quebrar contratos internos compartilhados.

Preservar os signals, slots e properties existentes,
adaptando somente o necessário para a alteração.

Não implementar consultas HTTP diretamente no QML.

---

# 9. RF024.07 — AJUSTE VISUAL

Preservar a aparência atual da tabela.

A coluna Fornecedor deverá permanecer na
mesma posição anteriormente utilizada por Cliente.

Ajustar a largura da coluna apenas se necessário
para acomodar nomes de fornecedores.

Quando o nome exceder a largura disponível:

- Utilizar a elisão visual existente.
- Preservar o nome completo no modelo.
- Exibir o valor integral em tooltip, se o
  componente já oferecer esse comportamento.

Não modificar as cores das linhas normais.

Não modificar as cores das linhas Extra Box.

Não alterar:

- Altura da tabela.
- Sidebar retrátil.
- Cards.
- Botões.
- Header.
- Indicadores.

---

# 10. RF024.08 — PRESERVAÇÃO DOS REQUISITOS

A implementação deverá preservar integralmente:

RF016 — Consulta remota de EPC.

RF017 — Registro de passagem.

RF018 — Interface PySide6 + QML.

RF019 — Contabilização Extra Box.

RF020 — Otimização do Dashboard.

RF022 — Exibição de Extra Box na tabela.

RF023 — Filtro de EPC por prefixos autorizados.

Não modificar:

- Zebra FX9600.
- Biblioteca sllurp.
- Comunicação LLRP.
- Waveshare.
- DI1.
- DI2.
- CH1.
- CH2.
- CH3.
- Timer de 60 segundos.
- Máquina de estados.
- GET de consulta.
- POST de passagem.
- Deduplicação de EPCs.
- Contadores.
- Classificação Extra Box.
- Filtro de prefixos.

---

# 11. ANÁLISE OBRIGATÓRIA

Antes de modificar o código:

1. Ler AGENTS.md.
2. Identificar a branch atual.
3. Executar git status.
4. Localizar o mapeamento atual de Cliente.
5. Verificar se utiliza destinatario, endereco
   ou outro campo.
6. Localizar o modelo Qt.
7. Localizar o cabeçalho QML.
8. Verificar a apresentação de Extra Box.
9. Identificar testes existentes.

Corrigir a origem dos dados, não apenas
o título da coluna.

Evitar alterações em arquivos não relacionados.

---

# 12. TESTES OBRIGATÓRIOS

## Teste 01 — EPC encontrado

Resposta:

    HTTP 200
    status = pendente
    fornecedor = BMW do Brasil Ltda

Resultado esperado:

    Coluna Fornecedor:
    BMW do Brasil Ltda

## Teste 02 — Extra Box já lido

Resposta:

    HTTP 200
    status = lido
    fornecedor = BMW do Brasil Ltda

Resultado esperado:

    Status: Extra box
    Fornecedor: BMW do Brasil Ltda

    Linha amarela preservada.

## Teste 03 — Extra Box não cadastrado

Resposta:

    HTTP 404

Resultado esperado:

    Status: Extra box
    Fornecedor: —

## Teste 04 — Fornecedor ausente

Resposta:

    HTTP 200
    fornecedor = null

Resultado esperado:

    Fornecedor: —

## Teste 05 — Campos diferentes

Resposta:

    destinatario = CALTEX VEICULOS LTDA
    endereco = AV EUSEBIO MATOSO
    fornecedor = BMW do Brasil Ltda

Resultado esperado:

    A coluna apresenta exclusivamente:
    BMW do Brasil Ltda

## Teste 06 — Múltiplos registros

Simular registros com fornecedores distintos.

Resultado esperado:

    Cada linha apresenta o fornecedor
    correspondente ao próprio EPC.

Não misturar informações entre registros.

## Teste 07 — Demais colunas

Verificar:

    Nota fiscal
    Volume
    Pedido
    Doca

Resultado esperado:

    Mapeamentos anteriores preservados.

## Teste 08 — Atualização em tempo real

Simular uma leitura RFID.

Resultado esperado:

    O fornecedor aparece automaticamente
    quando o registro é adicionado à tabela.

## Teste 09 — Regressão Extra Box

Verificar registros:

    Encontrados
    Extra Box já lidos
    Extra Box não cadastrados

Resultado esperado:

    Todos permanecem corretamente apresentados
    e contabilizados.

---

# 13. CRITÉRIOS DE ACEITE

- [ ] Coluna Cliente renomeada para Fornecedor.
- [ ] Valor obtido de data.fornecedor.
- [ ] Não utiliza data.destinatario.
- [ ] Não utiliza data.endereco.
- [ ] Registros encontrados apresentam fornecedor correto.
- [ ] Extra Box já lido apresenta fornecedor correto.
- [ ] Extra Box HTTP 404 apresenta —.
- [ ] Valores ausentes são tratados corretamente.
- [ ] Informações não são misturadas entre EPCs.
- [ ] Demais colunas preservadas.
- [ ] Cores Extra Box preservadas.
- [ ] Atualização em tempo real preservada.
- [ ] Nenhuma alteração no Backend.
- [ ] Nenhuma alteração no processamento RFID.
- [ ] Nenhuma alteração nos sensores e relés.
- [ ] Testes automatizados aprovados.

---

# 14. FORA DO ESCOPO

Não implementar:

- Novas colunas.
- Novas consultas HTTP.
- Alterações no Backend Rails.
- Alterações no PostgreSQL.
- Novos campos no banco de dados.
- Novo Dashboard.
- Mudanças no filtro EPC.
- Alterações no Extra Box.
- Refatorações amplas.
- Mudanças operacionais.

---

# 15. RELATÓRIO FINAL

Ao finalizar, informar:

1. Branch utilizada.
2. Arquivos modificados.
3. Campo utilizado anteriormente na coluna Cliente.
4. Local onde o mapeamento foi corrigido.
5. Alteração realizada no modelo Qt.
6. Alteração realizada no QML.
7. Tratamento para fornecedor ausente.
8. Testes implementados.
9. Resultados dos testes.
10. Confirmação de preservação do Extra Box.
11. Confirmação de que o Backend não foi alterado.
12. Confirmação de que o processamento RFID foi preservado.

Não realizar commit ou merge automaticamente.

---

# 16. DEFINIÇÃO DE PRONTO

O RF024 estará concluído quando a tabela RFID
apresentar a coluna Fornecedor no lugar de Cliente
e exibir corretamente o valor retornado pelo campo:

    data.fornecedor

Essa regra deverá funcionar para:

- EPCs encontrados.
- EPCs Extra Box previamente lidos.
- EPCs não cadastrados, respeitando a ausência
  de informações cadastrais.

Todos os demais comportamentos do sistema
deverão permanecer inalterados.

IMPLEMENTAR O RF024 COMPLETO, CORRIGINDO
O MAPEAMENTO DOS DADOS E PRESERVANDO
TODAS AS FUNCIONALIDADES EXISTENTES.