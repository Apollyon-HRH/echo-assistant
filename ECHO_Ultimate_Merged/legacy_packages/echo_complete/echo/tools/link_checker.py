from urllib.parse import urlparse

import requests

from core.exceptions import ToolException

def link_checker(url: str, timeout: int = 20) -> str:
    """Check whether a link is reachable and return status information."""
    try:
        resp = requests.head(url, allow_redirects=True, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code >= 400 or resp.status_code == 405:
            resp = requests.get(url, allow_redirects=True, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        return f"{url}\nstatus={resp.status_code}\nfinal={resp.url}"
    except Exception as e:
        raise ToolException(f"Erro na ferramenta link_checker: {e}") from e
