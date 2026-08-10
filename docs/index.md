---
hide:
  - navigation
  - toc
---

<div class="hero" markdown>

<h1 class="hero__title">⚡ Don't Lock My PC</h1>

<p class="hero__tagline">
Keep your computer <strong>awake and unlocked</strong> while long-running AI
agents do the work — then let it sleep normally when you're done.
</p>

<p class="hero__motto">
“While AI agents are working, your system should never lock or sleep.”
</p>

<p class="hero__badges">
<a href="https://github.com/mahanteshimath/do-not-lock-my-system/actions/workflows/ci.yml"><img src="https://github.com/mahanteshimath/do-not-lock-my-system/actions/workflows/ci.yml/badge.svg" alt="CI status"></a>
<a href="https://github.com/mahanteshimath/do-not-lock-my-system/releases/latest"><img src="https://img.shields.io/github/v/release/mahanteshimath/do-not-lock-my-system?display_name=tag&sort=semver" alt="Latest release"></a>
<a href="https://github.com/mahanteshimath/do-not-lock-my-system/releases"><img src="https://img.shields.io/github/downloads/mahanteshimath/do-not-lock-my-system/total" alt="Downloads"></a>
<img src="https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white" alt="Python 3.9+">
<img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-555?logo=apple&logoColor=white" alt="Platform">
<a href="https://github.com/mahanteshimath/do-not-lock-my-system/blob/main/LICENSE"><img src="https://img.shields.io/github/license/mahanteshimath/do-not-lock-my-system" alt="License"></a>
</p>

<div class="btn-row" markdown>
[:material-microsoft-windows: Download for Windows](https://github.com/mahanteshimath/do-not-lock-my-system/releases/latest/download/DontLockMyPC-windows.zip){ .btn .btn--primary }
[:material-apple: Download for macOS](https://github.com/mahanteshimath/do-not-lock-my-system/releases/latest/download/DontLockMyPC-macos.zip){ .btn .btn--secondary }
[:material-book-open-variant: Get started](installation.md){ .btn }
[:material-github: Star on GitHub](https://github.com/mahanteshimath/do-not-lock-my-system){ .btn }
</div>

<p class="hero__shot">
<img src="screenshot.png" alt="Don't Lock My PC — app window">
</p>

</div>

---

## Why this exists

AI agents and automated workflows often run for **minutes or hours**. If you
walk away, corporate or personal lock-and-sleep policies kick in — locking the
screen, sleeping the machine, or turning off the display. That can pause the
agent, drop an RDP session, or interrupt the task entirely.

Start **Don't Lock My PC** before a long run and it keeps everything awake
until you click **STOP** — no registry hacks, no policy changes you can't undo.

<div class="grid-cards" markdown>

<div class="card" markdown>
### 🤖 Built for agent runs
Start it before a lengthy agent or automation task so the session never locks
or sleeps mid-run.
</div>

<div class="card" markdown>
### 🖥️ Cross-platform
One codebase, one identical UI on **Windows** and **macOS**, with OS-native
mechanisms behind a small backend abstraction.
</div>

<div class="card" markdown>
### 💤 Lid-close stay-awake
On Windows, optionally keep working with the laptop lid **shut** — your
original power setting is restored on STOP.
</div>

<div class="card" markdown>
### ⏻ Scheduled power action
Sleep, Hibernate, or Shut down after a timer — “keep my PC awake for the
agent, then power it off when done.”
</div>

<div class="card" markdown>
### 🫥 Zero footprint
An invisible **F15** keypress and ±1px mouse nudges. No clicking, no typing,
no interference with your work.
</div>

<div class="card" markdown>
### 🚀 Start at login
Optional autostart via the Windows `Run` key or a macOS LaunchAgent, so it's
ready before your next run.
</div>

</div>

---

## Quick start

=== "Prebuilt app (no Python)"

    1. Download the archive for your OS from the buttons above or the
       [latest release](https://github.com/mahanteshimath/do-not-lock-my-system/releases/latest).
    2. Unzip it.
    3. Run **`DontLockMyPC.exe`** (Windows) or **`DontLockMyPC.app`** (macOS).

=== "Windows (PowerShell)"

    ```powershell
    git clone https://github.com/mahanteshimath/do-not-lock-my-system.git
    cd do-not-lock-my-system
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install .
    python -m dontlockpc
    ```

=== "macOS (bash/zsh)"

    ```bash
    git clone https://github.com/mahanteshimath/do-not-lock-my-system.git
    cd do-not-lock-my-system
    python3 -m venv .venv
    source .venv/bin/activate
    pip install .
    python -m dontlockpc
    ```

Then press **START**, and the machine stays awake until you press **STOP**.

[Full installation guide :material-arrow-right:](installation.md){ .md-button }
[How it works :material-arrow-right:](architecture.md){ .md-button }

---

## How it keeps you awake

| Platform | Prevent sleep / display off | Reset lock / inactivity timer |
|---|---|---|
| **Windows** | `SetThreadExecutionState` (`ES_SYSTEM_REQUIRED` \| `ES_DISPLAY_REQUIRED`) | `SendInput` mouse ±1px + invisible **F15** keypress |
| **macOS** | built-in `caffeinate -dimsu` subprocess | Quartz `CGEvent` mouse ±1px + invisible **F15** keypress |

!!! info "Why both mechanisms?"
    On Windows, `SetThreadExecutionState` prevents sleep but does **not** reset
    the screen-lock timer — which is why the mouse + F15 nudge is also needed.
    On macOS, `caffeinate` handles sleep while the Quartz events keep the
    session active.

---

<p align="center" markdown>
Developed with ❤️ by [**MAHANTESH HIREMATH**](https://bit.ly/atozaboutdata)
</p>
