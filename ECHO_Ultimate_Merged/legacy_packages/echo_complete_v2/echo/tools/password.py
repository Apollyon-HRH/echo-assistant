from __future__ import annotations

import secrets
import string

from tools._base import ToolException

def password(length: int = 24) -> str:
    """Generate a strong random password."""
    try:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        return "".join(secrets.choice(alphabet) for _ in range(length))
    except Exception as e:
        raise ToolException(str(e)) from e
