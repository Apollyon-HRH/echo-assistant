#!/usr/bin/env python3
"""
ECHO - Assistente pessoal local com Ollama.
"""

import sys
import os
import asyncio
import signal
import argparse
from typing import Optional

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter

from core.config import CONFIG
from core.logger import setup_logger, get_logger
from core.model import ModelManager
from core.memory import MemoryManager
from core.tools import ToolRegistry

console = Console()
logger = get_logger(__name__)

# Comandos especiais
COMMANDS = {
    "/help": "Mostra esta ajuda.",
    "/gp": "Força modelo geral pesado (14B).",
    "/gl": "Força modelo geral leve (7B).",
    "/cp": "Força modelo código pesado (14B).",
    "/cl": "Força modelo código leve (7B).",
    "/auto": "Volta à alternância automática.",
    "/reset": "Reseta o histórico da conversa.",
    "/model": "Mostra o modelo atual e uso de contexto.",
    "/tools": "Lista ferramentas disponíveis.",
    "/save": "Salva a sessão atual.",
    "/load <id>": "Carrega uma sessão anterior.",
    "/list": "Lista sessões salvas.",
    "/delete <id>": "Deleta uma sessão.",
    "/search <query>": "Busca na web (atalho).",
    "/run <comando>": "Executa comando no terminal (atalho).",
    "/exit": "Sai do assistente.",
}

class ECHOAssistant:
    def __init__(self, mode="cli"):
        self.mode = mode
        self.model = ModelManager()
        self.memory = MemoryManager()
        self.tools = ToolRegistry()
        self.session_id = self.memory.create_session()
        # Carrega histórico da sessão se existir
        hist = self.memory.load_session(self.session_id)
        if hist:
            self.model.history = hist
        self.running = True
        self.command_completer = WordCompleter(list(COMMANDS.keys()) + self.tools.get_tool_names())

    def run_cli(self):
        """Modo CLI interativo com prompt_toolkit."""
        console.print(Panel.fit(
            "[bold blue]ECHO Assistant[/bold blue] - Digite [bold]/help[/bold] para comandos",
            border_style="blue"
        ))
        session = PromptSession(history=FileHistory(".echo_history"))
        while self.running:
            try:
                user_input = session.prompt(
                    ">>> ",
                    completer=self.command_completer,
                    auto_suggest=AutoSuggestFromHistory(),
                ).strip()
                if not user_input:
                    continue
                self._process_input(user_input)
            except KeyboardInterrupt:
                console.print("\n[bold yellow]Sessão interrompida. Digite /exit para sair.[/bold yellow]")
            except EOFError:
                break
            except Exception as e:
                console.print(f"[bold red]Erro:[/bold red] {e}")

    def _process_input(self, user_input: str):
        """Processa a entrada do usuário (comandos ou perguntas)."""
        # Comandos especiais
        if user_input.startswith("/"):
            self._handle_command(user_input)
            return
        # Verifica se é uma ferramenta (atalho)
        if user_input.startswith("!") or user_input.startswith("."):
            parts = user_input.split(" ", 1)
            tool_name = parts[0][1:]
            args = parts[1] if len(parts) > 1 else ""
            if tool_name in self.tools.get_tool_names():
                with console.status(f"[bold green]Executando ferramenta {tool_name}...[/bold green]"):
                    result = self.tools.execute(tool_name, query=args) if args else self.tools.execute(tool_name)
                console.print(Panel(result, title=f"🔧 {tool_name}", border_style="cyan"))
                return
            else:
                console.print(f"[bold red]Ferramenta '{tool_name}' não encontrada.[/bold red]")
                return
        # Pergunta normal
        with console.status("[bold green]Processando...[/bold green]", spinner="dots"):
            try:
                full_response = ""
                with Live(console=console, refresh_per_second=10) as live:
                    live.update(Text("Recebendo resposta...", style="yellow"))
                    for chunk in self.model.ask(user_input, stream=True):
                        full_response += chunk
                        live.update(Text(full_response, style="white"))
                console.print()
                # Exibe resposta final com Markdown
                if full_response:
                    console.print(Markdown(full_response))
                # Salva sessão automaticamente
                self.memory.save_session(self.session_id, self.model.history)
            except Exception as e:
                console.print(f"[bold red]Erro:[/bold red] {e}")

    def _handle_command(self, cmd: str):
        """Processa comandos especiais."""
        parts = cmd.split(" ", 1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if command == "/help":
            table = Table(title="Comandos ECHO", border_style="blue")
            table.add_column("Comando", style="cyan")
            table.add_column("Descrição")
            for c, desc in COMMANDS.items():
                table.add_row(c, desc)
            console.print(table)

        elif command == "/gp":
            self.model.set_model("geral_pesado")
            console.print("[bold green]Modelo alterado para: Geral Pesado (14B)[/bold green]")

        elif command == "/gl":
            self.model.set_model("geral_leve")
            console.print("[bold green]Modelo alterado para: Geral Leve (7B)[/bold green]")

        elif command == "/cp":
            self.model.set_model("codigo_pesado")
            console.print("[bold green]Modelo alterado para: Código Pesado (14B)[/bold green]")

        elif command == "/cl":
            self.model.set_model("codigo_leve")
            console.print("[bold green]Modelo alterado para: Código Leve (7B)[/bold green]")

        elif command == "/auto":
            self.model.set_model(self.model.default_model)
            console.print("[bold green]Alternância automática restaurada.[/bold green]")

        elif command == "/reset":
            self.model.reset_history()
            self.memory.save_session(self.session_id, [])
            console.print("[bold yellow]Histórico resetado.[/bold yellow]")

        elif command == "/model":
            usage = self.model.get_context_usage()
            console.print(Panel(
                f"[bold]Modelo atual:[/bold] {usage['model']}\n"
                f"[bold]Mensagens:[/bold] {usage['history_messages']}\n"
                f"[bold]Tokens estimados:[/bold] {usage['estimated_tokens']}/{usage['max_tokens']} ({usage['usage_percent']}%)",
                title="📊 Status do Modelo",
                border_style="green"
            ))

        elif command == "/tools":
            tools = self.tools.get_tool_list()
            if not tools:
                console.print("[yellow]Nenhuma ferramenta carregada.[/yellow]")
                return
            table = Table(title="Ferramentas Disponíveis", border_style="cyan")
            table.add_column("Nome", style="green")
            table.add_column("Descrição")
            table.add_column("Parâmetros")
            for name, meta in tools.items():
                table.add_row(name, meta["description"], ", ".join(meta["parameters"]))
            console.print(table)

        elif command == "/save":
            self.memory.save_session(self.session_id, self.model.history)
            console.print(f"[bold green]Sessão {self.session_id} salva.[/bold green]")

        elif command == "/list":
            sessions = self.memory.list_sessions()
            if not sessions:
                console.print("[yellow]Nenhuma sessão salva.[/yellow]")
                return
            for s in sessions:
                console.print(f"[cyan]{s}[/cyan]")

        elif command == "/load":
            if not arg:
                console.print("[yellow]Use: /load <id>[/yellow]")
                return
            hist = self.memory.load_session(arg)
            if hist is not None:
                self.model.history = hist
                self.session_id = arg
                console.print(f"[bold green]Sessão {arg} carregada.[/bold green]")
            else:
                console.print(f"[red]Sessão {arg} não encontrada.[/red]")

        elif command == "/delete":
            if not arg:
                console.print("[yellow]Use: /delete <id>[/yellow]")
                return
            if self.memory.delete_session(arg):
                console.print(f"[bold green]Sessão {arg} deletada.[/bold green]")
            else:
                console.print(f"[red]Sessão {arg} não encontrada.[/red]")

        elif command == "/search":
            if not arg:
                console.print("[yellow]Use: /search <consulta>[/yellow]")
                return
            with console.status(f"[bold green]Buscando: {arg}...[/bold green]"):
                result = self.tools.execute("web_search", query=arg, num_results=5)
            console.print(Panel(result, title="🔍 Resultados da Busca", border_style="cyan"))

        elif command == "/run":
            if not arg:
                console.print("[yellow]Use: /run <comando>[/yellow]")
                return
            if Confirm.ask(f"[bold yellow]Executar comando: {arg}?[/bold yellow]"):
                with console.status("[bold green]Executando...[/bold green]"):
                    result = self.tools.execute("terminal", command=arg, confirm=False)
                console.print(Panel(result, title="💻 Terminal", border_style="green"))

        elif command == "/exit":
            self.running = False
            console.print("[bold blue]Até logo![/bold blue]")

        else:
            console.print(f"[red]Comando desconhecido: {command}. Digite /help para ajuda.[/red]")

    # ========== Modo Telegram ==========
    def run_telegram(self):
        """Inicia o bot do Telegram (async)."""
        try:
            from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
            from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
        except ImportError:
            console.print("[red]python-telegram-bot não instalado. Instale com: pip install python-telegram-bot[/red]")
            return

        token = os.getenv("TELEGRAM_TOKEN")
        if not token:
            console.print("[red]TELEGRAM_TOKEN não definido no .env[/red]")
            return

        # Configuração do bot
        application = Application.builder().token(token).build()

        # Comandos
        async def start(update: Update, context: CallbackContext):
            await update.message.reply_text(
                "🧠 ECHO Assistant online!\n"
                "Comandos: /help para ajuda, /model para ver modelo atual."
            )

        async def help_command(update: Update, context: CallbackContext):
            help_text = "Comandos disponíveis:\n" + "\n".join([f"{c}: {d}" for c, d in COMMANDS.items()])
            await update.message.reply_text(help_text)

        async def handle_message(update: Update, context: CallbackContext):
            user_id = str(update.effective_user.id)
            # Carrega sessão do usuário
            session_id = f"telegram_{user_id}"
            hist = self.memory.load_session(session_id)
            if hist:
                self.model.history = hist
            else:
                self.model.history = []
            user_text = update.message.text or ""
            # Processa comandos do Telegram
            if user_text.startswith("/"):
                # Redireciona para o handler de comandos via CLI adaptado
                # (simplificação: apenas alguns comandos)
                if user_text == "/reset":
                    self.model.reset_history()
                    self.memory.save_session(session_id, [])
                    await update.message.reply_text("Histórico resetado.")
                    return
                elif user_text == "/model":
                    usage = self.model.get_context_usage()
                    await update.message.reply_text(
                        f"Modelo: {usage['model']}\nTokens: {usage['estimated_tokens']}/{usage['max_tokens']} ({usage['usage_percent']}%)"
                    )
                    return
                elif user_text.startswith("/search"):
                    query = user_text[8:].strip()
                    if not query:
                        await update.message.reply_text("Use: /search <consulta>")
                        return
                    result = self.tools.execute("web_search", query=query)
                    await update.message.reply_text(result[:4000])
                    return
                # Outros comandos podem ser adicionados
            # Resposta normal
            await update.message.reply_text("Processando...")
            full_response = ""
            try:
                for chunk in self.model.ask(user_text, stream=True):
                    full_response += chunk
                # Salva histórico
                self.memory.save_session(session_id, self.model.history)
                # Envia resposta (dividida se muito longa)
                if len(full_response) > 4000:
                    for i in range(0, len(full_response), 4000):
                        await update.message.reply_text(full_response[i:i+4000])
                else:
                    await update.message.reply_text(full_response)
            except Exception as e:
                await update.message.reply_text(f"Erro: {e}")

        # Registra handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        console.print("[bold green]Bot do Telegram iniciado![/bold green]")
        application.run_polling()

    def run(self):
        """Ponto de entrada principal."""
        if self.mode == "telegram":
            self.run_telegram()
        else:
            self.run_cli()


def main():
    parser = argparse.ArgumentParser(description="ECHO Assistant")
    parser.add_argument("--cli", action="store_true", help="Modo CLI (padrão)")
    parser.add_argument("--telegram", action="store_true", help="Modo Telegram")
    parser.add_argument("--query", "-q", type=str, help="Modo one-shot: pergunta única")
    args = parser.parse_args()

    # Configura logs
    setup_logger()

    # Modo one-shot
    if args.query:
        model = ModelManager()
        console.print(f"[bold cyan]ECHO:[/bold cyan]")
        for chunk in model.ask(args.query, stream=True):
            console.print(chunk, end="")
        console.print()
        return

    # Modo normal
    mode = "telegram" if args.telegram else "cli"
    assistant = ECHOAssistant(mode=mode)
    try:
        assistant.run()
    except KeyboardInterrupt:
        console.print("\n[bold blue]Encerrando...[/bold blue]")

if __name__ == "__main__":
    main()