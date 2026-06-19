
"""Entry point for ECHO: CLI and Telegram bot."""
from __future__ import annotations

import argparse
import asyncio
import shlex
import signal
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from prompt_toolkit import PromptSession
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from core.config import CONFIG
from core.exceptions import OllamaError, ToolException
from core.logger import setup_logger
from core.memory import Memory
from core.model import ModelManager
from core.tools import ToolRegistry

console = Console()

CODE_KEYS = {
    "código", "função", "script", "debug", "algoritmo", "parser", "compilador",
    "injetar", "exploit", "buffer", "overflow", "reverse", "engenharia reversa",
    "assembly", "ponteiro", "malloc", "fork", "thread", "socket", "payload", "shellcode",
}
GENERAL_KEYS = {"explique", "detalhe", "teoria", "história", "filosofia", "por que", "como funciona", "significado"}


@dataclass
class RoutingState:
    """Manual routing override state."""
    mode: str = "auto"  # auto, gp, gl, cp, cl


def count_words(text: str) -> int:
    """Count approximate word count."""
    return len(text.strip().split())


def choose_model(prompt: str, config: Dict[str, Dict[str, str]], manual_mode: str = "auto") -> str:
    """Select a model according to the prompt and manual override rules."""
    if manual_mode == "gp":
        return config["models"]["geral_pesado"]
    if manual_mode == "gl":
        return config["models"]["geral_leve"]
    if manual_mode == "cp":
        return config["models"]["codigo_pesado"]
    if manual_mode == "cl":
        return config["models"]["codigo_leve"]

    lower = prompt.lower()
    words = count_words(prompt)
    if any(key in lower for key in CODE_KEYS):
        return config["models"]["codigo_pesado"] if words >= 10 else config["models"]["codigo_leve"]
    if any(key in lower for key in GENERAL_KEYS):
        return config["models"]["geral_pesado"]
    if words > 30:
        return config["models"]["geral_pesado"]
    return config["models"]["geral_leve"]


def format_help(tools: ToolRegistry) -> str:
    """Build a rich help message."""
    tool_names = ", ".join(sorted(tools.tools.keys()))
    return (
        "Comandos:\n"
        " /help, /model, /switch <gp|gl|cp|cl|auto>, /tools, /reset, /save, /load <id>, /exit\n"
        " /search <query>, /run <comando>\n\n"
        "Ferramentas habilitadas:\n "
        f"{tool_names or '(nenhuma)'}\n\n"
        "Observação: o roteamento automático segue as regras definidas no prompt."
    )


def parse_command(line: str) -> Tuple[str, List[str]]:
    """Split a command line using shell-like rules."""
    parts = shlex.split(line)
    if not parts:
        return "", []
    return parts[0], parts[1:]


def summarize_if_needed(memory: Memory, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Trim memory to stay within the token budget."""
    max_tokens = CONFIG["context"]["max_tokens"]
    return memory.truncate(messages, max_tokens)


def call_tool_shortcut(name: str, args: List[str], tools: ToolRegistry) -> str:
    """Call a tool using shortcut commands."""
    if name == "search":
        query = " ".join(args)
        return tools.execute("web_search", query=query, num_results=5)
    if name == "run":
        command = " ".join(args)
        return tools.execute("terminal", command=command, confirm=True, timeout=CONFIG["timeouts"]["terminal_command"])
    raise ToolException(f"Comando desconhecido: /{name}")


def print_model_response(model: ModelManager, prompt: str) -> str:
    """Stream a model response to the console and return the accumulated text."""
    start = time.time()
    chunks: List[str] = []
    stream = model.ask(prompt, stream=True)
    if isinstance(stream, str):
        console.print(Panel(Markdown(stream), title=f"ECHO • {model.model}"))
        return stream
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Respondendo...", total=None)
        for chunk in stream:
            chunks.append(chunk)
            progress.update(task, description="Respondendo...")
    elapsed = time.time() - start
    response = "".join(chunks).strip()
    console.print(Panel(Markdown(response or "(sem resposta)"), title=f"ECHO • {model.model} • {elapsed:.2f}s"))
    return response


def run_cli() -> None:
    """Run the interactive CLI."""
    logger = setup_logger()
    memory = Memory()
    tools = ToolRegistry(CONFIG)
    session_id = "default"
    routing = RoutingState()
    model = ModelManager(CONFIG["models"]["default"], CONFIG["context"]["max_tokens"], CONFIG["system_prompt"])

    console.print(Panel.fit("ECHO Assistant", subtitle="Digite /help para comandos", style="bold blue"))
    prompt_session = PromptSession()

    def _sigint(_signum, _frame):
        console.print("\nEncerrando...")
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _sigint)

    while True:
        try:
            line = prompt_session.prompt(f"ECHO[{model.model}]> ")
            if not line.strip():
                continue
            if line.strip() in {"/exit", "exit", "quit"}:
                break
            if line.startswith("/switch"):
                _, args = parse_command(line)
                if not args:
                    console.print("Uso: /switch gp|gl|cp|cl|auto")
                    continue
                routing.mode = args[0]
                model.set_model(choose_model("", CONFIG, routing.mode))
                console.print(f"Modo definido para {routing.mode}.")
                continue
            if line == "/reset":
                session_id = "default"
                memory.save_session(session_id, [])
                console.print("Sessão reiniciada.")
                continue
            if line.startswith("/load"):
                _, args = parse_command(line)
                if not args:
                    console.print("Uso: /load <id>")
                    continue
                session_id = args[0]
                console.print(f"Sessão carregada: {session_id}")
                continue
            if line == "/save":
                messages = memory.load_session(session_id)
                memory.save_session(session_id, messages)
                console.print(f"Sessão salva: {session_id}")
                continue
            if line == "/model":
                console.print(f"Modelo atual: {model.model} | modo: {routing.mode}")
                continue
            if line in {"/tools", "/help"}:
                console.print(format_help(tools))
                continue
            if line.startswith("/search"):
                _, args = parse_command(line)
                console.print(Panel(Markdown(call_tool_shortcut("search", args, tools)), title="web_search"))
                continue
            if line.startswith("/run"):
                _, args = parse_command(line)
                console.print(Panel(Markdown(call_tool_shortcut("run", args, tools)), title="terminal"))
                continue
            if line.startswith("/"):
                console.print("Comando não reconhecido.")
                continue

            selected = choose_model(line, CONFIG, routing.mode)
            model.set_model(selected)
            messages = memory.load_session(session_id)
            messages.append({"role": "user", "content": line})
            memory.save_session(session_id, summarize_if_needed(memory, messages))
            response = print_model_response(model, line)
            messages = memory.load_session(session_id)
            messages.append({"role": "assistant", "content": response})
            memory.save_session(session_id, summarize_if_needed(memory, messages))
        except KeyboardInterrupt:
            break
        except Exception as exc:
            logger.exception("CLI error")
            console.print(f"[red]Erro: {exc}[/red]")



def run_telegram() -> None:
    """Run the Telegram bot."""
    from telegram import Update
    from telegram.constants import ChatAction
    from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

    token = CONFIG["telegram"]["token"]
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN não configurado")

    memory = Memory()
    tools = ToolRegistry(CONFIG)
    routing_map: Dict[int, RoutingState] = {}
    model = ModelManager(CONFIG["models"]["default"], CONFIG["context"]["max_tokens"], CONFIG["system_prompt"])
    logger = setup_logger("echo.telegram")

    def get_state(user_id: int) -> RoutingState:
        return routing_map.setdefault(user_id, RoutingState())

    async def reply_text(update: Update, text: str) -> None:
        if update.message:
            await update.message.reply_text(text)

    async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await reply_text(update, "ECHO pronto. Use /help para comandos.")

    async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await reply_text(update, format_help(tools))

    async def cmd_switch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        state = get_state(user_id)
        cmd = update.message.text.split()[0].lstrip("/") if update.message else "auto"
        state.mode = {"gp": "gp", "gl": "gl", "cp": "cp", "cl": "cl", "auto": "auto"}.get(cmd, "auto")
        if context.args:
            state.mode = context.args[0]
        await reply_text(update, f"Modo definido para {state.mode}")

    async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        session_id = str(update.effective_user.id)
        memory.save_session(session_id, [])
        await reply_text(update, "Sessão resetada.")

    async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = " ".join(context.args)
        result = tools.execute("web_search", query=query, num_results=5)
        await reply_text(update, result)

    async def cmd_run(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        command = " ".join(context.args)
        result = tools.execute("terminal", command=command, confirm=False, timeout=CONFIG["timeouts"]["terminal_command"])
        await reply_text(update, result)

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message or not update.message.text:
            return
        user_id = update.effective_user.id
        state = get_state(user_id)
        session_id = str(user_id)
        selected = choose_model(update.message.text, CONFIG, state.mode)
        model.set_model(selected)
        messages = memory.load_session(session_id)
        messages.append({"role": "user", "content": update.message.text})
        memory.save_session(session_id, summarize_if_needed(memory, messages))
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        try:
            response = await asyncio.to_thread(model.ask_sync, update.message.text)
            messages = memory.load_session(session_id)
            messages.append({"role": "assistant", "content": response})
            memory.save_session(session_id, summarize_if_needed(memory, messages))
            await reply_text(update, response)
        except Exception as exc:
            logger.exception("Telegram error")
            await reply_text(update, f"Erro: {exc}")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("gp", cmd_switch))
    app.add_handler(CommandHandler("gl", cmd_switch))
    app.add_handler(CommandHandler("cp", cmd_switch))
    app.add_handler(CommandHandler("cl", cmd_switch))
    app.add_handler(CommandHandler("auto", cmd_switch))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(CommandHandler("run", cmd_run))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


def main_cli() -> None:
    """Entry point for CLI mode."""
    run_cli()


def main_telegram() -> None:
    """Entry point for Telegram mode."""
    run_telegram()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", action="store_true", help="Modo CLI")
    parser.add_argument("--telegram", action="store_true", help="Modo Telegram")
    args = parser.parse_args()
    if args.telegram:
        main_telegram()
    else:
        main_cli()
