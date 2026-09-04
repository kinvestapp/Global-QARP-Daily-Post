# QARP Daily — Kronos Kapital

Five independent daily workflows, one per market, each emailing a Kronos
Kapital-branded roundup: a fun/wild finance fact, a market news summary,
and the top 3 QARP/value picks with Claude-generated commentary and
fundamentals. You review and publish to Substack manually — there's no
automated posting step (see the Substack section below for why).

## Schedule

| Day       | Market                                   | Workflow file              |
|-----------|-------------------------------------------|-----------------------------|
| Monday    | United States (NYSE & NASDAQ)             | `qarp-US.yml`               |
| Tuesday   | Europe & UK, Nordics-focused              | `qarp-Europe-Nordics.yml`   |
| Wednesday | India (NSE)                               | `qarp-India.yml`            |
| Thursday  | China, Japan & East Asia                  | `qarp-East-Asia.yml`        |
| Friday    | Other Emerging Markets (Brazil, Mexico, South Africa, Southeast Asia) | `qarp-Emerging.yml` |

Each runs at 23:00 CET/CEST (dual cron handles the DST shift automatically,
same pattern as before — see `run_qarp_scan.py`'s `is_send_slot`).

## Pipeline (per day)

1. `markets.py` — looks up that day's market via the `MARKET` env var set in its workflow file
2. Universe fetch — US/OMX Stockholm use live scrapers (`fetch_universe.py`,
   `fetch_omx_stockholm.py`); the other 4 markets use hand-curated seed
   lists in `universes/` (no free bulk APIs exist for NSE, most European
   exchanges, East Asian exchanges, or other emerging markets — same
   constraint that applies to OMX Stockholm's fallback list)
3. Optional market-cap pre-filter, then `qarp_screen.py`'s base QARP filter
4. `rank_and_select.py` — multi-year trend check, composite z-score ranking, outlier flagging, sector cap → top 3
5. `commentary.py` — Claude writes grounded commentary per pick
6. `news_and_facts.py` — Claude + web search generates a market news roundup and a fun/wild finance fact, paraphrased with source attribution (no verbatim quoting)
7. `send_email.py` — one branded email per day with everything above

## Setup checklist

1. **Repo**: push this folder (including the `universes/` subfolder and all
   5 files in `.github/workflows/`) to your GitHub repo.
2. **Secrets** (Settings → Secrets and variables → Actions) — shared across
   all 5 workflows: `GMAIL_USER`, `GMAIL_APP_PASSWORD` (paste with NO
   spaces — see note below), `RECIPIENT_EMAIL`, `ANTHROPIC_API_KEY`, and
   optionally `MIN_MARKET_CAP`.
3. **Gmail app password**: paste it as the raw 16 characters, no spaces.
   (`send_email.py` also strips whitespace defensively, but starting clean
   avoids the earlier `\xa0` non-breaking-space bug entirely.)
4. **Test each market independently**: Actions → pick one of the 5
   workflows → Run workflow → `force_run: true`. Do this for all 5 before
   trusting the schedule, since each has a different ticker universe and
   can fail independently.
5. **Publishing**: copy the email content into Substack's editor and
   publish manually. Automated posting was removed after Substack's login
   endpoint started returning a Cloudflare bot-challenge page — building a
   bypass for that isn't something to pursue (see prior discussion); manual
   publish is also the safer design anyway, since you were already
   reviewing every pick before it went out.

## Pick performance tracking

Every day's top 3 picks get logged to `picks_log.csv` in the repo root
(`pick_log.py`), and each run also checks older entries for 30-day/90-day
price outcomes, filling them in automatically. The workflow commits this
file back to the repo after each run (`git push` step, uses the default
`GITHUB_TOKEN` — no new secret needed).

This is what eventually lets you show subscribers a real track record
("our picks are up X% on average after 30 days") instead of just asking
them to trust the methodology. `pick_log.summary_stats()` computes that
aggregate whenever you're ready to surface it — not wired into the email
yet, but the data will be there once a few cycles have run.

## Known constraints


- **Non-US/Sweden universes are curated seed lists, not full exchange
  listings.** India (~85 large/liquid names), Europe/UK (~100 names across
  UK/Germany/France/Netherlands/Switzerland/Italy/Nordics), East Asia
  (~75 names across Japan/Korea/Hong Kong/China A-shares), and other
  emerging markets (~40 names across Brazil/Mexico/South Africa/Southeast
  Asia) are all hand-picked large/liquid companies, not the full listed
  universe like the US NASDAQ/NYSE fetch. Expand the relevant file in
  `universes/` over time if you want deeper coverage.
- **Mainland China A-shares (.SS/.SZ)** have inconsistent free fundamentals
  coverage via Yahoo — treat any A-share pass with extra skepticism.
- **Rate limits**: even at reduced universe sizes, Yahoo can still
  rate-limit GitHub's shared runner IPs. The `MIN_MARKET_CAP` pre-filter
  and `MAX_RETRIES` backoff in `qarp_screen.py` help but don't eliminate this.
- **News/fact generation cost**: each day's run makes 2 additional Claude
  API calls with web search enabled — small but non-zero cost, on top of
  the per-stock commentary calls.
- **No screen predicts future returns.** This ranks historical fundamentals
  and summarizes news; none of it is investment advice, and the emails
  should say so before anything goes out to subscribers.
