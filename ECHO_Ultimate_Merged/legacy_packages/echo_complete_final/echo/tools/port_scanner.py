from __future__ import annotations

import socket
from typing import Iterable, List

from core.exceptions import ToolException
from ._shared import json_pretty

def port_scanner(host: str, ports: str = "22,80,443", timeout: float = 0.5) -> str:
    """Scan TCP ports with socket connect attempts."""
    if not host.strip():
        raise ToolException("host cannot be empty")
    port_list = []
    for part in ports.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            port_list.extend(range(int(a), int(b) + 1))
        elif part:
            port_list.append(int(part))
    results = []
    for port in sorted(set(port_list)):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            code = s.connect_ex((host, port))
            results.append({"port": port, "open": code == 0})
        finally:
            s.close()
    return json_pretty(results)
