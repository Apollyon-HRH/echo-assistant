# ECHO — Efficient Command Handler & Orchestrator

ECHO é um assistente local para Windows 11 com execução via Ollama, CLI interativa e bot do Telegram.

## O que este projeto entrega

- Roteamento automático entre 4 modelos locais do Ollama.
- Streaming de resposta no CLI e no Telegram.
- Memória persistente por sessão em JSON.
- Logger com rotação.
- Registro dinâmico de ferramentas em `tools/`.
- Conjunto amplo de ferramentas reais: web, arquivos, terminal, mídia, monitoramento, integrações e utilitários.

## Requisitos

- Python 3.10+
- Ollama rodando localmente
- Windows 11
- Tesseract, se for usar OCR
- FFmpeg, se for trabalhar com áudio/vídeo em alguns fluxos
- Dependências Python em `requirements.txt`

## Instalação

1. Crie e ative um ambiente virtual.
2. Instale dependências:

```bash
pip install -r requirements.txt
```

3. Copie `.env.example` para `.env` e preencha os tokens.
4. Inicie o Ollama:

```bash
ollama serve
```

5. Faça o pull dos modelos configurados no `config.yaml`.

## Execução

CLI:

```bash
python main.py --cli
```

Telegram:

```bash
python main.py --telegram
```

Ou use os arquivos `.bat`.

## Comandos do CLI

- `/help`
- `/tools`
- `/model`
- `/switch`
- `/reset`
- `/save`
- `/load <id>`
- `/search <consulta>`
- `/run <comando>`
- `/gp`
- `/gl`
- `/cp`
- `/cl`
- `/auto`
- `/exit`

## Estrutura

- `core/`: config, logger, memória, modelo e registry de ferramentas
- `tools/`: ferramentas implementadas
- `sessions/`: histórico persistente
- `logs/`: logs rotativos
- `memory/`: estado auxiliar
- `temp/`: arquivos temporários

## Observações

Algumas ferramentas dependem de serviços externos ou bibliotecas opcionais. Quando faltarem dependências ou credenciais, elas falham com mensagem explícita em vez de quebrar o projeto inteiro.
