# Contributing to Don't Lock My PC

Thanks for your interest in improving **Don't Lock My PC**! Contributions of
all kinds are welcome — bug reports, feature requests, docs, and code.

## Development setup

```bash
# Clone your fork
git clone https://github.com/mahanteshimath/do-not-lock-my-system.git
cd do-not-lock-my-system

# Create a virtual environment
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS:    source .venv/bin/activate

# Install in editable mode with dev tools
pip install -e ".[dev]"
```

## Running the app

```bash
python -m dontlockpc
# or, after install:
dontlockpc
```

## Quality checks

Please run these before opening a pull request:

```bash
ruff check .        # lint
ruff format .       # format
pytest              # tests
```

## Project layout

```
src/dontlockpc/
├── app.py              # Tkinter UI + keep-alive orchestrator (platform-agnostic)
├── autostart.py        # Cross-platform "run at login" management
├── tray.py             # System-tray wrapper with graceful degradation
└── backends/
    ├── base.py         # KeepAwakeBackend abstract interface
    ├── windows.py      # Win32 ctypes implementation
    ├── macos.py        # caffeinate + Quartz implementation
    └── __init__.py     # get_backend() platform factory
```

## Adding a platform backend

1. Create `src/dontlockpc/backends/<platform>.py`.
2. Subclass `KeepAwakeBackend` and implement the required methods:
   `prevent_sleep`, `allow_sleep`, and `nudge`.
3. Optionally implement the capability hooks (each defaults to a safe no-op):
   - `prevent_lid_sleep` / `restore_lid_sleep` + set `lid_close_supported = True`
     to keep the system awake with the lid closed.
   - `power_action(action)` + set `power_actions = (...)` (a subset of
     `"Sleep"`, `"Hibernate"`, `"Shutdown"`) to enable the scheduled power timer.
4. Wire it up in `backends/__init__.get_backend()`.
5. Add tests in `tests/`.

## Commit & PR guidelines

- Keep changes focused; one logical change per PR.
- Describe *what* and *why* in the PR description.
- Ensure lint and tests pass.
- Be kind and follow the [Code of Conduct](CODE_OF_CONDUCT.md).
