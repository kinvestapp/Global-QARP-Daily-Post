"""
fetch_omx_stockholm.py
Scrapes Nasdaq Nordic's public "listed companies" page for the full Stockholm
main-market universe, converting each symbol into the .ST ticker format
yfinance expects.

Source: http://www.nasdaqomxnordic.com/shares/listed-companies/stockholm
This is a server-rendered HTML table (name, symbol, currency, ISIN, sector) —
no official bulk API exists, so this is a straightforward scrape, same class
of dependency as yfinance itself: convenient, but can break if Nasdaq changes
the page. If it fails, we fall back to the hand-curated list in
omx_stockholm.py so the pipeline never dies for lack of a Swedish universe.

Note: this deliberately scrapes only the MAIN MARKET listing (Large/Mid/Small
Cap), not Nasdaq First North — First North is a junior/growth market with
looser listing requirements, a poor fit for a quality-at-reasonable-price
screen, and excluding it mirrors how fetch_universe.py already excludes
OTC/Pink-sheet tiers for NYSE/NASDAQ.
"""

import re
import logging
import requests
from bs4 import BeautifulSoup

log = logging.getLogger("omx_scraper")

LISTED_COMPANIES_URL = "http://www.nasdaqomxnordic.com/shares/listed-companies/stockholm"
STOCKANALYSIS_URL = "https://stockanalysis.com/list/nasdaq-stockholm/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; KronosKapitalScreener/1.0)"}


def _symbol_to_yfinance_ticker(symbol: str) -> str:
    """'VOLV B' -> 'VOLV-B.ST', 'SAND' -> 'SAND.ST'"""
    cleaned = re.sub(r"\s+", "-", symbol.strip())
    return f"{cleaned}.ST"


def scrape_omx_stockholm() -> list[str]:
    resp = requests.get(LISTED_COMPANIES_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")
    all_tables = soup.find_all("table")
    rows = soup.select("table tbody tr")

    if not rows:
        # Diagnostics: log enough to actually see what came back, without
        # dumping the whole page. This is what tells us whether the page is
        # JS-rendered, restructured, or blocking non-browser requests silently.
        log.warning(
            f"nasdaqomxnordic.com scrape diagnostics — "
            f"status={resp.status_code}, content-length={len(resp.content)}, "
            f"<table> tags found={len(all_tables)}, "
            f"response snippet: {resp.text[:400]!r}"
        )
        raise ValueError("No table rows found — page structure may have changed")

    tickers = []
    for row in rows:
        cells = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cells) < 3:
            continue
        # Expected column order: Name, Symbol, Currency, ISIN, Sector, ICB code
        name, symbol, currency = cells[0], cells[1], cells[2]
        if not symbol:
            continue
        if currency and currency.upper() not in ("SEK",):
            continue  # skip cross-listed shares priced in another currency
        tickers.append(_symbol_to_yfinance_ticker(symbol))

    tickers = sorted(set(tickers))
    if len(tickers) < 100:
        raise ValueError(f"Only parsed {len(tickers)} tickers — likely a broken scrape, not a real result")
    return tickers


def scrape_stockanalysis() -> list[str]:
    """Second-choice free source. stockanalysis.com lists Nasdaq Stockholm
    tickers already in a form close to what's needed; symbols there use '.'
    for share classes (e.g. 'VOLV.B'), which we convert to yfinance's '-'
    convention."""
    resp = requests.get(STOCKANALYSIS_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")
    rows = soup.select("table tbody tr")
    if not rows:
        log.warning(
            f"stockanalysis.com scrape diagnostics — "
            f"status={resp.status_code}, content-length={len(resp.content)}, "
            f"response snippet: {resp.text[:400]!r}"
        )
        raise ValueError("No table rows found on stockanalysis.com either — page structure may have changed")

    tickers = []
    for row in rows:
        cells = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cells) < 2:
            continue
        symbol = cells[1] if cells[0].isdigit() else cells[0]
        if not symbol:
            continue
        yf_symbol = symbol.replace(".", "-")
        tickers.append(f"{yf_symbol}.ST")

    tickers = sorted(set(tickers))
    if len(tickers) < 100:
        raise ValueError(f"Only parsed {len(tickers)} tickers from stockanalysis.com — likely broken")
    return tickers


def get_omx_stockholm_tickers() -> list[str]:
    try:
        tickers = scrape_omx_stockholm()
        log.info(f"Scraped {len(tickers)} OMX Stockholm tickers from Nasdaq Nordic")
        return tickers
    except Exception as e:
        log.warning(f"Nasdaq Nordic scrape failed ({e}) — trying stockanalysis.com")

    try:
        tickers = scrape_stockanalysis()
        log.info(f"Scraped {len(tickers)} OMX Stockholm tickers from stockanalysis.com")
        return tickers
    except Exception as e:
        log.warning(f"stockanalysis.com scrape also failed ({e}) — falling back to curated static list")
        from omx_stockholm import OMX_STOCKHOLM_TICKERS
        return sorted(set(OMX_STOCKHOLM_TICKERS))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = get_omx_stockholm_tickers()
    print(f"Total: {len(result)} tickers")
    print(result[:20])
