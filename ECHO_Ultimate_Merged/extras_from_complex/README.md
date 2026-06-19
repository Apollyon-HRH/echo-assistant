# ECHO — Efficient Command Hub & Orchestrator

ECHO is a local-first orchestration platform with:
- Ollama model routing
- session memory
- plugin loading
- task queue
- knowledge base search
- optional FastAPI dashboard
- safe terminal/file utilities
- audit logging and permissions

## Quick start

1. Install Python 3.10+.
2. Install Ollama and pull your preferred models.
3. Copy `.env.example` to `.env`.
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the CLI:
   ```bash
   python main.py --cli
   ```
6. Run the API:
   ```bash
   python main.py --api
   ```

## Structure

- `core/` — configuration, logging, memory, routing, plugins, permissions, tasks
- `tools/` — reusable utilities
- `api/` — FastAPI application
- `ui/` — terminal UI
- `plugins/` — example plugin
- `tests/` — basic checks

This is a substantial, modular scaffold designed to be extended into a larger local assistant platform.
