# Curated China, Japan & broader East Asia universe. yfinance suffixes:
# .T (Tokyo), .KS (Korea/KOSPI), .HK (Hong Kong), .SS (Shanghai), .SZ (Shenzhen).
#
# Caveat: mainland China A-shares (.SS/.SZ) have inconsistent, sometimes
# delayed or missing fundamentals coverage on Yahoo Finance for
# foreign/free access — treat any passing A-share result with extra
# skepticism and cross-check before publishing. Hong Kong-listed China
# names (.HK) tend to have more reliable data.

JAPAN_TICKERS = [
    "7203.T", "6758.T", "9984.T", "8306.T", "6861.T", "9432.T", "8035.T",
    "6098.T", "4063.T", "6501.T", "7267.T", "6367.T", "9433.T", "4502.T",
    "8058.T", "8031.T", "8001.T", "6902.T", "7751.T", "6503.T", "4519.T",
    "9020.T", "9022.T", "4568.T", "6273.T", "6702.T", "5108.T", "8411.T",
    "8316.T", "8766.T", "4661.T", "9613.T", "6752.T",
]

KOREA_TICKERS = [
    "005930.KS", "000660.KS", "373220.KS", "207940.KS", "005380.KS",
    "006400.KS", "051910.KS", "035420.KS", "005490.KS", "105560.KS",
    "012330.KS", "028260.KS", "066570.KS", "096770.KS", "003670.KS",
]

HONG_KONG_TICKERS = [
    "0700.HK", "9988.HK", "0941.HK", "1299.HK", "0388.HK", "3690.HK",
    "1810.HK", "2318.HK", "0005.HK", "0883.HK", "1211.HK", "9618.HK",
    "2020.HK", "1997.HK", "0027.HK", "0016.HK",
]

CHINA_A_SHARE_TICKERS = [
    "600519.SS", "601318.SS", "600036.SS", "601857.SS", "600276.SS",
    "000858.SZ", "000333.SZ", "300750.SZ", "002594.SZ", "600900.SS",
]

EAST_ASIA_TICKERS = JAPAN_TICKERS + KOREA_TICKERS + HONG_KONG_TICKERS + CHINA_A_SHARE_TICKERS
