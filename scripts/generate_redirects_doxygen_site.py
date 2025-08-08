#!/usr/bin/env python3
# scripts/generate_redirects_doxygen_site.py
# Generate HTML redirect pages under docs_build/html/sym so that Doxygen remains the site root.

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOXY_HTML = ROOT / "docs_build" / "html"
OUT_DIR = DOXY_HTML / "sym"
REDIR_GENERATED = ROOT / "redirects_generated.json"

TEMPLATE = """<!doctype html>
<meta charset="utf-8">
<title>Redirecting...</title>
<meta http-equiv="refresh" content="0; url={url}">
<script>window.location.replace("{url}");</script>
<p>If you are not redirected automatically, <a href="{url}">click here</a>.</p>
"""

def main():
    if not DOXY_HTML.exists():
        raise SystemExit(f"Doxygen output not found at {DOXY_HTML}. Did Doxygen run?")
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
