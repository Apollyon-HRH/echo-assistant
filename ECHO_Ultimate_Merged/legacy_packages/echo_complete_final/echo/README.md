# ECHO — Efficient Command Handler & Orchestrator

Assistente local para Windows 11, usando Ollama, com CLI e bot Telegram.

## Requisitos
- Python 3.10+
- Ollama instalado e executando
- Tesseract OCR instalado no sistema
- Opcional: Playwright, FFmpeg, LibreTranslate, Home Assistant, SMTP configurado

## Instalação
1. Extraia o ZIP.
2. Abra o terminal na pasta `echo/`.
3. Crie o ambiente virtual:
   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   ```
4. Instale dependências:
   ```bat
   pip install -r requirements.txt
   ```
5. Instale o navegador do Playwright, se for usar browser headless:
   ```bat
   playwright install
   ```
6. Copie `.env.example` para `.env` e preencha os tokens.
7. Garanta que os modelos do Ollama existam:
   ```bat
   ollama pull huihui_ai/qwen3-abliterated:14b-v2
   ollama pull huihui_ai/qwen2.5-abliterate:7b
   ollama pull huihui_ai/qwen2.5-coder-abliterate:14b
   ollama pull huihui_ai/qwen2.5-coder-abliterate:7b
   ```

## Como rodar
CLI:
```bat
python main.py --cli
```

Telegram:
```bat
python main.py --telegram
```

Ou use:
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

## Observações
- O assistente seleciona o modelo automaticamente pela regra definida em `core/model.py`.
- As sessões ficam em `sessions/`.
- Os logs ficam em `logs/echo.log`.
- Ferramentas dependentes de API falham de forma explícita quando a variável necessária não está configurada.
