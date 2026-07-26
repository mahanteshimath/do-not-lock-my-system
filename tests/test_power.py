"""Tests for the scheduled power-action deadline parser.

``_parse_power_deadline`` is a pure staticmethod, so it can be exercised
without creating a Tk window.
"""

from __future__ import annotations

import time

from dontlockpc.app import DontLockPC

parse = DontLockPC._parse_power_deadline


def test_blank_and_invalid_return_none():
    for bad in ("", "   ", "abc", "0", "-5", "1:99", "24:00", "12:60", "9:9x"):
        assert parse(bad) is None


def test_minutes_returns_future_epoch():
    now = time.time()
    val = parse("10")
    assert val is not None
    assert 595 < val - now < 605  # ~10 minutes ahead


def test_clock_time_within_next_24h():
    now = time.time()
    val = parse("23:59")
    assert val is not None
    assert 0 < val - now <= 24 * 3600 + 120
