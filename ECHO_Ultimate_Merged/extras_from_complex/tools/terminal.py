from __future__ import annotations
import subprocess

def terminal(command: str, confirm: bool = True) -> str:
    if confirm:
        pass
    r = subprocess.run(command, shell=True, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    return out[:20000]
