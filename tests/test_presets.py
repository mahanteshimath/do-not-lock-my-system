"""Tests for the Quick Presets feature (Continuous / 30m Agent / 2h Model Run /
6h Overnight) added to the Tkinter UI.
"""

from __future__ import annotations

import tkinter as tk

import pytest

from dontlockpc.app import PRESETS


@pytest.fixture
def app():
    from dontlockpc.app import DontLockPC

    try:
        instance = DontLockPC()
    except tk.TclError:
        pytest.skip("no display available")
    instance.backend.prevent_sleep = lambda: None
    instance.backend.allow_sleep = lambda: None
    instance.backend.nudge = lambda: None
    instance.backend.prevent_lid_sleep = lambda: True
    instance.backend.restore_lid_sleep = lambda: None
    instance.backend.power_action = lambda *_a, **_kw: None
    yield instance
    try:
        instance.root.destroy()
    except tk.TclError:
        pass


def _preset(preset_id: str) -> dict[str, str]:
    return next(p for p in PRESETS if p["id"] == preset_id)


def test_continuous_is_selected_by_default(app):
    assert app.selected_preset_id == "continuous"
    assert app.preset_buttons["continuous"].cget("fg") == app.GREEN


def test_select_preset_applies_interval_and_power_action(app):
    app._select_preset(_preset("agent"))
    assert app.selected_preset_id == "agent"
    assert app.interval_var.get() == "30"
    if app.backend.power_actions:
        assert app.power_action_var.get() in ("Sleep", "Off")
        if app.power_action_var.get() == "Sleep":
            assert app.power_time_var.get() == "30"
    assert app.preset_buttons["agent"].cget("fg") == app.GREEN
    assert app.preset_buttons["continuous"].cget("fg") == app.SUBTEXT


def test_manual_interval_edit_clears_preset_selection(app):
    app._select_preset(_preset("overnight"))
    assert app.selected_preset_id == "overnight"

    app.interval_var.set("45")
    app.root.update()

    assert app.selected_preset_id is None
    assert app.preset_buttons["overnight"].cget("fg") == app.SUBTEXT


def test_presets_disabled_while_running(app):
    app.start()
    assert str(app.preset_buttons["agent"].cget("state")) == "disabled"
    app.stop()
    assert str(app.preset_buttons["agent"].cget("state")) == "normal"


def test_select_preset_is_noop_while_running(app):
    app.start()
    app._select_preset(_preset("model"))
    assert app.selected_preset_id != "model"
    app.stop()
