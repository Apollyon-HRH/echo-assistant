# ECHO

ECHO (Efficient Command Handler & Orchestrator) é um assistente local para Windows 11 com Ollama, CLI interativa e bot Telegram.

## Requisitos

- Python 3.10+
- Ollama instalado e em execução
- Modelos baixados no Ollama:
  - `huihui_ai/qwen3-abliterated:14b-v2`
  - `huihui_ai/qwen2.5-abliterate:7b`
  - `huihui_ai/qwen2.5-coder-abliterate:14b`
  - `huihui_ai/qwen2.5-coder-abliterate:7b`
- Tesseract OCR, FFmpeg e dependências do sistema para voz/imagem quando usar essas ferramentas
- Windows 11 (testado para este alvo)

## Instalação

1. Extraia o ZIP.
2. Crie e ative um ambiente virtual.
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Copie `.env.example` para `.env` e preencha os tokens.
5. Inicie o Ollama:
   ```bash
   ollama serve
   ```
6. Baixe os modelos:
   ```bash
   ollama pull huihui_ai/qwen3-abliterated:14b-v2
   ollama pull huihui_ai/qwen2.5-abliterate:7b
   ollama pull huihui_ai/qwen2.5-coder-abliterate:14b
   ollama pull huihui_ai/qwen2.5-coder-abliterate:7b
   ```

## Como executar

CLI:
```bash
python main.py --cli
```

Telegram:
```bash
python main.py --telegram
```

Ou use os arquivos `.bat`.

## Comandos da CLI

- `/help`
- `/model`
- `/switch gp`
- `/switch gl`
- `/switch cp`
- `/switch cl`
- `/switch auto`
- `/tools`
- `/reset`
- `/save`
- `/load <id>`
- `/exit`
- `/search <query>`
- `/run <comando>`

## Comandos do Telegram

- `/start`
- `/help`
- `/gp`
- `/gl`
- `/cp`
- `/cl`
- `/auto`
- `/reset`
- `/search <query>`
- `/run <comando>`

## Estrutura

O projeto foi organizado em:
- `core/` para configuração, modelo, memória, logs e registro de ferramentas
- `tools/` para as funções utilitárias
- `sessions/`, `logs/`, `memory/`, `temp/` para dados locais

## Observações

- O sistema carrega um modelo por vez.
- O roteamento automático segue regras por palavras-chave e tamanho da mensagem.
- O histórico é salvo em JSON por sessão.
- Ferramentas externas podem exigir instalação adicional do software correspondente.
