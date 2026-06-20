# ⚡ Don't Lock My PC

**A lightweight Windows utility that prevents your PC from locking, sleeping, or turning off the display — even under Group Policy restrictions.**

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)
![UI](https://img.shields.io/badge/UI-Tkinter-orange)
![Theme](https://img.shields.io/badge/Theme-Catppuccin%20Mocha-b4befe)

---

## Overview

Corporate and enterprise environments often enforce aggressive screen lock and sleep policies via Group Policy. **Don't Lock My PC** defeats these lockouts using a triple-layer keep-alive strategy that operates at the hardware input level — making it effective where simpler tools fail.

### Why Three Mechanisms?

| Mechanism | What It Does | Why It's Needed |
|---|---|---|
| `SetThreadExecutionState` | Tells the Windows kernel not to sleep or turn off the display | Prevents OS-level sleep but **does not** reset the lock inactivity timer |
| `SendInput` — Mouse Move | Moves the mouse ±1 pixel via hardware-level input | Resets the user inactivity timer that triggers screen lock |
| `SendInput` — F15 Keypress | Simulates an invisible F15 key press/release | Defeats Group Policy lock timers; F15 has no visible side effects |

---

## Features

- **Catppuccin Mocha Dark UI** — Frameless, draggable window with a modern dark theme
- **System Tray Integration** — Minimizes to tray on close; right-click tray icon for quick actions
- **Configurable Interval** — Set the keep-alive signal frequency (default: 30 seconds)
- **Live Status Dashboard** — Pulse animation, signal counter, and last-signal timestamp
- **Zero Footprint** — Uses the invisible F15 key and ±1px mouse moves; no visible interference
- **Start/Stop Controls** — One-click activation with clear ACTIVE/INACTIVE status

---

## Architecture

```mermaid
graph TD
    subgraph UI["🖥️ UI Layer"]
        TK["<b>Tkinter Window</b><br/>Custom Title Bar<br/>Status Card &amp; Controls<br/>Interval Configuration"]
        TRAY["<b>System Tray</b><br/>pystray Icon<br/>Right-Click Menu"]
    end

    subgraph Core["⚙️ Application Core"]
        APP["<b>DontLockPC</b><br/>Main Orchestrator<br/>Event Handling"]
        THREAD["<b>Keep-Alive Thread</b><br/>Daemon Thread<br/>Runs _keep_alive loop"]
    end

    subgraph WinAPI["🪟 Windows API Layer"]
        EXEC["<b>kernel32.dll</b><br/>SetThreadExecutionState<br/>ES_CONTINUOUS |<br/>ES_SYSTEM_REQUIRED |<br/>ES_DISPLAY_REQUIRED"]
        MOUSE["<b>user32.dll — SendInput</b><br/>MOUSEEVENTF_MOVE<br/>dx=+1 then dx=−1"]
        KEY["<b>user32.dll — SendInput</b><br/>VK_F15 Key Down<br/>VK_F15 Key Up"]
    end

    TK <-->|"Start · Stop<br/>Show · Minimize"| APP
    TRAY <-->|"Show · Start<br/>Stop · Exit"| APP
    APP -->|"Spawns on START"| THREAD
    THREAD -->|"① Prevent Sleep<br/>&amp; Display Off"| EXEC
    THREAD -->|"② Reset Lock<br/>Inactivity Timer"| MOUSE
    THREAD -->|"③ Defeat Group<br/>Policy Lock"| KEY
    TK -.->|"Close Button =<br/>Minimize to Tray"| TRAY
```

---

## Keep-Alive Flow

```mermaid
flowchart TD
    A(["▶ User Clicks START"]) --> B["Validate Interval Input<br/><i>default: 30 seconds</i>"]
    B --> C["Update UI State<br/>Status → ACTIVE<br/>Start Pulse Animation<br/>Disable Interval Input"]
    C --> D["Spawn Daemon Thread<br/><i>_keep_alive()</i>"]
    D --> E{"self.running<br/>== True?"}

    E -- "No" --> K["Reset ExecutionState<br/>to ES_CONTINUOUS"]
    K --> L(["🛑 Thread Exits"])

    E -- "Yes" --> F["<b>Step 1:</b> SetThreadExecutionState<br/>ES_CONTINUOUS | ES_SYSTEM_REQUIRED<br/>| ES_DISPLAY_REQUIRED"]
    F --> G["<b>Step 2:</b> SendInput Mouse Move<br/>+1px → 50ms delay → −1px"]
    G --> H["<b>Step 3:</b> SendInput F15 Key<br/>Key Down → Key Up"]
    H --> I["Increment Signal Counter<br/>Record Timestamp<br/>Update UI Labels"]
    I --> J["time.sleep(interval)"]
    J --> E

    style A fill:#a6e3a1,color:#11111b
    style L fill:#f38ba8,color:#11111b
    style F fill:#89b4fa,color:#11111b
    style G fill:#89b4fa,color:#11111b
    style H fill:#89b4fa,color:#11111b
```

---

## UI Interaction Flow

```mermaid
stateDiagram-v2
    [*] --> WindowOpen: Launch App

    WindowOpen --> Active: Click START
    Active --> Inactive: Click STOP
    Inactive --> Active: Click START

    WindowOpen --> Tray: Click ✕ (Close)
    Active --> Tray: Click ✕ (Close)
    Inactive --> Tray: Click ✕ (Close)

    Tray --> WindowOpen: Tray → Show
    Tray --> Active: Tray → Start
    Active --> Inactive: Tray → Stop
    Tray --> [*]: Tray → Exit

    WindowOpen --> Minimized: Click ─ (Minimize)
    Minimized --> WindowOpen: Restore

    state Active {
        [*] --> PulseOn
        PulseOn --> PulseOff: 800ms
        PulseOff --> PulseOn: 800ms
    }
```

---

## Installation

### Prerequisites

- **Python 3.x** (tested on 3.10+)
- **Windows** (uses Win32 API via `ctypes` — not compatible with macOS/Linux)

### Steps

```bash
# Clone or download the project
cd DontLockPC

# Install dependencies
pip install -r requirements.txt
```

Dependencies (`requirements.txt`):
- `pystray` — System tray icon and menu
- `Pillow` — Tray icon image generation

> `tkinter` and `ctypes` are included with Python on Windows — no extra install needed.

---

## Usage

```bash
python dont_lock_pc.py
```

| Action | Behavior |
|---|---|
| **START** | Begins sending keep-alive signals at the configured interval |
| **STOP** | Halts all keep-alive signals and resets Windows execution state |
| **Close (✕)** | Minimizes to system tray (does **not** exit) |
| **Minimize (─)** | Standard window minimize to taskbar |
| **Tray → Show** | Restores the window from tray |
| **Tray → Exit** | Fully quits the application |
| **Interval field** | Set signal frequency in seconds (editable when stopped) |

---

## How It Works

The app uses a **background daemon thread** that loops while active, executing three complementary Windows API calls each cycle:

1. **`kernel32.SetThreadExecutionState`** — Sets flags `ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED` to inform the OS that the system and display are in use. This prevents automatic sleep and display power-off but does **not** prevent screen lock.

2. **`user32.SendInput` (Mouse)** — Injects a hardware-level mouse move of +1 pixel followed by −1 pixel (with a 50ms gap). This resets the user inactivity timer that Windows uses to trigger screen lock, without visibly moving the cursor.

3. **`user32.SendInput` (Keyboard)** — Simulates an F15 key press and release. F15 is a valid USB HID key code that Windows recognizes as user input but no application acts on — making it invisible. This provides an additional inactivity timer reset that works even when Group Policy ignores mouse input.

When stopped, the app calls `SetThreadExecutionState(ES_CONTINUOUS)` to restore the default power behavior.

---

## Project Structure

```
DontLockPC/
├── dont_lock_pc.py      # Single-file application (all logic)
├── requirements.txt     # Python dependencies (pystray, Pillow)
└── README.md            # This file
```

---

## Limitations

- **Windows only** — Relies on `ctypes` calls to `kernel32.dll` and `user32.dll`
- **No admin rights needed** — Runs in user space, but effectiveness may vary under heavily locked-down environments
- **Mouse jitter** — The ±1px mouse move is imperceptible but technically moves the cursor

---

## Disclaimer

This tool is intended for **personal productivity use** — keeping your own workstation awake during long-running tasks, presentations, or remote sessions. Always comply with your organization's IT policies regarding workstation management.

---

<p align="center">
  <b>Built with Python + Tkinter</b><br/>
  <sub>Catppuccin Mocha theme • System tray powered by pystray</sub>
</p>
