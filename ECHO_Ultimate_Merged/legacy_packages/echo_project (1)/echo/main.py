"""ECHO assistant entry point."""

from __future__ import annotations

import argparse
import asyncio
import shlex
import sys
import threading
import queue
import time
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.live import Live

from core.config import CONFIG, BASE_DIR
from core.logger import setup_logger
from core.model import ModelManager, route_model_name, count_words
from core.memory import Memory
from core.tools import ToolRegistry
from tools._common import ToolException, chunk_text, clamp_text

console = Console()


def build_prompt(model_name: str, context_tokens: int, mode: str) -> str:
    """Build the CLI prompt string."""
    return f"[bold cyan]ECHO[/bold cyan] [dim]({mode})[/dim] [yellow]{model_name}[/yellow] [dim]{context_tokens} tok[/dim] > "


def estimate_tokens(messages: list[dict[str, str]]) -> int:
    """Estimate token count from message history."""
    chars = sum(len(m.get("content", "")) for m in messages)
    return max(1, chars // 4)


def format_help() -> Panel:
    """Return a help panel."""
    text = """\
/help          mostra comandos
/model         mostra modelo atual
/switch <m>    gp | gl | cp | cl
/auto          volta ao modo automático
/tools         lista ferramentas habilitadas
/reset         limpa contexto da sessão
/save          salva a sessão
/load <id>     carrega sessão
/search <q>    busca na web
/run <cmd>     executa comando no terminal
/exit          sair
"""
    return Panel(text, title="Comandos", border_style="blue")


def build_context(memory: Memory, session_id: str, user_input: str, max_tokens: int) -> list[dict[str, str]]:
    """Load and truncate context for a session."""
    msgs = memory.load_session(session_id)
    msgs.append({"role": "user", "content": user_input})
    return memory.truncate(msgs, max_tokens)


def collect_stream(generator):
    """Collect a streaming response into chunks via a queue."""
    q: queue.Queue[str | None] = queue.Queue()

    def worker():
        try:
            for chunk in generator:
                q.put(chunk)
        except Exception as e:
            q.put(f"\n[ERRO] {e}")
        finally:
            q.put(None)

    threading.Thread(target=worker, daemon=True).start()
    return q


def cli_process_command(cmd: str, state: dict, memory: Memory, tools: ToolRegistry, model: ModelManager, logger):
    """Process a slash command in CLI mode."""
    parts = shlex.split(cmd)
    name = parts[0].lower()
    args = parts[1:]
    session_id = state["session_id"]

    if name == "/help":
        console.print(format_help())
        return
    if name == "/model":
        console.print(f"Modelo atual: [bold]{model.model}[/bold]")
        return
    if name == "/tools":
        tbl = Table(title="Ferramentas habilitadas")
        tbl.add_column("Nome")
        tbl.add_column("Descrição")
        for item in tools.get_tool_list():
            tbl.add_row(item["name"], item["description"])
        console.print(tbl)
        return
    if name == "/auto":
        state["forced"] = None
        console.print("Modo automático ativado.")
        return
    if name == "/switch":
        if not args:
            console.print("Uso: /switch gp|gl|cp|cl")
            return
        forced_map = {"gp": "geral_pesado", "gl": "geral_leve", "cp": "codigo_pesado", "cl": "codigo_leve"}
        if args[0] not in forced_map:
            console.print("Modo inválido.")
            return
        state["forced"] = args[0]
        model.set_model(CONFIG["models"][forced_map[args[0]]])
        console.print(f"Modelo forçado: {model.model}")
        return
    if name == "/reset":
        memory.save_session(session_id, [])
        console.print("Contexto limpo.")
        return
    if name == "/save":
        memory.save_session(session_id, state.get("messages", []))
        console.print("Sessão salva.")
        return
    if name == "/load":
        if not args:
            console.print("Uso: /load <id>")
            return
        loaded = memory.load_session(args[0])
        state["messages"] = loaded
        console.print(f"Sessão carregada: {args[0]} ({len(loaded)} mensagens)")
        return
    if name == "/search":
        q = " ".join(args)
        if not q:
            console.print("Uso: /search <query>")
            return
        try:
            console.print(Markdown(tools.execute("web_search", query=q, num_results=5)))
        except Exception as e:
            console.print(f"[red]{e}[/red]")
        return
    if name == "/run":
        cmdline = " ".join(args)
        if not cmdline:
            console.print("Uso: /run <comando>")
            return
        try:
            res = tools.execute("terminal", command=cmdline, confirm=True, timeout=CONFIG["timeouts"]["terminal_command"])
            console.print(Panel(res, title="Terminal"))
        except Exception as e:
            console.print(f"[red]{e}[/red]")
        return
    if name == "/exit":
        raise SystemExit
    console.print("Comando desconhecido. Use /help.")


def handle_user_prompt(user_input: str, state: dict, memory: Memory, tools: ToolRegistry, model: ModelManager, logger):
    """Process a regular user prompt."""
    session_id = state["session_id"]
    forced = state.get("forced")
    model_name = route_model_name(user_input, CONFIG["models"], forced=forced)
    model.set_model(model_name)
    history = build_context(memory, session_id, user_input, CONFIG["context"]["max_tokens"])
    context_text = "\n".join(f'{m["role"]}: {m["content"]}' for m in history)
    prompt = f"""Conversation history:
{context_text}

User:
{user_input}

Assistant:"""

    start = time.time()
    console.print(Panel.fit(f"Modelo: {model.model} | contexto: {estimate_tokens(history)} tokens", style="cyan"))
    q = collect_stream(model.ask_stream(prompt))
    rendered = ""
    with Live(console=console, refresh_per_second=8) as live:
        while True:
            item = q.get()
            if item is None:
                break
            rendered += item
            live.update(Panel(Markdown(rendered or "…"), title="ECHO", border_style="green"))
    elapsed = time.time() - start
    state.setdefault("messages", history)
    state["messages"].append({"role": "user", "content": user_input})
    state["messages"].append({"role": "assistant", "content": rendered})
    memory.save_session(session_id, memory.truncate(state["messages"], CONFIG["context"]["max_tokens"]))
    console.print(Panel(Markdown(rendered), title=f"ECHO ({elapsed:.2f}s)", border_style="green"))


def main_cli():
    """Run the interactive CLI."""
    logger = setup_logger()
    memory = Memory()
    tools = ToolRegistry(CONFIG)
    model = ModelManager(
        model_name=CONFIG["models"]["default"],
        context_length=CONFIG["context"]["max_tokens"],
        system_prompt=CONFIG["system_prompt"],
        model_map=CONFIG["models"],
    )
    session_id = "cli"
    history_path = BASE_DIR / ".echo_cli_history"
    session = PromptSession(history=FileHistory(str(history_path)))
    completer = WordCompleter(
        ["/help", "/model", "/switch", "/auto", "/tools", "/reset", "/save", "/load", "/search", "/run", "/exit"],
        ignore_case=True,
    )
    state = {"session_id": session_id, "forced": None, "messages": memory.load_session(session_id)}
    console.print(Panel.fit("ECHO Assistant - digite /help para comandos", style="bold blue"))

    while True:
        try:
            current_tokens = estimate_tokens(state.get("messages", []))
            prompt = build_prompt(model.model, current_tokens, state.get("forced", "auto") or "auto")
            user_input = session.prompt(prompt, completer=completer).strip()
            if not user_input:
                continue
            if user_input.startswith("/"):
                cli_process_command(user_input, state, memory, tools, model, logger)
            else:
                handle_user_prompt(user_input, state, memory, tools, model, logger)
        except (KeyboardInterrupt, EOFError):
            console.print("\nSaindo.")
            break
        except SystemExit:
            break
        except Exception as e:
            console.print(f"[red]Erro:[/red] {e}")
            logger.exception("CLI error")


async def telegram_stream_reply(message, model: ModelManager, prompt: str, logger):
    """Stream a response to Telegram by editing a message."""
    q: queue.Queue[str | None] = collect_stream(model.ask_stream(prompt))
    text = ""
    last_edit = 0.0
    while True:
        item = await asyncio.to_thread(q.get)
        if item is None:
            break
        text += item
        now = time.time()
        if now - last_edit >= 1.2 or len(text) > 300:
            await message.edit_text(text[-3500:])
            last_edit = now
    if text:
        await message.edit_text(text[-3500:])
    return text


def main_telegram():
    """Run the Telegram bot."""
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

    logger = setup_logger()
    if not CONFIG["telegram"]["enabled"]:
        console.print("Telegram desativado no config.yaml")
        return
    token = CONFIG["telegram"]["token"]
    if not token:
        console.print("TELEGRAM_TOKEN ausente no .env")
        return

    memory = Memory()
    tools = ToolRegistry(CONFIG)
    base_model = ModelManager(
        model_name=CONFIG["models"]["default"],
        context_length=CONFIG["context"]["max_tokens"],
        system_prompt=CONFIG["system_prompt"],
        model_map=CONFIG["models"],
    )
    states: dict[int, dict] = {}

    def get_state(user_id: int):
        st = states.setdefault(user_id, {"forced": None, "messages": memory.load_session(str(user_id))})
        return st

    async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("ECHO ativo. Envie uma mensagem ou use /help.")

    async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "/gp /gl /cp /cl /auto /reset /search /run /help"
        )

    async def cmd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str):
        st = get_state(update.effective_user.id)
        st["forced"] = mode
        await update.message.reply_text(f"Modo definido: {mode}")

    def mode_handler(mode: str):
        async def _handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await cmd_mode(update, context, mode)
        return _handler

    async def cmd_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
        st = get_state(update.effective_user.id)
        st["forced"] = None
        await update.message.reply_text("Modo automático ativado.")

    async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        states[uid] = {"forced": None, "messages": []}
        memory.save_session(str(uid), [])
        await update.message.reply_text("Sessão limpa.")

    async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = " ".join(context.args)
        if not q:
            await update.message.reply_text("Uso: /search <query>")
            return
        try:
            res = tools.execute("web_search", query=q, num_results=5)
            await update.message.reply_text(res[:3900])
        except Exception as e:
            await update.message.reply_text(str(e))

    async def cmd_run(update: Update, context: ContextTypes.DEFAULT_TYPE):
        cmdline = " ".join(context.args)
        if not cmdline:
            await update.message.reply_text("Uso: /run <comando>")
            return
        try:
            res = tools.execute("terminal", command=cmdline, confirm=False, timeout=CONFIG["timeouts"]["terminal_command"])
            await update.message.reply_text(res[:3900])
        except Exception as e:
            await update.message.reply_text(str(e))

    async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
        uid = update.effective_user.id
        st = get_state(uid)
        user_text = update.message.text.strip()
        if user_text.startswith("/"):
            return
        forced = st.get("forced")
        model_name = route_model_name(user_text, CONFIG["models"], forced=forced)
        base_model.set_model(model_name)
        hist = memory.truncate(st.get("messages", []) + [{"role": "user", "content": user_text}], CONFIG["context"]["max_tokens"])
        st["messages"] = hist
        prompt = "\n".join(f'{m["role"]}: {m["content"]}' for m in hist) + f"\nassistant:"
        msg = await update.message.reply_text("…")
        try:
            text = await telegram_stream_reply(msg, base_model, prompt, logger)
            st["messages"].append({"role": "assistant", "content": text})
            memory.save_session(str(uid), st["messages"])
        except Exception as e:
            await msg.edit_text(f"Erro: {e}")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("gp", mode_handler("geral_pesado")))
    app.add_handler(CommandHandler("gl", mode_handler("geral_leve")))
    app.add_handler(CommandHandler("cp", mode_handler("codigo_pesado")))
    app.add_handler(CommandHandler("cl", mode_handler("codigo_leve")))
    app.add_handler(CommandHandler("auto", cmd_auto))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(CommandHandler("run", cmd_run))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    console.print("Telegram bot iniciado.")
    app.run_polling(close_loop=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", action="store_true", help="Modo CLI")
    parser.add_argument("--telegram", action="store_true", help="Modo Telegram")
    args = parser.parse_args()
    if args.telegram:
        main_telegram()
    else:
        main_cli()


if __name__ == "__main__":
    main()
