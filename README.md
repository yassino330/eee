# VacuumTube Remote

A Windows companion app for controlling a user-selected VacuumTube executable, with a Zoom Meeting SDK for Web front end.

## Current scope

- React + TypeScript + Vite front end using the installed `@zoom/meetingsdk` package.
- Python local controller with a **manual-only** executable picker. It never scans the PC or auto-detects VacuumTube.
- Local control API is bound to `127.0.0.1` only.
- Safe command allowlist: navigation, play/pause, mute, and opening a YouTube URL after explicit validation.

## Important Zoom limitation

The Meeting SDK embeds a meeting experience in this app; it does not attach to an already-running Zoom desktop meeting. Zoom's Meeting SDK is intended for human meeting experiences and does not support bots or automated notetakers. This starter does **not** implement an unattended meeting participant or silently harvest meeting chat. Before adding any chat-driven automation, obtain confirmation from Zoom that the exact use case is permitted and use only documented SDK chat APIs with clear participant/host consent.

## Requirements

- Node.js 22.12.0 or newer
- Python 3.10+
- A Zoom Meeting SDK app and credentials configured locally (never commit secrets)

## Front end

```bash
npm install
npm run dev
```

Create `.env.local` from `.env.example` and configure the public SDK key and a server-generated meeting signature. Never put the SDK secret in browser code.

## Local controller

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python local_agent.py
```

Open http://127.0.0.1:8765 in the browser to check the local agent.

## Manual VacuumTube selection

Use the app's Browse button to select `VacuumTube.exe`. The selected path is saved in the user's local config file. No automatic detection is performed.

## Security

- Keep Zoom SDK secrets out of Git.
- Keep the local agent bound to loopback.
- Do not expose the local agent to the public internet.
- Only allowlisted commands are accepted; arbitrary shell commands are never executed.
