from __future__ import annotations

import socket

from tools._base import ToolException

def port_scanner(host: str, start: int = 1, end: int = 1024, timeout: float = 0.2) -> str:
    """Simple TCP port scanner."""
    try:
        open_ports = []
        for port in range(start, end + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                if s.connect_ex((host, port)) == 0:
                    open_ports.append(port)
        return ", ".join(map(str, open_ports)) if open_ports else "No open ports."
    except Exception as e:
        raise ToolException(str(e)) from e
