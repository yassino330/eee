# VacuumTube Remote

Windows desktop launcher with a local OCR listener for visible Zoom meeting chat.

## Setup

1. Install Python 3.10 or newer.
2. Install **Tesseract OCR for Windows**. The app needs the Tesseract program (tesseract.exe), not just the Python package. Official project: https://github.com/UB-Mannheim/tesseract/wiki.
3. Download this repository.
4. Run install.bat.
5. Run start.bat.
6. Paste your Zoom meeting invite link.
7. Click **Browse** and select the actual VacuumTube.exe.
8. If Tesseract was not found automatically, click **Find…** and select tesseract.exe.
9. Click **START — OPEN ZOOM + VACUUMTUBE**.
10. Join the Zoom meeting, open the meeting chat panel, and keep the chat visible on screen.
11. Click **START CHAT LISTENER**.

## Supported chat commands

- !up
- !down
- !left
- !right
- !enter
- !play
- !pause
- !mute

The OCR listener checks the visible desktop locally about once per second. It looks for supported command text in visible chat and sends the corresponding key to the VacuumTube window. It does not read Zoom's private chat messages or access Zoom's internal data.

## OCR limitations

- Zoom's chat must be open and visible. Messages that are off-screen, hidden, or not loaded cannot be detected.
- Keep Zoom's chat panel readable and avoid covering it with other windows.
- OCR can misread text, especially at small sizes or low contrast. Use a larger Zoom chat font if needed.
- Screenshots are processed locally on your PC and are not uploaded.
- Repeated identical command lines have a short duplicate-suppression window.
- The player window must have a title containing “VacuumTube” for reliable focusing.

## Settings

Settings are saved to %APPDATA%\\VacuumTubeRemote\\settings.json. No .env file or Zoom API credentials are used.

## Troubleshooting

- **Tesseract not installed or selected:** install Tesseract OCR and use Find… to select tesseract.exe.
- **No commands detected:** open Zoom chat, make it wider/larger, put a visible !up message in the chat, then click TEST OCR NOW.
- **Key not reaching VacuumTube:** make sure the player is open and its window title includes “VacuumTube”.

This is a local screen-OCR workaround, not an official Zoom chat integration. It only detects messages visibly rendered on the local screen.
