"""
core/model.py - Gerenciador de modelos Ollama com alternância inteligente,
fallback, streaming, otimização de contexto e descarregamento automático.
"""

import json
import requests
import time
from typing import Generator, Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from core.logger import get_logger
from core.config import CONFIG

logger = get_logger(__name__)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_PS_URL = "http://localhost:11434/api/ps"
OLLAMA_STOP_URL = "http://localhost:11434/api/stop"


class ModelManager:
    """
    Gerencia os modelos Ollama, com:
    - Alternância automática baseada em palavras-chave e comprimento.
    - Comandos manuais para forçar modelo (/gp, /gl, /cp, /cl).
    - Streaming de respostas.
    - Fallback para modelo leve em caso de falha.
    - Descarregamento automático do modelo anterior para economizar VRAM.
    - Otimização de contexto (truncagem e sumarização).
    """
    def __init__(self):
        self.config = CONFIG
        self.models = self.config["models"]
        self.default_model = self.models.get("default", "geral_leve")
        self.context_length = self.config["context"]["max_tokens"]
        self.system_prompt = self.config["system_prompt"]
        self.current_model_name = self.default_model
        self.current_model_tag = self.models[self.default_model]
        self.history: List[Dict[str, str]] = []
        self.executor = ThreadPoolExecutor(max_workers=2)

    def set_model(self, model_key: str) -> str:
        """Troca o modelo atual, descarregando o anterior."""
        if model_key not in self.models:
            logger.warning(f"Modelo '{model_key}' não encontrado. Mantendo '{self.current_model_name}'.")
            return self.current_model_name
        old_tag = self.current_model_tag
        new_tag = self.models[model_key]
        if old_tag != new_tag:
            self._unload_model(old_tag)
            self.current_model_name = model_key
            self.current_model_tag = new_tag
            logger.info(f"Modelo alterado para: {model_key} ({new_tag})")
        return self.current_model_name

    def _unload_model(self, model_tag: str) -> None:
        """Descarrega o modelo da VRAM via API do Ollama."""
        try:
            resp = requests.post(OLLAMA_STOP_URL, json={"model": model_tag}, timeout=5)
            if resp.status_code == 200:
                logger.debug(f"Modelo {model_tag} descarregado.")
            else:
                logger.warning(f"Falha ao descarregar {model_tag}: {resp.text}")
        except Exception as e:
            logger.warning(f"Erro ao descarregar {model_tag}: {e}")

    def _detect_model(self, prompt: str) -> str:
        """Detecta automaticamente qual modelo usar baseado no prompt."""
        prompt_lower = prompt.lower()
        words = prompt.split()
        # Palavras que indicam código pesado
        code_keywords = [
            "código", "função", "script", "debug", "algoritmo", "parser",
            "compilador", "injetar", "exploit", "buffer", "overflow",
            "reverse", "engenharia reversa", "assembly", "ponteiro",
            "malloc", "fork", "thread", "socket", "payload", "shellcode",
            "heap", "stack", "registro", "interrupção", "syscall",
            "kernel", "driver", "firmware", "boot", "UEFI", "BIOS"
        ]
        # Palavras que indicam raciocínio profundo
        deep_keywords = [
            "explique", "detalhe", "teoria", "história", "filosofia",
            "por que", "como funciona", "significado", "contexto",
            "implicação", "fundamento", "paradigma", "ontologia",
            "epistemologia", "metafísica", "lógica", "dialética"
        ]
        # Verifica palavras-chave de código
        if any(kw in prompt_lower for kw in code_keywords):
            if len(words) > 15:
                return "codigo_pesado"
            else:
                return "codigo_leve"
        # Verifica palavras-chave de raciocínio profundo
        if any(kw in prompt_lower for kw in deep_keywords) or len(words) > 30:
            return "geral_pesado"
        # Padrão: leve
        return "geral_leve"

    def _build_prompt(self, user_prompt: str) -> str:
        """Constrói o prompt completo com system prompt e histórico."""
        messages = [f"System: {self.system_prompt}"]
        for msg in self.history[-self.context_length//4:]:
            messages.append(f"{msg['role'].capitalize()}: {msg['content']}")
        messages.append(f"User: {user_prompt}")
        return "\n".join(messages)

    def ask(self, prompt: str, stream: bool = True, force_model: Optional[str] = None) -> Generator[str, None, None]:
        """
        Envia uma pergunta ao modelo, com streaming opcional.
        Se force_model for fornecido, usa esse modelo (ex: "gp", "gl", "cp", "cl").
        """
        # Determina o modelo
        if force_model and force_model in self.models:
            model_key = force_model
        else:
            model_key = self._detect_model(prompt)
        model_tag = self.models[model_key]
        # Se mudou de modelo, descarrega o anterior
        if self.current_model_tag != model_tag:
            self._unload_model(self.current_model_tag)
            self.current_model_name = model_key
            self.current_model_tag = model_tag
            logger.info(f"Alternância automática: usando {model_key} ({model_tag})")
        # Constrói prompt
        full_prompt = self._build_prompt(prompt)
        payload = {
            "model": model_tag,
            "prompt": full_prompt,
            "stream": stream,
            "options": {
                "num_ctx": self.context_length,
                "temperature": 0.2,  # baixo para respostas mais determinísticas
                "top_p": 0.9,
                "repeat_penalty": 1.1,
                "stop": ["\nSystem:", "\nUser:"]
            }
        }
        logger.debug(f"Enviando prompt para {model_tag} (ctx: {self.context_length})")
        try:
            if stream:
                response = requests.post(OLLAMA_API_URL, json=payload, stream=True, timeout=180)
                response.raise_for_status()
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode())
                            chunk = data.get("response", "")
                            if chunk:
                                full_response += chunk
                                yield chunk
                        except json.JSONDecodeError:
                            continue
                # Adiciona ao histórico após completar
                self.history.append({"role": "user", "content": prompt})
                self.history.append({"role": "assistant", "content": full_response})
                # Trunca histórico se necessário
                self._truncate_history()
            else:
                response = requests.post(OLLAMA_API_URL, json=payload, timeout=180)
                response.raise_for_status()
                data = response.json()
                full_response = data.get("response", "")
                self.history.append({"role": "user", "content": prompt})
                self.history.append({"role": "assistant", "content": full_response})
                self._truncate_history()
                yield full_response
        except requests.exceptions.Timeout:
            logger.error("Timeout na requisição ao Ollama")
            yield "Erro: Tempo limite excedido. Tente novamente."
        except requests.exceptions.ConnectionError:
            logger.error("Ollama não está rodando")
            yield "Erro: Ollama não está em execução. Execute 'ollama serve'."
        except Exception as e:
            logger.error(f"Erro na chamada ao Ollama: {e}")
            # Fallback para modelo leve
            if model_key != "geral_leve" and "codigo_leve" in self.models:
                logger.warning("Tentando fallback para modelo leve...")
                yield from self.ask(prompt, stream, force_model="geral_leve")
            else:
                yield f"Erro: {str(e)}"

    def ask_sync(self, prompt: str, force_model: Optional[str] = None) -> str:
        """Versão síncrona (sem streaming) para uso em ferramentas."""
        result = ""
        for chunk in self.ask(prompt, stream=False, force_model=force_model):
            result += chunk
        return result

    def _truncate_history(self):
        """Trunca o histórico para não exceder max_tokens (estimativa 4 chars/token)."""
        max_chars = self.context_length * 4
        total = sum(len(msg["content"]) for msg in self.history)
        while total > max_chars and len(self.history) > 2:
            # Remove a mensagem mais antiga (exceto a primeira do sistema)
            removed = self.history.pop(1) if self.history[0]["role"] == "system" else self.history.pop(0)
            total -= len(removed["content"])
            logger.debug(f"Histórico truncado: removida mensagem de {removed['role']}")

    def reset_history(self):
        """Reseta o histórico da conversa."""
        self.history = []
        logger.info("Histórico resetado.")

    def get_current_model(self) -> str:
        """Retorna o nome do modelo atual."""
        return self.current_model_name

    def get_context_usage(self) -> Dict[str, Any]:
        """Retorna estatísticas do contexto atual."""
        total_chars = sum(len(msg["content"]) for msg in self.history)
        estimated_tokens = total_chars // 4
        return {
            "model": self.current_model_name,
            "history_messages": len(self.history),
            "estimated_tokens": estimated_tokens,
            "max_tokens": self.context_length,
            "usage_percent": round((estimated_tokens / self.context_length) * 100, 2)
        }