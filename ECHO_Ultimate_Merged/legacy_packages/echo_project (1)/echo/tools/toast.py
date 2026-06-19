"""Windows toast notifications."""

from __future__ import annotations

from tools._common import ToolException

def toast(title: str, message: str) -> str:
    """Show a desktop notification on Windows."""
    try:
        try:
            from win10toast import ToastNotifier
            ToastNotifier().show_toast(title, message, duration=5, threaded=True)
            return "Toast exibido."
        except Exception:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)
            return "Toast/Mensagem exibida."
    except Exception as e:
        raise ToolException(f"Falha no toast: {e}")
