# Installation

There are two ways to run **Don't Lock My PC**: download a prebuilt app (no
Python needed), or install the Python package from source.

---

## Option 1 — Prebuilt app (recommended)

Every tagged release ships standalone binaries built by GitHub Actions.

<div class="btn-row" markdown>
[:material-microsoft-windows: DontLockMyPC-windows.zip](https://github.com/mahanteshimath/do-not-lock-my-system/releases/latest/download/DontLockMyPC-windows.zip){ .btn .btn--primary }
[:material-apple: DontLockMyPC-macos.zip](https://github.com/mahanteshimath/do-not-lock-my-system/releases/latest/download/DontLockMyPC-macos.zip){ .btn .btn--secondary }
</div>

1. Download the archive for your platform.
2. Unzip it.
3. Launch **`DontLockMyPC.exe`** (Windows) or **`DontLockMyPC.app`** (macOS).

No Python installation is required — the interpreter is bundled.

!!! warning "First-launch security prompts"
    Because these binaries are unsigned, your OS may warn you the first time:

    - **Windows** — SmartScreen may show *“Windows protected your PC.”* Choose
      **More info → Run anyway**.
    - **macOS** — Gatekeeper may say the app *“cannot be opened.”* Right-click
      the app → **Open** → **Open**, or allow it under
      **System Settings → Privacy & Security**.

    Prefer to avoid this entirely? Install from source (Option 2) or
    [build it yourself](building.md).

---

## Option 2 — Install from source

### Prerequisites

- **Python 3.9 or newer**
- **Windows** or **macOS**
- **Tkinter** — bundled with the official Python installers. On macOS with
  Homebrew Python, install it separately:

    ```bash
    brew install python-tk
    ```

### Install

=== "Windows (PowerShell)"

    ```powershell
    git clone https://github.com/mahanteshimath/do-not-lock-my-system.git
    cd do-not-lock-my-system

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1

    pip install .
    ```

=== "macOS (bash/zsh)"

    ```bash
    git clone https://github.com/mahanteshimath/do-not-lock-my-system.git
    cd do-not-lock-my-system

    python3 -m venv .venv
    source .venv/bin/activate

    pip install .
    ```

On macOS the install pulls in `pyobjc-framework-Quartz` automatically (via
platform markers) so the mouse/F15 nudge works. `caffeinate` is built into
macOS — nothing extra to install.

### Run it

```bash
dontlockpc              # console entry point (after install)
python -m dontlockpc    # run the package
```

On Windows, launch it without a console window using `pythonw`:

```powershell
.\.venv\Scripts\pythonw.exe -m dontlockpc
```

---

## Editable install (for development)

If you plan to change the code, install in editable mode with the dev extras:

```bash
pip install -e ".[dev]"
```

That adds `ruff`, `pytest`, and `pyinstaller`. See
[Development](development.md) for the full workflow.

---

## Upgrading

!!! danger "Restart the app after upgrading"
    A running instance keeps the **old code in memory**. After `git pull` or
    installing a new version, **close the app completely and relaunch it** —
    otherwise you're still running the previous build. On Windows, check the
    system tray for a lingering instance.

```bash
git pull
pip install .        # or: pip install -e ".[dev]"
```

---

## Uninstall

```bash
pip uninstall dontlockpc
```

If you enabled **Start automatically at login**, turn that checkbox off before
uninstalling so the autostart entry is removed cleanly. If you already removed
the app, delete the entry manually:

- **Windows** — remove the `DontLockMyPC` value under
  `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- **macOS** — delete the LaunchAgent `.plist` from `~/Library/LaunchAgents/`

---

**Next:** [Usage :material-arrow-right:](usage.md){ .md-button }
