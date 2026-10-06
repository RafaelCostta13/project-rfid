# RF010 — Criar tela de teste e diagnóstico da Waveshare

## 1. Objetivo

Criar uma tela de teste/diagnóstico para a placa Waveshare integrada ao software RFID.

A tela deverá permitir:

- conectar à Waveshare utilizando as configurações existentes;
- visualizar em tempo real o estado das 5 entradas digitais;
- identificar quando cada entrada digital é acionada ou desacionada;
- testar manualmente os 8 relés da placa;
- ligar individualmente CH1 até CH8;
- desligar individualmente CH1 até CH8;
- visualizar o estado atual de cada relé;
- desconectar da Waveshare.

Esta funcionalidade terá finalidade de diagnóstico e validação do hardware.

Neste requisito NÃO implementar ainda a lógica operacional automática entre sensores, relés e RFID.

---

# 2. Ambiente oficial

O projeto deve ser desenvolvido, executado e testado exclusivamente em:

Windows

Não utilizar WSL como ambiente de desenvolvimento, execução ou validação deste requisito.

Considerar especialmente:

- portas seriais no formato COM;
- ambiente virtual Python do Windows;
- caminhos do Windows;
- drivers instalados no Windows;
- comunicação Modbus RTU através da porta COM.

Os testes reais com a Waveshare devem obrigatoriamente ser executados no Windows.

---

# 3. Contexto

O requisito anterior já implementou as configurações necessárias para comunicação com a Waveshare.

Já existe na tela de configurações um container contendo os parâmetros da placa, incluindo a configuração da porta COM.

O RF010 deve reutilizar integralmente essa configuração.

NÃO criar:

- segundo arquivo de configuração;
- segunda configuração de COM;
- parâmetros Modbus duplicados;
- nova fonte de configuração.

A tela de teste deve utilizar os valores atualmente configurados para a Waveshare.

---

# 4. Hardware

A placa utilizada atualmente no projeto possui:

## Entradas digitais

5 entradas:

- D1
- D2
- D3
- D4
- D5

## Saídas por relé

8 canais:

- CH1
- CH2
- CH3
- CH4
- CH5
- CH6
- CH7
- CH8

O RF010 deve contemplar todas essas entradas e saídas.

---

# 5. Acesso à tela de teste

NÃO adicionar inicialmente um novo item ao menu lateral.

O botão para acessar a tela deve ser criado dentro do container existente de configuração da Waveshare.

Este é o mesmo container que contém atualmente os inputs relacionados à comunicação serial, incluindo:

- Porta COM;
- Baud Rate;
- demais parâmetros Modbus existentes.

Adicionar nesse container um botão:

[ Testar Waveshare ]

ou:

[ Teste da Waveshare ]

Utilizar o padrão de nomenclatura e estilo visual já existente no projeto.

---

# 6. Posicionamento do botão

O botão deve ficar visualmente associado às configurações da Waveshare.

Exemplo conceitual:

Configurações Waveshare

Porta COM
[ COM5 ]

Baud Rate
[ 9600 ]

Data Bits
[ 8 ]

Parity
[ None ]

Stop Bits
[ 1 ]

Device ID
[ 1 ]

[ Testar conexão ] [ Salvar configurações ]

[ Testar Waveshare ]

O layout acima é apenas conceitual.

Antes de alterar a interface, analisar o layout atual e posicionar o botão de forma coerente com os demais componentes.

Não redesenhar a tela de configurações.

---

# 7. Comportamento do botão

Ao clicar em:

Testar Waveshare

abrir a nova tela de diagnóstico.

Essa ação NÃO deve:

- alterar configurações;
- salvar configurações;
- iniciar leitura RFID;
- iniciar automaticamente a lógica operacional;
- alterar relés automaticamente.

---

# 8. Tela de diagnóstico

Criar uma tela específica para teste da Waveshare.

Estrutura conceitual:

--------------------------------------------------
Teste da Waveshare
--------------------------------------------------

Status da conexão

● Desconectado

[ Conectar ] [ Desconectar ]


ENTRADAS DIGITAIS

D1        ● Desativado
D2        ● Desativado
D3        ● Desativado
D4        ● Desativado
D5        ● Desativado


TESTE DOS RELÉS

CH1       ● OFF       [ Ligar ] [ Desligar ]
CH2       ● OFF       [ Ligar ] [ Desligar ]
CH3       ● OFF       [ Ligar ] [ Desligar ]
CH4       ● OFF       [ Ligar ] [ Desligar ]
CH5       ● OFF       [ Ligar ] [ Desligar ]
CH6       ● OFF       [ Ligar ] [ Desligar ]
CH7       ● OFF       [ Ligar ] [ Desligar ]
CH8       ● OFF       [ Ligar ] [ Desligar ]


[ Voltar ]

--------------------------------------------------

O desenho é apenas uma referência funcional.

Manter o padrão visual existente da aplicação.

---

# 9. Conectar à Waveshare

Adicionar o botão:

Conectar

Ao clicar:

1. obter as configurações da Waveshare;
2. verificar se existe porta COM configurada;
3. abrir a comunicação serial;
4. estabelecer comunicação Modbus RTU;
5. validar uma resposta real da placa;
6. atualizar o status para `Conectado`;
7. iniciar o monitoramento das entradas digitais.

Não considerar apenas a abertura da COM como confirmação de conexão.

Deve existir resposta Modbus válida da Waveshare.

---

# 10. Configuração utilizada

A tela de teste deve utilizar a configuração existente criada no requisito anterior.

Não criar campos de configuração dentro da tela de teste.

Exemplo:

Configurações
      ↓
Waveshare
      ↓
COM5 / 9600 / 8N1 / Device ID
      ↓
Tela de teste
      ↓
WaveshareService
      ↓
Modbus RTU
      ↓
Hardware

---

# 11. COM não configurada

Caso a porta COM esteja vazia e o usuário tente conectar:

não tentar abrir a comunicação.

Exibir mensagem:

Configure a porta COM da Waveshare antes de iniciar o teste.

A aplicação deve continuar funcionando normalmente.

---

# 12. Entradas digitais

Quando houver conexão ativa, monitorar:

D1
D2
D3
D4
D5

Cada entrada deverá possuir indicação visual individual.

Exemplo:

D1    ● Ativado

ou:

D1    ● Desativado

---

# 13. Atualização em tempo real

Enquanto a Waveshare estiver conectada, a aplicação deverá realizar leituras periódicas das entradas digitais.

Quando uma entrada mudar fisicamente:

Desativado
    ↓
Ativado

a interface deverá refletir a mudança automaticamente.

Quando voltar:

Ativado
    ↓
Desativado

a interface também deverá ser atualizada.

Não exigir clique do usuário para atualizar os estados.

---

# 14. Polling

A leitura das entradas deve ocorrer através de polling Modbus em background.

O polling NÃO deve bloquear a interface.

Antes de definir o intervalo, verificar:

- implementação já existente;
- código dos testes anteriores;
- limitações da placa;
- tempo de resposta Modbus.

Utilizar um intervalo adequado para diagnóstico visual.

Não criar polling excessivamente agressivo sem necessidade.

---

# 15. Interpretação das entradas

Antes de implementar, localizar no projeto ou nos scripts anteriores a leitura Modbus que já funcionou com a Waveshare.

Confirmar:

- função Modbus utilizada;
- endereço inicial;
- quantidade de entradas;
- interpretação dos bits;
- Device ID;
- comportamento da biblioteca `pymodbus`.

NÃO adivinhar os endereços Modbus.

---

# 16. Nomes das entradas

Nesta tela de diagnóstico utilizar inicialmente:

D1
D2
D3
D4
D5

Caso o código atual já possua aliases para sensores específicos, não remover esses dados.

Porém, esta tela deve deixar claro qual entrada física está sendo monitorada.

Não inventar novas funções para D3, D4 ou D5.

---

# 17. Estado antes da conexão

Antes de existir leitura real da Waveshare, NÃO apresentar as entradas como `Desativadas`.

Utilizar:

D1    --
D2    --
D3    --
D4    --
D5    --

ou:

Desconhecido

Isso evita indicar falsamente um estado físico que ainda não foi lido.

---

# 18. Destaque visual das entradas

Deve existir diferença visual clara entre:

Ativado
Desativado
Desconhecido

Pode ser utilizado:

- indicador circular;
- badge;
- texto;
- combinação desses elementos.

Seguir o padrão visual existente.

Não utilizar somente cor como informação; manter também indicação textual.

---

# 19. Relés

A tela deve apresentar todos os 8 canais:

CH1
CH2
CH3
CH4
CH5
CH6
CH7
CH8

Cada canal deverá permitir controle manual individual.

---

# 20. Controle manual dos relés

Cada relé deve possuir:

- identificação do canal;
- indicação de estado;
- comando `Ligar`;
- comando `Desligar`.

Exemplo:

CH1     OFF     [ Ligar ] [ Desligar ]

---

# 21. Ligar relé

Ao clicar em:

Ligar

a aplicação deverá:

1. verificar se existe conexão ativa;
2. identificar o canal selecionado;
3. enviar o comando Modbus correspondente;
4. verificar a resposta do dispositivo;
5. atualizar o estado visual somente após uma resposta válida.

Exemplo:

CH4
OFF
 ↓
usuário clica Ligar
 ↓
comando Modbus
 ↓
resposta válida
 ↓
CH4 = ON

---

# 22. Desligar relé

Ao clicar em:

Desligar

realizar o processo equivalente.

Exemplo:

CH4
ON
 ↓
usuário clica Desligar
 ↓
comando Modbus
 ↓
resposta válida
 ↓
CH4 = OFF

---

# 23. Controle independente

Cada relé deve poder ser controlado independentemente.

Exemplo válido durante o teste:

CH1 = ON
CH2 = OFF
CH3 = ON
CH4 = OFF
CH5 = OFF
CH6 = ON
CH7 = OFF
CH8 = ON

Não implementar intertravamento entre os canais neste requisito.

---

# 24. Endereços dos relés

Antes de implementar o controle de CH1 até CH8, identificar no código funcional anterior ou na documentação utilizada pelo projeto:

- endereço Modbus de CH1;
- endereço Modbus de CH2;
- endereço Modbus de CH3;
- endereço Modbus de CH4;
- endereço Modbus de CH5;
- endereço Modbus de CH6;
- endereço Modbus de CH7;
- endereço Modbus de CH8;
- comando utilizado para ON;
- comando utilizado para OFF.

NÃO assumir que os canais são simplesmente endereços sequenciais sem confirmar.

---

# 25. Estado inicial dos relés

Antes da conexão, apresentar:

CH1    --
CH2    --
CH3    --
CH4    --
CH5    --
CH6    --
CH7    --
CH8    --

Não assumir `OFF` sem consultar o hardware.

---

# 26. Estado real dos relés

Se a Waveshare permitir leitura do estado atual dos relés, utilizar essa informação após conectar.

Preferir:

conectar
   ↓
consultar estados
   ↓
CH1 = estado real
CH2 = estado real
...
CH8 = estado real

em vez de assumir que todos estão desligados.

Se a implementação/hardware atual não fornecer uma forma confiável de leitura do estado dos relés, o Codex deve documentar essa limitação e não inventar estado.

---

# 27. Não executar lógica automática

Muito importante:

O estado das entradas digitais NÃO deve acionar automaticamente nenhum relé neste RF.

Por exemplo:

D1 acionado

NÃO deve automaticamente:

- ligar CH1;
- desligar CH2;
- iniciar timer;
- iniciar RFID.

A tela serve somente para diagnóstico.

---

# 28. Não implementar ainda a lógica operacional existente

Já existe uma lógica operacional definida anteriormente no projeto envolvendo sensores e relés.

Essa lógica NÃO faz parte deste requisito.

Não implementar ainda regras como:

- combinação dos sensores acionando CH1;
- início do timer acionando CH2;
- sensores desativados acionando CH3.

Essa integração será tratada em requisito posterior.

---

# 29. Independência do RFID

A tela de teste da Waveshare não deve interferir na operação do Zebra FX9600.

Durante os testes:

- não iniciar inventário RFID;
- não parar inventário RFID;
- não consultar EPC;
- não enviar EPC ao Power Automate;
- não alterar tabela de resultados;
- não alterar contador de EPCs encontrados.

Waveshare e Zebra permanecem independentes neste RF.

---

# 30. Concorrência Modbus

A aplicação terá polling das entradas digitais e comandos manuais dos relés utilizando a mesma comunicação serial.

Essas operações não devem acessar a porta serial simultaneamente de maneira não controlada.

Implementar uma estratégia adequada, conforme a arquitetura atual, como:

- lock;
- worker único;
- fila de comandos;
- serialização das operações Modbus.

Exemplo conceitual:

             ┌── leitura D1-D5
UI ──> Service ──┤
             └── comando CH1-CH8
                     │
                     ▼
              controle concorrência
                     │
                     ▼
                 Modbus RTU
                     │
                     ▼
                 Waveshare

Não permitir múltiplas operações concorrentes corrompendo a comunicação Modbus.

---

# 31. Interface responsiva durante comunicação

Nenhuma operação Modbus deve congelar a interface gráfica.

Executar fora da thread principal:

- conexão;
- polling;
- controle dos relés;
- desconexão quando necessário.

Utilizar o padrão de worker/thread já existente no projeto.

---

# 32. Perda de comunicação

Caso a Waveshare deixe de responder durante o teste:

1. identificar a falha;
2. interromper o polling;
3. tratar a conexão;
4. liberar recursos quando necessário;
5. atualizar:

Status: Desconectado

6. colocar entradas em:

Desconhecido

7. colocar estados não confirmados dos relés em:

Desconhecido

8. informar:

Comunicação com a Waveshare perdida.

A aplicação não deve fechar.

---

# 33. Falha ao controlar um relé

Se o usuário solicitar:

Ligar CH5

e o comando Modbus falhar:

NÃO alterar visualmente CH5 para ON como se a operação tivesse sido concluída.

Informar que o comando falhou.

Registrar detalhes técnicos no log.

---

# 34. Botão Desconectar

Adicionar:

[ Desconectar ]

Ao clicar:

1. interromper polling;
2. finalizar operações em andamento de maneira segura;
3. fechar o cliente Modbus;
4. fechar/liberar a porta serial;
5. atualizar o status;
6. alterar entradas para estado desconhecido;
7. alterar estados dos relés para desconhecido quando não houver mais confirmação do hardware.

---

# 35. Botão Voltar

Adicionar mecanismo para retornar à tela de configurações.

Ao sair da tela de teste, NÃO deixar o polling rodando escondido.

Se a tela estiver conectada, definir comportamento seguro:

- interromper monitoramento;
- encerrar a conexão de diagnóstico;
- liberar a COM;
- retornar à tela de configurações.

Não deixar worker órfão.

---

# 36. Fechamento da aplicação

Se o usuário fechar o software enquanto a tela de diagnóstico estiver conectada:

1. parar polling;
2. finalizar worker;
3. fechar comunicação Modbus;
4. liberar a COM;
5. permitir encerramento normal da aplicação.

---

# 37. Arquitetura

Não colocar comandos `pymodbus` diretamente nos handlers dos botões.

Preferir a separação existente no projeto.

Exemplo conceitual:

TestWaveshareView
        ↓
Controller / ViewModel
        ↓
WaveshareService
        ↓
Modbus Client
        ↓
COM
        ↓
Waveshare

Adaptar os nomes à arquitetura real.

Não criar camadas desnecessárias se o projeto já possui estrutura equivalente.

---

# 38. Reutilização

Antes de escrever novas funções, verificar o que foi criado no requisito anterior.

Reutilizar quando aplicável:

- configuração;
- cliente Modbus;
- abertura da serial;
- timeout;
- validação de conexão;
- tratamento de exceções;
- fechamento da conexão;
- logging.

Evitar duplicação.

---

# 39. Testes automatizados

Os testes automatizados comuns NÃO devem depender da Waveshare física.

Utilizar fake/mock para representar o dispositivo.

Cobrir pelo menos:

- abertura da tela;
- configuração existente;
- COM vazia;
- conexão com sucesso;
- falha de conexão;
- D1 ativado/desativado;
- D2 ativado/desativado;
- D3 ativado/desativado;
- D4 ativado/desativado;
- D5 ativado/desativado;
- CH1 ON/OFF;
- CH2 ON/OFF;
- CH3 ON/OFF;
- CH4 ON/OFF;
- CH5 ON/OFF;
- CH6 ON/OFF;
- CH7 ON/OFF;
- CH8 ON/OFF;
- erro ao acionar relé;
- perda de comunicação;
- parada do polling;
- desconexão;
- liberação da COM;
- fechamento da tela;
- fechamento da aplicação;
- prevenção de acesso concorrente à serial.

---

# 40. Teste manual — entradas digitais

No Windows:

1. conectar a Waveshare;
2. confirmar porta COM;
3. salvar a configuração;
4. abrir `Teste Waveshare`;
5. conectar;
6. confirmar `Conectado`;
7. acionar fisicamente D1;
8. confirmar alteração visual;
9. desacionar D1;
10. confirmar alteração;
11. repetir para D2;
12. repetir para D3;
13. repetir para D4;
14. repetir para D5.

---

# 41. Teste manual — relés

Com a Waveshare conectada:

1. ligar CH1;
2. confirmar acionamento físico;
3. desligar CH1;
4. repetir o teste para CH2;
5. CH3;
6. CH4;
7. CH5;
8. CH6;
9. CH7;
10. CH8.

Verificar que um comando direcionado a determinado canal não altera outro canal indevidamente.

---

# 42. Teste manual — perda de comunicação

Com a tela funcionando:

1. manter polling ativo;
2. provocar perda de comunicação de forma controlada;
3. verificar tratamento da falha;
4. confirmar que a UI não congela;
5. confirmar atualização para `Desconectado`;
6. confirmar interrupção do polling;
7. confirmar que o restante da aplicação continua funcionando.

---

# 43. Fora do escopo

NÃO implementar neste RF:

- lógica automática D1/D2;
- timer operacional;
- lógica automática CH1/CH2/CH3;
- lógica envolvendo CH4-CH8;
- acionamento automático de relés;
- integração sensores + RFID;
- início automático do Zebra;
- parada automática do Zebra;
- regras de leitura de EPC;
- histórico de sensores;
- histórico de relés;
- banco de dados;
- dashboard;
- estatísticas;
- exportação;
- configuração de regras pelo usuário.

---

# 44. Preservar funcionalidades existentes

Não alterar o comportamento atual de:

- Zebra FX9600;
- conexão LLRP;
- Start/Stop RFID;
- processamento de EPC;
- consulta Power Automate;
- tabela de itens encontrados;
- contador de EPCs encontrados;
- configurações do Zebra;
- configurações da Waveshare;
- persistência da COM;
- status de internet.

Não realizar refatorações não relacionadas ao RF010.

---

# 45. Análise obrigatória antes da implementação

Antes de modificar código, o Codex deve analisar o projeto e identificar:

1. como a tela de configurações está estruturada;
2. qual container contém as configurações da Waveshare;
3. onde adicionar o botão `Testar Waveshare`;
4. como funciona a navegação atual;
5. como retornar para Configurações;
6. como as configurações da Waveshare são carregadas;
7. serviço Modbus já existente;
8. versão instalada do `pymodbus`;
9. código dos testes físicos anteriores, se estiver no repositório;
10. endereço das 5 entradas digitais;
11. comando utilizado para leitura;
12. endereço dos 8 relés;
13. comandos ON/OFF;
14. possibilidade de consultar estado dos relés;
15. estratégia atual de threads/workers;
16. estratégia de logging;
17. pontos de cleanup ao fechar a aplicação.

Antes da implementação, apresentar resumidamente:

- arquivos que serão alterados;
- componentes que serão reutilizados;
- endereços Modbus identificados;
- estratégia de polling;
- estratégia para controle dos relés;
- estratégia para evitar concorrência.

Somente depois realizar as alterações.

---

# 46. Alterações mínimas

Implementar somente o necessário para este requisito.

Não aproveitar a tarefa para:

- reorganizar toda a aplicação;
- renomear módulos não relacionados;
- alterar arquitetura RFID;
- atualizar bibliotecas sem necessidade;
- modificar API;
- alterar configurações já funcionais;
- implementar antecipadamente a lógica automática.

Revisar o diff final para garantir que as alterações estejam limitadas ao RF010.

---

# 47. Critérios de aceite

O RF010 estará concluído quando:

1. existir botão para abrir o teste da Waveshare;
2. o botão estiver dentro do container das configurações da Waveshare;
3. a nova tela abrir corretamente;
4. utilizar a configuração existente;
5. permitir conectar;
6. permitir desconectar;
7. mostrar status da conexão;
8. mostrar D1;
9. mostrar D2;
10. mostrar D3;
11. mostrar D4;
12. mostrar D5;
13. refletir acionamento/desacionamento das entradas;
14. mostrar CH1 até CH8;
15. permitir ligar individualmente CH1-CH8;
16. permitir desligar individualmente CH1-CH8;
17. refletir estado confirmado dos relés;
18. não executar lógica automática;
19. não interferir no RFID;
20. não bloquear a interface;
21. tratar perda de comunicação;
22. impedir acesso concorrente inadequado à serial;
23. liberar a COM ao sair;
24. funcionar no ambiente Windows;
25. testes automatizados passarem;
26. funcionalidades existentes não apresentarem regressão.

---

# 48. Validação do projeto

Executar no ambiente Windows utilizando o ambiente virtual oficial do projeto.

Executar os comandos que realmente estiverem configurados no projeto.

Quando aplicável:

ruff check .
ruff format --check .
mypy src
pytest

Não assumir que uma ferramenta está instalada.

Se algum comando não fizer parte do projeto, registrar isso no relatório em vez de instalar ou alterar dependências sem necessidade.

---

# 49. Relatório final

Ao concluir, apresentar:

- análise realizada;
- arquivos alterados;
- localização do botão `Testar Waveshare`;
- estrutura da nova tela;
- configuração reutilizada;
- versão do `pymodbus`;
- endereços das entradas identificados;
- endereços dos relés identificados;
- método de leitura de D1-D5;
- método de controle de CH1-CH8;
- possibilidade ou não de leitura do estado real dos relés;
- intervalo de polling;
- estratégia de concorrência;
- comportamento em perda de comunicação;
- cleanup implementado;
- testes criados;
- testes executados;
- resultado dos testes;
- validações manuais pendentes;
- confirmação de que nenhuma lógica automática foi implementada.