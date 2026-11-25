from __future__ import annotations
import json, os, re, subprocess, webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import pyautogui

APP_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "VacuumTubeRemote"
SETTINGS_FILE = APP_DIR / "settings.json"
APP_DIR.mkdir(parents=True, exist_ok=True)

def load_settings():
    try: return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return {}

def save_settings(data):
    SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VacuumTube Remote")
        self.geometry("650x570")
        self.minsize(560, 500)
        self.configure(bg="#0b0e14")
        saved = load_settings()
        self.exe = tk.StringVar(value=saved.get("executable", ""))
        self.meeting = tk.StringVar(value=saved.get("meeting_url", ""))
        self.status = tk.StringVar(value="Ready. Enter your Zoom meeting and select VacuumTube.exe.")
        self.started = False
        self.build()

    def label(self, parent, text, color="#a7e875", size=10, bold="bold"):
        return tk.Label(parent, text=text, bg=parent["bg"], fg=color, font=("Segoe UI", size, bold))

    def build(self):
        head = tk.Frame(self, bg="#0b0e14"); head.pack(fill="x", padx=26, pady=(24, 14))
        self.label(head, "VACUUMTUBE REMOTE", size=10).pack(anchor="w")
        self.label(head, "Meeting launcher", color="#f4f5f8", size=23).pack(anchor="w", pady=(5, 0))
        self.label(head, "Enter your meeting, choose the player, then press Start.", color="#9ba6b8", size=10, bold="normal").pack(anchor="w", pady=5)
        panel = tk.Frame(self, bg="#151a24", highlightbackground="#ffffff22", highlightthickness=1)
        panel.pack(fill="x", padx=26, pady=8)
        self.label(panel, "01  /  ZOOM MEETING", color="#91a0b9").pack(anchor="w", padx=18, pady=(18, 7))
        tk.Entry(panel, textvariable=self.meeting, bg="#0e131c", fg="#f4f5f8", insertbackground="white", relief="flat", font=("Segoe UI", 10)).pack(fill="x", padx=18, ipady=10)
        self.label(panel, "Paste the Zoom meeting invite link.", color="#8290a6", size=9, bold="normal").pack(anchor="w", padx=18, pady=(5, 16))
        self.label(panel, "02  /  VACUUMTUBE APPLICATION", color="#91a0b9").pack(anchor="w", padx=18, pady=(0, 7))
        row = tk.Frame(panel, bg="#151a24"); row.pack(fill="x", padx=18)
        tk.Entry(row, textvariable=self.exe, bg="#0e131c", fg="#f4f5f8", insertbackground="white", relief="flat", font=("Segoe UI", 9)).pack(side="left", fill="x", expand=True, ipady=10)
        tk.Button(row, text="Browse…", command=self.browse, bg="#273245", fg="white", relief="flat", padx=16, pady=8).pack(side="left", padx=(8, 0))
        self.label(panel, "Select VacuumTube.exe manually. The path is remembered.", color="#8290a6", size=9, bold="normal").pack(anchor="w", padx=18, pady=(5, 18))
        tk.Button(self, text="START  —  OPEN MEETING + VACUUMTUBE", command=self.start, bg="#a7e875", fg="#101710", relief="flat", font=("Segoe UI", 10, "bold"), pady=13).pack(fill="x", padx=26, pady=12)
        controls = tk.Frame(self, bg="#151a24", highlightbackground="#ffffff22", highlightthickness=1)
        controls.pack(fill="x", padx=26, pady=8)
        self.label(controls, "LOCAL PLAYER CONTROLS", color="#91a0b9").pack(anchor="w", padx=16, pady=(13, 8))
        grid = tk.Frame(controls, bg="#151a24"); grid.pack(pady=(0, 14))
        for label, key, r, c in [("↑","up",0,1),("←","left",1,0),("ENTER","enter",1,1),("→","right",1,2),("↓","down",2,1),("PLAY / PAUSE","space",3,0),("MUTE","m",3,2)]:
            tk.Button(grid, text=label, command=lambda k=key:self.press(k), bg="#273245", fg="white", relief="flat", padx=16, pady=8).grid(row=r,column=c,padx=4,pady=4,sticky="ew")
        box = tk.Frame(self, bg="#202735"); box.pack(fill="x", padx=26, pady=(4, 8))
        self.label(box, "STATUS", color="#91a0b9").pack(anchor="w", padx=13, pady=(10, 3))
        tk.Label(box, textvariable=self.status, bg="#202735", fg="#c4ccda", font=("Segoe UI", 9), wraplength=570, justify="left").pack(anchor="w", padx=13, pady=(0, 10))
        tk.Label(self, text="Normal Zoom chat commands are not connected in this build.", bg="#0b0e14", fg="#e6ad5a", font=("Segoe UI", 9, "bold")).pack(pady=8)

    def browse(self):
        path = filedialog.askopenfilename(title="Find VacuumTube.exe", filetypes=[("VacuumTube executable","VacuumTube.exe"),("Windows applications","*.exe")])
        if path:
            if Path(path).name.lower() != "vacuumtube.exe":
                messagebox.showerror("Wrong file", "Please select the actual VacuumTube.exe file."); return
            self.exe.set(path); self.status.set("VacuumTube.exe selected.")

    def start(self):
        meeting = self.meeting.get().strip()
        exe = Path(self.exe.get().strip().strip('"'))
        if not re.match(r"^https://([\w-]+\.)?(zoom\.us|zoom\.com)/", meeting, re.I):
            messagebox.showerror("Zoom meeting link needed", "Paste a valid HTTPS Zoom meeting invite link."); return
        if not exe.is_file() or exe.name.lower() != "vacuumtube.exe":
            messagebox.showerror("VacuumTube not selected", "Click Browse and select VacuumTube.exe."); return
        save_settings({"executable":str(exe), "meeting_url":meeting})
        try:
            webbrowser.open(meeting)
            subprocess.Popen([str(exe)], cwd=str(exe.parent))
            self.started = True
            self.status.set("Zoom meeting opened and VacuumTube launched. Local controller is active. Zoom chat commands are not connected.")
        except OSError as exc:
            messagebox.showerror("Could not start", str(exc)); self.status.set("Startup failed.")

    def press(self, key):
        if not self.started:
            self.status.set("Click START first to launch VacuumTube."); return
        try:
            pyautogui.press(key); self.status.set(f"Sent local keyboard input: {key}")
        except Exception as exc: self.status.set(f"Could not send input: {exc}")

if __name__ == "__main__":
    App().mainloop()
