# VacuumTube Remote

Windows desktop launcher with a local Zoom meeting-chat reader using Windows UI Automation (UIA). It does not use screenshots or OCR.

## Setup

1. Install Python 3.10 or newer.
2. Download this repository.
3. Run `install.bat`.
4. Run `start.bat`.
5. Paste your Zoom meeting invite link.
6. Click **Browse** and select the actual `VacuumTube.exe`.
7. Click **START — OPEN ZOOM + VACUUMTUBE**.
8. Join the Zoom meeting and open the normal meeting chat panel.
9. Click **TEST CHAT READER**. The test displays a sample of text Windows can read from Zoom.
10. If the test can see chat text, click **START CHAT LISTENER**.

## Supported chat commands

- `!up`
- `!down`
- `!left`
- `!right`
- `!enter`
- `!play`
- `!pause`
- `!mute`

The reader polls text exposed by Zoom's visible Windows UI Automation controls about once per second. It does not capture screenshots, upload screen contents, or use Zoom API credentials.

## Important compatibility note

This method only works if the installed Zoom client exposes its meeting-chat messages through Windows accessibility/UI Automation. Some Zoom versions or chat layouts may expose only the chat panel and not individual message text. **Use TEST CHAT READER before relying on it.** If the test sample does not contain the chat messages, this method cannot read those messages on that Zoom build; it will not silently claim to be working.

Keep the meeting chat open. The app reads only controls exposed by the local Zoom desktop window. Repeated identical command lines have a duplicate-suppression window.

The VacuumTube player window must have a title containing “VacuumTube” for reliable focusing.

## Settings

Settings are saved to `%APPDATA%\\VacuumTubeRemote\\settings.json`. No `.env` file or Zoom API credentials are used.

## Troubleshooting

- **No Zoom window found:** use the Zoom desktop client and make sure the meeting window is open.
- **Test shows no chat messages:** your Zoom build is not exposing the message text through UI Automation. This is a compatibility limitation, not a command syntax issue.
- **Commands are visible in the test but do not control the player:** make sure the player is open and its window title includes “VacuumTube”.

This is a local Windows accessibility workaround, not an official Zoom chat integration.
