import time
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import ctypes
import ctypes.wintypes
import pystray
from PIL import Image, ImageDraw

# Windows API to prevent sleep
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

# SendInput structures for simulating real hardware input (prevents lock)
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
MOUSEEVENTF_MOVE = 0x0001
KEYEVENTF_KEYUP = 0x0002
VK_F15 = 0x7E  # F15 key — invisible, no side effects


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.wintypes.LONG),
                ("dy", ctypes.wintypes.LONG),
                ("mouseData", ctypes.wintypes.DWORD),
                ("dwFlags", ctypes.wintypes.DWORD),
                ("time", ctypes.wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.wintypes.WORD),
                ("wScan", ctypes.wintypes.WORD),
                ("dwFlags", ctypes.wintypes.DWORD),
                ("time", ctypes.wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.wintypes.DWORD),
                ("wParamL", ctypes.wintypes.WORD),
                ("wParamH", ctypes.wintypes.WORD)]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.wintypes.DWORD), ("union", INPUT_UNION)]


class DontLockPC:
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

    def __init__(self):
        self.running = False
        self.thread = None
        self.interval = 30
        self.last_move_time = None
        self.move_count = 0
        self.tray_icon = None
        self._pulse_state = False

        self.root = tk.Tk()
        self.root.title("Don't Lock My PC")
        self.root.geometry("420x480")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG)
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        # Remove default title bar for cleaner look
        self.root.overrideredirect(True)
        self._offset_x = 0
        self._offset_y = 0

        self._build_ui()
        self._center_window()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(200, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()
        self.root.bind("<Map>", self._on_map)

    def _center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

    def _build_ui(self):
        # Custom title bar
        title_bar = tk.Frame(self.root, bg=self.SURFACE, height=36)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        title_bar.bind("<Button-1>", self._start_drag)
        title_bar.bind("<B1-Motion>", self._on_drag)

        tk.Label(title_bar, text="  \u26a1 Don't Lock My PC", bg=self.SURFACE,
                 fg=self.SUBTEXT, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=4)

        close_btn = tk.Label(title_bar, text=" \u2715 ", bg=self.SURFACE,
                             fg=self.DIM, font=("Segoe UI", 11), cursor="hand2")
        close_btn.pack(side=tk.RIGHT, padx=4)
        close_btn.bind("<Button-1>", lambda e: self.minimize_to_tray())
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg=self.RED))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg=self.DIM))

        minimize_btn = tk.Label(title_bar, text=" \u2500 ", bg=self.SURFACE,
                                fg=self.DIM, font=("Segoe UI", 11), cursor="hand2")
        minimize_btn.pack(side=tk.RIGHT)
        minimize_btn.bind("<Button-1>", lambda e: self._minimize_window())
        minimize_btn.bind("<Enter>", lambda e: minimize_btn.config(fg=self.TEXT))
        minimize_btn.bind("<Leave>", lambda e: minimize_btn.config(fg=self.DIM))

        # Main content area
        content = tk.Frame(self.root, bg=self.BG)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Header
        tk.Label(content, text="Keep Awake", bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI Semibold", 22)).pack(pady=(20, 2))
        tk.Label(content, text="Prevents sleep, display off & screen lock",
                 bg=self.BG, fg=self.DIM, font=("Segoe UI", 9)).pack()

        # Status card
        self.card = tk.Frame(content, bg=self.CARD, highlightbackground=self.DIM,
                             highlightthickness=1)
        self.card.pack(fill=tk.X, pady=20, ipady=16)

        # Pulse dot + status
        status_row = tk.Frame(self.card, bg=self.CARD)
        status_row.pack(pady=(12, 4))

        self.pulse_canvas = tk.Canvas(status_row, width=16, height=16,
                                      bg=self.CARD, highlightthickness=0)
        self.pulse_canvas.pack(side=tk.LEFT, padx=(0, 8))
        self._draw_pulse(self.RED)

        self.status_label = tk.Label(status_row, text="INACTIVE", bg=self.CARD,
                                     fg=self.RED, font=("Segoe UI Semibold", 12))
        self.status_label.pack(side=tk.LEFT)

        # Stats row
        stats_frame = tk.Frame(self.card, bg=self.CARD)
        stats_frame.pack(pady=(8, 4))

        self.moves_label = tk.Label(stats_frame, text="Signals: 0", bg=self.CARD,
                                    fg=self.SUBTEXT, font=("Segoe UI", 9))
        self.moves_label.pack(side=tk.LEFT, padx=12)

        tk.Label(stats_frame, text="\u2022", bg=self.CARD, fg=self.DIM,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)

        self.time_label = tk.Label(stats_frame, text="Last: --:--:--", bg=self.CARD,
                                   fg=self.SUBTEXT, font=("Segoe UI", 9))
        self.time_label.pack(side=tk.LEFT, padx=12)

        # Interval control
        interval_frame = tk.Frame(content, bg=self.BG)
        interval_frame.pack(pady=(0, 12))

        tk.Label(interval_frame, text="Interval", bg=self.BG, fg=self.SUBTEXT,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 8))

        self.interval_var = tk.StringVar(value="30")
        self.interval_entry = tk.Entry(
            interval_frame, textvariable=self.interval_var, width=4,
            font=("Segoe UI Semibold", 11), bg=self.CARD, fg=self.TEXT,
            insertbackground=self.TEXT, relief="flat", justify="center",
            highlightbackground=self.DIM, highlightthickness=1)
        self.interval_entry.pack(side=tk.LEFT, ipady=3)

        tk.Label(interval_frame, text="sec", bg=self.BG, fg=self.DIM,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(4, 0))

        # Action buttons
        btn_frame = tk.Frame(content, bg=self.BG)
        btn_frame.pack(pady=8, fill=tk.X)

        self.start_btn = tk.Button(
            btn_frame, text="\u25b6  START", command=self.start,
            font=("Segoe UI Semibold", 11), bg=self.GREEN, fg=self.BG,
            activebackground=self.TEAL, activeforeground=self.BG,
            relief="flat", cursor="hand2", bd=0, padx=20, pady=8)
        self.start_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        self.stop_btn = tk.Button(
            btn_frame, text="\u23f9  STOP", command=self.stop,
            font=("Segoe UI Semibold", 11), bg=self.CARD, fg=self.DIM,
            activebackground=self.RED, activeforeground=self.BG,
            relief="flat", cursor="hand2", bd=0, padx=20, pady=8,
            state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0))

        # Footer
        footer = tk.Frame(content, bg=self.BG)
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=(12, 4))
        tk.Label(footer, text="Closes to tray  \u2022  Right-click tray icon for menu",
                 bg=self.BG, fg=self.DIM, font=("Segoe UI", 8)).pack()

    def _draw_pulse(self, color):
        self.pulse_canvas.delete("all")
        self.pulse_canvas.create_oval(3, 3, 13, 13, fill=color, outline=color)

    def _animate_pulse(self):
        if not self.running:
            return
        self._pulse_state = not self._pulse_state
        color = self.GREEN if self._pulse_state else "#40a040"
        self._draw_pulse(color)
        self.root.after(800, self._animate_pulse)

    def _minimize_window(self):
        self.root.overrideredirect(False)
        self.root.iconify()

    def _on_map(self, event):
        if self.root.state() == "normal":
            self.root.overrideredirect(True)

    def _start_drag(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def _on_drag(self, event):
        x = self.root.winfo_pointerx() - self._offset_x
        y = self.root.winfo_pointery() - self._offset_y
        self.root.geometry(f"+{x}+{y}")

    def _create_tray_image(self, color="green"):
        img = Image.new("RGB", (64, 64), color=(30, 30, 46))
        draw = ImageDraw.Draw(img)
        fill_color = (166, 227, 161) if color == "green" else (243, 139, 168)
        draw.ellipse([12, 12, 52, 52], fill=fill_color)
        draw.text((22, 20), "PC", fill=(30, 30, 46))
        return img

    def minimize_to_tray(self):
        self.root.withdraw()
        if self.tray_icon is None:
            color = "green" if self.running else "red"
            menu = pystray.Menu(
                pystray.MenuItem("Show", self.show_window),
                pystray.MenuItem("Start", self.start),
                pystray.MenuItem("Stop", self.stop),
                pystray.MenuItem("Exit", self.quit_app),
            )
            self.tray_icon = pystray.Icon(
                "DontLockPC", self._create_tray_image(color),
                "Don't Lock My PC", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self, icon=None, item=None):
        self.root.after(0, self.root.deiconify)

    def quit_app(self, icon=None, item=None):
        self.running = False
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.root.destroy)

    def start(self, icon=None, item=None):
        try:
            self.interval = int(self.interval_var.get())
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

        if self.tray_icon:
            self.tray_icon.icon = self._create_tray_image("green")

        self._animate_pulse()
        self.thread = threading.Thread(target=self._keep_alive, daemon=True)
        self.thread.start()

    def stop(self, icon=None, item=None):
        self.running = False
        self._draw_pulse(self.RED)
        self.status_label.config(text="INACTIVE", fg=self.RED)
        self.card.config(highlightbackground=self.DIM)
        self.start_btn.config(state=tk.NORMAL, bg=self.GREEN, fg=self.BG)
        self.stop_btn.config(state=tk.DISABLED, bg=self.CARD, fg=self.DIM)
        self.interval_entry.config(state=tk.NORMAL)

        if self.tray_icon:
            self.tray_icon.icon = self._create_tray_image("red")

    def _send_input(self, *inputs):
        n = len(inputs)
        arr = (INPUT * n)(*inputs)
        ctypes.windll.user32.SendInput(n, ctypes.pointer(arr), ctypes.sizeof(INPUT))

    def _simulate_mouse_move(self):
        """Move mouse 1px using SendInput (hardware-level, resets lock timer)."""
        inp = INPUT()
        inp.type = INPUT_MOUSE
        inp.union.mi.dx = 1
        inp.union.mi.dy = 0
        inp.union.mi.mouseData = 0
        inp.union.mi.dwFlags = MOUSEEVENTF_MOVE
        inp.union.mi.time = 0
        inp.union.mi.dwExtraInfo = None
        self._send_input(inp)
        time.sleep(0.05)
        inp.union.mi.dx = -1
        self._send_input(inp)

    def _simulate_key_press(self):
        """Press and release F15 via SendInput — invisible key, no side effects."""
        key_down = INPUT()
        key_down.type = INPUT_KEYBOARD
        key_down.union.ki.wVk = VK_F15
        key_down.union.ki.wScan = 0
        key_down.union.ki.dwFlags = 0
        key_down.union.ki.time = 0
        key_down.union.ki.dwExtraInfo = None

        key_up = INPUT()
        key_up.type = INPUT_KEYBOARD
        key_up.union.ki.wVk = VK_F15
        key_up.union.ki.wScan = 0
        key_up.union.ki.dwFlags = KEYEVENTF_KEYUP
        key_up.union.ki.time = 0
        key_up.union.ki.dwExtraInfo = None

        self._send_input(key_down, key_up)

    def _keep_alive(self):
        while self.running:
            try:
                # 1. Tell Windows kernel not to sleep / turn off display
                ctypes.windll.kernel32.SetThreadExecutionState(
                    ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
                # 2. Simulate hardware mouse move (resets lock inactivity timer)
                self._simulate_mouse_move()
                # 3. Simulate F15 keypress (resets lock timer even under Group Policy)
                self._simulate_key_press()
                self.move_count += 1
                self.last_move_time = datetime.now().strftime("%H:%M:%S")
                self.root.after(0, self._update_info)
                time.sleep(self.interval)
            except Exception:
                pass
        # Reset execution state when stopped
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

    def _update_info(self):
        self.moves_label.config(text=f"Signals: {self.move_count}")
        self.time_label.config(text=f"Last: {self.last_move_time}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = DontLockPC()
    app.run()
