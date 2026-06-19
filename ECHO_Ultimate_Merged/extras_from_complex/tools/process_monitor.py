from __future__ import annotations
import psutil

def process_monitor() -> str:
    procs = []
    for p in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_percent"]):
        info = p.info
        procs.append(f'{info["pid"]} {info["name"]} cpu={info["cpu_percent"]} mem={info["memory_percent"]}')
    return "\n".join(procs[:50])
