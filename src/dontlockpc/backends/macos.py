"""macOS keep-awake backend.

Uses two complementary mechanisms:

1. ``caffeinate`` — the built-in macOS utility. A long-lived
   ``caffeinate -dimsu`` subprocess keeps the display and system awake and
   declares the user active while it runs.
2. Quartz ``CGEvent`` input synthesis — a tiny mouse move (+/-1px) plus an
   invisible F15 key press to reset the screen-lock / screensaver idle timer.

Quartz is provided by ``pyobjc-framework-Quartz``. If it is unavailable the
backend still prevents sleep via ``caffeinate`` and simply skips the nudge.
"""

from __future__ import annotations

import subprocess

from .base import KeepAwakeBackend

try:  # pragma: no cover - import guard depends on platform/deps
    import Quartz  # type: ignore

    _QUARTZ_AVAILABLE = True
except Exception:  # pragma: no cover
    Quartz = None  # type: ignore
    _QUARTZ_AVAILABLE = False

# Virtual keycode for F15 on macOS (kVK_F15).
_KVK_F15 = 0x71


class MacOSBackend(KeepAwakeBackend):
    """Keep-awake implementation for macOS via ``caffeinate`` + Quartz."""

    name = "macos"

    def __init__(self) -> None:
        self._caffeinate: subprocess.Popen | None = None

    def prevent_sleep(self) -> None:
        if self._caffeinate is not None and self._caffeinate.poll() is None:
            return  # already running
        # -d display, -i idle system sleep, -m disk, -s system, -u user active
        self._caffeinate = subprocess.Popen(
            ["caffeinate", "-dimsu"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def allow_sleep(self) -> None:
        proc = self._caffeinate
        self._caffeinate = None
        if proc is None or proc.poll() is not None:
            return
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:  # pragma: no cover - defensive
            proc.kill()

    def nudge(self) -> None:
        if not _QUARTZ_AVAILABLE:
            return
        self._move_mouse()
        self._press_f15()

    # -- internals ---------------------------------------------------------

    def _move_mouse(self) -> None:
        current = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
        for dx in (1, -1):
            event = Quartz.CGEventCreateMouseEvent(
                None,
                Quartz.kCGEventMouseMoved,
                (current.x + dx, current.y),
                Quartz.kCGMouseButtonLeft,
            )
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

    def _press_f15(self) -> None:
        for is_down in (True, False):
            event = Quartz.CGEventCreateKeyboardEvent(None, _KVK_F15, is_down)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
