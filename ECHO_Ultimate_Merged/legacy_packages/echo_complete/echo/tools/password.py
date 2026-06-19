import secrets
import string

from core.exceptions import ToolException

def password(length: int = 20, include_symbols: bool = True) -> str:
    """Generate a strong random password."""
    try:
        alphabet = string.ascii_letters + string.digits
        if include_symbols:
            alphabet += "!@#$%^&*()-_=+[]{};:,.?"
        if length < 8:
            raise ToolException("length deve ser >= 8")
        return "".join(secrets.choice(alphabet) for _ in range(length))
    except Exception as e:
        raise ToolException(f"Erro na ferramenta password: {e}") from e
