from __future__ import annotations

import argparse
import asyncio
import os
import signal
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.spinner import Spinner
from rich.live import Live

from core.config import CONFIG
from core.logger import setup_logger
from core.memory import Memory
from core.model import ModelManager
from core.tools import ToolRegistry
from core.exceptions import ToolException
from tools._shared import split_chunks

console = Console()
logger = setup_logger("echo.main")

COMMANDS = [
    "/help", "/model", "/switch", "/tools", "/reset", "/save", "/load",
    "/exit", "/search", "/run", "/gp", "/gl", "/cp", "/cl", "/auto"
]

def build_prompt(history: List[dict], user_message: str) -> str:
    """Build a plain-text conversation prompt for Ollama."""
    lines = []
    for item in history[-CONFIG["context"].get("max_turns", 24):]:
        role = item.get("role", "user")
        content = item.get("content", "")
        lines.append(f"{role.upper()}: {content}")
    lines.append(f"USER: {user_message}")
    lines.append("ASSISTANT:")
    return "\n\n".join(lines)

def show_help(tools: ToolRegistry) -> None:
    """Render command and tool help."""
    tool_lines = "\n".join(f"- {t['name']}: {t['description']}" for t in tools.get_tool_list())
    md = f"""# ECHO

## Comandos
- `/help`
- `/model`
- `/switch gp|gl|cp|cl`
- `/tools`
- `/reset`
- `/save`
- `/load <id>`
- `/search <query>`
- `/run <comando>`
- `/exit`

## Ferramentas habilitadas
{tool_lines}
"""
    console.print(Markdown(md))

def parse_switch_arg(arg: str) -> str:
    arg = arg.strip().lower()
    mapping = {"gp": "gp", "gl": "gl", "cp": "cp", "cl": "cl", "auto": "auto"}
    if arg not in mapping:
        raise ValueError("Modelo inválido. Use gp, gl, cp, cl ou auto.")
    return mapping[arg]

def run_tool(registry: ToolRegistry, name: str, **kwargs) -> str:
    """Execute a tool and normalize errors."""
    try:
        result = registry.execute(name, **kwargs)
        return result if isinstance(result, str) else str(result)
    except ToolException as exc:
        return f"Erro da ferramenta: {exc}"
    except Exception as exc:
        return f"Erro inesperado: {exc}"

def main_cli() -> None:
    """Interactive CLI entry point."""
    memory = Memory()
    tools = ToolRegistry(CONFIG)
    model = ModelManager(
        model_name=CONFIG["models"]["default"],
        context_length=CONFIG["context"]["max_tokens"],
        system_prompt=CONFIG["system_prompt"],
    )
    session = PromptSession(completer=WordCompleter(COMMANDS, ignore_case=True))
    session_id = "cli_default"
    history = memory.load_session(session_id)

    console.print(Panel.fit("ECHO Assistant — digite /help para comandos", style="bold blue"))

    while True:
        try:
            current = model.current_model
            tokens = memory.count_tokens_estimate(history)
            prompt_text = f"[{current}] tokens≈{tokens}> "
            user_input = session.prompt(prompt_text).strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\nSaindo...")
            break

        if not user_input:
            continue

        if user_input in {"/exit", "exit", "quit"}:
            break

        if user_input == "/help":
            show_help(tools)
            continue

        if user_input == "/tools":
            console.print(Panel.fit("\n".join(t["name"] for t in tools.get_tool_list()), title="Ferramentas"))
            continue

        if user_input == "/model":
            console.print(f"Modelo atual: {model.current_model} | modo: {model.manual_mode}")
            continue

        if user_input.startswith("/switch "):
            try:
                mode = parse_switch_arg(user_input.split(maxsplit=1)[1])
                model.set_mode(mode)
                console.print(f"Modo alterado para: {mode}")
            except Exception as exc:
                console.print(f"[red]{exc}[/red]")
            continue

        if user_input == "/reset":
            history = []
            memory.save_session(session_id, history)
            console.print("Contexto limpo.")
            continue

        if user_input == "/save":
            path = memory.save_session(session_id, history)
            console.print(f"Sessão salva em {path}")
            continue

        if user_input.startswith("/load "):
            sid = user_input.split(maxsplit=1)[1].strip()
            history = memory.load_session(sid)
            session_id = sid
            console.print(f"Sessão carregada: {sid} ({len(history)} mensagens)")
            continue

        if user_input.startswith("/search "):
            query = user_input.split(maxsplit=1)[1].strip()
            result = run_tool(tools, "web_search", query=query, num_results=5)
            console.print(Markdown(result))
            continue

        if user_input.startswith("/run "):
            command = user_input.split(maxsplit=1)[1]
            result = run_tool(tools, "terminal", command=command, confirm=True)
            console.print(result)
            continue

        if user_input == "/gp":
            model.set_mode("gp"); console.print("Modo geral pesado ativado."); continue
        if user_input == "/gl":
            model.set_mode("gl"); console.print("Modo geral leve ativado."); continue
        if user_input == "/cp":
            model.set_mode("cp"); console.print("Modo código pesado ativado."); continue
        if user_input == "/cl":
            model.set_mode("cl"); console.print("Modo código leve ativado."); continue
        if user_input == "/auto":
            model.set_mode("auto"); console.print("Modo automático ativado."); continue

        history.append({"role": "user", "content": user_input})
        if CONFIG["context"].get("auto_summarize", True):
            history = memory.summarize_if_needed(history, CONFIG["context"]["max_tokens"])

        prompt = build_prompt(history, user_input)
        start = time.perf_counter()
        buffer = []
        with Live(Panel.fit("Respondendo...", title="ECHO"), console=console, refresh_per_second=10) as live:
            try:
                chunks = model.ask_stream(prompt)
                for chunk in chunks:
                    buffer.append(chunk)
                    live.update(Panel.fit("".join(buffer)[-3000:], title=f"ECHO · {model.current_model}"))
            except Exception as exc:
                live.update(Panel.fit(f"Erro: {exc}", title="ECHO"))
                console.print(f"[red]{exc}[/red]")
                continue

        answer = "".join(buffer).strip()
        elapsed = time.perf_counter() - start
        history.append({"role": "assistant", "content": answer})
        memory.save_session(session_id, history)
        console.print(Panel(Markdown(answer or "(vazio)"), title=f"ECHO · {model.current_model} · {elapsed:.2f}s"))

def main_telegram() -> None:
    """Run the Telegram bot using python-telegram-bot."""
    try:
        from telegram import Update
        from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
    except Exception as exc:
        raise SystemExit(f"python-telegram-bot não está instalado: {exc}")

    token = CONFIG.get("env", {}).get("telegram_token")
    if not token:
        raise SystemExit("TELEGRAM_TOKEN não configurado no .env")

    memory = Memory()
    tools = ToolRegistry(CONFIG)
    model = ModelManager(
        model_name=CONFIG["models"]["default"],
        context_length=CONFIG["context"]["max_tokens"],
        system_prompt=CONFIG["system_prompt"],
    )

    def user_session_id(update: Update) -> str:
        return f"tg_{update.effective_user.id}"

    def format_session(history: List[dict], user_message: str) -> str:
        return build_prompt(history, user_message)

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("ECHO ativo. Envie uma mensagem ou use /help.")

    async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Comandos: /gp /gl /cp /cl /auto /reset /search /run. "
            "Envie texto normal para conversar."
        )

    async def mode_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text(f"Modo atual: {model.manual_mode}")
            return
        mode = parse_switch_arg(context.args[0])
        model.set_mode(mode)
        await update.message.reply_text(f"Modo alterado para {mode}")

    async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        sid = user_session_id(update)
        memory.save_session(sid, [])
        await update.message.reply_text("Contexto limpo.")

    async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = " ".join(context.args).strip()
        if not query:
            await update.message.reply_text("Use: /search <consulta>")
            return
        result = run_tool(tools, "web_search", query=query, num_results=5)
        await update.message.reply_text(result[:4000])

    async def run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        command = " ".join(context.args).strip()
        if not command:
            await update.message.reply_text("Use: /run <comando>")
            return
        result = run_tool(tools, "terminal", command=command, confirm=True)
        await update.message.reply_text(result[:4000])

    async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
        text = update.message.text.strip()
        if text.startswith("/"):
            return
        sid = user_session_id(update)
        history = memory.load_session(sid)
        history.append({"role": "user", "content": text})
        history = memory.summarize_if_needed(history, CONFIG["context"]["max_tokens"])
        prompt = format_session(history, text)

        sent = await update.message.reply_text("…")
        buffer = []
        last_edit = time.time()
        try:
            for chunk in model.ask_stream(prompt):
                buffer.append(chunk)
                if time.time() - last_edit > 1.2:
                    preview = "".join(buffer)
                    await sent.edit_text(preview[-4000:] or "…")
                    last_edit = time.time()
            answer = "".join(buffer).strip()
        except Exception as exc:
            await sent.edit_text(f"Erro: {exc}")
            return

        history.append({"role": "assistant", "content": answer})
        memory.save_session(sid, history)
        chunks = split_chunks(answer, CONFIG["telegram"].get("max_message_length", 3500))
        await sent.edit_text(chunks[0][:4000] if chunks else answer[:4000])
        for extra in chunks[1:]:
            await update.message.reply_text(extra[:4000])

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("gp", mode_cmd))
    app.add_handler(CommandHandler("gl", mode_cmd))
    app.add_handler(CommandHandler("cp", mode_cmd))
    app.add_handler(CommandHandler("cl", mode_cmd))
    app.add_handler(CommandHandler("auto", mode_cmd))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(CommandHandler("search", search_cmd))
    app.add_handler(CommandHandler("run", run_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.run_polling(allowed_updates=CONFIG["telegram"]["allowed_updates"])

def main() -> None:
    parser = argparse.ArgumentParser(description="ECHO local assistant")
    parser.add_argument("--cli", action="store_true", help="Run CLI mode")
    parser.add_argument("--telegram", action="store_true", help="Run Telegram bot")
    args = parser.parse_args()

    if args.telegram and args.cli:
        print("Escolha apenas um modo.")
        raise SystemExit(1)

    if args.telegram:
        main_telegram()
    else:
        main_cli()

if __name__ == "__main__":
    main()
