# RF030 — Alteração das Colunas e Reorganização da Tabela RFID

Projeto: DSV RFID System
Requisito: RF030
Categoria: Interface / Integração API
Tecnologia: Python + PySide6/QML
Prioridade: Baixa

---

## 1. OBJETIVO

Modificar os nomes, o mapeamento e a ordem
das colunas da tabela "Etiquetas lidas",
localizada no painel "Inventário RFID automático".

O ajuste deverá preservar todas as regras
operacionais existentes.

---

## 2. ALTERAÇÕES SOLICITADAS

### 2.1 Renomear Fornecedor para Cliente

Alterar o cabeçalho:

    Fornecedor

Para:

    Cliente

IMPORTANTE:

A coluna Cliente continuará utilizando
o campo retornado pela API:

    data.fornecedor

Não utilizar data.destinatario para Cliente.

### 2.2 Substituir Tag por Dealer

Remover a coluna visual:

    Tag

Adicionar a coluna:

    Dealer

A coluna Dealer deverá utilizar:

    data.destinatario

Não utilizar data.tag para preencher Dealer.

Não remover o campo tag do Backend Rails,
dos modelos internos ou de outras funcionalidades.

A alteração se limita à apresentação
da tabela de etiquetas lidas.

---

## 3. ORDEM OBRIGATÓRIA DAS COLUNAS

A tabela deverá apresentar exatamente
sete colunas, nesta ordem:

1. Status
2. Cliente
3. Nota Fiscal
4. Volume
5. Pedido
6. Doca
7. Dealer

ATENÇÃO:

Esta ordem é obrigatória.

Dealer deverá ser a última coluna.

Não posicionar Dealer após Cliente.

Não manter a coluna Tag.

Não modificar a ordem especificada.

---

## 4. MAPEAMENTO DOS DADOS

| Ordem | Coluna      | Campo da API      |
|-------|-------------|-------------------|
| 1     | Status      | Regra atual       |
| 2     | Cliente     | data.fornecedor   |
| 3     | Nota Fiscal | data.notafiscal   |
| 4     | Volume      | data.volume       |
| 5     | Pedido      | data.pedido       |
| 6     | Doca        | data.doca         |
| 7     | Dealer      | data.destinatario |

Preservar os mapeamentos existentes
das demais colunas.

Não alterar o contrato da API.

---

## 5. EXEMPLO DE RETORNO DA API

{
  "found": true,
  "data": {
    "epc": "424D57303131313938343937",
    "tag": "BMW011198497",
    "fornecedor": "BMW do Brasil Ltda",
    "destinatario": "CALTEX VEICULOS LTDA",
    "notafiscal": "1198497",
    "volume": "1/1",
    "pedido": "0007818432",
    "doca": "DOCA 42",
    "status": "pendente"
  }
}

Resultado esperado:

Status: OK
Cliente: BMW do Brasil Ltda
Nota Fiscal: 1198497
Volume: 1/1
Pedido: 0007818432
Doca: DOCA 42
Dealer: CALTEX VEICULOS LTDA

A coluna Tag não deverá aparecer.

---

## 6. ALTERAÇÕES NA INTERFACE QML

Localizar o componente responsável
pela tabela "Etiquetas lidas".

Implementar:

1. Renomear Fornecedor para Cliente.
2. Remover visualmente a coluna Tag.
3. Adicionar a coluna Dealer.
4. Mapear Dealer para data.destinatario.
5. Reorganizar as sete colunas.
6. Posicionar Dealer na última coluna.
7. Preservar o tema visual atual.
8. Preservar as cores dos registros.
9. Preservar o estado de tabela vazia.
10. Preservar a rolagem e responsividade.

Não modificar outros componentes
da interface sem necessidade.

---

## 7. INTEGRAÇÃO PYTHON / QML

Verificar como os dados da API
são disponibilizados ao modelo QML.

Se data.destinatario já estiver
disponível, reutilizar o campo.

Caso contrário, adicionar somente
o mapeamento necessário.

Não criar novas requisições HTTP.

Não alterar endpoints existentes.

Não alterar o processamento de EPCs.

Não modificar o Backend Rails.

---

## 8. VALORES AUSENTES

Quando data.destinatario estiver:

- Ausente.
- Null.
- Vazio.
- Contendo apenas espaços.

Exibir:

    —

Não utilizar valores alternativos
como fornecedor ou tag.

Preservar o tratamento existente
para registros HTTP 404.

---

## 9. EXTRA BOX

Preservar integralmente as regras
de classificação Extra box.

Não modificar:

- Classificação HTTP 404.
- Classificação de status lido.
- Deduplicação de EPCs.
- Contadores.
- Cores.
- Destaques visuais.

A coluna Dealer deverá apresentar
data.destinatario quando disponível,
inclusive nos registros Extra box.

---

## 10. DIMENSIONAMENTO DA TABELA

A nova ordem deverá ser respeitada
também no dimensionamento das colunas.

Considerar:

- Status: largura adequada ao indicador.
- Cliente: espaço para nome do fornecedor.
- Nota Fiscal: largura adequada.
- Volume: largura adequada.
- Pedido: preservar zeros à esquerda.
- Doca: exibir o valor completo.
- Dealer: espaço para nomes longos.

Preservar a legibilidade dos dados.

Se necessário, utilizar a rolagem
horizontal existente.

Não alterar a altura geral da tabela.

Não adicionar novas colunas.

---

## 11. TESTES OBRIGATÓRIOS

### Teste 1 — Ordem das colunas

Confirmar exatamente:

Status | Cliente | Nota Fiscal |
Volume | Pedido | Doca | Dealer

### Teste 2 — Cliente

Confirmar:

    Cliente = data.fornecedor

### Teste 3 — Dealer

Confirmar:

    Dealer = data.destinatario

### Teste 4 — Remoção de Tag

Confirmar que Tag não aparece
como coluna da tabela.

### Teste 5 — Posicionamento

Confirmar que Dealer é
a sétima e última coluna.

### Teste 6 — Independência

Utilizar valores diferentes para:

    fornecedor
    destinatario
    tag

Confirmar que não existe
troca de informações.

### Teste 7 — Dados ausentes

Confirmar exibição de "—"
quando destinatario estiver ausente.

### Teste 8 — Extra Box

Confirmar que as regras e cores
permanecem inalteradas.

### Teste 9 — Regressão

Confirmar que todas as demais
colunas continuam funcionando.

---

## 12. PRESERVAR FUNCIONALIDADES

Não modificar:

- Zebra FX9600.
- Comunicação LLRP.
- Múltiplas antenas.
- Filtro de EPC.
- Waveshare.
- Sensores DI1 e DI2.
- Relés CH1, CH2 e CH3.
- Timer de leitura.
- Botão Iniciar/Parar leitura.
- Máquina de estados.
- Consultas e registros da API.
- Extra Box.
- Banco de dados.
- Indicadores do sistema.
- Cards do dashboard.
- Configurações.
- Logs.
- Build Windows.
- GitHub Actions.

---

## 13. PROCEDIMENTO DO CODEX

Antes de implementar:

1. Ler AGENTS.md.
2. Verificar branch atual.
3. Executar git status.
4. Identificar os arquivos QML.
5. Identificar o modelo Python.
6. Verificar os testes existentes.
7. Preservar alterações locais.

Após implementar:

1. Executar testes relevantes.
2. Validar mapeamentos.
3. Validar ordem das sete colunas.
4. Validar dimensionamento.
5. Validar Extra Box.
6. Executar git diff.
7. Verificar possíveis regressões.

Não realizar git reset --hard.
Não descartar alterações locais.
Não realizar commit automaticamente.
Não realizar push automaticamente.
Não realizar merge na main.

---

## 14. CRITÉRIOS DE ACEITE

- [ ] Fornecedor renomeado para Cliente.
- [ ] Cliente utiliza data.fornecedor.
- [ ] Coluna Tag removida visualmente.
- [ ] Coluna Dealer adicionada.
- [ ] Dealer utiliza data.destinatario.
- [ ] Status na primeira posição.
- [ ] Cliente na segunda posição.
- [ ] Nota Fiscal na terceira posição.
- [ ] Volume na quarta posição.
- [ ] Pedido na quinta posição.
- [ ] Doca na sexta posição.
- [ ] Dealer na sétima posição.
- [ ] Sete colunas preservadas.
- [ ] Layout preservado.
- [ ] Extra Box preservado.
- [ ] Valores ausentes tratados.
- [ ] Testes automatizados aprovados.
- [ ] Nenhuma regressão operacional.

---

## 15. RELATÓRIO FINAL

Informar:

1. Branch utilizada.
2. Arquivos modificados.
3. Alterações na interface QML.
4. Alterações no modelo Python.
5. Mapeamento final das colunas.
6. Ordem final das colunas.
7. Testes executados.
8. Resultado dos testes.
9. Problemas encontrados.
10. Confirmação de que as regras RFID
    e o Backend Rails não foram alterados.

IMPLEMENTAR O RF030 COM A ORDEM EXATA:

Status
Cliente
Nota Fiscal
Volume
Pedido
Doca
Dealer