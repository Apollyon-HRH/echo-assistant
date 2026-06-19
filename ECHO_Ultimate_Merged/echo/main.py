
from __future__ import annotations

import argparse
from typing import Dict, List, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from core.config import CONFIG
from core.exceptions import ModelException, ToolException
from core.logger import setup_logger
from core.memory import Memory
from core.model import ModelManager
from core.routing import route_prompt
from core.tools import ToolRegistry
from tools._shared import split_chunks

console = Console()
logger = setup_logger("echo.main")

COMMANDS = [
    "/help", "/model", "/switch", "/tools", "/reset", "/save", "/load",
    "/exit", "/search", "/run", "/auto", "/sessions", "/delete"
]

def build_prompt(messages: List[Dict[str, str]], user_message: str) -> str:
    """Build a prompt with compact turn history."""
    lines = []
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
    route = route_prompt(user_message, state.get("mode", "auto"))
    model.set_model(CONFIG["models"][route])
    prompt = build_prompt(turns, user_message)
    try:
        reply = model.ask(prompt).text
    except ModelException as exc:
        return f"[erro do modelo] {exc}"
    return reply

def main_cli() -> None:
    memory = Memory()
    tools = ToolRegistry(CONFIG)
    model = ModelManager(
        model_name=CONFIG["models"][CONFIG["models"]["default"]],
        context_length=CONFIG["context"]["max_tokens"],
        system_prompt=CONFIG["system_prompt"],
    )
    state = {"mode": "auto"}
    session_id = "cli_default"
    turns = memory.load_session(session_id)
    session = PromptSession(completer=WordCompleter(COMMANDS, ignore_case=True))

    console.print(Panel.fit("ECHO Assistant — digite /help para comandos", title="ECHO"))
    show_help(tools)

    while True:
        try:
            message = session.prompt("\nVocê> ").strip()
            if not message:
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

def telegram_placeholder() -> None:
    console.print("Modo Telegram ainda depende de configuração adicional do bot.")
    console.print("Use o CLI ou integre python-telegram-bot no mesmo padrão de memória e roteamento.")

def main() -> None:
    parser = argparse.ArgumentParser(description="ECHO — assistant framework")
    parser.add_argument("--cli", action="store_true", help="Run interactive CLI")
    parser.add_argument("--telegram", action="store_true", help="Run Telegram bot mode")
    args = parser.parse_args()

    if args.telegram:
        telegram_placeholder()
    else:
        main_cli()

if __name__ == "__main__":
    main()
