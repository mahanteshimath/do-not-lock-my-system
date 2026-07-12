# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.1] - 2026-07-13

### Added
- **Automated release builds** — a GitHub Actions `Release` workflow that, on
  every `v*` tag, builds the standalone `DontLockMyPC.exe` (Windows) and
  `DontLockMyPC.app` (macOS) with PyInstaller, zips them, and attaches them to
  the published GitHub Release.

## [1.1.0] - 2026-07-13

### Added
- **Start at login** — an in-app "Start automatically at login" toggle backed by
  a new cross-platform `autostart` module (Windows `Run` registry key / macOS
  LaunchAgent).
- **Standalone build** — a checked-in `dontlockpc.spec` for PyInstaller that
  produces a windowed `DontLockMyPC.exe` (Windows) or `DontLockMyPC.app`
  (macOS); `pyinstaller` added to the dev extras.
- **UI preview** — `docs/screenshot.svg` embedded in the README.

### Changed
- Repositioned the app around its core use case: **keeping the system awake and
  unlocked while long-running AI agents work.** Updated README, in-app subtitle,
  and package metadata accordingly.
- Close button (✕) now fully exits the app; the minimize button (─) hides to the
  system tray.

## [1.0.0] - 2026-07-13

### Added
- **Cross-platform support** for Windows and macOS via a pluggable
  keep-awake backend abstraction (`KeepAwakeBackend`).
- macOS backend using the built-in `caffeinate` utility plus Quartz
  `CGEvent` mouse/F15 input synthesis.
- Proper `src/` package layout (`dontlockpc`) with `python -m dontlockpc`
  and a `dontlockpc` console entry point.
- Packaging via `pyproject.toml`, platform-marked dependencies, and a
  development extras group.
- System-tray wrapper that degrades gracefully where a background-thread tray
  is unavailable (e.g. macOS → minimize to Dock).
- GitHub Actions CI (lint + import smoke on Windows and macOS), issue/PR
  templates, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and tests.

### Changed
- Extracted the original single-file Windows script into a package; the
  Windows Win32 logic now lives in `backends/windows.py`.
- UI now uses platform-appropriate fonts and a native title bar on macOS.

[1.1.1]: https://github.com/mahanteshimath/do-not-lock-my-system/releases/tag/v1.1.1
[1.1.0]: https://github.com/mahanteshimath/do-not-lock-my-system/releases/tag/v1.1.0
[1.0.0]: https://github.com/mahanteshimath/do-not-lock-my-system/releases/tag/v1.0.0
