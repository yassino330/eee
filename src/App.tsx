import { useEffect, useRef, useState } from "react";
import ZoomMtgEmbedded from "@zoom/meetingsdk/embedded";

const AGENT = "http://127.0.0.1:8765";

export default function App() {
  const zoomRoot = useRef<HTMLDivElement>(null);
  const [agent, setAgent] = useState("Checking local controller…");
  const [selected, setSelected] = useState(false);
  const [meetingNumber, setMeetingNumber] = useState("");
  const [passcode, setPasscode] = useState("");
  const [displayName, setDisplayName] = useState("VacuumTube Remote");
  const [status, setStatus] = useState("Not connected");
  const [videoUrl, setVideoUrl] = useState("");

  useEffect(() => {
    fetch(`${AGENT}/settings`)
      .then(r => r.json())
      .then(d => { setSelected(Boolean(d.selected)); setAgent(d.selected ? `Selected: ${d.filename}` : "No executable selected"); })
      .catch(() => setAgent("Local controller not running"));
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
    const r = await fetch(`${AGENT}/launch`, { method: "POST" });
    const d = await r.json();
    setAgent(d.launched ? "VacuumTube launched" : (d.detail || "Launch failed"));
  }

  async function send(command: string) {
    await fetch(`${AGENT}/command`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command })
    });
  }

  async function openVideo() {
    const r = await fetch(`${AGENT}/video`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: videoUrl })
    });
    const d = await r.json();
    setStatus(d.opened ? "YouTube video opened" : (d.detail || "Could not open video"));
  }

  async function joinMeeting() {
    setStatus("Meeting SDK joining is not configured yet. Add a server-generated signature and SDK key first.");
    // The Zoom Meeting SDK must be initialized with a short-lived signature generated
    // by a trusted backend. Do not put the SDK secret in this browser app.
  }

  return <main className="shell">
    <header><div className="brand-mark">V</div><div><p className="eyebrow">REMOTE CONTROL</p><h1>VacuumTube <span>Remote</span></h1></div><div className="live-pill">LOCAL APP</div></header>
    <section className="hero">
      <p className="eyebrow">CONTROL CENTER</p><h2>Your meeting. Your media.</h2>
      <p className="muted">A companion interface for a manually selected VacuumTube installation.</p>
    </section>
    <div className="columns">
      <section className="panel">
        <div className="panel-heading"><div><p className="eyebrow">01 / LOCAL PLAYER</p><h3>VacuumTube connection</h3></div><span className={selected ? "dot good" : "dot"} /></div>
        <p className="muted">{agent}</p>
        <div className="actions"><button className="secondary" onClick={chooseExe}>Choose VacuumTube.exe</button><button onClick={launchExe} disabled={!selected}>Launch</button></div>
        <div className="divider" />
        <p className="eyebrow">QUICK CONTROLS</p>
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
        <p className="eyebrow">02 / ZOOM MEETING SDK</p><h3>Meeting connection</h3>
        <p className="muted">This embeds a Zoom meeting in this app. It does not connect to a meeting already open in the Zoom desktop client.</p>
        <label>Meeting ID<input value={meetingNumber} onChange={e => setMeetingNumber(e.target.value)} placeholder="Meeting number" /></label>
        <label>Passcode<input value={passcode} onChange={e => setPasscode(e.target.value)} placeholder="Meeting passcode" type="password" /></label>
        <label>Display name<input value={displayName} onChange={e => setDisplayName(e.target.value)} /></label>
        <button className="wide" onClick={joinMeeting} disabled={!meetingNumber || !displayName}>Connect to meeting</button>
        <p className="status">{status}</p>
        <div ref={zoomRoot} id="zoom-root" />
        <div className="notice"><strong>Zoom policy note</strong><p>The SDK is intended for human meeting experiences. This starter does not silently read chat or run as an unattended bot. Confirm Zoom permits your exact chat-command workflow before adding it.</p></div>
      </section>
    </div>
    <footer>VACUUMTUBE REMOTE <span>EARLY DEVELOPMENT BUILD</span></footer>
  </main>;
}