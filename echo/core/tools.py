"""
core/tools.py - Registro e carregamento dinâmico de todas as ferramentas.
"""

import importlib
import pkgutil
import inspect
from typing import Dict, Callable, Any, Optional
from core.logger import get_logger
from core.config import CONFIG

logger = get_logger(__name__)


class ToolRegistry:
    """
    Registra e gerencia todas as ferramentas disponíveis no diretório tools/.
    Cada ferramenta é um módulo Python com uma função principal (mesmo nome do arquivo).
    """
    def __init__(self):
        self.config = CONFIG
        self.tools: Dict[str, Callable] = {}
        self.tool_metadata: Dict[str, Dict] = {}
        self._load_tools()

    def _load_tools(self):
        """Importa dinamicamente todos os módulos em tools/ que estão habilitados."""
        enabled = self.config.get("tools", {})
        import tools as tools_package
        for module_info in pkgutil.iter_modules(tools_package.__path__, tools_package.__name__ + "."):
            module_name = module_info.name.split(".")[-1]
            if module_name.startswith("_"):
                continue
            # Verifica se a ferramenta está habilitada (padrão: True)
            if not enabled.get(module_name, True):
                logger.debug(f"Ferramenta {module_name} desabilitada.")
                continue
            try:
                module = importlib.import_module(module_info.name)
                # Procura a função principal (mesmo nome do módulo)
                func = getattr(module, module_name, None)
                if func and callable(func):
                    self.tools[module_name] = func
                    # Extrai metadados da docstring
                    doc = inspect.getdoc(func) or "Sem descrição."
                    sig = inspect.signature(func)
                    params = list(sig.parameters.keys())
                    self.tool_metadata[module_name] = {
                        "description": doc.split("\n")[0],
                        "parameters": params,
                        "module": module_info.name
                    }
                    logger.debug(f"Ferramenta carregada: {module_name}")
                else:
                    logger.warning(f"Ferramenta {module_name} não possui função principal.")
            except Exception as e:
                logger.error(f"Erro ao carregar ferramenta {module_name}: {e}")

    def execute(self, tool_name: str, **kwargs) -> str:
        """Executa uma ferramenta pelo nome, passando os argumentos."""
        if tool_name not in self.tools:
            return f"Ferramenta '{tool_name}' não encontrada."
        try:
            func = self.tools[tool_name]
            result = func(**kwargs)
            return str(result)
        except TypeError as e:
            return f"Erro nos argumentos para {tool_name}: {e}"
        except Exception as e:
            logger.error(f"Erro ao executar {tool_name}: {e}")
            return f"Erro na ferramenta {tool_name}: {str(e)}"

    def get_tool_list(self) -> Dict[str, Dict]:
        """Retorna a lista de todas as ferramentas carregadas com metadados."""
        return self.tool_metadata

    def get_tool_names(self) -> list:
        """Retorna os nomes de todas as ferramentas carregadas."""
        return list(self.tools.keys())

    def is_enabled(self, tool_name: str) -> bool:
        """Verifica se uma ferramenta está habilitada no config.yaml."""
        return self.config.get("tools", {}).get(tool_name, True)