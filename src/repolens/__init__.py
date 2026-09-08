"""RepoLens — zero-dependency Git repository health, hotspot and risk analyzer."""

from __future__ import annotations

__version__ = "0.1.0"
__all__ = ["__version__", "analyze", "compare"]


def __getattr__(name: str):  # lazy import keeps `import repolens` cheap
    if name in ("analyze", "compare"):
        from . import analyzer
        return getattr(analyzer, name)
    raise AttributeError(name)
