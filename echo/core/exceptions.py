from __future__ import annotations

class ECHOError(Exception):
    """Base error for the project."""

class ConfigurationError(ECHOError):
    """Raised when configuration is missing or invalid."""

class ModelException(ECHOError):
    """Raised for model/API failures."""

class ToolException(ECHOError):
    """Raised when a tool fails or is unavailable."""
