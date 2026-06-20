#!/usr/bin/env python3
"""
Teste completo do ECHO Assistant - executa todos os comandos e ferramentas.
"""

import subprocess
import sys
import time
import json
from pathlib import Path

# Configurações
ECHO_MAIN = "python main.py --query"
MODELOS = ["geral_leve", "geral_pesado", "codigo_leve", "codigo_pesado"]

def run_query(query, model=None):
    """Executa uma pergunta no modo one-shot e retorna a resposta."""
    cmd = f"{ECHO_MAIN} \"{query}\""
    if model:
        cmd = f"python main.py --query \"{query}\" --model {model}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"

def test_tool(tool_name, args=""):
    """Testa uma ferramenta específica."""
    cmd = f"python -c \"from core.tools import ToolRegistry; t=ToolRegistry(); print(t.execute('{tool_name}', {args}))\""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return result.stdout.strip()
    except Exception as e:
        return f"[ERRO] {e}"

def main():
    print("="*60)
    print("🧪 TESTE COMPLETO DO ECHO ASSISTANT")
    print("="*60)

    # Teste 1: Modelos
    print("\n📌 TESTE DE MODELOS")
    for modelo in MODELOS:
        print(f"\n▶️ Modelo: {modelo}")
        resp = run_query("Qual é a capital do Brasil?", model=modelo)
        print(f"   Resposta: {resp[:100]}...")

    # Teste 2: Comandos especiais (simulados com --query)
    print("\n📌 TESTE DE COMANDOS")
    comandos = [
        ("/search inteligência artificial", "Busca"),
        ("/run dir", "Terminal"),
        ("/model", "Status do modelo"),
        ("/tools", "Lista de ferramentas"),
    ]
    for cmd, desc in comandos:
        print(f"\n▶️ {desc}: {cmd}")
        resp = run_query(cmd)
        print(f"   {resp[:200]}...")

    # Teste 3: Ferramentas individuais (via ToolRegistry)
    print("\n📌 TESTE DE FERRAMENTAS (selecionadas)")
    ferramentas = [
        ("web_search", 'query="Python", num_results=2'),
        ("terminal", 'command="echo Hello"'),
        ("filesystem", 'action="read", path="README.md"'),
        ("hash", 'text="teste", algorithm="sha256"'),
        ("password", 'length=12'),
        ("monitor", ''),
    ]
    for tool, args in ferramentas:
        print(f"\n▶️ Ferramenta: {tool} ({args})")
        resp = test_tool(tool, args)
        print(f"   {resp[:200]}...")

    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    main()