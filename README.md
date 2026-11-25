# VacuumTube Remote

A native Windows launcher for starting a Zoom meeting and a manually selected VacuumTube installation.

## Current workflow

1. Run `install.bat` once.
2. Run `start.bat`.
3. Paste your Zoom meeting invite link.
4. Click **Browse** and select the actual `VacuumTube.exe`.
5. Click **START**. The app opens the Zoom meeting in your default browser/Zoom client and launches VacuumTube.
6. Use the local arrow, Enter, Play/Pause, and Mute controls in the launcher.

The selected executable and meeting link are saved locally in:

`%APPDATA%\VacuumTubeRemote\settings.json`

The executable is selected manually; the app does not scan your computer for it. No `.env` file, Zoom credentials, or server setup is required for this local launcher.

## Important Zoom chat limitation

This build does **not** read or monitor normal Zoom meeting chat, and it does not receive commands sent by other participants. Zoom's supported chat-data integration requires Zoom-authorized access. The local controls in this build are not a substitute for that integration. No hidden Zoom-client scraping or chat interception is used.

## Requirements

- Windows 10 or Windows 11
- Python 3.10+
- VacuumTube installed locally
- Zoom installed, or a browser capable of opening Zoom meeting links

## Notes

- Keyboard input is sent to the currently focused application. Focus VacuumTube before using local controls.
- The Zoom meeting link must be an HTTPS link on a Zoom domain.
- This is a local launcher/controller, not a Zoom chat bot.
