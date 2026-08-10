# Development

Contributions of all kinds are welcome — bug reports, feature requests, docs,
and code.

---

## Set up

```bash
git clone https://github.com/mahanteshimath/do-not-lock-my-system.git
cd do-not-lock-my-system

python -m venv .venv
# Windows:  .\.venv\Scripts\Activate.ps1
# macOS:    source .venv/bin/activate

pip install -e ".[dev]"
```

---

## Quality gate

Run all three before pushing — CI runs the same checks on Windows and macOS:

```bash
ruff check .          # lint
ruff format .         # format
pytest                # tests
```

| Tool | Config | Notes |
|---|---|---|
| **ruff** | `line-length = 88`, `target-version = "py39"` | Rules: `E`, `F`, `I`, `UP`, `B`, `W` |
| **pytest** | `pythonpath = ["src"]`, `testpaths = ["tests"]` | No plugins required |

---

## Tests

| File | Covers |
|---|---|
| `tests/test_backends.py` | `get_backend()` factory, the ABC contract, per-platform capability flags |
| `tests/test_power.py` | `_parse_power_deadline` — minutes, `HH:MM`, blank/invalid input |
| `tests/test_power_actions.py` | Windows + macOS power actions, and the warning-dialog render/execute flow |

Two techniques keep the suite fast and safe on any OS:

**1. Monkeypatch the platform.** `get_backend()` reads `sys.platform` at call
time, so either backend can be selected without reloading modules:

```python
def test_macos_power_actions(monkeypatch):
    monkeypatch.setattr("sys.platform", "darwin")
    assert get_backend().power_actions == ("Sleep", "Shutdown")
```

**2. Stub only the final OS call.** The real backend code runs; only the
destructive boundary is replaced, so nothing actually sleeps or shuts down:

```python
def test_macos_sleep_runs_pmset(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "dontlockpc.backends.macos.subprocess.run",
        lambda cmd, **kw: calls.append(cmd),
    )
    MacOSBackend().power_action("Sleep")
    assert calls == [["pmset", "sleepnow"]]
```

!!! danger "Never let a test call the real power API"
    Always stub `subprocess.run` / `SetSuspendState` in power-action tests.
    Windows-only tests are guarded with
    `@pytest.mark.skipif(not IS_WINDOWS, ...)`.

---

## Adding a platform backend

1. Create `src/dontlockpc/backends/<platform>.py` with a class subclassing
   `KeepAwakeBackend`.
2. Implement `prevent_sleep`, `allow_sleep`, and `nudge`.
3. Advertise optional capabilities via `lid_close_supported` and
   `power_actions`, implementing the matching hooks.
4. Register it in `get_backend()` in `backends/__init__.py`.
5. Add capability assertions to `tests/test_backends.py`.

No UI changes are required — see [Architecture](architecture.md).

---

## Continuous integration

| Workflow | Trigger | Does |
|---|---|---|
| **CI** | push / PR to `main` | ruff lint + format check, then pytest on Windows & macOS across Python 3.10 and 3.12 |
| **Release** | tag `v*` | PyInstaller builds for both platforms, attached to a GitHub Release |
| **Publish** | GitHub Release | Publishes to PyPI via trusted publishing |
| **Docs** | push to `main` (docs paths) | Builds this site and deploys to GitHub Pages |

---

## Working on these docs

```bash
pip install -r requirements-docs.txt
mkdocs serve          # live preview at http://127.0.0.1:8000
mkdocs build --strict # what CI runs; fails on broken links
```

Pages live in `docs/` and the nav is defined in `mkdocs.yml`. Every page has an
**Edit** pencil that takes you straight to the file on GitHub.

---

## Pull requests

1. Read [CONTRIBUTING.md](https://github.com/mahanteshimath/do-not-lock-my-system/blob/main/CONTRIBUTING.md)
   and the [Code of Conduct](https://github.com/mahanteshimath/do-not-lock-my-system/blob/main/CODE_OF_CONDUCT.md).
2. Fork and create a feature branch.
3. Run the quality gate: `ruff check .`, `ruff format .`, `pytest`.
4. Open a PR describing **what** changed and **why**.

Browse the [open issues](https://github.com/mahanteshimath/do-not-lock-my-system/issues)
for something to pick up.

---

## Security

Please **do not** report security issues in public GitHub issues. Use GitHub's
private [**Report a vulnerability**](https://github.com/mahanteshimath/do-not-lock-my-system/security/advisories/new)
workflow. See [SECURITY.md](https://github.com/mahanteshimath/do-not-lock-my-system/blob/main/SECURITY.md)
for the full policy.

The app runs locally with your own privileges and makes **no network calls**.
The lid-close and power features change local OS power settings only, and
restore them on stop.

---

**Next:** [Roadmap :material-arrow-right:](roadmap.md){ .md-button }
