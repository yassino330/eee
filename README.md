# VacuumTube Remote

A Windows companion controller with a **Zoom Apps SDK** frontend and a local Python controller for a manually selected VacuumTube executable.

## What this version does

- React + TypeScript + Vite interface.
- Zoom Apps SDK integration: initializes inside the Zoom client and reads only basic meeting/user context when available.
- In-app command box: the user explicitly submits allowlisted commands such as `!up`, `!left`, `!play`, and `!mute`.
- Manual-only `VacuumTube.exe` selection using the Windows file picker. No automatic detection.
- Local allowlisted keyboard controls and validated YouTube video URL opening.
- Local controller binds to loopback (127.0.0.1), not the public network.
- Browser preview mode remains available for testing the local controls outside Zoom.

## Zoom policy boundary

Zoom's Meeting SDK is designed for human use cases and does not support bots or AI notetakers. Zoom's Zoom Apps data-access documentation identifies RTMS as the route for real-time meeting media and chat data. This project therefore uses the **Zoom Apps SDK**, not a second Meeting SDK participant, and does not read, scrape, or listen to meeting chat. It only acts on commands that the user deliberately enters into the VacuumTube Remote app panel.

This does **not** implement the requested `!commands` inside the regular Zoom chat. A chat-driven integration needs Zoom's explicit approval and must use the applicable authorized RTMS workflow. Do not add DOM scraping, hidden chat listeners, or automated participant behavior.

## Requirements

- Windows 10/11
- Node.js 22.12.0 or newer
- Python 3.10+
- A Zoom account and a Zoom Apps developer app configured with the deployed HTTPS Home URL

## Setup

1. Download or clone this repository to your Windows PC.
2. Run `install.bat` once. It installs Python and Node dependencies and creates a local `.env` file from `.env.example`.
3. Choose VacuumTube.exe manually in the app and launch it.
4. For local browser preview, run `start.bat`.
5. To run inside Zoom, deploy the Vite production build to an HTTPS host and configure that URL as your Zoom App's Home URL. In the Zoom Marketplace app build flow, enable the Zoom Apps SDK capabilities `getRunningContext`, `getMeetingContext`, and `getUserContext`.
6. On each Windows PC that will run VacuumTube, set `APP_ORIGIN` in its local `.env` to the exact HTTPS origin of your deployed app (for example, `https://remote.example.com`, with no trailing slash), then restart the local controller. This allows the hosted Zoom App to call that PC's loopback controller through CORS.
7. Install/test the Zoom App through the Zoom client. Opening localhost in a normal browser is only a preview; it does not make the page a Zoom App.

## Commands

- `!up`, `!down`, `!left`, `!right`
- `!enter`
- `!play`, `!pause`, `!mute`
- `!help`
- `!video <YouTube URL>` fills the video field; press Open to open it in your browser.

`!type` is intentionally disabled: arbitrary text injection is not supported.

## Safety notes

- Never expose the local controller on a public network.
- Keyboard control uses PyAutoGUI and sends input to the currently focused window. Focus VacuumTube before using the controls.
- The current YouTube action opens the validated video in the system browser; it does not guarantee that VacuumTube itself will navigate to it.
- Zoom Apps capabilities and supported contexts vary by Zoom client version and app configuration. The app must be configured and approved/published as required by Zoom.
