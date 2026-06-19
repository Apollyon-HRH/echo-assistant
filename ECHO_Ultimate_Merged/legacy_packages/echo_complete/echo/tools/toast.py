from core.exceptions import ToolException

def toast(title: str, message: str) -> str:
    """Show a Windows toast notification."""
    try:
        try:
            from win10toast import ToastNotifier
            ToastNotifier().show_toast(title, message, duration=5, threaded=True)
            return "Notificação exibida"
        except Exception:
            print(f"[TOAST] {title}: {message}")
            return "Notificação enviada para o console"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta toast: {e}") from e
