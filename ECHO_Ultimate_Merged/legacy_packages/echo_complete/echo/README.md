# ECHO — Efficient Command Handler & Orchestrator

Assistente local modular para Windows 11, projetado para operar com Ollama, CLI interativa e bot Telegram.

## O que este projeto inclui

- Roteamento de modelo com quatro perfis locais
- Memória persistente por sessão
- Logger com rotação
- Registro dinâmico de ferramentas
- CLI com `rich` e `prompt_toolkit`
- Bot Telegram com sessão isolada por usuário
- 40+ ferramentas locais e integrações opcionais

## Pré-requisitos

- Python 3.10+
- Ollama em execução local
- Modelos baixados no Ollama
- Tesseract OCR (para `ocr`)
- FFmpeg/ffprobe (para `metadata` de mídia)
- Git opcionalmente

## Instalação

1. Crie um ambiente virtual.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Copie `.env.example` para `.env` e preencha os tokens necessários.
4. Garanta que o Ollama esteja rodando:
   ```bash
   ollama serve
   ```

## Modelos

Configure no Ollama os modelos usados pelo roteador:

- `huihui_ai/qwen3-abliterated:14b-v2`
- `huihui_ai/qwen2.5-abliterate:7b`
- `huihui_ai/qwen2.5-coder-abliterate:14b`
- `huihui_ai/qwen2.5-coder-abliterate:7b`

O projeto usa `num_ctx=8192` por padrão.

## Como executar

CLI:

```bash
python main.py --cli
```

Telegram:

```bash
python main.py --telegram
```

Ou use os atalhos:

- `start.bat`
- `start_telegram.bat`

## Comandos do CLI

- `/help`
- `/model`
- `/switch gp|gl|cp|cl|auto`
- `/tools`
- `/reset`
- `/save`
- `/load <id>`
- `/search <query>`
- `/run <comando>`
- `/exit`

## Ferramentas

As ferramentas ficam em `tools/` e são carregadas dinamicamente por `core/tools.py`.

## Observações práticas

Algumas integrações dependem de serviços externos ou variáveis de ambiente, por exemplo:

- Telegram
- SMTP
- GitHub/Reddit/Twitter/YouTube
- Home Assistant
- API de geração de imagem

Sem essas chaves, as funções retornam erros explícitos em vez de falhar silenciosamente.

## Estrutura de memória

- `sessions/`: sessões do chat
- `logs/`: logs rotacionados
- `memory/`: estados auxiliares
- `temp/`: arquivos temporários
