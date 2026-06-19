from __future__ import annotations

import secrets
import string

from core.exceptions import ToolException

def password(length: int = 20, symbols: bool = True) -> str:
    """Generate a strong password."""
    if length < 8:
        raise ToolException("length must be >= 8")
    alphabet = string.ascii_letters + string.digits
    if symbols:
        alphabet += "!@#$%^&*()-_=+[]{};:,.?/<>"
    return "".join(secrets.choice(alphabet) for _ in range(length))
