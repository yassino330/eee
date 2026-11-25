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
import pytesseract
from PIL import ImageOps

APP_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "VacuumTubeRemote"
SETTINGS_FILE = APP_DIR / "settings.json"
APP_DIR.mkdir(parents=True, exist_ok=True)

COMMANDS = {
    "!up": "up", "!down": "down", "!left": "left", "!right": "right",
    "!enter": "enter", "!play": "space", "!pause": "space", "!mute": "m",
}
TESSERACT_CANDIDATES = [
    shutil.which("tesseract"),
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]

def load_settings():
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

def save_settings(data):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def find_tesseract():
    for candidate in TESSERACT_CANDIDATES:
        if candidate and Path(candidate).is_file():
            return candidate
    return ""

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
        self.tesseract = tk.StringVar(value=saved.get("tesseract_path", find_tesseract()))
        self.status = tk.StringVar(value="Ready. Enter your Zoom meeting and select VacuumTube.exe.")
        self.started = False
        self.ocr_running = False
        self.ocr_thread = None
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
        self.label(head, "Open Zoom + VacuumTube, then listen to visible chat using local OCR.",
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

        self.label(panel, "03  /  OCR ENGINE (TESSERACT)", color="#91a0b9").pack(anchor="w", padx=16, pady=(0, 6))
        trow = tk.Frame(panel, bg="#151a24")
        trow.pack(fill="x", padx=16)
        tk.Entry(trow, textvariable=self.tesseract, bg="#0e131c", fg="#f4f5f8",
                 insertbackground="white", relief="flat", font=("Segoe UI", 8)).pack(side="left", fill="x", expand=True, ipady=8)
        tk.Button(trow, text="Find…", command=self.browse_tesseract, bg="#273245", fg="white",
                  relief="flat", padx=14, pady=7).pack(side="left", padx=(8, 0))
        self.label(panel, "Install Tesseract OCR for Windows, then select tesseract.exe if not found automatically.",
                   color="#8290a6", size=8, bold="normal").pack(anchor="w", padx=16, pady=(4, 13))

        tk.Button(self, text="START  —  OPEN ZOOM + VACUUMTUBE", command=self.start,
                  bg="#a7e875", fg="#101710", relief="flat",
                  font=("Segoe UI", 10, "bold"), pady=11).pack(fill="x", padx=24, pady=(8, 5))

        ocr = tk.Frame(self, bg="#151a24", highlightbackground="#ffffff22", highlightthickness=1)
        ocr.pack(fill="x", padx=24, pady=7)
        self.label(ocr, "04  /  NORMAL ZOOM CHAT OCR", color="#91a0b9").pack(anchor="w", padx=15, pady=(11, 4))
        self.label(ocr, "Keep Zoom's meeting chat open and visible. OCR reads only text visible on your screen.",
                   color="#c4ccda", size=8, bold="normal").pack(anchor="w", padx=15, pady=(0, 8))
        buttons = tk.Frame(ocr, bg="#151a24")
        buttons.pack(fill="x", padx=15, pady=(0, 12))
        self.ocr_button = tk.Button(buttons, text="START CHAT LISTENER", command=self.toggle_ocr,
                                    bg="#273245", fg="white", relief="flat", padx=14, pady=8)
        self.ocr_button.pack(side="left")
        tk.Button(buttons, text="TEST OCR NOW", command=self.test_ocr,
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
        tess = self.tesseract.get().strip().strip('"')
        if not re.match(r"^https://([\w-]+\.)?(zoom\.us|zoom\.com)/", meeting, re.I):
            messagebox.showerror("Zoom meeting link needed", "Paste a valid HTTPS Zoom meeting invite link.")
            return
        if not exe.is_file() or exe.name.lower() != "vacuumtube.exe":
            messagebox.showerror("VacuumTube not selected", "Click Browse and select VacuumTube.exe.")
            return
        if tess and not Path(tess).is_file():
            messagebox.showerror("Tesseract not found", "Select the installed tesseract.exe file.")
            return
        save_settings({"executable":str(exe), "meeting_url":meeting, "tesseract_path":tess})
        try:
            webbrowser.open(meeting)
            subprocess.Popen([str(exe)], cwd=str(exe.parent))
            self.started = True
            self.status.set("Zoom meeting opened and VacuumTube launched. Open the meeting chat, keep it visible, then start the OCR listener.")
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

    def get_ocr_engine(self):
        tess = self.tesseract.get().strip().strip('"') or find_tesseract()
        if not tess or not Path(tess).is_file():
            raise RuntimeError("Tesseract OCR is not installed or selected. Install it and browse to tesseract.exe.")
        pytesseract.pytesseract.tesseract_cmd = tess
        return pytesseract

    def read_visible_commands(self):
        engine = self.get_ocr_engine()
        shot = pyautogui.screenshot()
        # Enlarge and improve contrast to help OCR read Zoom's chat text.
        shot = ImageOps.grayscale(shot)
        shot = ImageOps.autocontrast(shot)
        shot = shot.resize((shot.width * 2, shot.height * 2))
        text = engine.image_to_string(shot, config="--psm 6")
        found = []
        for line in text.splitlines():
            match = re.search(r"!(up|down|left|right|enter|play|pause|mute)\b", line.lower())
            if match:
                found.append(("!" + match.group(1), line.strip()))
        return found, text

    def test_ocr(self):
        try:
            found, raw = self.read_visible_commands()
            self.status.set("OCR test: " + (", ".join(c for c, _ in found) if found else "No supported !commands visible. Keep the Zoom chat panel open."))
        except Exception as exc:
            messagebox.showerror("OCR setup problem", str(exc))
            self.status.set("OCR test failed.")

    def toggle_ocr(self):
        if self.ocr_running:
            self.stop_event.set()
            self.ocr_running = False
            self.ocr_button.config(text="START CHAT LISTENER")
            self.status.set("OCR listener stopped.")
            return
        if not self.started:
            messagebox.showwarning("Start the app first", "Click START to open Zoom and VacuumTube first.")
            return
        try:
            self.get_ocr_engine()
        except Exception as exc:
            messagebox.showerror("OCR setup problem", str(exc))
            return
        self.stop_event.clear()
        self.ocr_running = True
        self.ocr_button.config(text="STOP CHAT LISTENER")
        self.ocr_thread = threading.Thread(target=self.ocr_loop, daemon=True)
        self.ocr_thread.start()
        self.status.set("Listening to visible Zoom chat. Keep the chat panel on screen.")

    def ocr_loop(self):
        while not self.stop_event.is_set():
            try:
                found, _ = self.read_visible_commands()
                now = time.time()
                self.seen = {k:v for k,v in self.seen.items() if now-v < 180}
                for command, line in found:
                    signature = (command, re.sub(r"\s+", " ", line.lower()).strip())
                    if signature in self.seen:
                        continue
                    self.seen[signature] = now
                    self.after(0, lambda c=command, l=line: self.handle_chat_command(c, l))
            except Exception as exc:
                self.after(0, lambda e=str(exc): self.status.set("OCR error: " + e))
                time.sleep(2)
            time.sleep(1.2)

    def handle_chat_command(self, command, line):
        key = COMMANDS[command]
        self.status.set("Zoom chat command detected: " + command + " | " + line[:90])
        self.send_key(key)

    def on_close(self):
        self.stop_event.set()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
