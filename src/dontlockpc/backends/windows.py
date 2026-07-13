"""Windows keep-awake backend.

Uses three complementary Win32 mechanisms:

1. ``kernel32.SetThreadExecutionState`` — prevents system sleep and display
   power-off (but does **not** reset the screen-lock inactivity timer).
2. ``user32.SendInput`` mouse move (+/-1px) — resets the user inactivity timer.
3. ``user32.SendInput`` F15 key press — an invisible key that resets the lock
   timer even where Group Policy ignores mouse movement.
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes
import re
import subprocess
import time

from .base import KeepAwakeBackend

# SetThreadExecutionState flags
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

# SendInput constants
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
MOUSEEVENTF_MOVE = 0x0001
KEYEVENTF_KEYUP = 0x0002
VK_F15 = 0x7E  # F15 — no visible side effects

# powercfg identifiers for the "lid close action" power setting.
_SUB_BUTTONS = "4f971e89-eebd-4455-a8de-9e59040e7347"
_LIDACTION = "5ca83367-6e45-459f-a27b-476b1d01c936"
_LID_DO_NOTHING = "0"  # 0=Do nothing, 1=Sleep, 2=Hibernate, 3=Shut down
# Hide the console window when shelling out to powercfg.
_NO_WINDOW = 0x08000000


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.wintypes.LONG),
        ("dy", ctypes.wintypes.LONG),
        ("mouseData", ctypes.wintypes.DWORD),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.wintypes.WORD),
        ("wScan", ctypes.wintypes.WORD),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.wintypes.DWORD),
        ("wParamL", ctypes.wintypes.WORD),
        ("wParamH", ctypes.wintypes.WORD),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.wintypes.DWORD), ("union", INPUT_UNION)]


class WindowsBackend(KeepAwakeBackend):
    """Keep-awake implementation for Windows via Win32 ``ctypes`` calls."""

    name = "windows"
    lid_close_supported = True

    def __init__(self) -> None:
        # Saved lid-close action indexes (AC, DC) captured before override.
        self._saved_lid: tuple[str, str] | None = None

    def prevent_sleep(self) -> None:
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        )

    def allow_sleep(self) -> None:
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

    def nudge(self) -> None:
        self._simulate_mouse_move()
        self._simulate_key_press()

    # -- lid-close override -------------------------------------------------

    def prevent_lid_sleep(self) -> bool:
        """Set the active power plan's lid-close action to "Do nothing".

        Remembers the previous AC/DC values so :meth:`restore_lid_sleep` can
        put them back. Returns ``True`` on success.
        """
        try:
            if self._saved_lid is None:
                self._saved_lid = self._query_lid_action()
            self._set_lid_action(_LID_DO_NOTHING, _LID_DO_NOTHING)
            return True
        except Exception:
            return False

    def restore_lid_sleep(self) -> None:
        if self._saved_lid is None:
            return
        ac, dc = self._saved_lid
        try:
            self._set_lid_action(ac, dc)
        except Exception:
            pass
        finally:
            self._saved_lid = None

    def _powercfg(self, *args: str) -> str:
        result = subprocess.run(
            ["powercfg", *args],
            capture_output=True,
            text=True,
            creationflags=_NO_WINDOW,
            check=True,
        )
        return result.stdout

    def _query_lid_action(self) -> tuple[str, str]:
        out = self._powercfg("/query", "SCHEME_CURRENT", _SUB_BUTTONS, _LIDACTION)
        ac = re.search(r"Current AC Power Setting Index:\s*0x([0-9a-fA-F]+)", out)
        dc = re.search(r"Current DC Power Setting Index:\s*0x([0-9a-fA-F]+)", out)
        ac_val = str(int(ac.group(1), 16)) if ac else _LID_DO_NOTHING
        dc_val = str(int(dc.group(1), 16)) if dc else _LID_DO_NOTHING
        return ac_val, dc_val

    def _set_lid_action(self, ac: str, dc: str) -> None:
        self._powercfg(
            "/setacvalueindex", "SCHEME_CURRENT", _SUB_BUTTONS, _LIDACTION, ac
        )
        self._powercfg(
            "/setdcvalueindex", "SCHEME_CURRENT", _SUB_BUTTONS, _LIDACTION, dc
        )
        self._powercfg("/setactive", "SCHEME_CURRENT")

    # -- internals ---------------------------------------------------------

    def _send_input(self, *inputs: INPUT) -> None:
        n = len(inputs)
        arr = (INPUT * n)(*inputs)
        ctypes.windll.user32.SendInput(n, ctypes.pointer(arr), ctypes.sizeof(INPUT))

    def _simulate_mouse_move(self) -> None:
        """Move the cursor +1px then -1px via hardware-level input."""
        inp = INPUT()
        inp.type = INPUT_MOUSE
        inp.union.mi.dx = 1
        inp.union.mi.dy = 0
        inp.union.mi.mouseData = 0
        inp.union.mi.dwFlags = MOUSEEVENTF_MOVE
        inp.union.mi.time = 0
        inp.union.mi.dwExtraInfo = None
        self._send_input(inp)
        time.sleep(0.05)
        inp.union.mi.dx = -1
        self._send_input(inp)

    def _simulate_key_press(self) -> None:
        """Press and release F15 — an invisible key with no side effects."""
        key_down = INPUT()
        key_down.type = INPUT_KEYBOARD
        key_down.union.ki.wVk = VK_F15
        key_down.union.ki.wScan = 0
        key_down.union.ki.dwFlags = 0
        key_down.union.ki.time = 0
        key_down.union.ki.dwExtraInfo = None

        key_up = INPUT()
        key_up.type = INPUT_KEYBOARD
        key_up.union.ki.wVk = VK_F15
        key_up.union.ki.wScan = 0
        key_up.union.ki.dwFlags = KEYEVENTF_KEYUP
        key_up.union.ki.time = 0
        key_up.union.ki.dwExtraInfo = None

        self._send_input(key_down, key_up)
