"""Entry point for ECHO CLI and Telegram bot."""

from __future__ import annotations

import argparse
import asyncio
import signal
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from core.config import CONFIG
from core.exceptions import ModelException, ToolException
from core.logger import setup_logger
from core.memory import Memory
from core.model import ModelManager
from core.routing import manual_alias, route_prompt
from core.tools import ToolRegistry

console = Console()


def estimate_tokens(messages: List[Dict[str, str]]) -> int:
    """Estimate tokens using a 4 chars/token heuristic."""
    chars = sum(len(m.get("content", "")) for m in messages)
    return chars // 4 + 1


def build_prompt(messages: List[Dict[str, str]], user_message: str) -> str:
    """Build the prompt string from message history."""
    parts = []
    for msg in messages:
        role = msg.get("role", "user").capitalize()
        parts.append(f"{role}: {msg.get('content', '')}")
    parts.append(f"User: {user_message}")
    return "\n\n".join(parts)


def split_text(text: str, max_len: int = 3900) -> List[str]:
    """Split text into chunks for Telegram or terminal display."""
    if len(text) <= max_len:
        return [text]
    chunks = []
    current = []
    length = 0
    for paragraph in text.split("\n\n"):
        paragraph_len = len(paragraph) + 2
        if length + paragraph_len > max_len and current:
            chunks.append("\n\n".join(current))
            current = [paragraph]
            length = paragraph_len
        else:
            current.append(paragraph)
            length += paragraph_len
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def process_command(command: str, state: Dict[str, str], memory: Memory, model: ModelManager, tools: ToolRegistry, session_id: str) -> str | None:
    """Handle slash commands in the CLI."""
    parts = command.strip().split()
    cmd = parts[0].lower()

    if cmd == "/help":
        return (
            "/help, /model, /switch <gp|gl|cp|cl|auto>, /tools, /reset, /save, "
            "/load <id>, /exit, /search <query>, /run <command>"
        )
    if cmd == "/model":
        return f"Modelo atual: {model.model} | modo: {state['mode']}"
    if cmd == "/switch" and len(parts) > 1:
        mode = parts[1].lower()
        state["mode"] = mode if mode in {"gp", "gl", "cp", "cl", "auto"} else "auto"
        selected = route_prompt("teste", state["mode"])
        model.set_model(CONFIG["models"][selected])
        return f"Modo alterado para {state['mode']} ({model.model})"
    if cmd == "/tools":
        return "\n".join(f"- {item['name']}: {item['description']}" for item in tools.get_tool_list())
    if cmd == "/reset":
        state["messages"] = []
        return "Sessão atual limpa."
    if cmd == "/save":
        memory.save_session(session_id, state["messages"])
        return f"Sessão salva em {session_id}"
    if cmd == "/load" and len(parts) > 1:
        loaded = memory.load_session(parts[1])
        state["messages"] = loaded
        return f"Sessão carregada: {parts[1]} ({len(loaded)} mensagens)"
    if cmd == "/search" and len(parts) > 1:
        query = " ".join(parts[1:])
        return tools.execute("web_search", query=query, num_results=3)
    if cmd == "/run" and len(parts) > 1:
        command_to_run = " ".join(parts[1:])
        return tools.execute("terminal", command=command_to_run, confirm=True)
    if cmd == "/exit":
        raise SystemExit(0)
    return None


def run_model_turn(user_input: str, state: Dict[str, str], memory: Memory, model: ModelManager) -> str:
    """Generate a model response and update session history."""
    routed = route_prompt(user_input, state.get("mode", "auto"))
    model.set_model(CONFIG["models"][routed])
    messages = state.setdefault("messages", [])
    messages.append({"role": "user", "content": user_input})
    max_tokens = int(CONFIG["context"]["max_tokens"])
    if CONFIG["context"].get("auto_summarize", True):
        messages[:] = memory.truncate(messages, max_tokens)
    prompt = build_prompt(messages[:-1], user_input) if len(messages) > 1 else user_input
    start = time.time()
    try:
        chunks = []
        for chunk in model.ask(prompt, stream=True):
            chunks.append(chunk)
            console.print(chunk, end="")
        response = "".join(chunks).strip()
        elapsed = time.time() - start
        console.print()
        console.print(Panel.fit(f"Modelo: {model.model} | Tokens: {estimate_tokens(messages)} | Tempo: {elapsed:.2f}s", title="ECHO"))
        messages.append({"role": "assistant", "content": response})
        return response
    except ModelException as exc:
        return str(exc)


def main_cli() -> None:
    """Run the interactive terminal client."""
    logger = setup_logger()
    memory = Memory()
    tools = ToolRegistry(CONFIG)
    model = ModelManager(
        model_name=CONFIG["models"]["default"],
        context_length=CONFIG["context"]["max_tokens"],
        system_prompt=CONFIG["system_prompt"],
    )
    state = {"mode": "auto", "messages": []}
    session_id = "default"

    console.print(Panel.fit("ECHO Assistant - Digite /help para comandos", style="bold blue"))
    history = FileHistory(str(Path("memory") / "cli_history.txt"))
    prompt_session = PromptSession(history=history)

    while True:
        try:
            user_input = prompt_session.prompt("ECHO> ").strip()
            if not user_input:
                continue
            if user_input.startswith("/"):
                result = process_command(user_input, state, memory, model, tools, session_id)
                if result is not None:
                    console.print(Markdown(result) if len(result) < 4000 else result[:4000])
                continue
            response = run_model_turn(user_input, state, memory, model)
            if state["messages"]:
                memory.save_session(session_id, state["messages"])
        except KeyboardInterrupt:
            console.print("\nSaindo...")
            break
        except SystemExit:
            break
        except ToolException as exc:
            console.print(f"[red]{exc}[/red]")
        except Exception as exc:
            logger.exception("CLI error: %s", exc)
            console.print(f"[red]Erro: {exc}[/red]")


async def _send_telegram_chunks(bot, chat_id: int, text: str) -> None:
    """Send long responses as chunks."""
    for chunk in split_text(text):
        await bot.send_message(chat_id=chat_id, text=chunk)


async def main_telegram() -> None:
    """Run the Telegram bot."""
    from telegram import Update
    from telegram.constants import ChatAction
    from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

    token = CONFIG.get("telegram", {}).get("token")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN is not configured")

    memory = Memory()
    tools = ToolRegistry(CONFIG)
    model = ModelManager(
        model_name=CONFIG["models"]["default"],
        context_length=CONFIG["context"]["max_tokens"],
        system_prompt=CONFIG["system_prompt"],
    )
    sessions: Dict[int, Dict[str, object]] = defaultdict(lambda: {"mode": "auto", "messages": []})

    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        state = sessions[user_id]
        text = update.message.text.strip()

        if text.startswith("/"):
            cmd = text.split()[0].lower()
            if cmd == "/start":
                await update.message.reply_text("ECHO ativo. Envie uma mensagem ou use /help.")
                return
            if cmd == "/help":
                await update.message.reply_text("Comandos: /gp /gl /cp /cl /auto /reset /search /run")
                return
            if cmd in {"/gp", "/gl", "/cp", "/cl", "/auto"}:
                state["mode"] = cmd[1:]
                await update.message.reply_text(f"Modo alterado para {state['mode']}")
                return
            if cmd == "/reset":
                state["messages"] = []
                memory.delete_session(str(user_id))
                await update.message.reply_text("Sessão limpa.")
                return
            if cmd == "/search":
                query = text.partition(" ")[2]
                result = tools.execute("web_search", query=query, num_results=3) if query else "Consulta vazia"
                await _send_telegram_chunks(context.bot, chat_id, result)
                return
            if cmd == "/run":
                command = text.partition(" ")[2]
                result = tools.execute("terminal", command=command, confirm=False) if command else "Comando vazio"
                await _send_telegram_chunks(context.bot, chat_id, result)
                return

        state["messages"].append({"role": "user", "content": text})
        model_key = route_prompt(text, state["mode"])
        model.set_model(CONFIG["models"][model_key])

        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        prompt = build_prompt(state["messages"][:-1], text) if len(state["messages"]) > 1 else text
        try:
            response_chunks = []
            last_message = await update.message.reply_text("...")
            current_text = ""
            for chunk in model.ask(prompt, stream=True):
                response_chunks.append(chunk)
                current_text += chunk
                if len(current_text) % 400 < len(chunk):
                    await last_message.edit_text(current_text[-3900:])
            response = "".join(response_chunks).strip()
            if not response:
                response = "(sem resposta)"
            await last_message.edit_text(response[:3900])
            state["messages"].append({"role": "assistant", "content": response})
            memory.save_session(str(user_id), state["messages"])
        except Exception as exc:
            await update.message.reply_text(str(exc))

    async def cmd_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await handle_text(update, context)

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", cmd_handler))
    application.add_handler(CommandHandler("help", cmd_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CommandHandler("gp", cmd_handler))
    application.add_handler(CommandHandler("gl", cmd_handler))
    application.add_handler(CommandHandler("cp", cmd_handler))
    application.add_handler(CommandHandler("cl", cmd_handler))
    application.add_handler(CommandHandler("auto", cmd_handler))
    application.add_handler(CommandHandler("reset", cmd_handler))
    application.add_handler(CommandHandler("search", cmd_handler))
    application.add_handler(CommandHandler("run", cmd_handler))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.idle()


def main() -> None:
    """Command-line entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", action="store_true", help="Modo CLI")
    parser.add_argument("--telegram", action="store_true", help="Modo Telegram")
    args = parser.parse_args()

    if args.telegram:
        asyncio.run(main_telegram())
    else:
        main_cli()


if __name__ == "__main__":
    main()
