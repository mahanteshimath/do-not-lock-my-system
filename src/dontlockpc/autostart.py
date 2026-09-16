"""Cross-platform "run at login" (autostart) management.

Enables or disables launching the app automatically when the user signs in.

* **Windows** — a value under the per-user
  ``HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run`` registry key.
* **macOS** — a LaunchAgent ``plist`` in ``~/Library/LaunchAgents``.

Every function degrades gracefully (returns ``False`` / no-op) on unsupported
platforms or if the underlying OS call fails, so the UI can rely on it without
raising.
"""

from __future__ import annotations

import sys
from pathlib import Path

#: Identifier used for the Windows registry value.
APP_ID = "DontLockMyPC"
#: Reverse-DNS label used for the macOS LaunchAgent.
_MACOS_LABEL = "com.dontlockpc.autostart"
_WIN_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def supported() -> bool:
    """Return ``True`` if autostart can be managed on this platform."""
    return sys.platform.startswith("win") or sys.platform == "darwin"


def _launch_command() -> list[str]:
    """Return the argv used to start the app at login."""
    exe = sys.executable
    if sys.platform.startswith("win"):
        # Prefer the windowless interpreter so no console flashes at login.
        pythonw = Path(exe).with_name("pythonw.exe")
        if pythonw.exists():
            exe = str(pythonw)
    return [exe, "-m", "dontlockpc"]


# -- Windows ---------------------------------------------------------------


def _win_command_string() -> str:
    return " ".join(f'"{p}"' if " " in p else p for p in _launch_command())


def _win_is_enabled() -> bool:
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _WIN_RUN_KEY) as key:
            winreg.QueryValueEx(key, APP_ID)
        return True
    except OSError:
        return False


def _win_set(enable: bool) -> bool:
    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _WIN_RUN_KEY, 0, winreg.KEY_SET_VALUE
        ) as key:
            if enable:
                winreg.SetValueEx(key, APP_ID, 0, winreg.REG_SZ, _win_command_string())
            else:
                try:
                    winreg.DeleteValue(key, APP_ID)
                except FileNotFoundError:
                    pass
        return True
    except OSError:
        return False


# -- macOS -----------------------------------------------------------------


def _macos_plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{_MACOS_LABEL}.plist"


def _macos_is_enabled() -> bool:
    return _macos_plist_path().exists()


def _macos_set(enable: bool) -> bool:
    path = _macos_plist_path()
    try:
        if enable:
            path.parent.mkdir(parents=True, exist_ok=True)
            args = "".join(f"        <string>{a}</string>\n" for a in _launch_command())
            plist = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
                '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
                '<plist version="1.0">\n'
                "<dict>\n"
                "    <key>Label</key>\n"
                f"    <string>{_MACOS_LABEL}</string>\n"
                "    <key>ProgramArguments</key>\n"
                "    <array>\n"
                f"{args}"
                "    </array>\n"
                "    <key>RunAtLoad</key>\n"
                "    <true/>\n"
                "</dict>\n"
                "</plist>\n"
            )
            path.write_text(plist, encoding="utf-8")
        else:
            path.unlink(missing_ok=True)
        return True
    except OSError:
        return False


# -- public API ------------------------------------------------------------


def is_enabled() -> bool:
    """Return ``True`` if the app is currently set to run at login."""
    if sys.platform.startswith("win"):
        return _win_is_enabled()
    if sys.platform == "darwin":
        return _macos_is_enabled()
    return False


def set_enabled(enable: bool) -> bool:
    """Enable or disable running the app at login.

    Returns ``True`` on success, ``False`` if the platform is unsupported or
    the change could not be applied.
    """
    if sys.platform.startswith("win"):
        return _win_set(enable)
    if sys.platform == "darwin":
        return _macos_set(enable)
    return False
