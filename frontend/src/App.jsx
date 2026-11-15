import { useState } from "react";
import { useDebounced } from "./api.js";
import Overview from "./views/Overview.jsx";
import Patterns from "./views/Patterns.jsx";
import Patients from "./views/Patients.jsx";

const TABS = [
  ["overview", "Overview"],
  ["patterns", "Pathways"],
  ["patients", "Patient journeys"],
];

export default function App() {
  const [tab, setTab] = useState("overview");
  const [support, setSupport] = useState(100);
  const minSupport = useDebounced(support, 300);

  return (
    <>
      <header className="top">
        <div className="brand">
          <svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true">
            <path d="M3 22 L10 22 L14 10 L19 19 L22 19" fill="none" stroke="var(--teal)" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="25" cy="19" r="3.4" fill="var(--deviation)" />
          </svg>
          <div><strong>Protocol Deviation Mining</strong><span>Sequential patterns before a trial goes off protocol</span></div>
        </div>
        <nav aria-label="Views">
          {TABS.map(([k, l]) => (
            <button key={k} className={tab === k ? "on" : ""} aria-current={tab === k ? "page" : undefined} onClick={() => setTab(k)}>{l}</button>
          ))}
        </nav>
        {tab !== "patients" && (
          <label className="support">
            <span>Minimum support <b>{support}</b> patients</span>
            <input type="range" min="50" max="3000" step="10" value={support} onChange={(e) => setSupport(+e.target.value)} />
          </label>
        )}
      </header>
      <main>
        {tab === "overview" && <Overview minSupport={minSupport} />}
        {tab === "patterns" && <Patterns minSupport={minSupport} />}
        {tab === "patients" && <Patients />}
      </main>
    </>
  );
}
