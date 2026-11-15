import { useState } from "react";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { fmt, pct, useApi, useDebounced } from "../api.js";
import Pathway from "../components/Pathway.jsx";
import { ErrorBox, Loading } from "../components/States.jsx";

const SORTS = [
  ["support", "Support"],
  ["confidence", "Confidence"],
  ["lift", "Lift"],
  ["length", "Length"],
];

export default function Patterns({ minSupport }) {
  const [q, setQ] = useState("");
  const [sort, setSort] = useState("support");
  const [limit, setLimit] = useState(25);
  const dq = useDebounced(q);

  const pats = useApi("patterns", { min_support: minSupport, q: dq, sort, limit });
  const risk = useApi("risk-events", { min_support: minSupport, limit: 10 });
  const lens = useApi("length-distribution", { min_support: minSupport });

  if (pats.error) return <ErrorBox error={pats.error} />;
  const rows = pats.data?.patterns || [];
  const maxSupport = Math.max(1, ...rows.map((r) => r.support));

  return (
    <div className="view patterns-view">
      <div className="main-col">
        <h1 className="page-title">Deviation pathways</h1>
        <p className="lede">
          Sequences that end in a protocol deviation and occur in at least {fmt.format(minSupport)} patients.
          Confidence is how often the lead-up was followed by a deviation; lift compares that to the trial-wide rate.
        </p>

        <div className="toolbar">
          <label className="search">
            <span className="sr">Filter by event name</span>
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter by event, e.g. Missed Visit" />
          </label>
          <div className="seg" role="group" aria-label="Sort by">
            {SORTS.map(([k, label]) => (
              <button key={k} className={sort === k ? "on" : ""} aria-pressed={sort === k} onClick={() => setSort(k)}>
                {label}
              </button>
            ))}
          </div>
        </div>

        {!pats.data ? <Loading /> : (
          <>
            <div className="rows head" aria-hidden="true">
              <span>Pathway</span><span>Patients</span><span>Confidence</span><span>Lift</span>
            </div>
            <ul className={`rows ${pats.loading ? "stale" : ""}`}>
              {rows.map((r) => (
                <li key={r.pattern.join("|")} className="row">
                  <Pathway pattern={r.pattern} size="sm" />
                  <div className="cell support">
                    <span className="meter" style={{ "--w": `${(r.support / maxSupport) * 100}%` }} />
                    <span><b>{fmt.format(r.support)}</b><em>{r.support_pct}%</em></span>
                  </div>
                  <div className="cell" data-label="Confidence"><b>{pct(r.confidence)}</b></div>
                  <div className="cell" data-label="Lift"><b>{r.lift.toFixed(2)}×</b></div>
                </li>
              ))}
              {!rows.length && <li className="empty">No pathway matches "{dq}" at this support.</li>}
            </ul>
            {pats.data.total > rows.length && (
              <button className="more" onClick={() => setLimit(limit + 25)}>
                Show more ({pats.data.total - rows.length} left)
              </button>
            )}
          </>
        )}
      </div>

      <aside className="side-col">
        <h2>Strongest warning signals</h2>
        <p className="sub">Events that appear most often in the lead-up to a deviation.</p>
        <div className="chart">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={risk.data || []} layout="vertical" margin={{ left: 0, right: 12 }}>
              <XAxis type="number" hide />
              <YAxis type="category" dataKey="event" width={140} tick={{ fontSize: 12, fill: "var(--ink)" }} axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: "rgba(14,110,110,.08)" }} formatter={(v) => [fmt.format(v), "Risk score"]} />
              <Bar dataKey="score" fill="var(--teal)" radius={[0, 2, 2, 0]} barSize={14} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <h2>How long are they?</h2>
        <p className="sub">Number of pathways by length, deviation included.</p>
        <div className="chart">
          <ResponsiveContainer width="100%" height={150}>
            <BarChart data={lens.data || []} margin={{ left: -24, right: 4 }}>
              <XAxis dataKey="length" tick={{ fontSize: 11, fill: "var(--muted)" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "var(--muted)" }} axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: "rgba(14,110,110,.08)" }} formatter={(v) => [v, "Pathways"]} labelFormatter={(l) => `${l} events`} />
              <Bar dataKey="patterns" fill="var(--deviation)" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </aside>
    </div>
  );
}
