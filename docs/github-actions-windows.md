# Build Windows pelo GitHub Actions

## Conceitos rápidos

O GitHub Actions executa tarefas automatizadas no GitHub. Um **workflow** é o arquivo que descreve a automação; um **job** é o conjunto de tarefas executado em uma máquina; um **step** é uma etapa do job; o **runner** é essa máquina temporária; e o **artifact** é o resultado que pode ser baixado ao final.

Neste projeto, o workflow **Build DSV RFID Windows** usa um runner Windows x64, executa testes sem hardware, gera o pacote PyInstaller e disponibiliza um ZIP para download. Ele não cria release, tag, commit ou publicação automática.

## Como iniciar

1. Envie o workflow para o GitHub e confirme que ele está na branch padrão.
2. Abra o repositório no GitHub e selecione a aba **Actions**.
3. Selecione **Build DSV RFID Windows**.
4. Clique em **Run workflow**.
5. Escolha a branch que deseja compilar e confirme.
6. Aguarde a execução terminar.

O workflow é exclusivamente manual; um `push` não inicia compilação.

## Como acompanhar e baixar

Verde significa sucesso; vermelho indica falha. Abra a execução para localizar a etapa que falhou. Em caso de sucesso, na seção **Artifacts**, baixe `DSV-RFID-Windows`.

O download do artifact contém o ZIP e o arquivo `.sha256`. Extraia o artifact, depois extraia o ZIP. Copie a pasta completa `DSV-RFID` para o computador Windows. Não copie somente `DSV-RFID.exe`.

## Configuração da estação

O pacote contém apenas `.env.example`. Crie a configuração real fora da pasta distribuída, por exemplo:

```text
C:\ProgramData\DSV-RFID\station.env
```

Execute:

```powershell
C:\DSV-RFID\DSV-RFID.exe --env-file C:\ProgramData\DSV-RFID\station.env
```

Nunca envie `station.env`, `.env`, chaves, tokens, bancos SQLite ou logs para o repositório ou para o artifact.

## Verificação do download

No PowerShell, calcule o hash do ZIP:

```powershell
(Get-FileHash .\DSV-RFID-Windows-<commit>.zip -Algorithm SHA256).Hash
```

Compare-o com o valor `SHA256` do arquivo `.sha256` baixado. O hash confirma a integridade do download; ele não substitui assinatura digital.

## Build local

O GitHub Actions não é obrigatório. Em Windows, o build local permanece:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[build-windows]"
.\.venv\Scripts\python.exe tools\build_windows.py
.\.venv\Scripts\python.exe tools\verify_windows.py
```

## Limites e segurança

O workflow usa somente permissões de leitura do repositório e não requer secrets. Seu uso está sujeito às cotas, políticas e cobrança do plano GitHub. Em **Settings → Actions → General**, confirme que Actions está habilitado, que Actions oficiais são permitidas e que o token padrão possui permissões somente de leitura quando possível.

O runner não possui Zebra FX9600, antenas, Waveshare ou sensores. O workflow valida testes simulados e o bundle; a homologação física continua obrigatória na estação operacional.
