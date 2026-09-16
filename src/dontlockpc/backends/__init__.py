"""Keep-awake backends and the platform-selection factory."""

from __future__ import annotations

import sys

from .base import KeepAwakeBackend

__all__ = ["KeepAwakeBackend", "get_backend"]


def get_backend() -> KeepAwakeBackend:
    """Return the keep-awake backend for the current operating system.

    Raises:
        RuntimeError: If the current platform is not supported.
    """
    if sys.platform.startswith("win"):
        from .windows import WindowsBackend

        return WindowsBackend()
    if sys.platform == "darwin":
        from .macos import MacOSBackend

        return MacOSBackend()
    raise RuntimeError(
        f"Unsupported platform: {sys.platform!r}. "
        "Don't Lock My PC currently supports Windows and macOS."
    )
