"""First-party read-only STEMMA adapter."""

from .client import BadRequestError, NotFoundError, Stemma
from .loader import ExportError, SUPPORTED_EXPORT_MAJOR, load_export

__all__ = [
    "BadRequestError",
    "ExportError",
    "NotFoundError",
    "ReleaseError",
    "SUPPORTED_EXPORT_MAJOR",
    "Stemma",
    "load_export",
]

__version__ = "0.3.0"


def __getattr__(name: str):
    # Lazy, so `import stemma_adapter` stays free of network/verification modules.
    if name == "ReleaseError":
        from .release import ReleaseError

        return ReleaseError
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
