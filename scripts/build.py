#!/usr/bin/env python3
"""Build the Base Quest Scout static page from public, read-only sources."""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
APP_ID = "6a1e989b48bd6000dbb5b58f"

PUBLIC_READONLY = ["docs", "documentation", "learn", "leaderboard", "public", "campaign", "builder", "app"]
CONFIRM_BOUNDARY = ["wallet", "account", "login", "connect", "social", "share", "registration", "register"]
HARD_STOP = ["signature", "sign", "gas", "transaction", "transactions", "claim", "payout", "reward", "rewards", "kyc", "funds", "faucet", "eth"]


def fetch_text(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "BaseQuestScout/1.0 (+https://mnxd.github.io/base-quest-scout/)",
            "Accept": "text/html,text/plain,application/json;q=0.8,*/*;q=0.5",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read(750_000)
    return raw.decode("utf-8", "replace")


def strip_html(text: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def snippets(text: str, keywords: list[str], limit: int = 6) -> list[str]:
    lowered = text.lower()
    out: list[str] = []
    for keyword in keywords:
        idx = lowered.find(keyword.lower())
        if idx < 0:
            continue
        start = max(0, idx - 130)
        end = min(len(text), idx + 270)
        snippet = text[start:end].strip()
        if snippet and snippet not in out:
            out.append(snippet)
        if len(out) >= limit:
            break
    return out


def classify(seed: dict[str, Any], text: str) -> tuple[str, list[str], list[str]]:
    haystack = f"{seed.get('title','')} {seed.get('description','')} {text}".lower()
    signals: list[str] = []
    for keyword in PUBLIC_READONLY:
        if keyword in haystack:
            signals.append(f"public_readonly:{keyword}")
    for keyword in CONFIRM_BOUNDARY:
        if keyword in haystack:
            signals.append(f"confirmation:{keyword}")
    for keyword in HARD_STOP:
        if keyword in haystack:
            signals.append(f"hard_stop:{keyword}")

    # Explicitly curated read-only resources stay auto-trackable unless the
    # page itself contains hard-stop language around funds/signatures/KYC.
    curated_readonly = seed.get("default_decision") == "auto_track_zero_cost"
    has_hard_stop = any(signal.startswith("hard_stop:") for signal in signals)
    has_confirmation = any(signal.startswith("confirmation:") for signal in signals)
    forced_decision = seed.get("force_decision")
    if forced_decision:
        decision = forced_decision
    elif curated_readonly and not has_hard_stop:
        decision = "auto_track_zero_cost"
    elif curated_readonly and has_hard_stop:
        decision = "manual_confirmation_required"
    elif has_hard_stop:
        decision = "hard_stop"
    elif has_confirmation:
        decision = "manual_confirmation_required"
    else:
        decision = seed.get("default_decision") or "auto_track_zero_cost"

    evidence_keywords = HARD_STOP + CONFIRM_BOUNDARY + PUBLIC_READONLY
    return decision, signals[:14], snippets(text, evidence_keywords)


def build() -> dict[str, Any]:
    seeds = json.loads((ROOT / "data" / "seeds.json").read_text(encoding="utf-8"))
    items = []
    for seed in seeds:
        try:
            raw = fetch_text(seed["url"])
            text = strip_html(raw)
            error = None
        except Exception as exc:  # Keep build deterministic and visible.
            text = ""
            error = f"fetch_error:{type(exc).__name__}: {exc}"
        decision, signals, evidence = classify(seed, text)
        if error:
            signals.append(error)
            evidence = [error]
        items.append({
            "id": seed["id"],
            "title": seed["title"],
            "description": seed["description"],
            "url": seed["url"],
            "decision": decision,
            "signals": signals,
            "evidence": evidence or ["No strong signal extracted."],
        })
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "app_id": APP_ID,
        "items": items,
    }


def main() -> int:
    data = build()
    template = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    page = template.replace("__DATA__", json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/"))
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    (ROOT / "data" / "latest.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
