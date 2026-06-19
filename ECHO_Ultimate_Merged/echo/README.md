# ECHO — Efficient Command Handler & Orchestrator

Assistente local para Windows e Linux, com CLI e integração opcional com Telegram.

## O que este pacote inclui
- Roteamento automático entre modelos leves e pesados
- Memória persistente por sessão
- Registros em arquivo com rotação
- Loader dinâmico de ferramentas
- Ferramentas para web, arquivos, mídia, automação e análise
- Relatórios e backups locais
- Fallbacks para dependências opcionais

## Requisitos
- Python 3.10+
- Ollama rodando localmente
- Dependências listadas em `requirements.txt`
- Opcionais: Tesseract, FFmpeg, LibreTranslate, Home Assistant, SMTP, Telegram bot token

## Instalação
```bash
python -m venv .venv
source .venv/bin/activate   # no Windows use .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Execução
CLI:
```bash
python main.py --cli
```

Telegram:
```bash
python main.py --telegram
```

## Comandos principais
- `/help`
- `/model`
- `/switch gp|gl|cp|cl|auto`
- `/tools`
- `/reset`
- `/save`
- `/load <id>`
- `/search <consulta>`
- `/run <comando>`
- `/exit`

## Estrutura
- `core/` — config, logger, memória, modelos, roteamento
- `tools/` — ferramentas carregadas dinamicamente
- `logs/` — arquivo de log principal
- `sessions/` — sessões persistidas
- `memory/` — resumos e artefatos auxiliares

## Observação
Este pacote foi montado para ser extenso e modular, com muitos módulos separados para facilitar expansão posterior.
