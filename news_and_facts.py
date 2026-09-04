"""
news_and_facts.py
Uses the Anthropic API with web search enabled to generate two grounded,
market-specific pieces for the daily email:
  1. A short "top business/finance news" roundup for that market
  2. One fun/wild/crazy business-finance-market fact

Both are generated with strict instructions to paraphrase rather than quote
verbatim, and to name sources rather than reproduce their text — the same
copyright discipline that applies to any published research content.
"""

import os
import logging
from anthropic import Anthropic

log = logging.getLogger("news_and_facts")

MODEL = "claude-sonnet-4-6"


def _client() -> Anthropic:
    return Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def generate_news_summary(market_display_name: str, news_focus: str) -> str:
    client = _client()
    prompt = f"""Search the web for today's top business and financial market news relevant to: {news_focus}.

Write a concise roundup (120-180 words) of the 3-4 most important stories for
someone investing in {market_display_name}. Rules:
- Paraphrase everything in your own words — never quote a source directly, not even short phrases.
- Name the outlet/source informally in prose (e.g. "Reuters reported that...") rather than footnoting or linking.
- Focus on what's actually market-moving: central bank moves, major earnings, macro data, regulatory news — not celebrity or lifestyle stories.
- Plain prose, no headers, no bullet points, no markdown formatting.
- If search turns up nothing genuinely news-relevant, say so plainly rather than inventing content."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
    )
    text_blocks = [b.text for b in response.content if b.type == "text"]
    return "\n".join(text_blocks).strip()


def generate_fun_fact(market_display_name: str) -> str:
    client = _client()
    prompt = f"""Search the web if needed, then share ONE genuinely fun, wild, or
surprising business/finance/market fact or story related to {market_display_name}
or global markets more broadly (doesn't have to be recent — historical oddities
are great too). Think: a bizarre IPO story, a wild trading anecdote, an
unexpected correlation, a strange regulatory quirk, a legendary investor blunder
or win — the kind of thing that makes someone say "wait, really?"

Rules:
- 2-4 sentences, written with personality and a light, engaging tone.
- Paraphrase any source material in your own words — never quote directly.
- Must be factually accurate — if you're not confident it's true, pick a different fact.
- No markdown formatting, just plain prose."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
    )
    text_blocks = [b.text for b in response.content if b.type == "text"]
    return "\n".join(text_blocks).strip()


def generate_news_and_fact(market_display_name: str, news_focus: str) -> dict:
    log.info("Generating news summary via Claude + web search...")
    news = generate_news_summary(market_display_name, news_focus)
    log.info("Generating fun fact via Claude + web search...")
    fact = generate_fun_fact(market_display_name)
    return {"news_summary": news, "fun_fact": fact}
