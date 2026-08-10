# Features

Everything **Don't Lock My PC** does, and exactly how it does it.

---

## Keep-awake engine

Two complementary mechanisms run together, because neither is sufficient alone:

| Platform | Prevent sleep / display off | Reset lock / inactivity timer |
|---|---|---|
| **Windows** | `SetThreadExecutionState` (`ES_CONTINUOUS \| ES_SYSTEM_REQUIRED \| ES_DISPLAY_REQUIRED`) | `SendInput` mouse ±1px + invisible **F15** keypress |
| **macOS** | built-in `caffeinate -dimsu` subprocess | Quartz `CGEvent` mouse ±1px + invisible **F15** keypress |

**Why F15?** It's a key virtually no application binds, so pressing it has no
visible side effect — unlike `Shift` (can affect typing) or `Ctrl` (can trigger
shortcuts). Some enterprise policies ignore mouse movement when deciding
whether a user is idle, so the keypress is the reliable half.

**Why the ±1px mouse move?** It returns the cursor to its exact starting
position, so it's imperceptible while still counting as user activity.

The loop runs on a **daemon thread**, so it never blocks the UI or prevents the
app from exiting.

---

## Cross-platform by design

The UI is completely platform-agnostic. All OS-specific logic lives behind a
small abstraction, `KeepAwakeBackend`, selected automatically at runtime:

```python
from dontlockpc.backends import get_backend

backend = get_backend()  # WindowsBackend or MacOSBackend
print(backend.name)  # "windows" / "macos"
```

Adding Linux support means writing one new backend class — no UI changes. See
[Architecture](architecture.md) and [Python API](api.md).

---

## Stay awake with the lid closed :material-microsoft-windows:

The keep-awake APIs above do **not** stop a lid-close sleep — that's a separate
power-plan setting.

When enabled, the app:

1. Reads the current lid-close action for both **AC** and **DC** power via
   `powercfg /query`.
2. Sets both to **Do nothing** while keep-alive runs.
3. **Restores your original values** on STOP or exit.

!!! success "Non-destructive"
    Your original setting is saved before any change and restored automatically
    — including when you close the app.

Not available on macOS, where clamshell sleep is enforced by firmware.

---

## Scheduled power action

Optionally power the machine down once a timer elapses.

| Action | Windows implementation | macOS implementation |
|---|---|---|
| **Sleep** | `SetSuspendState(0, 1, 0)` | `pmset sleepnow` |
| **Hibernate** | `shutdown /h` *(falls back to `SetSuspendState(1, 1, 0)`)* | ➖ not supported |
| **Shutdown** | `shutdown /s /t 0` | `osascript` → *System Events → shut down* |

Timer accepts either **minutes** (`90`) or a **24-hour clock time** (`23:30`,
next occurrence). Safety behaviour:

- Armed only while keep-awake is **running** — STOP disarms it.
- A **30-second cancelable warning** fires first.
- Keep-awake is **released before** the action, so the OS can actually power
  down (and the lid-close override is restored).
- Invalid input simply disarms the timer rather than guessing.

!!! tip "Windows hibernate"
    `shutdown /h` is used because `SetSuspendState` can silently fall back to
    sleep on some machines. Check hibernation is available with
    `powercfg /a` — see the [FAQ](faq.md).

---

## Start at login

| Platform | Mechanism |
|---|---|
| **Windows** | `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` registry value |
| **macOS** | LaunchAgent `.plist` in `~/Library/LaunchAgents/` |

Both are per-user — **no administrator rights required**. If the OS rejects the
change, the checkbox reverts so it always reflects the real state.

---

## System tray

On Windows the app minimizes to the system tray with a right-click menu:
**Show · Start · Stop · Exit**.

The tray wrapper **degrades gracefully** — if `pystray` is unavailable or the
platform can't support it (macOS, where it would need the main thread), the app
falls back to a normal minimize instead of crashing.

---

## Live status dashboard

- **Pulse animation** — an at-a-glance ACTIVE/INACTIVE indicator
- **Signal counter** — how many keep-alive nudges have been sent
- **Last signal time** — timestamp of the most recent nudge

Useful for confirming it's genuinely running before you walk away.

---

## Catppuccin Mocha UI

A clean, modern dark Tkinter interface using the
[Catppuccin](https://github.com/catppuccin/catppuccin) Mocha palette — the same
colours this documentation site uses.

---

## Proper Python packaging

- `pip install .` → `dontlockpc` console command and `dontlockpc-gui` GUI script
- `python -m dontlockpc` module entry point
- src-layout package, typed, linted with **ruff**, tested with **pytest**
- Standalone binaries via **PyInstaller** — see [Build](building.md)

---

**Next:** [FAQ & troubleshooting :material-arrow-right:](faq.md){ .md-button }
