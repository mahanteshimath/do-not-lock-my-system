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
├── tray.py             # System-tray wrapper with graceful degradation
└── backends/
    ├── base.py         # KeepAwakeBackend abstract interface
    ├── windows.py      # Win32 ctypes implementation
    ├── macos.py        # caffeinate + Quartz implementation
    └── __init__.py     # get_backend() platform factory
```

## Adding a platform backend

1. Create `src/dontlockpc/backends/<platform>.py`.
2. Subclass `KeepAwakeBackend` and implement `prevent_sleep`, `allow_sleep`,
   and `nudge`.
3. Wire it up in `backends/__init__.get_backend()`.
4. Add tests in `tests/`.

## Commit & PR guidelines

- Keep changes focused; one logical change per PR.
- Describe *what* and *why* in the PR description.
- Ensure lint and tests pass.
- Be kind and follow the [Code of Conduct](CODE_OF_CONDUCT.md).
