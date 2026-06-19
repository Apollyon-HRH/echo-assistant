"""Basic TCP port scanner."""

from __future__ import annotations
import socket
from ipaddress import ip_address

from tools._common import ToolException


def port_scanner(host: str, ports: str = "22,80,443", timeout: float = 0.5, limit_private: bool = False) -> str:
    """Scan a limited set of ports on a host."""
    try:
        if limit_private:
            ip = ip_address(host)
            if not (ip.is_private or ip.is_loopback):
                raise ToolException("Scanning restricted to private/local addresses when limit_private=True.")
        port_list = []
        for part in ports.split(","):
            part = part.strip()
            if "-" in part:
                a, b = part.split("-", 1)
                port_list.extend(range(int(a), int(b) + 1))
            elif part:
                port_list.append(int(part))
        out = []
        for port in sorted(set(port_list))[:256]:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            res = s.connect_ex((host, port))
            s.close()
            out.append(f"{port}: {'open' if res == 0 else 'closed'}")
        return "\n".join(out)
    except Exception as e:
        raise ToolException(f"Falha no port scanner: {e}")
