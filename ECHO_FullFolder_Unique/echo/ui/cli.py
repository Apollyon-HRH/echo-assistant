from __future__ import annotations

from prompt_toolkit import PromptSession
from rich.console import Console
from rich.panel import Panel

console = Console()

def run_cli(runtime):
    session_id = runtime.memory.new_session("cli")
    console.print(Panel.fit("ECHO CLI — type /help", title="ECHO"))
    ps = PromptSession()

    while True:
        try:
            text = ps.prompt("echo> ")
        except (EOFError, KeyboardInterrupt):
            break

        if not text:
            continue

        if text == "/help":
            console.print("/model /plugins /sessions /kb <query> /exit")
            continue
        if text == "/model":
            console.print(runtime.router.choose("test").name)
            continue
        if text == "/plugins":
            console.print(runtime.plugins.list())
            continue
        if text == "/sessions":
            console.print(runtime.memory.list_sessions())
            continue
        if text.startswith("/kb "):
            q = text[4:]
            from core.knowledge import KnowledgeBase
            kb = KnowledgeBase(runtime.config)
            res = kb.search(q)
            console.print([r[1]["content"][:200] for r in res])
            continue
        if text == "/exit":
            break

        result = runtime.chat(session_id, text)
        console.print(Panel(result.text, title=f"{result.model} | {result.latency_ms}ms"))
