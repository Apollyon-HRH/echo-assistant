from __future__ import annotations

import argparse
from pathlib import Path

from api.app import create_app
from core.config import AppConfig
from core.logger import setup_logging
from core.memory import SessionMemory
from core.model import ModelRouter
from core.orchestrator import Orchestrator
from core.permissions import PermissionManager
from core.plugins import PluginManager
from core.tasks import TaskQueue
from ui.cli import run_cli

def build_runtime() -> Orchestrator:
    config = AppConfig.load(Path("config.yaml"))
    setup_logging(config.logging.level, config.logging.path, json_logs=config.logging.json)
    memory = SessionMemory(config)
    permissions = PermissionManager(config)
    plugins = PluginManager(config)
    plugins.load_all()
    router = ModelRouter(config, memory=memory)
    tasks = TaskQueue()
    return Orchestrator(config, router, memory, plugins, permissions, tasks)

def main() -> None:
    parser = argparse.ArgumentParser(prog="echo")
    parser.add_argument("--cli", action="store_true", help="Run terminal UI")
    parser.add_argument("--api", action="store_true", help="Run FastAPI app")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()

    runtime = build_runtime()

    if args.api:
        import uvicorn
        uvicorn.run(
            create_app(runtime),
            host=args.host or runtime.config.api.host,
            port=args.port or runtime.config.api.port,
            log_level="info",
        )
    else:
        run_cli(runtime)

if __name__ == "__main__":
    main()
