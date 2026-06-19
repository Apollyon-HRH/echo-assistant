"""Custom exceptions used across the ECHO project."""

class ECHOError(Exception):
    """Base exception for ECHO."""

class ConfigError(ECHOError):
    """Raised when configuration is invalid."""

class OllamaError(ECHOError):
    """Raised when Ollama requests fail."""

class ToolException(ECHOError):
    """Raised when a tool fails."""
