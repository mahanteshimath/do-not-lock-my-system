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

    def prevent_sleep(self) -> None:
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        )

    def allow_sleep(self) -> None:
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

    def nudge(self) -> None:
        self._simulate_mouse_move()
        self._simulate_key_press()

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
