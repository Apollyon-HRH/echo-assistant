from core.exceptions import ToolException
from tools._shared import timeout_run

def terminal(command: str, confirm: bool = True, timeout: int = 120) -> str:
    """Execute a shell command with optional confirmation."""
    try:
        if confirm:
            response = input(f"Executar comando? {command}\n[y/N]: ").strip().lower()
            if response not in {"y", "yes", "s", "sim"}:
                return "Execução cancelada pelo usuário."
        result = timeout_run(command, timeout=timeout, shell=True)
        output = (result.stdout or "") + (result.stderr or "")
        return output.strip() or f"Comando concluído com código {result.returncode}"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta terminal: {e}") from e
