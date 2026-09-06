"""STEMMA ingestion/review webapp (human-in-the-loop).

This is a *proposal-engineering* tool. It never writes under content/,
connections/, or sources/. Everything it produces lives under the git-ignored
``workflow/`` directory so a human can review and later drive the canonical
gate (``scripts/review.py`` + ``scripts/verify_all.py``).
"""

__all__ = ["core", "server"]
