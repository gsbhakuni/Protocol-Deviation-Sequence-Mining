import { useEffect, useState } from "react";

const BASE = import.meta.env.VITE_API_URL || "";

export async function get(path, params = {}) {
  const qs = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== "" && v != null)
  ).toString();
  const res = await fetch(`${BASE}/api/${path}${qs ? `?${qs}` : ""}`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

/** Fetch on mount and whenever path/params change. Keeps previous data while reloading. */
export function useApi(path, params = {}) {
  const [state, setState] = useState({ data: null, loading: true, error: null });
  const key = path + JSON.stringify(params);
  useEffect(() => {
    if (!path) return;          // pass null to skip the request
    let live = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    get(path, params)
      .then((data) => live && setState({ data, loading: false, error: null }))
      .catch((error) => live && setState((s) => ({ ...s, loading: false, error })));
    return () => { live = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);
  return state;
}

export function useDebounced(value, ms = 250) {
  const [v, setV] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setV(value), ms);
    return () => clearTimeout(t);
  }, [value, ms]);
  return v;
}

export const fmt = new Intl.NumberFormat("en-US");
export const pct = (x, d = 0) => `${(x * 100).toFixed(d)}%`;
