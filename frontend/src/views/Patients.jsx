import { useEffect, useState } from "react";
import { useApi, useDebounced } from "../api.js";
import { ErrorBox, Loading } from "../components/States.jsx";

export default function Patients() {
  const [q, setQ] = useState("");
  const [filter, setFilter] = useState("yes");
  const [selected, setSelected] = useState(null);
  const dq = useDebounced(q);

  const list = useApi("patients", { q: dq, deviation: filter, limit: 80 });
  const detail = useApi(selected ? `patients/${selected}` : null);

  // auto-select the first patient in the list so the journey panel is never empty
  useEffect(() => {
    if (!selected && list.data?.patients.length) setSelected(list.data.patients[0].id);
  }, [list.data, selected]);

  if (list.error && !list.data) return <ErrorBox error={list.error} />;
  const p = selected && detail.data?.id === selected ? detail.data : null;

  return (
    <div className="view journeys">
      <div className="picker">
        <h1 className="page-title">Patient journeys</h1>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Find a patient, e.g. P00002" aria-label="Find a patient" />
        <div className="seg" role="group" aria-label="Deviation filter">
          {[["yes", "Deviated"], ["no", "Clean"], ["all", "All"]].map(([k, l]) => (
            <button key={k} className={filter === k ? "on" : ""} aria-pressed={filter === k} onClick={() => setFilter(k)}>{l}</button>
          ))}
        </div>
        <p className="sub">{list.data ? `${list.data.total.toLocaleString()} patients` : "Loading…"}</p>
        <ul className="plist">
          {list.data?.patients.map((x) => (
            <li key={x.id}>
              <button className={selected === x.id ? "on" : ""} onClick={() => setSelected(x.id)}>
                <i className={x.deviation ? "flag" : "flag ok"} aria-label={x.deviation ? "Deviation" : "No deviation"} />
                <b>{x.id}</b>
                <span>Site {x.site}</span>
                <em>{x.events} events</em>
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="journey">
        {!p ? <Loading label="Loading journey" /> : (
          <>
            <header>
              <h2>{p.id}</h2>
              <span className="tag">Site {p.site}</span>
              {p.deviation
                ? <span className={`tag sev ${p.severity?.toLowerCase()}`}>{p.severity} deviation</span>
                : <span className="tag clean">No deviation</span>}
              <span className="tag">{p.events.length} events over {p.events[p.events.length - 1].day} days</span>
            </header>
            <ol className="timeline">
              {p.events.map((e, i) => (
                <li key={i} className={e.is_deviation ? "ev dev" : "ev"}>
                  <time>day {e.day}</time>
                  <span className="mark" aria-hidden="true" />
                  <div><b>{e.event}</b><small>{e.date}</small></div>
                </li>
              ))}
            </ol>
          </>
        )}
      </div>
    </div>
  );
}
