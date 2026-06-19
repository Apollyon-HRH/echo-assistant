"""Password generation."""

from __future__ import annotations
import secrets
import string

from tools._common import ToolException

def password(length: int = 20, symbols: bool = True) -> str:
    """Generate a random password."""
    if length < 4:
        raise ToolException("length muito curto.")
    alphabet = string.ascii_letters + string.digits + (string.punctuation if symbols else "")
    return "".join(secrets.choice(alphabet) for _ in range(length))
