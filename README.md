# ⚡ Don't Lock My PC

**Keep your computer awake and unlocked while long-running AI agents do the work.**

When you kick off an AI agent, coding assistant, or any long task and step away,
Windows/macOS often lock the screen or go to sleep — pausing or interrupting the
run. **Don't Lock My PC** keeps your session alive so agents keep working
uninterrupted, then lets the machine sleep normally when you stop it.

> **Motto:** *While AI agents are working, your system should never lock or sleep.*

<p align="center">
  <img src="docs/screenshot.png" alt="Don't Lock My PC — app window" width="360">
</p>

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-555?logo=apple&logoColor=white)
![UI](https://img.shields.io/badge/UI-Tkinter-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Theme](https://img.shields.io/badge/Theme-Catppuccin%20Mocha-b4befe)

---

## Overview

**Why this exists:** AI agents and automated workflows often run for many
minutes or hours. If you walk away, corporate/personal lock and sleep policies
kick in — locking the screen, sleeping the machine, or turning off the display —
which can pause the agent, drop RDP/remote sessions, or interrupt the task. Run
this app before you start a long agent run and it keeps everything awake until
you click **STOP**.

**Don't Lock My PC** keeps your session alive using OS-native,
side-effect-free "keep-awake" signals — a tiny mouse nudge and an invisible
**F15** keypress — combined with the platform's official sleep-prevention API.

The UI is identical on every platform; all OS-specific logic lives behind a
small backend abstraction that is selected automatically at runtime.

### Keep-alive mechanisms per platform

| Platform | Prevent sleep / display off | Reset lock / inactivity timer |
|---|---|---|
| **Windows** | `SetThreadExecutionState` (`ES_SYSTEM_REQUIRED` \| `ES_DISPLAY_REQUIRED`) | `SendInput` mouse ±1px + invisible **F15** keypress |
| **macOS** | built-in `caffeinate -dimsu` subprocess | Quartz `CGEvent` mouse ±1px + invisible **F15** keypress |

> Windows' `SetThreadExecutionState` prevents sleep but does **not** reset the
> screen-lock timer — that is why the mouse + F15 nudge is also needed. On
> macOS, `caffeinate` handles sleep while the Quartz events keep the session
> active.

> **Closing the laptop lid:** the keep-awake APIs above do **not** stop a
> lid-close sleep. On Windows, enable **“Stay awake even with the lid closed”**
> and the app temporarily changes the active power plan's lid-close action to
> *Do nothing* while running, then restores your original setting on STOP/exit.
> On macOS, clamshell sleep is enforced by firmware and can only be disabled
> with `sudo pmset -a disablesleep 1`, so the app does not change it
> automatically.

### Typical use cases

- Running an **AI coding agent** or automation that takes many minutes/hours
- Long **model training / inference / data jobs** you monitor remotely
- Keeping an **RDP / remote-desktop** session from locking mid-task
- Presentations, downloads, or any unattended long-running process

---

## Features

- **Built for long AI-agent runs** — start it before a lengthy agent/automation
  task so the session never locks or sleeps mid-run
- **Cross-platform** — one codebase for Windows and macOS
- **Catppuccin Mocha dark UI** — clean, modern Tkinter interface
- **System-tray integration** on Windows (minimizes to tray on close); graceful
  minimize-to-Dock fallback on macOS
- **Configurable interval** — set the keep-alive frequency (default: 30s)
- **Start at login** — optional autostart (Windows registry `Run` key / macOS
  LaunchAgent) so it's ready before your next agent run
- **Stay awake with the lid closed** (Windows) — optionally overrides the power
  plan's "lid close" action so shutting the lid won't sleep the machine; the
  original setting is restored automatically on **STOP**/exit
- **Scheduled power action** — optionally **Sleep**, **Hibernate** (Windows), or
  **Shut down** the machine after a set time (in minutes, or at a `HH:MM` clock
  time). It counts down while keep-awake is running — handy for "keep my PC awake
  for the agent, then power it off when done." A 30-second cancelable warning
  fires first so you can abort.
- **Live status dashboard** — pulse animation, signal counter, last-signal time
- **Zero footprint** — invisible F15 key and ±1px mouse moves; no interference
- **Proper Python packaging** — `pip install .`, `dontlockpc` console command

---

## Installation

### Prerequisites

- **Python 3.9+**
- **Windows** or **macOS**
- Tkinter (bundled with the official Python installers; on macOS via Homebrew
  use `brew install python-tk`)

### Install

```bash
# Clone the repository
git clone https://github.com/mahanteshimath/do-not-lock-my-system.git
cd do-not-lock-my-system

# (recommended) create a virtual environment
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS:    source .venv/bin/activate

# Install the package and its dependencies
pip install .
```

On macOS, the install pulls in `pyobjc-framework-Quartz` automatically (via
platform markers) so the mouse/F15 nudge works. `caffeinate` is built into
macOS — no extra install needed.

---

## Usage

Run it any of these ways:

```bash
dontlockpc              # console entry point (after install)
python -m dontlockpc    # run the package
python dont_lock_pc.py  # legacy launcher (compatibility shim)
```

| Action | Behavior |
|---|---|
| **START** | Begins sending keep-alive signals at the configured interval |
| **STOP** | Halts signals and restores default power/idle behavior |
| **Close (✕)** | Windows: minimizes to tray · macOS: minimizes to Dock |
| **Interval field** | Signal frequency in seconds (editable when stopped) |
| **Start automatically at login** | Toggles autostart (Windows `Run` key / macOS LaunchAgent) |
| **Stay awake even with the lid closed** | Windows: keeps the system awake when the lid is shut (restored on STOP) |
| **Then … after …** | Schedule Sleep / Hibernate / Shutdown once the time elapses (minutes or `HH:MM`); armed while running, with a 30s cancelable warning |
| **Tray → Show/Start/Stop/Exit** | Quick actions (Windows) |

---

## Set up & run programmatically

### 1. Clone, isolate, install, launch

**Windows (PowerShell):**

```powershell
git clone https://github.com/mahanteshimath/do-not-lock-my-system.git
cd do-not-lock-my-system
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
python -m dontlockpc              # launch the GUI
# or windowless (no console):  .\.venv\Scripts\pythonw.exe -m dontlockpc
```

**macOS / Linux (bash/zsh):**

```bash
git clone https://github.com/mahanteshimath/do-not-lock-my-system.git
cd do-not-lock-my-system
python3 -m venv .venv
source .venv/bin/activate
pip install -e .                  # macOS: `brew install python-tk` if Tkinter is missing
python -m dontlockpc              # launch the GUI
```

### 2. Launch the GUI from Python

```python
from dontlockpc.app import main

main()   # opens the window; blocks until the app is closed
```

### 3. Drive the keep-awake engine headless (no GUI)

Use the platform backend directly — handy for scripts, servers, or CI runners.
`get_backend()` returns the right implementation for the current OS:

```python
import time
from dontlockpc.backends import get_backend

backend = get_backend()           # WindowsBackend / MacOSBackend
backend.prevent_sleep()           # block system sleep + display-off
try:
    for _ in range(120):          # keep awake for ~1 hour (120 × 30s)
        backend.nudge()           # invisible mouse ±1px + F15 keypress
        time.sleep(30)
finally:
    backend.allow_sleep()         # restore default power behaviour
    backend.close()               # also restores any lid-close override
```

### 4. Optional capabilities

Guard these with their feature flags so the code stays cross-platform:

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

> `prevent_lid_sleep` temporarily changes the active power plan's lid-close
> action and `power_action` will sleep/hibernate/shut down the machine — call
> `allow_sleep()` first so the OS can actually power down.

---

## Build a standalone executable

Ship it without requiring Python on the target machine using
[PyInstaller](https://pyinstaller.org/). Build on the OS you want to target
(PyInstaller does not cross-compile):

```bash
pip install .[dev]        # includes pyinstaller
pyinstaller dontlockpc.spec
```

The bundled app appears in `dist/`:

- **Windows** → `dist/DontLockMyPC.exe` (windowed, no console)
- **macOS** → `dist/DontLockMyPC.app`

---

## Project structure

```
do-not-lock-my-system/
├── src/dontlockpc/
│   ├── __init__.py          # package metadata / version
│   ├── __main__.py          # `python -m dontlockpc`
│   ├── app.py               # Tkinter UI + keep-alive orchestrator
│   ├── autostart.py         # cross-platform "run at login" management
│   ├── tray.py              # system-tray wrapper (graceful degradation)
│   └── backends/
│       ├── __init__.py      # get_backend() platform factory
│       ├── base.py          # KeepAwakeBackend abstract interface
│       ├── windows.py       # Win32 ctypes implementation
│       └── macos.py         # caffeinate + Quartz implementation
├── tests/
│   ├── test_backends.py     # backend factory + contract + capability tests
│   └── test_power.py        # power-timer deadline parser tests
├── docs/screenshot.png      # UI preview used in this README
├── .github/                 # CI workflow, issue/PR templates
├── dont_lock_pc.py          # legacy launcher shim
├── dontlockpc.spec          # PyInstaller build spec (standalone exe/app)
├── pyproject.toml           # packaging + tooling config
├── requirements.txt         # runtime deps (with platform markers)
├── requirements-dev.txt     # dev deps (ruff, pytest)
├── LICENSE                  # MIT
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── CHANGELOG.md
└── README.md
```

---

## Architecture

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

---

## Scheduled power action

Optional: after a timer elapses, put the machine to **Sleep**, **Hibernate**
(Windows), or **Shut down**. The countdown is armed on START and only runs while
keep-alive is active; when it fires, keep-alive is released first so the OS can
actually power down, and a 30-second cancelable warning gives you a chance to
abort.

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

---

## Development

```bash
pip install -e ".[dev]"

ruff check .          # lint
ruff format .         # format
pytest                # tests
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for details, including how to add a new
platform backend.

---

## Limitations

- **Windows & macOS only.** The backend abstraction makes Linux support
  straightforward to add later (planned) — contributions welcome.
- **macOS system tray:** `pystray`'s macOS backend must run on the main thread,
  which conflicts with Tkinter. To stay stable, the app minimizes to the Dock
  on macOS instead of a menu-bar tray.
- **Mouse jitter:** the ±1px mouse move is imperceptible but technically moves
  the cursor.
- Effectiveness may vary under heavily locked-down enterprise policies.

---

## License

[MIT](LICENSE) © Don't Lock My PC contributors
