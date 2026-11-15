/** A sequence of events drawn as a track: prefix nodes, then the deviation terminal. */
export default function Pathway({ pattern, size = "md", animate = false }) {
  return (
    <ol className={`pathway ${size} ${animate ? "animate" : ""}`} aria-label={pattern.join(", then ")}>
      {pattern.map((ev, i) => {
        const last = i === pattern.length - 1;
        return (
          <li key={i} className={last ? "node terminal" : "node"} style={{ "--i": i }}>
            <span className="dot" aria-hidden="true" />
            <span className="label">{ev}</span>
          </li>
        );
      })}
    </ol>
  );
}
