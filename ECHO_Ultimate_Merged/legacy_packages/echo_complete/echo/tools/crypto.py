import base64
import os

from core.exceptions import ToolException

def crypto(action: str, text: str, key: str) -> str:
    """Encrypt or decrypt text using AES-GCM when available, otherwise Fernet."""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import hashlib
        nonce = hashlib.sha256(key.encode("utf-8")).digest()[:12]
        aes = AESGCM(hashlib.sha256(key.encode("utf-8")).digest())
        if action == "encrypt":
            ct = aes.encrypt(nonce, text.encode("utf-8"), None)
            return base64.b64encode(nonce + ct).decode("ascii")
        if action == "decrypt":
            raw = base64.b64decode(text)
            nonce, ct = raw[:12], raw[12:]
            pt = aes.decrypt(nonce, ct, None)
            return pt.decode("utf-8")
        raise ToolException("Ação inválida. Use encrypt ou decrypt.")
    except Exception as e:
        raise ToolException(f"Erro na ferramenta crypto: {e}") from e
