# RF039 — Mapa de Leitura / Cobertura das Antenas RFID

Projeto: DSV RFID System
Requisito: RF039
Requisito base: RF038
Categoria: RFID / Diagnóstico / Visualização
Tecnologia: Python + PySide6/QML + sllurp/LLRP
Hardware: Zebra FX9600
Sistema operacional: Windows
Prioridade: Alta

---

## 1. OBJETIVO

Criar uma área de diagnóstico visual
para mapear a área de leitura
das antenas RFID.

Essa área deverá gerar um mapa visual
inspirado em gráficos polares,
sem necessidade de copiar exatamente
a imagem de referência enviada.

A ideia é que:

- Cada antena conectada seja representada
  por uma linha/série própria.
- Ao realizar leituras RFID,
  o sistema marque pontos no mapa.
- O operador consiga visualizar
  a cobertura aproximada de cada antena.

O objetivo é auxiliar na calibração,
regulagem de potência e posicionamento
das antenas no portal RFID.

---

## 2. CONTEXTO

A simples leitura de EPCs não mostra
de forma visual como está a cobertura
de cada antena.

Precisamos de uma ferramenta interna
de diagnóstico para apoiar os testes.

Essa ferramenta não faz parte
do fluxo operacional normal do portal.

Ela será utilizada para calibração.

A imagem de referência mostra
um gráfico polar com curvas.

Queremos um comportamento semelhante:

- Um gráfico circular/polar.
- Uma série por antena.
- Pontos ou traçados com base
  nas leituras obtidas.

IMPORTANTE:

O mapa deverá ser uma ferramenta
de diagnóstico/teste.

Não substituirá a tela Start.

Não alterará o fluxo normal
de produção do sistema.

---

## 3. RELAÇÃO COM O RF038

Este requisito poderá ser implementado
como parte da mesma tela de antenas
ou como uma aba/seção dentro dela.

Exemplo:

    Tela de Antenas RFID
        ├── Aba 1: Configuração
        └── Aba 2: Mapa de leitura

Ou:

    Botão na tela de antenas:
        [ Abrir mapa de leitura ]

O Codex deverá escolher a melhor
organização visual,
preservando clareza e usabilidade.

---

## 4. PREMISSAS TÉCNICAS

Para esse mapa fazer sentido,
o sistema precisa utilizar informações
que já vêm da leitura RFID,
principalmente:

- AntennaID
- RSSI, PeakRSSI ou métrica equivalente
- EPC lido
- Momento da leitura

O Codex deverá analisar os eventos
já recebidos do Zebra FX9600
na implementação atual do projeto.

Se o payload de leitura já expõe
AntennaID e RSSI,
utilizar essas informações.

Se a informação de RSSI
não estiver sendo aproveitada ainda,
o Codex deverá verificar
como extraí-la da leitura,
sem quebrar o fluxo atual.

IMPORTANTE:

Não inventar posicionamento físico
automático se a informação não existir.

O software não sabe sozinho
o ângulo físico do tag no espaço.

Por isso, o modo de mapeamento
deverá ser assistido pelo operador.

---

## 5. MODO DE MAPEAMENTO ASSISTIDO

Para permitir um gráfico polar útil,
criar um modo de mapeamento assistido.

Esse modo deverá funcionar assim:

1. O operador abre a área
   de mapa de leitura.

2. O operador escolhe
   um ângulo/posição de teste.

3. O operador aproxima a etiqueta
   ou realiza a leitura naquele ponto.

4. O sistema recebe a leitura.

5. O sistema marca no gráfico
   um ponto para a antena correspondente.

6. Ao repetir esse processo
   em vários ângulos/posições,
   o mapa vai sendo desenhado.

Sem essa referência manual,
não é possível inferir
o ângulo físico da leitura.

---

## 6. CONTROLES DO MAPA

A tela do mapa deverá possuir
controles mínimos para o operador.

### 6.1 Seleção de ângulo/posição

Adicionar um controle para informar
o ângulo de teste atual.

Exemplo:

-180
-150
-120
-90
-60
-30
0
30
60
90
120
150
180

O Codex poderá implementar isso como:

- Slider
- Dropdown
- Stepper
- Botões de avanço

Preferência:

Um controle simples, claro e rápido.

### 6.2 Sessão de mapeamento

Criar botões como:

    Iniciar mapeamento
    Parar mapeamento
    Limpar mapa

Opcionalmente:

    Exportar dados

Durante o mapeamento:

- O sistema deve capturar leituras.
- Associar a leitura ao ângulo
  atualmente selecionado.
- Plotar os dados por antena.

### 6.3 Informações auxiliares

Mostrar também:

- EPC lido
- Antena que leu
- RSSI
- Horário
- Ângulo associado

Essas informações podem aparecer
em uma tabela/log auxiliar
abaixo ou ao lado do gráfico.

---

## 7. REPRESENTAÇÃO VISUAL DO MAPA

O gráfico deverá ser semelhante
a um gráfico polar/circular.

Elementos esperados:

- Centro do gráfico
- Eixos angulares
- Graduação circular
- Séries por antena
- Pontos marcados
- Legenda das antenas

Cada antena deverá ter:

- Cor própria
- Linha própria
- Pontos próprios

Exemplo conceitual:

    Antena 1 — linha azul
    Antena 2 — linha vermelha
    Antena 3 — linha verde
    Antena 4 — linha amarela

A interface não precisa copiar
o gráfico exatamente,
mas deve seguir a ideia de:

    Visualizar cobertura por antena
    de forma comparável.

---

## 8. COMO PLOTAR OS DADOS

A lógica de plotagem deverá usar:

- Ângulo informado pelo operador
- Intensidade do sinal (RSSI)
- Antena que realizou a leitura

Recomendação:

- Eixo angular = ângulo escolhido
- Eixo radial = intensidade do sinal

Se o RSSI vier em valores negativos,
o Codex deverá normalizar
a exibição no gráfico
de forma visualmente clara,
sem perder a referência técnica.

Exemplo:

- Quanto mais forte o sinal,
  mais próximo da borda externa
  ou conforme a convenção escolhida.

O importante é manter consistência.

A interface deverá indicar
qual escala está sendo usada.

---

## 9. REGRA PARA MARCAÇÃO DOS PONTOS

Ao realizar uma leitura válida
durante o mapeamento:

- Identificar a antena da leitura.
- Capturar RSSI.
- Capturar EPC.
- Ler o ângulo atual informado.
- Adicionar uma marcação no gráfico.

Essa marcação deverá aparecer:

- Na série da antena correspondente.
- Na posição angular correta.
- Na intensidade radial correspondente.

Também adicionar ao log/tabela auxiliar.

---

## 10. AGREGAÇÃO DOS DADOS

Evitar poluição visual excessiva.

Se o mesmo EPC for lido muitas vezes
no mesmo ângulo e pela mesma antena,
o gráfico pode ficar carregado.

Por isso, o Codex deverá implementar
uma regra de agregação.

Regra sugerida:

Para cada combinação de:

    sessão de mapeamento
    + antena
    + ângulo
    + EPC

manter o maior RSSI observado
ou uma média consistente.

Preferência inicial:

    Manter o maior RSSI

Isso gera uma curva mais limpa
e mais útil para calibração.

Ainda assim, o log auxiliar
poderá guardar os eventos individuais
ou um resumo por ponto.

---

## 11. MAPA COM MÚLTIPLAS ANTENAS

Se houver várias antenas conectadas,
o gráfico deverá mostrar todas.

Exemplo:

    Antena 1 — azul
    Antena 2 — vermelho

Resultado esperado:

- Duas linhas distintas
- Duas legendas
- Pontos distintos
- Comparação visual clara

Se existir apenas uma antena,
o gráfico continua funcionando.

---

## 12. TABELA / LOG AUXILIAR

A tela deverá ter uma área auxiliar
para listar as leituras do mapeamento.

Campos sugeridos:

- Data/Hora
- EPC
- Antena
- RSSI
- Ângulo
- Sessão de mapeamento

Essa tabela é importante
para auditoria e análise.

Não precisa substituir
a tabela principal da tela Start.

É uma tabela específica
do modo de mapeamento.

---

## 13. INDEPENDÊNCIA DO FLUXO OPERACIONAL

O modo de mapeamento não deverá depender
do fluxo automático com DI1 e DI2.

Trata-se de uma ferramenta de diagnóstico.

Por isso:

- Não depender de DI1 para iniciar.
- Não depender de DI2 para encerrar.
- Não acionar relés CH1, CH2 ou CH3
  especificamente para o mapa,
  salvo se o Codex reutilizar estados
  técnicos internos sem impacto visual.
- Não consultar backend para classificar EPC.
- Não registrar passagem operacional.
- Não alterar a tela Start.

O mapa é para calibração,
não para operação produtiva.

---

## 14. LEITURAS UTILIZADAS NO MAPA

Durante o modo de mapeamento,
as leituras RFID poderão ser capturadas
em um fluxo de teste dedicado.

O Codex deverá analisar
se consegue reutilizar com segurança
o reader controller existente.

IMPORTANTE:

O modo de mapeamento deve ser isolado
do fluxo operacional do portal.

Não misturar leituras do mapa
com sessões reais do portal.

Se necessário, criar um modo de inventário
de diagnóstico específico para esse recurso.

---

## 15. BOTÃO LIMPAR MAPA

Adicionar um botão:

    Limpar mapa

Ao clicar:

- Apagar todos os pontos/curvas
  da sessão visual atual.
- Limpar a tabela auxiliar da sessão,
  se esse for o comportamento escolhido.
- Não apagar configurações das antenas.
- Não alterar potência configurada.
- Não afetar a tela Start.

---

## 16. EXPORTAÇÃO DE DADOS (OPCIONAL)

Se a implementação permitir
sem aumentar muito a complexidade,
o Codex poderá adicionar:

    Exportar CSV

com as colunas:

- timestamp
- epc
- antenna_id
- rssi
- angle

Se isso aumentar demais o escopo,
pode deixar documentado
como melhoria futura.

Não é obrigatório para aprovação inicial.

---

## 17. INTERFACE VISUAL

Seguir o padrão Corporate Dark.

A tela/aba do mapa deverá conter:

- Título
- Controles de mapeamento
- Controle de ângulo
- Gráfico polar
- Legenda
- Tabela/log auxiliar

A interface deve ser clara,
técnica e utilizável em ambiente Windows.

Não usar visual genérico improvisado.

O gráfico deve ser legível.

---

## 18. REGRAS IMPORTANTES

Este requisito NÃO deve alterar:

- Fluxo operacional DI1/DI2/DI3
- Relés
- Backend Rails
- Extra box
- Tela Start
- Tabela operacional
- Áudio RF033
- Voz RF035
- Filtro EPC
- Regras de potência salvas no RF038

Este requisito cria
uma ferramenta de diagnóstico visual.

---

## 19. TESTES OBRIGATÓRIOS

### Teste 1 — Abertura do mapa

Abrir a tela/aba do mapa.

Resultado esperado:

- Tela abre corretamente.

### Teste 2 — Exibição de antenas

Com duas antenas configuradas:

- Mostrar duas séries/legendas.

### Teste 3 — Início de mapeamento

Clicar em Iniciar mapeamento.

Resultado esperado:

- Sistema entra em modo de captura.

### Teste 4 — Ângulo selecionado

Selecionar ângulo 30.

Realizar leitura.

Resultado esperado:

- Ponto associado ao ângulo 30.

### Teste 5 — Associação da antena

Realizar leitura pela Antena 2.

Resultado esperado:

- Ponto plotado na série da Antena 2.

### Teste 6 — Associação do RSSI

Confirmar que o valor de RSSI
influencia a posição radial.

### Teste 7 — Log auxiliar

Confirmar que a leitura aparece
na tabela auxiliar
com EPC, antena, RSSI e ângulo.

### Teste 8 — Leituras repetidas

Ler o mesmo EPC várias vezes
no mesmo ângulo.

Resultado esperado:

- Agregação conforme regra definida.
- Sem poluição visual excessiva.

### Teste 9 — Limpar mapa

Clicar em Limpar mapa.

Resultado esperado:

- Gráfico limpo
- Tabela da sessão limpa
  conforme comportamento definido

### Teste 10 — Regressão

Confirmar que o fluxo operacional normal
continua intacto.

---

## 20. CRITÉRIOS DE ACEITE

- [ ] Tela/aba de mapa criada.
- [ ] Gráfico polar/circular criado.
- [ ] Uma série por antena implementada.
- [ ] Controle de ângulo implementado.
- [ ] Botão Iniciar mapeamento implementado.
- [ ] Botão Parar mapeamento implementado.
- [ ] Botão Limpar mapa implementado.
- [ ] Marcação no mapa ao ler etiqueta implementada.
- [ ] Uso de AntennaID implementado.
- [ ] Uso de RSSI implementado.
- [ ] Tabela/log auxiliar implementada.
- [ ] Agregação de leituras implementada.
- [ ] Layout Corporate Dark preservado.
- [ ] Ferramenta isolada do fluxo operacional.
- [ ] Sem regressões no restante do sistema.

---

## 21. PROCEDIMENTO DO CODEX

Antes de implementar:

1. Ler AGENTS.md.
2. Verificar a branch atual.
3. Executar git status.
4. Identificar a tela criada no RF038.
5. Verificar suporte atual a múltiplas antenas.
6. Identificar onde o software recebe
   AntennaID e RSSI.
7. Avaliar a melhor forma de construir
   o gráfico no PySide6/QML.
8. Preservar alterações locais.

Durante a implementação:

- Reutilizar o máximo da arquitetura atual.
- Criar o modo de mapeamento
  de forma isolada.
- Não interferir no fluxo operacional.
- Construir gráfico legível e estável.
- Manter a ferramenta utilizável.

Após implementar:

1. Executar testes.
2. Validar múltiplas antenas.
3. Validar marcações no mapa.
4. Validar log auxiliar.
5. Validar limpeza do mapa.
6. Executar git diff.
7. Informar arquivos alterados
   e testes realizados.

Não executar git reset --hard.
Não descartar alterações locais.
Não realizar commit automaticamente.
Não realizar push automaticamente.
Não realizar merge automaticamente.

---

## 22. RESULTADO ESPERADO

O DSV RFID System deverá possuir
uma ferramenta visual de diagnóstico
para mapear a cobertura das antenas RFID.

Essa ferramenta deverá:

- Mostrar uma série por antena.
- Permitir selecionar ângulos de teste.
- Marcar leituras no gráfico.
- Utilizar AntennaID e RSSI.
- Exibir um mapa visual útil
  para calibração e análise.

IMPLEMENTAR O RF039.

CRIAR O MAPA DE LEITURA RFID.

UMA LINHA/SÉRIE POR ANTENA.

MARCAR LEITURAS NO MAPA.

MANTER O RECURSO ISOLADO
DO FLUXO OPERACIONAL DO PORTAL.