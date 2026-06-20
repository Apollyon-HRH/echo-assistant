#!/usr/bin/env python3
"""
Teste completo do ECHO Assistant.
Testa todos os modelos, ferramentas e comandos.
"""

import sys
import os
import json
import subprocess
import time
from pathlib import Path

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.model import ModelManager
from core.tools import ToolRegistry
from core.config import CONFIG

def test_modelo(model_key, pergunta="Qual é a capital do Brasil?"):
    """Testa um modelo específico e retorna a resposta."""
    print(f"\n▶️ Testando modelo: {model_key}")
    try:
        model = ModelManager()
        model.set_model(model_key)
        resposta = ""
        for chunk in model.ask(pergunta, stream=False):
            resposta += chunk
        print(f"   ✅ Resposta: {resposta[:150]}...")
        return resposta
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None

def test_ferramenta(tool_name, **kwargs):
    """Testa uma ferramenta e retorna o resultado."""
    print(f"\n▶️ Ferramenta: {tool_name} ({kwargs})")
    try:
        tools = ToolRegistry()
        resultado = tools.execute(tool_name, **kwargs)
        print(f"   ✅ Resultado: {str(resultado)[:200]}...")
        return resultado
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None

def test_comando_cli(comando, descricao):
    """Simula um comando no CLI (via --query) e mostra a resposta."""
    print(f"\n▶️ Comando: {descricao} ({comando})")
    try:
        cmd = f"python main.py --query \"{comando}\""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        output = result.stdout.strip()
        print(f"   ✅ Resposta: {output[:200]}...")
        return output
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None

def main():
    print("="*60)
    print("🧪 TESTE COMPLETO DO ECHO ASSISTANT (v2)")
    print("="*60)

    # 1. Testar todos os modelos
    print("\n📌 TESTE DE MODELOS")
    modelos = ["geral_leve", "geral_pesado", "codigo_leve", "codigo_pesado"]
    for modelo in modelos:
        test_modelo(modelo)

    # 2. Testar ferramentas essenciais
    print("\n📌 TESTE DE FERRAMENTAS")
    test_ferramenta("web_search", query="Python", num_results=2)
    test_ferramenta("terminal", command="echo Hello")
    test_ferramenta("hash", text="teste", algorithm="sha256")
    test_ferramenta("password", length=12)
    test_ferramenta("monitor")

    # 3. Testar comandos especiais (simulados)
    print("\n📌 TESTE DE COMANDOS (simulados)")
    test_comando_cli("/search inteligência artificial", "Busca")
    test_comando_cli("/run dir", "Terminal")
    test_comando_cli("/model", "Status do modelo")
    test_comando_cli("/tools", "Lista de ferramentas")

    print("\n" + "="*60)
    print("✅ TESTE CONCLUÍDO!")
    print("="*60)

if __name__ == "__main__":
    main()