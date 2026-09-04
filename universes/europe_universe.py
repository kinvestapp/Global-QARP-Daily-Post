# Curated Europe & UK universe (Nordics-weighted per user focus), yfinance
# suffixes: .L (London), .DE (Xetra/Germany), .PA (Paris), .AS (Amsterdam),
# .MI (Milan), .SW (Switzerland), .OL (Oslo), .CO (Copenhagen), .HE (Helsinki).
# OMX Stockholm is fetched separately via fetch_omx_stockholm.py (scraper +
# fallback) since that already exists — this file covers the rest of Europe.
# Hand-maintained starting list; expand as needed.

UK_FTSE_TICKERS = [
    "AZN.L", "SHEL.L", "HSBA.L", "ULVR.L", "BP.L", "GSK.L", "DGE.L", "RIO.L",
    "BATS.L", "REL.L", "LSEG.L", "NG.L", "CPG.L", "AAL.L", "GLEN.L", "BARC.L",
    "LLOY.L", "NWG.L", "PRU.L", "VOD.L", "TSCO.L", "IMB.L", "SSE.L", "BA.L",
    "RR.L", "STAN.L", "ANTO.L", "SGE.L", "CRH.L", "SMIN.L", "ITRK.L", "WTB.L",
]

GERMANY_TICKERS = [
    "SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "MBG.DE", "BAS.DE",
    "BMW.DE", "MUV2.DE", "IFX.DE", "DPW.DE", "BAYN.DE", "ADS.DE", "VOW3.DE",
    "HEN3.DE", "RWE.DE", "MRK.DE", "DB1.DE",
]

FRANCE_TICKERS = [
    "MC.PA", "OR.PA", "TTE.PA", "SAN.PA", "AI.PA", "SU.PA", "EL.PA", "BNP.PA",
    "DG.PA", "AIR.PA", "CS.PA", "RMS.PA", "SGO.PA", "KER.PA", "VIE.PA",
]

NETHERLANDS_TICKERS = ["ASML.AS", "UNA.AS", "HEIA.AS", "AD.AS", "INGA.AS", "PHIA.AS", "WKL.AS"]
SWITZERLAND_TICKERS = ["NESN.SW", "ROG.SW", "NOVN.SW", "UBSG.SW", "ZURN.SW", "ABBN.SW"]
ITALY_TICKERS = ["ENI.MI", "ISP.MI", "UCG.MI", "ENEL.MI", "RACE.MI"]

NORWAY_TICKERS = ["EQNR.OL", "DNB.OL", "NHY.OL", "TEL.OL", "MOWI.OL", "ORK.OL"]
DENMARK_TICKERS = ["NOVO-B.CO", "DSV.CO", "ORSTED.CO", "MAERSK-B.CO", "CARL-B.CO", "GN.CO"]
FINLAND_TICKERS = ["NOKIA.HE", "NESTE.HE", "SAMPO.HE", "KNEBV.HE", "FORTUM.HE"]

EUROPE_TICKERS = (
    UK_FTSE_TICKERS + GERMANY_TICKERS + FRANCE_TICKERS + NETHERLANDS_TICKERS
    + SWITZERLAND_TICKERS + ITALY_TICKERS + NORWAY_TICKERS + DENMARK_TICKERS
    + FINLAND_TICKERS
)
