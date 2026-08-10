# Build a standalone app

Ship the app without requiring Python on the target machine, using
[PyInstaller](https://pyinstaller.org/).

!!! warning "PyInstaller does not cross-compile"
    Build on the OS you want to target. A Windows `.exe` must be built on
    Windows; a macOS `.app` must be built on macOS.

---

## Build it

```bash
pip install ".[dev]"      # includes pyinstaller
pyinstaller dontlockpc.spec
```

The bundled app appears in `dist/`:

| Platform | Output |
|---|---|
| **Windows** | `dist/DontLockMyPC.exe` (windowed, no console) |
| **macOS** | `dist/DontLockMyPC.app` |

---

## What the spec does

`dontlockpc.spec` is checked into the repo so builds are reproducible. It:

- Uses `src/dontlockpc/__main__.py` as the entry point, with `pathex=["src"]`
- Builds **windowed** (no console window on launch)
- Declares hidden imports PyInstaller can't detect on its own:

    ```python
    hidden_imports = ["PIL._tkinter_finder"]
    if sys.platform.startswith("win"):
        hidden_imports.append("pystray._win32")
    elif sys.platform == "darwin":
        hidden_imports.append("pystray._darwin")
    ```

`pystray` picks its platform backend dynamically, so it must be named
explicitly — otherwise the frozen app fails at startup with a tray import
error.

---

## Automated releases

Pushing a version tag builds both platforms and publishes a GitHub Release
automatically:

```bash
git tag v1.3.1
git push origin v1.3.1
```

The [release workflow](https://github.com/mahanteshimath/do-not-lock-my-system/blob/main/.github/workflows/release.yml)
then:

1. Builds on `windows-latest` and `macos-latest` in parallel
2. Zips the results into `DontLockMyPC-windows.zip` / `DontLockMyPC-macos.zip`
3. Attaches both to a GitHub Release with generated release notes

That's what the download buttons on this site point at — always the
[latest release](https://github.com/mahanteshimath/do-not-lock-my-system/releases/latest).

---

## Troubleshooting builds

??? question "Antivirus / SmartScreen flags the .exe"
    Unsigned PyInstaller binaries are a common false positive because the
    bootstrapper unpacks itself at runtime. Options: build it yourself, run
    from source, or code-sign the executable.

??? question "`ModuleNotFoundError` for pystray or PIL at runtime"
    A hidden import is missing. Add it to `hidden_imports` in
    `dontlockpc.spec` and rebuild.

??? question "macOS says the .app is damaged"
    Gatekeeper quarantines unsigned downloads. Clear it with:

    ```bash
    xattr -dr com.apple.quarantine dist/DontLockMyPC.app
    ```

??? question "The build is very large"
    Expected — the bundle contains the Python interpreter, Tk, and Pillow.
    Roughly 30-60 MB compressed is normal.

---

**Next:** [Development :material-arrow-right:](development.md){ .md-button }
