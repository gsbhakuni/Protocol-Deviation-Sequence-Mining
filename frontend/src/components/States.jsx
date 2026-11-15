export function Loading({ label = "Mining sequences" }) {
  return <div className="state" role="status"><span className="pulse" />{label}…</div>;
}

export function ErrorBox({ error }) {
  return (
    <div className="state error" role="alert">
      <strong>Can't reach the API.</strong> Start it from the project root with{" "}
      <code>uvicorn api.main:app --reload --port 8000</code>.
      <small>{String(error?.message || error)}</small>
    </div>
  );
}
