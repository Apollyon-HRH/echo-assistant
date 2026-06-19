from __future__ import annotations

import socket
from tools._shared import json_dump
from core.exceptions import ToolException

def port_scanner(host: str, ports: list[int], timeout: float = 0.5, **kwargs) -> str:
    """Scan TCP ports on a host."""
    try:
        results = []
        for port in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            ok = s.connect_ex((host, int(port))) == 0
            s.close()
            results.append({"port": int(port), "open": ok})
        return json_dump(results)
    except Exception as exc:
        raise ToolException(f"port_scanner failed: {exc}")
