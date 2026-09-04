"""
run_qarp_scan.py
Entry point run by GitHub Actions, once daily per weekday-market rotation:
  Mon -> US, Tue -> Europe/UK+Nordics, Wed -> India,
  Thu -> China/Japan/East Asia, Fri -> Other Emerging Markets.

Pipeline:
  1. Look up the day's market (markets.py) via the MARKET env var
  2. Fetch that market's ticker universe
  3. Optional market-cap pre-filter, then base QARP filter (qarp_screen)
  4. Multi-year trend check + composite z-score ranking + sector cap (rank_and_select)
  5. Claude-generated commentary per pick (commentary)
  6. Claude + web search: top market news roundup and a fun finance fact (news_and_facts)
  7. Review/final email — you publish to Substack manually from this (send_email)
"""

import os
import sys
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import qarp_screen
from markets import get_market
from rank_and_select import compute_composite_scores, apply_trend_check, select_top_n
from commentary import generate_all
from news_and_facts import generate_news_and_fact
from send_email import send_review_email
import pick_log

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("run")

STOCKHOLM = ZoneInfo("Europe/Stockholm")
TARGET_LOCAL_HOUR = 23
TOP_N = 3


def is_send_slot(now_utc: datetime, target_weekday: int) -> bool:
    if os.environ.get("FORCE_RUN", "").lower() == "true":
        return True
    local = now_utc.astimezone(STOCKHOLM)
    if local.weekday() != target_weekday:
        return False
    if local.hour != TARGET_LOCAL_HOUR:
        return False  # the "wrong" seasonal cron fired; the matching one will run instead
    return True


def main():
    market_key = os.environ.get("MARKET")
    if not market_key:
        log.error("MARKET env var not set — must be one of US, EUROPE_NORDICS, INDIA, EAST_ASIA, EMERGING")
        sys.exit(1)
    market = get_market(market_key)

    now_utc = datetime.now(ZoneInfo("UTC"))
    if not is_send_slot(now_utc, market.weekday):
        log.info(f"{now_utc.isoformat()} is not {market.display_name}'s scheduled slot — skipping "
                 f"(set FORCE_RUN=true to override).")
        sys.exit(0)

    scan_date = now_utc.astimezone(STOCKHOLM).strftime("%d %B %Y")
    scan_date_iso = now_utc.astimezone(STOCKHOLM).date().isoformat()

    log.info("Checking for pick outcomes due for update...")
    try:
        pick_log.update_outcomes()
    except Exception as e:
        log.warning(f"Pick outcome update failed (non-fatal, continuing): {e}")

    log.info(f"Market: {market.display_name}")
    log.info("Fetching universe...")
    tickers = market.get_tickers()
    log.info(f"{market.key}: {len(tickers)} tickers")

    min_cap = float(os.environ.get("MIN_MARKET_CAP", "0"))
    qarp_screen.MIN_MARKET_CAP = min_cap

    if min_cap:
        log.info(f"Pre-filtering {market.key} ({len(tickers)} tickers) by market cap...")
        tickers = qarp_screen.prefilter_by_market_cap(tickers, min_cap)
        log.info(f"{market.key}: {len(tickers)} tickers cleared the cap floor, proceeding to full QARP scan")

    log.info(f"Screening {market.key} ({len(tickers)} tickers)...")
    results = qarp_screen.run_screen(tickers)
    passed = [r for r in results if r.passed]
    log.info(f"{market.key}: {len(passed)} passed base QARP filters")

    news_fact = generate_news_and_fact(market.display_name, market.news_focus)

    if not passed:
        log.warning("No stocks passed base QARP filters today — sending news/fact-only email.")
        send_review_email([], {}, scan_date, market.display_name, news_fact)
        sys.exit(0)

    log.info("Scoring and ranking candidates...")
    ranked = compute_composite_scores(passed)
    ranked = apply_trend_check(ranked)
    top_picks = select_top_n(ranked, n=TOP_N)

    if not top_picks:
        log.warning("No candidates survived trend check — sending news/fact-only email.")
        send_review_email([], {}, scan_date, market.display_name, news_fact)
        sys.exit(0)

    log.info(f"Top {len(top_picks)} selected: {[s.ticker for s in top_picks]}")

    try:
        pick_log.log_picks(market.key, scan_date, top_picks, pick_date_iso=scan_date_iso)
    except Exception as e:
        log.warning(f"Pick logging failed (non-fatal, continuing): {e}")

    log.info("Generating stock commentary via Claude...")
    commentary_by_ticker = generate_all(top_picks)

    log.info("Sending email...")
    send_review_email(top_picks, commentary_by_ticker, scan_date, market.display_name, news_fact)

    log.info("Done.")


if __name__ == "__main__":
    main()
