from __future__ import annotations

from tools._base import ToolException

def toast(title: str, message: str) -> str:
    """Show a Windows toast notification when available."""
    try:
        from win10toast import ToastNotifier
        t = ToastNotifier()
        t.show_toast(title, message, duration=5, threaded=True)
        return "shown"
    except Exception as e:
        raise ToolException(str(e)) from e
