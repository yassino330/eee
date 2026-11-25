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

1. Download or clone this repository to your Windows PC.
2. Run `install.bat` once. It installs the Python and Node dependencies and creates a local `.env` file from `.env.example`.
3. Open `.env` in Notepad. In your Zoom Marketplace developer app, enable Meeting SDK and enter your Client ID and Client Secret:
   - `ZOOM_MEETING_SDK_KEY=...`
   - `ZOOM_MEETING_SDK_SECRET=...`
4. Never commit `.env`, share the secret, or put it in a `VITE_*` browser variable.
5. Run `start.bat`. It starts the local controller and web interface, then opens the app in your browser.
6. Choose `VacuumTube.exe` manually, then launch it.
7. Enter a Zoom Meeting ID, passcode, and display name, then click Join. The app joins as a separate visible participant; the meeting host may need to admit it.

If you prefer manual setup, install Node.js 22.12.0+ and Python 3.10+, run `npm install`, install Python packages with `pip install -r requirements.txt`, then run the local agent with `uvicorn local_agent:app --host 127.0.0.1 --port 8765` and the frontend with `npm run dev`.

## Notes

- Meeting SDK signatures are generated locally by the Python backend using the SDK secret and a short expiry.
- For meetings outside your developer account, Zoom may require app review and user authorization.
- The `!type` command is intentionally not implemented: arbitrary text injection is risky and has not been authorized.
- Keyboard control uses PyAutoGUI and sends input to the currently focused window. Focus VacuumTube before using the manual controls.
- The current YouTube action opens the validated video in the system browser; it does not guarantee that VacuumTube itself will navigate to it.
