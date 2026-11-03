# RF028 — Análise para Geração do Executável Windows

Projeto: RFID System
Tecnologias: Python, PySide6/QML, sllurp/LLRP
Sistema operacional: Windows

## Objetivo

Analisar a estrutura atual do projeto e preparar
um plano técnico para gerar um executável Windows
utilizando PyInstaller no modo --onedir.

Nesta primeira etapa, realizar somente a análise.
Não modificar arquivos e não gerar o executável.

## Atividades

1. Ler AGENTS.md e as instruções do projeto.

2. Identificar o arquivo principal responsável
   pela inicialização da aplicação.

3. Identificar a versão do Python utilizada.

4. Identificar o gerenciador de dependências
   e os arquivos de requisitos existentes.

5. Identificar todos os arquivos QML necessários.

6. Identificar os recursos visuais:
   - Logo DSV.
   - Ícones.
   - Imagens.
   - Fontes, se aplicável.

7. Identificar as dependências utilizadas:
   - PySide6.
   - sllurp.
   - Comunicação serial.
   - Cliente HTTP.
   - Demais bibliotecas necessárias.

8. Analisar como o software carrega:
   - Variáveis de ambiente.
   - Arquivos de configuração.
   - IP do Zebra FX9600.
   - Antenas RFID.
   - Porta COM Waveshare.
   - URL do Backend Rails.

9. Verificar se o código utiliza caminhos
   relativos que podem falhar no executável.

10. Identificar onde os logs são armazenados.

11. Verificar se existem arquivos que precisam
    permanecer editáveis após o empacotamento.

12. Identificar possíveis problemas relacionados
    à distribuição do PySide6/QML.

13. Avaliar a viabilidade do PyInstaller --onedir
    para a arquitetura atual.

14. Propor uma estrutura de distribuição
    que funcione sem instalação do Python
    no computador de destino.

15. Identificar os testes necessários para validar:
    - Inicialização da interface.
    - Carregamento dos recursos QML.
    - Conexão Zebra FX9600.
    - Múltiplas antenas.
    - Comunicação Waveshare.
    - Conexão com Backend Rails.
    - Leitura e classificação de EPCs.
    - Extra Box.
    - Start/Stop.
    - Configurações persistentes.

## Restrições

Não alterar:

- Lógica RFID.
- Comunicação LLRP.
- Comunicação Waveshare.
- Máquina de estados.
- Interface QML.
- Filtro de EPC.
- Extra Box.
- Backend Rails.
- Banco de dados.

Não incorporar credenciais ou segredos
de desenvolvimento no executável.

Não realizar commit ou merge.

## Entrega esperada

Apresentar um relatório contendo:

1. Arquivo principal da aplicação.
2. Dependências identificadas.
3. Recursos que precisam ser empacotados.
4. Problemas potenciais.
5. Estratégia para arquivos de configuração.
6. Estratégia para armazenamento de logs.
7. Estrutura recomendada da pasta dist.
8. Ferramenta de empacotamento recomendada.
9. Etapas necessárias para gerar o executável.
10. Plano de testes no Windows.

Ao final, informar se o projeto está pronto
para iniciar o empacotamento ou se existem
ajustes prévios necessários.

IMPORTANTE:

Não implementar o RF028 nesta etapa.

Realizar somente a análise técnica
e apresentar o plano de implementação.