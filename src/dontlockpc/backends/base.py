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

    #: Whether this backend can keep the system awake with the lid closed.
    lid_close_supported: bool = False

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

    def prevent_lid_sleep(self) -> bool:
        """Keep the system awake even when the laptop lid is closed.

        This overrides the OS "lid close action" so shutting the lid no longer
        sleeps the machine. The previous setting is remembered so it can be
        restored by :meth:`restore_lid_sleep`.

        Returns:
            ``True`` if the override was applied, ``False`` if the platform
            does not support it or the change failed.
        """
        return False

    def restore_lid_sleep(self) -> None:  # noqa: B027 - optional no-op hook
        """Restore the original lid-close behaviour saved by
        :meth:`prevent_lid_sleep`. Safe to call when nothing was changed."""

    def close(self) -> None:
        """Release any resources held by the backend."""
        self.restore_lid_sleep()
        self.allow_sleep()
