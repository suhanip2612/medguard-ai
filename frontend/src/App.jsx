import { useEffect, useRef, useState } from "react";
import { api } from "./api";

function PatientCard({ p }) {
  return (
    <div className="card">
      <h2>{p.name}</h2>
      <p className="muted">{p.age} yrs · {p.weight_kg} kg · card {p.card_uid}</p>
      <h4>Conditions</h4>
      <div className="chips">
        {p.conditions.length ? p.conditions.map((c) => <span key={c} className="chip">{c.replace(/_/g, " ")}</span>) : <span className="muted">none</span>}
      </div>
      <h4>Allergies</h4>
      <div className="chips">
        {p.allergies.length ? p.allergies.map((a) => <span key={a} className="chip red">{a}</span>) : <span className="muted">none recorded</span>}
      </div>
      <h4>Current medicines</h4>
      <div className="chips">
        {p.current_meds.length ? p.current_meds.map((m, i) => (
          <span key={i} className="chip blue">
            {m.brand ? `${m.brand} (${m.generic})` : m.generic}
            {m.dose_mg ? ` ${m.dose_mg}mg` : ""}{m.times_per_day ? ` ×${m.times_per_day}/day` : ""}
          </span>
        )) : <span className="muted">none</span>}
      </div>
    </div>
  );
}

function AlertCard({ a }) {
  const [open, setOpen] = useState(false);
  return (
    <div className={`alert ${a.severity}`}>
      <div className="alert-head">
        <span className="badge">{a.severity.toUpperCase()}</span>
        <strong>{a.title}</strong>
      </div>
      <p className="explain">{a.explanation}</p>
      {a.alternative && <p className="alt"><b>Safer option to consider:</b> {a.alternative}</p>}
      <button className="link" onClick={() => setOpen(!open)}>{open ? "Hide details" : "Why? Show details"}</button>
      {open && (
        <div className="details">
          <p><b>Mechanism:</b> {a.mechanism}</p>
          <p><b>Recommended action:</b> {a.recommendation}</p>
          <p><b>Source:</b> {a.source}</p>
          <p className="muted">Explanation written by: {a.explanation_source === "llm" ? "AI (wording only)" : "fixed template"}. Detection by fixed rules.</p>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [patient, setPatient] = useState(null);
  const [patients, setPatients] = useState([]);
  const [drugNames, setDrugNames] = useState([]);
  const [drug, setDrug] = useState("");
  const [dose, setDose] = useState("");
  const [perDay, setPerDay] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [reason, setReason] = useState("");
  const [saved, setSaved] = useState("");
  const lastSeq = useRef(0);

  useEffect(() => {
    api.patients().then(setPatients).catch(() => setError("Cannot reach backend. Is it running on port 8000?"));
    api.drugs().then(setDrugNames).catch(() => {});
  }, []);

  // Poll the backend for RFID taps every 500 ms
  useEffect(() => {
    const t = setInterval(async () => {
      try {
        const s = await api.lastTap();
        if (s.seq !== lastSeq.current) {
          lastSeq.current = s.seq;
          if (s.uid) loadPatient(s.uid);
        }
      } catch {}
    }, 500);
    return () => clearInterval(t);
  }, []);

  async function loadPatient(uid) {
    setError(""); setResult(null); setSaved(""); setDrug(""); setDose(""); setPerDay(""); setReason("");
    try { setPatient(await api.patient(uid)); }
    catch (e) { setPatient(null); setError(e.message); }
  }

  async function runCheck() {
    if (!patient || !drug.trim()) return;
    setLoading(true); setError(""); setSaved(""); setResult(null);
    try {
      setResult(await api.check({
        uid: patient.card_uid, drug,
        dose_mg: dose ? Number(dose) : null,
        times_per_day: perDay ? Number(perDay) : null,
      }));
    } catch (e) { setError(e.message); }
    setLoading(false);
  }

  async function decide(action) {
    if (action === "override" && !reason.trim()) { setError("Please enter a reason to override."); return; }
    setError("");
    await api.decision({ uid: patient.card_uid, drug, action, reason, alerts: result?.alerts || [] });
    setSaved(`Decision recorded: ${action}`);
  }

  const hasAlerts = result && !result.unknown && result.alerts.length > 0;

  return (
    <div className="app">
      <header>
        <h1>🛡️ MedGuard AI</h1>
        <p className="muted">Decision support only. The doctor always makes the final call. Demo uses synthetic patients.</p>
      </header>

      <div className="tapbar">
        {patient ? <span>✅ Card loaded: <b>{patient.name}</b></span> : <span>📡 Waiting for RFID tap…</span>}
        <span className="sim">
          Simulate tap:{" "}
          <select value="" onChange={(e) => e.target.value && loadPatient(e.target.value)}>
            <option value="">choose patient…</option>
            {patients.map((p) => <option key={p.uid} value={p.uid}>{p.name}</option>)}
          </select>
        </span>
      </div>

      {error && <div className="error">{error}</div>}

      {patient && (
        <div className="grid">
          <PatientCard p={patient} />
          <div className="card">
            <h2>Prescribe a new medicine</h2>
            <label>Drug or brand name</label>
            <input list="drugs" value={drug} onChange={(e) => setDrug(e.target.value)} placeholder="e.g. Crocin" />
            <datalist id="drugs">{drugNames.map((n) => <option key={n} value={n} />)}</datalist>
            <div className="row">
              <div><label>Dose (mg)</label><input type="number" value={dose} onChange={(e) => setDose(e.target.value)} /></div>
              <div><label>Times per day</label><input type="number" value={perDay} onChange={(e) => setPerDay(e.target.value)} /></div>
            </div>
            <button className="primary" onClick={runCheck} disabled={loading || !drug.trim()}>
              {loading ? "Checking…" : "Check safety"}
            </button>

            {result?.unknown && <div className="error">Unknown drug “{result.input}”. Try another spelling.</div>}
            {result && !result.unknown && (
              <p className="muted">
                Checked as <b>{result.resolved_generic}</b>
                {result.matched_via === "fuzzy" && " (closest match – please confirm)"}
              </p>
            )}
            {result && !result.unknown && !hasAlerts && <div className="ok">✅ No issues found by the rule checks.</div>}
            {hasAlerts && result.alerts.map((a) => <AlertCard key={a.id} a={a} />)}

            {result && !result.unknown && (
              <div className="decision">
                <input placeholder="Reason (required to override)" value={reason} onChange={(e) => setReason(e.target.value)} />
                <button onClick={() => decide("accept")}>Accept &amp; prescribe</button>
                <button className="warn" onClick={() => decide("override")}>Override alerts</button>
                <button onClick={() => decide("change")}>Change drug</button>
                {saved && <p className="ok">{saved}</p>}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
