"""Builds data/live_trading.csv for the Live trading tab from the desk's bet history.

Usage:  python build_live.py path\to\bet_history.csv
The input is the CSV the desk's History page downloads. Stakes and P&L are dropped, only prices and
CLV are kept. Rows are kept when the bet exited on or after START, or is still open.
"""
import sys

import pandas as pd

START = pd.Timestamp("2026-10-19", tz="UTC")
COLS = ["placed", "match", "league", "venue", "outcome", "conv", "mode", "stake", "entry", "status",
        "exit_target", "exit_time", "close", "clv", "result", "pnl", "settled"]


def build(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d.columns = COLS
    d["exit_dt"] = pd.to_datetime(d["exit_time"], utc=True, errors="coerce")
    d["settled_dt"] = pd.to_datetime(d["settled"], utc=True, errors="coerce")
    d["clv_pct"] = pd.to_numeric(d["clv"].astype(str).str.extract(r"([+-]?\d+\.?\d*)%")[0], errors="coerce")
    st_ = d["status"].astype(str)
    kind = pd.Series("", index=d.index)
    kind[st_.str.startswith("EXITED") & ~st_.str.contains("in-play")] = "prekick"
    kind[st_.str.contains("in-play")] = "inplay"
    kind[st_.str.startswith("SETTLED") & d["exit_dt"].isna()] = "held"
    kind[st_.str.startswith("PLACED")] = "open"
    d["kind"] = kind
    keep = (d["kind"] == "open") | (
        d["kind"].isin(["prekick", "inplay"]) & (d["exit_dt"] >= START)) | (
        (d["kind"] == "held") & (d["settled_dt"] >= START))
    out = d[keep & (d["kind"] != "")].copy()
    out["exit"] = out["exit_target"]
    return out[["kind", "match", "league", "venue", "outcome", "entry", "exit", "exit_time", "clv_pct", "placed"]]


if __name__ == "__main__":
    src = sys.argv[1]
    raw = pd.read_csv(src, dtype=str, header=0).fillna("")
    res = build(raw)
    res.to_csv("data/live_trading.csv", index=False)
    print(len(res), "rows written;", (res["kind"] != "open").sum(), "exited or settled since", START.date(),
          ";", (res["kind"] == "open").sum(), "open")
