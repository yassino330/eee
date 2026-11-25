from __future__ import annotations

import json
import os
import re
import subprocess
import time
import webbrowser
from pathlib import Path
from typing import Literal

import jwt
import pyautogui
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()
APP_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "VacuumTubeRemote"
SETTINGS_FILE = APP_DIR / "settings.json"
APP_DIR.mkdir(parents=True, exist_ok=True)
APP_ORIGIN = os.getenv("APP_ORIGIN", "http://127.0.0.1:5173")

app = FastAPI(title="VacuumTube Remote Local Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[APP_ORIGIN, "http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

def load_settings() -> dict:
    if not SETTINGS_FILE.exists():
        return {"executable": ""}
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"executable": ""}

def save_settings(data: dict) -> None:
    SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

class Command(BaseModel):
    command: Literal["up", "down", "left", "right", "enter", "play", "pause", "mute"]

class VideoCommand(BaseModel):
    url: str = Field(min_length=1, max_length=500)

class SignatureRequest(BaseModel):
    meeting_number: str = Field(pattern=r"^[0-9]{9,12}$")

@app.get("/health")
def health():
    return {"ok": True, "selected": bool(load_settings().get("executable"))}

@app.get("/settings")
def settings():
    path = load_settings().get("executable", "")
    return {"selected": bool(path), "filename": Path(path).name if path else ""}

@app.post("/zoom/signature")
def zoom_signature(payload: SignatureRequest):
    sdk_key = os.getenv("ZOOM_MEETING_SDK_KEY", "").strip()
    sdk_secret = os.getenv("ZOOM_MEETING_SDK_SECRET", "").strip()
    if not sdk_key or not sdk_secret:
        raise HTTPException(status_code=503, detail="Add Zoom SDK key and secret to your local .env file, then restart the controller.")
    now = int(time.time())
    claims = {
        "appKey": sdk_key,
        "mn": payload.meeting_number,
        "role": 0,
        "iat": now - 30,
        "exp": now + 60 * 60,
        "tokenExp": now + 60 * 60,
    }
    signature = jwt.encode(claims, sdk_secret, algorithm="HS256")
    return {"sdkKey": sdk_key, "signature": signature}

@app.post("/select-executable")
def select_executable():
    # Manual-only selection. No automatic filesystem discovery is performed.
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(
            title="Select VacuumTube.exe manually",
            filetypes=[("VacuumTube application", "VacuumTube.exe"), ("Windows executable", "*.exe")],
        )
        root.destroy()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not open file picker: {exc}")
    if not path:
        return {"selected": False, "cancelled": True}
    if not Path(path).is_file() or Path(path).suffix.lower() != ".exe":
        raise HTTPException(status_code=400, detail="Please select a valid .exe file.")
    save_settings({"executable": path})
    return {"selected": True, "filename": Path(path).name}

@app.post("/launch")
def launch():
    path = load_settings().get("executable", "")
    if not path or not Path(path).is_file():
        raise HTTPException(status_code=400, detail="Select VacuumTube.exe first.")
    subprocess.Popen([path], cwd=str(Path(path).parent))
    return {"launched": True}

@app.post("/command")
def command(payload: Command):
    keys = {
        "up": "up", "down": "down", "left": "left", "right": "right",
        "enter": "enter", "play": "space", "pause": "space", "mute": "m",
    }
    pyautogui.press(keys[payload.command])
    return {"sent": payload.command}

@app.post("/video")
def open_video(payload: VideoCommand):
    match = re.fullmatch(
        r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)?([A-Za-z0-9_-]{11})",
        payload.url.strip(),
    )
    if not match:
        raise HTTPException(status_code=400, detail="Enter a valid YouTube video URL or 11-character ID.")
    webbrowser.open(f"https://www.youtube.com/watch?v={match.group(1)}")
    return {"opened": True}
