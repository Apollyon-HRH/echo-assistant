import socket

from core.exceptions import ToolException

def port_scanner(host: str, start_port: int = 1, end_port: int = 1024, timeout: float = 0.3) -> str:
    """Scan a small range of TCP ports."""
    try:
        open_ports = []
        for port in range(start_port, end_port + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                if s.connect_ex((host, port)) == 0:
                    open_ports.append(port)
        return ", ".join(map(str, open_ports)) if open_ports else "Nenhuma porta aberta encontrada."
    except Exception as e:
        raise ToolException(f"Erro na ferramenta port_scanner: {e}") from e
