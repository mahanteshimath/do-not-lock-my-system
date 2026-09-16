# Python API

Use the keep-awake engine directly from your own scripts — no GUI required.
Handy for automation, servers, and CI runners.

---

## Launch the GUI from Python

```python
from dontlockpc.app import main

main()  # opens the window; blocks until the app is closed
```

---

## Drive the engine headless

`get_backend()` returns the right implementation for the current OS:

```python
import time
from dontlockpc.backends import get_backend

backend = get_backend()  # WindowsBackend / MacOSBackend
backend.prevent_sleep()  # block system sleep + display-off
try:
    for _ in range(120):  # keep awake for ~1 hour (120 × 30s)
        backend.nudge()  # invisible mouse ±1px + F15 keypress
        time.sleep(30)
finally:
    backend.allow_sleep()  # restore default power behaviour
    backend.close()  # also restores any lid-close override
```

!!! tip "Always use `try` / `finally`"
    If your script crashes without calling `allow_sleep()`, the machine stays
    awake until the process exits. `close()` is the belt-and-braces version —
    it restores the lid-close override too.

### As a context manager

`KeepAwakeBackend` has no `__enter__`, but `contextlib` makes one in three
lines:

```python
from contextlib import contextmanager
from dontlockpc.backends import get_backend


@contextmanager
def keep_awake():
    backend = get_backend()
    backend.prevent_sleep()
    try:
        yield backend
    finally:
        backend.close()


with keep_awake() as backend:
    run_my_long_job(on_tick=backend.nudge)
```

---

## Optional capabilities

Guard these with their feature flags so your code stays cross-platform:

```python
backend = get_backend()

# Keep awake with the lid closed (Windows only).
if backend.lid_close_supported:
    backend.prevent_lid_sleep()
    # ... work ...
    backend.restore_lid_sleep()

# Power the machine down. power_actions is a subset of
# ("Sleep", "Hibernate", "Shutdown") — macOS omits "Hibernate".
if "Sleep" in backend.power_actions:
    backend.power_action("Sleep")
```

!!! danger "`power_action` really does power down the machine"
    Call `allow_sleep()` (or `close()`) **first**, otherwise the keep-awake
    request can block the OS from actually sleeping.

---

## Reference

### `get_backend()`

```python
def get_backend() -> KeepAwakeBackend: ...
```

Returns the backend for the current OS. Raises `RuntimeError` on unsupported
platforms. Reads `sys.platform` at call time.

### `KeepAwakeBackend`

| Member | Signature | Notes |
|---|---|---|
| `name` | `str` | `"windows"` / `"macos"` |
| `lid_close_supported` | `bool` | `True` on Windows only |
| `power_actions` | `tuple[str, ...]` | Windows: Sleep/Hibernate/Shutdown · macOS: Sleep/Shutdown |
| `prevent_sleep()` | `-> None` | Safe to call repeatedly |
| `allow_sleep()` | `-> None` | Safe if sleep was never prevented |
| `nudge()` | `-> None` | Mouse ±1px + invisible F15 |
| `prevent_lid_sleep()` | `-> bool` | `False` if unsupported or it failed |
| `restore_lid_sleep()` | `-> None` | No-op when nothing was changed |
| `power_action(action)` | `-> None` | `action` must be in `power_actions` |
| `close()` | `-> None` | `restore_lid_sleep()` + `allow_sleep()` |

### Timer parsing

The scheduled-power-action field is parsed by a pure static method you can
reuse or test directly:

```python
from dontlockpc.app import DontLockPC

DontLockPC._parse_power_deadline("90")  # epoch, 90 minutes from now
DontLockPC._parse_power_deadline("23:30")  # epoch, next 23:30
DontLockPC._parse_power_deadline("")  # None — timer disarmed
DontLockPC._parse_power_deadline("nope")  # None — timer disarmed
```

---

## Writing a new backend

Subclass `KeepAwakeBackend`, implement the three required methods, advertise any
optional capabilities, and register it in `get_backend()`:

```python
from dontlockpc.backends.base import KeepAwakeBackend


class LinuxBackend(KeepAwakeBackend):
    name = "linux"
    lid_close_supported = False
    power_actions = ("Sleep", "Shutdown")

    def prevent_sleep(self) -> None: ...
    def allow_sleep(self) -> None: ...
    def nudge(self) -> None: ...
```

The UI adapts automatically — no changes needed there. See
[Development](development.md) for the contribution workflow.

---

**Next:** [Build a standalone app :material-arrow-right:](building.md){ .md-button }
