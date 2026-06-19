from __future__ import annotations

import base64
import os

from cryptography.fernet import Fernet

from tools._base import ToolException

def crypto(action: str, data: str, key: str | None = None) -> str:
    """Encrypt or decrypt text with Fernet."""
    try:
        if not key:
            key = Fernet.generate_key().decode()
        f = Fernet(key.encode() if isinstance(key, str) else key)
        if action == "encrypt":
            return f.encrypt(data.encode()).decode()
        if action == "decrypt":
            return f.decrypt(data.encode()).decode()
        return f"key={key}"
    except Exception as e:
        raise ToolException(str(e)) from e
