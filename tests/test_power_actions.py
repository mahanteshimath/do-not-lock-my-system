"""Thorough cross-platform tests for the scheduled power-action feature.

These drive the *real* backend code paths for both Windows and macOS, stubbing
only the final OS call (SetSuspendState / subprocess) so nothing destructive
runs. The GUI tests reproduce the exact dialog-render regression that used to
swallow the action, and are skipped automatically where no display is present.
"""

from __future__ import annotations

import sys
import tkinter as tk

import pytest

from dontlockpc.backends.macos import MacOSBackend

IS_WINDOWS = sys.platform.startswith("win")


# --------------------------------------------------------------------------
# macOS backend — runs on any OS (Quartz import is guarded, calls are stubbed)
# --------------------------------------------------------------------------


def test_macos_sleep_runs_pmset(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "dontlockpc.backends.macos.subprocess.run",
        lambda cmd, **kw: calls.append(cmd),
    )
    MacOSBackend().power_action("Sleep")
    assert calls == [["pmset", "sleepnow"]]


def test_macos_shutdown_runs_osascript(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "dontlockpc.backends.macos.subprocess.run",
        lambda cmd, **kw: calls.append(cmd),
    )
    MacOSBackend().power_action("Shutdown")
    assert calls == [
        ["osascript", "-e", 'tell application "System Events" to shut down']
    ]


def test_macos_unknown_action_is_noop(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "dontlockpc.backends.macos.subprocess.run",
        lambda cmd, **kw: calls.append(cmd),
    )
    MacOSBackend().power_action("Hibernate")  # not offered on macOS
    assert calls == []


# --------------------------------------------------------------------------
# Windows backend — only meaningful on Windows (needs ctypes.windll / powrprof)
# --------------------------------------------------------------------------


@pytest.mark.skipif(not IS_WINDOWS, reason="Windows-only power API")
def test_windows_sleep_and_hibernate_call_setsuspendstate(monkeypatch):
    import ctypes

    from dontlockpc.backends.windows import WindowsBackend

    seen = []

    class _FakePowrprof:
        def SetSuspendState(self, hibernate, force, wake):  # noqa: N802
            seen.append((hibernate, force, wake))
            return 1

    monkeypatch.setattr(ctypes.windll, "powrprof", _FakePowrprof())

    backend = WindowsBackend()
    backend.power_action("Sleep")
    backend.power_action("Hibernate")
    # Sleep => bHibernate=0, Hibernate => bHibernate=1; both force, wake-enabled.
    assert seen == [(0, 1, 0), (1, 1, 0)]


@pytest.mark.skipif(not IS_WINDOWS, reason="Windows-only power API")
def test_windows_shutdown_runs_shutdown_command(monkeypatch):
    from dontlockpc.backends import windows

    calls = []
    monkeypatch.setattr(windows.subprocess, "run", lambda cmd, **kw: calls.append(cmd))
    windows.WindowsBackend().power_action("Shutdown")
    assert calls == [["shutdown", "/s", "/t", "0"]]


# --------------------------------------------------------------------------
# GUI flow — the regression that used to swallow the action (skip if headless)
# --------------------------------------------------------------------------


@pytest.fixture
def app():
    from dontlockpc.app import DontLockPC

    try:
        instance = DontLockPC()
    except tk.TclError:
        pytest.skip("no display available")
    # Neutralise every real OS side effect; only observe the power action.
    instance._captured = []
    instance.backend.prevent_sleep = lambda: None
    instance.backend.allow_sleep = lambda: None
    instance.backend.nudge = lambda: None
    instance.backend.prevent_lid_sleep = lambda: True
    instance.backend.restore_lid_sleep = lambda: None
    instance.backend.power_action = instance._captured.append
    yield instance
    try:
        instance.root.destroy()
    except tk.TclError:
        pass


def test_warning_dialog_renders_then_executes(app):
    """Full flow: the dialog renders (the old regression) then fires the action.

    The empty-dialog bug meant ``_begin_power_warning`` raised before building
    its widgets, so the countdown/execute never ran. This asserts both halves.
    """
    if not app.backend.power_actions:
        pytest.skip("backend has no power actions on this platform")
    action = app.backend.power_actions[0]
    app.power_action_var.set(action)
    app.start()
    assert app.running is True

    app._begin_power_warning(seconds=30)
    app.root.update()

    win = app._power_win
    assert win is not None
    kinds = sorted(child.winfo_class() for child in win.winfo_children())
    assert kinds == ["Button", "Label"]
    label = next(c for c in win.winfo_children() if c.winfo_class() == "Label")
    assert label.cget("text").startswith("System will")

    # Reaching 0 executes the action and releases keep-awake first.
    app._execute_power_action(action, win)
    assert app._captured == [action]
    assert app.running is False
