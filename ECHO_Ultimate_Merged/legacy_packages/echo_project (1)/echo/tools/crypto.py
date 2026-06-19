"""Encryption/decryption helpers."""

from __future__ import annotations
import os
from cryptography.fernet import Fernet

from tools._common import ToolException

def crypto(action: str, text: str, key: str | None = None) -> str:
    """Encrypt or decrypt text with Fernet."""
    try:
        k = key.encode() if key else os.getenv("ECHO_FERNET_KEY", "").encode()
        if not k:
            k = Fernet.generate_key()
        f = Fernet(k)
        if action == "encrypt":
            return f.encrypt(text.encode("utf-8")).decode("utf-8")
        if action == "decrypt":
            return f.decrypt(text.encode("utf-8")).decode("utf-8")
        raise ToolException("action deve ser encrypt ou decrypt")
    except Exception as e:
        raise ToolException(f"Falha em crypto: {e}")
