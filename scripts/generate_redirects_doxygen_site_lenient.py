#!/usr/bin/env python3
# scripts/generate_redirects_doxygen_site_lenient.py
# - Reads redirects_generated.json
# - Merges redirects_static.json (if present) with STATIC taking precedence
# - Generates /sym/<path>/<func>/index.html redirect pages INSIDE Doxygen site (docs_build/html)
# - Publishes merged mapping to docs_build/html/sym/redirects.json
# - NEW: Builds a human-readable docs_build/html/sym/index.html listing all redirects
#
# Safe/lenient: never fails the build if inputs are missing. Prints warnings instead.

import json
import os
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
DOXY_HTML = ROOT / "docs_build" / "html"
OUT_DIR = DOXY_HTML / "sym"
GEN_JSON = ROOT / "redirects_generated.json"
STATIC_JSON = ROOT / "redirects_static.json"
MERGED_JSON = ROOT / "redirects_merged.json"

TEMPLATE = """<!doctype html>
<meta charset="utf-8">
<title>Redirecting...</title>
<meta http-equiv="refresh" content="0; url={url}">
<script>window.location.replace("{url}");</script>
<p>If you are not redirected automatically, <a href="{url}">click here</a>.</p>
"""

def build_index_page(redirects: dict):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index_path = OUT_DIR / "index.html"
    # Build a simple, readable index
    rows = []
    for key in sorted(redirects.keys()):
        url = redirects[key]
        # Left link goes through our stable redirect path; right link goes direct to target
        left = f"{OUT_DIR.relative_to(DOXY_HTML).as_posix()}/{escape(key)}/"
        right = escape(url)
        rows.append(f"<li><a href='{left}'>{escape(key)}</a> &rarr; <a href='{right}' target='_blank'>{right}</a></li>")

    html = f"""<!doctype html>
<meta charset="utf-8">
<title>Symbol Redirects</title>
<style>
  body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; max-width: 980px; margin: 40px auto; padding: 0 16px; }}
  h1 {{ margin-bottom: 8px; }}
  .hint {{ color: #666; margin-bottom: 16px; }}
  ul {{ line-height: 1.6; }}
  code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 4px; }}
</style>
<h1>Symbol Redirects</h1>
<p class="hint">
  Stable links under <code>/sym/&lt;path&gt;/&lt;symbol&gt;/</code> redirect to the current GitHub blob line range.
  This list is generated at build time by <code>generate_redirects_doxygen_site_lenient.py</code>.
</p>
<ul>
  {''.join(rows) if rows else '<li><em>No redirects available.</em></li>'}
</ul>
<p class="hint">Merged mapping (JSON): <a href="/{OUT_DIR.relative_to(DOXY_HTML).as_posix()}/redirects.json">/sym/redirects.json</a></p>
"""
    index_path.write_text(html, encoding="utf-8")
    print(f"[OK] created index page at {index_path.relative_to(DOXY_HTML)}")

def main():
    if not DOXY_HTML.exists():
        print(f"[WARN] Doxygen output not found at {DOXY_HTML}. Skipping sym generation.")
        return 0

    redirects = {}
    if GEN_JSON.exists():
        try:
            redirects = json.loads(GEN_JSON.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[WARN] Failed to read {GEN_JSON}: {e}")
            redirects = {}
    else:
        print(f"[WARN] {GEN_JSON} not found. (Autodiscover may have not produced it.)")

    if STATIC_JSON.exists():
        try:
            static_map = json.loads(STATIC_JSON.read_text(encoding="utf-8"))
            redirects.update(static_map)  # STATIC overrides GENERATED
            print(f"[INFO] Merged static overrides from {STATIC_JSON} ({len(static_map)} entries)")
        except Exception as e:
            print(f"[WARN] Failed to read {STATIC_JSON}: {e}")

    if not redirects:
        print("[WARN] No redirects to generate.")
        # Still create an empty index so the page exists
        build_index_page({})
        return 0

    # Save merged for debugging/visibility (optional)
    MERGED_JSON.write_text(json.dumps(redirects, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] wrote merged map to {MERGED_JSON} ({len(redirects)} entries)")

    # Ensure sym directory exists
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Publish merged mapping to the site so you can view it at /sym/redirects.json
    site_json = OUT_DIR / "redirects.json"
    site_json.write_text(json.dumps(redirects, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] published {site_json.relative_to(DOXY_HTML)}")

    # Generate redirect pages
    created = 0
    for key, url in redirects.items():
        parts = [p for p in key.split('/') if p]
        path = OUT_DIR
        for p in parts:
            path = path / p
        path.mkdir(parents=True, exist_ok=True)
        (path / "index.html").write_text(TEMPLATE.format(url=url), encoding="utf-8")
        created += 1
    print(f"[OK] generated {created} redirect pages under {OUT_DIR.relative_to(DOXY_HTML)}")

    # Build index page
    build_index_page(redirects)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
