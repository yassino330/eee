import { useEffect, useRef, useState } from "react";
import ZoomMtgEmbedded from "@zoom/meetingsdk/embedded";

const AGENT = "http://127.0.0.1:8765";

export default function App() {
  const zoomRoot = useRef<HTMLDivElement>(null);
  const zoomClient = useRef<ReturnType<typeof ZoomMtgEmbedded.createClient> | null>(null);
  const [agent, setAgent] = useState("Checking local controller…");
  const [selected, setSelected] = useState(false);
  const [meetingNumber, setMeetingNumber] = useState("");
  const [passcode, setPasscode] = useState("");
  const [displayName, setDisplayName] = useState("VacuumTube Remote");
  const [status, setStatus] = useState("Not connected");
  const [videoUrl, setVideoUrl] = useState("");
  const [joining, setJoining] = useState(false);

  useEffect(() => {
    fetch(`${AGENT}/settings`)
      .then(r => r.json())
      .then(d => {
        setSelected(Boolean(d.selected));
        setAgent(d.selected ? `Selected: ${d.filename}` : "No executable selected");
      })
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
    try {
      const r = await fetch(`${AGENT}/launch`, { method: "POST" });
      const d = await r.json();
      setAgent(d.launched ? "VacuumTube launched" : (d.detail || "Launch failed"));
    } catch { setAgent("Could not reach local controller"); }
  }

  async function send(command: string) {
    try {
      const r = await fetch(`${AGENT}/command`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command })
      });
      if (!r.ok) throw new Error("Controller rejected command");
      setStatus(`Sent local command: ${command}`);
    } catch { setStatus("Local controller unavailable"); }
  }

  async function openVideo() {
    try {
      const r = await fetch(`${AGENT}/video`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: videoUrl })
      });
      const d = await r.json();
      setStatus(d.opened ? "YouTube video opened in your browser" : (d.detail || "Could not open video"));
    } catch { setStatus("Local controller unavailable"); }
  }

  async function joinMeeting() {
    if (!zoomRoot.current || joining) return;
    setJoining(true);
    setStatus("Preparing Zoom meeting…");
    try {
      const signatureResponse = await fetch(`${AGENT}/zoom/signature`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ meeting_number: meetingNumber.replace(/\s/g, "") })
      });
      const signatureData = await signatureResponse.json();
      if (!signatureResponse.ok) throw new Error(signatureData.detail || "Could not create Zoom signature");

      const client = ZoomMtgEmbedded.createClient();
      zoomClient.current = client;
      await client.init({
        zoomAppRoot: zoomRoot.current,
        language: "en-US",
        patchJsMedia: true,
        leaveOnPageUnload: true
      });
      await client.join({
        sdkKey: signatureData.sdkKey,
        signature: signatureData.signature,
        meetingNumber: meetingNumber.replace(/\s/g, ""),
        password: passcode,
        userName: displayName.trim()
      });
      setStatus("Joined the Zoom meeting. You are visible to meeting participants.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Could not join Zoom meeting");
      zoomClient.current = null;
    } finally {
      setJoining(false);
    }
  }

  async function leaveMeeting() {
    if (!zoomClient.current) return;
    try {
      await zoomClient.current.leave();
      setStatus("You left the Zoom meeting.");
    } catch {
      setStatus("Could not leave cleanly. Close this page if the meeting SDK is stuck.");
    } finally {
      zoomClient.current = null;
    }
  }

  return <main className="shell">
    <header><div className="brand-mark">V</div><div><p className="eyebrow">REMOTE CONTROL</p><h1>VacuumTube <span>Remote</span></h1></div><div className="live-pill">LOCAL APP</div></header>
    <section className="hero">
      <p className="eyebrow">CONTROL CENTER</p><h2>Your meeting. Your media.</h2>
      <p className="muted">Join a Zoom meeting visibly and control a manually selected VacuumTube installation from this page.</p>
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
        <p className="eyebrow">02 / ZOOM MEETING SDK</p><h3>Join the actual meeting</h3>
        <p className="muted">This joins the meeting as a separate, visible participant in this app. It cannot attach to a meeting already open in the Zoom desktop client.</p>
        <label>Meeting ID<input value={meetingNumber} onChange={e => setMeetingNumber(e.target.value)} placeholder="Meeting number" inputMode="numeric" /></label>
        <label>Passcode<input value={passcode} onChange={e => setPasscode(e.target.value)} placeholder="Meeting passcode" type="password" /></label>
        <label>Display name<input value={displayName} onChange={e => setDisplayName(e.target.value)} /></label>
        <div className="actions"><button className="wide" onClick={joinMeeting} disabled={!meetingNumber || !displayName.trim() || joining}>{joining ? "Joining…" : "Join meeting"}</button><button className="secondary" onClick={leaveMeeting}>Leave</button></div>
        <p className="status">{status}</p>
        <div ref={zoomRoot} id="zoom-root" />
        <div className="notice"><strong>Chat automation is not enabled</strong><p>The Meeting SDK policy says it is for human use and does not support bots. This build provides a visible, user-operated meeting session and manual controls; it does not automatically read meeting chat or execute commands from other participants. Confirm Zoom's approval before adding that workflow.</p></div>
      </section>
    </div>
    <footer>VACUUMTUBE REMOTE <span>EARLY DEVELOPMENT BUILD</span></footer>
  </main>;
}
