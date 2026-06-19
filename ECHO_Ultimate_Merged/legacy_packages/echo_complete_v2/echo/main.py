from __future__ import annotations

import argparse
import asyncio
import os
import shlex
import time
from dataclasses import dataclass, field
from typing import List

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner

from core.config import CONFIG
from core.logger import setup_logger
from core.memory import Memory
from core.model import ModelManager
from core.tools import ToolRegistry
from tools._base import ToolException

console = Console()
logger = setup_logger()

@dataclass
class SessionState:
    session_id: str
    forced_mode: str = "auto"
    messages: List[dict] = field(default_factory=list)

def compose_prompt(history: List[dict], user_text: str) -> str:
    transcript = []
    for msg in history[-12:]:
        transcript.append(f"{msg['role'].upper()}: {msg['content']}")
    transcript.append(f"USER: {user_text}")
    transcript.append("ASSISTANT:")
    return "\n".join(transcript)

def parse_command(text: str) -> tuple[str, list[str]]:
    parts = shlex.split(text)
    return parts[0].lower(), parts[1:]

def handle_manual_mode(state: SessionState, cmd: str) -> str | None:
    mapping = {"/gp": "gp", "/gl": "gl", "/cp": "cp", "/cl": "cl", "/auto": "auto"}
    if cmd in mapping:
        state.forced_mode = mapping[cmd]
        return f"Mode set to {state.forced_mode}"
    return None

def execute_command(text: str, tools: ToolRegistry, memory: Memory, state: SessionState) -> str:
    cmd, args = parse_command(text)
    if cmd in {"/gp", "/gl", "/cp", "/cl", "/auto"}:
        return handle_manual_mode(state, cmd) or ""
    if cmd == "/help":
        return (
            "Commands: /help /model /tools /switch <gp|gl|cp|cl|auto> /reset /save /load <id> "
            "/search <query> /run <command> /exit"
        )
    if cmd == "/tools":
        return "\n".join(f"- {t['name']}: {t['description']}" for t in tools.get_tool_list())
    if cmd == "/model":
        return f"current={state.forced_mode}"
    if cmd == "/switch":
        if not args:
            return "Usage: /switch <gp|gl|cp|cl|auto>"
        state.forced_mode = args[0]
        return f"Mode set to {state.forced_mode}"
    if cmd == "/reset":
        state.messages.clear()
        memory.delete_session(state.session_id)
        return "Session reset."
    if cmd == "/save":
        memory.save_session(state.session_id, state.messages)
        return f"Saved session {state.session_id}"
    if cmd == "/load":
        if not args:
            return "Usage: /load <session_id>"
        state.session_id = args[0]
        state.messages = memory.load_session(state.session_id)
        return f"Loaded session {state.session_id}"
    if cmd == "/search":
        from tools.web_search import web_search
        return web_search(" ".join(args), num_results=5)
    if cmd == "/run":
        from tools.terminal import terminal
        return terminal(" ".join(args), confirm=False)
    raise ToolException(f"Unknown command: {cmd}")

def print_banner(model: ModelManager, session_id: str) -> None:
    console.print(
        Panel.fit(
            f"[bold]ECHO[/bold] | model: [cyan]{model.model_key}[/cyan] | session: [magenta]{session_id}[/magenta]\n"
            f"[dim]Use /help for commands[/dim]",
            title="ECHO Assistant",
        )
    )

def ask_model(model: ModelManager, prompt: str, stream: bool = True) -> str:
    start = time.time()
    buffer: list[str] = []
    if stream:
        spinner = Spinner("dots", text="Streaming...")
        with Live(spinner, console=console, refresh_per_second=12) as live:
            for chunk in model.ask_stream(prompt):
                buffer.append(chunk)
                spinner.text = f"{model.model_key}: {''.join(buffer)[-80:]}"
                live.update(spinner)
    else:
        buffer.append(model.ask_sync(prompt))
    elapsed = time.time() - start
    text = "".join(buffer).strip()
    console.print(f"[dim]({elapsed:.2f}s)[/dim]")
    return text

def main_cli() -> None:
    memory = Memory()
    tools = ToolRegistry(CONFIG)
    model = ModelManager(
        model_name=CONFIG["models"]["default"],
        context_length=CONFIG["context"]["max_tokens"],
        system_prompt=CONFIG["system_prompt"],
    )
    state = SessionState(session_id="cli_default")
    print_banner(model, state.session_id)
    session = PromptSession(history=InMemoryHistory())

    while True:
        try:
            user_text = session.prompt("ECHO> ").strip()
            if not user_text:
                continue
            if user_text in {"/exit", "exit", "quit"}:
                break

            if user_text.startswith("/"):
                result = execute_command(user_text, tools, memory, state)
                if result:
                    console.print(Markdown(result))
                continue

            decision = model.choose_model(user_text, manual=None if state.forced_mode == "auto" else state.forced_mode)
            model.set_model(decision.model_name)

            history = memory.load_session(state.session_id)
            history.append({"role": "user", "content": user_text})
            prompt = compose_prompt(history, user_text)
            console.print(f"[dim]model={decision.model_key} tokens≈{len(prompt)//4}[/dim]")
            response = ask_model(model, prompt, stream=True)
            console.print(Markdown(response or "_no response_"))
            history.append({"role": "assistant", "content": response})
            state.messages = history
            if CONFIG["context"]["save_history"]:
                memory.save_session(state.session_id, memory.truncate(history, CONFIG["context"]["max_tokens"]))
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            logger.exception("CLI error")
            console.print(f"[red]{e}[/red]")

def main_telegram() -> None:
    token = CONFIG.get("telegram", {}).get("token") or os.getenv("TELEGRAM_TOKEN", "")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN missing")
    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
    except Exception as e:
        raise RuntimeError(f"python-telegram-bot unavailable: {e}") from e

    memory = Memory()
    tools = ToolRegistry(CONFIG)
    model = ModelManager(
        model_name=CONFIG["models"]["default"],
        context_length=CONFIG["context"]["max_tokens"],
        system_prompt=CONFIG["system_prompt"],
    )
    states: dict[int, SessionState] = {}

    def get_state(user_id: int) -> SessionState:
        if user_id not in states:
            states[user_id] = SessionState(session_id=f"tg_{user_id}")
        return states[user_id]

    async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("ECHO online. Use /help for commands.")

    async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Commands: /help /gp /gl /cp /cl /auto /reset /search /run")

    async def cmd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str):
        st = get_state(update.effective_user.id)
        st.forced_mode = mode
        await update.message.reply_text(f"Mode set to {mode}")

    async def gp(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await cmd_mode(update, context, "gp")

    async def gl(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await cmd_mode(update, context, "gl")

    async def cp(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await cmd_mode(update, context, "cp")

    async def cl(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await cmd_mode(update, context, "cl")

    async def auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await cmd_mode(update, context, "auto")

    async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
        st = get_state(update.effective_user.id)
        st.messages.clear()
        memory.delete_session(st.session_id)
        await update.message.reply_text("Session reset.")

    async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
        from tools.web_search import web_search
        query = " ".join(context.args)
        await update.message.reply_text(web_search(query, num_results=5)[:4000])

    async def cmd_run(update: Update, context: ContextTypes.DEFAULT_TYPE):
        from tools.terminal import terminal
        out = terminal(" ".join(context.args), confirm=False)
        await update.message.reply_text(out[:4000])

    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        st = get_state(user_id)
        text = update.message.text.strip()

        if text.startswith("/"):
            cmd = text.split()[0].lower()
            if cmd in {"/gp", "/gl", "/cp", "/cl", "/auto"}:
                mapping = {"/gp": "gp", "/gl": "gl", "/cp": "cp", "/cl": "cl", "/auto": "auto"}
                st.forced_mode = mapping[cmd]
                await update.message.reply_text(f"Mode set to {st.forced_mode}")
                return
            if cmd == "/help":
                await cmd_help(update, context); return
            if cmd == "/reset":
                await cmd_reset(update, context); return
            if cmd == "/search":
                await cmd_search(update, context); return
            if cmd == "/run":
                await cmd_run(update, context); return

        decision = model.choose_model(text, manual=None if st.forced_mode == "auto" else st.forced_mode)
        model.set_model(decision.model_name)
        history = memory.load_session(st.session_id)
        history.append({"role": "user", "content": text})
        prompt = compose_prompt(history, text)

        msg = await update.message.reply_text("Streaming...")
        chunks: list[str] = []
        try:
            for chunk in model.ask_stream(prompt):
                chunks.append(chunk)
                if len("".join(chunks)) % 200 < 50:
                    await msg.edit_text("".join(chunks)[-3500:])
            answer = "".join(chunks).strip()
        except Exception as e:
            answer = f"Error: {e}"
        await msg.edit_text(answer[:4000])
        history.append({"role": "assistant", "content": answer})
        memory.save_session(st.session_id, memory.truncate(history, CONFIG["context"]["max_tokens"]))

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("gp", gp))
    app.add_handler(CommandHandler("gl", gl))
    app.add_handler(CommandHandler("cp", cp))
    app.add_handler(CommandHandler("cl", cl))
    app.add_handler(CommandHandler("auto", auto))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(CommandHandler("run", cmd_run))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

def main() -> None:
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
