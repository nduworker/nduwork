#!/usr/bin/env python3
"""Pick one of my starred repos (across STAR_USERS) for today and have a local LLM say why I like it.

Writes pick.json at the repo root. Stdlib only.
  python3 scripts/pick.py            # real run (GitHub API + Ollama)
  python3 scripts/pick.py --selftest # offline checks
"""
import base64
import datetime
import json
import os
import pathlib
import random
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "pick.json"
USERS = os.environ.get("STAR_USERS", "nduworker").split(",")
MODEL = os.environ.get("OLLAMA_MODEL") or "qwen3.8:27b"
OLLAMA_URL = os.environ.get("OLLAMA_URL") or "http://localhost:11434/v1/chat/completions"
HISTORY_DAYS = 7


def http_json(url, data=None, headers=None, timeout=60):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers=headers or {})
    if data:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def gh(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "nduwork-pick"}
    if tok := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {tok}"
    return http_json(f"https://api.github.com{path}", headers=headers)


def starred(user):
    out, page = [], 1
    while batch := gh(f"/users/{user}/starred?per_page=100&page={page}"):
        out += batch
        page += 1
    return out


def choose(names, day, history):
    """Deterministic per day; skips repos picked in the last HISTORY_DAYS unless too few remain."""
    recent = set(history[-HISTORY_DAYS:])
    pool = sorted(n for n in names if n not in recent)
    if len(pool) < 8:
        pool = sorted(names)
    return random.Random(day).choice(pool)


def clean(text):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    return " ".join(text.split()).strip().strip('"')


def summarize(repo, readme):
    persona = (ROOT / "scripts" / "persona.md").read_text()
    user = f"Repo: {repo['full_name']}\nDescription: {repo.get('description') or ''}\n\nREADME excerpt:\n{readme[:6000]}"
    resp = http_json(OLLAMA_URL, {
        "model": MODEL,
        "messages": [{"role": "system", "content": persona}, {"role": "user", "content": user}],
        "temperature": 0.6,
        "stream": False,
    }, timeout=900)
    out = clean(resp["choices"][0]["message"]["content"])
    if len(out) < 40:
        raise SystemExit(f"LLM output too short: {out!r}")
    return out


def main():
    day = datetime.date.today().isoformat()
    prev = json.loads(OUT.read_text()) if OUT.exists() else {}
    if prev.get("date") == day:
        print(f"already picked for {day}: {prev['repo']}")
        return
    by_name = {r["full_name"]: r for u in USERS for r in starred(u.strip())}
    history = prev.get("history", [])
    name = choose(list(by_name), day, history)
    repo = by_name[name]
    try:
        readme = base64.b64decode(gh(f"/repos/{name}/readme")["content"]).decode("utf-8", "replace")
    except Exception:
        readme = ""
    pick = {
        "date": day,
        "repo": name,
        "url": repo["html_url"],
        "description": repo.get("description") or "",
        "language": repo.get("language") or "",
        "stars": repo.get("stargazers_count", 0),
        "summary": summarize(repo, readme),
        "model": MODEL,
        "history": (history + [name])[-30:],
    }
    OUT.write_text(json.dumps(pick, indent=2) + "\n")
    print(json.dumps(pick, indent=2))


def selftest():
    names = [f"o/r{i}" for i in range(17)]
    a = choose(names, "2026-09-23", [])
    assert a == choose(names, "2026-09-23", []), "same day, same pick"
    hist = names[:7]
    for d in range(30):
        assert choose(names, f"2026-10-{d + 1:02d}", hist) not in hist, "recent picks excluded"
    small = names[:9]
    assert choose(small, "2026-09-23", small[:7]) in small, "falls back when pool is small"
    assert clean("<think>hmm\nok</think>\n\"I like it.\"") == "I like it."
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
