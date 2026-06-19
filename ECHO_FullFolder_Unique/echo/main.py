from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Dict, List, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from api.app import create_app
from core.config import CONFIG, AppConfig, CONFIG_PATH
from core.exceptions import ToolException
from core.logger import setup_logger, setup_logging
from core.memory import Memory, SessionMemory
from core.model import ModelManager, ModelRouter
from core.orchestrator import Orchestrator
from core.permissions import PermissionManager
from core.plugins import PluginManager
from core.routing import route_prompt
from core.tasks import TaskQueue
from core.tools import ToolRegistry
from tools._shared import split_chunks

console = Console()
logger = setup_logger("echo.main")

COMMANDS = [
    "/help", "/model", "/switch", "/tools", "/reset", "/save", "/load",
    "/exit", "/search", "/run", "/auto", "/sessions", "/delete"
]


@dataclass
class RuntimeBundle:
    config: AppConfig
    memory: SessionMemory
    router: ModelRouter
    permissions: PermissionManager
    plugins: PluginManager
    tasks: TaskQueue
    orchestrator: Orchestrator

    def chat(self, session_id: str, prompt: str):
        return self.orchestrator.chat(session_id, prompt)



def build_prompt(messages: List[Dict[str, str]], user_message: str) -> str:
    lines: List[str] = []
    for msg in messages[-CONFIG["context"].get("max_turns", 24):]:
        role = msg.get("role", "user").upper()
        content = msg.get("content", "")
        lines.append(f"{role}: {content}")
    lines.append(f"USER: {user_message}")
    lines.append("ASSISTANT:")
    return "\n\n".join(lines)



def show_help(tools: ToolRegistry) -> None:
    tool_lines = "\n".join(f"- {t['name']}: {t['description']}" for t in tools.get_tool_list())
    md = f"""# ECHO

## Comandos
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

## Ferramentas habilitadas
{tool_lines}
"""
    console.print(Markdown(md))



def run_tool(registry: ToolRegistry, name: str, **kwargs) -> str:
    try:
        result = registry.execute(name, **kwargs)
        return result if isinstance(result, str) else str(result)
    except ToolException as exc:
        return f"Erro da ferramenta: {exc}"
    except Exception as exc:
        return f"Erro inesperado: {exc}"



def process_command(command: str, state: Dict[str, str], memory: Memory, model: ModelManager, tools: ToolRegistry, session_id: str, turns: List[Dict[str, str]]) -> Optional[str]:
    parts = command.strip().split()
    cmd = parts[0].lower()

    if cmd == "/help":
        return None
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
        turns.clear()
        return "Sessão limpa."
    if cmd == "/save":
        summary = memory.summarize_turns(turns)
        path = memory.save_session(session_id, turns, summary=summary)
        return f"Sessão salva em: {path}"
    if cmd == "/load" and len(parts) > 1:
        loaded = memory.load_session(parts[1])
        turns.clear()
        turns.extend(loaded)
        return f"Carregados {len(loaded)} turnos."
    if cmd == "/sessions":
        return "\n".join(memory.list_sessions()) or "Nenhuma sessão."
    if cmd == "/delete" and len(parts) > 1:
        ok = memory.delete_session(parts[1])
        return "Sessão removida." if ok else "Sessão não encontrada."
    if cmd == "/search" and len(parts) > 1:
        query = " ".join(parts[1:])
        return run_tool(tools, "web_search", query=query, num_results=5)
    if cmd == "/run" and len(parts) > 1:
        return run_tool(tools, "terminal", command=" ".join(parts[1:]))
    if cmd == "/auto":
        state["mode"] = "auto"
        return "Modo automático ativado."
    if cmd == "/exit":
        raise SystemExit
    return "Comando não reconhecido. Use /help."



def handle_user_message(user_message: str, state: Dict[str, str], turns: List[Dict[str, str]], memory: Memory, model: ModelManager, tools: ToolRegistry) -> str:
    route = state.get("mode", "auto")
    if route != "auto":
        selected = {"gp": "geral_pesado", "gl": "geral_leve", "cp": "codigo_pesado", "cl": "codigo_leve"}.get(route, "geral_leve")
        model.set_model(CONFIG["models"][selected])
    else:
        selected = route_prompt(user_message)
        model.set_model(CONFIG["models"][selected])

    prompt = build_prompt(turns, user_message)
    reply = model.ask(prompt)
    return reply.text



def main_cli() -> None:
    logger = setup_logger("echo.cli")
    memory = Memory()
    tools = ToolRegistry(CONFIG)
    model = ModelManager(
        model_name=CONFIG["models"][CONFIG["models"].get("default", "geral_leve")],
        context_length=CONFIG["context"].get("max_tokens", 8192),
        system_prompt=CONFIG.get("system_prompt", "")
    )
    state = {"mode": "auto"}
    session_id = "default"
    turns: List[Dict[str, str]] = memory.load_session(session_id)

    console.print(Panel.fit("ECHO Assistant - Digite /help para comandos", style="bold blue"))
    completer = WordCompleter(COMMANDS, ignore_case=True)
    session = PromptSession(completer=completer)

    while True:
        try:
            message = session.prompt("ECHO> ")
            if not message.strip():
                continue
            if message.startswith("/"):
                result = process_command(message, state, memory, model, tools, session_id, turns)
                if result is None:
                    show_help(tools)
                    continue
                console.print(result)
                continue

            memory.append_turn(turns, "user", message)
            with console.status("Pensando..."):
                reply = handle_user_message(message, state, turns, memory, model, tools)
            memory.append_turn(turns, "assistant", reply, model=model.model)
            for chunk in split_chunks(reply, 3900):
                console.print(chunk)
        except KeyboardInterrupt:
            console.print("\nInterrompido. Use /save para persistir a sessão.")
        except SystemExit:
            summary = memory.summarize_turns(turns)
            memory.save_session(session_id, turns, summary=summary)
            console.print("Encerrando...")
            break
        except Exception as exc:
            logger.exception("Erro no CLI")
            console.print(f"Erro: {exc}")



def build_runtime() -> RuntimeBundle:
    config = AppConfig.load(CONFIG_PATH)
    setup_logging(config.logging.level, config.logging.path, json_logs=config.logging.json)
    memory = SessionMemory(config)
    permissions = PermissionManager(config)
    plugins = PluginManager(config)
    plugins.load_all()
    router = ModelRouter(config, memory=memory)
    tasks = TaskQueue()
    orchestrator = Orchestrator(config, router, memory, plugins, permissions, tasks)
    return RuntimeBundle(config=config, memory=memory, router=router, permissions=permissions, plugins=plugins, tasks=tasks, orchestrator=orchestrator)



def run_api(runtime: RuntimeBundle, host: str | None = None, port: int | None = None) -> None:
    import uvicorn
    app = create_app(runtime)
    uvicorn.run(app, host=host or runtime.config.api.host, port=port or runtime.config.api.port, log_level="info")



def run_telegram(runtime: RuntimeBundle) -> None:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

    token = str(runtime.config.raw.get("telegram", {}).get("token", "") or "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN não configurado")

    allowed = set(runtime.config.raw.get("telegram", {}).get("allowed_users", []) or [])

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("ECHO ativo. Envie uma mensagem.")

    async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Comandos: /start /help /reset /sessions /model")

    async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id if update.effective_user else 0
        if allowed and user_id not in allowed:
            return
        session_id = f"tg-{user_id}"
        text = update.message.text if update.message else ""
        result = runtime.chat(session_id, text)
        await update.message.reply_text(result.text[:4000])

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_message))
    app.run_polling()



def main() -> None:
    parser = argparse.ArgumentParser(description="ECHO — assistant framework")
    parser.add_argument("--cli", action="store_true", help="Run interactive CLI")
    parser.add_argument("--api", action="store_true", help="Run API mode")
    parser.add_argument("--telegram", action="store_true", help="Run Telegram bot mode")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()

    runtime = build_runtime()

    if args.api:
        run_api(runtime, host=args.host, port=args.port)
    elif args.telegram:
        run_telegram(runtime)
    else:
        main_cli()


if __name__ == "__main__":
    main()
