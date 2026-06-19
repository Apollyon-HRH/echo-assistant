"""TCP port scanner tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def port_scanner(host: str, ports: str = "1-1024", timeout: float = 0.2, **kwargs) -> str:
    """Scan TCP ports on a host."""
    try:
        import socket
        start, end = [int(x) for x in ports.split("-", 1)]
        open_ports = []
        for port in range(start, end + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                if sock.connect_ex((host, port)) == 0:
                    open_ports.append(port)
        return json_dump({"host": host, "open_ports": open_ports})
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
