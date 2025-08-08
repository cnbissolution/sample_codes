#!/usr/bin/env python3
# scripts/generate_redirects_doxygen_site_lenient.py
# Same as _doxygen_site but does NOT fail if redirects_generated.json is empty.

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
        print(f"[WARN] Doxygen output not found at {DOXY_HTML}. Did Doxygen run?")
        return 0
    if not REDIR_GENERATED.exists():
        print(f"[WARN] missing {REDIR_GENERATED}")
        return 0
    data = json.loads(REDIR_GENERATED.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data:
        print("[WARN] redirects_generated.json has no entries. Skipping sym generation.")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for key, url in data.items():
        parts = key.split("/")
        path = OUT_DIR
        for p in parts:
            path = path / p
        path.mkdir(parents=True, exist_ok=True)
        (path / "index.html").write_text(TEMPLATE.format(url=url), encoding="utf-8")
        print(f"[OK] sym/{'/'.join(parts)}/ -> {url}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
