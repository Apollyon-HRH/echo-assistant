# ECHO — Efficient Command Handler & Orchestrator

ECHO é um assistente local orientado a terminal e Telegram, com roteamento automático de modelos via Ollama, memória persistente, registro de logs e uma biblioteca de ferramentas modulares.

## O que este projeto inclui

- CLI interativa com `rich` e `prompt_toolkit`
- Bot Telegram com sessões separadas por usuário
- Roteamento automático entre quatro modelos Ollama
- Memória persistente em `sessions/`
- Logging rotativo em `logs/`
- Ferramentas locais para web, arquivos, mídia, sistema, utilitários e integrações

## Pré-requisitos

- Python 3.10+
- Ollama instalado e em execução
- Os modelos listados em `config.yaml` baixados no Ollama
- Tesseract OCR instalado no sistema, se for usar `ocr`
- Windows 11 para os atalhos `.bat` e notificações toast

## Instalação

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Instale também os modelos no Ollama:

```bash
ollama pull huihui_ai/qwen3-abliterated:14b-v2
ollama pull huihui_ai/qwen2.5-abliterate:7b
ollama pull huihui_ai/qwen2.5-coder-abliterate:14b
ollama pull huihui_ai/qwen2.5-coder-abliterate:7b
```

Depois, inicie o serviço do Ollama:

```bash
ollama serve
```

## Configuração

1. Copie `.env.example` para `.env`
2. Preencha os tokens e chaves necessários
3. Ajuste `config.yaml` se quiser alterar caminhos, logs ou modelos

### Variáveis principais

- `TELEGRAM_TOKEN`: token do bot do Telegram
- `SMTP_*`: dados de envio de e-mail
- `HOME_ASSISTANT_*`: integração opcional com Home Assistant
- `DISCORD_WEBHOOK_URL` e `SLACK_WEBHOOK_URL`: webhooks opcionais
- `IMAGE_GEN_URL`: endpoint local de geração de imagem, se houver

## Como rodar

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

## Comandos CLI

- `/help`
- `/model`
- `/switch gp|gl|cp|cl`
- `/auto`
- `/tools`
- `/reset`
- `/save`
- `/load <id>`
- `/search <query>`
- `/run <comando>`
- `/exit`

## Ferramentas incluídas

- Busca web
- Extração web
- Download
- Navegação básica
- Verificação de links
- Monitoramento de sites
- E-mail
- RSS
- Integração HTTP genérica
- Tradução
- Terminal
- Sistema de arquivos
- Diretórios
- Arquivos compactados
- Busca local
- Watchdog
- OCR
- Visão
- Geração de imagem via endpoint local
- Conversão de imagem
- Metadados
- STT
- TTS
- Cron local
- Timer
- Monitor de processos
- Criptografia
- Hash
- Senhas
- Port scanner
- Análise de logs
- Resumo
- Embeddings
- Sentimento
- Classificação
- NER
- Geração de código
- Telegram
- Discord
- Slack
- Toast
- Calendar
- Home Assistant
- Cleanup
- Backup
- Monitor
- Report
- Convert

## Estrutura

```text
echo/
├── main.py
├── config.yaml
├── .env.example
├── requirements.txt
├── start.bat
├── start_telegram.bat
├── README.md
├── core/
└── tools/
```

## Observações

- As funções são reais e executáveis.
- Algumas integrações dependem de software externo ou variáveis de ambiente.
- `image_gen` exige um endpoint local configurado em `IMAGE_GEN_URL`.
- `ocr` exige Tesseract instalado.
- `stt` exige o modelo Whisper e dependências de áudio.

## Licença

Projeto gerado sob demanda para uso pessoal e experimental.
