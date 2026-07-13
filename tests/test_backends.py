"""Tests for the keep-awake backend factory and contract.

``get_backend`` reads ``sys.platform`` at call time, so we can select a
backend by monkeypatching the platform without reloading modules.
"""

from __future__ import annotations

import pytest

from dontlockpc.backends import KeepAwakeBackend, get_backend


def test_get_backend_windows(monkeypatch):
    monkeypatch.setattr("sys.platform", "win32")
    backend = get_backend()
    assert backend.name == "windows"
    assert isinstance(backend, KeepAwakeBackend)


def test_get_backend_macos(monkeypatch):
    monkeypatch.setattr("sys.platform", "darwin")
    backend = get_backend()
    assert backend.name == "macos"
    assert isinstance(backend, KeepAwakeBackend)


def test_get_backend_unsupported(monkeypatch):
    monkeypatch.setattr("sys.platform", "sunos")
    with pytest.raises(RuntimeError):
        get_backend()


def test_backend_implements_contract():
    """The backend for the current platform must expose the full interface."""
    backend = get_backend()
    for method in (
        "prevent_sleep",
        "allow_sleep",
        "nudge",
        "prevent_lid_sleep",
        "restore_lid_sleep",
        "close",
    ):
        assert callable(getattr(backend, method))


def test_windows_backend_supports_lid_close(monkeypatch):
    monkeypatch.setattr("sys.platform", "win32")
    backend = get_backend()
    assert backend.lid_close_supported is True


def test_macos_backend_no_lid_close(monkeypatch):
    monkeypatch.setattr("sys.platform", "darwin")
    backend = get_backend()
    assert backend.lid_close_supported is False
