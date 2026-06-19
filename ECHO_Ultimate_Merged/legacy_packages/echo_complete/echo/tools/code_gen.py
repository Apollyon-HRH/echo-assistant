from core.exceptions import ToolException

def code_gen(description: str, language: str = "python") -> str:
    """Generate code from a description using the local model if integrated."""
    try:
        return f"// Gerar {language} para: {description}\n// Integração com ModelManager deve ser feita pelo fluxo principal."
    except Exception as e:
        raise ToolException(f"Erro na ferramenta code_gen: {e}") from e
