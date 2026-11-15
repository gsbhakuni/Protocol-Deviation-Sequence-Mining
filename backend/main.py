"""
FastAPI layer over the existing mining code in src/.
Run from the project root:   uvicorn api.main:app --reload --port 8000
"""
import sys
from functools import lru_cache
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from src.data_preprocessing import load_and_clean_data
from src.sequence_builder import build_sequences
from src.prefixspan_mining import mine_patterns
from src.pattern_analysis import get_deviation_patterns, add_support_percentage, sort_patterns

DEVIATION = "Protocol Deviation"

app = FastAPI(title="Protocol Deviation Mining API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- load once at start-up -------------------------------------------------
df = load_and_clean_data(str(ROOT / "data" / "dataset.csv"))
sequences = build_sequences(df)
N_PATIENTS = len(sequences)
patient_flags = df.groupby("patient_id")["deviation_flag"].max()
N_DEV_PATIENTS = int(patient_flags.sum())
BASE_RATE = N_DEV_PATIENTS / N_PATIENTS


def _contains(seq, sub):
    """True if `sub` occurs in `seq` as an ordered subsequence."""
    it = iter(seq)
    return all(any(x == s for x in it) for s in sub)


@lru_cache(maxsize=64)
def _mined(min_support: int):
    """Deviation patterns (len >= 2) with support, confidence and lift."""
    raw = mine_patterns(sequences, min_support=min_support)
    dev = sort_patterns(get_deviation_patterns(raw))
    dev = [(s, p) for s, p in dev if len(p) > 1]      # drop the trivial ['Protocol Deviation']
    rows = []
    for support, pct, pattern in add_support_percentage(dev, N_PATIENTS):
        prefix = pattern[:-1]
        prefix_support = sum(1 for s in sequences if _contains(s, prefix))
        confidence = support / prefix_support if prefix_support else 0
        rows.append({
            "pattern": pattern,
            "prefix": prefix,
            "support": support,
            "support_pct": pct,
            "confidence": round(confidence, 4),
            "lift": round(confidence / BASE_RATE, 3) if BASE_RATE else 0,
            "length": len(pattern),
        })
    return rows


# ---- endpoints -------------------------------------------------------------
@app.get("/api/summary")
def summary(min_support: int = Query(100, ge=10, le=3000)):
    rows = _mined(min_support)
    dev = df[df["deviation_flag"] == 1]
    sev = (
        dev.drop_duplicates("patient_id")["deviation_severity"].value_counts()
        .reindex(["Minor", "Major", "Critical"], fill_value=0)
    )
    per_site = df.groupby("site_id")["patient_id"].nunique()
    dev_site = dev.groupby("site_id")["patient_id"].nunique().reindex(per_site.index, fill_value=0)
    sites = [
        {"site": s, "patients": int(per_site[s]), "deviations": int(dev_site[s]),
         "rate": round(dev_site[s] / per_site[s], 4)}
        for s in per_site.index
    ]
    sites.sort(key=lambda x: x["deviations"], reverse=True)
    return {
        "kpis": {
            "patients": N_PATIENTS,
            "events": len(df),
            "deviation_patients": N_DEV_PATIENTS,
            "deviation_rate": round(BASE_RATE, 4),
            "patterns": len(rows),
            "sites": int(per_site.shape[0]),
        },
        "severity": [{"severity": k, "patients": int(v)} for k, v in sev.items()],
        "sites": sites,
        "top_pattern": rows[0] if rows else None,
        "min_support": min_support,
    }


@app.get("/api/patterns")
def patterns(
    min_support: int = Query(100, ge=10, le=3000),
    q: str = "",
    sort: str = Query("support", pattern="^(support|confidence|lift|length)$"),
    limit: int = Query(50, ge=1, le=500),
):
    rows = _mined(min_support)
    if q:
        rows = [r for r in rows if q.lower() in " → ".join(r["pattern"]).lower()]
    rows = sorted(rows, key=lambda r: r[sort], reverse=True)
    return {"total": len(rows), "patterns": rows[:limit]}


@app.get("/api/risk-events")
def risk_events(min_support: int = Query(100, ge=10, le=3000), limit: int = 12):
    """Same scoring as the Streamlit app: sum of support over patterns an event appears in."""
    score = {}
    for r in _mined(min_support):
        for ev in r["prefix"]:
            score[ev] = score.get(ev, 0) + r["support"]
    top = sorted(score.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    return [{"event": e, "score": s} for e, s in top]


@app.get("/api/length-distribution")
def length_distribution(min_support: int = Query(100, ge=10, le=3000)):
    counts = pd.Series([r["length"] for r in _mined(min_support)]).value_counts().sort_index()
    return [{"length": int(k), "patterns": int(v)} for k, v in counts.items()]


@app.get("/api/patients")
def patients(q: str = "", deviation: str = Query("all", pattern="^(all|yes|no)$"), limit: int = 60):
    g = df.groupby("patient_id").agg(
        site=("site_id", "first"), events=("event", "size"), deviation=("deviation_flag", "max")
    ).reset_index()
    if q:
        g = g[g["patient_id"].str.contains(q, case=False)]
    if deviation != "all":
        g = g[g["deviation"] == (1 if deviation == "yes" else 0)]
    return {
        "total": len(g),
        "patients": [
            {"id": r.patient_id, "site": r.site, "events": int(r.events), "deviation": bool(r.deviation)}
            for r in g.head(limit).itertuples()
        ],
    }


@app.get("/api/patients/{patient_id}")
def patient(patient_id: str):
    p = df[df["patient_id"] == patient_id].sort_values("timestamp").copy()
    if p.empty:
        raise HTTPException(404, "Unknown patient")
    p["timestamp"] = pd.to_datetime(p["timestamp"])
    start = p["timestamp"].iloc[0]
    sev = p[p["deviation_flag"] == 1]["deviation_severity"]
    return {
        "id": patient_id,
        "site": p["site_id"].iloc[0],
        "deviation": bool(p["deviation_flag"].max()),
        "severity": sev.iloc[0] if len(sev) else None,
        "events": [
            {"event": r.event, "date": r.timestamp.strftime("%Y-%m-%d"),
             "day": int((r.timestamp - start).days), "is_deviation": r.event == DEVIATION}
            for r in p.itertuples()
        ],
    }
