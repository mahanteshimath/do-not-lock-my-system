# Architecture

The UI is platform-agnostic; every OS-specific behaviour lives behind a small
backend interface chosen at runtime. Adding a platform means writing one class.

---

## System overview

```mermaid
graph TD
    subgraph UI["🖥️ UI Layer (platform-agnostic)"]
        TK["<b>Tkinter Window</b><br/>Status card · Interval<br/>Options: lid-close, autostart<br/>Scheduled power action"]
        TRAY["<b>SystemTray</b><br/>pystray (Win) /<br/>Dock fallback (macOS)"]
        WARN["<b>Warning dialog</b><br/>30s cancelable"]
    end

    subgraph Core["⚙️ Application Core"]
        APP["<b>DontLockPC</b><br/>Orchestrator + event handling"]
        THREAD["<b>Keep-Alive Thread</b><br/>Daemon nudge loop"]
        TIMER["<b>Power timer</b><br/>root.after countdown"]
    end

    subgraph Backend["🔌 Backend Abstraction"]
        BASE["<b>KeepAwakeBackend</b><br/>prevent/allow_sleep · nudge<br/>prevent/restore_lid_sleep · power_action"]
        WIN["<b>WindowsBackend</b><br/>SetThreadExecutionState · SendInput F15<br/>powercfg lid · SetSuspendState / shutdown"]
        MAC["<b>MacOSBackend</b><br/>caffeinate -dimsu · Quartz F15<br/>pmset sleepnow / osascript shutdown"]
    end

    subgraph OS["🔧 System integration"]
        AUTO["<b>autostart</b><br/>Run key (Win) / LaunchAgent (macOS)"]
    end

    TK <--> APP
    TRAY <--> APP
    APP --> WARN
    APP -->|"START"| THREAD
    APP -->|"START (if armed)"| TIMER
    APP --> AUTO
    THREAD --> BASE
    TIMER -->|"deadline → warn → act"| BASE
    BASE -.->|"sys.platform == win32"| WIN
    BASE -.->|"sys.platform == darwin"| MAC
```

---

## Keep-alive flow

```mermaid
flowchart TD
    A(["▶ START"]) --> B["Validate interval (default 30s)"]
    B --> C["Update UI · start pulse"]
    C --> D["Spawn daemon thread"]
    D --> E["backend.prevent_sleep()"]
    E --> F{"running?"}
    F -- "No" --> K["backend.allow_sleep()"] --> L(["🛑 Thread exits"])
    F -- "Yes" --> G["backend.nudge()<br/>mouse ±1px + F15"]
    G --> H["Increment counter · timestamp · update UI"]
    H --> I["sleep(interval)"]
    I --> F

    style A fill:#a6e3a1,color:#11111b
    style L fill:#f38ba8,color:#11111b
    style E fill:#89b4fa,color:#11111b
    style G fill:#89b4fa,color:#11111b
```

The loop runs on a **daemon** thread so it can never keep the process alive
after the window closes. All UI updates are marshalled back to the Tk main
thread with `root.after(0, ...)`.

---

## Scheduled power action

```mermaid
flowchart TD
    S(["▶ START (action armed)"]) --> P["Parse timer field<br/>N minutes or HH:MM"]
    P --> Q{"deadline reached?<br/>(checked while running)"}
    Q -- "No" --> Q
    Q -- "Yes" --> X["Show 30s cancelable warning"]
    X -- "Cancel / STOP" --> Y(["Aborted · keep-alive keeps running"])
    X -- "Countdown ends" --> W["Release keep-alive<br/>allow_sleep() + restore lid"]
    W --> Z["backend.power_action()<br/>Sleep · Hibernate · Shutdown"]

    style S fill:#a6e3a1,color:#11111b
    style Y fill:#a6e3a1,color:#11111b
    style Z fill:#f38ba8,color:#11111b
    style W fill:#89b4fa,color:#11111b
```

The countdown uses Tk's `after()` on the main thread — no extra thread, and it
stops cleanly whenever `running` becomes false.

---

## The backend contract

`KeepAwakeBackend` is an ABC with three required methods and three optional
capability hooks:

| Member | Kind | Purpose |
|---|---|---|
| `prevent_sleep()` | **required** | Ask the OS to keep system + display awake |
| `allow_sleep()` | **required** | Restore default power/idle behaviour |
| `nudge()` | **required** | Emit a tiny, invisible input event |
| `prevent_lid_sleep()` | optional | Override lid-close action; returns `bool` |
| `restore_lid_sleep()` | optional | Put the lid-close action back |
| `power_action(action)` | optional | Sleep / Hibernate / Shut down |
| `close()` | provided | Calls `restore_lid_sleep()` + `allow_sleep()` |

Capabilities are advertised as class attributes so the UI can adapt without
platform checks:

```python
lid_close_supported: bool = False
power_actions: tuple[str, ...] = ()
```

The UI only renders the lid-close checkbox when `lid_close_supported` is true,
and only builds the power-action menu from `power_actions` — which is why macOS
never shows *Hibernate*.

`get_backend()` reads `sys.platform` **at call time**, which keeps it trivially
monkeypatchable in tests.

---

## Project structure

```text
do-not-lock-my-system/
├── src/dontlockpc/
│   ├── __init__.py           # package metadata / version
│   ├── __main__.py           # `python -m dontlockpc`
│   ├── app.py                # Tkinter UI + keep-alive orchestrator
│   ├── autostart.py          # cross-platform "run at login" management
│   ├── tray.py               # system-tray wrapper (graceful degradation)
│   └── backends/
│       ├── __init__.py       # get_backend() platform factory
│       ├── base.py           # KeepAwakeBackend abstract interface
│       ├── windows.py        # Win32 ctypes implementation
│       └── macos.py          # caffeinate + Quartz implementation
├── tests/
│   ├── test_backends.py      # backend factory + contract + capabilities
│   ├── test_power.py         # power-timer deadline parser
│   └── test_power_actions.py # cross-platform power actions + dialog
├── docs/                     # this documentation site (MkDocs)
├── .github/workflows/        # CI, release, PyPI publish, docs
├── dontlockpc.spec           # PyInstaller build spec
└── pyproject.toml            # packaging + tooling config
```

---

## Design principles

- **No platform checks in the UI** — capabilities are advertised by the backend.
- **Always restore what you change** — lid-close settings and execution state
  are put back on STOP, exit, and before any power action.
- **Fail soft** — an unavailable tray, autostart, or optional capability
  degrades gracefully instead of crashing.
- **Nothing leaves the machine** — no network calls, no telemetry.

---

**Next:** [Python API :material-arrow-right:](api.md){ .md-button }
