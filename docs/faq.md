# FAQ & troubleshooting

---

## Getting started

??? question "Does this work on Linux?"
    Not yet. Windows and macOS are supported today. The backend abstraction
    makes Linux support straightforward to add (X11/Wayland input +
    `systemd-inhibit`/logind) — it's on the [roadmap](roadmap.md) and
    contributions are welcome.

??? question "Do I need administrator rights?"
    No. Everything is per-user: the autostart entry, the power-plan lid setting,
    and the keep-awake APIs all work with normal user privileges.

??? question "Does it send anything over the network?"
    No. There are **zero network calls** — no telemetry, no update checks, no
    analytics. Everything happens locally.

??? question "Will it interfere with what I'm doing?"
    No. It sends an invisible **F15** keypress (a key nothing binds) and moves
    the mouse ±1px, returning it to the exact starting position. You won't
    notice it, and it won't type or click anything.

---

## Keep-awake issues

??? question "My screen still locked while it was running"
    Check these in order:

    1. **Is the interval shorter than your lock timeout?** If your policy locks
       after 60 seconds, an interval of `30` is fine but `90` is not.
    2. **Is the status ACTIVE?** The card must be green and the *Signals*
       counter must be climbing.
    3. **Enterprise policy.** Some hardened environments ignore synthetic input
       entirely. Nothing running in user space can defeat that.

??? question "It sleeps anyway when I close the laptop lid"
    That's a separate power setting from sleep/idle.

    - **Windows** — tick **“Stay awake even with the lid closed”** *before*
      pressing START. The app sets the lid action to *Do nothing* while running
      and restores your original setting on STOP/exit.
    - **macOS** — clamshell sleep is enforced by firmware and cannot be
      overridden by an app. Only a system-wide
      `sudo pmset -a disablesleep 1` disables it (undo with `0`). The app
      deliberately won't do that for you.

??? question "The signal counter isn't increasing"
    The keep-alive thread only runs after you press **START**. If it's green
    and still not counting, restart the app — and see the update note below.

---

## Scheduled power action

??? question "I set Hibernate after 1 minute and nothing happened"
    The overwhelmingly common cause: **the app was started before you updated
    the code**. A running process keeps the *old* code in memory.

    **Fix:** close the app completely (check the Windows system tray for a
    lingering instance) and relaunch it. Then retry.

    If it still doesn't fire, confirm hibernation is actually available on the
    machine — see the next question.

??? question "How do I check whether hibernation is available? (Windows)"
    Run:

    ```powershell
    powercfg /a
    ```

    If **Hibernate** appears under *“The following sleep states are available”*,
    you're good. If it's listed as unavailable, enable it with an elevated
    prompt:

    ```powershell
    powercfg /hibernate on
    ```

    The app uses `shutdown /h`, falling back to the `SetSuspendState` power API
    if that command is unavailable.

??? question "Why is there no Hibernate option on macOS?"
    macOS has no user-facing hibernate equivalent, so the backend advertises
    only `("Sleep", "Shutdown")` and the menu is built from that list.

??? question "Can I cancel a scheduled action?"
    Yes, two ways:

    - Click **Cancel** in the 30-second warning dialog when it appears.
    - Press **STOP** at any time beforehand — that disarms the timer entirely.

??? question "What happens if I type something invalid in the timer field?"
    A blank or unparseable value simply **disarms** the timer. Keep-awake runs
    normally and nothing is powered off — it never guesses.

??? question "Can I use a clock time instead of minutes?"
    Yes. Enter `HH:MM` in 24-hour form (e.g. `23:30`) and it targets the next
    occurrence of that time. Plain numbers are treated as minutes.

---

## Install & updates

!!! danger "Always restart the app after updating"
    A running instance keeps the **old code in memory**. After `git pull` or
    installing a new version, close the app fully and relaunch it — otherwise
    you're still testing the previous build. This is the single most common
    source of “the fix didn't work”.

??? question "Windows SmartScreen blocked the download"
    The binaries are unsigned. Choose **More info → Run anyway**, or install
    from source / [build it yourself](building.md).

??? question "macOS says the app can't be opened"
    Gatekeeper quarantines unsigned downloads. Right-click the app → **Open** →
    **Open**, allow it under **System Settings → Privacy & Security**, or clear
    the flag:

    ```bash
    xattr -dr com.apple.quarantine DontLockMyPC.app
    ```

??? question "`ModuleNotFoundError: No module named 'tkinter'`"
    Tkinter isn't bundled with your Python build. On macOS with Homebrew:

    ```bash
    brew install python-tk
    ```

    On Windows, re-run the official Python installer and ensure **tcl/tk** is
    selected.

??? question "Can I install it from PyPI?"
    Not yet — publishing is set up but pending. For now, install from source
    or download a prebuilt release. Track it on the [roadmap](roadmap.md).

---

## Behaviour

??? question "Where does the tray icon go on macOS?"
    There isn't one. `pystray`'s macOS backend must own the main thread, which
    conflicts with Tkinter, so the app minimizes to the **Dock** instead. A
    native menu-bar item is on the roadmap.

??? question "Does “Start automatically at login” also press START?"
    No — it only opens the window. You stay in control of when the machine is
    actually held awake.

??? question "Does it change my system settings permanently?"
    No. The only persistent change is the optional autostart entry (removed
    when you untick it). The lid-close override is temporary and restored on
    STOP and on exit.

??? question "Can I run it without a GUI?"
    Yes — drive the backend directly from Python. See the
    [Python API](api.md).

---

## Still stuck?

- 🐛 [Open an issue](https://github.com/mahanteshimath/do-not-lock-my-system/issues/new/choose)
- 💬 [Start a discussion](https://github.com/mahanteshimath/do-not-lock-my-system/discussions)
- 🔒 Security problems: use the private
  [vulnerability report](https://github.com/mahanteshimath/do-not-lock-my-system/security/advisories/new)
  form — **not** a public issue.
