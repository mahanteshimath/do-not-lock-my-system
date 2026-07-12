"""Abstract keep-awake backend interface.

Each platform provides a concrete implementation that knows how to:

* ``prevent_sleep`` — ask the OS to keep the system and display awake.
* ``allow_sleep``   — restore the default power/idle behaviour.
* ``nudge``         — simulate a tiny, side-effect-free user input so the
  inactivity/lock timer is reset.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class KeepAwakeBackend(ABC):
    """Platform-agnostic contract for keeping a machine awake and unlocked."""

    #: Human-readable backend name (overridden by subclasses).
    name: str = "base"

    @abstractmethod
    def prevent_sleep(self) -> None:
        """Tell the OS not to sleep or turn off the display.

        Called once when keep-alive starts. Implementations must be safe to
        call again without stacking side effects.
        """

    @abstractmethod
    def allow_sleep(self) -> None:
        """Restore the OS default power/idle behaviour.

        Called when keep-alive stops. Must be safe to call when sleep was
        never prevented.
        """

    @abstractmethod
    def nudge(self) -> None:
        """Emit a tiny, invisible input event to reset the lock timer."""

    def close(self) -> None:
        """Release any resources held by the backend."""
        self.allow_sleep()
