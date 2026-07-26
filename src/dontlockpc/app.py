"""Cross-platform keep-awake desktop app (Tkinter UI).

The UI is platform-agnostic; all OS-specific keep-awake logic lives behind a
:class:`~dontlockpc.backends.base.KeepAwakeBackend` selected at runtime.
"""

from __future__ import annotations

import sys
import threading
import time
import tkinter as tk
import webbrowser
from datetime import datetime, timedelta

from . import autostart
from .backends import get_backend
from .tray import SystemTray

IS_WINDOWS = sys.platform.startswith("win")
IS_MACOS = sys.platform == "darwin"

# Platform-appropriate UI fonts (Tk falls back to a default if unavailable).
if IS_MACOS:
    FONT = "Helvetica Neue"
    FONT_SEMIBOLD = "Helvetica Neue"
elif IS_WINDOWS:
    FONT = "Segoe UI"
    FONT_SEMIBOLD = "Segoe UI Semibold"
else:  # Linux / other
    FONT = "DejaVu Sans"
    FONT_SEMIBOLD = "DejaVu Sans"


class DontLockPC:
    """Main application window and keep-alive orchestrator."""

    # Color palette (Catppuccin Mocha-inspired)
    BG = "#11111b"
    CARD = "#181825"
    TEXT = "#cdd6f4"
    SUBTEXT = "#a6adc8"
    DIM = "#585b70"
    GREEN = "#a6e3a1"
    RED = "#f38ba8"
    TEAL = "#94e2d5"

    def __init__(self) -> None:
        self.backend = get_backend()
        self.running = False
        self.thread: threading.Thread | None = None
        self.interval = 30
        self.last_move_time: str | None = None
        self.move_count = 0
        self._pulse_state = False
        self._power_deadline: float | None = None
        self._power_win: tk.Toplevel | None = None

        self.tray = SystemTray(
            on_show=self.show_window,
            on_start=self.start,
            on_stop=self.stop,
            on_exit=self.quit_app,
        )

        self.root = tk.Tk()
        self.root.title("\u26a1 Don't Lock My PC")
        self.root.geometry("460x580")
        self.root.minsize(240, 300)
        self.root.resizable(True, True)
        self.root.configure(bg=self.BG)
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        self._build_ui()
        self._center_window()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(200, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()
        # A native minimize sends the app to the system tray where supported.
        self.root.bind("<Unmap>", self._on_unmap)

    # -- window helpers ----------------------------------------------------

    def _center_window(self) -> None:
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

    def _build_ui(self) -> None:
        content = tk.Frame(self.root, bg=self.BG)
        content.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)
        content.columnconfigure(0, weight=1)
        # Flexible top/bottom rows keep the controls vertically centered
        content.rowconfigure(0, weight=1)
        content.rowconfigure(8, weight=1)

        # Header
        tk.Label(
            content,
            text="\u26a1 Keep Awake",
            bg=self.BG,
            fg=self.TEXT,
            font=(FONT_SEMIBOLD, 24),
        ).grid(row=1, column=0, sticky="ew", pady=(0, 2))
        tk.Label(
            content,
            text="Keeps AI agents running — no lock, sleep or display-off",
            bg=self.BG,
            fg=self.DIM,
            font=(FONT, 9),
        ).grid(row=2, column=0, sticky="ew", pady=(0, 18))

        # Status card
        self.card = tk.Frame(
            content,
            bg=self.CARD,
            highlightbackground=self.DIM,
            highlightthickness=1,
        )
        self.card.grid(row=3, column=0, sticky="ew", ipady=18)

        status_row = tk.Frame(self.card, bg=self.CARD)
        status_row.pack(pady=(12, 4))

        self.pulse_canvas = tk.Canvas(
            status_row, width=16, height=16, bg=self.CARD, highlightthickness=0
        )
        self.pulse_canvas.pack(side=tk.LEFT, padx=(0, 8))
        self._draw_pulse(self.RED)

        self.status_label = tk.Label(
            status_row,
            text="INACTIVE",
            bg=self.CARD,
            fg=self.RED,
            font=(FONT_SEMIBOLD, 12),
        )
        self.status_label.pack(side=tk.LEFT)

        # Stats row
        stats_frame = tk.Frame(self.card, bg=self.CARD)
        stats_frame.pack(pady=(8, 4))

        self.moves_label = tk.Label(
            stats_frame,
            text="Signals: 0",
            bg=self.CARD,
            fg=self.SUBTEXT,
            font=(FONT, 9),
        )
        self.moves_label.pack(side=tk.LEFT, padx=12)

        tk.Label(
            stats_frame,
            text="\u2022",
            bg=self.CARD,
            fg=self.DIM,
            font=(FONT, 9),
        ).pack(side=tk.LEFT)

        self.time_label = tk.Label(
            stats_frame,
            text="Last: --:--:--",
            bg=self.CARD,
            fg=self.SUBTEXT,
            font=(FONT, 9),
        )
        self.time_label.pack(side=tk.LEFT, padx=12)

        # Interval control
        interval_frame = tk.Frame(content, bg=self.BG)
        interval_frame.grid(row=4, column=0, pady=(18, 12))

        tk.Label(
            interval_frame,
            text="Interval",
            bg=self.BG,
            fg=self.SUBTEXT,
            font=(FONT, 9),
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.interval_var = tk.StringVar(value="30")
        self.interval_entry = tk.Entry(
            interval_frame,
            textvariable=self.interval_var,
            width=4,
            font=(FONT_SEMIBOLD, 11),
            bg=self.CARD,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            justify="center",
            highlightbackground=self.DIM,
            highlightthickness=1,
        )
        self.interval_entry.pack(side=tk.LEFT, ipady=3)

        tk.Label(
            interval_frame, text="sec", bg=self.BG, fg=self.DIM, font=(FONT, 9)
        ).pack(side=tk.LEFT, padx=(4, 0))

        # Action buttons
        btn_frame = tk.Frame(content, bg=self.BG)
        btn_frame.grid(row=5, column=0, sticky="ew", pady=8)

        self.start_btn = tk.Button(
            btn_frame,
            text="\u25b6  START",
            command=self.start,
            font=(FONT_SEMIBOLD, 11),
            bg=self.GREEN,
            fg=self.BG,
            activebackground=self.TEAL,
            activeforeground=self.BG,
            relief="flat",
            cursor="hand2",
            bd=0,
            padx=20,
            pady=8,
        )
        self.start_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        self.stop_btn = tk.Button(
            btn_frame,
            text="\u23f9  STOP",
            command=self.stop,
            font=(FONT_SEMIBOLD, 11),
            bg=self.CARD,
            fg=self.DIM,
            activebackground=self.RED,
            activeforeground=self.BG,
            relief="flat",
            cursor="hand2",
            bd=0,
            padx=20,
            pady=8,
            state=tk.DISABLED,
        )
        self.stop_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0))

        # Options (lid-close + run-at-login)
        options = tk.Frame(content, bg=self.BG)
        options.grid(row=6, column=0, sticky="ew", pady=(6, 0))
        options.columnconfigure(0, weight=1)
        opt_row = 0

        # Scheduled power action (Sleep / Hibernate / Shutdown after a time).
        if self.backend.power_actions:
            power = tk.Frame(options, bg=self.BG)
            power.grid(row=opt_row, column=0, pady=(0, 8))
            opt_row += 1
            tk.Label(
                power, text="Then", bg=self.BG, fg=self.SUBTEXT, font=(FONT, 9)
            ).pack(side=tk.LEFT, padx=(0, 6))
            self.power_action_var = tk.StringVar(value="Off")
            self.power_menu = tk.OptionMenu(
                power, self.power_action_var, "Off", *self.backend.power_actions
            )
            self.power_menu.config(
                bg=self.CARD,
                fg=self.TEXT,
                activebackground=self.DIM,
                activeforeground=self.TEXT,
                highlightthickness=0,
                bd=0,
                font=(FONT, 9),
                cursor="hand2",
                width=8,
            )
            self.power_menu["menu"].config(bg=self.CARD, fg=self.TEXT)
            self.power_menu.pack(side=tk.LEFT)
            tk.Label(
                power, text="after", bg=self.BG, fg=self.SUBTEXT, font=(FONT, 9)
            ).pack(side=tk.LEFT, padx=6)
            self.power_time_var = tk.StringVar(value="")
            self.power_entry = tk.Entry(
                power,
                textvariable=self.power_time_var,
                width=7,
                font=(FONT_SEMIBOLD, 10),
                bg=self.CARD,
                fg=self.TEXT,
                insertbackground=self.TEXT,
                relief="flat",
                justify="center",
                highlightbackground=self.DIM,
                highlightthickness=1,
            )
            self.power_entry.pack(side=tk.LEFT, ipady=2)
            tk.Label(
                power,
                text="min / HH:MM",
                bg=self.BG,
                fg=self.DIM,
                font=(FONT, 8),
            ).pack(side=tk.LEFT, padx=(6, 0))

        if self.backend.lid_close_supported:
            self.lid_var = tk.BooleanVar(value=True)
            self.lid_check = tk.Checkbutton(
                options,
                text="Stay awake even with the lid closed",
                variable=self.lid_var,
                command=self._toggle_lid,
                bg=self.BG,
                fg=self.SUBTEXT,
                activebackground=self.BG,
                activeforeground=self.TEXT,
                selectcolor=self.CARD,
                font=(FONT, 9),
                bd=0,
                highlightthickness=0,
                cursor="hand2",
                anchor="center",
            )
            self.lid_check.grid(row=opt_row, column=0, sticky="ew")
            opt_row += 1

        # Run at login
        if autostart.supported():
            self.autostart_var = tk.BooleanVar(value=autostart.is_enabled())
            self.autostart_check = tk.Checkbutton(
                options,
                text="Start automatically at login",
                variable=self.autostart_var,
                command=self._toggle_autostart,
                bg=self.BG,
                fg=self.SUBTEXT,
                activebackground=self.BG,
                activeforeground=self.TEXT,
                selectcolor=self.CARD,
                font=(FONT, 9),
                bd=0,
                highlightthickness=0,
                cursor="hand2",
                anchor="center",
            )
            self.autostart_check.grid(row=opt_row, column=0, sticky="ew", pady=(2, 0))
            opt_row += 1

        # Footer
        footer = tk.Frame(content, bg=self.BG)
        footer.grid(row=7, column=0, sticky="ew", pady=(16, 0))
        footer.columnconfigure(0, weight=1)
        if self.tray.supported:
            footer_text = "\u2715 exits  \u2022  \u2500 minimize hides to the tray"
        elif IS_MACOS:
            footer_text = "\u2715 exits  \u2022  \u2500 minimizes to the Dock"
        else:
            footer_text = "\u2715 exits  \u2022  \u2500 minimizes to the taskbar"
        tk.Label(
            footer, text=footer_text, bg=self.BG, fg=self.DIM, font=(FONT, 8)
        ).grid(row=0, column=0, sticky="ew")
        if self.backend.lid_close_supported:
            tk.Label(
                footer,
                text=(
                    "Lid-closed stay-awake changes the power plan while running "
                    "and restores it on STOP/exit."
                ),
                bg=self.BG,
                fg=self.DIM,
                font=(FONT, 8),
                wraplength=380,
                justify="center",
            ).grid(row=1, column=0, sticky="ew", pady=(4, 0))

        # Credit
        credit = tk.Frame(footer, bg=self.BG)
        credit.grid(row=2, column=0, pady=(10, 0))
        tk.Label(
            credit,
            text="Developed with ",
            bg=self.BG,
            fg=self.DIM,
            font=(FONT, 8),
        ).pack(side=tk.LEFT)
        tk.Label(credit, text="\u2665", bg=self.BG, fg=self.RED, font=(FONT, 9)).pack(
            side=tk.LEFT
        )
        tk.Label(credit, text=" by ", bg=self.BG, fg=self.DIM, font=(FONT, 8)).pack(
            side=tk.LEFT
        )
        link = tk.Label(
            credit,
            text="MAHANTESH HIREMATH",
            bg=self.BG,
            fg=self.TEAL,
            font=(FONT_SEMIBOLD, 8, "underline"),
            cursor="hand2",
        )
        link.pack(side=tk.LEFT)
        link.bind(
            "<Button-1>",
            lambda _e: webbrowser.open("https://bit.ly/atozaboutdata"),
        )
        link.bind("<Enter>", lambda _e: link.config(fg=self.GREEN))
        link.bind("<Leave>", lambda _e: link.config(fg=self.TEAL))

    def _draw_pulse(self, color: str) -> None:
        self.pulse_canvas.delete("all")
        self.pulse_canvas.create_oval(3, 3, 13, 13, fill=color, outline=color)

    def _animate_pulse(self) -> None:
        if not self.running:
            return
        self._pulse_state = not self._pulse_state
        color = self.GREEN if self._pulse_state else "#40a040"
        self._draw_pulse(color)
        self.root.after(800, self._animate_pulse)

    def _toggle_autostart(self) -> None:
        want = self.autostart_var.get()
        if not autostart.set_enabled(want):
            # Revert the checkbox if the OS change could not be applied.
            self.autostart_var.set(not want)

    def _toggle_lid(self) -> None:
        # Only apply/restore live while running; otherwise it takes effect on
        # the next START.
        if not self.running:
            return
        if self.lid_var.get():
            if not self.backend.prevent_lid_sleep():
                self.lid_var.set(False)
        else:
            self.backend.restore_lid_sleep()

    def _minimize_window(self) -> None:
        self.root.iconify()

    def _on_unmap(self, event) -> None:
        # Route a native minimize to the system tray when it's available.
        if (
            event.widget is self.root
            and self.root.state() == "iconic"
            and self.tray.supported
        ):
            self.minimize_to_tray()

    # -- tray / lifecycle --------------------------------------------------

    def minimize_to_tray(self) -> None:
        if self.tray.supported:
            self.root.withdraw()
            self.tray.start(active=self.running)
        else:
            # No background tray (e.g. macOS): minimize to Dock instead.
            self._minimize_window()

    def show_window(self, *_) -> None:
        self.root.after(0, self.root.deiconify)

    def quit_app(self, *_) -> None:
        self.running = False
        self.tray.stop()
        try:
            self.backend.close()
        except Exception:
            pass
        self.root.after(0, self.root.destroy)

    def start(self, *_) -> None:
        try:
            self.interval = max(1, int(self.interval_var.get()))
        except ValueError:
            self.interval = 30
            self.interval_var.set("30")

        self.running = True
        self._draw_pulse(self.GREEN)
        self.status_label.config(text="ACTIVE", fg=self.GREEN)
        self.card.config(highlightbackground=self.GREEN)
        self.start_btn.config(state=tk.DISABLED, bg=self.CARD, fg=self.DIM)
        self.stop_btn.config(state=tk.NORMAL, bg=self.RED, fg=self.BG)
        self.interval_entry.config(state=tk.DISABLED)
        self.tray.set_active(True)

        # Optionally keep the system awake with the lid closed.
        if getattr(self, "lid_var", None) is not None and self.lid_var.get():
            if not self.backend.prevent_lid_sleep():
                self.lid_var.set(False)

        # Arm the scheduled power action (only runs while keep-awake is active).
        self._power_deadline = None
        if getattr(self, "power_action_var", None) is not None:
            if self.power_action_var.get() != "Off":
                self._power_deadline = self._parse_power_deadline(
                    self.power_time_var.get()
                )
            self.power_menu.config(state=tk.DISABLED)
            self.power_entry.config(state=tk.DISABLED)
        if self._power_deadline is not None:
            self.root.after(1000, self._tick_power_timer)

        self._animate_pulse()
        self.thread = threading.Thread(target=self._keep_alive, daemon=True)
        self.thread.start()

    def stop(self, *_) -> None:
        self.running = False
        self._draw_pulse(self.RED)
        self.status_label.config(text="INACTIVE", fg=self.RED)
        self.card.config(highlightbackground=self.DIM)
        self.start_btn.config(state=tk.NORMAL, bg=self.GREEN, fg=self.BG)
        self.stop_btn.config(state=tk.DISABLED, bg=self.CARD, fg=self.DIM)
        self.interval_entry.config(state=tk.NORMAL)
        self.tray.set_active(False)
        # Restore the original lid-close behaviour.
        self.backend.restore_lid_sleep()
        # Disarm any scheduled power action and re-enable its controls.
        self._power_deadline = None
        self._cancel_power_warning()
        if getattr(self, "power_menu", None) is not None:
            self.power_menu.config(state=tk.NORMAL)
            self.power_entry.config(state=tk.NORMAL)

    # -- scheduled power action --------------------------------------------

    @staticmethod
    def _parse_power_deadline(text: str) -> float | None:
        """Parse the timer field into an epoch deadline.

        Accepts either a positive number of minutes (``"90"``) or a 24-hour
        clock time (``"23:30"``, next occurrence). Returns ``None`` for blank
        or invalid input, so a bad value simply disarms the timer.
        """
        text = text.strip()
        if not text:
            return None
        if ":" in text:
            try:
                hh, mm = (int(x) for x in text.split(":", 1))
            except ValueError:
                return None
            if not (0 <= hh < 24 and 0 <= mm < 60):
                return None
            now = datetime.now()
            target = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
            if target <= now:
                target += timedelta(days=1)
            return target.timestamp()
        try:
            minutes = float(text)
        except ValueError:
            return None
        if minutes <= 0:
            return None
        return time.time() + minutes * 60

    def _tick_power_timer(self) -> None:
        if not self.running or self._power_deadline is None:
            return
        if time.time() >= self._power_deadline:
            self._power_deadline = None
            self._begin_power_warning()
            return
        self.root.after(1000, self._tick_power_timer)

    def _begin_power_warning(self, seconds: int = 30) -> None:
        action = self.power_action_var.get()
        if action == "Off":
            return
        win = tk.Toplevel(self.root)
        self._power_win = win
        win.title("Power action")
        win.configure(bg=self.CARD)
        win.resizable(False, False)
        win.transient(self.root)
        win.protocol("WM_DELETE_WINDOW", self._cancel_power_warning)

        msg = tk.Label(
            win,
            bg=self.CARD,
            fg=self.TEXT,
            font=(FONT_SEMIBOLD, 11),
            padx=24,
            pady=(18, 6),
        )
        msg.pack()
        tk.Button(
            win,
            text="Cancel",
            command=self._cancel_power_warning,
            bg=self.GREEN,
            fg=self.BG,
            activebackground=self.TEAL,
            activeforeground=self.BG,
            relief="flat",
            cursor="hand2",
            bd=0,
            padx=24,
            pady=6,
            font=(FONT_SEMIBOLD, 10),
        ).pack(pady=(0, 18))

        def countdown(n: int) -> None:
            if self._power_win is not win:
                return  # cancelled
            if n <= 0:
                self._execute_power_action(action, win)
                return
            msg.config(text=f"System will {action.lower()} in {n}s")
            win.after(1000, countdown, n - 1)

        countdown(seconds)
        win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - win.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - win.winfo_height()) // 2
        win.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        win.lift()
        win.grab_set()

    def _cancel_power_warning(self) -> None:
        win = self._power_win
        self._power_win = None
        if win is not None:
            try:
                win.grab_release()
                win.destroy()
            except Exception:
                pass

    def _execute_power_action(self, action: str, win: tk.Toplevel) -> None:
        self._power_win = None
        try:
            win.grab_release()
            win.destroy()
        except Exception:
            pass
        # Release keep-awake so the OS can actually sleep/hibernate/shut down.
        self.stop()
        try:
            self.backend.power_action(action)
        except Exception:
            pass

    # -- keep-alive worker -------------------------------------------------

    def _keep_alive(self) -> None:
        self.backend.prevent_sleep()
        while self.running:
            try:
                self.backend.nudge()
                self.move_count += 1
                self.last_move_time = datetime.now().strftime("%H:%M:%S")
                self.root.after(0, self._update_info)
            except Exception:
                pass
            time.sleep(self.interval)
        self.backend.allow_sleep()

    def _update_info(self) -> None:
        self.moves_label.config(text=f"Signals: {self.move_count}")
        self.time_label.config(text=f"Last: {self.last_move_time}")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    """Console entry point."""
    DontLockPC().run()


if __name__ == "__main__":
    main()
