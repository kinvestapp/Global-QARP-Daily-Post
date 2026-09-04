"""
markets.py
Defines the 5-market weekday rotation. Each weekday's workflow sets a
MARKET env var; run_qarp_scan.py looks it up here to get the right ticker
universe, display name, and target weekday (used for the DST-safe slot
check in run_qarp_scan.py).
"""

from dataclasses import dataclass, field


@dataclass
class MarketConfig:
    key: str
    display_name: str
    weekday: int  # 0=Monday ... 4=Friday
    get_tickers: callable
    news_focus: str  # short phrase used in the Claude news/fact prompt


def _us_tickers() -> list[str]:
    from fetch_universe import get_nasdaq_tickers, get_nyse_tickers
    return sorted(set(get_nasdaq_tickers() + get_nyse_tickers()))


def _europe_nordics_tickers() -> list[str]:
    from fetch_universe import get_omx_stockholm_tickers
    from universes.europe_universe import EUROPE_TICKERS
    return sorted(set(get_omx_stockholm_tickers() + EUROPE_TICKERS))


def _india_tickers() -> list[str]:
    from universes.india_universe import INDIA_NSE_TICKERS
    return sorted(set(INDIA_NSE_TICKERS))


def _east_asia_tickers() -> list[str]:
    from universes.east_asia_universe import EAST_ASIA_TICKERS
    return sorted(set(EAST_ASIA_TICKERS))


def _emerging_tickers() -> list[str]:
    from universes.emerging_universe import OTHER_EMERGING_TICKERS
    return sorted(set(OTHER_EMERGING_TICKERS))


MARKETS = {
    "US": MarketConfig(
        key="US",
        display_name="United States (NYSE & NASDAQ)",
        weekday=0,  # Monday
        get_tickers=_us_tickers,
        news_focus="U.S. stock market and macroeconomic news",
    ),
    "EUROPE_NORDICS": MarketConfig(
        key="EUROPE_NORDICS",
        display_name="Europe & UK, with a Nordics focus",
        weekday=1,  # Tuesday
        get_tickers=_europe_nordics_tickers,
        news_focus="European and UK stock market news, with extra attention to the Nordic markets (Sweden, Norway, Denmark, Finland)",
    ),
    "INDIA": MarketConfig(
        key="INDIA",
        display_name="India (NSE)",
        weekday=2,  # Wednesday
        get_tickers=_india_tickers,
        news_focus="Indian stock market (NSE/BSE) and economic news",
    ),
    "EAST_ASIA": MarketConfig(
        key="EAST_ASIA",
        display_name="China, Japan & East Asia",
        weekday=3,  # Thursday
        get_tickers=_east_asia_tickers,
        news_focus="Chinese, Japanese, Korean, and Hong Kong stock market news",
    ),
    "EMERGING": MarketConfig(
        key="EMERGING",
        display_name="Other Emerging Markets (Brazil, Mexico, South Africa, Southeast Asia)",
        weekday=4,  # Friday
        get_tickers=_emerging_tickers,
        news_focus="emerging markets stock and economic news across Latin America, Africa, and Southeast Asia",
    ),
}


def get_market(key: str) -> MarketConfig:
    if key not in MARKETS:
        raise ValueError(f"Unknown MARKET '{key}' — must be one of {list(MARKETS)}")
    return MARKETS[key]
