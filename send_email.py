"""
send_email.py
Formats QARP scan results into a Kronos Kapital branded HTML email
and sends via Gmail SMTP (app password auth).
"""

import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

AUBERGINE = "#2E1A33"
GOLD = "#C9A24B"
CREAM = "#F7F3EC"


def _fmt_pct(v):
    return f"{v * 100:.1f}%" if v is not None else "—"


def _fmt_num(v, digits=2):
    return f"{v:.{digits}f}" if v is not None else "—"


def build_html(results_by_exchange: dict, scan_date: str) -> str:
    rows_html = ""
    total_passed = 0
    for exchange, results in results_by_exchange.items():
        passed = [r for r in results if r.passed]
        total_passed += len(passed)
        if not passed:
            continue
        rows_html += f"""
        <tr><td colspan="7" style="padding:18px 12px 6px;font-family:Georgia,serif;
            color:{GOLD};font-size:14px;letter-spacing:2px;text-transform:uppercase;
            border-bottom:1px solid {GOLD};">{exchange}</td></tr>
        """
        for r in sorted(passed, key=lambda x: x.metrics.get("roic") or 0, reverse=True):
            m = r.metrics
            rows_html += f"""
            <tr style="border-bottom:1px solid #e5ded0;">
                <td style="padding:8px 12px;font-family:Georgia,serif;color:{AUBERGINE};font-weight:bold;">{r.ticker}</td>
                <td style="padding:8px 12px;font-family:Arial,sans-serif;font-size:13px;color:#444;">{m.get('name','')}</td>
                <td style="padding:8px 12px;text-align:right;font-family:Arial,sans-serif;font-size:13px;">{_fmt_pct(m.get('roe'))}</td>
                <td style="padding:8px 12px;text-align:right;font-family:Arial,sans-serif;font-size:13px;">{_fmt_pct(m.get('roic'))}</td>
                <td style="padding:8px 12px;text-align:right;font-family:Arial,sans-serif;font-size:13px;">{_fmt_num(m.get('trailing_pe'),1)}</td>
                <td style="padding:8px 12px;text-align:right;font-family:Arial,sans-serif;font-size:13px;">{_fmt_num(m.get('peg'))}</td>
                <td style="padding:8px 12px;text-align:right;font-family:Arial,sans-serif;font-size:13px;">{_fmt_pct(m.get('gross_margin'))}</td>
            </tr>
            """

    if total_passed == 0:
        rows_html = f"""
        <tr><td style="padding:24px 12px;font-family:Georgia,serif;color:{AUBERGINE};">
            No stocks met all QARP thresholds this cycle.</td></tr>
        """

    html = f"""
    <html><body style="margin:0;padding:0;background:{CREAM};">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:{CREAM};padding:32px 0;">
    <tr><td align="center">
    <table width="680" cellpadding="0" cellspacing="0" style="background:#fff;border:1px solid {GOLD};">
        <tr><td style="background:{AUBERGINE};padding:28px 32px;">
            <div style="font-family:Georgia,serif;color:{GOLD};font-size:22px;letter-spacing:3px;">KRONOS KAPITAL</div>
            <div style="font-family:Georgia,serif;color:{CREAM};font-size:14px;letter-spacing:2px;margin-top:4px;">
                QARP SCREEN &mdash; {scan_date}</div>
        </td></tr>
        <tr><td style="padding:20px 32px 8px;font-family:Arial,sans-serif;color:#444;font-size:13px;">
            Quality-at-a-reasonable-price scan across NYSE, NASDAQ, and OMX Stockholm.
            {total_passed} stock(s) passed all filters this cycle.
        </td></tr>
        <tr><td style="padding:8px 20px 28px;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr style="border-bottom:2px solid {AUBERGINE};">
                    <th align="left" style="padding:8px 12px;font-family:Arial,sans-serif;font-size:11px;color:{AUBERGINE};text-transform:uppercase;">Ticker</th>
                    <th align="left" style="padding:8px 12px;font-family:Arial,sans-serif;font-size:11px;color:{AUBERGINE};text-transform:uppercase;">Name</th>
                    <th align="right" style="padding:8px 12px;font-family:Arial,sans-serif;font-size:11px;color:{AUBERGINE};text-transform:uppercase;">ROE</th>
                    <th align="right" style="padding:8px 12px;font-family:Arial,sans-serif;font-size:11px;color:{AUBERGINE};text-transform:uppercase;">ROIC</th>
                    <th align="right" style="padding:8px 12px;font-family:Arial,sans-serif;font-size:11px;color:{AUBERGINE};text-transform:uppercase;">P/E</th>
                    <th align="right" style="padding:8px 12px;font-family:Arial,sans-serif;font-size:11px;color:{AUBERGINE};text-transform:uppercase;">PEG</th>
                    <th align="right" style="padding:8px 12px;font-family:Arial,sans-serif;font-size:11px;color:{AUBERGINE};text-transform:uppercase;">Gross Marg.</th>
                </tr>
                {rows_html}
            </table>
        </td></tr>
        <tr><td style="background:{AUBERGINE};padding:16px 32px;">
            <div style="font-family:Arial,sans-serif;color:{CREAM};font-size:11px;">
                Automated QARP scan &middot; K-Invest.app / Kronos Kapital &middot; Not investment advice.
            </div>
        </td></tr>
    </table>
    </td></tr>
    </table>
    </body></html>
    """
    return html


def _clean_gmail_password(raw: str) -> str:
    """Gmail app passwords are 16 alphanumeric characters; Google displays
    them grouped with spaces for readability, but those aren't required.
    Strips ALL whitespace — including non-breaking spaces (\\xa0), which
    smtplib can't ASCII-encode and will crash on during login() if a
    password was copy-pasted from a browser display into a GitHub secret."""
    return re.sub(r"\s+", "", raw)


def _require_env(name: str) -> str:
    """Fetches a required env var and fails fast with a clear message if it's
    missing or blank — rather than letting an empty value silently reach
    smtplib, which produces a cryptic 'recipient refused' error instead of
    saying what's actually wrong."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Required secret/env var '{name}' is missing or empty. "
            f"Check Settings → Secrets and variables → Actions in this repo."
        )
    return value


def send_email(results_by_exchange: dict):
    gmail_user = _require_env("GMAIL_USER")
    gmail_app_password = _clean_gmail_password(_require_env("GMAIL_APP_PASSWORD"))
    recipient = _require_env("RECIPIENT_EMAIL")

    scan_date = datetime.now().strftime("%d %B %Y")
    html = build_html(results_by_exchange, scan_date)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Kronos Kapital — QARP Scan ({scan_date})"
    msg["From"] = gmail_user
    msg["To"] = recipient
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_app_password)
        server.sendmail(gmail_user, [recipient], msg.as_string())


def send_review_email(ranked_stocks, commentary_by_ticker, scan_date: str,
                       market_display_name: str = "", news_fact: dict | None = None):
    """Daily email per market. Contains a fun/wild finance fact, a market
    news roundup, and the top QARP/value picks with commentary and metrics.
    You publish to Substack manually from this — no automated posting step."""
    gmail_user = _require_env("GMAIL_USER")
    gmail_app_password = _clean_gmail_password(_require_env("GMAIL_APP_PASSWORD"))
    recipient = _require_env("RECIPIENT_EMAIL")
    news_fact = news_fact or {}

    fun_fact_html = ""
    if news_fact.get("fun_fact"):
        fun_fact_html = f"""
        <div style="background:{CREAM};border-left:4px solid {GOLD};padding:14px 18px;margin:0 0 20px;font-family:Georgia,serif;">
            <div style="color:{AUBERGINE};font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;">Fun Fact</div>
            <div style="font-size:14px;color:#333;line-height:1.5;">{news_fact['fun_fact']}</div>
        </div>
        """

    news_html = ""
    if news_fact.get("news_summary"):
        news_html = f"""
        <div style="padding:0 0 20px;font-family:Arial,sans-serif;">
            <div style="color:{AUBERGINE};font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;font-family:Georgia,serif;">Top Market News</div>
            <div style="font-size:14px;color:#333;line-height:1.6;">{news_fact['news_summary']}</div>
        </div>
        """

    rows = ""
    for stock in ranked_stocks:
        m = stock.metrics
        flag = f"<div style='color:#b3261e;font-weight:bold;font-size:12px;'>⚠ {stock.outlier_reason}</div>" if stock.is_outlier_flag else ""
        rows += f"""
        <div style="border:1px solid #e5ded0;margin-bottom:14px;padding:16px;font-family:Arial,sans-serif;">
            <h3 style="margin:0 0 6px;color:{AUBERGINE};font-family:Georgia,serif;">{stock.ticker} — {m.get('name','')} <span style="font-weight:normal;font-size:12px;color:#888;">(score: {stock.composite_score:.2f})</span></h3>
            {flag}
            <p style="font-size:13px;color:#333;line-height:1.5;">{commentary_by_ticker.get(stock.ticker,'')}</p>
            <p style="font-size:12px;color:#666;">
                ROE {_fmt_pct(m.get('roe'))} · ROIC {_fmt_pct(m.get('roic'))} ·
                P/E {_fmt_num(m.get('trailing_pe'),1)} · PEG {_fmt_num(m.get('peg'))} ·
                D/E {_fmt_num(m.get('debt_to_equity'))} · Sector {m.get('sector','—')}
            </p>
        </div>
        """
    if not rows:
        rows = f'<p style="font-family:Arial,sans-serif;color:#666;">No stocks cleared all QARP filters today — market conditions or the current thresholds mean nothing qualified.</p>'

    html = f"""
    <html><body style="margin:0;padding:0;background:{CREAM};">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:{CREAM};padding:32px 0;">
    <tr><td align="center">
    <table width="680" cellpadding="0" cellspacing="0" style="background:#fff;border:1px solid {GOLD};">
        <tr><td style="background:{AUBERGINE};padding:28px 32px;">
            <div style="font-family:Georgia,serif;color:{GOLD};font-size:22px;letter-spacing:3px;">KRONOS KAPITAL</div>
            <div style="font-family:Georgia,serif;color:{CREAM};font-size:14px;letter-spacing:2px;margin-top:4px;">
                {market_display_name.upper()} &mdash; {scan_date}</div>
        </td></tr>
        <tr><td style="padding:24px 32px 8px;">
            {fun_fact_html}
            {news_html}
            <div style="color:{AUBERGINE};font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;font-family:Georgia,serif;">Top QARP Picks</div>
            {rows}
        </td></tr>
        <tr><td style="background:{AUBERGINE};padding:16px 32px;">
            <div style="font-family:Arial,sans-serif;color:{CREAM};font-size:11px;">
                Kronos Kapital &middot; Not investment advice &middot; Review before publishing to Substack.
            </div>
        </td></tr>
    </table>
    </td></tr>
    </table>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Kronos Kapital — {market_display_name} — {scan_date}"
    msg["From"] = gmail_user
    msg["To"] = recipient
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_app_password)
        server.sendmail(gmail_user, [recipient], msg.as_string())
