import { useEffect, useState } from "react";
import zoomSdk from "@zoom/appssdk";

const AGENT = "http://127.0.0.1:8765";
const COMMANDS = new Set(["up", "down", "left", "right", "enter", "play", "pause", "mute"]);

type ZoomState = { ready: boolean; runningContext: string; meeting: string; user: string; message: string };

export default function App() {
  const [agent, setAgent] = useState("Checking local controller…");
  const [selected, setSelected] = useState(false);
  const [videoUrl, setVideoUrl] = useState("");
  const [commandText, setCommandText] = useState("");
  const [status, setStatus] = useState("Ready. Commands are only sent after you press Send.");
  const [zoom, setZoom] = useState<ZoomState>({
    ready: false, runningContext: "Checking Zoom…", meeting: "", user: "", message: ""
  });

  useEffect(() => {
    let active = true;
    fetch(`${AGENT}/settings`)
      .then(r => r.json())
      .then(d => {
        if (!active) return;
        setSelected(Boolean(d.selected));
        setAgent(d.selected ? `Selected: ${d.filename}` : "No executable selected");
      })
      .catch(() => active && setAgent("Local controller not running"));

    async function connectZoomApp() {
      try {
        const config = await zoomSdk.config({
          capabilities: ["getRunningContext", "getMeetingContext", "getUserContext"]
        });
        const runningContext = String(config.runningContext || "Zoom App connected");
        let meeting = "";
        let user = "";
        if (runningContext.toLowerCase().includes("meeting")) {
          try {
            const context = await zoomSdk.getMeetingContext();
            meeting = String(context.meetingTopic || context.meetingID || "Active meeting");
          } catch { meeting = "Meeting context unavailable"; }
        }
        try {
          const context = await zoomSdk.getUserContext();
          user = String(context.screenName || "");
        } catch { /* user context is optional */ }
        if (active) setZoom({
          ready: true, runningContext, meeting, user,
          message: "Connected to the Zoom client. This app does not read meeting chat."
        });
      } catch {
        if (active) setZoom({
          ready: false, runningContext: "Browser preview",
          meeting: "", user: "",
          message: "Open this page as an installed Zoom App to connect it to your meeting. Browser preview still supports manual controls."
        });
      }
    }
    void connectZoomApp();
    return () => { active = false; };
  }, []);

  async function chooseExe() {
    try {
      const r = await fetch(`${AGENT}/select-executable`, { method: "POST" });
      const d = await r.json();
      setSelected(Boolean(d.selected));
      setAgent(d.selected ? `Selected: ${d.filename}` : "Selection cancelled");
    } catch { setAgent("Could not reach local controller"); }
  }

  async function launchExe() {
    try {
      const r = await fetch(`${AGENT}/launch`, { method: "POST" });
      const d = await r.json();
      setAgent(d.launched ? "VacuumTube launched" : (d.detail || "Launch failed"));
    } catch { setAgent("Could not reach local controller"); }
  }

  async function send(command: string) {
    if (!COMMANDS.has(command)) {
      setStatus("That command is not allowed. Use !help to see the supported commands.");
      return;
    }
    try {
      const r = await fetch(`${AGENT}/command`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command })
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || "Controller rejected command");
      setStatus(`Sent local command: !${command}`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Local controller unavailable");
    }
  }

  async function submitCommand() {
    const raw = commandText.trim();
    if (!raw) return;
    const [first, ...rest] = raw.replace(/^!/, "").split(/\s+/);
    const command = first.toLowerCase();
    if (command === "help") {
      setStatus("Commands: !up !down !left !right !enter !play !pause !mute. !type is disabled.");
      setCommandText("");
      return;
    }
    if (command === "video") {
      setVideoUrl(rest.join(" "));
      setStatus("Video URL copied into the Open Video field. Press Open to launch it.");
      setCommandText("");
      return;
    }
    if (command === "type") {
      setStatus("!type is disabled: arbitrary text injection is not supported.");
      setCommandText("");
      return;
    }
    await send(command);
    setCommandText("");
  }

  async function openVideo() {
    try {
      const r = await fetch(`${AGENT}/video`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: videoUrl })
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || "Could not open video");
      setStatus("YouTube video opened in your browser.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Local controller unavailable");
    }
  }

  return <main className="shell">
    <header><div className="brand-mark">V</div><div><p className="eyebrow">ZOOM APP · REMOTE CONTROL</p><h1>VacuumTube <span>Remote</span></h1></div><div className="live-pill">{zoom.ready ? "ZOOM CONNECTED" : "PREVIEW MODE"}</div></header>
    <section className="hero">
      <p className="eyebrow">CONTROL CENTER</p><h2>Your meeting. Your media.</h2>
      <p className="muted">Open VacuumTube Remote from the Zoom Apps panel, then use its controls to operate your own VacuumTube installation.</p>
    </section>
    <div className="columns">
      <section className="panel">
        <div className="panel-heading"><div><p className="eyebrow">01 / LOCAL PLAYER</p><h3>VacuumTube connection</h3></div><span className={selected ? "dot good" : "dot"} /></div>
        <p className="muted">{agent}</p>
        <div className="actions"><button className="secondary" onClick={chooseExe}>Choose VacuumTube.exe</button><button onClick={launchExe} disabled={!selected}>Launch</button></div>
        <div className="divider" />
        <p className="eyebrow">MANUAL CONTROLS</p>
        <div className="dpad">
          <span /><button onClick={() => send("up")}>↑</button><span />
          <button onClick={() => send("left")}>←</button><button onClick={() => send("enter")}>↵</button><button onClick={() => send("right")}>→</button>
          <span /><button onClick={() => send("down")}>↓</button><span />
        </div>
        <div className="actions three"><button className="secondary" onClick={() => send("play")}>Play</button><button className="secondary" onClick={() => send("pause")}>Pause</button><button className="secondary" onClick={() => send("mute")}>Mute</button></div>
        <div className="divider" />
        <p className="eyebrow">OPEN A VIDEO</p>
        <div className="input-row"><input value={videoUrl} onChange={e => setVideoUrl(e.target.value)} placeholder="YouTube URL or video ID" /><button onClick={openVideo}>Open</button></div>
      </section>
      <section className="panel zoom-panel">
        <p className="eyebrow">02 / ZOOM APPS SDK</p><h3>In-meeting controller</h3>
        <p className="muted">{zoom.message}</p>
        <div className="zoom-context">
          <div><span>CONTEXT</span><strong>{zoom.runningContext}</strong></div>
          {zoom.meeting && <div><span>MEETING</span><strong>{zoom.meeting}</strong></div>}
          {zoom.user && <div><span>YOU</span><strong>{zoom.user}</strong></div>}
        </div>
        <div className="divider" />
        <p className="eyebrow">SEND A COMMAND</p>
        <p className="muted">Type a command here and press Send. This is an app input, not the Zoom meeting chat.</p>
        <div className="input-row"><input value={commandText} onChange={e => setCommandText(e.target.value)} onKeyDown={e => { if (e.key === "Enter") void submitCommand(); }} placeholder="!up, !left, !play, !help…" /><button onClick={() => void submitCommand()}>Send</button></div>
        <p className="status">{status}</p>
        <div className="notice"><strong>Zoom policy & privacy</strong><p>This is a user-operated Zoom App. It does not monitor, collect, or parse meeting chat, and it does not act on commands sent by other participants. Only commands you explicitly submit in this app control your local player. To build a chat-driven workflow, obtain Zoom's approval and use its designated RTMS route where authorized.</p></div>
      </section>
    </div>
    <footer>VACUUMTUBE REMOTE <span>EARLY DEVELOPMENT BUILD</span></footer>
  </main>;
}
