"""Custom exceptions for ECHO."""

class ECHOError(Exception):
    """Base exception for the project."""


class ToolException(ECHOError):
    """Raised when a tool fails."""


class ModelException(ECHOError):
    """Raised when the model subsystem fails."""
