"""Cross-platform keep-awake desktop app (Tkinter UI).

The UI is platform-agnostic; all OS-specific keep-awake logic lives behind a
:class:`~dontlockpc.backends.base.KeepAwakeBackend` selected at runtime.
"""

from __future__ import annotations

import sys
import threading
import time
import tkinter as tk
from datetime import datetime

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
    SURFACE = "#1e1e2e"
    CARD = "#181825"
    TEXT = "#cdd6f4"
    SUBTEXT = "#a6adc8"
    DIM = "#585b70"
    GREEN = "#a6e3a1"
    RED = "#f38ba8"
    TEAL = "#94e2d5"
    BLUE = "#89b4fa"

    def __init__(self) -> None:
        self.backend = get_backend()
        self.running = False
        self.thread: threading.Thread | None = None
        self.interval = 30
        self.last_move_time: str | None = None
        self.move_count = 0
        self._pulse_state = False

        # Use a custom frameless title bar only where it behaves well (Windows).
        self._frameless = IS_WINDOWS

        self.tray = SystemTray(
            on_show=self.show_window,
            on_start=self.start,
            on_stop=self.stop,
            on_exit=self.quit_app,
        )

        self.root = tk.Tk()
        self.root.title("Don't Lock My PC")
        self.root.geometry("420x480")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG)
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        self._offset_x = 0
        self._offset_y = 0
        if self._frameless:
            self.root.overrideredirect(True)

        self._build_ui()
        self._center_window()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(200, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()
        if self._frameless:
            self.root.bind("<Map>", self._on_map)

    # -- window helpers ----------------------------------------------------

    def _center_window(self) -> None:
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

    def _build_ui(self) -> None:
        if self._frameless:
            self._build_title_bar()

        content = tk.Frame(self.root, bg=self.BG)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Header
        tk.Label(
            content,
            text="Keep Awake",
            bg=self.BG,
            fg=self.TEXT,
            font=(FONT_SEMIBOLD, 22),
        ).pack(pady=(20, 2))
        tk.Label(
            content,
            text="Keeps AI agents running — no lock, sleep or display-off",
            bg=self.BG,
            fg=self.DIM,
            font=(FONT, 9),
        ).pack()

        # Status card
        self.card = tk.Frame(
            content,
            bg=self.CARD,
            highlightbackground=self.DIM,
            highlightthickness=1,
        )
        self.card.pack(fill=tk.X, pady=20, ipady=16)

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
        interval_frame.pack(pady=(0, 12))

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
        btn_frame.pack(pady=8, fill=tk.X)

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

        # Footer
        footer = tk.Frame(content, bg=self.BG)
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=(12, 4))
        footer_text = (
            "\u2715 exits  \u2022  \u2500 hides to tray (right-click for menu)"
            if self.tray.supported
            else "\u2715 exits  \u2022  \u2500 minimizes to the Dock"
        )
        tk.Label(
            footer, text=footer_text, bg=self.BG, fg=self.DIM, font=(FONT, 8)
        ).pack()

    def _build_title_bar(self) -> None:
        title_bar = tk.Frame(self.root, bg=self.SURFACE, height=36)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)
        title_bar.bind("<Button-1>", self._start_drag)
        title_bar.bind("<B1-Motion>", self._on_drag)

        tk.Label(
            title_bar,
            text="  \u26a1 Don't Lock My PC",
            bg=self.SURFACE,
            fg=self.SUBTEXT,
            font=(FONT, 9),
        ).pack(side=tk.LEFT, padx=4)

        close_btn = tk.Label(
            title_bar,
            text=" \u2715 ",
            bg=self.SURFACE,
            fg=self.DIM,
            font=(FONT, 11),
            cursor="hand2",
        )
        close_btn.pack(side=tk.RIGHT, padx=4)
        close_btn.bind("<Button-1>", lambda e: self.quit_app())
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg=self.RED))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg=self.DIM))

        minimize_btn = tk.Label(
            title_bar,
            text=" \u2500 ",
            bg=self.SURFACE,
            fg=self.DIM,
            font=(FONT, 11),
            cursor="hand2",
        )
        minimize_btn.pack(side=tk.RIGHT)
        minimize_btn.bind("<Button-1>", lambda e: self.minimize_to_tray())
        minimize_btn.bind("<Enter>", lambda e: minimize_btn.config(fg=self.TEXT))
        minimize_btn.bind("<Leave>", lambda e: minimize_btn.config(fg=self.DIM))

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

    def _minimize_window(self) -> None:
        if self._frameless:
            self.root.overrideredirect(False)
        self.root.iconify()

    def _on_map(self, event) -> None:
        if self.root.state() == "normal":
            self.root.overrideredirect(True)

    def _start_drag(self, event) -> None:
        self._offset_x = event.x
        self._offset_y = event.y

    def _on_drag(self, event) -> None:
        x = self.root.winfo_pointerx() - self._offset_x
        y = self.root.winfo_pointery() - self._offset_y
        self.root.geometry(f"+{x}+{y}")

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
