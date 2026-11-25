# VacuumTube Remote

A Windows companion app with a Zoom Meeting SDK for Web meeting view and a local Python controller for a manually selected VacuumTube executable.

## What works in this starter

- React + TypeScript + Vite interface.
- Zoom Meeting SDK 6.10.5 component-view initialization and visible meeting join/leave flow.
- Backend-generated, short-lived Meeting SDK signature. The SDK secret stays in the local Python process and is never sent to browser JavaScript.
- Manual-only `VacuumTube.exe` selection using the Windows file picker. No automatic detection.
- Local allowlisted keyboard controls and validated YouTube video URL opening.
- Local controller binds to loopback (127.0.0.1), not the public network.

## Zoom policy boundary

Zoom's Meeting SDK documentation says the SDK is designed for human use cases and does not support bots or AI notetakers. This starter therefore joins as a visible, user-operated meeting session and does **not** automatically read meeting chat or execute commands from other participants. Do not add unattended chat scraping or bot-like command execution. Ask Zoom to confirm the exact proposed workflow before extending it.

The Meeting SDK embeds a meeting in this app. It does not attach to a meeting already open in the Zoom desktop client.

## Requirements

- Windows 10/11
- Node.js 22.12.0 or newer
- Python 3.10+

## Setup

1. Copy `.env.example` to `.env`.
2. In your Zoom Marketplace developer app, enable the Meeting SDK and copy the SDK Key and SDK Secret into the local `.env` file:
   - `ZOOM_MEETING_SDK_KEY=...`
   - `ZOOM_MEETING_SDK_SECRET=...`
3. Never commit `.env`, share the secret, or put it in a `VITE_*` browser variable.
4. Open a terminal in the repository:

```powershell
npm install
npm run dev
```

5. In a second PowerShell window:

```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn local_agent:app --host 127.0.0.1 --port 8765
```

6. Open the Vite URL shown in the first terminal (normally http://127.0.0.1:5173).
7. Choose `VacuumTube.exe` manually, then launch it.
8. Enter a Zoom Meeting ID, passcode, and display name, then click Join. The app joins as a separate visible participant; the meeting host may need to admit it.

## Notes

- Meeting SDK signatures are generated locally by the Python backend using the SDK secret and a short expiry.
- For meetings outside your developer account, Zoom may require app review and user authorization.
- The `!type` command is intentionally not implemented: arbitrary text injection is risky and has not been authorized.
- Keyboard control uses PyAutoGUI and sends input to the currently focused window. Focus VacuumTube before using the manual controls.
- The current YouTube action opens the validated video in the system browser; it does not guarantee that VacuumTube itself will navigate to it.
