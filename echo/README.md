# ECHO — Efficient Command Handler & Orchestrator

Projeto local com CLI, API opcional, bot Telegram opcional, roteamento entre modelos Ollama, memória persistente, loader dinâmico de ferramentas e módulos de automação.

## O que há aqui
- CLI interativa no terminal
- API FastAPI opcional
- Bot Telegram opcional
- Roteamento entre modelos leves e pesados
- Memória persistente por sessão
- Ferramentas dinâmicas em `tools/`
- Plugins locais em `plugins/`
- Base de conhecimento local
- Logs estruturados

## Requisitos
- Python 3.10+
- Ollama rodando localmente
- Dependências do `requirements.txt`
- Opcional: Tesseract, FFmpeg, Telegram bot token, Home Assistant, SMTP

## Instalação
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## Execução
CLI:
```bash
python main.py --cli
```

API:
```bash
python main.py --api
```

Telegram:
```bash
python main.py --telegram
```

## Estrutura
- `core/` — configuração, memória, modelo, plugins, orquestração
- `tools/` — ferramentas carregadas dinamicamente
- `api/` — FastAPI
- `ui/` — CLI adicional
- `plugins/` — plugins locais
- `sessions/` — sessões salvas
- `memory/` — memória auxiliar e base de conhecimento
- `logs/` — arquivos de log

## Comandos CLI
- `/help`
- `/model`
- `/switch gp|gl|cp|cl|auto`
- `/tools`
- `/reset`
- `/save`
- `/load <id>`
- `/sessions`
- `/delete <id>`
- `/search <consulta>`
- `/run <comando>`
- `/exit`
