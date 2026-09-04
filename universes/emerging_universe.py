# Curated "other emerging markets" universe — Brazil, Mexico, South Africa,
# Southeast Asia. yfinance suffixes: .SA (Brazil/B3), .MX (Mexico),
# .JO (Johannesburg), .SI (Singapore), .KL (Malaysia/Bursa), .BK (Thailand).
# Hand-maintained starting list; expand as needed.

BRAZIL_TICKERS = [
    "VALE3.SA", "PETR4.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA", "WEGE3.SA",
    "B3SA3.SA", "RENT3.SA", "SUZB3.SA", "RAIL3.SA", "PRIO3.SA", "EQTL3.SA",
    "JBSS3.SA", "GGBR4.SA", "ELET3.SA",
]

MEXICO_TICKERS = [
    "AMXL.MX", "WALMEX.MX", "GFNORTEO.MX", "FEMSAUBD.MX", "GMEXICOB.MX",
    "CEMEXCPO.MX", "KIMBERA.MX", "BIMBOA.MX",
]

SOUTH_AFRICA_TICKERS = [
    "NPN.JO", "PRX.JO", "BHP.JO", "AGL.JO", "SOL.JO", "MTN.JO", "SBK.JO", "FSR.JO",
]

SOUTHEAST_ASIA_TICKERS = [
    "D05.SI", "O39.SI", "U11.SI", "C6L.SI",  # Singapore
    "1155.KL", "1023.KL", "5347.KL",          # Malaysia
    "PTT.BK", "AOT.BK", "CPALL.BK",           # Thailand
]

OTHER_EMERGING_TICKERS = (
    BRAZIL_TICKERS + MEXICO_TICKERS + SOUTH_AFRICA_TICKERS + SOUTHEAST_ASIA_TICKERS
)
