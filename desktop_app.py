from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import pyautogui
import pygetwindow
from pywinauto import Desktop

APP_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "VacuumTubeRemote"
SETTINGS_FILE = APP_DIR / "settings.json"
APP_DIR.mkdir(parents=True, exist_ok=True)

COMMANDS = {
    "!up": "up", "!down": "down", "!left": "left", "!right": "right",
    "!enter": "enter", "!play": "space", "!pause": "space", "!mute": "m",
}
def load_settings():
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

def save_settings(data):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VacuumTube Remote")
        self.geometry("700x700")
        self.minsize(590, 630)
        self.configure(bg="#0b0e14")
        saved = load_settings()
        self.exe = tk.StringVar(value=saved.get("executable", ""))
        self.meeting = tk.StringVar(value=saved.get("meeting_url", ""))
        self.status = tk.StringVar(value="Ready. Enter your Zoom meeting and select VacuumTube.exe.")
        self.started = False
        self.listener_running = False
        self.listener_thread = None
        self.stop_event = threading.Event()
        self.seen = {}
        self.build()

    def label(self, parent, text, color="#a7e875", size=10, bold="bold"):
        return tk.Label(parent, text=text, bg=parent["bg"], fg=color, font=("Segoe UI", size, bold))

    def build(self):
        head = tk.Frame(self, bg="#0b0e14")
        head.pack(fill="x", padx=24, pady=(18, 10))
        self.label(head, "VACUUMTUBE REMOTE", size=10).pack(anchor="w")
        self.label(head, "Meeting launcher", color="#f4f5f8", size=22).pack(anchor="w", pady=(3, 0))
        self.label(head, "Open Zoom + VacuumTube, then read accessible text from the meeting chat.",
                   color="#9ba6b8", size=9, bold="normal").pack(anchor="w", pady=4)

        panel = tk.Frame(self, bg="#151a24", highlightbackground="#ffffff22", highlightthickness=1)
        panel.pack(fill="x", padx=24, pady=7)
        self.label(panel, "01  /  ZOOM MEETING", color="#91a0b9").pack(anchor="w", padx=16, pady=(13, 6))
        tk.Entry(panel, textvariable=self.meeting, bg="#0e131c", fg="#f4f5f8",
                 insertbackground="white", relief="flat", font=("Segoe UI", 10)).pack(fill="x", padx=16, ipady=8)
        self.label(panel, "Paste the Zoom meeting invite link.", color="#8290a6", size=8, bold="normal").pack(anchor="w", padx=16, pady=(4, 12))

        self.label(panel, "02  /  VACUUMTUBE.EXE", color="#91a0b9").pack(anchor="w", padx=16, pady=(0, 6))
        row = tk.Frame(panel, bg="#151a24")
        row.pack(fill="x", padx=16)
        tk.Entry(row, textvariable=self.exe, bg="#0e131c", fg="#f4f5f8",
                 insertbackground="white", relief="flat", font=("Segoe UI", 9)).pack(side="left", fill="x", expand=True, ipady=8)
        tk.Button(row, text="Browse…", command=self.browse_exe, bg="#273245", fg="white",
                  relief="flat", padx=14, pady=7).pack(side="left", padx=(8, 0))
        self.label(panel, "Select the actual VacuumTube.exe manually.", color="#8290a6", size=8, bold="normal").pack(anchor="w", padx=16, pady=(4, 12))

        tk.Button(self, text="START  —  OPEN ZOOM + VACUUMTUBE", command=self.start,
                  bg="#a7e875", fg="#101710", relief="flat",
                  font=("Segoe UI", 10, "bold"), pady=11).pack(fill="x", padx=24, pady=(8, 5))

        listener = tk.Frame(self, bg="#151a24", highlightbackground="#ffffff22", highlightthickness=1)
        listener.pack(fill="x", padx=24, pady=7)
        self.label(listener, "03  /  ZOOM CHAT ACCESSIBILITY READER", color="#91a0b9").pack(anchor="w", padx=15, pady=(11, 4))
        self.label(listener, "Reads text exposed by Zoom's Windows accessibility controls. Keep the meeting chat open.",
                   color="#c4ccda", size=8, bold="normal").pack(anchor="w", padx=15, pady=(0, 8))
        buttons = tk.Frame(listener, bg="#151a24")
        buttons.pack(fill="x", padx=15, pady=(0, 12))
        self.listener_button = tk.Button(buttons, text="START CHAT LISTENER", command=self.toggle_listener,
                                         bg="#273245", fg="white", relief="flat", padx=14, pady=8)
        self.listener_button.pack(side="left")
        tk.Button(buttons, text="TEST CHAT READER", command=self.test_reader,
                  bg="#273245", fg="white", relief="flat", padx=14, pady=8).pack(side="left", padx=8)

        controls = tk.Frame(self, bg="#151a24", highlightbackground="#ffffff22", highlightthickness=1)
        controls.pack(fill="x", padx=24, pady=7)
        self.label(controls, "MANUAL TEST CONTROLS", color="#91a0b9").pack(anchor="w", padx=15, pady=(10, 5))
        grid = tk.Frame(controls, bg="#151a24")
        grid.pack(pady=(0, 10))
        for label, key, r, c in [("↑","up",0,1),("←","left",1,0),("ENTER","enter",1,1),
                                 ("→","right",1,2),("↓","down",2,1),("PLAY","space",3,0),("MUTE","m",3,2)]:
            tk.Button(grid, text=label, command=lambda k=key:self.send_key(k),
                      bg="#273245", fg="white", relief="flat", padx=13, pady=6).grid(row=r,column=c,padx=3,pady=3)

        box = tk.Frame(self, bg="#202735")
        box.pack(fill="x", padx=24, pady=(4, 7))
        self.label(box, "STATUS", color="#91a0b9").pack(anchor="w", padx=12, pady=(8, 2))
        tk.Label(box, textvariable=self.status, bg="#202735", fg="#c4ccda",
                 font=("Segoe UI", 8), wraplength=630, justify="left").pack(anchor="w", padx=12, pady=(0, 8))

    def browse_exe(self):
        path = filedialog.askopenfilename(title="Find VacuumTube.exe",
            filetypes=[("VacuumTube executable", "VacuumTube.exe"), ("Windows applications", "*.exe")])
        if path:
            if Path(path).name.lower() != "vacuumtube.exe":
                messagebox.showerror("Wrong file", "Please select the actual VacuumTube.exe file.")
                return
            self.exe.set(path)
            self.status.set("VacuumTube.exe selected.")

    def browse_tesseract(self):
        path = filedialog.askopenfilename(title="Find Tesseract OCR",
            filetypes=[("Tesseract executable", "tesseract.exe"), ("Windows applications", "*.exe")])
        if path:
            self.tesseract.set(path)
            self.status.set("Tesseract OCR selected.")

    def start(self):
        meeting = self.meeting.get().strip()
        exe = Path(self.exe.get().strip().strip('"'))
        if not re.match(r"^https://([\w-]+\.)?(zoom\.us|zoom\.com)/", meeting, re.I):
            messagebox.showerror("Zoom meeting link needed", "Paste a valid HTTPS Zoom meeting invite link.")
            return
        if not exe.is_file() or exe.name.lower() != "vacuumtube.exe":
            messagebox.showerror("VacuumTube not selected", "Click Browse and select VacuumTube.exe.")
            return
        save_settings({"executable":str(exe), "meeting_url":meeting})
        try:
            webbrowser.open(meeting)
            subprocess.Popen([str(exe)], cwd=str(exe.parent))
            self.started = True
            self.status.set("Zoom meeting opened and VacuumTube launched. Join, open meeting chat, then start the chat reader.")
        except OSError as exc:
            messagebox.showerror("Could not start", str(exc))
            self.status.set("Startup failed.")

    def send_key(self, key):
        exe = self.exe.get().strip().strip('"')
        if not self.started or not Path(exe).is_file():
            self.status.set("Click START first.")
            return
        try:
            wins = pygetwindow.getWindowsWithTitle("VacuumTube")
            if wins:
                wins[0].activate()
                time.sleep(0.15)
                pyautogui.press(key)
                # Bring Zoom back so its chat remains visible for OCR.
                zoom = pygetwindow.getWindowsWithTitle("Zoom")
                if zoom:
                    zoom[0].activate()
                self.status.set("Sent key to VacuumTube: " + key)
            else:
                self.status.set("VacuumTube window not found. Check its window title.")
        except Exception as exc:
            self.status.set("Input error: " + str(exc))

    def read_accessible_commands(self):
        """Read UI Automation text exposed by Zoom; never capture the screen."""
        desktop = Desktop(backend="uia")
        zoom_windows = []
        for window in desktop.windows():
            try:
                title = window.window_text() or ""
                if "zoom" in title.lower() and window.is_visible():
                    zoom_windows.append(window)
            except Exception:
                continue
        if not zoom_windows:
            raise RuntimeError("No visible Zoom window found. Open the Zoom desktop meeting window.")

        texts = []
        for window in zoom_windows:
            try:
                controls = [window] + window.descendants()
            except Exception:
                controls = [window]
            for control in controls:
                try:
                    value = (control.window_text() or "").strip()
                    if value and value not in texts:
                        texts.append(value)
                except Exception:
                    continue
        raw = "\\n".join(texts)
        found = []
        for line in raw.splitlines():
            match = re.search(r"!(up|down|left|right|enter|play|pause|mute)\b", line.lower())
            if match:
                found.append(("!" + match.group(1), line.strip()))
        return found, raw

    def test_reader(self):
        try:
            found, raw = self.read_accessible_commands()
            commands = ", ".join(command for command, _ in found) if found else "No supported commands exposed."
            preview = raw[:700] if raw else "(Zoom exposes no readable text controls.)"
            messagebox.showinfo("Zoom chat reader test", f"Commands: {commands}\\n\\nAccessible text sample:\\n{preview}")
            self.status.set("Chat reader test complete: " + commands)
        except Exception as exc:
            messagebox.showerror("Chat reader problem", str(exc))
            self.status.set("Chat reader test failed: " + str(exc))

    def toggle_listener(self):
        if self.listener_running:
            self.stop_event.set()
            self.listener_running = False
            self.listener_button.config(text="START CHAT LISTENER")
            self.status.set("Chat listener stopped.")
            return
        if not self.started:
            messagebox.showwarning("Start the app first", "Click START to open Zoom and VacuumTube first.")
            return
        try:
            self.read_accessible_commands()
        except Exception as exc:
            messagebox.showerror("Zoom accessibility unavailable", str(exc))
            return
        self.stop_event.clear()
        self.listener_running = True
        self.listener_button.config(text="STOP CHAT LISTENER")
        self.listener_thread = threading.Thread(target=self.listener_loop, daemon=True)
        self.listener_thread.start()
        self.status.set("Reading accessible text from Zoom. Keep the meeting chat open.")

    def listener_loop(self):
        while not self.stop_event.is_set():
            try:
                found, _ = self.read_accessible_commands()
                now = time.time()
                self.seen = {key: value for key, value in self.seen.items() if now - value < 180}
                for command, line in found:
                    signature = (command, re.sub(r"\s+", " ", line.lower()).strip())
                    if signature in self.seen:
                        continue
                    self.seen[signature] = now
                    self.after(0, lambda c=command, l=line: self.handle_chat_command(c, l))
            except Exception as exc:
                self.after(0, lambda error=str(exc): self.status.set("Chat reader error: " + error))
            time.sleep(1.0)

    def handle_chat_command(self, command, line):
        self.status.set("Zoom chat command detected: " + command + " | " + line[:90])
        self.send_key(COMMANDS[command])

    def on_close(self):
        self.stop_event.set()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
