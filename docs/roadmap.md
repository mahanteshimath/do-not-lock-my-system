# Roadmap

What's done, and what's next.

---

## Shipped

- [x] Cross-platform keep-awake (Windows + macOS)
- [x] System-tray integration (Windows)
- [x] Run at login (autostart)
- [x] Stay awake with the lid closed (Windows)
- [x] Scheduled Sleep / Hibernate / Shutdown timer
- [x] Standalone binaries via PyInstaller + automated GitHub Releases
- [x] Documentation site (this one)

## Planned

- [ ] **Linux** backend (X11/Wayland + `systemd-inhibit` / logind)
- [ ] Publish to **PyPI** (`pip install dontlockpc`)
- [ ] Menu-bar tray on macOS
- [ ] Optional force-true-sleep on Windows (bypass hibernate)

Have an idea?
[Open an issue](https://github.com/mahanteshimath/do-not-lock-my-system/issues/new/choose)
or [start a discussion](https://github.com/mahanteshimath/do-not-lock-my-system/discussions).

---

## Limitations

Known constraints, stated plainly:

**Windows & macOS only.**
The backend abstraction makes Linux support straightforward to add later —
contributions welcome.

**macOS has no menu-bar tray.**
`pystray`'s macOS backend must run on the main thread, which conflicts with
Tkinter. To stay stable, the app minimizes to the Dock instead.

**macOS clamshell sleep can't be overridden.**
Closing the lid triggers firmware-level sleep. Only a system-wide
`sudo pmset -a disablesleep 1` disables it, which the app won't do for you.

**Mouse jitter.**
The ±1px mouse move is imperceptible but technically moves the cursor.

**Enterprise policy.**
Effectiveness may vary under heavily locked-down corporate configurations that
ignore synthetic input. No user-space app can defeat those.

**Not yet on PyPI.**
Install from source or download a prebuilt release for now.

---

**Next:** [Changelog :material-arrow-right:](changelog.md){ .md-button }
