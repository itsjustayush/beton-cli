"""Human-readable errors for normal Beton failures."""


class BetonError(Exception):
    """Base exception for expected user-facing failures."""


class ConfigurationError(BetonError):
    """Raised when configuration cannot be read or written."""


class ResolutionError(BetonError):
    """Raised when a target cannot be resolved."""


class CapabilityError(BetonError):
    """Raised when an operation is unsupported on the current platform."""


class PermissionDeniedError(BetonError):
    """Raised when the OS refuses an action."""
