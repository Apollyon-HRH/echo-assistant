from __future__ import annotations

from core.exceptions import ToolException

def toast(title: str, message: str) -> str:
    """Show a Windows toast notification when supported."""
    try:
        try:
            from win10toast import ToastNotifier  # type: ignore
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=5, threaded=True)
            return "Toast shown"
        except Exception:
            from winotify import Notification  # type: ignore
            toast = Notification(app_id="ECHO", title=title, msg=message)
            toast.show()
            return "Toast shown"
    except Exception as exc:
        raise ToolException(f"toast failed: {exc}") from exc
