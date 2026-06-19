class EchoError(Exception):
    """Base exception for ECHO."""

class ConfigurationError(EchoError):
    """Raised when configuration is invalid."""

class ModelError(EchoError):
    """Raised when Ollama/model operations fail."""

class ToolException(EchoError):
    """Raised by tools when execution fails."""

class MemoryError(EchoError):
    """Raised by memory operations."""
