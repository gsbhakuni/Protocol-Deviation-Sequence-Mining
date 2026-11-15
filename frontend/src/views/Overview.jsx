import { Bar, BarChart, CartesianGrid, Cell, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { fmt, pct, useApi } from "../api.js";
import Pathway from "../components/Pathway.jsx";
import { ErrorBox, Loading } from "../components/States.jsx";

const SEV_COLOR = { Minor: "var(--minor)", Major: "var(--major)", Critical: "var(--critical)" };

export default function Overview({ minSupport }) {
  const sum = useApi("summary", { min_support: minSupport });
  const pats = useApi("patterns", { min_support: minSupport, limit: 5 });

  if (sum.error) return <ErrorBox error={sum.error} />;
  if (!sum.data) return <Loading />;
  const { kpis, severity, sites } = sum.data;
  const top = sum.data.top_pattern;
  const sevTotal = severity.reduce((a, s) => a + s.patients, 0) || 1;
  const bySite = [...sites].sort((a, b) => b.rate - a.rate);

  return (
    <div className="view">
      <section className="hero">
        <h1>
          {top
            ? <>{top.prefix[top.prefix.length - 1]} showed up before {fmt.format(top.support)} protocol deviations.</>
            : "No deviation pathways at this support threshold."}
        </h1>
        <p className="lede">
          {fmt.format(kpis.deviation_patients)} of {fmt.format(kpis.patients)} patients ({pct(kpis.deviation_rate)})
          had a deviation. These are the event sequences that most often came right before one.
        </p>

        <div className="pathways">
          {pats.data?.patterns.map((p) => (
            <div className="pathway-row" key={p.pattern.join("|")}>
              <Pathway pattern={p.pattern} animate />
              <div className="pathway-meta">
                <span className="meter" style={{ "--w": `${Math.min(100, p.support_pct * 2)}%` }} />
                <b>{fmt.format(p.support)}</b> patients
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="strip" aria-label="Key figures">
        <Fig n={fmt.format(kpis.patients)} t="patients" />
        <Fig n={fmt.format(kpis.events)} t="recorded events" />
        <Fig n={kpis.sites} t="sites" />
        <Fig n={fmt.format(kpis.patterns)} t="deviation pathways found" />
      </section>

      <section className="split">
        <div>
          <h2>How severe were they?</h2>
          <p className="sub">Patients with a deviation, by severity of the flag on their record.</p>
          <div className="stack" role="img" aria-label="Severity distribution">
            {severity.map((s) => (
              <div key={s.severity} style={{ flexGrow: s.patients, background: SEV_COLOR[s.severity] }} />
            ))}
          </div>
          <ul className="legend">
            {severity.map((s) => (
              <li key={s.severity}>
                <i style={{ background: SEV_COLOR[s.severity] }} />
                <span>{s.severity}</span>
                <b>{fmt.format(s.patients)}</b>
                <em>{pct(s.patients / sevTotal)}</em>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h2>Which sites run hot?</h2>
          <p className="sub">
            Share of each site's patients with a deviation. The dashed line is the trial-wide rate ({pct(kpis.deviation_rate, 1)}).
          </p>
          <div className="chart">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={bySite} margin={{ top: 8, right: 4, left: -18, bottom: 0 }}>
                <CartesianGrid vertical={false} stroke="var(--rule)" />
                <XAxis dataKey="site" tick={{ fontSize: 10, fill: "var(--muted)" }} interval={0} angle={-60} textAnchor="end" height={42} tickLine={false} />
                <YAxis tickFormatter={(v) => pct(v)} tick={{ fontSize: 11, fill: "var(--muted)" }} axisLine={false} tickLine={false} domain={[0, "dataMax"]} />
                <Tooltip
                  cursor={{ fill: "rgba(14,110,110,.08)" }}
                  content={({ active, payload }) => active && payload?.length ? (
                    <div className="tip">
                      <b>Site {payload[0].payload.site}</b>
                      {payload[0].payload.deviations} of {payload[0].payload.patients} patients ({pct(payload[0].payload.rate, 1)})
                    </div>
                  ) : null}
                />
                <ReferenceLine y={kpis.deviation_rate} stroke="var(--ink)" strokeDasharray="4 4" />
                <Bar dataKey="rate" radius={[2, 2, 0, 0]}>
                  {bySite.map((s) => (
                    <Cell key={s.site} fill={s.rate > kpis.deviation_rate ? "var(--deviation)" : "var(--teal)"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>
    </div>
  );
}

const Fig = ({ n, t }) => (
  <div className="fig"><b>{n}</b><span>{t}</span></div>
);
