"""
pick_log.py
Tracks whether QARP picks actually performed. Appends every pick to
picks_log.csv (committed back to the repo by the workflow — see the
"Commit picks log" step added to each qarp-*.yml), and on each run also
checks older entries to see if they've crossed the 30-day or 90-day mark,
fetching current price and recording the % change.

This is what eventually lets you show subscribers a real track record
instead of just "trust the methodology."
"""

import os
import csv
import logging
from datetime import datetime, date
from dataclasses import dataclass

import yfinance as yf

log = logging.getLogger("pick_log")

LOG_PATH = os.environ.get("PICKS_LOG_PATH", "picks_log.csv")
FIELDNAMES = [
    "pick_date", "market", "ticker", "name", "sector", "composite_score",
    "price_at_pick", "currency",
    "price_30d", "pct_change_30d", "price_90d", "pct_change_90d",
    "updated_at",
]
HORIZONS = [(30, "price_30d", "pct_change_30d"), (90, "price_90d", "pct_change_90d")]


def _ensure_file():
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=FIELDNAMES).writeheader()


def _read_all() -> list[dict]:
    _ensure_file()
    with open(LOG_PATH, newline="") as f:
        return list(csv.DictReader(f))


def _write_all(rows: list[dict]):
    with open(LOG_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def log_picks(market_key: str, scan_date: str, picks: list, pick_date_iso: str | None = None):
    """picks: list of RankedStock (from rank_and_select.py), each with .metrics
    containing 'price' and 'currency' (added in qarp_screen.py)."""
    _ensure_file()
    pick_date_iso = pick_date_iso or date.today().isoformat()
    rows = _read_all()

    for stock in picks:
        m = stock.metrics
        rows.append({
            "pick_date": pick_date_iso,
            "market": market_key,
            "ticker": stock.ticker,
            "name": m.get("name", ""),
            "sector": m.get("sector", ""),
            "composite_score": f"{stock.composite_score:.4f}",
            "price_at_pick": m.get("price", ""),
            "currency": m.get("currency", ""),
            "price_30d": "", "pct_change_30d": "",
            "price_90d": "", "pct_change_90d": "",
            "updated_at": "",
        })

    _write_all(rows)
    log.info(f"Logged {len(picks)} pick(s) to {LOG_PATH}")


def _fetch_current_price(ticker: str) -> float | None:
    try:
        t = yf.Ticker(ticker)
        fi = t.fast_info
        return fi.get("last_price") if hasattr(fi, "get") else getattr(fi, "last_price", None)
    except Exception as e:
        log.warning(f"Could not fetch current price for {ticker}: {e}")
        return None


def update_outcomes():
    """Finds logged picks that have crossed a 30d/90d horizon without a
    recorded outcome yet, fetches current price, and fills in % change."""
    rows = _read_all()
    if not rows:
        return

    today = date.today()
    updated_count = 0
    price_cache: dict[str, float | None] = {}

    for row in rows:
        try:
            pick_date = date.fromisoformat(row["pick_date"])
        except (ValueError, KeyError):
            continue
        days_elapsed = (today - pick_date).days

        for horizon_days, price_field, pct_field in HORIZONS:
            if days_elapsed >= horizon_days and not row.get(price_field):
                ticker = row["ticker"]
                if ticker not in price_cache:
                    price_cache[ticker] = _fetch_current_price(ticker)
                current_price = price_cache[ticker]
                price_at_pick = row.get("price_at_pick")

                if current_price is not None and price_at_pick:
                    try:
                        price_at_pick_f = float(price_at_pick)
                        pct_change = ((current_price - price_at_pick_f) / price_at_pick_f) * 100
                        row[price_field] = f"{current_price:.2f}"
                        row[pct_field] = f"{pct_change:+.1f}%"
                        row["updated_at"] = datetime.now().isoformat(timespec="seconds")
                        updated_count += 1
                    except (ValueError, ZeroDivisionError):
                        continue

    if updated_count:
        _write_all(rows)
        log.info(f"Updated {updated_count} outcome field(s) in {LOG_PATH}")
    else:
        log.info("No pick outcomes due for update this run.")


def summary_stats(market_key: str | None = None) -> dict:
    """Quick aggregate for eventual use in emails/newsletter copy: how many
    picks have a recorded 30d/90d outcome, and the average % change."""
    rows = _read_all()
    if market_key:
        rows = [r for r in rows if r["market"] == market_key]

    result = {}
    for _, price_field, pct_field in HORIZONS:
        changes = []
        for r in rows:
            val = r.get(pct_field, "")
            if val:
                try:
                    changes.append(float(val.strip("%").replace("+", "")))
                except ValueError:
                    continue
        if changes:
            result[pct_field] = {
                "count": len(changes),
                "avg_pct": sum(changes) / len(changes),
                "win_rate": sum(1 for c in changes if c > 0) / len(changes),
            }
    return result
