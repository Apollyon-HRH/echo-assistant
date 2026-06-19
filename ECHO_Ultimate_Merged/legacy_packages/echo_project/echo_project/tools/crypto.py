"""Crypto tool."""

from __future__ import annotations

import json

from core.exceptions import ToolException
from tools._common import json_dump, normalize_url, read_text_file, write_text_file, safe_filename, ensure_parent, download_stream, run_subprocess, sha256_bytes, now_iso

def crypto(text: str, action: str = "encrypt", password: str | None = None, **kwargs) -> str:
    """Encrypt or decrypt data using a password-derived key."""
    try:
        from cryptography.fernet import Fernet
        import base64, hashlib
        password = password or "echo-default-password"
        key = base64.urlsafe_b64encode(hashlib.sha256(password.encode("utf-8")).digest())
        f = Fernet(key)
        if action == "encrypt":
            return f.encrypt(text.encode("utf-8")).decode("utf-8")
        if action == "decrypt":
            return f.decrypt(text.encode("utf-8")).decode("utf-8")
        raise ToolException("Invalid action")
    except Exception as e:
        raise ToolException(f"Erro na ferramenta: {e}")
