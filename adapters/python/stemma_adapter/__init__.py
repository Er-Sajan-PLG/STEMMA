"""First-party read-only STEMMA adapter."""

from .client import BadRequestError, NotFoundError, Stemma
from .loader import ExportError, SUPPORTED_EXPORT_MAJOR, load_export

__all__ = [
    "BadRequestError",
    "ExportError",
    "NotFoundError",
    "SUPPORTED_EXPORT_MAJOR",
    "Stemma",
    "load_export",
]

__version__ = "0.1.0"
