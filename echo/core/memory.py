"""
core/memory.py - Gerenciamento de sessões e memória persistente.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from core.config import CONFIG
from core.logger import get_logger

logger = get_logger(__name__)

class MemoryManager:
    def __init__(self):
        self.base_path = CONFIG["context"]["history_path"]
        os.makedirs(self.base_path, exist_ok=True)
        self.max_tokens = CONFIG["context"]["max_tokens"]

    def create_session(self) -> str:
        """Cria uma nova sessão com ID baseado em timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"session_{timestamp}"
        return session_id

    def save_session(self, session_id: str, history: List[Dict[str, str]]) -> bool:
        """Salva o histórico em um arquivo JSON."""
        if not history:
            logger.debug(f"Sessão {session_id} vazia, não salva.")
            return False
        filepath = os.path.join(self.base_path, f"{session_id}.json")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            logger.debug(f"Sessão {session_id} salva ({len(history)} mensagens).")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar sessão {session_id}: {e}")
            return False

    def load_session(self, session_id: str) -> Optional[List[Dict[str, str]]]:
        """Carrega o histórico de uma sessão."""
        filepath = os.path.join(self.base_path, f"{session_id}.json")
        if not os.path.exists(filepath):
            logger.debug(f"Sessão {session_id} não encontrada.")
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                history = json.load(f)
            logger.debug(f"Sessão {session_id} carregada ({len(history)} mensagens).")
            return history
        except Exception as e:
            logger.error(f"Erro ao carregar sessão {session_id}: {e}")
            return None

    def list_sessions(self) -> List[str]:
        """Lista todas as sessões salvas."""
        files = os.listdir(self.base_path)
        sessions = [f.replace(".json", "") for f in files if f.endswith(".json")]
        return sorted(sessions, reverse=True)

    def delete_session(self, session_id: str) -> bool:
        """Deleta uma sessão."""
        filepath = os.path.join(self.base_path, f"{session_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.debug(f"Sessão {session_id} deletada.")
            return True
        return False