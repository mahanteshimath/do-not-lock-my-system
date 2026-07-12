"""System-tray integration with graceful cross-platform degradation.

``pystray``'s macOS (AppKit) backend must run on the main thread, which
conflicts with Tkinter's ``mainloop``. To avoid crashing the UI, the tray is
only enabled where it can run on a background thread (Windows/Linux). On macOS
``tray_supported()`` returns ``False`` and the app degrades to minimizing to
the Dock instead.
"""

from __future__ import annotations

import sys
import threading
from typing import Callable

try:  # pragma: no cover - depends on optional deps
    import pystray
    from PIL import Image, ImageDraw

    _PYSTRAY_AVAILABLE = True
except Exception:  # pragma: no cover
    pystray = None  # type: ignore
    Image = ImageDraw = None  # type: ignore
    _PYSTRAY_AVAILABLE = False

_IS_MACOS = sys.platform == "darwin"


def tray_supported() -> bool:
    """Return ``True`` if a background-thread system tray is usable here."""
    return _PYSTRAY_AVAILABLE and not _IS_MACOS


def _create_image(active: bool):
    img = Image.new("RGB", (64, 64), color=(30, 30, 46))
    draw = ImageDraw.Draw(img)
    fill = (166, 227, 161) if active else (243, 139, 168)
    draw.ellipse([12, 12, 52, 52], fill=fill)
    draw.text((22, 20), "PC", fill=(30, 30, 46))
    return img


class SystemTray:
    """Thin wrapper around ``pystray`` with a no-op fallback."""

    def __init__(
        self,
        on_show: Callable[[], None],
        on_start: Callable[[], None],
        on_stop: Callable[[], None],
        on_exit: Callable[[], None],
    ) -> None:
        self._on_show = on_show
        self._on_start = on_start
        self._on_stop = on_stop
        self._on_exit = on_exit
        self.icon = None

    @property
    def supported(self) -> bool:
        return tray_supported()

    def start(self, active: bool) -> None:
        """Create and run the tray icon (once) on a background thread."""
        if not self.supported or self.icon is not None:
            return
        menu = pystray.Menu(
            pystray.MenuItem("Show", lambda *_: self._on_show()),
            pystray.MenuItem("Start", lambda *_: self._on_start()),
            pystray.MenuItem("Stop", lambda *_: self._on_stop()),
            pystray.MenuItem("Exit", lambda *_: self._on_exit()),
        )
        self.icon = pystray.Icon(
            "DontLockPC", _create_image(active), "Don't Lock My PC", menu
        )
        threading.Thread(target=self.icon.run, daemon=True).start()

    def set_active(self, active: bool) -> None:
        if self.icon is not None:
            self.icon.icon = _create_image(active)

    def stop(self) -> None:
        if self.icon is not None:
            self.icon.stop()
            self.icon = None
