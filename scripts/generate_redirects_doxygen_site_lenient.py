#!/usr/bin/env python3
# scripts/generate_redirects_doxygen_site_lenient.py
# Generate HTML redirect pages under docs_build/html/sym/
# Merges redirects_generated.json with redirects_static.json if present.
# static entries override generated ones.

import os
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOXYGEN_HTML_DIR = ROOT / "docs_build" / "html"
SYM_DIR = DOXYGEN_HTML_DIR / "sym"

generated_file = ROOT / "redirects_generated.json"
static_file = ROOT / "redirects_static.json"

if not generated_file.exists():
    print(f"[ERROR] {generated_file} not found. Did build_symbol_map_autodiscover.py run?")
    exit(1)

with open(generated_file, "r", encoding="utf-8") as f:
    redirects = json.load(f)

if static_file.exists():
    with open(static_file, "r", encoding="utf-8") as f:
        static_map = json.load(f)
    redirects.update(static_map)  # static overrides generated
    print(f"[INFO] merged {len(static_map)} static entries")

print(f"[INFO] total redirects: {len(redirects)}")

# Create redirect HTML pages
for key, target in redirects.items():
    parts = key.strip("/").split("/")
    dest_dir = SYM_DIR.joinpath(*parts)
    dest_dir.mkdir(parents=True, exist_ok=True)
    html = f"""<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="refresh" content="0; url={target}"/>
    <link rel="canonical" href="{target}"/>
  </head>
  <body>
    <p>Redirecting to <a href="{target}">{target}</a>...</p>
  </body>
</html>
"""
    with open(dest_dir / "index.html", "w", encoding="utf-8") as outf:
        outf.write(html)

print(f"[DONE] redirect pages written under {SYM_DIR}")

# Also publish merged redirects.json for inspection
SYM_DIR.mkdir(parents=True, exist_ok=True)
with open(SYM_DIR / "redirects.json", "w", encoding="utf-8") as f:
    json.dump(redirects, f, ensure_ascii=False, indent=2)
print(f"[DONE] wrote merged redirects.json to {SYM_DIR / 'redirects.json'}")
