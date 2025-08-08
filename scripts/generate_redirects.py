#!/usr/bin/env python3
# scripts/generate_redirects.py
# Generate HTML redirect pages from redirects_generated.json

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "site" / "sym"
REDIR_GENERATED = ROOT / "redirects_generated.json"

TEMPLATE = """<!doctype html>
<meta charset="utf-8">
<title>Redirecting...</title>
<meta http-equiv="refresh" content="0; url={url}">
<script>window.location.replace("{url}");</script>
<p>If you are not redirected automatically, <a href="{url}">click here</a>.</p>
"""

def main():
    if not REDIR_GENERATED.exists():
        raise SystemExit(f"missing {REDIR_GENERATED}")
    data = json.loads(REDIR_GENERATED.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for key, url in data.items():
        parts = key.split("/")
        path = OUT_DIR
        for p in parts:
            path = path / p
        path.mkdir(parents=True, exist_ok=True)
        (path / "index.html").write_text(TEMPLATE.format(url=url), encoding="utf-8")
        print(f"[OK] sym/{'/'.join(parts)}/ -> {url}")

if __name__ == "__main__":
    main()
